# TLM-006 registration (DRAFT): is seed 41's multi-story copying excess real, with 200 fresh samples per seed?

**Status:** DRAFT, NOT FROZEN, NOTHING BUILT OR RUN. No new sample has been generated and no new reference story read.
Written for ChatGPT's attack before any freeze ([COLLAB_TLM006.md](COLLAB_TLM006.md)). Changes before the freeze are
new commits on this file. The freeze waits for Chad Holland's own words on this line's PR. **Authors:** Direction:
Chad Holland, 2026-11-25. Design: Claude (Anthropic, Opus 5.5). Human review: none. Method: METHOD.md as on this
branch.

## Question

TLM-005 (20 samples per seed, masked windows) found seed 41's multi-story rate r = 0.0405 above the maximum of 10
real-story blocks (0.026), and seed 42's (0.0212) not. **With 200 fresh samples per seed, compared with real-story
blocks of the same size, which seeds still show a multi-story excess?**

- **Simplest rival (M14), sampling noise:** neither seed shows an excess at 200 samples.
- **Claude's expectation, recorded before any sample (not a criterion, M1):** the rival (NEITHER). In TLM-005, 13
  of seed 41's 247 eligible windows were copied, and 10 of those were multi-story. One or two windows move r by about
  0.004 to 0.008.

## Inputs

- **Models:** TLM-004's seeds 41 and 42 (BPE-1024, 989,520 parameters). Their weight files were not committed. Only
  their SHA-256 values are (`results/tiny_lm/004/runs/SHA256SUMS_weights.txt`). They come from one of two sources:
  - **Source A, preferred:** the original `t41.pt` and `t42.pt`, if anyone still has them, accepted only if their
    SHA-256 matches.
  - **Source B:** retrain with `train_tok.py` at TLM-004's exact settings (seeds 41 and 42, 6,250 steps, d 120,
    L 5, h 4, 2 threads). Gates G1 and G2 below decide what the retrained models may claim.
- **Model text:** `gencheck_tok.py`'s generation procedure: prompt "Once upon a time", temperature 0.8, at most 330
  tokens, stop at `<|endoftext|>`. **Generation seeds 5020 to 5219** (200 per model seed). These are disjoint from
  TLM-004's 5000 to 5019, so none of these samples has been seen.
- **Reference:** valid stories 200 to 2,199 of `data/v2_valid.txt` (split on `<|endoftext|>` as in TLM-005), as 10
  blocks of 200. TLM-005 used stories 0 to 199. Those stay out, because they have been seen.
- **Training slice and instrument:** unchanged from TLM-005: the slice SHA-256 `ee5242d9…69e9`. The functions of
  `tlm005_attrib.py` at `66966b7` (SHA-256 `93948c3c…0590`) are **imported, not copied**: the window grid, the masks,
  df with duplicate collapse, and the U, R, B and N classes. ChatGPT's blind controls passed on that code in TLM-005
  (CONTRIBUTOR REPORTED).

## Gates, in order (C-BUILD)

1. **G0, instrument fidelity:** the new driver, on TLM-004's 40 committed samples and on TLM-005's block 1, must
   print TLM-005's lines exactly: `t41: E 247 U 3 R 10 B 0`, `t42: E 236 U 4 R 5 B 0`, `block01: E 338 U 7 R 8 B 0`.
   If not, stop.
2. **G1, same weights (Source B only):** the retrained weights' SHA-256 equals the recorded one.
3. **G2, same generator (Source B, if G1 fails):** generation seeds 5000 to 5019 reproduce
   `t41.samples.txt` and `t42.samples.txt` byte for byte.
4. **Scope rule (revised after ChatGPT note 002).** The scope is decided per model, here, before any run:
   - **TLM-004 MODEL:** Source A with a matching hash, or Source B with G1 holding.
   - **RECIPE REPLICATE, OLD OUTPUTS MATCHED:** G1 fails but G2 holds. Matching 20 old texts does not show the weights
     are the same. Two models can agree on seeds 5000 to 5019 and still differ at 5020.
   - **RECIPE REPLICATE:** G1 and G2 both fail. The run continues on the retrained models.
