# TINY-ENGINE-003 registration: copying strings with repeated symbols

**Status:** REGISTERED, NOT RUN on seeds 11–16. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-20). Design and code: Claude (Anthropic, Opus 5.5). Human review level:
direction only.

## Why

TINY-ENGINE-002 ([RESULTS_002.md](RESULTS_002.md)) fixed long copying for strings of **distinct** symbols. Two weak
spots remain:

- **Repeated symbols were never trained or tested.** Version 2's second layer matches on content only. When a symbol
  occurs several times in the string, "where did I see this before?" has several answers. Codex (OpenAI) raised this in
  its review (item 3) and in the V2-CHECK plan on branch `review/tiny-engine-v2-check-20261117`.
- **Free-running 127-token copies are exactly right in only 58–85% of tries** (version 2, `freerun_v1_v2.txt`).

Both Claude's RESULTS_002 "Next" list and Codex's V2-CHECK name the same next door: a separately registered training
change with fresh seeds and untouched evaluation cases. This is that change.

**Not overlapping V2-CHECK.** V2-CHECK evaluates the *released* v1 and v2 weights. This run trains new models on new
seeds and never loads the released weights. V2-CHECK is ChatGPT's to run and is left untouched.

## The change (frozen at this commit: `engine.CFG3`)

- **Arm B (`CFG3`)** is `CFG2` with half of the copy examples drawn by `task_copy_rep`: each string draws, with
  replacement, from an alphabet of a random size from 2 to 127 symbols. The other half stay distinct-symbol.
- **Arm A (`CFG2`)** is version 2 unchanged. It is the simplest rival (M14), trained on the same seeds.
- **Same model:** 165,120 parameters, same steps, same optimiser, same lengths.
- **Same behaviour for old configs:** with `copy_rep_frac` absent, `make_batch` draws no extra random numbers. Checked
  by training `CFG` and `CFG2` for 40 steps with the old and the new `engine.py`: identical weights.

## Exploration (C-EXPLORE: seen before registering)

One seed per arm, seeds 901 and 902 (so the two arms also differ by seed), with case seeds in the 5000–7300 range.
Predictions were written down before the run in `results/tiny_engine/003/exploration/PREMORTEM.md`.

| Score | Arm A (seed 901) | Arm B (seed 902) | Untrained |
|---|---|---|---|
| Teacher-forced copy, 8-symbol alphabet, 63 tokens | 0.6886 | 0.8442 | 0.0075 |
| Teacher-forced copy, 8-symbol alphabet, 127 tokens | 0.4937 | 0.6584 | 0.0073 |
| Teacher-forced copy, 32-symbol alphabet, 127 tokens | 0.8959 | 0.9701 | 0.0085 |
| Teacher-forced copy, distinct, 127 tokens | 0.9974 | 0.9996 | 0.0088 |
| **Free-running whole copy exactly right, distinct, 127 tokens** | **0.67** | **0.94** | 0.00 |
| Free-running whole copy exactly right, 8-symbol, 63 tokens | 0.00 | 0.00 | 0.00 |
| Held-out periods, 1,024 tokens | 0.9987 | 0.9961 | 0.008 |
| Recall, 1,024 tokens | 1.0000 | 1.0000 | 0.0079 |

- **My first prediction was wrong.** I predicted arm A would score below 0.50 on 8-symbol copies at 63 tokens. It
  scored 0.6886, so content-only matching handles repeats better than I expected.
- **The free-running gain is the surprise**, and with one seed per arm it may be seed luck. Version 2's six released
  seeds ranged 0.58–0.85 on a similar test.

## Registered predictions (paired seeds 11–16; each holds if true in ≥ 5 of 6 seeds)

| ID | Prediction | Exploration |
|---|---|---|
| P1 | Arm B beats arm A on teacher-forced 8-symbol copies at 63 tokens (strictly greater) | 0.8442 vs 0.6886 |
| P2 | Arm B beats arm A on free-running whole distinct copies at 127 tokens (strictly greater) | 0.94 vs 0.67 |
| P3 | Arm B still meets the full version 2 bar: Q1–Q3 ≥ 0.95 at 128, 256, 512; Q4 ≥ 0.90 at 1,024 | met |
| P4 | **A limit, registered so it can be wrong:** arm B stays below 0.90 on teacher-forced 8-symbol copies at 127 tokens | 0.6584 |
| P5 | Anti-vacuity: an untrained model (torch seed 991) scores below 0.05 on every new test | 0.0073–0.0088 |

- **P5 is already checked** by `test_eval3.py`, together with the instrument's other direction: an exact-copy oracle
  scores 1.0 and an off-by-one oracle scores below 0.5 (teacher-forced) and 0.0 (free-running).
- **Verdict code:** `score3.py`, through `guard.py`. It refuses any result set that is not exactly seeds 11–16 in each
  arm with the right config. Three deliberate mutants (flipped comparison, alphabet ignored, target compared with
  itself) each fail a test.
- **Descriptive only:** free-running 32-symbol and 8-symbol copies at 63 tokens, and every other score. No threshold.

## Cases and counts (C-FEAS)

- 12 training runs (2 arms × 6 seeds), about 10 minutes each on one CPU thread.
- Per model: 6 teacher-forced cells × 256 cases, 3 free-running cells × 100 cases, plus the version 2 evaluation.
- Evaluation case seeds 8000–8503 (`eval3.py`), not used by any earlier run or by the exploration.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Yes: counts above. |
| Noise | Yes: version 2 retraining was byte-identical (`results/002/determinism.txt`); evaluation is greedy and deterministic. Not re-measured here. |
| Statistics | No population claim: integer seed counts against a pre-set 5-of-6 rule, no p-values. |
| Evidence | Yes: fail-closed loader; malformed or duplicated result sets give exit 2 and no verdict. |
| Independence | No: Claude designed, ran and grades this. SELF-TESTED. Codex's V2-CHECK is a separate, independent plan. |
| External | Prior work below is context, not evidence. |
| Device | Linux container CPU only. S25 NOT VALIDATED. |
| Verdict code | Yes: `score3.py`, mutants above. |
| Exploration | Yes: disclosed above, seeds 901–902, not reused. |
| Held-out | Yes: confirmation uses fresh training seeds and fresh case seeds. |
| Generated inputs | Yes: `test_eval3.py` checks each family's layout, mask and repeat counts. AI inspection only. |
| People's data | No: synthetic tokens. |
| Design | Paired two-arm training intervention; supports "the training change raises these scores on these cases", not a mechanism. |

## Prior work

- Copying by content matching struggles when tokens repeat: Jelassi et al., "Repeat After Me: Transformers are Better
  than State Space Models at Copying" (ICML 2024), describe copying as n-gram matching and its limits.
- The hybrid position design is from Yang et al., arXiv 2501.18795.
- Nothing here is a new mechanism. The question is whether one cheap data change helps a 165K-parameter model.

## Unrun door

- If P4 holds, a 2-layer, 2-head model has a capacity limit on repeated symbols. The next test is a third layer, or an
  exact-copy tool for agent use with neural copying measured separately.
- Phone measurement on the S25: cached generation, latency, memory.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, coded and wrote this → human validation: not performed →
human editing/curation: direction by Chad Holland, 2026-11-20 → human responsibility: Chad Holland. Review level:
direction only.*
