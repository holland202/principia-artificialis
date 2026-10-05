#!/usr/bin/env python3
"""note067_reference.py - Note #067: S3P bounds the evaluator-judged rate; a canary-corrected bound.

  python scripts/note067_reference.py              # registered run (prints every number in the note)
  python scripts/note067_reference.py --sabotage   # composed bound replaced by the S3P bound alone; P4 must fail, exit 1

Exact Clopper-Pearson bounds by bisection on the binomial CDF (stdlib math only, NumPy for draws).
Exit 0 only if the outcome equals RECORDED (held predictions and digest).
"""
import hashlib
import json
import math
import sys
from functools import lru_cache

import numpy as np

N, K, ALPHA, EPOCHS = 600, 20, 0.05, 2000
SENS, RATES = (1.0, 0.9, 0.5, 0.1, 0.0), (0.005, 0.04)
RECORDED = (("P1", "P3", "P4", "P5", "P6"), "44e15cac2d627520307e0901e38f75c5b5669f598ff822a0daf523ae09a0725d")


def binom_cdf(x, n, q):
    """P(X <= x), X ~ Binomial(n, q)."""
    if x < 0:
        return 0.0
    if x >= n or q <= 0.0:
        return 1.0
    if q >= 1.0:
        return 0.0
    lq, l1 = math.log(q), math.log1p(-q)
    return min(1.0, sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lq + (n - i) * l1)
                        for i in range(x + 1)))


def _bisect(f, lo=0.0, hi=1.0):
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(mid):
            hi = mid
        else:
            lo = mid
    return hi


@lru_cache(maxsize=None)
def upper(x, n, a):
    """One-sided upper Clopper-Pearson bound: smallest q with P(X <= x | q) <= a."""
    return 1.0 if x >= n else _bisect(lambda q: binom_cdf(x, n, q) <= a)


@lru_cache(maxsize=None)
def lower(x, n, a):
    """One-sided lower Clopper-Pearson bound: largest s with P(X >= x | s) <= a."""
    return 0.0 if x <= 0 else _bisect(lambda s: 1 - binom_cdf(x - 1, n, s) > a) - 0.0


def miss_bounds(m, t):
    """(rate, 99% one-sided lower, 99% one-sided upper) for m misses in t epochs."""
    return m / t, lower(m, t, 0.01), upper(m, t, 0.01)


def arm(rng, s, p, canary_s=None, sabotage=False):
    cs = s if canary_s is None else canary_s
    judged = rng.binomial(N, s * p, EPOCHS)
    caught = rng.binomial(K, cs, EPOCHS)
    u = np.array([upper(int(x), N, ALPHA) for x in judged])
    u2 = np.array([upper(int(x), N, ALPHA / 2) for x in judged])
    lo = np.array([lower(int(c), K, ALPHA / 2) for c in caught])
    with np.errstate(divide="ignore"):
        b = np.where(lo > 0, u2 / np.where(lo > 0, lo, 1), np.inf)
    if sabotage:
        b = u
    return {"s3p_miss": int(np.sum(u < p)), "comp_miss": int(np.sum(b < p)), "no_claim": int(np.sum(np.isinf(b))),
            "s3p_bound_min": float(u.min()), "s3p_bound_max": float(u.max()),
            "comp_median": float(np.median(b[np.isfinite(b)])) if np.isfinite(b).any() else None}


