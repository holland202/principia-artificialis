"""MEM-DECAY-002: dual-strength decay, graded importance floors and noisy importance labels (REGISTRATION.md).

Usage (from the repository root):
    python3 experiments/mem_decay_002/memdecay2.py seal --split test
    python3 experiments/mem_decay_002/memdecay2.py run  --split dev
    python3 experiments/mem_decay_002/memdecay2.py run  --split test [--expect-seal S] [--expect-digest D]

Reuses experiments/mem_decay_001/memdecay.py unchanged for the base store, the categories and the hit rules.
Exit: 0 ran (and on test every control held); 1 a control failed or the digest differs; 2 COULD NOT BUILD.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-14. SELF-TESTED only.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mem_decay_001"))
import memdecay as m  # noqa: E402

m.SPLITS["d2dev"] = {"seed": 20261117, "n": 50, "filler": 1000}
m.SPLITS["d2test"] = {"seed": 20261116, "n": 200, "filler": 8000}
SPLIT_NAME = {"dev": "d2dev", "test": "d2test"}
EPS = (0.0, 0.1, 0.3)
ARMS = ("A0", "A3", "A4L", "A6", "A5", "A7")
PIN = 0.5
MUTANT = None   # set only by tests: "floor", "storage", "pins", "no_noise", "wrong_class"


# ---------------------------------------------------------------- extra fields
def extras(store, seed):
    """Use counts and label draws from a generator seeded seed + 7; the base store is not touched."""
    rng = np.random.default_rng(seed + 7)
    n = len(store["age"])
    crit = store["critical"]
    counts = rng.poisson(2.0, n)
    counts[crit] = 0
    ex = {
        "count": counts,
        "u": rng.uniform(size=n),
        "w_true": np.where(crit, rng.uniform(0.8, 1.0, n), rng.uniform(0.0, 0.3, n)),
        "w_low": rng.uniform(0.0, 0.3, n),
        "w_high": rng.uniform(0.8, 1.0, n),
    }
    ex["eff_access"] = np.where(counts == 0, store["age"], store["access"])
    ex["S"] = 1.0 + np.log2(1.0 + counts)
    return ex


def labels(ex, crit, eps):
    missed = crit & (ex["u"] < eps)
    raised = ~crit & (ex["u"] < eps / 10)
    if MUTANT == "no_noise":
        missed = raised = np.zeros_like(crit)
    if MUTANT == "wrong_class":
        missed, raised = ~crit & (ex["u"] < eps), crit & (ex["u"] < eps / 10)
    w = ex["w_true"].copy()
    w[missed] = ex["w_low"][missed]
    w[raised] = ex["w_high"][raised]
    return w


# ---------------------------------------------------------------- scores
def retrieval_strength(age_like, S, h):
    if MUTANT == "storage":
        S = np.ones_like(S)
    return np.exp(-math.log(2) * age_like / (h * S))


def scores(sim, store, ex, w, arm, T, h, true_pins=False):
    """Score array and alive mask for one query's similarity vector `sim`."""
    n = len(sim)
    alive = np.ones(n, bool)
    if arm == "A0":
        return sim, alive
    if arm == "A3":
        return sim * np.exp(-math.log(2) * store["age"] / h), alive
    if arm == "A4L":
        pinned = store["critical"] if true_pins else (w >= PIN)
        return sim, (store["age"] <= T) | pinned
    if arm == "A6":
        return sim * retrieval_strength(ex["eff_access"], ex["S"], h), alive
    if arm == "A5":
        R = retrieval_strength(ex["eff_access"], ex["S"], h)
        floor = np.zeros(n) if MUTANT == "floor" else w
        return sim * np.maximum(floor, R), alive
    if arm == "A7":
        dec = sim * np.exp(-math.log(2) * store["age"] / h)
        if MUTANT == "pins":
            return dec, alive
        return np.where(w >= PIN, sim, dec), alive
    raise ValueError(arm)


def topk(score, alive, status):
    mask = alive & (status == m.CURRENT)
    s = np.where(mask, score, -np.inf)
    order = np.lexsort((np.arange(len(s)), -s))[:m.K]
    return [int(i) for i in order if np.isfinite(s[i])]


