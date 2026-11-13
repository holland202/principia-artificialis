"""MEM-DECAY-001 P6: the same five arms, with T taken from background (filler) ages and 4x the filler.

Usage (from the repository root):
    python3 experiments/mem_decay_001/memdecay_p6.py seal
    python3 experiments/mem_decay_001/memdecay_p6.py run [--expect-seal S] [--expect-digest D]

It reuses memdecay.py unchanged (generator, arms, guard, scorer). Only the split and the T rule differ:
  split p6   seed 20261115, 200 queries per category, filler 8000 (4x the registered test split)
  T = h      median age of FILLER records only (background store age), not of the whole store
  N          LRU keeps as many records as TTL keeps (matched deletion; the registered n/2 no longer matches)
  sweep      A3 alone at h = T x {1, 2, 4, 8, 16, 32}: critical, stale and current recall (registered as P6d)
Registered in REGISTRATION_P6.md before any metric was computed. Written by Claude (Anthropic, Opus 5.5),
2026-11-13. SELF-TESTED only.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memdecay as m  # noqa: E402

m.SPLITS["p6"] = {"seed": 20261115, "n": 200, "filler": 8000}
MULTS = (1, 2, 4, 8, 16, 32)
_registered_candidates = m.candidates


def candidates_p6(store, arm, T):
    """Matched deletion: A2 (LRU) keeps exactly as many records as A1 (TTL) keeps. Other arms unchanged."""
    if arm != "A2":
        return _registered_candidates(store, arm, T)
    n_keep = int((store["age"] <= T).sum())
    keep = np.zeros(len(store["age"]), bool)
    keep[np.argsort(store["access"], kind="stable")[:n_keep]] = True
    return keep


m.candidates = candidates_p6   # memdecay.evaluate looks the function up at call time


def background_T(store):
    filler = np.array([r == "filler" for r in store["role"]])
    return float(np.median(store["age"][filler]))


def gate(store, queries, T):
    n = m.SPLITS["p6"]["n"]
    problems = [f"{c}: wrong query count" for c in m.CATS if sum(q["cat"] == c for q in queries) != n]
    crit = store["critical"]
    if not (store["age"][crit] > T).all():
        problems.append("a critical record is not older than T")
    if sum(r == "filler" for r in store["role"]) != m.SPLITS["p6"]["filler"]:
        problems.append("filler count differs")
    return problems


def sweep(store, queries, T):
    out = {}
    alive = m.candidates(store, "A3", T)
    for k in MULTS:
        h = k * T
        hits = {"critical": 0, "stale": 0, "current": 0}
        for qd in queries:
            c = qd["cat"]
            if c not in hits:
                continue
            top = m.topk(store, qd["qvec"], "A3", "G1", T, h, alive)
            if c == "stale":
                t, s = qd["target"], qd["stale"]
                hits[c] += t in top and (s not in top or top.index(t) < top.index(s))
            else:
                hits[c] += qd["target"] in top
        out[k] = hits
    return out


def predictions(res, sw, n):
    r = lambda a, c, g="G1": m.rate(res, a, g, c)
    return {
        "P6a A3 critical <= 0.05 at h = T (decay still loses critical records at a background-age half-life)":
            r("A3", "critical") <= 0.05,
        "P6b A3 stale >= A1 stale - 0.05 (non-inferiority holds at a longer half-life)":
            r("A3", "stale") >= r("A1", "stale") - 0.05,
        "P6c A3 current < A0 current - 0.05 (decay still costs recall of old ordinary facts)":
            r("A3", "current") < r("A0", "current") - 0.05,
        "P6d A3 critical <= 0.05 for h <= 4T and >= 0.95 at h = 32T":
            all(sw[k]["critical"] / n <= 0.05 for k in (1, 2, 4)) and sw[32]["critical"] / n >= 0.95,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="MEM-DECAY-001 P6")
    ap.add_argument("cmd", choices=("seal", "run"))
    ap.add_argument("--expect-seal")
    ap.add_argument("--expect-digest")
    a = ap.parse_args(argv)
    store, queries = m.build("p6")
    seal = hashlib.sha256(m.canonical(store, queries)).hexdigest()
    T = background_T(store)
    print(f"MEM-DECAY-001 P6 | seed {m.SPLITS['p6']['seed']} | python {sys.version.split()[0]} numpy {np.__version__}")
    print(f"store {len(store['age'])} records, {len(queries)} queries; T = h = {T:.4f} days (filler median); "
          f"whole-store median {float(np.median(store['age'])):.4f}; N = {int((store['age'] <= T).sum())} "
          f"(= records TTL keeps); k = {m.K}")
    print(f"SEAL {seal}")
    problems = gate(store, queries, T)
    if problems:
        print("COULD NOT BUILD: " + "; ".join(problems))
        return 2
    if a.expect_seal and a.expect_seal != seal:
        print(f"COULD NOT BUILD: seal mismatch (expected {a.expect_seal})")
        return 2
    if a.cmd == "seal":
        print("sealed; nothing scored")
        return 0
    res = m.evaluate(store, queries, T, T)
    n = m.SPLITS["p6"]["n"]
    print(f"\n{'arm/guard':9} " + " ".join(f"{c:>21}" for c in m.CATS) + "   kept")
    for arm in m.ARMS:
        for g in ("G0", "G1"):
            cells = []
            for c in m.CATS:
                k, nn = res[(arm, g)][c]
                lo, hi = m.wilson(k, nn)
                cells.append(f"{k:>4}/{nn} {k / nn:.3f} [{lo:.2f},{hi:.2f}]")
            kk, kn = res[(arm, g)]["keep"]
            print(f"{arm}/{g:6} " + " ".join(f"{x:>21}" for x in cells) + f"   {kk / kn:.3f}")
    print("(revoked column = leak rate: lower is better)")
    sw = sweep(store, queries, T)
    print("\nA3 half-life sweep (guard G1)")
    for k in MULTS:
        print(f"  h = {k:>2} x T = {k * T:8.1f} days: critical {sw[k]['critical']:>3}/{n} {sw[k]['critical'] / n:.3f}  "
              f"stale {sw[k]['stale']:>3}/{n} {sw[k]['stale'] / n:.3f}  current {sw[k]['current']:>3}/{n} {sw[k]['current'] / n:.3f}")
    print()
    for name, held in predictions(res, sw, n).items():
        print(f"{'HELD   ' if held else 'REFUTED'} {name}")
    alive = m.candidates(store, "A0", T)
    same = all(m.topk(store, q["qvec"], "A3", "G1", T, float("inf"), alive)
               == m.topk(store, q["qvec"], "A0", "G1", T, float("inf"), alive) for q in queries)
    print(f"{'HELD  ' if same else 'FAILED'} NC2 h = inf gives rankings identical to A0 on {len(queries)} queries")
    rows = {f"{x}/{g}": {c: list(v) for c, v in res[(x, g)].items()} for x in m.ARMS for g in ("G0", "G1")}
    rows["sweep"] = {str(k): v for k, v in sw.items()}
    dg = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    print(f"DIGEST {dg}")
    rc = 0 if same else 1
    if a.expect_digest and a.expect_digest != dg:
        print(f"DIGEST MISMATCH (expected {a.expect_digest})")
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
