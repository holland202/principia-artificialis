"""CCC-001 accept-shift decomposition. Registration: ACCBIAS_PREREG.md (commit f416f86).

Post-hoc reanalysis of stored readings, no model: does adding the explicit instruction (arm E vs arm D) raise the
probability of the letter meaning *accept* in every letter x slot cell (QORDER), and in every pi (LONGCTX REF)?
Development-only (C-EXPLORE). No earlier verdict changes whatever this prints (M12).

Usage:
  python3 experiments/ccc_001/accbias.py [--sabotage] [--json results/ccc_001/accbias.json]

Prints one HELD/REFUTED line per registered prediction P0-P3, `VERDICT n of 4 as registered` and a `DIGEST`.
Lines starting `REPORT` are registered as reported and never gated. Exit 0 only on the outcome pinned in RECORDED.
"""
import argparse
import ast
import hashlib
import json
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from probes import ITEMS, OPTIONS  # noqa: E402

RECORDED = None  # pinned after the run

RES = os.path.join(ROOT, "results", "ccc_001")
MEANINGS = ("accept", "reject", "notenough")
SEED, NSHUF = 20261122, 2000
NEAR_ZERO = 1e-4


def qdiag_literals():
    """KEY_MEANING and PI read from qdiag.py's source without importing it (it imports torch)."""
    tree = ast.parse(open(os.path.join(HERE, "qdiag.py")).read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("KEY_MEANING", "PI"):
                out[node.targets[0].id] = ast.literal_eval(node.value)
    return out["KEY_MEANING"], out["PI"]


KEY_MEANING, PI = qdiag_literals()
ITEM_MEANING = [KEY_MEANING[k] for k, _, _ in ITEMS]


def softmax(z):
    m = max(z)
    e = [math.exp(x - m) for x in z]
    s = sum(e)
    return [x / s for x in e]


def load():
    """Pairs: list of dicts {src, cond, item, letters, slot, pD, pE}. Fail closed on any key mismatch."""
    q = json.load(open(os.path.join(RES, "qorder.json")))["conditions"]
    pairs = []
    for cid, c in q.items():
        lam, order = c["letters"], c["order"]
        assert sorted(lam) == sorted(MEANINGS) and sorted(lam.values()) == list(OPTIONS), cid
        for i in range(24):
            for arm in ("D", "E"):
                assert c[arm][i]["key"] == lam[ITEM_MEANING[i]], (cid, arm, i)
            pairs.append({"src": "Q", "cond": cid, "item": i, "letters": lam,
                          "slot": {m: order.index(m) + 1 for m in MEANINGS},
                          "pD": softmax(c["D"][i]["z"]), "pE": softmax(c["E"][i]["z"]),
                          "keyp": (c["D"][i]["key"], c["E"][i]["key"])})
    lc = json.load(open(os.path.join(RES, "longctx_ref.json")))["cells"]
    for k in (0, 1, 2):
        lam = PI[k]
        for i in range(24):
            for arm in ("D", "E"):
                assert lc[f"{arm}{k}"][i]["key"] == lam[ITEM_MEANING[i]], (k, arm, i)
            pairs.append({"src": "L", "cond": k, "item": i, "letters": lam,
                          "slot": {m: OPTIONS.index(lam[m]) + 1 for m in MEANINGS},
                          "pD": lc[f"D{k}"][i]["p"], "pE": lc[f"E{k}"][i]["p"],
                          "GD": lc[f"D{k}"][i]["G"], "GE": lc[f"E{k}"][i]["G"]})
    return pairs


def delta(pr, m, letter=None):
    j = OPTIONS.index(letter if letter is not None else pr["letters"][m])
    return pr["pE"][j] - pr["pD"][j]


def item_equal_mean(vals):
    """vals: list of (item, value). Mean over items of each item's mean."""
    by = {}
    for i, v in vals:
        by.setdefault(i, []).append(v)
    return sum(sum(v) / len(v) for v in by.values()) / len(by)


def cell_table(Q, m):
    """9 cells (letter of m, slot of m) -> dict with mean, item up/down, pair up/down/zero, other-meaning means."""
    out = {}
    for L in OPTIONS:
        for s in (1, 2, 3):
            ps = [p for p in Q if p["letters"][m] == L and p["slot"][m] == s]
            vals = [(p["item"], delta(p, m)) for p in ps]
            items = {}
            for i, v in vals:
                items.setdefault(i, []).append(v)
            im = [sum(v) / len(v) for v in items.values()]
            out[(L, s)] = {"mean": item_equal_mean(vals), "n": len(ps),
                           "items_up": sum(1 for x in im if x > 0), "items_down": sum(1 for x in im if x < 0),
                           "pairs_up": sum(1 for _, v in vals if v > 0), "pairs_down": sum(1 for _, v in vals if v < 0),
                           "pairs_zero": sum(1 for _, v in vals if v == 0),
                           "other": {o: item_equal_mean([(p["item"], delta(p, o)) for p in ps])
                                     for o in MEANINGS if o != m}}
    return out


def ranges(t):
    lm = {L: sum(t[(L, s)]["mean"] for s in (1, 2, 3)) / 3 for L in OPTIONS}
    sm = {s: sum(t[(L, s)]["mean"] for L in OPTIONS) / 3 for s in (1, 2, 3)}
    return lm, sm, max(lm.values()) - min(lm.values()), max(sm.values()) - min(sm.values())


def shuffle_null(Q):
    rng = random.Random(SEED)
    order = sorted(Q, key=lambda p: (p["cond"], p["item"]))  # qorder.json order is sorted condition ids
    mins, allpos = [], 0
    for _ in range(NSHUF):
        cells = {}
        for p in order:
            L = OPTIONS[rng.randrange(3)]
            s = p["slot"][{v: k for k, v in p["letters"].items()}[L]]
            cells.setdefault((L, s), []).append((p["item"], delta(p, None, L)))
        vals = [item_equal_mean(v) for v in cells.values()]
        mins.append(min(vals))
        allpos += int(len(vals) == 9 and all(v > 0 for v in vals))
    return mins, allpos


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def p0(pairs):
    Q = [p for p in pairs if p["src"] == "Q"]
    L = [p for p in pairs if p["src"] == "L"]
    lines, ok = [], []
    run = open(os.path.join(RES, "qorder_run.txt")).read().splitlines()
    dl = [x for x in run if re.match(r"REPORT   letter [ABC]: j=1 [0-9.]+ \[", x)]
    el = [x for x in run if re.match(r"REPORT   letter [ABC]: j=1 [0-9.]+ gain", x)]
    assert len(dl) == 3 and len(el) == 3
    # (a) arm-D cell means of p(not-enough letter)
    da = 0.0
    for x in dl:
        Lt = x.split("letter ")[1][0]
        for s, v in re.findall(r"j=(\d) ([0-9.]+) \[", x):
            ps = [p for p in Q if p["letters"]["notenough"] == Lt and p["slot"]["notenough"] == int(s)]
            j = OPTIONS.index(Lt)
            mine = sum(p["pD"][j] for p in ps) / len(ps)
            da = max(da, abs(mine - float(v)))
    ok.append(da <= 1e-6)
    lines.append(f"P0a arm-D not-enough cell means vs qorder_run.txt: max |diff| {da:.2e} (<= 1e-6)")
    # (b) arm-E gains and E>D counts per not-enough cell
    db, cnt_ok = 0.0, True
    for x in el:
        Lt = x.split("letter ")[1][0]
        for s, g, w in re.findall(r"j=(\d) [0-9.]+ gain ([+-][0-9.]+) E>D (\d+)/96", x):
            ps = [p for p in Q if p["letters"]["notenough"] == Lt and p["slot"]["notenough"] == int(s)]
            gD = [p["pD"][OPTIONS.index(p["keyp"][0])] for p in ps]
            gE = [p["pE"][OPTIONS.index(p["keyp"][1])] for p in ps]
            db = max(db, abs(sum(gE) / len(gE) - sum(gD) / len(gD) - float(g)))
            cnt_ok &= sum(1 for a, b in zip(gE, gD) if a > b) == int(w)
    ok.append(db <= 5e-5 and cnt_ok)
    lines.append(f"P0b arm-E gains per not-enough cell: max |diff| {db:.2e} (<= 5e-5), E>D counts equal: {cnt_ok}")
    # (c) LONGCTX per-pi gains
    lr = open(os.path.join(RES, "longctx_ref_run.txt")).read()
    want = [float(v) for v in re.search(r"G5 \w+ .*per pi \[([^\]]+)\]", lr).group(1).split(",")]
    got = [round(sum(p["GE"] for p in L if p["cond"] == k) / 24 - sum(p["GD"] for p in L if p["cond"] == k) / 24, 4)
           for k in (0, 1, 2)]
    ok.append(got == want)
    lines.append(f"P0c LONGCTX per-pi gains {got} vs longctx_ref_run.txt {want}: equal {got == want}")
    # (d) bookkeeping
    bq = max(abs(sum(delta(p, m) for m in MEANINGS)) for p in Q)
    bl = max(abs(sum(delta(p, m) for m in MEANINGS)) for p in L)
    ok.append(bq <= 1e-12 and bl <= 5e-6)
    lines.append(f"P0d bookkeeping |d_acc+d_rej+d_ne| max: QORDER {bq:.2e} (<= 1e-12), LONGCTX {bl:.2e} (<= 5e-6)")
    # (e) identity: E := D gives exactly zero everywhere
    ident = [dict(p, pE=p["pD"]) for p in pairs]
    zq = [c["mean"] for m in MEANINGS for c in cell_table([p for p in ident if p["src"] == "Q"], m).values()]
    zl = [item_equal_mean([(p["item"], delta(p, m)) for p in ident if p["src"] == "L" and p["cond"] == k])
          for k in (0, 1, 2) for m in MEANINGS]
    ze = len(zq) == 27 and len(zl) == 9 and all(v == 0.0 for v in zq + zl)
    ok.append(ze)
    lines.append(f"P0e identity E:=D: {len(zq)} QORDER and {len(zl)} LONGCTX cell values exactly 0: {ze}")
    return all(ok), lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true", help="replace every arm-E reading by its arm-D reading")
    ap.add_argument("--json")
    a = ap.parse_args()
    pairs = load()
    g0, l0 = p0(pairs)
    if a.sabotage:
        pairs = [dict(p, pE=p["pD"]) for p in pairs]
    Q = [p for p in pairs if p["src"] == "Q"]
    L = [p for p in pairs if p["src"] == "L"]
    T = {m: cell_table(Q, m) for m in MEANINGS}
    acc = T["accept"]
    lm, sm, lr, sr = ranges(acc)
    lc = {k: {m: item_equal_mean([(p["item"], delta(p, m)) for p in L if p["cond"] == k]) for m in MEANINGS}
          for k in (0, 1, 2)}
    lcounts = {}
    for k in (0, 1, 2):
        v = [delta(p, "accept") for p in L if p["cond"] == k]
        lcounts[k] = (sum(1 for x in v if x > 0), sum(1 for x in v if x < 0))
    held = [g0, False, False, False]
    for x in l0:
        print(x)
    print(f"P0 {'HELD' if g0 else 'REFUTED'} reproduction and bookkeeping gate (a-e all required)")
    mincell = min(acc, key=lambda c: acc[c]["mean"])
    if g0:
        held[1] = any(c["mean"] <= 0 for c in acc.values())
        held[2] = lr > sr
        held[3] = all(lc[k]["accept"] > 0 for k in (0, 1, 2))
        print(f"P1 {'HELD' if held[1] else 'REFUTED'} QORDER accept cells with d_acc <= 0: "
              f"{sum(1 for c in acc.values() if c['mean'] <= 0)} of 9 (>= 1); smallest {acc[mincell]['mean']:.6f} "
              f"at letter {mincell[0]} slot {mincell[1]}")
        print(f"P2 {'HELD' if held[2] else 'REFUTED'} d_acc letter range {lr:.6f} > slot range {sr:.6f}")
        print(f"P3 {'HELD' if held[3] else 'REFUTED'} LONGCTX REF d_acc per pi "
              f"[{', '.join(f'{lc[k]['accept']:.6f}' for k in (0, 1, 2))}] (> 0 each)")
    else:
        for i in (1, 2, 3):
            print(f"P{i} NOT READ (P0 failed)")
    for m in MEANINGS:
        print(f"REPORT d_{m} by its own letter x slot (cell mean; items up/down of 24; pairs up/down/zero of 96):")
        for Lt in OPTIONS:
            print(f"REPORT   letter {Lt}: " + "  ".join(
                f"s={s} {T[m][(Lt, s)]['mean']:+.6f} it {T[m][(Lt, s)]['items_up']}/{T[m][(Lt, s)]['items_down']} "
                f"pr {T[m][(Lt, s)]['pairs_up']}/{T[m][(Lt, s)]['pairs_down']}/{T[m][(Lt, s)]['pairs_zero']}"
                for s in (1, 2, 3)))
    print("REPORT d_acc letter means " + " ".join(f"{k} {v:+.6f}" for k, v in lm.items())
          + " | slot means " + " ".join(f"{k} {v:+.6f}" for k, v in sm.items()))
    print("REPORT inside each accept cell, where the change comes from (d_acc, d_rej, d_ne):")
    for Lt in OPTIONS:
        print(f"REPORT   letter {Lt}: " + "  ".join(
            f"s={s} {acc[(Lt, s)]['mean']:+.6f} {acc[(Lt, s)]['other']['reject']:+.6f} "
            f"{acc[(Lt, s)]['other']['notenough']:+.6f}" for s in (1, 2, 3)))
    mabs = min(abs(c["mean"]) for c in acc.values())
    print(f"REPORT min |d_acc cell| {mabs:.6f}{' NEAR ZERO' if mabs < NEAR_ZERO else ''}")
    for k in (0, 1, 2):
        print(f"REPORT LONGCTX pi{k} (accept={PI[k]['accept']}): d_acc {lc[k]['accept']:+.6f} "
              f"d_rej {lc[k]['reject']:+.6f} d_ne {lc[k]['notenough']:+.6f} | items d_acc up/down "
              f"{lcounts[k][0]}/{lcounts[k][1]} of 24")
    mins, allpos = shuffle_null(Q)
    obs = acc[mincell]["mean"]
    ge = sum(1 for x in mins if x >= obs)
    print(f"REPORT shuffle null ({NSHUF} shuffles, seed {SEED}, same draw for E and D): observed min {obs:+.6f}; "
          f"shuffled min p5 {pct(mins, 0.05):+.6f} p50 {pct(mins, 0.5):+.6f} p95 {pct(mins, 0.95):+.6f}; "
          f"fraction min >= observed {ge}/{NSHUF}; fraction all 9 > 0 {allpos}/{NSHUF}")
    canon = {"held": held,
             "cells": {m: {f"{c[0]}{c[1]}": round(v["mean"], 6) for c, v in T[m].items()} for m in MEANINGS},
             "longctx": {str(k): {m: round(v, 6) for m, v in lc[k].items()} for k in lc},
             "per_item": [[p["src"], str(p["cond"]), p["item"], [round(delta(p, m), 6) for m in MEANINGS]]
                          for p in pairs]}
    dg = hashlib.sha256(json.dumps(canon, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(f"VERDICT {sum(held)} of 4 as registered")
    print(f"DIGEST {dg}")
    if a.json:
        json.dump(dict(canon, sabotage=a.sabotage, digest=dg,
                       shuffle={"seed": SEED, "n": NSHUF, "observed_min": round(obs, 6),
                                "ge": ge, "allpos": allpos}), open(a.json, "w"), indent=1)
    sys.exit(0 if RECORDED is not None and (tuple(held), dg) == RECORDED else 1)


if __name__ == "__main__":
    main()
