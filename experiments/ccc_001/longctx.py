"""CCC-001 long-context qualification harness. Registration: LONGCTX_PREREG.md (cf1fbcd); deviations D1-D2 in
LONGCTX_DEVIATIONS.md (633ed1e), committed before any model reading.

Development-only (C-EXPLORE). Qwen2.5-1.5B-Instruct did not qualify in stage Q, so this is a length diagnostic of
an unqualified model, not a qualification of a measured model. Stage Q's verdict does not change (M12).

The synthetic context, relabelings, probes and read-out are imported, not copied:
  longctx_feasibility.context / synthetic_turns / PIS / TARGETS / WINDOW   (registered construction)
  qdiag.explicit / keys / probe_msgs / readout                             (relabelings and read-out)
  relay_render.content(..., escape=False)                                  (the --sabotage-escape path only)

usage:
  python longctx.py --g0-only [--sabotage-escape]        # G0 at all three lengths, tokenizer only, no weights
  python longctx.py --length REF [--sabotage] [--json F]  # G0-G6 at REF (D1: the only length read this run)

Exit 0 only on the outcome pinned in RECORDED after the run.
"""
import argparse
import hashlib
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import longctx_feasibility as lf  # noqa: E402
import relay_render as rr  # noqa: E402
import render_feasibility as rf  # noqa: E402
from common import MODEL_DIR, digest, option_ids, render  # noqa: E402
from probes import ITEMS, OPTIONS  # noqa: E402
from qdiag import explicit, keys, probe_msgs  # noqa: E402

RECORDED = {  # pinned after the runs at d96634f (REF) and c537acb (g0); sabotage modes are never pinned, so they exit 1
    "g0": ((True, True, True), "fa5c56adae8c2c43aa231b9936de16473a1516a7e2f9876efac22305a1e09a9b"),
    "REF": ((True, True, True, True, True, False, False),
            "1ebd6751e49dcb09d4118dd86188efb9d7613b7631f8d6eb9f9a8c5916eb57c4"),
}

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
FEAS = os.path.join(ROOT, "results/ccc_001/longctx_feasibility.txt")
DAYS = {"REF": 44, "N016": 165, "STRESS": 340}  # from the committed feasibility output (D2)
IM_START, IM_END = lf.IM_START, lf.IM_END


def sha(b):
    return hashlib.sha256(b).hexdigest()


def committed_digests():
    """Parse the 18 committed cell digests and days from longctx_feasibility.txt (the handoff values)."""
    dig, days = {}, {}
    for line in open(FEAS):
        w = line.split()
        if len(w) > 4 and w[0].startswith("[") and w[1] == "target":
            days[w[0][1:-1]] = int(w[4])
        if "cell digest" in line:
            dig[(w[0][1:-1], w[2], int(w[3][2:]))] = w[-1]
    assert days == DAYS, (days, DAYS)
    assert len(dig) == 18
    return dig


def context(days, arm, k, escape=True):
    if escape:
        return lf.context(days, arm, k)
    m = [{"role": "user", "content": rr.content(lf.synthetic_turns(days), escape=False)},
         {"role": "assistant", "content": rf.ACK}]
    return m + (explicit(k) if arm == "E" else [])


def prompt_ids(tok, msgs):
    return tok(render(tok, msgs, gen=True), add_special_tokens=False).input_ids


def g0(tok, name, escape, committed):
    """Handoff check: transformers path reproduces the committed digests; no control tokens inside message 1."""
    days = DAYS[name]
    c1 = tok(context(days, "D", 0, escape)[0]["content"], add_special_tokens=False).input_ids
    nctl = c1.count(IM_START) + c1.count(IM_END)
    ok, lines, cells = nctl == 0, [], {}
    for arm in ("D", "E"):
        for k in lf.PIS:
            cell = [prompt_ids(tok, context(days, arm, k, escape) + pm) for pm in probe_msgs(k)]
            cells[(arm, k)] = cell
            dg = sha(json.dumps([sha(json.dumps(c, separators=(",", ":")).encode()) for c in cell]).encode())
            match = dg == committed[(name, arm, k)]
            n = [len(c) for c in cell]
            if arm == "D":
                match_len = min(n) >= lf.TARGETS[name] and max(n) <= lf.TARGETS[name] + lf.WINDOW
                ok &= match_len
            ok &= match
            lines.append(f"  [{name}] arm {arm} pi{k} tokens {min(n)}..{max(n)} digest {dg[:12]} "
                         f"{'matches' if match else 'DIFFERS from'} committed {committed[(name, arm, k)][:12]}")
    print(f"G0 [{name}]", "HELD" if ok else "REFUTED", f"6 cell digests and window; control tokens inside "
          f"message-1 content: {nctl} (= 0)")
    for ln in lines:
        print(ln)
    if not ok:
        first_difference(tok, name, escape)
    return ok, cells


