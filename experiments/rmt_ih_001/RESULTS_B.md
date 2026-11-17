# RMT-IH-001 results, part B: the top singular value dips as the model learns to copy (run 2026-11-16)

> **Most important failure (found after both runs, 2026-11-16): these models are not induction heads.** They copy
> only at the trained distance of 32 tokens. Copy accuracy is 1.00 at that offset, but 0.01–0.07 when the same
> repeat is shorter or placed elsewhere, near chance (1/63 ≈ 0.016) (`results/rmt_ih_001/offset_test.txt`). The data
> always put the repeat exactly 32 positions later, and the model has learned position embeddings. It solved the
> task with a fixed-offset positional shortcut, not with content-based induction.
>
> **So read every "induction" below as "copying at a fixed offset".** The registered tests, which time the ICL
> score, are computed correctly. What they time is a different mechanism from the one the question names. A real
> test needs repeats at varying offsets and positions; see part C, unrun, in `RESULTS_B.md`.

**Status:** run as registered at `2702574` ([REGISTRATION_B.md](REGISTRATION_B.md)), on fresh seeds 7–12. Self-tested.
**P6a HELD, P6b HELD, P6c FAILED.**

- **Digest:** `9bd3d951f38adadf32a4051146d1d0484b4fbe72e07084dcd2cc9de5719cfb88`.
- **Raw output** (in [`results/rmt_ih_001/`](../../results/rmt_ih_001/)):
  - `partB_runs.json`;
  - `partB_analysis.txt`;
  - `partB_trajectories.txt`, opened before interpretation.

## Failures first

**P6c FAILED: the dip is not an early warning.**

- **The registered measure:** the dip's deepest point came before the onset of copying (the 10% point of the ICL
  score) in only **1 of 6** seeds.
- **Timing:** in 4 seeds the deepest point fell on the same checkpoint as the onset, and in 1 seed it came 20
  steps after.
- **Interpretation, as registered in advance:** the dip marks the transition as it starts. It does not predict it.

## What held

| Seed | Dip size | Dip step | ICL 10% point | ICL 50% point |
|---|---|---|---|---|
| 7 | 1.124 | 780 | 760 | 900 |
| 8 | 1.380 | 920 | 920 | 1040 |
| 9 | 1.355 | 940 | 960 | 1080 |
| 10 | 1.206 | 860 | 860 | 1000 |
| 11 | 1.526 | 920 | 920 | 1040 |
| 12 | 1.270 | 860 | 860 | 980 |

- **P6a HELD:**
  - in the repeat arm, the dip was at least 0.5 in **6 of 6** seeds (1.124–1.526);
  - in the no-repeat arm, it was under 0.2 in **6 of 6** (0.000 in every seed). There `top_norm` rose
    monotonically.
- **P6b HELD:** the dip came before the 50% point of the jump in **6 of 6** seeds.

**What this supports (strongest claim):** in this tiny attention-only model, a fall of the QK spectrum's
normalised top singular value is a weight-only signature that appears at the onset of learning to copy, and only
when copying is learnable. The copying learned here is a fixed-offset positional shortcut, **not** an induction
head (see the box above). The evidence is 6 confirmatory seeds, plus the 6 exploratory ones that
prompted it. Design: within-model, two arms, registered, self-tested.

## Seen in the raw series, not registered (a door)

**The descent starts before the onset; only the trough lands on it.**

- **Example:** in seed 8, `top_norm` falls steadily from about step 700 (4.86), while the ICL score is still 0.01.
- **Comparison:** its 10% point comes at step 920.
- **Untested prediction (P7):** the *start* of the decline precedes the onset in most seeds.
- **Proper test:** a registered "first sustained fall" rule, applied to fresh seeds 13–18. Not run.

## Part C, unrun: the test this should have been

Repeats at random offsets and positions (for example, segment lengths 8–32 and random start positions), so that only
content-based induction can solve the task. Check, before registering, that the trained models copy at unseen
offsets. Then retest P6a/b/c and P7 on fresh seeds.

## What this does not show

- Nothing about induction heads: these models do not have them.
- Nothing about larger or real-text models. Pythia's public training checkpoints would be the next test.
- Nothing about which heads carry the dip. The registered statistic pools all four heads.
- Nothing independent: the design, the code and the grading are all Claude's.
- Novelty is not established. Activation-based spectral signals around induction-head formation are reported (Xu,
  arXiv 2605.24059). I have not found this weight-based dip in prior work, but my part A search missed Xu, so treat
  that absence with caution.

## Published

The models, metrics, code and model card are on Hugging Face at [holland202/rmt-ih-001](https://huggingface.co/holland202/rmt-ih-001), commit `6f72ebb`. Chad Holland uploaded them from Termux on 2026-11-16, after `sha256sum -c SHA256SUMS` passed for all 32 files on his device. The uploaded `SHA256SUMS` matches the package built here.
