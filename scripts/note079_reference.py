#!/usr/bin/env python3
"""note079 reference: what ToyBlocks' published sim and real-robot counts can and cannot show.

Arithmetic on the authors' own counts only (Molmo 2 + ManiFlow: 111/200 in simulation, 15/30 on the real robot,
from the Ai2 blog post of 2026-11-06). Nothing is re-run. Prints every number note079 uses.
Fisher's exact test is computed with exact fractions; intervals and power use the normal distribution.
Standard library only.

  python3 scripts/note079_reference.py
"""
import math
from fractions import Fraction
from statistics import NormalDist

SIM = (111, 200)
REAL = (15, 30)
ALPHA, POWER = 0.05, 0.80
Z_A = NormalDist().inv_cdf(1 - ALPHA / 2)
Z_B = NormalDist().inv_cdf(POWER)
PHI = NormalDist().cdf


def wilson(k, n, z=Z_A):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def fisher_two_sided(a, n1, b, n2):
    """Exact two-sided p: total probability of tables no more likely than the observed one (exact fractions)."""
    k, n = a + b, n1 + n2
    pmf = lambda x: Fraction(math.comb(n1, x) * math.comb(n2, k - x), math.comb(n, k))  # noqa: E731
    obs = pmf(a)
    lo, hi = max(0, k - n2), min(k, n1)
    return sum(p for p in (pmf(x) for x in range(lo, hi + 1)) if p <= obs)


def power(p1, n1, p2, n2):
    """Two-sided normal-approximation power, unpooled standard error."""
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return PHI(abs(p1 - p2) / se - Z_A)


def equal_n(p1, p2):
    """Episodes per arm (equal arms) to detect p1 vs p2 at ALPHA two-sided with POWER."""
    pbar = (p1 + p2) / 2
    num = Z_A * math.sqrt(2 * pbar * (1 - pbar)) + Z_B * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return math.ceil((num / (p1 - p2)) ** 2)


def min_detectable(n1, n2, p=0.5):
    return (Z_A + Z_B) * math.sqrt(p * (1 - p) / n1 + p * (1 - p) / n2)


def main():
    p1, p2 = SIM[0] / SIM[1], REAL[0] / REAL[1]
    ws, wr = wilson(*SIM), wilson(*REAL)
    print(f"sim  {SIM[0]}/{SIM[1]} = {p1:.4f}; Wilson 95% [{ws[0]:.4f}, {ws[1]:.4f}], width {ws[1] - ws[0]:.4f}")
    print(f"real {REAL[0]}/{REAL[1]} = {p2:.4f}; Wilson 95% [{wr[0]:.4f}, {wr[1]:.4f}], width {wr[1] - wr[0]:.4f}")
    print(f"gap {p1 - p2:.4f}")
    f = fisher_two_sided(SIM[0], SIM[1], REAL[0], REAL[1])
    print(f"Fisher exact two-sided p, 111/200 vs 15/30: {float(f):.4f}")
    pw = power(p1, SIM[1], p2, REAL[1])
    print(f"power to detect the observed gap at the published design (200 vs 30): {pw:.4f}")
    cap = PHI(abs(p1 - p2) / math.sqrt(p1 * (1 - p1) / SIM[1]) - Z_A)
    print(f"power with the simulation arm fixed at 200 and unlimited real episodes: {cap:.4f}")
    print(f"real episodes for that cap to be within 0.01: {next(n for n in range(30, 10**7) if cap - power(p1, SIM[1], p2, n) < 0.01)}")
    print(f"minimum detectable gap at 80% power, 200 vs 30 (p = 0.5): {min_detectable(SIM[1], REAL[1]):.4f}")
    print(f"minimum detectable gap at 80% power, 200 vs 200 (p = 0.5): {min_detectable(SIM[1], SIM[1]):.4f}")
    print(f"episodes per arm (equal arms) to detect 0.555 vs 0.500 at 80% power: {equal_n(p1, p2)}")
    # Anti-vacuity: the same test can say "different", and gives exactly 1 for identical counts.
    k1 = fisher_two_sided(111, 200, 5, 30)
    k2 = fisher_two_sided(15, 30, 15, 30)
    print(f"control K1, 111/200 vs 5/30: Fisher p {float(k1):.6f} ({'below' if k1 < Fraction(1, 20) else 'not below'} 0.05)")
    print(f"control K2, 15/30 vs 15/30: Fisher p {k2} (exact)")
    ok = k1 < Fraction(1, 20) and k2 == 1
    print(f"controls: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