5. **G3, counts:** the valid file must hold at least 2,600 stories (counted and printed first). Any missing count
   gives INCONCLUSIVE.

## Measures (per model seed, and per reference block)

The measures are as in TLM-005, on masked windows. E is the number of eligible windows. u = U/E (single-story),
r = R/E (multi-story), b = B/E, and the masked copy rate is u + r + b. The share of texts with a longest match of
200 bytes or more is also reported. **Primary:** rates pooled over all texts of the set, i.e. the sum of counts
divided by the sum of E. Pooling weights each text by its eligible windows (ChatGPT note 002).

**Frozen sensitivity analyses** (reported, not part of the verdict; any disagreement with the primary is named in the
results):
- **S1, matched length:** each reference story is encoded with `tok1024.json`, cut at the model's cap of 330 tokens,
  decoded, and masked exactly as model text is. Then the same rule as the primary is applied.
- **S2, per-text mean:** the mean of each text's r (texts with E = 0 excluded and counted), with the same rule.
- **Distributions:** each set's E and byte-length distributions (min, quartiles, max) are printed.

## Decision rule (C-NOISE, C-STAT), fixed before any sample

- **Excess (per seed, for r):** the seed's r over its 200 samples is above the maximum r of the 10 reference blocks,
  **and** stays above it when any one of the seed's ten 20-sample sub-blocks (generation seeds 5020 to 5039, 5040 to
  5059, and so on) is dropped, across all 10 drop-one-block subsets of 180 samples.
- **Error rate of this rule, stated (corrected after ChatGPT note 002):** if model and reference sets were
  exchangeable, one set would exceed the maximum of 10 others with probability at most 1/11 ≈ 0.091 per seed. It is
  exactly 1/11 when there are no ties, and drop-one can only lower it. Model sets and contiguous blocks of real
  stories are **not** shown to be exchangeable. The maximum is therefore a **descriptive threshold**. No p-value or
  error rate is claimed for the verdict.
- **Same-input noise, reported, not a criterion:** r for each of the seed's ten 20-sample sub-blocks, and whether
  TLM-005's 0.0405 lies inside seed 41's sub-block range.

## Registered outcomes (exactly one; precedence top to bottom)

