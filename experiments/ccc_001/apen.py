"""CCC-001 A-penalty contrast. Registration: APEN_PREREG.md (commit f58daf6).

Post-hoc reanalysis of stored QORDER logits, no model. For each meaning M and item i:
  pen_M(s,i) = d_M(A,s,i) - (d_M(B,s,i) + d_M(C,s,i))/2
  J12 = pen1 - pen2, J13 = pen1 - pen3, I = pen1 - (pen2 + pen3)/2
Development-only (C-EXPLORE). No earlier verdict changes whatever this prints (M12).

Usage:
  python3 experiments/ccc_001/apen.py [--sabotage] [--json results/ccc_001/apen.json]

Prints one HELD/REFUTED line per registered prediction P0-P3, `VERDICT n of 4 as registered` and a `DIGEST`.
Lines starting `REPORT` are registered as reported and never gated. Exit 0 only on the outcome pinned in RECORDED.
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from accbias import MEANINGS, RES, delta, load  # noqa: E402
from probes import OPTIONS  # noqa: E402

RECORDED = None  # pinned after the run

SLOTS = (1, 2, 3)
SEED_SHUF, NSHUF = 20261122, 2000
SEED_SYN, KAPPA = 20261123, 0.05
TIE = 1e-12


def item_tables(Q, m):
    """d[i][(L, s)] = mean of delta_m over the pairs of item i where m is printed as L in slot s."""
    acc = {}
    for p in Q:
        acc.setdefault(p["item"], {}).setdefault((p["letters"][m], p["slot"][m]), []).append(delta(p, m))
    return {i: {c: sum(v) / len(v) for c, v in t.items()} for i, t in acc.items()}


def contrasts(d):
    """d: {(L, s): value}. Returns pen per slot, J12, J13, I."""
    pen = {s: d[("A", s)] - 0.5 * (d[("B", s)] + d[("C", s)]) for s in SLOTS}
    return {"pen": pen, "J12": pen[1] - pen[2], "J13": pen[1] - pen[3], "I": pen[1] - 0.5 * (pen[2] + pen[3])}


def per_item(tabs):
    return {i: contrasts(t) for i, t in sorted(tabs.items())}


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def sign_counts(xs):
    xs = list(xs)
    return (sum(1 for x in xs if x > TIE), sum(1 for x in xs if x < -TIE), sum(1 for x in xs if abs(x) <= TIE))


def cell_means(tabs):
    return {c: mean(t[c] for t in tabs.values()) for c in next(iter(tabs.values()))}


def all_values(ci):
    for c in ci.values():
        yield from c["pen"].values()
        yield c["J12"]
        yield c["J13"]
        yield c["I"]


def synthetic():
    """P0(c): additive tables, then injected interactions. Returns (ok, lines)."""
    rng = random.Random(SEED_SYN)
    u = [rng.uniform(-0.3, 0.3) for _ in range(24)]
    a = {L: rng.uniform(-0.3, 0.3) for L in OPTIONS}
    b = {s: rng.uniform(-0.3, 0.3) for s in SLOTS}
    base = {i: {(L, s): u[i] + a[L] + b[s] for L in OPTIONS for s in SLOTS} for i in range(24)}

    def inject(extra):
        return {i: {c: v + extra.get(c, 0.0) for c, v in t.items()} for i, t in base.items()}

    cases = [("additive", base, (0.0, 0.0, 0.0)),
             ("A1+k", inject({("A", 1): KAPPA}), (KAPPA, KAPPA, KAPPA)),
             ("A2+k,A3-k", inject({("A", 2): KAPPA, ("A", 3): -KAPPA}), (0.0, -KAPPA, KAPPA))]
    ok, lines = True, []
    for name, tabs, (wi, w12, w13) in cases:
        ci = per_item(tabs)
        err = max(max(abs(c["I"] - wi), abs(c["J12"] - w12), abs(c["J13"] - w13)) for c in ci.values())
        ok &= err <= 1e-12
        lines.append(f"P0c synthetic {name}: want I {wi:+.2f} J12 {w12:+.2f} J13 {w13:+.2f}; "
                     f"max |err| over 24 items {err:.2e} (<= 1e-12)")
    return ok, lines


def p0(Q):
    lines, ok = [], []
    pub = json.load(open(os.path.join(RES, "accbias.json")))["cells"]
    da = 0.0
    for m in MEANINGS:
        cm = cell_means(item_tables(Q, m))
        for (L, s), v in cm.items():
            da = max(da, abs(v - pub[m][f"{L}{s}"]))
    ok.append(da <= 1e-6)
    lines.append(f"P0a 27 rebuilt cell means vs accbias.json: max |diff| {da:.2e} (<= 1e-6)")
    ident = [dict(p, pE=p["pD"]) for p in Q]
    zs = [v for m in MEANINGS for v in all_values(per_item(item_tables(ident, m)))]
    zc = [v for m in MEANINGS for v in contrasts(cell_means(item_tables(ident, m))).values()
          for v in (v.values() if isinstance(v, dict) else [v])]
    zb = all(v == 0.0 for v in zs + zc)
    ok.append(zb)
    lines.append(f"P0b identity E:=D: {len(zs)} per-item and {len(zc)} aggregate contrasts exactly 0: {zb}")
    sok, sl = synthetic()
    ok.append(sok)
    lines += sl
    dl = 0.0
    for m in MEANINGS:
        tabs = item_tables(Q, m)
        dl = max(dl, abs(contrasts(cell_means(tabs))["I"] - mean(c["I"] for c in per_item(tabs).values())))
    ok.append(dl <= 1e-12)
    lines.append(f"P0d linearity: |I from cells - mean item I| max {dl:.2e} (<= 1e-12)")
    return all(ok), lines


def shuffle_null(Q):
    rng = random.Random(SEED_SHUF)
    order = sorted(Q, key=lambda p: (p["cond"], p["item"]))
    out = []
    for _ in range(NSHUF):
        cells = {}
        for p in order:
            L = OPTIONS[rng.randrange(3)]
            s = p["slot"][{v: k for k, v in p["letters"].items()}[L]]
            cells.setdefault((L, s), {}).setdefault(p["item"], []).append(delta(p, None, L))
        cm = {c: mean(mean(v) for v in by.values()) for c, by in cells.items()}
        out.append(contrasts(cm)["I"] if len(cm) == 9 else float("nan"))
    return out


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true", help="replace every arm-E reading by its arm-D reading")
    ap.add_argument("--json")
    a = ap.parse_args()
    Q = [p for p in load() if p["src"] == "Q"]
    g0, l0 = p0(Q)
    if a.sabotage:
        Q = [dict(p, pE=p["pD"]) for p in Q]
    R = {}
    for m in MEANINGS:
        tabs = item_tables(Q, m)
        ci = per_item(tabs)
        R[m] = {"ci": ci, "cm": cell_means(tabs),
                "pen": {s: mean(c["pen"][s] for c in ci.values()) for s in SLOTS},
                **{k: mean(c[k] for c in ci.values()) for k in ("J12", "J13", "I")}}
        R[m]["penbar"] = mean(R[m]["pen"].values())
    held = [g0, False, False, False]
    for x in l0:
        print(x)
    print(f"P0 {'HELD' if g0 else 'REFUTED'} rebuild, identity, synthetic and linearity gate (a-d all required)")
    ca = R["accept"]["ci"]
    nI = sign_counts(c["I"] for c in ca.values())
    n12 = sign_counts(c["J12"] for c in ca.values())
    n13 = sign_counts(c["J13"] for c in ca.values())
    if g0:
        held[1] = nI[0] >= 13
        held[2] = n12[0] >= 13 and n13[0] >= 13
        held[3] = all(R[m]["penbar"] < 0 for m in MEANINGS)
        print(f"P1 {'HELD' if held[1] else 'REFUTED'} accept items with I > 0: {nI[0]} of 24 (>= 13); "
              f"negative {nI[1]}, tied {nI[2]}")
        print(f"P2 {'HELD' if held[2] else 'REFUTED'} accept items with J12 > 0: {n12[0]} of 24, "
              f"J13 > 0: {n13[0]} of 24 (each >= 13)")
        print(f"P3 {'HELD' if held[3] else 'REFUTED'} pen-bar < 0 for all three meanings: "
              + ", ".join(f"{m} {R[m]['penbar']:+.6f}" for m in MEANINGS))
    else:
        for i in (1, 2, 3):
            print(f"P{i} NOT READ (P0 failed)")
    for m in MEANINGS:
        r, ci = R[m], R[m]["ci"]
        print(f"REPORT {m}: pen1 {r['pen'][1]:+.6f} pen2 {r['pen'][2]:+.6f} pen3 {r['pen'][3]:+.6f} "
              f"pen-bar {r['penbar']:+.6f} | J12 {r['J12']:+.6f} J13 {r['J13']:+.6f} I {r['I']:+.6f}")
        print(f"REPORT   {m} item counts +/-/tied: "
              + " ".join(f"pen{s} {'/'.join(map(str, sign_counts(c['pen'][s] for c in ci.values())))}" for s in SLOTS)
              + " " + " ".join(f"{k} {'/'.join(map(str, sign_counts(c[k] for c in ci.values())))}"
                               for k in ("J12", "J13", "I")))
        lo = min(ci, key=lambda i: ci[i]["I"])
        hi = max(ci, key=lambda i: ci[i]["I"])
        print(f"REPORT   {m} item I range: min {ci[lo]['I']:+.6f} (item {lo}) max {ci[hi]['I']:+.6f} (item {hi})")
        print(f"REPORT   {m} within-row first-slot contrast d(L,1) - mean(d(L,2), d(L,3)): "
              + " ".join(f"{L} {r['cm'][(L, 1)] - 0.5 * (r['cm'][(L, 2)] + r['cm'][(L, 3)]):+.6f}" for L in OPTIONS))
    sh = shuffle_null(Q)
    good = [x for x in sh if x == x]
    obs = R["accept"]["I"]
    ge = sum(1 for x in good if abs(x) >= abs(obs))
    print(f"REPORT shuffle null ({NSHUF} shuffles, seed {SEED_SHUF}, same draw for E and D; {len(good)} with all 9 "
          f"cells): observed I_acc {obs:+.6f}; shuffled I p5 {pct(good, 0.05):+.6f} p50 {pct(good, 0.5):+.6f} "
          f"p95 {pct(good, 0.95):+.6f}; fraction |I| >= |observed| {ge}/{len(good)}")
    print("REPORT no equivalence margin is registered, so 'I ~ 0' is not decided")
    canon = {"held": held,
             "per_item": {m: [[i, [round(c["pen"][s], 6) for s in SLOTS], round(c["J12"], 6), round(c["J13"], 6),
                               round(c["I"], 6)] for i, c in R[m]["ci"].items()] for m in MEANINGS}}
    dg = hashlib.sha256(json.dumps(canon, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(f"VERDICT {sum(held)} of 4 as registered")
    print(f"DIGEST {dg}")
    if a.json:
        json.dump(dict(canon, sabotage=a.sabotage, digest=dg,
                       aggregate={m: {"pen": [round(R[m]["pen"][s], 6) for s in SLOTS],
                                      "penbar": round(R[m]["penbar"], 6), "J12": round(R[m]["J12"], 6),
                                      "J13": round(R[m]["J13"], 6), "I": round(R[m]["I"], 6)} for m in MEANINGS},
                       shuffle={"seed": SEED_SHUF, "n": NSHUF, "valid": len(good), "observed_I": round(obs, 6),
                                "ge": ge}), open(a.json, "w"), indent=1)
    sys.exit(0 if RECORDED is not None and (tuple(held), dg) == RECORDED else 1)


if __name__ == "__main__":
    main()
