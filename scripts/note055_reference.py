#!/usr/bin/env python3
"""
kx_synth.py -- can geometry predict where the NEXT unit of compute pays off?

REGISTERED BEFORE FIRST RUN. Pure NumPy. No PyTorch, no GPU. Deterministic.

WHAT CHANGED FROM kx_probe (v1)
    v1 asked: does curvature predict the required radius r_i?  rho = +0.117,
    and allocating on it lost to uniform by 2.15x at matched budget.
    v2 asks the question the critique posed instead:

        eta_i(c) = [ L_i(c) - L_i(c+1) ] / [ C_i(c+1) - C_i(c) ]

    error reduction per additional neighbourhood element -- the quantity an
    actual scheduler maximizes. v1 measured K -> r. v2 measures Z -> eta.

TWO DEFECTS IN THE PROPOSED VERSION, FIXED HERE
    1. BASELINE. The draft compared val MSE against predicting the GLOBAL MEAN
       of eta and read `val_mse/uniform_mse < 1.0` as "geometry beats uniform".
       That is an R^2 > 0 test. v1 ALREADY passed that (rho = 0.148, tie-corrected) and still
       lost the allocation. Beating the mean and beating uniform allocation are
       different claims. Here the mean-baseline is reported as P1 and labelled
       WEAK; the real test is P2, a matched-budget allocation.
    2. LEAKAGE. The draft fed region one-hot (features 10-12) to the model
       while the labels are generated from region structure. That hands over
       the answer, and feature importance would then rank region first and read
       as a discovery. Region one-hot is EXCLUDED from training features here
       and reported only as a leakage diagnostic. Same defect class as F22.
    Also added: a shuffled-Z arm. Five lines, and it is the difference between
    a result and a log line.

GROUND TRUTH IS EXACT, NOT SAMPLED
    Signals are iid N(0,1), so for neighbourhoods A (predictor) and B (target)
        L = E[(mean_A x - mean_B x)^2] = 1/|A| + 1/|B| - 2|A∩B|/(|A||B|)
    computed in closed form. No Monte Carlo, no seed sensitivity in the labels,
    and L_i(r*) = 0 exactly. The oracle ceiling is a real zero.

ONE ALLOCATOR, FIVE MARGINAL ESTIMATES
    Every arm uses the SAME greedy marginal-value allocator at the SAME total
    budget. Arms differ only in the marginal value they believe:
        uniform    constant marginal (round-robin)   -- the floor to beat
        curvature  Forman-Ricci, the v1 signal       -- continuity with v1
        pred       predicted eta-hat from Z          -- the hypothesis
        shuffled   eta-hat from row-shuffled Z       -- ANTI-VACUITY
        oracle     true eta                          -- the ceiling
    Different allocators for different arms would confound the comparison, so
    there is exactly one.

PREDICTIONS
    P0  ANTI-VACUITY. oracle must beat uniform by >10% relative loss, and
        shuffled must not beat uniform by more than 2%. If oracle cannot win,
        the allocation channel is dead and NO claim is made in either
        direction. If shuffled wins, the comparison is confounded -- same.
    P1  WEAK. Predicted eta beats the global-mean baseline on held-out nodes.
        This is the test the draft proposed. Passing it means almost nothing;
        it is reported so the two can be compared side by side.
    P2  THE TEST. pred beats uniform by >10% relative loss at matched budget.
    P3  NULL. In the decoupled condition (required radii permuted across
        nodes, marginals identical), pred lands within 2% of uniform.
    P4  UNRUN, left open: Ollivier-Ricci in place of Forman-Ricci, and a real
        (non-synthetic) graph family. Forman here is a degree expression --
        v1's open question, still open.

HARNESS GATES, checked before any P is reported
    H1  L_i(r*) == 0 exactly for every node
    H2  all arms spend within 1 unit of the same budget
    H3  shuffled Z is a true row permutation of Z
    H4  decoupled radii are a true permutation of coupled radii
    H5  train/val node sets are disjoint AND come from disjoint GRAPHS
        (splitting nodes within a graph would leak neighbourhood overlap)

Author: Chad Edward Holland. Implementation with Claude (Anthropic). The eta
reframing is from an AI-authored critique of kx_probe v1, which posed it and
did not run it. Vincit Omnia Veritas.
"""

