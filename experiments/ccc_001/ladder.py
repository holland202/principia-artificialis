"""CCC-001 LADDER. Registration: LADDER_PREREG.md (commit 536e49c).

Post-hoc reanalysis of stored QORDER logits, no model. Nested layout models for y = Delta_M (p_E - p_D of the
meaning's printed letter), one row per (condition, item, meaning):
  R0 additive M + L + S (6 cols), R1 + all two-ways (18), R2 + M x L x S (26); R3 layout ceiling (72, reported).
Columns are sum-to-zero effect codes, centred within each pair. Leave-one-item-out held-out MSE.
Development-only (C-EXPLORE). No earlier verdict changes whatever this prints (M12).

Usage:
  python3 experiments/ccc_001/ladder.py [--sabotage] [--json results/ccc_001/ladder.json]

Prints one HELD/REFUTED line per registered prediction P0-P1, `VERDICT n of 2 as registered` and a `DIGEST`.
Lines starting `REPORT` are registered as reported and never gated. Exit 0 only on the outcome pinned in RECORDED.
"""
import argparse
import hashlib
import json
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from accbias import MEANINGS, RES, delta, load  # noqa: E402
from apen import cell_means, item_tables  # noqa: E402
from probes import OPTIONS  # noqa: E402

RECORDED = None  # pinned after the run

SLOTS = (1, 2, 3)
SEED_SYN = 20261124
TIE = 1e-15
NAMES = ("R0 additive", "R1 two-way", "R2 MxLxS", "R3 layout ceiling")


def eff(v, levels):
    return [1.0 if v == levels[k] else (-1.0 if v == levels[2] else 0.0) for k in (0, 1)]


def rows_of(Q):
    """Rows in (pair, meaning) order: (cond, item, meaning, letter, slot, y)."""
    out = []
    for p in sorted(Q, key=lambda p: (p["cond"], p["item"])):
        for m in MEANINGS:
            out.append((p["cond"], p["item"], m, p["letters"][m], p["slot"][m], delta(p, m)))
    return out


def centre(X):
    X3 = X.reshape(-1, 3, X.shape[1])
    return (X3 - X3.mean(axis=1, keepdims=True)).reshape(-1, X.shape[1])


def design(rows, rung):
    if rung == 3:
        conds = sorted({r[0] for r in rows})
        X = np.zeros((len(rows), 3 * len(conds)))
        for j, r in enumerate(rows):
            X[j, conds.index(r[0]) * 3 + MEANINGS.index(r[2])] = 1.0
        return centre(X)
    out = []
    for r in rows:
        a, b, d = eff(r[2], MEANINGS), eff(r[3], OPTIONS), eff(r[4], SLOTS)
        cols = a + b + d
        if rung >= 1:
            cols += [x * y for x in a for y in b] + [x * y for x in a for y in d] + [x * y for x in b for y in d]
        if rung >= 2:
            cols += [x * y * z for x in a for y in b for z in d]
        out.append(cols)
    return centre(np.array(out))


