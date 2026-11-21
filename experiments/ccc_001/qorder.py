"""CCC-001 stage Q letter-by-position crossing harness. Registration: QORDER_PREREG.md (commit 88614da).

Is Qwen2.5-1.5B-Instruct's no-context abstention bias about the letter A or about first place in the option line?
36 conditions = 6 letter assignments x 6 display orders, 24 development items each, uncached forward passes,
arm D (no context) primary, arm E (explicit instruction) secondary. Development-only (C-EXPLORE). Stage Q's verdict
does not change whatever this prints (M12).

Usage:
  python3 experiments/ccc_001/qorder.py --print-prompts      # print all 36 option lines and exit (C-SYNTH)
  python3 experiments/ccc_001/qorder.py [--sabotage] [--json results/ccc_001/qorder.json]

Prints one HELD/REFUTED line per registered prediction P0-P3, `VERDICT n of 4 as registered` and a `DIGEST`.
Lines starting `REPORT` are reported in the registration and never gated. Lines starting `SUPP` were asked for in
ccc-relay/chatgpt/008 after registration and before this run; they are not registered and never gated.
Exit 0 only on the outcome pinned in RECORDED after the run.
"""
import argparse
import copy
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import torch  # noqa: E402

import common  # noqa: E402
from common import EXPLICIT, digest, option_ids, render  # noqa: E402
from probes import ITEMS, OPTIONS, QUESTION  # noqa: E402
from qdiag import EXPLICIT_TEMPLATE, KEY_MEANING, MEANINGS, PHRASE, PI  # noqa: E402

RECORDED = None  # pinned after the run at its commit

TOL = 0.01
NE = "notenough"
LETTERS = [dict(zip(MEANINGS, perm)) for perm in itertools.permutations(OPTIONS)]  # meaning -> letter
ORDERS = list(itertools.permutations(MEANINGS))  # display position 1..3 -> meaning
CONDS = [(li, oi) for li in range(6) for oi in range(6)]


def option_line(lam, order):
    return ", ".join(f"{lam[m]} = {PHRASE[m]}" for m in order) + "."


def question(lam, order):
    return "Report: {report}\nClaim: {claim}\n\n" + option_line(lam, order) + "\nReply with one letter only."


def instruction(lam):
    return [{"role": "user", "content": EXPLICIT_TEMPLATE.format(**lam)}, copy.deepcopy(EXPLICIT[1])]


def keys(lam):
    return [lam[KEY_MEANING[key]] for key, _, _ in ITEMS]


def cell(c):
    lam, order = LETTERS[c[0]], ORDERS[c[1]]
    return lam[NE], order.index(NE) + 1


def seen_pi(c):
    """QDIAG mapping index if this condition's letters read A, B, C in display order, else None."""
    lam, order = LETTERS[c[0]], ORDERS[c[1]]
    if [lam[m] for m in order] != list(OPTIONS):
        return None
    return next(k for k in PI if PI[k] == lam)


def others_desc(c):
    """True if the two non-abstention letters are displayed in descending alphabetical order."""
    lam, order = LETTERS[c[0]], ORDERS[c[1]]
    rest = [lam[m] for m in order if m != NE]
    return rest[0] > rest[1]


