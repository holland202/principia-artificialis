#!/usr/bin/env python3
"""
kx_probe.py -- Does geometric complexity predict where extra computation helps?

REGISTERED BEFORE FIRST RUN. Predictions P0-P4 below. Pure NumPy, no training,
no optimizer, no seeds beyond the graph/signal generator. Deterministic.

THE QUESTION
    Adaptive-compute proposals say "high geometric complexity -> spend more
    compute there." That is an engineering hypothesis, not a theorem. This
    script tests it at MATCHED TOTAL BUDGET, which is the only way to separate
    "geometry tells you where to spend" from "spending more helps."

THE SETUP
    Omega : an undirected graph, 3 stitched regions (grid / tree / clique-chain)
    G     : permutation (node relabelling) -- nothing here is orientation-aware
    K(x)  : Forman-Ricci curvature, simplified unweighted form
                F(u,v) = 4 - deg(u) - deg(v)
            node curvature kappa_i = mean of F over incident edges.
            STATED EXPLICITLY per the contract: this is combinatorial
            Forman-Ricci, NOT Gaussian, scalar, sectional, or Ollivier-Ricci.
            No claim here transfers to those without re-measuring.
    task  : each node i has a TRUE required radius r_i. The target is the mean
            of the node signal over the r_i-hop neighbourhood. A predictor that
            looks c_i hops out incurs error (mean_{c_i} - mean_{r_i})^2.
            So this is a PURE ALLOCATION problem: no weights are learned, and
            the only decision is how many hops each node gets.
    budget: total cost = sum_i |N_{c_i}(i)|, held equal across every arm by a
            greedy filler. Every arm spends the same. Nobody buys a win.

ARMS
    uniform    round-robin allocation           -- the floor that must be beaten
    kx         allocate by kappa_i              -- the hypothesis
    inv-kx     allocate by -kappa_i             -- spend where geometry is flat
    shuffled   kappa_i permuted across nodes    -- ANTI-VACUITY
    oracle     allocate by r_i itself           -- the ceiling

CONDITIONS
    coupled    r_i is set by region, so geometry and required radius are
               correlated BY CONSTRUCTION. This is the friendly case.
    decoupled  r_i is permuted across nodes, destroying that correlation while
               leaving both marginal distributions identical. The hypothesis
               MUST fail here. If it does not, the harness is broken.

PREDICTIONS (registered before the first run)
    P0  ANTI-VACUITY. In coupled, oracle must beat uniform by >10% relative
        MSE, and shuffled must not beat uniform by more than 2%. If oracle
        cannot win, the allocation channel carries nothing and NO claim is
        made in either direction. If shuffled wins, the comparison is
        confounded and NO claim is made.
    P1  In coupled, Spearman(kappa_i, r_i) is non-zero -- curvature carries
        information about required radius.
    P2  In coupled, kx beats uniform by >10% relative MSE at matched budget.
    P3  In decoupled, kx is within 2% of uniform. The instrument returns null
        when the hypothesis is false.
    P4  UNRUN, left open deliberately: repeat with Ollivier-Ricci curvature
        instead of Forman-Ricci. Forman is a degree expression and may be
        acting as a degree proxy rather than as curvature. P4 is the
        experiment that would tell those two apart.

HARNESS GATES (must pass before any P is reported)
    H1  oracle error is exactly 0 when c_i == r_i is affordable
    H2  every arm spends within 1 unit of the same total budget
    H3  shuffled kappa has the same multiset of values as true kappa
    H4  decoupled r has the same multiset of values as coupled r

Author: Chad Edward Holland. Method and implementation with Claude (Anthropic).
The framing question is taken from an AI-authored critique of a GDL system
prompt, which posed it in a box and did not answer it.
Vincit Omnia Veritas.
"""

import numpy as np
from collections import deque

# ----------------------------------------------------------------- graph build