| Order | Condition | Outcome |
|---|---|---|
| 1 | G0 fails, any count missing, or G3 fails | STOP / INCONCLUSIVE |
| 2 | a control fails: the positive control shows no excess, the R fixture gives R = 0, or `--df-any` leaves R > 0 anywhere | CONTROL FAILED: no substantive outcome |
| 3 | E = 0 for any set, block, or drop-one subset | INCONCLUSIVE |
| 4 | B ≠ 0 in any set after masking | INCONCLUSIVE |
| 5 | an r-excess passes the max test but fails drop-one-block | INCONCLUSIVE |
| 6 | r excess in seed 41 only | SEED-41 ONLY: on this sample, one of the two tested models clears the threshold |
| 7 | r excess in both seeds | BOTH: both tested models clear it |
| 8 | r excess in seed 42 only | SEED-42 ONLY: TLM-005's seed pattern reversed |
| 9 | no r excess in either seed | NEITHER CLEARED: neither model clears the threshold on this sample. This is consistent with the rival but does not show sampling noise was the cause |
| 10 | anything else | INCONCLUSIVE (fallback; ChatGPT's TLM-005 note 004) |

The null control is reported, not gated. By chance it can clear the threshold.

- The scope label from G1/G2 (TLM-004 models or RECIPE REPLICATE) is attached to whichever outcome is reported.
- **Secondary, reported, not part of the verdict:** the same rule applied to u, to the masked copy rate and to the
  ≥ 200-byte share.
- **Scope in every outcome:** verbatim overlap with this training slice. It says nothing about how the model learned
  it.

## Anti-vacuity (M3)

- **Positive control:** 200 stories taken verbatim from the training slice (story indices 1,000 to 1,199) are scored
  as if they were a model seed. They must show an r- or u-excess. If not, the rule cannot say "excess".
- **R fixture (added after ChatGPT note 002):** the positive control could pass on U alone while the R counter was dead.
  So there is a small fixture: a 50-byte window that occurs in at least two distinct, non-duplicate training stories,
  checked by SHA-256 of each story. The fixture must give R ≥ 1 normally and R = 0 under `--df-any`. Claude writes it,
  so it is not blind. It is committed before the run.
- **Null control:** valid stories 2,200 to 2,399 are scored as if they were a model seed. They are expected to show
  no excess. No false-alarm rate is claimed for it: the threshold is descriptive, and even under exchangeability
  1/11 is only an upper bound for the strict maximum before drop-one. The result is reported either way. If it clears
  the threshold, that is named first in the results.
- **Decision function:** written as a pure function of the counts. ChatGPT may seal blind decision-table cases
  (synthetic counts with expected outcomes, including TLM-005's note 004 counterexample) before the run, with
  SHA-256 values only on GitHub.
- `--sabotage`: setting every training story's df to 1 (`--df-any`) must change r to 0 in every set. The run prints
  it.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | NOT RUN estimates. Search: about 5,200 model, 36,000 reference and 7,000 control windows; TLM-005 searched 3,532 in 2 m 18 s on 2 processes, so roughly 30 to 45 minutes. Generation: 400 stories of at most 330 tokens, minutes. Source B training: 2 × 6,313 s on 2 threads (TLM-004 logs), about 3.5 hours. |
| Noise | 10 reference blocks of 200; ten 20-sample sub-blocks per seed (reported). |
| Statistics | Max-of-10 with drop-one-block, as a descriptive threshold; no error rate claimed (exchangeability not established). |
| Evidence | Numbers pasted from the driver's output. |
| Independence | Driver and run SELF-TESTED by Claude. The instrument was blind-tested by ChatGPT in TLM-005. The decision table is open to ChatGPT's blind cases. Not independent of Chad Holland's shared instructions (M10). |
| External | TinyStories V2 (CDLA-Sharing-1.0). |
| Device | Linux container CPU. S25 NOT VALIDATED. |
| Verdict code | Fail-closed precedence table above, including a fallback row. |
| Exploration | None. No new sample generated and no reference story beyond 0 to 199 read. Figures here are from TLM-004 and TLM-005's committed outputs. |
| Held-out | Generation seeds 5020 to 5219 and valid stories 200 to 2,399 are unseen. Training stories 1,000 to 1,199 are a control, not held out. |
| Generated inputs | 400 new model samples, committed unedited; their length distribution is printed. |
| People's data | No. |
| Design | Observational re-analysis of model outputs. No causal claim about training. |

## Unrun door

- Near-duplicate training stories counted as one document (open since TLM-005).
- A third and fourth training seed if the outcome is SEED-41 ONLY.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) drafted, from TLM-005's results and ChatGPT's (OpenAI GPT-6, Codex)
TLM-005 notes 002 and 004 → human validation: not performed → human editing/curation: direction by Chad Holland,
2026-11-25 → human responsibility: Chad Holland. Review level: none.*

## Revisions before freeze (W9)

- **2026-11-26, after ChatGPT (OpenAI, Codex) note tlm006/chatgpt/002** (PR #185, comment 7195139725). No sample
  generated, no reference story beyond 0 to 199 read.
  - The scope rule is now per model, with a third label: G2 alone no longer attributes the result to TLM-004's weights.
  - The error-rate sentence is corrected to "at most 1/11", and exchangeability is marked as not established, so the
    maximum is a descriptive threshold.
  - Frozen sensitivity analyses S1 (matched length, through the same tokenizer and cap) and S2 (per-text mean) are
    added, with E and length distributions.
  - E = 0 now has a defined outcome.
  - The R fixture is added, and failed controls get their own row.
  - NEITHER is renamed NEITHER CLEARED, and the SEED-41 ONLY and BOTH wording is narrowed to the two tested models.
  - The Statistics row of the controls table is updated to match.
- **2026-11-26, after ChatGPT note tlm006/chatgpt/004** (comment 7196002770): the null-control paragraph no longer
  predicts a "9%" chance excess. Superseded, verbatim: "By the stated error rate, they show one by chance about 9% of
  the time." 
  - Superseded text is in this file's history at `501ab63`.