def check_conditions():
    """Fail closed unless the base condition is stage Q's prompt byte for byte and every line is complete."""
    base = (LETTERS.index(PI[0]), ORDERS.index(("accept", "reject", "notenough")))
    assert question(*[LETTERS[base[0]], ORDERS[base[1]]]) == QUESTION, "base condition differs from probes.QUESTION"
    assert instruction(PI[0]) == EXPLICIT, "pi0 instruction differs from common.EXPLICIT"
    assert len(CONDS) == 36 and len({option_line(LETTERS[a], ORDERS[b]) for a, b in CONDS}) == 36
    for a, b in CONDS:
        line = option_line(LETTERS[a], ORDERS[b])
        for m in MEANINGS:
            assert line.count(f"{LETTERS[a][m]} = {PHRASE[m]}") == 1, (a, b, m)
        assert sorted(LETTERS[a].values()) == list(OPTIONS)
    cells = {}
    for c in CONDS:
        cells.setdefault(cell(c), []).append(c)
    assert len(cells) == 9 and all(len(v) == 4 for v in cells.values())
    seen = [c for c in CONDS if seen_pi(c) is not None]
    assert len(seen) == 6 and sorted(seen_pi(c) for c in seen) == list(range(6))
    assert sorted({cell(c) for c in seen}) == [("A", 1), ("B", 2), ("C", 3)]
    for c in seen:  # seen conditions render exactly QDIAG's question for that mapping
        import qdiag
        assert question(LETTERS[c[0]], ORDERS[c[1]]) == qdiag.question(seen_pi(c))
    print(f"conditions {len(CONDS)}  cells {len(cells)}  per cell {sorted({len(v) for v in cells.values()})}  "
          f"seen {len(seen)} in cells {sorted({cell(c) for c in seen})}  unseen {36 - len(seen)}")
    return cells


@torch.no_grad()
def run_condition(tok, model, oid, context, lam, order):
    q = question(lam, order)
    out = []
    for kl, (_, r, cl) in zip(keys(lam), ITEMS):
        msgs = context + [{"role": "user", "content": q.format(report=r, claim=cl)}]
        ids = tok(render(tok, msgs, gen=True), return_tensors="pt", add_special_tokens=False).input_ids
        z = model(ids).logits[0, -1].float()[oid]
        out.append({"key": kl, "z": [float(x) for x in z], "n_tokens": ids.shape[1]})
    return out


def probs(z, sabotage):
    t = torch.tensor(z, dtype=torch.float64)
    if sabotage:
        t = torch.zeros_like(t)
    return torch.softmax(t, dim=0).tolist()