def hit(qd, top):
    c = qd["cat"]
    if c in ("current", "critical", "adversarial"):
        return qd["target"] in top
    if c == "stale":
        t, s = qd["target"], qd["stale"]
        return t in top and (s not in top or top.index(t) < top.index(s))
    if c == "contradictory":
        return all(r in top for r in qd["pair"])
    return qd["revoked"] in top   # revoked: a leak, lower is better


# ---------------------------------------------------------------- evaluation
def run_arm(store, queries, sims, ex, w, arm, T, h, **kw):
    hits = {c: [0, 0] for c in m.CATS}
    tops = []
    for qd, sim in zip(queries, sims):
        sc, alive = scores(sim, store, ex, w, arm, T, h, **kw)
        top = topk(sc, alive, store["status"])
        tops.append(top)
        hits[qd["cat"]][0] += hit(qd, top)
        hits[qd["cat"]][1] += 1
    return {c: tuple(v) for c, v in hits.items()}, tops


def background_T(store):
    filler = np.array([r == "filler" for r in store["role"]])
    return float(np.median(store["age"][filler]))


def gate(store, queries, ex, split):
    cfg = m.SPLITS[split]
    probs = [f"{c}: wrong query count" for c in m.CATS if sum(q["cat"] == c for q in queries) != cfg["n"]]
    T = background_T(store)
    crit = store["critical"]
    if not (store["age"][crit] > T).all():
        probs.append("a critical record is not older than T")
    if (ex["count"][crit] != 0).any():
        probs.append("a critical record has a use count")
    if not (ex["eff_access"] <= store["age"] + 1e-12).all():
        probs.append("effective access age exceeds age")
    return T, probs


def synth_summary(store, ex):
    crit = store["critical"]
    lines = [f"use count mean: critical {ex['count'][crit].mean():.3f}, other {ex['count'][~crit].mean():.3f}"]
    for eps in EPS:
        w = labels(ex, crit, eps)
        lines.append(f"eps {eps}: critical labelled >= {PIN}: {(w[crit] >= PIN).mean():.4f} "
                     f"({int((w[crit] >= PIN).sum())}/{int(crit.sum())}); other labelled >= {PIN}: "
                     f"{(w[~crit] >= PIN).mean():.5f} ({int((w[~crit] >= PIN).sum())}/{int((~crit).sum())})")
    return lines


def seal_bytes(store, queries, ex):
    extra = {k: np.round(v, 9).tolist() for k, v in ex.items()}
    return m.canonical(store, queries) + json.dumps(extra, sort_keys=True, separators=(",", ":")).encode()


