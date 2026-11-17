# RMT-IH-001 results, part A (run 2026-11-16)

> **Most important failure (found after both runs, 2026-11-16): these models are not induction heads.** They copy
> only at the trained distance of 32 tokens. Copy accuracy is 1.00 at that offset, but 0.01–0.07 when the same
> repeat is shorter or placed elsewhere, near chance (1/63 ≈ 0.016) (`results/rmt_ih_001/offset_test.txt`). The data
> always put the repeat exactly 32 positions later, and the model has learned position embeddings. It solved the
> task with a fixed-offset positional shortcut, not with content-based induction.
>
> **So read every "induction" below as "copying at a fixed offset".** The registered tests, which time the ICL
> score, are computed correctly. What they time is a different mechanism from the one the question names. A real
> test needs repeats at varying offsets and positions; see part C, unrun, in `RESULTS_B.md`.

**Status:** run as registered at `57eef9d` ([REGISTRATION.md](REGISTRATION.md)). Self-tested.
**Result: P1 FAILED, so P2 and P3 are NOT TESTABLE. P4 FAILED. The lead is killed.** All controls held.

- **Digest:** `81287f73d3362fdde582ed8f90f95246f7369548833c733576b696979be95e44`, over the merged runs of seeds 1–6.
- **Raw output** (in [`results/rmt_ih_001/`](../../results/rmt_ih_001/)):
  - `all_runs.json`: every checkpoint;
  - `analysis.txt`: the frozen script's output;
  - `analysis_gated.txt`: the same, with the registered P1 gate applied;
  - `trajectories.txt`: the raw series, opened before any interpretation.
- **Environment:** torch 2.15.0+cpu on 2 CPU threads. About 160–170 s per run.

## Failures first

1. **P1 FAILED: the edge signal does not reliably fall at this scale.**
   - The mean edge ⟨r̃⟩ change in the repeat arm was **+0.0046**, a rise, where the registration needed a drop of at
     least 0.02.
   - It dropped in only **3 of 6** seeds:

     | Seed | 1 | 2 | 3 | 4 | 5 | 6 |
     |---|---|---|---|---|---|---|
     | Change | −0.0656 | −0.0382 | +0.0103 | −0.0575 | +0.0599 | +0.0637 |

   - **Not tested as a result:** by the registration, P2 and P3 are NOT TESTABLE, because a statistic without a
     consistent direction has no meaningful time.
2. **P4 FAILED: whatever the edge does is not tied to induction.**
   - The no-repeat arm, where induction is impossible, had a mean edge **drop of 0.0398**.
   - That is far more than half of the repeat arm's mean drop, which was −0.0046 (a rise).
3. **Defect in my analysis script.** `analyze.py`, as frozen, did not apply the registration's P1 gate, and printed
   `P2: HELD (edge before induction jump in 5/6 seeds)`.
   - That count is shown, but it does not count as a result. Two of those five "leads" are seeds where the edge
     *rose*.
   - The gate was added after the run, in a dated comment. `analysis_gated.txt` is its output.
4. **Prior work missed by my pre-run search.** Xu (arXiv 2605.24059, 2026) already reports a per-head spectral
   signal that is elevated "at or before" induction-head formation in Pythia 1B. It is not the QK spacing ratio:
   it is the participation ratio of each head's attention *output*. The broader idea of a spectral early warning
   for induction heads was therefore not new.

## Controls

| ID | Result |
|---|---|
| C1/C2 | HELD: the statistic gives the GOE and Poisson reference values within ±0.01 (test) |
| C3 anti-vacuity | HELD: no-repeat final ICL is −0.001, 0.000, −0.001, 0.001, −0.000, −0.000; repeat final ICL is 4.10, 3.95, 4.09, 4.11, 4.11, 4.10 |
| C4 | HELD: QK levels via QR equal the full SVD (test, relative error 3.0e-15 in the smoke check) |
| C5 | HELD: rerunning repeat seed 1 gave identical rows (101 of 101) |

## Per-seed timings, repeat arm (from `analysis.txt`)

| Seed | t_IH | t_edge | t_top | t_srank |
|---|---|---|---|---|
| 1 | 1120 | 300 | 320 | 300 |
| 2 | 1260 | 360 | 320 | 280 |
| 3 | 1260 | None | 320 | 280 |
| 4 | 1040 | 280 | 340 | 300 |
| 5 | 1060 | 100 | 340 | 300 |
| 6 | 1180 | 200 | 320 | 280 |

All three spectral statistics changed around step 300, in **both** arms. That is generic early training, about
800 steps before the induction jump.

## Something not registered: a dip

`top_norm` (the largest QK singular value over the mean) briefly **fell** in every repeat run, by 1.18–2.08 at steps
920–1120. It never fell in a no-repeat run. That was seen only after the run, so it proves nothing here. It is
registered as part B ([REGISTRATION_B.md](REGISTRATION_B.md)) and tested on fresh seeds 7–12.

## Also recorded

My first version of the part B dip test expected the wrong step on a series I had planted myself. The planted
series rises inside the dip, so its first step is the deepest. I corrected the expectation, not the code, before
part B's commit.

## What this does not show

- Nothing about GPT-2 or OPT scale.
- Nothing independent: the design, the code and the grading are all Claude's.
