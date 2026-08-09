# 055 — Geometry predicts marginal compute value. Allocating on it still loses.

**Status:** Draft, verified reference code — ⚠ P2 and P3 refuted, kept
**Reference code:** `scripts/note055_reference.py`
**Result scope:** DEVICE-VERIFIED on Samsung Galaxy S25 Ultra (Termux, aarch64), 2026-08-08. Bit-identical to two prior x86_64 container runs.
**Credit:** Chad Edward Holland. Implementation with Claude (Anthropic). The
η reframing is from an AI-authored critique of [[note054_kx_allocation]] which
posed it in a box and did not run it.
**Related:** [[note054_kx_allocation]] · [[note053_soft_hyperdga]]

---

## What failed

Two registered predictions, at two data scales.

```
                        40 graphs / 20ep     240 graphs / 40ep
P1 (WEAK)   eta MSE     2.5364e-03           3.3953e-04
            global-mean 2.8681e-03           3.5041e-03
            ratio       1.13x better         10.3x better       PASS  PASS
P2 THE TEST pred vs uniform  -0.2806              -0.2932        FAIL  FAIL
P3 null decoupled            -0.2220              -0.2086        FAIL  FAIL
```

**The finding is the divergence between those two rows.** Six times the data
made the predictor an order of magnitude better at predicting η. It moved the
allocation result by 0.0126 — in the wrong direction. Prediction quality and
allocation value are not the same axis, and the gap is not a data-starvation
problem.

**P1 is the test a draft proposal wanted to publish on.** `val_mse /
uniform_mse < 1.0`, read as "geometry beats uniform." It passes. P2 runs the
same trained model as an actual allocator at matched budget and it comes in
29% worse than spreading compute evenly. Both numbers, same model, same run.

**P3 refuted, and the registered bar was the wrong shape** — the same error as
[[note054_kx_allocation]]'s P3, made again after being diagnosed once. I
predicted the predictor would go neutral when the geometry↔task correlation
is destroyed. It goes to −0.2086. A misallocating arm is harmful in both
conditions, never neutral in one. Registering "≈ 0" for an arm that can only
be ≤ 0 was a bad prediction twice.

## What held

```
P0 anti-vacuity  oracle  +1.0000  (loss exactly 0.000000)
                 shuffled -2.5095  (does not beat uniform)     PASS
H1  L_i(r*) == 0 exactly for every node                        PASS
H2  no arm exceeds budget; worst spread 0.11%                  PASS
H5  train/val split by GRAPH, never within one                 PASS
```

The channel is live and worth +100%: with true η, greedy allocation recovers
the exact required radius at the same budget, loss exactly zero. Shuffled-Z is
2.5× worse than uniform. So there is a right answer, something could have
found it, and the comparison is not confounded.

Continuity with v1: the raw Forman-Ricci arm scores **−23.8158** in this
harness. The η reframing was an enormous improvement — from catastrophic to
merely losing.

## Two defects in the proposed design, fixed before running

**1. The baseline was the wrong one.** The draft compared η-MSE against
predicting the *global mean* of η. That is an R² > 0 test. [[note054_kx_allocation]]
already passed its analogue (ρ = +0.117) and still lost the allocation. Here
the mean-baseline is kept as P1 and labelled WEAK precisely so the two can be
read side by side — and they diverge, which is the note.

**2. Region one-hot was in the feature set.** The labels are generated from
region structure, so feeding region one-hot to the model hands over the answer;
feature importance would then rank region first and read as a discovery. Same
class as the F22 leakage. Excluded from Z, retained as a diagnostic only.
Measured cost of excluding it: 2.93e-04 with vs 3.40e-04 without. Mild — the
structural features already carry most of what region encodes.

## Design

Ω: 240 randomized graphs, ~240 nodes each, three stitched regions (grid /
binary tree / clique-chain). G: permutation.

**Ground truth is exact, not sampled.** Signals are iid N(0,1), so for
neighbourhoods A and B, L = 1/|A| + 1/|B| − 2|A∩B|/(|A||B|) in closed form. No
Monte Carlo, no seed sensitivity in the labels, and L_i(r*) = 0 exactly.

    eta_i(c) = [ L_i(c) - L_i(c+1) ] / [ C_i(c+1) - C_i(c) ]

**One allocator, five marginal estimates.** Every arm runs through the same
greedy marginal-value allocator at the same budget, differing only in the
marginal value it believes: uniform (round-robin), curvature (v1's signal),
pred (η̂ from a 9-feature MLP), shuffled (η̂ from row-shuffled Z), oracle (true
η). Using different allocators per arm would compare score quality and
allocator quality at once.

## Harness defects found and kept

**The uniform arm was not uniform.** A constant marginal makes the priority
queue re-insert the same node at unchanged priority, so it walks node 0 to the
ceiling before node 1 gets anything. Uniform scored 0.509690 as a "floor" that
every arm beat, including shuffled at +0.8686 — which is what exposed it.
Fixed to decay with c. Uniform then scores 0.020527 and everything loses to it.
**A second independent implementation hit this identical defect the same
week**, which is the strongest evidence available that it is a natural trap
rather than one person's slip.

**H2 was unsatisfiable as registered.** It demanded all arms spend within 1
unit of budget, but one hop can cost 50 nodes, so exact matching is impossible
by construction. Restated: no arm may exceed budget, spread under 2%. Worst
observed 0.11%. The original gate failed every run until restated.

## Open

**P4, unrun.** Ollivier-Ricci in place of Forman-Ricci, and a non-synthetic
graph family. Forman as used here is `4 − deg(u) − deg(v)`, a degree
expression — so "curvature failed" and "a degree proxy failed" are still not
distinguished. That was v1's open question and this note does not close it.

## Reproduce

```bash
python3 scripts/note055_reference.py --graphs 240 --epochs 40
```

Pure NumPy. Every number above is pasted from its output.
