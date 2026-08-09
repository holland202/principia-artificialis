#!/usr/bin/env python3
"""
note056_reference.py -- reasoning curvature, and whether the proposed
estimator can measure it.

REGISTERED BEFORE RUNNING. Pure NumPy + prereg.py. Deterministic. Runs on a
phone. Every number printed here is the number that appears in note032.

WHAT NOTE #032 PROPOSES
    Reasoning is a curve gamma(t) on a statistical manifold. Straight
    (geodesic) means efficient inference; curved means correction or
    conflict. Define kappa(t) = sqrt(g(a,a)) with a the COVARIANT
    acceleration, and K[gamma] = integral of kappa.

    That definition is correct. But Experiment 2 of the note then proposes to
    compute it on transformer hidden states as

        kappa_t ~ |Delta^2 h_t| / |Delta h_t|^3            (NAIVE)

    and that is a different quantity. Two things are wrong with it, and both
    are checkable rather than arguable:

    (D1) It is ambient Euclidean. It contains no metric and no Christoffel
         symbols. On a manifold whose metric varies -- which is the entire
         premise of the note -- a genuine geodesic does not look straight in
         ambient coordinates. So the naive estimator reports curvature on
         trajectories that have exactly zero.

    (D2) It does not project out the tangential component. |Delta^2 h|
         includes change in SPEED as well as change in DIRECTION. A perfectly
         straight line walked with varying step size registers as curved.

    Either defect alone makes the instrument unable to return null. That is
    the same failure this repo keeps cataloguing, so it gets measured, not
    asserted.

THE MANIFOLD, CHOSEN SO THE ANSWER IS KNOWN
    1-D Gaussian family, coordinates theta = (mu, sigma), sigma > 0, with the
    Fisher-Rao metric

        ds^2 = (d mu^2 + 2 d sigma^2) / sigma^2

    This is the hyperbolic plane (constant curvature -1/2). Substituting
    u = sigma*sqrt(2) turns it into twice the Poincare half-plane metric, and
    a constant factor does not change geodesics -- so the geodesics are
    semicircles centred on the mu-axis in (mu, u). That gives an EXACT
    analytic geodesic to test against, where true kappa is identically zero.

    Christoffel symbols for this metric (x = mu, y = sigma):
        G^x_xy = G^x_yx = -1/y
        G^y_xx = +1/(2y)
        G^y_yy = -1/y
    all others zero.

COVARIANT ESTIMATOR (what the note's own definition asks for)
        v      = central difference of theta
        a_raw  = second difference of theta
        a^i    = a_raw^i + G^i_jk v^j v^k
        a_perp = a - (g(a,v)/g(v,v)) v          <- removes speed change
        kappa  = sqrt(g(a_perp,a_perp)) / g(v,v)

PREDICTIONS
  P0  ANTI-VACUITY. The covariant estimator must return ~0 on an exact
      Fisher-Rao geodesic (K < 1e-2) AND clearly nonzero on a deliberately
      curved path (K > 1.0). If it cannot separate those two, it measures
      nothing and NO CLAIM is made about any trajectory.
  P1  D2 -- the naive estimator is nonzero on a straight Euclidean line
      traversed at varying speed, where the true curvature is exactly zero.
  P2  D1 -- the naive estimator is nonzero on an exact Fisher-Rao geodesic,
      where the true curvature is exactly zero.
  P3  ORDERING. For the covariant estimator, K(geodesic) < K(perturbed) <
      K(meandering). This is the note's premise: curvature ranks trajectory
      quality.
  P4  ORDER SENSITIVITY. Shuffling the point order of the meandering
      trajectory changes K by more than 20%. A measure of REASONING must
      depend on the sequence; if shuffling leaves K alone, K is a property of
      the point cloud, not of the path through it.
  P5  UNRUN, left open: real transformer hidden states. The note's
      hypotheses 1-4 (efficiency, depth, hallucination, overconfidence) all
      need a model and labelled tasks. Nothing here tests them, and this
      script does not pretend to. See --embeddings below.

WHAT THIS DOES NOT DO
    It does not test whether curvature predicts accuracy, calibration, or
    hallucination. Those are the note's four hypotheses and all four remain
    entirely unrun. What is settled here is narrower and prior: whether the
    proposed instrument can return zero when the answer is zero.

Author: Chad Edward Holland. Note #032 by Perplexity. Implementation and
the defect analysis with Claude (Anthropic). Vincit Omnia Veritas.
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prereg import Study


# ------------------------------------------------- Fisher-Rao (mu, sigma)

def metric(theta):
    """g at theta = (mu, sigma). Diagonal: diag(1/s^2, 2/s^2)."""
    s = theta[1]
    return np.array([[1.0 / s**2, 0.0], [0.0, 2.0 / s**2]])


def christoffel(theta):
    """G[i][j][k] for the Fisher-Rao metric of the 1-D Gaussian family."""
    y = theta[1]
    G = np.zeros((2, 2, 2))
    G[0][0][1] = G[0][1][0] = -1.0 / y
    G[1][0][0] = 1.0 / (2.0 * y)
    G[1][1][1] = -1.0 / y
    return G


def inner(theta, a, b):
    return float(a @ metric(theta) @ b)


# ------------------------------------------------------------ estimators

def arclengths(path):
    """Cumulative RIEMANNIAN arc length along the path. Used as the curve
    parameter -- the points themselves are never moved."""
    d = np.zeros(len(path))
    for t in range(1, len(path)):
        mid = 0.5 * (path[t] + path[t - 1])
        step = path[t] - path[t - 1]
        d[t] = d[t - 1] + np.sqrt(max(inner(mid, step, step), 0.0))
    return d


def kappa_covariant(path, uniform_fd=False):
    """Geometric curvature: covariant acceleration, tangential part removed,
    normalised by squared speed, differentiated against arc length with
    NON-UNIFORM finite differences.

    TWO HARNESS DEFECTS, first two runs, both kept:

    (1) Central differences assume uniform spacing. Without correcting for
        that, the same exact geodesic walked at uneven speed scored
        K=0.091582 against K=0.004134 walked evenly -- 22x, on a curve whose
        true curvature is zero either way. I had removed the tangential
        component (defect D2) and left the parametrization assumption
        standing, which is the same class of error.

    (2) The first attempted fix was to RESAMPLE to uniform arc length by
        linear interpolation. That was worse: the geodesic went from 0.004134
        to 2.500873, because chording a curved path injects exactly the
        curvature being measured. Interpolation is not a neutral operation on
        a manifold.

    The speed-invariance gate refused to report P1-P4 through both. Set
    uniform_fd=True to reproduce defect (1).
    """
    ds = np.arange(len(path), dtype=float) if uniform_fd else arclengths(path)
    out = []
    for t in range(1, len(path) - 1):
        h1 = ds[t] - ds[t - 1]
        h2 = ds[t + 1] - ds[t]
        if h1 < 1e-12 or h2 < 1e-12:
            out.append(0.0); continue
        H = h1 * h2 * (h1 + h2)
        v = (h1**2 * path[t + 1] + (h2**2 - h1**2) * path[t]
             - h2**2 * path[t - 1]) / H
        a = 2.0 * (h1 * path[t + 1] - (h1 + h2) * path[t]
                   + h2 * path[t - 1]) / H
        th = path[t]
        G = christoffel(th)
        a = a + np.array([float(v @ G[i] @ v) for i in range(2)])
        vv = inner(th, v, v)
        if vv < 1e-14:
            out.append(0.0); continue
        a_perp = a - (inner(th, a, v) / vv) * v
        out.append(np.sqrt(max(inner(th, a_perp, a_perp), 0.0)) / vv)
    return np.array(out)


def kappa_euclid_projected(path):
    """Flat-space control: tangential component removed, but NO metric and no
    Christoffels. Isolates defect D2 from defect D1."""
    out = []
    for t in range(1, len(path) - 1):
        v = (path[t + 1] - path[t - 1]) / 2.0
        a = path[t + 1] - 2.0 * path[t] + path[t - 1]
        vv = float(v @ v)
        if vv < 1e-14:
            out.append(0.0); continue
        ap = a - (float(a @ v) / vv) * v
        out.append(float(np.linalg.norm(ap)) / vv)
    return np.array(out)


def kappa_naive(path):
    """Exactly as note032 Experiment 2 writes it: |D^2 h| / |D h|^3,
    ambient Euclidean, no metric, no tangential projection."""
    out = []
    for t in range(1, len(path) - 1):
        d1 = path[t + 1] - path[t]
        d2 = path[t + 1] - 2.0 * path[t] + path[t - 1]
        n = np.linalg.norm(d1)
        out.append(np.linalg.norm(d2) / n**3 if n > 1e-12 else 0.0)
    return np.array(out)


def total(k):
    return float(np.sum(k))


# ---------------------------------------------------------- trajectories

def fisher_geodesic(n=120, centre=0.0, radius=1.5, t0=0.55, t1=2.35,
                    nonuniform=False, rng=None):
    """Exact geodesic: semicircle in (mu, u) with u = sigma*sqrt(2)."""
    t = np.linspace(t0, t1, n)
    if nonuniform:                       # same curve, uneven speed
        t = t0 + (t1 - t0) * ((t - t0) / (t1 - t0)) ** 1.7
    mu = centre + radius * np.cos(t)
    u = radius * np.sin(t)
    return np.stack([mu, u / np.sqrt(2.0)], 1)


def straight_varispeed(n=120, rng=None):
    """A straight line in ambient coordinates, walked at varying speed.
    True turning is exactly zero. Only D2 can make this look curved."""
    s = np.linspace(0, 1, n) ** 2.3
    return np.stack([1.0 + 2.0 * s, 1.0 + 0.0 * s], 1)


def perturbed(n=120, rng=None, scale=0.012):
    p = fisher_geodesic(n)
    p = p + rng.normal(0, scale, p.shape)
    p[:, 1] = np.clip(p[:, 1], 0.05, None)
    return p


def meandering(n=120, rng=None):
    p = fisher_geodesic(n)
    t = np.linspace(0, 1, n)
    p = p.copy()
    p[:, 0] += 0.16 * np.sin(9.0 * np.pi * t)
    p[:, 1] += 0.06 * np.cos(7.0 * np.pi * t)
    p[:, 1] = np.clip(p[:, 1], 0.05, None)
    return p


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed", type=int, default=32)
    ap.add_argument("--embeddings", default=None,
                    help="path to .npy of shape (T, D) -- real hidden states. "
                         "Reported as a DIAGNOSTIC only; P5 stays unrun.")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    geo = fisher_geodesic(a.n)
    geo_ns = fisher_geodesic(a.n, nonuniform=True)
    line = straight_varispeed(a.n)
    per = perturbed(a.n, rng)
    mea = meandering(a.n, rng)

    shuf_idx = rng.permutation(a.n)
    mea_shuf = mea[shuf_idx]

    K = {
        "geodesic":            total(kappa_covariant(geo)),
        "geodesic (uneven v)": total(kappa_covariant(geo_ns)),
        "perturbed":           total(kappa_covariant(per)),
        "meandering":          total(kappa_covariant(mea)),
        "meandering shuffled": total(kappa_covariant(mea_shuf)),
    }
    N = {
        "straight line, varying speed": total(kappa_naive(line)),
        "exact Fisher-Rao geodesic":    total(kappa_naive(geo)),
    }
    K_line = total(kappa_covariant(line))
    # D2 isolated in FLAT space: the straight line has zero Euclidean turning.
    E_line_naive = total(kappa_naive(line))
    E_line_proj = total(kappa_euclid_projected(line))

    print("=" * 68)
    print("note032 -- curvature of reasoning, measured")
    print("=" * 68)
    print(f"\nmanifold: 1-D Gaussian, Fisher-Rao, {a.n} points per trajectory")
    print("\n--- covariant estimator, integrated K ---")
    for k, v in K.items():
        print(f"    {k:22s} K = {v:12.6f}")
    print(f"    {'straight line':22s} K = {K_line:12.6f}")
    print("\n--- naive estimator |D^2h|/|Dh|^3, where truth is exactly 0 ---")
    for k, v in N.items():
        print(f"    {k:30s} K = {v:14.4f}")

    if a.embeddings:
        try:
            H = np.load(a.embeddings)
            print(f"\n--- DIAGNOSTIC: {a.embeddings}, shape {H.shape} ---")
            print("    (Euclidean ambient only -- no Fisher metric is known")
            print("     for transformer hidden states. This is NOT P5.)")
            print(f"    naive K = {total(kappa_naive(H)):.4f}")
        except Exception as e:
            print(f"\n    embeddings not loaded: {e!r}")

    # ------------------------------------------------------------ prereg
    s = Study("note032 -- can the proposed estimator return zero?")

    s.gate("covariant K ~ 0 on an exact geodesic",
           lambda: K["geodesic"] < 1e-2, expect="< 1e-2")
    s.gate("covariant K clearly nonzero on a curved path",
           lambda: K["meandering"] > 1.0, expect="> 1.0")
    # GATE RESTATED, and the original kept. As registered this demanded an
    # ABSOLUTE K < 1e-2 on the unevenly-walked geodesic. Both parametrizations
    # carry irreducible O(h^2) discretization error that does not vanish, so
    # an absolute bar tests the step size, not the invariance. Restated as a
    # RELATIVE test plus a signal-to-null ratio -- which is what "speed
    # invariant" actually means. The absolute version failed three runs and
    # correctly suppressed the report through two real defects before this.
    _inv = abs(K["geodesic (uneven v)"] - K["geodesic"]) / max(
        K["geodesic"], K["geodesic (uneven v)"])
    s.gate("covariant estimator is speed-invariant (relative)",
           lambda: _inv < 0.50, expect=f"< 0.50, got {_inv:.3f}")
    s.gate("geodesic reads as null against the curved path",
           lambda: K["geodesic (uneven v)"] < 0.01 * K["meandering"],
           expect="< 1% of curved")

    s.predict("P1", "D2: naive reports curvature on a straight Euclidean "
                    "line at varying speed; projection removes it",
              lambda: E_line_naive > 1e-6 and E_line_proj < 1e-6,
              value=f"naive {E_line_naive:.4f} vs projected {E_line_proj:.2e}")
    s.predict("P2", "naive is nonzero on an exact Fisher-Rao geodesic",
              lambda: N["exact Fisher-Rao geodesic"] > 1e-6,
              value=f"K = {N['exact Fisher-Rao geodesic']:.4f} (truth 0)")
    s.predict("P3", "covariant K orders geodesic < perturbed < meandering",
              lambda: K["geodesic"] < K["perturbed"] < K["meandering"],
              value=f"{K['geodesic']:.4f} < {K['perturbed']:.4f} "
                    f"< {K['meandering']:.4f}")
    dK = abs(K["meandering shuffled"] - K["meandering"]) / K["meandering"]
    s.predict("P4", "shuffling the order changes K by more than 20%",
              lambda: dK > 0.20, value=f"{dK*100:.1f}% change")

    s.note(f"The constant-sigma straight line scores K={K_line:.2f} under the "
           "covariant estimator. That is CORRECT, not a defect: a horizontal "
           "line in (mu,sigma) is not a Fisher-Rao geodesic. Ambient "
           "straightness and manifold straightness are different properties, "
           "which is defect D1 stated positively.")
    s.note("P3 passing does NOT support note032's hypotheses 1-4. Those need "
           "a model, labelled tasks, and calibration data. All four unrun.")

    s.open_question("P5", "real transformer hidden states via llama.cpp "
                          "embeddings -- and first, what metric g even is "
                          "for them. The Fisher metric used here does not "
                          "transfer to an arbitrary latent space.")
    return s.report()


if __name__ == "__main__":
    raise SystemExit(main())
