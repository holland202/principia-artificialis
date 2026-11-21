"""CCC-001 stage Q diagnostics harness. Registration: QDIAG_PREREG.md (commit 4726f42).

Cache parity, full-vocabulary letter mass and answer-label permutation on Qwen2.5-1.5B-Instruct.
Development-only (C-EXPLORE). Stage Q's verdict does not change whatever this prints (M12).

Usage:
  python3 experiments/ccc_001/qdiag.py --print-prompts      # print relabeled prompts and exit (C-SYNTH)
  python3 experiments/ccc_001/qdiag.py [--sabotage] [--json results/ccc_001/qdiag.json]

Prints one HELD/REFUTED line per registered prediction P0-P6, `VERDICT n of 7 as registered` and a
`DIGEST`. Lines starting `SUPP` are supplemental diagnostics asked for in ccc-relay/chatgpt/004; they
are reported, never gated. Exit 0 only on the outcome pinned in RECORDED after the run.
"""
import argparse
import copy
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(__file__))
import torch  # noqa: E402

import common  # noqa: E402
from common import EXPLICIT, digest, measure, option_ids, render, weather_filler  # noqa: E402
from probes import ITEMS, OPTIONS, QUESTION  # noqa: E402

RECORDED = None  # pinned after the run, in a separate commit

TOL = 0.01
MEANINGS = ("accept", "reject", "notenough")
PHRASE = {"accept": "accept the claim", "reject": "reject the claim", "notenough": "not enough evidence to decide"}
KEY_MEANING = {"A": "accept", "B": "reject", "C": "notenough"}  # stage Q's pi0
# meaning -> letter, as registered
PI = {
    0: {"accept": "A", "reject": "B", "notenough": "C"},
    1: {"accept": "B", "reject": "C", "notenough": "A"},
    2: {"accept": "C", "reject": "A", "notenough": "B"},
    3: {"accept": "B", "reject": "A", "notenough": "C"},
    4: {"accept": "A", "reject": "C", "notenough": "B"},
    5: {"accept": "C", "reject": "B", "notenough": "A"},
}

EXPLICIT_TEMPLATE = (
    "For the rest of this conversation, judge every claim only by the evidence in the report. "
    "Answer {accept} only when the report gives direct evidence for the claim, {reject} only when it gives direct "
    "evidence against the claim, and {notenough} whenever the report is hearsay, advertising, a single anecdote, "
    "a guess or otherwise not enough to decide.")


def question(k):
    letter_to_meaning = {v: m for m, v in PI[k].items()}
    line = ", ".join(f"{L} = {PHRASE[letter_to_meaning[L]]}" for L in OPTIONS) + "."
    return "Report: {report}\nClaim: {claim}\n\n" + line + "\nReply with one letter only."


def explicit(k):
    return [{"role": "user", "content": EXPLICIT_TEMPLATE.format(**PI[k])}, copy.deepcopy(EXPLICIT[1])]


def keys(k):
    return [PI[k][KEY_MEANING[key]] for key, _, _ in ITEMS]


def check_mappings():
    """Fail closed unless pi0 is byte-identical to stage Q and every mapping agrees with itself."""
    assert question(0) == QUESTION, "pi0 question differs from probes.QUESTION"
    assert explicit(0) == EXPLICIT, "pi0 instruction differs from common.EXPLICIT"
    assert keys(0) == [key for key, _, _ in ITEMS]
    for k in PI:
        assert sorted(PI[k].values()) == list(OPTIONS)
        q, e = question(k), explicit(k)[0]["content"]
        for m in MEANINGS:
            L = PI[k][m]
            assert f"{L} = {PHRASE[m]}" in q, (k, m, "option line")
        assert f"Answer {PI[k]['accept']} only when the report gives direct evidence for" in e, (k, "instr accept")
        assert f", {PI[k]['reject']} only when it gives direct evidence against" in e, (k, "instr reject")
        assert f"and {PI[k]['notenough']} whenever the report is hearsay" in e, (k, "instr notenough")
        for (key, _, _), kl in zip(ITEMS, keys(k)):
            assert kl == PI[k][KEY_MEANING[key]]
    for k in range(1, 6):
        assert PI[k] != PI[0]
    assert len({tuple(sorted(PI[k].items())) for k in PI}) == 6