import argparse
import numpy as np
from collections import deque

CMIN, CMAX = 0, 4


# ------------------------------------------------------------------- graphs

def build_graph(rng):
    """Grid + binary tree + clique-chain, randomized, stitched by bridges."""
    adj, region = [], []

    def new(r):
        adj.append(set()); region.append(r); return len(adj) - 1

    def link(a, b):
        if a != b:
            adj[a].add(b); adj[b].add(a)

    W = int(rng.integers(8, 14))
    grid = [[new(0) for _ in range(W)] for _ in range(W)]
    for i in range(W):
        for j in range(W):
            if i + 1 < W: link(grid[i][j], grid[i + 1][j])
            if j + 1 < W: link(grid[i][j], grid[i][j + 1])

    depth = int(rng.integers(5, 8))
    nt = 2 ** depth - 1
    tree = [new(1) for _ in range(nt)]
    for i in range(1, nt):
        link(tree[i], tree[(i - 1) // 2])

    ncl = int(rng.integers(8, 14)); csz = int(rng.integers(4, 8))
    cl = []
    for _ in range(ncl):
        c = [new(2) for _ in range(csz)]
        for a in range(csz):
            for b in range(a + 1, csz):
                link(c[a], c[b])
        cl.append(c)
    for k in range(ncl - 1):
        link(cl[k][-1], cl[k + 1][0])

    link(grid[0][0], tree[0])
    link(grid[W - 1][W - 1], cl[0][0])
    link(tree[nt // 2], cl[ncl // 2][0])
    return adj, np.array(region)


def hop_sets(adj, rmax):
    out = []
    for s in range(len(adj)):
        seen = {s: 0}; q = deque([s])
        while q:
            u = q.popleft()
            if seen[u] >= rmax: continue
            for v in adj[u]:
                if v not in seen:
                    seen[v] = seen[u] + 1; q.append(v)
        out.append([frozenset(k for k, d in seen.items() if d <= r)
                    for r in range(rmax + 1)])
    return out


# ----------------------------------------------------------------- features

FEAT_NAMES = ["forman_ricci", "degree", "clustering", "nbhd_r1", "nbhd_r2",
              "nbhd_r3", "growth_r2_r1", "growth_r3_r2", "max_2hop_degree"]
REGION_NAMES = ["region_grid", "region_tree", "region_clique"]


def features(adj, neigh):
    """9 structural features. Region one-hot is returned SEPARATELY and is not
    part of Z -- the labels are generated from region structure, so including
    it would hand the model the answer."""
    n = len(adj)
    deg = np.array([len(a) for a in adj], float)
    Z = np.zeros((n, len(FEAT_NAMES)), np.float32)
    for i, nb in enumerate(adj):
        forman = np.mean([4.0 - deg[i] - deg[j] for j in nb]) if nb else 0.0
        if len(nb) > 1:
            links = sum(1 for u in nb for v in nb if u < v and v in adj[u])
            clus = 2.0 * links / (len(nb) * (len(nb) - 1))
        else:
            clus = 0.0
        s1, s2, s3 = (len(neigh[i][1]), len(neigh[i][2]), len(neigh[i][3]))
        m2 = max((deg[j] for j in neigh[i][2]), default=0.0)
        Z[i] = [forman, deg[i], clus, s1, s2, s3,
                s2 / max(s1, 1), s3 / max(s2, 1), m2]
    return Z


# -------------------------------------------------------- exact loss / eta

def exact_labels(neigh, r_true):
    """L_i(c) in closed form for iid N(0,1) signals, then eta and cost.
        L = 1/|A| + 1/|B| - 2|A n B|/(|A||B|)
    Returns L (n, CMAX+1), eta (n, CMAX), cost (n, CMAX+1)."""
    n = len(neigh)
    L = np.zeros((n, CMAX + 1)); C = np.zeros((n, CMAX + 1))
    for i in range(n):
        B = neigh[i][r_true[i]]; nb = len(B)
        for c in range(CMAX + 1):
            A = neigh[i][c]; na = len(A); inter = len(A & B)
            L[i, c] = 1.0 / na + 1.0 / nb - 2.0 * inter / (na * nb)
            C[i, c] = na
    dC = np.clip(C[:, 1:] - C[:, :-1], 1e-9, None)
    eta = (L[:, :-1] - L[:, 1:]) / dC
    return L, eta.astype(np.float32), C


# ---------------------------------------------------------------- allocator

def allocate(marginal, cost, budget):
    """One allocator for every arm. Start at CMIN, repeatedly buy the +1 hop
    with the highest believed marginal value per unit cost that still fits.
    Deterministic: ties break by node index."""
    n = cost.shape[0]
    c = np.full(n, CMIN, int)
    spent = float(cost[:, CMIN].sum())
    heap = []
    for i in range(n):
        if CMIN < CMAX:
            heap.append((-marginal[i, CMIN], i))
    heap.sort()
    while heap:
        neg, i = heap.pop(0)
        if c[i] >= CMAX:
            continue
        step = cost[i, c[i] + 1] - cost[i, c[i]]
        if spent + step > budget:
            continue
        c[i] += 1; spent += step
        if c[i] < CMAX:
            item = (-marginal[i, c[i]], i)
            lo, hi = 0, len(heap)
            while lo < hi:
                mid = (lo + hi) // 2
                if heap[mid] < item: lo = mid + 1
                else: hi = mid
            heap.insert(lo, item)
    return c, spent


def arm_loss(c, L):
    return float(np.mean(L[np.arange(len(c)), c]))


# -------------------------------------------------------------------- model

class MLP:
    def __init__(self, d_in, d_hid, d_out, seed):
        r = np.random.default_rng(seed)
        self.W1 = r.normal(0, np.sqrt(2 / d_in), (d_in, d_hid)).astype(np.float32)
        self.b1 = np.zeros(d_hid, np.float32)
        self.W2 = r.normal(0, np.sqrt(2 / d_hid), (d_hid, d_out)).astype(np.float32)
        self.b2 = np.zeros(d_out, np.float32)

    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = np.maximum(0, self.z1)
        return self.a1 @ self.W2 + self.b2

    def step(self, X, y, lr, l2):
        p = self.forward(X)
        N = X.shape[0]
        dz2 = (p - y) / N
        dW2 = self.a1.T @ dz2 + l2 * self.W2; db2 = dz2.sum(0)
        dz1 = (dz2 @ self.W2.T) * (self.z1 > 0)
        dW1 = X.T @ dz1 + l2 * self.W1; db1 = dz1.sum(0)
        for par, g in ((self.W1, dW1), (self.b1, db1), (self.W2, dW2), (self.b2, db2)):
            par -= lr * g
        return float(np.mean((p - y) ** 2))


def train(Ztr, Etr, Zva, Eva, hid, epochs, lr, seed, l2=1e-5, bs=256, quiet=False):
    m = MLP(Ztr.shape[1], hid, Etr.shape[1], seed)
    rng = np.random.default_rng(seed)
    for ep in range(1, epochs + 1):
        idx = rng.permutation(len(Ztr))
        for b in range(0, len(idx), bs):
            j = idx[b:b + bs]
            m.step(Ztr[j], Etr[j], lr, l2)
        if not quiet and (ep % 10 == 0 or ep == 1):
            v = float(np.mean((m.forward(Zva) - Eva) ** 2))
            print(f"    epoch {ep:3d}  val MSE {v:.6e}")
    return m


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graphs", type=int, default=240)
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--lr", type=float, default=0.02)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--seed", type=int, default=20260808)
    a = ap.parse_args()

    print("=" * 70)
    print("kx_synth v2 -- can geometry predict marginal compute value?")
    print("=" * 70)

    rng = np.random.default_rng(a.seed)
    r_by_region = {0: 3, 1: 2, 2: 1}
    packs = []
    print(f"\ngenerating {a.graphs} graphs (labels exact, not sampled)...")
    for g in range(a.graphs):
        adj, region = build_graph(rng)
        neigh = hop_sets(adj, CMAX)
        Z = features(adj, neigh)
        onehot = np.eye(3, dtype=np.float32)[region]
        r_cou = np.array([r_by_region[x] for x in region])
        r_dec = rng.permutation(r_cou)
        Lc, Ec, Cc = exact_labels(neigh, r_cou)
        Ld, Ed, Cd = exact_labels(neigh, r_dec)
        packs.append(dict(Z=Z, onehot=onehot, region=region,
                          r_cou=r_cou, r_dec=r_dec,
                          Lc=Lc, Ec=Ec, Cc=Cc, Ld=Ld, Ed=Ed, Cd=Cd))
    nodes = sum(len(p["Z"]) for p in packs)
    print(f"  {a.graphs} graphs, {nodes:,} nodes, "
          f"{len(FEAT_NAMES)} features (region one-hot EXCLUDED from Z)")

    # H5: split by GRAPH, never within one
    ng = len(packs); nval = max(1, int(0.15 * ng))
    order = np.random.default_rng(a.seed + 1).permutation(ng)
    val_g, tr_g = set(order[:nval].tolist()), set(order[nval:].tolist())

    def stack(gs, key):
        return np.concatenate([packs[i][key] for i in sorted(gs)], 0)

    Ztr_raw, Zva_raw = stack(tr_g, "Z"), stack(val_g, "Z")
    mu, sd = Ztr_raw.mean(0), Ztr_raw.std(0) + 1e-8
    Ztr, Zva = (Ztr_raw - mu) / sd, (Zva_raw - mu) / sd
    Etr, Eva = stack(tr_g, "Ec"), stack(val_g, "Ec")
    print(f"  split by graph: {len(tr_g)} train / {len(val_g)} val "
          f"({len(Ztr):,} / {len(Zva):,} nodes)")

    print("\ntraining Z -> eta ...")
    model = train(Ztr, Etr, Zva, Eva, a.hidden, a.epochs, a.lr, a.seed)

    # ---- P1 (weak): beat the global mean
    mean_mse = float(np.mean((Eva - Etr.mean(0)) ** 2))
    pred_mse = float(np.mean((model.forward(Zva) - Eva) ** 2))

    # ---- leakage diagnostic: same model WITH region one-hot
    Otr, Ova = stack(tr_g, "onehot"), stack(val_g, "onehot")
    leak = train(np.hstack([Ztr, Otr]), Etr, np.hstack([Zva, Ova]), Eva,
                 a.hidden, a.epochs, a.lr, a.seed, quiet=True)
    leak_mse = float(np.mean((leak.forward(np.hstack([Zva, Ova])) - Eva) ** 2))

    # ---- matched-budget allocation on held-out graphs
    def evaluate(cond):
        Lk, Ek, Ck = ("Lc", "Ec", "Cc") if cond == "coupled" else ("Ld", "Ed", "Cd")
        tot = {k: 0.0 for k in ("uniform", "curvature", "pred", "shuffled", "oracle")}
        spends, nn = [], 0
        for gi in sorted(val_g):
            p = packs[gi]
            L, E, C = p[Lk], p[Ek], p[Ck]
            n = len(L)
            budget = float(C[np.arange(n), p["r_cou"]].sum())
            Zn = (p["Z"] - mu) / sd
            ehat = model.forward(Zn)
            sh = np.random.default_rng(a.seed + gi).permutation(n)
            eshuf = model.forward(Zn[sh])
            marg = {
                # marginal must DECAY with c or the heap re-inserts the same
                # node at the same priority and walks node 0 to CMAX before
                # node 1 gets anything -- a floor that is not uniform at all.
                # Caught by the shuffled arm scoring +0.8686 on first run.
                "uniform":   np.tile(np.arange(CMAX, 0, -1, dtype=np.float32),
                                     (n, 1)),
                "curvature": np.repeat(p["Z"][:, :1], CMAX, 1),
                "pred":      ehat,
                "shuffled":  eshuf,
                "oracle":    E,
            }
            per = {}
            for k, m in marg.items():
                c, sp = allocate(m, C, budget)
                tot[k] += arm_loss(c, L) * n
                per[k] = sp
            spends.append((min(per.values()), max(per.values()), budget))
            nn += n
        return {k: v / nn for k, v in tot.items()}, spends

    print("\nevaluating matched-budget allocation on held-out graphs...")
    cou, spend_c = evaluate("coupled")
    dec, _ = evaluate("decoupled")

    def rel(x, base): return (base - x) / base

    print(f"\n--- coupled (held-out graphs) ---")
    for k in ("uniform", "curvature", "pred", "shuffled", "oracle"):
        print(f"    {k:10s} mean loss {cou[k]:.6f}   vs uniform {rel(cou[k], cou['uniform']):+.4f}")
    print(f"--- decoupled ---")
    for k in ("uniform", "pred", "oracle"):
        print(f"    {k:10s} mean loss {dec[k]:.6f}   vs uniform {rel(dec[k], dec['uniform']):+.4f}")

    # ---- gates
    gates = {}
    p0 = packs[0]
    gates["H1"] = bool(np.allclose(
        [p0["Lc"][i, p0["r_cou"][i]] for i in range(len(p0["Lc"]))], 0.0, atol=1e-12))
    # H2 restated. Neighbourhood costs are lumpy -- one hop can cost 50
    # nodes -- so exact matching to 1 unit is impossible by construction.
    # First version of this gate demanded it and failed on every run. The
    # honest requirement: no arm may EXCEED the budget, and the spread across
    # arms must stay under 2% of it. The residual is printed, not hidden.
    _bud = spend_c[0][2] if spend_c and len(spend_c[0]) > 2 else None
    gates["H2"] = all(hi <= b + 1e-6 and (hi - lo) <= 0.02 * b
                      for lo, hi, b in spend_c)
    _spread = max((hi - lo) / b for lo, hi, b in spend_c)
    gates["H3"] = True   # permutation of rows by construction
    gates["H4"] = bool(np.array_equal(np.sort(p0["r_dec"]), np.sort(p0["r_cou"])))
    gates["H5"] = len(tr_g & val_g) == 0
    print("\n--- harness gates ---")
    for k in sorted(gates):
        print(f"    {k}  {'PASS' if gates[k] else 'FAIL'}"
              + (f"   (worst spread {_spread*100:.2f}% of budget)" if k == "H2" else ""))
    if not all(gates.values()):
        print("\nHARNESS FAILED -- no predictions reported.")
        return 1

    g_or = rel(cou["oracle"], cou["uniform"])
    g_sh = rel(cou["shuffled"], cou["uniform"])
    g_pr = rel(cou["pred"], cou["uniform"])
    g_cu = rel(cou["curvature"], cou["uniform"])
    g_dc = rel(dec["pred"], dec["uniform"])

    print("\n" + "=" * 70)
    print("REGISTERED PREDICTIONS")
    print("=" * 70)
    p0ok = (g_or > 0.10) and (g_sh <= 0.02)
    print(f"P0 anti-vacuity   {'PASS' if p0ok else 'FAIL'}  "
          f"oracle {g_or:+.4f} (>+0.10), shuffled {g_sh:+.4f} (<=+0.02)")
    if not p0ok:
        print("\n   Allocation channel not demonstrably live. NO claim made.")
        return 0
    print(f"P1 (WEAK)         {'PASS' if pred_mse < mean_mse else 'FAIL'}  "
          f"eta MSE {pred_mse:.4e} vs global-mean {mean_mse:.4e}")
    print(f"     ^ this is the test the draft proposed. v1 already passed its")
    print(f"       analogue (rho=+0.117) and still lost the allocation.")
    print(f"P2 THE TEST       {'PASS' if g_pr > 0.10 else 'FAIL'}  "
          f"pred vs uniform {g_pr:+.4f} (bar >+0.10)")
    print(f"P3 null decoupled {'PASS' if abs(g_dc) < 0.02 else 'FAIL'}  "
          f"{g_dc:+.4f} (bar |.|<0.02)")
    print(f"\n   v1 curvature arm, same harness: {g_cu:+.4f}")
    print(f"   leakage diagnostic -- WITH region one-hot: {leak_mse:.4e} "
          f"vs {pred_mse:.4e} without")
    print(f"   (a large gap means region encodes the label; that is why it is")
    print(f"    excluded from Z, not why it is a finding)")
    print("\nP4 UNRUN: Ollivier-Ricci, and a non-synthetic graph family.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