def main():
    sabotage = "--sabotage" in sys.argv
    print(f"note067 | {'SABOTAGE: composed bound = S3P bound alone' if sabotage else 'registered run'} | "
          f"python {sys.version.split()[0]} | n={N} k={K} alpha={ALPHA} epochs={EPOCHS} seed=0")
    rng = np.random.default_rng(0)
    res = {}
    for s in SENS:
        for p in RATES:
            r = arm(rng, s, p, sabotage=sabotage)
            res[f"s{s}_p{p}"] = r
            sm, cm = miss_bounds(r["s3p_miss"], EPOCHS), miss_bounds(r["comp_miss"], EPOCHS)
            med = "none" if r["comp_median"] is None else f"{r['comp_median']:.6f}"
            print(f"  s={s:<4} p={p:<6} S3P miss {sm[0]:.4f} [99% {sm[1]:.4f}, {sm[2]:.4f}]  "
                  f"composed miss {cm[0]:.4f} [99% {cm[1]:.4f}, {cm[2]:.4f}]  no-claim {r['no_claim']}/{EPOCHS}  "
                  f"S3P bound {r['s3p_bound_min']:.6f}..{r['s3p_bound_max']:.6f}  composed median {med}")
    d = arm(rng, 0.1, 0.04, canary_s=1.0, sabotage=sabotage)
    res["distinguishable"] = d
    dm = miss_bounds(d["comp_miss"], EPOCHS)
    print(f"  distinguishable canaries (real s=0.1, canaries caught always), p=0.04: composed miss {dm[0]:.4f} "
          f"[99% {dm[1]:.4f}, {dm[2]:.4f}]  composed median {d['comp_median']:.6f}")
    u0, b0 = upper(0, N, ALPHA), upper(0, N, ALPHA / 2) / lower(K, K, ALPHA / 2)
    ratio = b0 / u0
    print(f"  P5 p=0, s=1: S3P bound {u0:.6f}, composed {b0:.6f}, ratio {ratio:.4f}")
    for p in RATES:  # diagnostic added after the first run (P2 refuted); not part of any verdict or the digest
        xs = [x for x in range(N + 1) if upper(x, N, ALPHA) < p]
        if xs:
            print(f"  (unregistered diagnostic) s=1, p={p}: S3P misses iff judged <= {max(xs)}; "
                  f"exact miss probability {binom_cdf(max(xs), N, p):.6f}")

    v = {}
    v["P1"] = all(abs(res[f"s0.0_p{p}"]["s3p_bound_min"] - 0.004980) < 5e-7 and
                  abs(res[f"s0.0_p{p}"]["s3p_bound_max"] - 0.004980) < 5e-7 and
                  res[f"s0.0_p{p}"]["s3p_miss"] == EPOCHS for p in RATES)
    v["P2"] = all(miss_bounds(res[f"s1.0_p{p}"]["s3p_miss"], EPOCHS)[0] <= 0.05 and
                  miss_bounds(res[f"s1.0_p{p}"]["s3p_miss"], EPOCHS)[2] <= 0.065 for p in RATES)
    v["P3"] = miss_bounds(res["s0.5_p0.04"]["s3p_miss"], EPOCHS)[1] >= 0.50
    v["P4"] = all(miss_bounds(res[f"s{s}_p{p}"]["comp_miss"], EPOCHS)[0] <= 0.05 and
                  miss_bounds(res[f"s{s}_p{p}"]["comp_miss"], EPOCHS)[2] <= 0.065 for s in SENS for p in RATES)
    v["P5"] = abs(ratio - 1.4799) <= 0.0005
    v["P6"] = dm[1] >= 0.50
    for k, ok in v.items():
        print(f"  {k}  {'HELD' if ok else 'REFUTED'}")
    held = tuple(k for k, ok in v.items() if ok)
    rounded = json.loads(json.dumps(res), parse_float=lambda x: round(float(x), 6))
    dg = hashlib.sha256(json.dumps({"r": rounded, "v": v, "ratio": round(ratio, 6)}, sort_keys=True).encode()).hexdigest()
    print(f"VERDICT {len(held)} of {len(v)} as registered (P7 is --sabotage)")
    print(f"DIGEST {dg}")
    if sabotage or RECORDED is None:
        return 0 if all(v.values()) else 1
    return 0 if (held, dg) == RECORDED else 1


if __name__ == "__main__":
    sys.exit(main())