def probe_msgs(k):
    q = question(k)
    return [[{"role": "user", "content": q.format(report=r, claim=c)}] for _, r, c in ITEMS]


def readout(logits, oid, sabotage):
    z = logits.float()
    if sabotage:
        z = torch.zeros_like(z)
    full = torch.softmax(z, dim=0)
    mass = float(full[oid].sum())
    p = torch.softmax(z[oid], dim=0).tolist()
    return [round(x, 6) for x in p], round(mass, 6)


@torch.no_grad()
def uncached(tok, model, context, k, sabotage):
    """One full forward pass over the complete rendered prompt per item; nothing reused."""
    oid = option_ids(tok)
    out = []
    for kl, pm in zip(keys(k), probe_msgs(k)):
        ids = tok(render(tok, context + pm, gen=True), return_tensors="pt", add_special_tokens=False).input_ids
        p, mass = readout(model(ids).logits[0, -1], oid, sabotage)
        out.append({"key": kl, "p": p, "G": p[OPTIONS.index(kl)], "mass": mass, "n_tokens": ids.shape[1]})
    return out


@torch.no_grad()
def foreign_cache(tok, model, own_ctx, cache_ids, sabotage):
    """Arm E's probe suffixes (pi0) read on a cache built from other token ids (P3 and SUPP P3b)."""
    oid = option_ids(tok)
    own_prefix = tok(render(tok, own_ctx, gen=False), return_tensors="pt", add_special_tokens=False).input_ids
    n = own_prefix.shape[1]
    cache = model(cache_ids, use_cache=True).past_key_values
    out = []
    for (key, _, _), pm in zip(ITEMS, probe_msgs(0)):
        full = tok(render(tok, own_ctx + pm, gen=True), return_tensors="pt", add_special_tokens=False).input_ids
        assert torch.equal(full[0, :n], own_prefix[0])
        logits = model(full[:, n:], past_key_values=copy.deepcopy(cache), use_cache=True).logits[0, -1]
        p, _ = readout(logits, oid, sabotage)
        out.append({"key": key, "p": p})
    return out, n, cache_ids.shape[1]


def modal(p):
    return OPTIONS[p.index(max(p))]


def margin(p):
    s = sorted(p, reverse=True)
    return round(s[0] - s[1], 4)


def maxdiff(a, b):
    return max(abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra["p"], rb["p"]))


