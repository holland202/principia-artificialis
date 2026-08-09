# 056 — The reasoning-curvature estimator reports 54 million where the answer is zero

**Status:** Draft, verified reference code — ⚠ P3 refuted, kept
**Reference code:** `scripts/note056_reference.py`
**Result scope:** DEVICE-VERIFIED on Samsung Galaxy S25 Ultra (Termux, aarch64), 2026-08-09. Bit-identical to the container run.
**Credit:** Chad Edward Holland. Note #032 by Perplexity. Implementation and defect analysis with Claude (Anthropic).
**Related:** [[032_curvature_of_reasoning]] · [[note054_kx_allocation]] · [[note055_kx_marginal_utility]]

---

## What this is

[[032_curvature_of_reasoning]] proposes reasoning curvature as a measurable
quantity: a trajectory on a statistical manifold, straight where inference is
efficient, curved where the model corrects itself. Its *definition* is right —
κ(t) = √(g(a,a)) with a the covariant acceleration. Its Experiment 2 then
proposes to compute that on transformer hidden states as

    kappa_t ~ |Delta^2 h_t| / |Delta h_t|^3

and that is a different quantity. This note tests whether the proposed
estimator can return zero when the answer is zero. It cannot, for two separate
reasons, and both are measured rather than argued.

The manifold is chosen so the answer is known: the 1-D Gaussian family with the
Fisher–Rao metric, which is the hyperbolic plane at constant curvature −1/2.
Its geodesics are semicircles centred on the μ-axis in (μ, σ√2), so an exact
zero-curvature trajectory is available in closed form.

## What failed

**P3 refuted.** The note's premise is that curvature ranks trajectory quality —
straight means efficient, curved means confused. It does not survive contact
with noise:

```
geodesic                K =        0.009069
perturbed               K =    10828.687460
meandering              K =     2984.870157
```

A trajectory with small-amplitude jitter scores **3.6× higher than one that
deliberately meanders**. Because κ goes as 1/|v|², noise makes tiny erratic
steps and those dominate the integral. Integrated curvature measures step-scale
noise, not trajectory shape. That is a direct obstacle to hypotheses 1–4 of
[[032_curvature_of_reasoning]], all of which assume K tracks reasoning quality.

## The two defects, confirmed

**P1 — no tangential projection.** |Δ²h| contains change in *speed* as well as
change in *direction*. A perfectly straight Euclidean line walked with varying
step size has exactly zero turning, and the proposed estimator reports:

```
naive        K = 54477471.3683
projected    K = 2.04e-12
```

**P2 — no metric.** The formula is ambient Euclidean; it carries no g and no
Christoffel symbols. On an exact Fisher–Rao geodesic, true curvature zero:

```
naive        K = 3412.3060
covariant    K = 0.009069
```

Either defect alone makes the instrument unable to return null.

## What held

```
gates   covariant K ~ 0 on an exact geodesic                    PASS
        covariant K clearly nonzero on a curved path            PASS
        speed-invariant (relative)          0.139 < 0.50        PASS
        geodesic reads as null vs curved    < 1% of curved      PASS

P4      shuffling point order changes K by 47471.9%             PASS
```

P4 matters more than it looks. A measure of *reasoning* must depend on the
order of the sequence; if shuffling left K alone, K would be a property of the
point cloud rather than of the path through it.

## Harness defects, all three kept

The gate suppressed the report three times, and each time there was something
real behind it.

**(1) Uniform central differences aren't reparametrization-invariant.** The
same exact geodesic walked at uneven speed scored 0.091582 against 0.004134
walked evenly — 22×, on a curve whose true curvature is zero either way. I had
removed the tangential component and left the parametrization assumption
standing, which is the same class of error I was testing #032 for.

**(2) The first fix made it worse.** Resampling to uniform arc length by linear
interpolation took the geodesic from 0.004134 to **2.500873** — chording a
curved path injects exactly the curvature being measured. Interpolation is not
a neutral operation on a manifold. Fixed properly with non-uniform finite
differences against Riemannian arc length, leaving the points where they are.

**(3) The gate itself was wrong.** As registered it demanded an absolute
K < 1e-2 on the unevenly-walked geodesic. Both parametrizations carry
irreducible O(h²) discretization error, so an absolute bar tests the step size,
not the invariance. Restated as a relative test plus a signal-to-null ratio.
The original is kept in the file.

## Observation, not a claim

A constant-σ horizontal line scores K = 83.4386 under the covariant estimator.
That is correct, not a defect: a horizontal line in (μ,σ) is not a Fisher–Rao
geodesic. Ambient straightness and manifold straightness are different
properties — which is defect P2 stated positively.

## What this does not do

It does not test whether curvature predicts accuracy, calibration, or
hallucination. Those are hypotheses 1–4 of [[032_curvature_of_reasoning]] and
all four remain entirely unrun. What is settled here is narrower and prior:
whether the proposed instrument can return zero when the answer is zero.

## Open

**P5, unrun deliberately.** Real transformer hidden states — and first, what
metric g even *is* for them. The Fisher–Rao metric that makes this work is a
property of a parametrized probability family; an arbitrary latent space does
not come with one. Without a metric, only the ambient version is available, and
P2 shows what that reports. `scripts/note056_reference.py --embeddings <file>`
accepts a (T, D) array and prints the naive figure as a diagnostic, clearly
labelled as not P5.

## Reproduce

```bash
python3 scripts/note056_reference.py
```

Pure NumPy plus `scripts/prereg.py`. Every number above is pasted from its
output.
