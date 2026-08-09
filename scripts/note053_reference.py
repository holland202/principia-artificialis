"""
SOFT-HyperDGA v0 — a differentiable relaxation of Hyperbolic Delaunay
Geometric Alignment. Registered 2026-08-08, before running.

MOTIVATION (their words, not mine). Medbouhi et al., arXiv:2404.08608,
Section 6: HyperDGA "takes values in rational numbers... As a consequence,
it is discontinuous and therefore non-differentiable, which is necessary
in the context of gradient-based optimization... designing continuous and
differentiable versions of HyperDGA represents a promising line for future
research."

HyperDGA(A,B) = 1 - |E_het| / |E|, counting Delaunay edges that connect a
point of A to a point of B. Edge counts are integers, so the score is
piecewise constant: its gradient is zero almost everywhere and undefined
at the flips. That is the blocker.

THE RELAXATION. A Delaunay edge (i,j) exists exactly when Voronoi cells i
and j share a facet. Facet MEASURE is continuous and goes to zero exactly
where the edge is about to flip. So replace the 0/1 edge indicator with
shared-boundary mass:

    p_i(x) = softmax_i( -d_H(x, site_i)^2 / tau )     over sites
    w_ij   = sum_x p_i(x) * p_j(x)                    (peaks on the bisector)
    softHyperDGA(A,B) = 1 - (sum_{i in A, j in B} w_ij) / (sum_{i<j} w_ij)

As tau -> 0 the softmax hardens and w_ij concentrates on genuine shared
facets, recovering the discrete count. Every term is smooth in the point
coordinates, so the whole score is differentiable.

PRIOR ART, STATED HONESTLY: weighting by Voronoi cell overlap is the same
machinery behind natural-neighbour (Sibson / Laplace) coordinates in
Euclidean computational geometry, which are known to be smooth away from
the sites. Nothing here invents that. What is new, if anything, is
applying it in the hyperbolic (Klein) setting to make HyperDGA itself
differentiable -- the gap the authors name.

HONEST LIMITATION, UP FRONT: this computes the hyperbolic Voronoi diagram
by SAMPLING the Klein disk on a grid, not by exact combinatorial
construction via the power-diagram route of their Theorem 1. So the "hard"
reference here is a grid-approximated Delaunay graph, not the exact one.
Everything below is a statement about that approximation. n=2 only.

REGISTERED:
  P0 ANTI-VACUITY. The problem must be real in this setup: under small
     random perturbations of one point, the HARD score must be EXACTLY
     unchanged in >30% of trials (zero gradient), while the SOFT score
     changes measurably in >90%. If hard also always moves, there is no
     discontinuity here to fix and NO CLAIM is made.
  P1 FIDELITY. As tau falls, soft approaches hard: |soft(tau_min) - hard|
     < 0.05.
  P2 USEFULNESS PRESERVED. Pull two clusters apart in the disk; the soft
     score must rise monotonically (Spearman rho > 0.9). This is the
     property that made HyperDGA worth having; a smooth version that
     loses it is worthless.
  P3 GRADIENT IS REAL. Central-difference gradient of the soft score wrt
     one point's coordinates must be finite and non-negligible
     (norm > 1e-6), where the hard score's is 0.
"""
import numpy as np

# ---------- Klein-Beltrami geometry ----------
def klein_dist(X, Y):
    """Pairwise hyperbolic distance in the Klein disk.
    d(x,y) = arccosh( (1 - <x,y>) / sqrt((1-|x|^2)(1-|y|^2)) )"""
    G = X @ Y.T
    nx = 1.0 - np.sum(X*X, axis=1)
    ny = 1.0 - np.sum(Y*Y, axis=1)
    denom = np.sqrt(np.maximum(1e-12, np.outer(nx, ny)))
    arg = np.clip((1.0 - G) / denom, 1.0, None)
    return np.arccosh(arg)

def disk_grid(res=180, rmax=0.985):
    g = np.linspace(-rmax, rmax, res)
    XX, YY = np.meshgrid(g, g)
    P = np.stack([XX.ravel(), YY.ravel()], axis=1)
    keep = np.sum(P*P, axis=1) < rmax**2
    return P[keep], keep, res

def softmax_rows(S):
    S = S - S.max(axis=1, keepdims=True)
    E = np.exp(S)
    return E / E.sum(axis=1, keepdims=True)

# ---------- the two scores ----------
def soft_hyperdga(sites, labels, grid, tau):
    D = klein_dist(grid, sites)              # (Ngrid, n)
    P = softmax_rows(-(D**2) / tau)
    W = P.T @ P                              # (n, n) shared-boundary mass
    np.fill_diagonal(W, 0.0)
    A = labels == 0
    B = labels == 1
    het = W[np.ix_(A, B)].sum() * 2.0        # both orderings
    tot = W.sum()
    return 1.0 - het / max(tot, 1e-15)

def hard_hyperdga(sites, labels, grid, res, keep):
    """Grid-approximate Delaunay: cells adjacent on the raster share a facet."""
    D = klein_dist(grid, sites)
    lab = np.argmin(D, axis=1)
    full = np.full(res*res, -1, dtype=int)
    full[keep] = lab
    L = full.reshape(res, res)
    edges = set()
    for a, b in ((L[:, :-1], L[:, 1:]), (L[:-1, :], L[1:, :])):
        m = (a >= 0) & (b >= 0) & (a != b)
        for u, v in zip(a[m], b[m]):
            edges.add((min(u, v), max(u, v)))
    if not edges:
        return 1.0
    het = sum(1 for u, v in edges if labels[u] != labels[v])
    return 1.0 - het / len(edges)