def predictions(R):
    r = lambda arm, eps, c: R[(arm, eps)][c][0] / R[(arm, eps)][c][1]
    return {
        "Q1 A6 critical <= 0.05 at every eps (instrument check)": all(r("A6", e, "critical") <= 0.05 for e in EPS),
        "Q2 A5 critical at eps 0 in [0.20, 0.70]": 0.20 <= r("A5", 0.0, "critical") <= 0.70,
        "Q3 A7 at eps 0: critical >= 0.95 and stale >= 0.95":
            r("A7", 0.0, "critical") >= 0.95 and r("A7", 0.0, "stale") >= 0.95,
        "Q4 at eps 0.3, A4L and A7 critical each in [0.60, 0.80]":
            all(0.60 <= r(a, 0.3, "critical") <= 0.80 for a in ("A4L", "A7")),
        "Q5 A6 current > A3 current + 0.10 at eps 0": r("A6", 0.0, "current") > r("A3", 0.0, "current") + 0.10,
        "Q6 A6 stale < A3 stale - 0.05 at eps 0": r("A6", 0.0, "stale") < r("A3", 0.0, "stale") - 0.05,
        "Q7 at eps 0.3 no arm but A0 has critical > 0.85":
            all(r(a, 0.3, "critical") <= 0.85 for a in ARMS if a != "A0"),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="MEM-DECAY-002")
    ap.add_argument("cmd", choices=("seal", "run"))
    ap.add_argument("--split", choices=("dev", "test"), required=True)
    ap.add_argument("--expect-seal")
    ap.add_argument("--expect-digest")
    a = ap.parse_args(argv)
    split = SPLIT_NAME[a.split]
    seed = m.SPLITS[split]["seed"]
    store, queries = m.build(split)
    ex = extras(store, seed)
    seal = hashlib.sha256(seal_bytes(store, queries, ex)).hexdigest()
    T, probs = gate(store, queries, ex, split)
    h = T
    print(f"MEM-DECAY-002 | split={a.split} seed={seed} | python {sys.version.split()[0]} numpy {np.__version__}")
    print(f"store {len(store['age'])} records, {len(queries)} queries; T = h = {T:.4f} days (filler median); "
          f"k = {m.K}; pin threshold {PIN}")
    print(f"SEAL {seal}")
    if probs:
        print("COULD NOT BUILD: " + "; ".join(probs))
        return 2
    if a.expect_seal and a.expect_seal != seal:
        print(f"COULD NOT BUILD: seal mismatch (expected {a.expect_seal})")
        return 2
    print("generated inputs (C-SYNTH):")
    for line in synth_summary(store, ex):
        print("  " + line)
    if a.cmd == "seal":
        print("sealed; nothing scored")
        return 0

    sims = [store["vec"] @ q["qvec"] for q in queries]
    crit = store["critical"]
    R, TOPS = {}, {}
    for eps in EPS:
        w = labels(ex, crit, eps)
        for arm in ARMS:
            R[(arm, eps)], TOPS[(arm, eps)] = run_arm(store, queries, sims, ex, w, arm, T, h)
    print(f"\n{'arm':4} {'eps':>4} " + " ".join(f"{c:>21}" for c in m.CATS))
    for arm in ARMS:
        for eps in EPS:
            cells = []
            for c in m.CATS:
                k, n = R[(arm, eps)][c]
                lo, hi = m.wilson(k, n)
                cells.append(f"{k:>4}/{n} {k / n:.3f} [{lo:.2f},{hi:.2f}]")
            print(f"{arm:4} {eps:>4} " + " ".join(f"{x:>21}" for x in cells))
    print("(revoked column = leak rate: lower is better)")

    rc = 0
    if a.split == "test":
        print()
        for name, held in predictions(R).items():
            print(f"{'HELD   ' if held else 'REFUTED'} {name}")
        print()
        w0 = labels(ex, crit, 0.0)
        nc = {}
        _, t = run_arm(store, queries, sims, ex, np.zeros(len(w0)), "A5", T, h)
        nc["NC1 A5 with zero floors == A6"] = t == TOPS[("A6", 0.0)]
        _, t = run_arm(store, queries, sims, ex, np.zeros(len(w0)), "A7", T, h)
        nc["NC2 A7 with no pins == A3"] = t == TOPS[("A3", 0.0)]
        ex3 = dict(ex, S=np.ones(len(w0)), eff_access=store["age"])
        _, t = run_arm(store, queries, sims, ex3, w0, "A6", T, h)
        nc["NC3 A6 with S = 1 and access age = age == A3"] = t == TOPS[("A3", 0.0)]
        _, t = run_arm(store, queries, sims, ex, w0, "A4L", T, h, true_pins=True)
        nc["NC4 A4L at eps 0 == A4 (true flag)"] = t == TOPS[("A4L", 0.0)]
        perm = np.random.default_rng(seed + 8).permutation(len(w0))
        res5, _ = run_arm(store, queries, sims, ex, w0[perm], "A7", T, h)
        c5 = res5["critical"][0] / res5["critical"][1]
        nc[f"NC5 shuffled labels: A7 critical {c5:.3f} <= 0.10"] = c5 <= 0.10
        for name, held in nc.items():
            print(f"{'HELD  ' if held else 'FAILED'} {name}")
            rc |= 0 if held else 1
    rows = {f"{arm}/{eps}": {c: list(v) for c, v in R[(arm, eps)].items()} for arm in ARMS for eps in EPS}
    dg = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    print(f"DIGEST {dg}")
    if a.expect_digest and a.expect_digest != dg:
        print(f"DIGEST MISMATCH (expected {a.expect_digest})")
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
