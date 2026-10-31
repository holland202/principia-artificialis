# Note #072 — "X times faster" is one sample from a surface: an instrument for the claim, and a butterfly operator through it

**Status:** Draft — September registration: P1 held; **P2, P3 and P4 REFUTED (kept)**; P5 NOT RUN. Reproduced in
the same direction on 2026-10-31 in 3 of 3 runs plus a sabotage run (SELF-TESTED). Container only; **NOT VALIDATED
on the S25.**
**Theme:** Measurement / Performance claims / Anti-vacuity
**Author:** Claude (Anthropic). The instrument, the registration and the first run were by Claude Opus 4.5 (2026-09-16).
This note and the reproduction are by Claude Opus 5.5 (2026-10-31). Both were done at Chad Edward Holland's
direction. Review level: direction only.
**Builds on:** [[note062_number_audit]] (numbers in prose must come from code). Prior art for the operator: Dao et
al. 2022, *Monarch: Expressive Structured Matrices*, and the Cooley–Tukey/FFT butterfly lineage. Nothing about the operator is claimed as new.
**Method:** [METHOD.md](../METHOD.md) at commit `7a08e0a`.
**Tool:** [`scripts/speedup_gate.py`](../scripts/speedup_gate.py). It is not named `note072_reference.py`, so CI does not run it on every push. The reason is under Triggered controls (C-NOISE).

## What broke (read first)

- **Three of four registered predictions were wrong, in September and again on 2026-10-31.** They all rested on one
  assumption: that a structured operator built from many small BLAS calls cannot reach a dense matmul's arithmetic
  intensity. It can.

  | Prediction (Sept registration) | September run | 2026-10-31 runs |
  |---|---|---|
  | P2 n=1024 speedup < 8.0x | 14.84x | 11.70x, 12.14x, 11.59x |
  | P3 crossover at n ≥ 256 | at n=64 | at n=64 (all three) |
  | P4 n=4096 candidate GF/s < 40% of dense | 125.0% | 132.3%, 123.5%, 128.6% |

- **The proposed mechanism is not measured.** The September record suggests the 67 MB dense weight at n=4096 misses cache while the 2 MB butterfly weights stay resident. That is offered as the likeliest explanation and has not been tested; it is P6 below.
- **The September registration cannot be dated from git.** It and the tool sat in Chad's Google Drive (dated 2026-09-16) and are committed here byte-for-byte, after the fact. "Registered before the script was written" is the author's statement, nothing more (C-EXPLORE).
- **The 2026-10-31 reproduction is not blind either.** A container run during a Drive survey came first. The reproduction registration ([REPRO_PREREG](../experiments/speedup_gate/REPRO_PREREG_2026-10-31.md)) says so.

## The claim

A claim of the form "my maths is faster" can be checked mechanically, by three gates in order:

1. **Correctness:** the fast path equals its own dense materialization on adversarial inputs.
2. **Operation count:** symbolic multiplies, candidate against baseline.
3. **Wall clock:** matched dtype, warmed, best of 7, with effective GFLOP/s.

Two anti-vacuity controls run first, and the instrument refuses to report speed unless both pass:

- **A0:** a silently broken candidate must fail gate 1.
- **A1:** the baseline submitted as a candidate must show no win, a ratio in [0.80, 1.25].

A candidate that **loses** is a result, not a build failure, and exits 0. Only a failed control exits 1.

The precise, refutable form of the "surface" claim below: at fixed n and fixed multiply count, the measured speedup is **not**
a constant of the operator. It depends on batch size, the run, and the machine.

## Epistemic status (read first)

| Kind of statement | Status |
|---|---|
| Mathematics: 2·n^1.5 against n² multiplies, a ratio of √n/2 | Exact |
| Implementation: the fast path equals its own materialization (rel. error 5.801e-07 against tolerance 1e-04) | Shown on these inputs |
| Empirical, x86_64 containers only: speedups, crossovers, GF/s | Two machines on two dates, one container each time |
| Device | Nothing here is an S25 result |

Expressivity is explicitly not claimed. A butterfly cannot represent an arbitrary dense matrix.

## The experiment

Registered predictions (verbatim in [PREREG_2026-09-16_original.md](../experiments/speedup_gate/PREREG_2026-09-16_original.md)):
P0 (both controls), P1 (op-count ratio exactly √n/2), P2–P4 (above), P5 (S25, left unrun).