# ---------- setup ----------
rng = np.random.default_rng(7)
grid, keep, res = disk_grid()
print("="*72)
print("SOFT-HyperDGA v0 — registered before running")
print("="*72)
print(f"grid points inside Klein disk: {len(grid)}   (res {res}x{res})")

def two_clusters(sep, n_per=9, spread=0.10, seed=3):
    r = np.random.default_rng(seed)
    A = r.normal([-sep, 0.0], spread, size=(n_per, 2))
    B = r.normal([+sep, 0.0], spread, size=(n_per, 2))
    P = np.vstack([A, B])
    nrm = np.linalg.norm(P, axis=1, keepdims=True)
    P = np.where(nrm > 0.90, P * (0.90/np.maximum(nrm,1e-12)), P)
    lab = np.array([0]*n_per + [1]*n_per)
    return P, lab

sites, labels = two_clusters(0.30)
TAU = 0.02

# ---------- P0 anti-vacuity ----------
print("\n--- P0 ANTI-VACUITY: is the discontinuity real here? ---")
h0 = hard_hyperdga(sites, labels, grid, res, keep)
s0 = soft_hyperdga(sites, labels, grid, TAU)
hard_frozen = 0; soft_moved = 0; TRIALS = 30
for t in range(TRIALS):
    q = sites.copy()
    k = rng.integers(0, len(q))
    q[k] += rng.normal(0, 8e-4, size=2)
    h = hard_hyperdga(q, labels, grid, res, keep)
    s = soft_hyperdga(q, labels, grid, TAU)
    if h == h0: hard_frozen += 1
    if abs(s - s0) > 1e-9: soft_moved += 1
fh, fs = hard_frozen/TRIALS, soft_moved/TRIALS
print(f"  hard score EXACTLY unchanged : {100*fh:.0f}% of {TRIALS} perturbations")
print(f"  soft score measurably moved  : {100*fs:.0f}%")
p0 = (fh > 0.30) and (fs > 0.90)
print(f"  P0 -> {p0}")
if not p0:
    print("  NO CLAIM. Either there is no discontinuity to fix, or the")
    print("  relaxation is not tracking the geometry.")

# ---------- P1 fidelity ----------
print("\n--- P1 FIDELITY: soft -> hard as tau falls ---")
print(f"  hard (grid Delaunay) = {h0:.4f}")
for tau in (0.5, 0.2, 0.08, 0.03, 0.01):
    print(f"    tau={tau:<5} soft={soft_hyperdga(sites, labels, grid, tau):.4f}")
s_min = soft_hyperdga(sites, labels, grid, 0.01)
p1 = abs(s_min - h0) < 0.05
print(f"  |soft(0.01) - hard| = {abs(s_min-h0):.4f}   P1 -> {p1}")

# ---------- P2 usefulness preserved ----------
print("\n--- P2 USEFULNESS: score rises as clusters separate ---")
seps, softs, hards = [], [], []
for sep in np.linspace(0.05, 0.60, 8):
    st, lb = two_clusters(sep)
    seps.append(sep)
    softs.append(soft_hyperdga(st, lb, grid, TAU))
    hards.append(hard_hyperdga(st, lb, grid, res, keep))
    print(f"    sep={sep:.2f}   soft={softs[-1]:.4f}   hard={hards[-1]:.4f}")
def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0,1])
rho = spearman(seps, softs)
p2 = rho > 0.9
print(f"  Spearman(separation, soft) = {rho:.4f}   P2 -> {p2}")

# ---------- P3 gradient ----------
print("\n--- P3 GRADIENT: finite and non-negligible where hard is zero ---")
eps = 1e-4; k = 0; g = np.zeros(2)
for d in range(2):
    up = sites.copy(); up[k, d] += eps
    dn = sites.copy(); dn[k, d] -= eps
    g[d] = (soft_hyperdga(up, labels, grid, TAU) - soft_hyperdga(dn, labels, grid, TAU)) / (2*eps)
gh = np.zeros(2)
for d in range(2):
    up = sites.copy(); up[k, d] += eps
    dn = sites.copy(); dn[k, d] -= eps
    gh[d] = (hard_hyperdga(up, labels, grid, res, keep) - hard_hyperdga(dn, labels, grid, res, keep)) / (2*eps)
p3 = np.isfinite(g).all() and np.linalg.norm(g) > 1e-6
print(f"  soft gradient wrt point 0 : [{g[0]:+.5f}, {g[1]:+.5f}]  |g|={np.linalg.norm(g):.5f}")
print(f"  hard gradient wrt point 0 : [{gh[0]:+.5f}, {gh[1]:+.5f}]  |g|={np.linalg.norm(gh):.5f}")
print(f"  P3 -> {p3}")

print("\n" + "="*72)
print(f"  P0 anti-vacuity {p0} | P1 fidelity {p1} | P2 usefulness {p2} | P3 gradient {p3}")
if not p0:
    print("  P0 failed -> no claim is made on P1-P3 regardless of their values.")
print("="*72)