def build_graph(seed=0):
    """Three stitched regions with deliberately different local structure.

    Returns adj (list of sets), region (int array), n.
      region 0 : 2D grid        -- degree ~4, locally flat
      region 1 : binary tree    -- degree ~3, bottlenecked
      region 2 : chain of cliques -- high degree, densely connected
    """
    rng = np.random.default_rng(seed)
    adj = []
    region = []

    def new_node(r):
        adj.append(set())
        region.append(r)
        return len(adj) - 1

    def link(a, b):
        if a != b:
            adj[a].add(b)
            adj[b].add(a)

    # region 0: 12x12 grid
    W = 12
    grid = [[new_node(0) for _ in range(W)] for _ in range(W)]
    for i in range(W):
        for j in range(W):
            if i + 1 < W:
                link(grid[i][j], grid[i + 1][j])
            if j + 1 < W:
                link(grid[i][j], grid[i][j + 1])

    # region 1: binary tree, 127 nodes
    tree = [new_node(1) for _ in range(127)]
    for i in range(1, 127):
        link(tree[i], tree[(i - 1) // 2])

    # region 2: chain of 12 cliques of size 6
    cliques = []
    for _ in range(12):
        c = [new_node(2) for _ in range(6)]
        for a in range(6):
            for b in range(a + 1, 6):
                link(c[a], c[b])
        cliques.append(c)
    for k in range(11):
        link(cliques[k][-1], cliques[k + 1][0])

    # stitch the three regions with a few bridges
    link(grid[0][0], tree[0])
    link(grid[W - 1][W - 1], cliques[0][0])
    link(tree[63], cliques[6][2])

    n = len(adj)
    return adj, np.array(region), n


# ------------------------------------------------------------ K(x): curvature

def forman_curvature(adj):
    """Simplified unweighted Forman-Ricci. Edge: F = 4 - deg(u) - deg(v).
    Node value is the mean over incident edges. Stated, not substituted."""
    deg = np.array([len(a) for a in adj], dtype=float)
    n = len(adj)
    kappa = np.zeros(n)
    for i, nbrs in enumerate(adj):
        if not nbrs:
            kappa[i] = 0.0
            continue
        kappa[i] = np.mean([4.0 - deg[i] - deg[j] for j in nbrs])
    return kappa


def hop_sets(adj, rmax):
    """neigh[i][r] = array of node ids within r hops of i (inclusive)."""
    n = len(adj)
    out = []
    for s in range(n):
        seen = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            if seen[u] >= rmax:
                continue
            for v in adj[u]:
                if v not in seen:
                    seen[v] = seen[u] + 1
                    q.append(v)
        per_r = []
        for r in range(rmax + 1):
            per_r.append(np.array([k for k, d in seen.items() if d <= r], dtype=int))
        out.append(per_r)
    return out


# --------------------------------------------------------- budget allocation

def _alloc_at(scores_norm, lam, cmin, cmax):
    c = np.rint(cmin + lam * scores_norm * (cmax - cmin))
    return np.clip(c, cmin, cmax).astype(int)


def greedy_allocate(scores, cost, budget, cmin, cmax):
    """Allocate hops from a score, at a fixed total budget.

    HARNESS DEFECT, first run 2026-08-08, kept: the original version started
    every node at cmin and handed out +1 in score order. Because the budget
    happened to equal the cost of all-nodes-at-2, the first pass lifted every
    node to 2 and consumed the budget exactly -- so all five arms produced
    identical allocations and identical MSE. P0 caught it. The instrument was
    dead and the gate said so before any prediction was reported.

    Replacement: bisect a gain lambda on the normalized score, then spend any
    remainder in score order (or claw back in reverse) so every arm lands on
    the same total. Deterministic; ties broken by node index.
    """
    s = np.asarray(scores, dtype=float)
    rng_s = s.max() - s.min()
    sn = (s - s.min()) / rng_s if rng_s > 0 else np.full(len(s), 0.5)

    def spend(c):
        return int(sum(cost[i][c[i]] for i in range(len(c))))

    lo, hi = 0.0, 8.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if spend(_alloc_at(sn, mid, cmin, cmax)) <= budget:
            lo = mid
        else:
            hi = mid
    c = _alloc_at(sn, lo, cmin, cmax)
    spent = spend(c)

    order = np.lexsort((np.arange(len(s)), -sn))
    for i in order:                      # top up
        while c[i] < cmax:
            m = cost[i][c[i] + 1] - cost[i][c[i]]
            if spent + m > budget:
                break
            c[i] += 1
            spent += m
    for i in order[::-1]:                # claw back if over
        while spent > budget and c[i] > cmin:
            spent -= cost[i][c[i]] - cost[i][c[i] - 1]
            c[i] -= 1
    return c, spent


# --------------------------------------------------------------- the measure

def run_arm(c, neigh, x_samples, r_true):
    """MSE between the c-hop mean and the r-hop mean, averaged over signals."""
    n = len(c)
    errs = []
    for x in x_samples:
        pred = np.array([x[neigh[i][c[i]]].mean() for i in range(n)])
        targ = np.array([x[neigh[i][r_true[i]]].mean() for i in range(n)])
        errs.append((pred - targ) ** 2)
    return float(np.mean(errs))


def _midrank(x):
    """Average ranks for ties.

    DEFECT, found on device 2026-08-09, kept: the original ranked by
    double-argsort with no tie correction. r_true takes 3 distinct values
    across 343 nodes and kappa takes 17, so almost everything is tied, and
    np.argsort defaults to an UNSTABLE sort -- the result depended on which
    sort path the build took. Same data, same NumPy: quicksort and heapsort
    gave +0.1170, mergesort and stable gave +0.2076, the S25 gave +0.1327.
    Correct tie-corrected value is +0.1480. Every MSE in this script was
    bit-identical across machines; only this statistic drifted, and it was
    the one prediction that PASSED."""
    order = np.argsort(x, kind="stable")
    ranks = np.empty(len(x), float)
    s_, i = x[order], 0
    while i < len(s_):
        j = i
        while j + 1 < len(s_) and s_[j + 1] == s_[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def spearman(a, b):
    ra = _midrank(np.asarray(a, float))
    rb = _midrank(np.asarray(b, float))
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / d) if d > 0 else 0.0


# --------------------------------------------------------------------- driver

CMIN, CMAX = 1, 4
NSIG = 40


def main():
    print("=" * 68)
    print("kx_probe -- does geometric complexity predict where compute helps?")
    print("=" * 68)

    adj, region, n = build_graph()
    deg = np.array([len(a) for a in adj])
    print(f"\ngraph: n={n} nodes, {sum(deg)//2} edges, "
          f"degree min/mean/max = {deg.min()}/{deg.mean():.2f}/{deg.max()}")
    print(f"regions: grid={int((region==0).sum())} "
          f"tree={int((region==1).sum())} clique={int((region==2).sum())}")

    kappa = forman_curvature(adj)
    print(f"K(x) = Forman-Ricci (unweighted): "
          f"min {kappa.min():.3f}  mean {kappa.mean():.3f}  max {kappa.max():.3f}")

    neigh = hop_sets(adj, CMAX)
    cost = [[len(neigh[i][r]) for r in range(CMAX + 1)] for i in range(n)]

    # true required radius, by region (coupled) and permuted (decoupled)
    r_by_region = {0: 3, 1: 2, 2: 1}
    r_coupled = np.array([r_by_region[g] for g in region])
    rng = np.random.default_rng(7)
    r_decoupled = rng.permutation(r_coupled)

    # signals
    sig_rng = np.random.default_rng(11)
    x_samples = [sig_rng.standard_normal(n) for _ in range(NSIG)]

    # Budget = exactly what the TRUE allocation costs in the coupled
    # condition. Same number used in both conditions. This is the honest
    # framing of the question: given precisely enough compute to do it right,
    # does curvature tell you where to put it?
    budget = sum(cost[i][r_coupled[i]] for i in range(n))
    print(f"matched budget: {budget} neighbourhood-units "
          f"(hops per node bounded to [{CMIN},{CMAX}])")

    kappa_shuf = np.random.default_rng(3).permutation(kappa)

    gates = {}
    results = {}

    for cond, r_true in (("coupled", r_coupled), ("decoupled", r_decoupled)):
        arms = {
            "uniform":  np.zeros(n),
            "kx":       kappa,
            "inv-kx":  -kappa,
            "shuffled": kappa_shuf,
            "oracle":   r_true.astype(float),
        }
        print(f"\n--- {cond} ---")
        print(f"    Spearman(kappa, r_true) = {spearman(kappa, r_true):+.4f}")
        row = {}
        spends = []
        for name, sc in arms.items():
            c, spent = greedy_allocate(sc, cost, budget, CMIN, CMAX)
            mse = run_arm(c, neigh, x_samples, r_true)
            row[name] = (mse, c, spent)
            spends.append(spent)
            print(f"    {name:9s} MSE {mse:.6f}   spend {spent:6d}   "
                  f"hops mean {c.mean():.3f}")
        results[cond] = row
        gates[f"H2_{cond}"] = (max(spends) - min(spends)) <= 1

    # ---- harness gates
    c_or, _ = greedy_allocate(r_coupled.astype(float), cost, budget, CMIN, CMAX)
    exact = int((c_or == r_coupled).sum())
    gates["H1"] = run_arm(r_coupled, neigh, x_samples, r_coupled) == 0.0
    gates["H3"] = np.array_equal(np.sort(kappa_shuf), np.sort(kappa))
    gates["H4"] = np.array_equal(np.sort(r_decoupled), np.sort(r_coupled))

    print("\n--- harness gates ---")
    for k in sorted(gates):
        print(f"    {k:14s} {'PASS' if gates[k] else 'FAIL'}")
    print(f"    (oracle allocation reproduces r_i exactly on "
          f"{exact}/{n} nodes at this budget)")

    if not all(gates.values()):
        print("\nHARNESS FAILED -- no predictions reported.")
        return 1

    # ---- registered predictions
    def rel(a, b):
        return (b - a) / b  # positive => a is better than b

    cp, dc = results["coupled"], results["decoupled"]
    u_c = cp["uniform"][0]
    g_or = rel(cp["oracle"][0], u_c)
    g_sh = rel(cp["shuffled"][0], u_c)
    g_kx = rel(cp["kx"][0], u_c)
    g_iv = rel(cp["inv-kx"][0], u_c)
    g_dc = rel(dc["kx"][0], dc["uniform"][0])
    rho = spearman(kappa, r_coupled)

    print("\n" + "=" * 68)
    print("REGISTERED PREDICTIONS")
    print("=" * 68)

    p0 = (g_or > 0.10) and (g_sh <= 0.02)
    print(f"P0 anti-vacuity  {'PASS' if p0 else 'FAIL'}  "
          f"oracle {g_or:+.4f} (bar >+0.10), shuffled {g_sh:+.4f} (bar <=+0.02)")
    if not p0:
        print("\n   P0 failed. The allocation channel is not demonstrably live,")
        print("   so NO claim is made in either direction. P1-P3 not reported.")
        return 0

    print(f"P1 correlation   {'PASS' if abs(rho) > 0.05 else 'FAIL'}  "
          f"Spearman(kappa, r) = {rho:+.4f}")
    print(f"P2 kx > uniform  {'PASS' if g_kx > 0.10 else 'FAIL'}  "
          f"relative MSE gain {g_kx:+.4f} (bar >+0.10)")
    print(f"P3 null decoupled {'PASS' if abs(g_dc) < 0.02 else 'FAIL'} "
          f"relative gain {g_dc:+.4f} (bar |.|<0.02)")
    print(f"   (inv-kx in coupled: {g_iv:+.4f} -- spending where geometry is "
          f"flat)")
    print("\nP4 UNRUN: repeat with Ollivier-Ricci. Forman-Ricci is a degree")
    print("   expression here and may be a degree proxy, not curvature.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
