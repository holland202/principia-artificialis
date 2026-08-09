# 053 — Soft-HyperDGA: a differentiable relaxation, and the reference it beat

**Status:** Draft, verified reference code — ⚠ P1 refuted, kept
**Reference code:** `scripts/note053_reference.py`
**Result scope:** DEVICE-VERIFIED on Samsung Galaxy S25 Ultra (Termux, aarch64), 2026-08-08. Bit-identical to two prior x86_64 container runs.
**Credit:** Chad Edward Holland. Implementation and review with Claude (Anthropic).
**Related:** [[note054_kx_allocation]] · [[note055_kx_marginal_utility]]

---

## What failed

**P1 refuted.** As τ falls the soft score does not converge to the hard one.

```
hard (grid Delaunay) = 0.8696
  tau=0.5   soft=0.6609
  tau=0.2   soft=0.7943
  tau=0.08  soft=0.8686
  tau=0.03  soft=0.9063
  tau=0.01  soft=0.9312
|soft(0.01) - hard| = 0.0617     bar was 0.05
```

Note τ=0.08 lands at 0.8686, within 0.001 of hard, and then the sequence keeps
climbing past it. This is not slow convergence to the wrong place — it crosses
and leaves.

**Diagnosis, kept, not repaired.** The relaxation weights each edge by shared
facet *mass*, not by an indicator. It therefore converges to an area-weighted
alignment ratio, not to the integer edge ratio HyperDGA defines. That is a
defensible quantity. It is not the registered one, so P1 stands refuted.

Repairing it would mean normalising each facet's mass to unity as τ→0, which
re-introduces the discontinuity the whole exercise exists to remove. The
failure is structural, not a tuning miss.

## What held

```
P0 anti-vacuity  hard score EXACTLY unchanged in 90% of 30 perturbations
                 soft score measurably moved in 100%          PASS
P2 usefulness    Spearman(separation, soft) = 1.0000          PASS
P3 gradient      |grad soft| = 0.05554   |grad hard| = 0.00000 exactly   PASS
```

P0 matters most. It establishes that the discontinuity is real *in this
setup* before anything is claimed about fixing it. Had the hard score also
moved under perturbation, there would be no problem here to solve and no
claim would have been made in either direction.

## The problem, in the authors' words

Medbouhi, Marchetti, Polianskii, Kravberg, Poklukar, Varava, Kragic —
*Hyperbolic Delaunay Geometric Alignment*, arXiv:2404.08608 (KTH). Their
Section 6 names the gap: the score takes values in the rationals, is therefore
discontinuous and non-differentiable, and a continuous differentiable version
is called a promising line for future research.

HyperDGA(A,B) = 1 − |Ẽ|/|E| over heterogeneous Delaunay edges. Integer counts,
so the gradient is zero almost everywhere and undefined at the flips.

**The relaxation.** A Delaunay edge exists exactly when two Voronoi cells share
a facet, and facet measure goes continuously to zero exactly where the edge is
about to flip. So replace the indicator with shared-boundary mass:

    p_i(x) = softmax( −d_H(x, site_i)² / τ )
    w_ij   = Σ_x p_i(x) p_j(x)
    soft   = 1 − Σ_{i∈A, j∈B} w_ij / Σ_{i<j} w_ij

**Prior art, stated up front.** Weighting by Voronoi cell overlap is the
machinery behind natural-neighbour (Sibson / Laplace) coordinates, known to be
smooth away from the sites. Nothing here invents that. The possibly-new part is
the hyperbolic (Klein) port.

**Limitation, stated up front.** The Voronoi diagram is computed by sampling
the Klein disk on a 25,132-point grid, not by the exact power-diagram
construction of their Theorem 1. Every statement here is about that
approximation. n=2 only.

## The observation that is not a claim

The grid-hard reference is **non-monotonic** across the separation sweep:

```
sep=0.36  soft=0.9311  hard=0.8667
sep=0.44  soft=0.9428  hard=0.8605   <- drops
sep=0.52  soft=0.9500  hard=0.8837
sep=0.60  soft=0.9540  hard=0.8810   <- drops
```

Soft rises at every step. Hard falls twice while the clusters are being pulled
further apart, which the score is supposed to track monotonically.

This is flagged as an observation, not registered and not claimed. But it
raises the possibility that the grid approximation is the broken component
rather than the relaxation — in which case P1 measured the relaxation against a
faulty reference, and the 0.0617 gap is partly the reference's.

## Open

**P4, unrun deliberately.** Recompute the hard reference by exact combinatorial
Delaunay via the paper's Theorem 1 power-diagram route, and re-measure the P1
gap against it. If the gap closes, P1 failed against a bad reference. If it
holds, the mass-weighting diagnosis above is the whole story. Nothing in this
note distinguishes those two, and it should not pretend to.

## Reproduce

```bash
python3 scripts/note053_reference.py
```

Pure NumPy. Runs on a phone. Every number above is pasted from its output.