def first_difference(tok, name, escape):
    """Print the first token at which the transformers path differs from the escaped jinja2 feasibility path."""
    _, jinja_ids, _ = lf.setup(MODEL_DIR)
    days = DAYS[name]
    a = prompt_ids(tok, context(days, "D", 0, escape) + probe_msgs(0)[0])
    b = jinja_ids(lf.context(days, "D", 0) + probe_msgs(0)[0])
    i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
    print(f"  [{name}] first differing token (arm D pi0 item 0) at position {i}: harness "
          f"{a[i:i + 3]} {tok.decode(a[i:i + 3])!r} vs feasibility {b[i:i + 3]} {tok.decode(b[i:i + 3])!r}; "
          f"lengths {len(a)} vs {len(b)}")


def read(model, ids, oid, sabotage, full_logits=False):
    import torch
    from qdiag import readout
    x = torch.tensor([ids])
    with torch.no_grad():
        logits = model(x).logits[0, -1] if full_logits else model(x, logits_to_keep=1).logits[0, -1]
    return readout(logits, oid, sabotage)


def rows(model, oid, cell, k, sabotage, full_logits=False):
    out = []
    for kl, ids in zip(keys(k), cell):
        p, mass = read(model, ids, oid, sabotage, full_logits)
        out.append({"key": kl, "p": p, "G": p[OPTIONS.index(kl)], "S": max(p), "mass": mass, "n": len(ids)})
    return out


def r6(rs):
    return [[round(x, 6) for x in r["p"]] for r in rs]