**Anti-vacuity.**
- **A0:** the broken candidate is rejected at relative error 1.033e+00, while the intact one passes at 5.801e-07.
- **A1:** the baseline-as-candidate ratio was 1.001x, 0.975x and 0.990x across the three runs.
- **`--sabotage`:** it feeds an intact candidate where the broken one belongs. A0 then reports FAIL, the run prints "INSTRUMENT UNTRUSTWORTHY" and exits 1, so the bad exit code is reachable ([run_2026-10-31_sabotage.txt](../experiments/speedup_gate/run_2026-10-31_sabotage.txt)).

**2026-10-31, run 1** (verbatim, [run_2026-10-31_1.txt](../experiments/speedup_gate/run_2026-10-31_1.txt); x86_64, Python 3.13.18, NumPy 2.5.3):

```
     n   theory  measured   verdict  base GF/s  cand GF/s  cand/base
    64     4.0x     0.25x      LOSS      37.34       2.31      6.2%
   256     8.0x     2.39x       WIN      41.63      12.44     29.9%
  1024    16.0x    11.70x       WIN      46.45      33.97     73.1%
  4096    32.0x    42.32x       WIN      42.94      56.78    132.3%
  P1 op-count ratio == sqrt(n)/2 exactly            : CONFIRMED
  P2 n=1024 measured < 8.0x (theory 16.0x)          : REFUTED   measured 11.70x
  P3 a crossover exists and sits at n >= 256        : REFUTED   losses at n=64
  P4 n=4096 candidate GF/s < 40% of baseline        : REFUTED   measured 132.3%
```

**What the failure taught.** The speedup at n=1024 was 14.84x on the September container and 11.59x–12.14x on today's. The September record also logged, unregistered, a 5.4x swing across batch sizes at n=4096 (13.46x to 73.34x). Taken together, a single "X times faster" number is one point on a surface over n, batch, dtype, BLAS and hardware. It is only reportable with all of those pinned. This is the same failure shape as a gate whose verdict is redrawn every run.

## Triggered controls (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | no — no real data; the inputs are generated |
| Noise | C-NOISE | **yes** — wall-clock timing. Measured: 3 runs of identical code today, plus September's 10-run spread at one point (11.91x to 14.85x). Because A1 is a timing ratio, the tool is kept out of CI's per-push reference-script loop, which requires deterministic verdicts (M5). |
| Statistics | C-STAT | **yes**. Speedups are best-of-7 timings from 3 runs. No interval is claimed, and the verdicts are the registered thresholds only. |
| Evidence | C-EVID | no — no evidence-handling rule is under test |
| Independence | C-INDEP | **yes, and not met.** Both runs are Claude's, in containers. This is not independent replication. |
| External | C-EXT | **yes** — the Monarch paper is cited as prior art, and the operator is not claimed as new |
| Device | C-DEVICE | **yes** — every number is x86_64 container only; the S25 is P5, not run |
| Verdict code | C-BUILD | **yes** — the tool returns a verdict. It fails closed: exit 1 on a failed control, exit 2 if it cannot run, and the sabotage run shows exit 1 is reachable. |
| Exploration | C-EXPLORE | **yes** — neither registration is shown in git to precede its run; disclosed above |
| Method comparison | C-METHCOMP | **yes** — structured against dense. Both are given the same dtype, batch and warm-up, and each is timed best-of-7. |
| People's data | C-PRIVATE | no |
| Design | C-DESIGN | **yes** — the mechanism (cache residency) is a causal story and is labeled unmeasured; claims stay at "this code, these inputs, this machine" |
| Held-out | C-HOLDOUT | no — nothing was tuned on these runs |
| Generated inputs | C-SYNTH | **yes** — the adversarial inputs are generated: normal, wide range, alternating, zeros, one-hot. They are listed in the tool. |

## Falsifiable next predictions (M15)

- **P5 (the door).** The same script on the S25 under Termux. Where the crossover falls there is not predicted.
- **P6.** Cache residency: sweep the butterfly weight footprint against L2/L3 size and look for a knee.
- **P7.** Does the n=64 loss survive on aarch64?
- **P8.** Expressivity: can a two-factor butterfly approximate a trained dense layer within a stated error budget? A speedup on an operator that cannot do the job is worth nothing.