def fit(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def evaluate(Xs, y, items):
    """Per rung: in-sample residual, held-out squared errors per item (LOIO)."""
    out = []
    for X in Xs:
        res_in = y - X @ fit(X, y)
        per_item = {}
        for i in sorted(set(items)):
            tr, te = items != i, items == i
            pred = X[te] @ fit(X[tr], y[tr])
            per_item[int(i)] = float(np.mean((y[te] - pred) ** 2))
        out.append({"res_in": res_in, "mse_i": per_item, "mse": float(np.mean(list(per_item.values())))})
    return out


def split_rss(res, rows):
    """Layout part: 24 x sum over (cond, meaning) of the item-mean residual squared. Item part: the rest."""
    by = {}
    for r, e in zip(rows, res):
        by.setdefault((r[0], r[2]), []).append(e)
    lay = sum(len(v) * (sum(v) / len(v)) ** 2 for v in by.values())
    tot = float(np.sum(res ** 2))
    return lay, tot - lay


def synthetic(Xs, items):
    """P0(d): noiseless fixtures y = X_k beta for k = 0, 1, 2. Returns (ok, lines)."""
    rng = random.Random(SEED_SYN)
    ok, lines = True, []
    for k in (0, 1, 2):
        beta = np.array([rng.uniform(-0.1, 0.1) for _ in range(Xs[k].shape[1])])
        ys = Xs[k] @ beta
        ev = evaluate(Xs, ys, items)
        parts = []
        for j in range(4):
            rss = float(np.sum(ev[j]["res_in"] ** 2))
            if j >= k:
                good = rss <= 1e-20 and ev[j]["mse"] <= 1e-20
            else:
                good = ev[j]["mse"] >= 1e-8
            if j <= 2:
                ok &= good
            parts.append(f"R{j} rss {rss:.2e} mse {ev[j]['mse']:.2e}{'' if good else ' FAIL'}")
        lines.append(f"P0d synthetic k={k}: " + "; ".join(parts))
    return ok, lines


def p0(Q, rows, Xs, items):
    lines, ok = [], []
    y = np.array([r[5] for r in rows])
    ps = np.abs(y.reshape(-1, 3).sum(axis=1)).max()
    ok.append(len(rows) == 2592 and ps <= 1e-9)
    lines.append(f"P0a rows {len(rows)} (2592); max |pair sum of y| {ps:.2e} (<= 1e-9)")
    rk = [int(np.linalg.matrix_rank(X)) for X in Xs]
    ok.append(rk == [6, 18, 26, 72])
    lines.append(f"P0b centred ranks {rk} (want [6, 18, 26, 72]); columns {[X.shape[1] for X in Xs]}")
    pub = json.load(open(os.path.join(RES, "accbias.json")))["cells"]
    da = max(abs(v - pub[m][f"{L}{s}"]) for m in MEANINGS for (L, s), v in cell_means(item_tables(Q, m)).items())
    ok.append(da <= 1e-6)
    lines.append(f"P0c 27 rebuilt cell means vs accbias.json: max |diff| {da:.2e} (<= 1e-6)")
    sok, sl = synthetic(Xs, items)
    ok.append(sok)
    lines += sl
    zero = np.zeros(len(rows))
    ident = rows_of([dict(p, pE=p["pD"]) for p in Q])
    yz = np.array([r[5] for r in ident])
    ev = evaluate(Xs, yz, items)
    mx = max(max(float(np.max(np.abs(X @ fit(X, yz)))) for X in Xs), max(e["mse"] for e in ev))
    ok.append(bool(np.all(yz == zero)) and mx <= 1e-30)
    lines.append(f"P0e identity E:=D: max |fitted| or MSE over 4 rungs {mx:.2e} (<= 1e-30)")
    return all(ok), lines


def counts(xs):
    xs = list(xs)
    return f"{sum(1 for x in xs if x > TIE)}/{sum(1 for x in xs if x < -TIE)}/{sum(1 for x in xs if abs(x) <= TIE)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true", help="replace every arm-E reading by its arm-D reading")
    ap.add_argument("--json")
    a = ap.parse_args()
    Q = [p for p in load() if p["src"] == "Q"]
    rows = rows_of(Q)
    items = np.array([r[1] for r in rows])
    Xs = [design(rows, k) for k in range(4)]
    g0, l0 = p0(Q, rows, Xs, items)
    if a.sabotage:
        Q = [dict(p, pE=p["pD"]) for p in Q]
        rows = rows_of(Q)
    y = np.array([r[5] for r in rows])
    ev = evaluate(Xs, y, items)
    mse = [e["mse"] for e in ev]
    d01 = {i: ev[0]["mse_i"][i] - ev[1]["mse_i"][i] for i in ev[0]["mse_i"]}
    d12 = {i: ev[1]["mse_i"][i] - ev[2]["mse_i"][i] for i in ev[0]["mse_i"]}
    d23 = {i: ev[2]["mse_i"][i] - ev[3]["mse_i"][i] for i in ev[0]["mse_i"]}
    D01, D12, D23 = mse[0] - mse[1], mse[1] - mse[2], mse[2] - mse[3]
    held = [g0, False]
    for x in l0:
        print(x)
    print(f"P0 {'HELD' if g0 else 'REFUTED'} rows, ranks, rebuild, synthetic and identity gate (a-e all required)")
    npos = sum(1 for v in d01.values() if v > TIE)
    if g0:
        held[1] = D01 > 0 and npos >= 13
        print(f"P1 {'HELD' if held[1] else 'REFUTED'} two-way beats additive held out: D01 {D01:+.9f} (> 0); "
              f"items with D01(i) > 0: {npos} of 24 (>= 13)")
    else:
        print("P1 NOT READ (P0 failed)")
    for k in range(4):
        print(f"REPORT {NAMES[k]}: held-out MSE {mse[k]:.9f} RMSE {mse[k] ** 0.5:.6f}")
    print(f"REPORT D01 (R0 - R1) {D01:+.9f} items +/-/tied {counts(d01.values())}")
    print(f"REPORT D12 (R1 - R2) {D12:+.9f} items +/-/tied {counts(d12.values())}")
    print(f"REPORT D23 (R2 - R3) {D23:+.9f} items +/-/tied {counts(d23.values())}")
    g02 = mse[0] - mse[2]
    if g02 > 0:
        print(f"REPORT gain fraction F = D01 / (MSE0 - MSE2) = {D01:+.9f} / {g02:+.9f} = {D01 / g02:.6f}")
    else:
        print(f"REPORT MSE0 - MSE2 {g02:+.9f}: no positive gain to apportion")
    if D12 < 0:
        print("REPORT two-way beats saturated")
    for k in range(4):
        lay, it = split_rss(ev[k]["res_in"], rows)
        print(f"REPORT in-sample {NAMES[k]}: RSS {lay + it:.9f} = layout part {lay:.9f} + item part {it:.9f}")
    b0 = fit(Xs[0], y)
    me = list(b0[0:2]) + [-(b0[0] + b0[1])]
    le = list(b0[2:4]) + [-(b0[2] + b0[3])]
    se = list(b0[4:6]) + [-(b0[4] + b0[5])]
    print("REPORT additive coefficients (all 24 items): meaning "
          + " ".join(f"{m} {v:+.6f}" for m, v in zip(MEANINGS, me)) + " | letter "
          + " ".join(f"{L} {v:+.6f}" for L, v in zip(OPTIONS, le)) + " | slot "
          + " ".join(f"{s} {v:+.6f}" for s, v in zip(SLOTS, se)))
    canon = {"held": held, "mse_i": [[round(ev[k]["mse_i"][i], 9) for i in sorted(ev[k]["mse_i"])] for k in range(4)]}
    dg = hashlib.sha256(json.dumps(canon, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(f"VERDICT {sum(held)} of 2 as registered")
    print(f"DIGEST {dg}")
    if a.json:
        json.dump(dict(canon, sabotage=a.sabotage, digest=dg, mse=[round(x, 9) for x in mse],
                       D01=round(D01, 9), D12=round(D12, 9), D23=round(D23, 9),
                       additive={"meaning": [round(v, 6) for v in me], "letter": [round(v, 6) for v in le],
                                 "slot": [round(v, 6) for v in se]}), open(a.json, "w"), indent=1)
    sys.exit(0 if RECORDED is not None and (tuple(held), dg) == RECORDED else 1)


if __name__ == "__main__":
    main()