def finish(held, canon, mode, sabotage):
    dg = digest(canon)
    print(f"VERDICT {sum(held)} of {len(held)} as registered")
    print("DIGEST", dg)
    if mode in RECORDED:
        ok = (tuple(held), dg) == RECORDED[mode]
    else:
        ok = all(held) and not sabotage
    print("RECORDED", "match" if mode in RECORDED and ok else ("none pinned" if mode not in RECORDED else "MISMATCH"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g0-only", action="store_true")
    ap.add_argument("--sabotage-escape", action="store_true")
    ap.add_argument("--length", choices=["REF"], default="REF")  # D1: REF is the only length read in this run
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()

    from transformers import AutoTokenizer
    import transformers
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    committed = committed_digests()
    print("transformers", transformers.__version__, "| committed digests", len(committed), "| days", DAYS,
          "| escaping", "OFF (sabotage)" if a.sabotage_escape else "on")
    for f in ("tokenizer.json", "tokenizer_config.json", "config.json"):
        print(f, "sha256", sha(open(os.path.join(MODEL_DIR, f), "rb").read()))

    if a.g0_only:
        held = [g0(tok, name, not a.sabotage_escape, committed)[0] for name in DAYS]
        mode = "g0" + ("_sabotage_escape" if a.sabotage_escape else "")
        print("weights loaded: no")
        return finish(held, {"g0": held}, mode, a.sabotage_escape)

    name = a.length
    ok0, cells = g0(tok, name, not a.sabotage_escape, committed)
    if not ok0:
        print("G0 failed: stopping before loading the model")
        print(f"LONGEST QUALIFIED NONE")
        return 1

    import torch
    from transformers import AutoModelForCausalLM
    torch.manual_seed(0)
    torch.set_num_threads(os.cpu_count())
    model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, dtype=torch.bfloat16).eval()
    w = os.path.join(MODEL_DIR, "model.safetensors")
    print("weights sha256", sha(open(w, "rb").read()), "| torch", torch.__version__, "| threads",
          torch.get_num_threads())
    oid = option_ids(tok)
    L = model.config.max_position_embeddings
    print("option_token_ids", oid, "vocab", model.config.vocab_size, "L", L)

    # G1 fit: no prompt truncated or at/over L
    allids = [c for cell in cells.values() for c in cell]
    g1 = max(len(c) for c in allids) < L
    print("G1", "HELD" if g1 else "REFUTED", f"longest prompt {max(len(c) for c in allids)} tokens (< L {L}); "
          "no truncation is applied anywhere")

    res = {}
    for arm in ("D", "E"):
        for k in lf.PIS:
            res[(arm, k)] = rows(model, oid, cells[(arm, k)], k, a.sabotage)
            sys.stdout.flush()
    rep = rows(model, oid, cells[("D", 0)], 0, a.sabotage)
    full = rows(model, oid, cells[("D", 0)], 0, a.sabotage, full_logits=True)

    g2n = sum(1 for x, y in zip(r6(res[("D", 0)]), r6(rep)) if x == y)
    g2 = g2n == 24
    d2 = max(abs(u - v) for x, y in zip(res[("D", 0)], rep) for u, v in zip(x["p"], y["p"]))
    print("G2", "HELD" if g2 else "REFUTED", f"arm D pi0 read twice: equal to 6 dp on {g2n} of 24 (= 24), "
          f"max diff {d2:.6f}")
    g3n = sum(1 for x, y in zip(r6(res[("D", 0)]), r6(full)) if x == y)
    g3 = g3n == 24
    d3 = max(abs(u - v) for x, y in zip(res[("D", 0)], full) for u, v in zip(x["p"], y["p"]))
    print("G3", "HELD" if g3 else "REFUTED", f"arm D pi0 logits_to_keep=1 vs full logits: equal to 6 dp on {g3n} "
          f"of 24 (= 24), max diff {d3:.6f}")

    meds = {c: statistics.median(r["mass"] for r in v) for c, v in res.items()}
    g4 = all(m >= 0.90 for m in meds.values())
    print("G4", "HELD" if g4 else "REFUTED", "median letter mass per cell (>= 0.90 each): "
          + "  ".join(f"{arm}pi{k} {m:.4f}" for (arm, k), m in meds.items()))

    gains = [round(sum(r["G"] for r in res[("E", k)]) / 24 - sum(r["G"] for r in res[("D", k)]) / 24, 4)
             for k in lf.PIS]
    g5v = round(sum(gains) / 3, 4)
    g5 = g5v >= 0.10
    print("G5", "HELD" if g5 else "REFUTED", f"mean over pi0-pi2 of mean G(E)-G(D) = {g5v:.4f} (>= 0.10); "
          f"per pi {gains}")
    gE = [sum(res[("E", k)][i]["G"] for k in lf.PIS) / 3 for i in range(24)]
    gD = [sum(res[("D", k)][i]["G"] for k in lf.PIS) / 3 for i in range(24)]
    wins = sum(1 for x, y in zip(gE, gD) if x > y)
    g6 = wins >= 14
    print("G6", "HELD" if g6 else "REFUTED", f"items with pi-averaged G(E) > G(D): {wins} of 24 (>= 14)")

    held = [ok0, g1, g2, g3, g4, g5, g6]
    for (arm, k), v in res.items():
        mod = {L_: sum(1 for r in v if OPTIONS[r["p"].index(max(r["p"]))] == L_) for L_ in OPTIONS}
        print(f"REPORT [{name}] arm {arm} pi{k} keys {''.join(keys(k))}: mean S {statistics.mean(r['S'] for r in v):.4f} "
              f"mean G {statistics.mean(r['G'] for r in v):.4f} modal {mod} mean mass "
              f"{statistics.mean(r['mass'] for r in v):.4f} min mass {min(r['mass'] for r in v):.4f}")
    by_key = {}
    for i, (key, _, _) in enumerate(ITEMS):
        by_key.setdefault(key, []).append(gE[i] - gD[i])
    print("REPORT item gain by stage-Q key (pi-averaged G(E)-G(D)): "
          + "  ".join(f"{key} {statistics.mean(v):.4f} (n={len(v)})" for key, v in by_key.items()))
    for n_ in ("N016", "STRESS"):
        print(f"[{n_}] NOT RUN (deviation D1)")
    qualified = all(held)
    print("LONGEST QUALIFIED", "REF" if qualified else "NONE", "(only REF was read: D1)")
    if a.sabotage:
        print("SABOTAGE expected G4, G5 and G6 REFUTED:", (not g4) and (not g5) and (not g6))
    canon = {f"{arm}{k}": [[round(x, 4) for x in r["p"]] + [round(r["mass"], 4)] for r in v]
             for (arm, k), v in res.items()}
    canon["D0_repeat"] = [[round(x, 4) for x in r["p"]] for r in rep]
    canon["D0_full_logits"] = [[round(x, 4) for x in r["p"]] for r in full]
    if a.json:
        json.dump({"held": held, "sabotage": a.sabotage, "length": name, "days": DAYS[name],
                   "cells": {f"{arm}{k}": v for (arm, k), v in res.items()}, "D0_repeat": rep,
                   "D0_full_logits": full}, open(a.json, "w"), indent=1)
    return finish(held, canon, f"{name}" + ("_sabotage" if a.sabotage else ""), a.sabotage)


if __name__ == "__main__":
    sys.exit(main())
