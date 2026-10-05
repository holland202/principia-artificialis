#!/usr/bin/env python3
"""note066_reference.py - Note #066, the Ambiguity Engine.

  python scripts/note066_reference.py            # every number in the note (explore table at this commit)
  python scripts/note066_reference.py --explore  # the exploratory chain check only

1-D mass-spring chain between two uniform leads; transmission of a plane wave by transfer matrices.
Lossless: scattering only.
"""
import sys

import numpy as np

K, M0 = 1.0, 2.0


def transmission(masses, ws):
    """Plane-wave power transmission through the chain at each frequency in ws (lead mass M0, spring K)."""
    ws = np.asarray(ws, dtype=float)
    q = np.arccos(1 - M0 * ws ** 2 / (2 * K))
    M = np.tile(np.eye(2, dtype=complex), (len(ws), 1, 1))
    for m in masses:
        A = np.zeros((len(ws), 2, 2), dtype=complex)
        A[:, 0, 0] = (2 * K - m * ws ** 2) / K
        A[:, 0, 1] = -1
        A[:, 1, 0] = 1
        M = A @ M
    P = np.zeros((len(ws), 2, 2), dtype=complex)
    P[:, 0, 0], P[:, 0, 1], P[:, 1, :] = np.exp(1j * q), np.exp(-1j * q), 1
    W = np.linalg.solve(P, M @ P)
    return np.abs(1 / W[:, 1, 1]) ** 2


def explore():
    n = 200
    ws = np.linspace(0.05, np.sqrt(4 * K / M0) - 0.05, 400)
    rng = np.random.default_rng(0)
    arms = {"uniform (control)": [np.full(n, 2.0)],
            "periodic 1,3,1,3": [np.tile([1.0, 3.0], n // 2)],
            "random U[1,3]": [rng.uniform(1, 3, n) for _ in range(30)],
            "graded 1->3": [np.linspace(1, 3, n)]}
    for name, chains in arms.items():
        t = np.mean([transmission(c, ws) for c in chains], axis=0)
        lo, hi = t[ws < 0.5].mean(), t[ws >= 0.5].mean()
        print(f"{name:20s} mean T {t.mean():.3f}   low band(w<0.5) {lo:.3f}   high band {hi:.3f}")


def main():
    print("== exploratory chain check (unregistered)")
    explore()
    return 0


if __name__ == "__main__":
    sys.exit(main())