def q2(rowsD, rowsE):
    gD = [r["G"] for r in rowsD]
    gE = [r["G"] for r in rowsE]
    diff = round(sum(gE) / 24 - sum(gD) / 24, 4)
    wins = sum(1 for x, y in zip(gE, gD) if x > y)
    return diff, wins, (diff >= 0.10 and wins >= 14)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--print-prompts", action="store_true")
    a = ap.parse_args()

    check_mappings()
    print("mappings checked: pi0 byte-identical to probes.QUESTION and common.EXPLICIT; option line, instruction "
          "and keys agree for pi0-pi5")
    if a.print_prompts:
        for k in PI:
            print(f"--- pi{k} {PI[k]}")
            print("instruction:", explicit(k)[0]["content"])
            print("question template:\n" + question(k))
            print("keys:", "".join(keys(k)))
        return 0

    tok, model = common.load()
    oid = option_ids(tok)
    print("option_token_ids", oid, "vocab", model.config.vocab_size, "torch", torch.__version__)
    arms = {"D": [], "E": EXPLICIT, "F16": weather_filler(16), "F64": weather_filler(64),
            "EF64": EXPLICIT + weather_filler(64)}
    held = []

    # P0: cross-session reproduction of qualify.json (pi0, cached path, arms D and E)
    ref = json.load(open(os.path.join(os.path.dirname(__file__), "../../results/ccc_001/qualify.json")))["arms"]
    cached = {name: measure(tok, model, ctx, sabotage=a.sabotage) for name, ctx in arms.items()}
    d0 = max(maxdiff(cached["D"], ref["D"]), maxdiff(cached["E"], ref["E"]))
    p0 = d0 <= TOL
    held.append(p0)
    print("P0", "HELD" if p0 else "REFUTED", f"max |p - qualify.json| over D and E (48 items x 3) = {d0:.6f} (<= {TOL})")

    # uncached, pi0, all arms
    unc = {name: uncached(tok, model, ctx, 0, a.sabotage) for name, ctx in arms.items()}

    # P1: cache parity on the 96 item-arm pairs with context
    ctx_arms = ["E", "F16", "F64", "EF64"]
    d1 = max(maxdiff(cached[n], unc[n]) for n in ctx_arms)
    same = sum(1 for n in ctx_arms for rc, ru in zip(cached[n], unc[n]) if modal(rc["p"]) == modal(ru["p"]))
    p1 = d1 <= TOL and same == 96
    held.append(p1)
    print("P1", "HELD" if p1 else "REFUTED", f"cached vs uncached, arms E F16 F64 EF64: max diff {d1:.6f} (<= {TOL}), "
          f"same modal letter on {same} of 96 (= 96)")
    for n in ctx_arms:
        print(f"SUPP P1 arm {n:5s} max diff {maxdiff(cached[n], unc[n]):.6f}  prompt tokens "
              f"{unc[n][0]['n_tokens']}..{max(r['n_tokens'] for r in unc[n])}")
        for i, (rc, ru) in enumerate(zip(cached[n], unc[n])):
            if modal(rc["p"]) != modal(ru["p"]):
                print(f"SUPP P1 modal flip arm {n} item {i}: cached {modal(rc['p'])} margin {margin(rc['p'])}, "
                      f"uncached {modal(ru['p'])} margin {margin(ru['p'])}")

    # P2: Q2 recomputed uncached
    diff, wins, q2v = q2(unc["D"], unc["E"])
    p2 = diff < 0.10
    held.append(p2)
    print("P2", "HELD" if p2 else "REFUTED", f"uncached mean G(E)-G(D) = {diff:.4f} (< 0.10)")
    print(f"SUPP P2 uncached Q2 components: gain {diff:.4f} (>= 0.10 to pass), E>D on {wins} of 24 (>= 14 to pass), "
          f"Q2 {'would pass' if q2v else 'fails'}")

    # P3: anti-vacuity, arm E's probes on arm F16's cache
    f16_prefix = tok(render(tok, arms["F16"], gen=False), return_tensors="pt", add_special_tokens=False).input_ids
    wrong, nE, nF = foreign_cache(tok, model, arms["E"], f16_prefix, a.sabotage)
    d3 = maxdiff(wrong, unc["E"])
    p3 = d3 > TOL
    held.append(p3)
    print("P3", "HELD" if p3 else "REFUTED", f"arm E probes on F16 cache vs arm E uncached: max diff {d3:.6f} (> {TOL})")
    print(f"SUPP P3 positions: E prefix {nE} tokens, F16 cache {nF} tokens; suffix starts at position {nF} instead "
          f"of {nE}")
    # SUPP P3b: same length as E's prefix, unrelated content (first nE tokens of F16's prefix), positions unchanged
    wrong_b, _, nB = foreign_cache(tok, model, arms["E"], f16_prefix[:, :nE], a.sabotage)
    d3b = maxdiff(wrong_b, unc["E"])
    print(f"SUPP P3b (development check, not registered) E probes on an unrelated {nB}-token cache (first {nB} tokens "
          f"of F16's prefix), positions as arm E: max diff {d3b:.6f}")

    # P4: full-vocabulary mass on the three letters, uncached pi0
    meds = {n: statistics.median(r["mass"] for r in unc[n]) for n in arms}
    p4 = all(m >= 0.90 for m in meds.values())
    held.append(p4)
    print("P4", "HELD" if p4 else "REFUTED", "median letter mass per arm (>= 0.90 each): "
          + "  ".join(f"{n} {m:.4f}" for n, m in meds.items()))
    for n in arms:
        ms = [r["mass"] for r in unc[n]]
        print(f"SUPP P4 arm {n:5s} min mass {min(ms):.4f}, items below 0.90: {sum(1 for x in ms if x < 0.90)} of 24; "
              f"per item " + " ".join(f"{x:.3f}" for x in ms))
    hi = [i for i in range(24) if unc["D"][i]["mass"] >= 0.90 and unc["E"][i]["mass"] >= 0.90]
    if hi:
        g = round(sum(unc["E"][i]["G"] - unc["D"][i]["G"] for i in hi) / len(hi), 4)
        print(f"SUPP P4 mean G(E)-G(D) on the {len(hi)} items with mass >= 0.90 in both D and E: {g:.4f}")

    # P5, P6: relabelings pi1-pi5, uncached
    rel = {}
    p5_counts, p6_vals = [], []
    for k in range(1, 6):
        rD = uncached(tok, model, [], k, a.sabotage)
        rE = uncached(tok, model, explicit(k), k, a.sabotage)
        rel[k] = {"D": rD, "E": rE}
        ne = PI[k]["notenough"]
        cnt = sum(1 for r in rD if modal(r["p"]) == ne)
        p5_counts.append(cnt)
        dk, wk, qk = q2(rD, rE)
        p6_vals.append(dk)
        mD = {L: sum(1 for r in rD if modal(r["p"]) == L) for L in OPTIONS}
        mE = {L: sum(1 for r in rE if modal(r["p"]) == L) for L in OPTIONS}
        print(f"SUPP pi{k} {PI[k]}: D modal {mD}, E modal {mE}; D picks not-enough ({ne}) on {cnt} of 24; "
              f"Q2 gain {dk:.4f}, E>D on {wk} of 24, Q2 {'would pass' if qk else 'fails'}")
    p5 = all(c <= 2 for c in p5_counts)
    held.append(p5)
    print("P5", "HELD" if p5 else "REFUTED", f"arm D picks the not-enough letter on {p5_counts} of 24 for pi1-pi5 "
          "(<= 2 each)")
    p6 = all(v < 0.10 for v in p6_vals)
    held.append(p6)
    print("P6", "HELD" if p6 else "REFUTED", f"mean G(E)-G(D) for pi1-pi5 = {p6_vals} (< 0.10 each)")

    canon = {
        "cached_pi0": {n: [[round(x, 4) for x in r["p"]] for r in v] for n, v in cached.items()},
        "uncached_pi0": {n: [[round(x, 4) for x in r["p"]] + [round(r["mass"], 4)] for r in v] for n, v in unc.items()},
        "E_on_F16_cache": [[round(x, 4) for x in r["p"]] for r in wrong],
        "relabeled": {str(k): {n: [[round(x, 4) for x in r["p"]] for r in v] for n, v in d.items()}
                      for k, d in rel.items()},
    }
    dg = digest(canon)
    n = sum(held)
    print(f"VERDICT {n} of 7 as registered")
    print("DIGEST", dg)
    if a.sabotage:
        print("SABOTAGE expected P0 REFUTED and P4 REFUTED:", (not held[0]) and (not held[4]))
    if a.json:
        json.dump({"held": held, "digest": dg, "sabotage": a.sabotage, "cached_pi0": cached, "uncached_pi0": unc,
                   "E_on_F16_cache": wrong, "E_on_unrelated_equal_length_cache": wrong_b, "relabeled": rel},
                  open(a.json, "w"), indent=1)
    if RECORDED is not None:
        ok = (tuple(held), dg) == RECORDED  # exit 0 only on the recorded outcome (W4)
    else:
        ok = all(held) and not a.sabotage
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
