# PREREG — speedup_gate.py + butterfly operator

**Registered:** before `speedup_gate.py` was written or run.
**Author:** Claude (Opus 4.5). Design is Claude's, not Chad's. This is NOT a
reconstruction of Chad's unpublished "faster maths model" — that design has
never been shown and cannot be reconstructed from its description.
**Status at registration:** Speculative. No number in this file is measured.

---

## What is being tested

The claim class **"my maths is faster"**. Not any specific person's maths —
the *instrument* that adjudicates such a claim, plus one real candidate run
through it as the first target.

**Candidate operator:** a two-factor butterfly / Monarch-style linear map.
For `n = b²`, replace a dense `n x n` matmul with two block-diagonal
transforms separated by a transpose:

```
x (B,n) -> (B,b,b) -> einsum W1 -> transpose(1,2) -> einsum W2 -> (B,n)
```

Multiplies per sample: `2·b³ = 2·n^1.5` versus dense `n²`.
Theoretical ratio: `n² / (2·n^1.5) = √n / 2`.

**Prior art, stated up front, not hidden:** butterfly/Monarch factorizations
are published (Dao et al., *Monarch: Expressive Structured Matrices*, 2022;
and the older Cooley–Tukey/FFT butterfly lineage). Nothing about the operator
is claimed as new. What is claimed as potentially useful is the *measured
crossover on this hardware*, which is not in any paper.

---

## Registered predictions

- **P0 (anti-vacuity, two-sided).** The harness must FAIL a deliberately
  broken candidate at the correctness gate, AND must report no win
  (ratio in [0.80, 1.25]) for a candidate that *is* the dense baseline.
  If either half fails, P1–P4 are VOID and no speed claim is admissible.

- **P1.** The symbolic multiply counter reproduces `√n / 2` exactly at every
  tested `n` (arithmetic check on the instrument itself).

- **P2.** Measured wall-clock speedup at `n = 1024`, batch 64, float32, will
  be **less than half** the theoretical ratio — i.e. **< 8.0x** where theory
  says 16.0x. Rationale: the structured path issues many small BLAS calls and
  cannot reach dense matmul's arithmetic intensity.

- **P3.** There exists a crossover: at least one tested `n` where the
  butterfly path is **slower** than dense in wall clock despite winning on
  op count, and that `n` is **≥ 256**. Falsifiable in both directions — if
  butterfly wins at every size including n=64, P3 is refuted.

- **P4.** Effective throughput (GFLOP/s) of the butterfly path will be
  **below 40%** of the dense path's at `n = 4096`.

- **P5 — LEFT UNRUN (the door).** The identical script on aarch64 / Termux /
  Python 3.14 on the S25 Ultra. Container is x86_64, 1 core, NumPy 2.4.4.
  The crossover `n` is a property of the BLAS and the cache hierarchy, so it
  is expected to move — direction not predicted. No claim about device
  behaviour is admissible until this runs.

## Explicitly NOT claimed

Expressivity. A butterfly cannot represent an arbitrary dense `W`; the
correctness gate here checks that the *fast path computes exactly what its own
dense materialization computes*, which is an implementation claim, not an
approximation-quality claim. Whether a butterfly can replace a given trained
layer without accuracy loss is a separate experiment and is not addressed.

*Vincit Omnia Veritas.*

---

# RESULT — container only (x86_64, 1 core, NumPy 2.4.4, Python 3.12.3)

NOT device-verified. No number here is claimable until P5 runs on the S25.

**Gate proven both directions:** real run exit 0; `--sabotage` exit 1 with
"INSTRUMENT UNTRUSTWORTHY". A0 rel err 1.033e+00 (broken) vs 5.801e-07
(intact) against tol 1e-04. A1 ratio 1.006x.

```
     n   theory  measured   verdict  base GF/s  cand GF/s  cand/base
    64     4.0x     0.33x      LOSS      54.38       4.46      8.2%
   256     8.0x     2.99x       WIN      57.35      21.45     37.4%
  1024    16.0x    14.84x       WIN      60.41      56.01     92.7%
  4096    32.0x    39.99x       WIN      65.13      81.40    125.0%
```

- **P1 CONFIRMED.** Op-count ratio is sqrt(n)/2 exactly at every n.
- **P2 REFUTED (kept).** Registered < 8.0x at n=1024; measured 14.84x.
- **P3 REFUTED (kept).** Registered the crossover at n >= 256; it is at n=64.
- **P4 REFUTED (kept).** Registered < 40% of baseline GF/s at n=4096;
  measured 125.0% — the structured path exceeds dense throughput.
- **P5 UNRUN.** aarch64 / Termux / S25.

**Why three predictions failed:** they all rested on one wrong assumption —
that many small BLAS calls cannot reach dense arithmetic intensity. At
n=4096 the dense weight is 67 MB and each element is reused only `batch`
times; the butterfly weights are 2 MB and stay cache-resident. The structured
path is compute-bound while the dense path is not. Stated as the most likely
mechanism, not as a measured one — it has not been tested.

## UNREGISTERED — not a claim, flagged for follow-up

Batch sensitivity at fixed n and fixed op count:

```
     n  batch   theory  measured
  1024      1    16.0x     7.34x
  1024      8    16.0x    18.65x
  1024     64    16.0x    11.71x
  1024    256    16.0x     9.85x
  4096      1    32.0x    56.58x
  4096      8    32.0x    73.34x
  4096     64    32.0x    38.91x
  4096    256    32.0x    13.46x
```

Run-to-run spread, 10 fresh runs of identical code at n=1024 / batch=64:
14.63 13.56 13.66 14.65 13.56 14.85 14.09 14.51 11.91 14.16
-> min 11.91x, max 14.85x, spread 1.25x, median 14.13x.

**The speedup is not a scalar.** At fixed n and fixed multiply count it moves
5.4x across batch size (13.46x - 73.34x at n=4096) and 1.25x run-to-run at a
single fixed point. Same defect shape as the quasar gate whose verdict was
redrawn every run. Any claim of the form "X times faster" that does not pin
n, batch, dtype and hardware is reporting one sample from a surface.

## New doors

- **P6.** Is the cache-residency mechanism real? Sweep butterfly weight
  footprint against L2/L3 size and look for a knee.
- **P7.** Does the n=64 loss survive on aarch64, where the BLAS and the cache
  hierarchy differ?
- **P8.** Expressivity, untouched here: can a two-factor butterfly approximate
  a trained dense layer within a stated error budget? A speedup on an operator
  that cannot do the job is worth nothing.
