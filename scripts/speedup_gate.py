#!/usr/bin/env python3
"""
speedup_gate.py — an instrument for adjudicating the claim "my maths is faster".

Three gates, cheapest first. A candidate that fails gate 1 never reaches gate 3.

  GATE 1  CORRECTNESS  candidate's fast path == its own dense materialization
                       on adversarial inputs, to tolerance.
  GATE 2  OP COUNT     symbolic multiply count, candidate vs baseline.
                       If it does not win here, wall clock will not rescue it.
  GATE 3  WALL CLOCK   matched dtype, warmed, best-of-k, plus effective GFLOP/s
                       so a loss is explainable rather than just recorded.

ANTI-VACUITY (runs first, always):
  A0  a deliberately broken candidate MUST fail gate 1.
  A1  a candidate that IS the baseline MUST report no win (0.80x - 1.25x).
  If either fails, the instrument cannot be trusted and every speed number
  printed below it is void.

EXIT CODES
  0  gates ran and the instrument is trustworthy. A candidate LOSING is a
     result, not a build failure, and still exits 0.
  1  anti-vacuity failed -> instrument untrustworthy, all claims void.
  2  could not run (no numpy, bad args).

  --sabotage  breaks A0 on purpose to prove exit 1 is reachable.

Author: Claude (Opus 4.5). Prior art for the butterfly/Monarch operator:
Dao et al. 2022; Cooley-Tukey butterfly lineage. Operator not claimed as new.
"""

import sys
import time
import argparse

try:
    import numpy as np
except ImportError:
    print("numpy not available", file=sys.stderr)
    sys.exit(2)

DTYPE = np.float32
TOL = 1e-4          # float32 matmul accumulation tolerance, relative
BATCH = 64


# ---------------------------------------------------------------- candidates

class Dense:
    """Baseline: a plain n x n matmul."""
    name = "dense"

    def __init__(self, n, rng):
        self.n = n
        self.W = rng.standard_normal((n, n)).astype(DTYPE) / np.sqrt(n)

    def __call__(self, x):
        return x @ self.W

    def multiplies_per_sample(self):
        return self.n * self.n


class Butterfly:
    """Two block-diagonal transforms separated by a transpose. n = b*b."""
    name = "butterfly"

    def __init__(self, n, rng):
        b = int(round(np.sqrt(n)))
        if b * b != n:
            raise ValueError(f"n={n} is not a perfect square")
        self.n, self.b = n, b
        s = np.sqrt(b)
        self.W1 = (rng.standard_normal((b, b, b)) / s).astype(DTYPE)
        self.W2 = (rng.standard_normal((b, b, b)) / s).astype(DTYPE)

    def __call__(self, x):
        b = self.b
        y = x.reshape(-1, b, b)
        y = np.einsum('bij,ijk->bik', y, self.W1, optimize=True)
        y = np.ascontiguousarray(y.transpose(0, 2, 1))
        y = np.einsum('bij,ijk->bik', y, self.W2, optimize=True)
        return y.reshape(-1, self.n)

    def multiplies_per_sample(self):
        return 2 * self.b ** 3

    def materialize(self):
        """The slow, obviously-correct reference: push I_n through the fast
        path and read off the matrix it implements."""
        eye = np.eye(self.n, dtype=DTYPE)
        return self(eye)


class BrokenButterfly(Butterfly):
    """A0 fixture. Computes something else and says nothing about it."""
    name = "butterfly-BROKEN"

    def __call__(self, x):
        out = super().__call__(x)
        out[:, 0] += np.float32(1.0)      # one element wrong, silently
        return out


class DenseAsCandidate(Dense):
    """A1 fixture. Identical to the baseline; must not show a win."""
    name = "dense-as-candidate"


# --------------------------------------------------------------------- gates