def analyse(raw, cells, sabotage):
    """All registered quantities from stored letter logits. raw[(c, arm)] -> list of 24 {z, key}."""
    P = {k: [probs(r["z"], sabotage) for r in v] for k, v in raw.items()}

    def pne(c, arm):  # per-item p(abstention letter)
        i = OPTIONS.index(LETTERS[c[0]][NE])
        return [p[i] for p in P[(c, arm)]]

    def m(conds, arm="D"):
        vals = [x for c in conds for x in pne(c, arm)]
        return sum(vals) / len(vals)

    mean = {k: m(v) for k, v in cells.items()}
    unseen = {k: [c for c in v if seen_pi(c) is None] for k, v in cells.items()}
    mean_u = {k: m(v) for k, v in unseen.items()}
    p1c = [mean[("A", j)] - mean[("C", j)] for j in (1, 2, 3)]
    p2c = [mean_u[("A", j)] - mean_u[("C", j)] for j in (1, 2, 3)]
    modal = {"A": 0, "B": 0, "C": 0, "tie": 0}
    for c in CONDS:
        for p in P[(c, "D")]:
            mx = max(p)
            w = [L for L, x in zip(OPTIONS, p) if x == mx]
            modal[w[0] if len(w) == 1 else "tie"] += 1
    return {"P": P, "mean": mean, "mean_u": mean_u, "p1c": p1c, "p2c": p2c, "modal": modal, "pne": pne, "m": m,
            "unseen": unseen}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--print-prompts", action="store_true")
    a = ap.parse_args()

    cells = check_conditions()
    if a.print_prompts:
        for c in CONDS:
            lam, order = LETTERS[c[0]], ORDERS[c[1]]
            s = seen_pi(c)
            print(f"cond {c[0]}{c[1]} cell {cell(c)} {'seen pi' + str(s) if s is not None else 'unseen'} | "
                  f"{option_line(lam, order)} | keys {''.join(keys(lam))}")
        for li, lam in enumerate(LETTERS):
            print(f"instruction letters {li} {lam}: {instruction(lam)[0]['content']}")
        return 0

    tok, model = common.load()
    oid = option_ids(tok)
    print("option_token_ids", oid, "torch", torch.__version__, "threads", torch.get_num_threads())
    raw = {}
    for n, c in enumerate(CONDS):
        lam, order = LETTERS[c[0]], ORDERS[c[1]]
        raw[(c, "D")] = run_condition(tok, model, oid, [], lam, order)
        raw[(c, "E")] = run_condition(tok, model, oid, instruction(lam), lam, order)
        print(f"progress {n + 1}/36", flush=True)

    R = analyse(raw, cells, a.sabotage)
    held = []

    # P0: the 6 seen conditions reproduce qdiag.json uncached arm D within TOL
    ref = json.load(open(os.path.join(os.path.dirname(__file__), "../../results/ccc_001/qdiag.json")))
    d0 = 0.0
    for c in CONDS:
        k = seen_pi(c)
        if k is None:
            continue
        rows = ref["uncached_pi0"]["D"] if k == 0 else ref["relabeled"][str(k)]["D"]
        assert [r["key"] for r in rows] == keys(LETTERS[c[0]])
        d0 = max(d0, max(abs(x - y) for pr, rr in zip(R["P"][(c, "D")], rows) for x, y in zip(pr, rr["p"])))
    held.append(d0 <= TOL)
    print("P0", "HELD" if held[-1] else "REFUTED", f"6 seen conditions vs qdiag.json uncached arm D: max |p diff| "
          f"{d0:.6f} (<= {TOL})")

    held.append(all(x > 0 for x in R["p1c"]))
    print("P1", "HELD" if held[-1] else "REFUTED", "m(A,j) - m(C,j), all 36 conditions, j=1,2,3: "
          + "  ".join(f"{x:.6f}" for x in R["p1c"]) + " (> 0 each)")
    held.append(all(x > 0 for x in R["p2c"]))
    print("P2", "HELD" if held[-1] else "REFUTED", "m(A,j) - m(C,j), 30 unseen conditions, j=1,2,3: "
          + "  ".join(f"{x:.6f}" for x in R["p2c"]) + " (> 0 each)")

    # P3: anti-vacuity, the same analysis on the same logits with every logit set to zero
    S = analyse(raw, cells, True)
    contrasts = S["p1c"] + S["p2c"] + [S["mean"][(L, 1)] - S["mean"][(L, 3)] for L in OPTIONS]
    p3 = (all(x == 0.0 for x in contrasts) and S["modal"]["tie"] == 864
          and not all(x > 0 for x in S["p1c"]) and not all(x > 0 for x in S["p2c"]))
    held.append(p3)
    print("P3", "HELD" if p3 else "REFUTED", f"sabotaged readout: contrasts all exactly 0: "
          f"{all(x == 0.0 for x in contrasts)}, ties {S['modal']['tie']} of 864 (= 864), P1 and P2 refuted under "
          f"sabotage: {not all(x > 0 for x in S['p1c']) and not all(x > 0 for x in S['p2c'])}")

    # REPORT (registered, never gated)
    print("REPORT cell means m(L,j), arm D, p(abstention letter), all conditions [unseen only in brackets]:")
    for L in OPTIONS:
        print(f"REPORT   letter {L}: " + "  ".join(
            f"j={j} {R['mean'][(L, j)]:.6f} [{R['mean_u'][(L, j)]:.6f} n={len(R['unseen'][(L, j)])}]"
            for j in (1, 2, 3)))
    for L in OPTIONS:
        print(f"REPORT position contrast m({L},1) - m({L},3) = {R['mean'][(L, 1)] - R['mean'][(L, 3)]:.6f}")
    print(f"REPORT arm D modal readings over 864: {R['modal']}")
    print("REPORT 36-condition table (arm D mean p(abstention letter), modal counts A/B/C/tie, arm E mean):")
    for c in CONDS:
        lam, order = LETTERS[c[0]], ORDERS[c[1]]
        mc = {"A": 0, "B": 0, "C": 0, "tie": 0}
        for p in R["P"][(c, "D")]:
            mx = max(p)
            w = [L for L, x in zip(OPTIONS, p) if x == mx]
            mc[w[0] if len(w) == 1 else "tie"] += 1
        s = seen_pi(c)
        print(f"REPORT   {c[0]}{c[1]} {str(cell(c)):9s} {'pi' + str(s) if s is not None else '   '} "
              f"{option_line(lam, order):88s} D {R['m']([c]):.4f} {mc['A']:2d}/{mc['B']:2d}/{mc['C']:2d}/{mc['tie']} "
              f"E {R['m']([c], 'E'):.4f}")
    print("REPORT secondary arm E cell means m_E(L,j), and Q2 components per cell (gain mean G(E)-G(D), E>D count "
          "of 96):")
    for L in OPTIONS:
        parts = []
        for j in (1, 2, 3):
            cs = cells[(L, j)]
            gD = [p[OPTIONS.index(r["key"])] for c in cs for p, r in zip(R["P"][(c, "D")], raw[(c, "D")])]
            gE = [p[OPTIONS.index(r["key"])] for c in cs for p, r in zip(R["P"][(c, "E")], raw[(c, "E")])]
            gain = sum(gE) / len(gE) - sum(gD) / len(gD)
            wins = sum(1 for x, y in zip(gE, gD) if x > y)
            parts.append(f"j={j} {R['m'](cs, 'E'):.6f} gain {gain:+.4f} E>D {wins}/96")
        print(f"REPORT   letter {L}: " + "  ".join(parts))

    # SUPP (asked for in ccc-relay/chatgpt/008 after registration, before this run; not registered, never gated)
    print(f"SUPP minimum of the three A-C contrasts: all {min(R['p1c']):.6f}, unseen {min(R['p2c']):.6f}")
    for j in (1, 2, 3):
        a_items = [sum(x) / 4 for x in zip(*[R["pne"](c, "D") for c in cells[("A", j)]])]
        c_items = [sum(x) / 4 for x in zip(*[R["pne"](c, "D") for c in cells[("C", j)]])]
        print(f"SUPP j={j}: items with per-item m(A,j) - m(C,j) > 0: {sum(1 for x, y in zip(a_items, c_items) if x > y)}"
              f" of 24")
    for j in (1, 3):
        ua = [c for c in R["unseen"][("A", j)] if others_desc(c)]
        uc = [c for c in R["unseen"][("C", j)] if others_desc(c)]
        assert ua and uc
        d = R["m"](ua) - R["m"](uc)
        print(f"SUPP matched P2 check j={j}: other two letters displayed in descending order on both sides "
              f"(A side {len(ua)} conditions, C side {len(uc)}): m(A) - m(C) = {d:.6f}, sign "
              f"{'same' if (d > 0) == (R['p2c'][j - 1] > 0) else 'CHANGED'} vs P2")

    canon = {f"{c[0]}{c[1]}": {arm: [[round(x, 6) for x in p] for p in R["P"][(c, arm)]] for arm in ("D", "E")}
             for c in CONDS}
    dg = digest(canon)
    print(f"VERDICT {sum(held)} of 4 as registered")
    print("DIGEST", dg)
    if a.json:
        json.dump({"held": held, "digest": dg, "sabotage": a.sabotage,
                   "conditions": {f"{c[0]}{c[1]}": {"letters": LETTERS[c[0]], "order": ORDERS[c[1]],
                                                     "cell": cell(c), "seen_pi": seen_pi(c),
                                                     "D": raw[(c, "D")], "E": raw[(c, "E")]} for c in CONDS}},
                  open(a.json, "w"), indent=1)
    if RECORDED is not None:
        ok = (tuple(held), dg) == RECORDED  # exit 0 only on the recorded outcome (W4)
    else:
        ok = all(held) and not a.sabotage
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