def adversarial_inputs(n, rng):
    """Not just easy inputs."""
    return [
        ("standard normal", rng.standard_normal((BATCH, n)).astype(DTYPE)),
        ("wide dynamic range",
         (rng.standard_normal((BATCH, n)) * 10.0 ** rng.integers(-6, 7, (BATCH, n))).astype(DTYPE)),
        ("alternating sign ones",
         (np.tile([1.0, -1.0], (BATCH, n // 2))).astype(DTYPE)),
        ("all zeros", np.zeros((BATCH, n), dtype=DTYPE)),
        ("single hot", np.eye(BATCH, n, dtype=DTYPE)),
    ]


def gate1_correctness(cand, rng):
    """Fast path must equal its own dense materialization."""
    M = cand.materialize()
    worst, worst_case = 0.0, ""
    for label, x in adversarial_inputs(cand.n, rng):
        fast = cand(x)
        slow = x @ M
        scale = max(float(np.abs(slow).max()), 1.0)
        rel = float(np.abs(fast - slow).max()) / scale
        if rel > worst:
            worst, worst_case = rel, label
    return worst <= TOL, worst, worst_case


def gate2_opcount(cand, base):
    c, b = cand.multiplies_per_sample(), base.multiplies_per_sample()
    return b / c, c, b


def timeit(fn, x, reps):
    fn(x)                                   # warm
    best = float("inf")
    for _ in range(7):
        t0 = time.perf_counter()
        for _ in range(reps):
            fn(x)
        best = min(best, (time.perf_counter() - t0) / reps)
    return best


def gate3_wallclock(cand, base, rng, reps):
    x = rng.standard_normal((BATCH, cand.n)).astype(DTYPE)
    t_base = timeit(base, x, reps)
    t_cand = timeit(cand, x, reps)
    gf = lambda op, t: (2.0 * op * BATCH) / t / 1e9
    return (t_base / t_cand,
            t_base, t_cand,
            gf(base.multiplies_per_sample(), t_base),
            gf(cand.multiplies_per_sample(), t_cand))


# -------------------------------------------------------------- anti-vacuity

def anti_vacuity(sabotage=False):
    rng = np.random.default_rng(0)
    n = 256
    ok = True

    print("ANTI-VACUITY")
    broken = Butterfly(n, rng) if sabotage else BrokenButterfly(n, rng)
    passed, rel, case = gate1_correctness(broken, rng)
    a0 = (not passed)
    print(f"  A0 broken candidate fails gate 1 : {'PASS' if a0 else 'FAIL'}"
          f"   (rel err {rel:.3e} on '{case}', tol {TOL:.0e})")
    if sabotage:
        print("     [--sabotage: fed an intact candidate where a broken one belongs]")
    ok &= a0

    d = DenseAsCandidate(n, rng)
    base = Dense(n, rng)
    base.W = d.W                             # same matrix, same work
    ratio, *_ = gate3_wallclock(d, base, rng, reps=30)
    a1 = 0.80 <= ratio <= 1.25
    print(f"  A1 baseline-as-candidate shows no win : {'PASS' if a1 else 'FAIL'}"
          f"   (ratio {ratio:.3f}x, band 0.80-1.25)")
    ok &= a1
    return ok


# --------------------------------------------------------------------- sweep

def sweep():
    rng = np.random.default_rng(1)
    print(f"\n{'n':>6} {'theory':>8} {'measured':>9} {'verdict':>9} "
          f"{'base GF/s':>10} {'cand GF/s':>10} {'cand/base':>10}")
    print("-" * 68)
    rows = []
    for n, reps in ((64, 300), (256, 200), (1024, 60), (4096, 8)):
        base = Dense(n, rng)
        cand = Butterfly(n, rng)

        passed, rel, case = gate1_correctness(cand, rng)
        if not passed:
            print(f"{n:>6}  GATE 1 FAILED rel={rel:.2e} on '{case}' — skipped")
            continue

        theory, mc, mb = gate2_opcount(cand, base)
        meas, tb, tc, gfb, gfc = gate3_wallclock(cand, base, rng, reps)
        verdict = "WIN" if meas > 1.0 else "LOSS"
        print(f"{n:>6} {theory:>7.1f}x {meas:>8.2f}x {verdict:>9} "
              f"{gfb:>10.2f} {gfc:>10.2f} {gfc/gfb:>9.1%}")
        rows.append(dict(n=n, theory=theory, meas=meas, gfb=gfb, gfc=gfc, rel=rel))
    return rows


def verdicts(rows):
    print("\nREGISTERED PREDICTIONS")
    p1 = all(abs(r["theory"] - np.sqrt(r["n"]) / 2) < 1e-9 for r in rows)
    print(f"  P1 op-count ratio == sqrt(n)/2 exactly            : "
          f"{'CONFIRMED' if p1 else 'REFUTED'}")

    r1k = next((r for r in rows if r["n"] == 1024), None)
    if r1k:
        p2 = r1k["meas"] < 8.0
        print(f"  P2 n=1024 measured < 8.0x (theory 16.0x)          : "
              f"{'CONFIRMED' if p2 else 'REFUTED'}   measured {r1k['meas']:.2f}x")

    losses = [r["n"] for r in rows if r["meas"] <= 1.0]
    p3 = bool(losses) and min(losses) >= 256
    print(f"  P3 a crossover exists and sits at n >= 256        : "
          f"{'CONFIRMED' if p3 else 'REFUTED'}   "
          f"{'losses at n=' + ','.join(map(str, losses)) if losses else 'no size lost'}")

    r4k = next((r for r in rows if r["n"] == 4096), None)
    if r4k:
        frac = r4k["gfc"] / r4k["gfb"]
        p4 = frac < 0.40
        print(f"  P4 n=4096 candidate GF/s < 40% of baseline        : "
              f"{'CONFIRMED' if p4 else 'REFUTED'}   measured {frac:.1%}")
    print("  P5 same sweep on aarch64/Termux S25              : UNRUN (the door)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true",
                    help="break A0 on purpose to prove exit 1 is reachable")
    args = ap.parse_args()

    print(f"speedup_gate.py  |  numpy {np.__version__}  |  "
          f"{sys.platform}  |  python {sys.version.split()[0]}")
    print(f"dtype {np.dtype(DTYPE).name}, batch {BATCH}, tol {TOL:.0e}\n")

    if not anti_vacuity(args.sabotage):
        print("\nINSTRUMENT UNTRUSTWORTHY — anti-vacuity failed. "
              "All speed numbers void.", file=sys.stderr)
        return 1

    rows = sweep()
    if rows:
        verdicts(rows)
    print("\nA candidate losing is a result, not a build failure. exit 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
