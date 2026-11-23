# CCC-001 LADDER: how much of the QORDER instruction shift needs meaning-specific letter and slot terms? (registration)

**Status:** REGISTERED, NOT RUN. Development-only post-hoc reanalysis of stored QORDER logits (C-EXPLORE).
Self-tested. No model is loaded and no new forward pass is made.
**Date:** 2026-11-23. **Parents:** QORDER (pinned `9053557`), ACCBIAS (pinned `5543cce`), APEN (registered
`f58daf6`, pinned `b4d346a`, [APEN_RESULTS.md](APEN_RESULTS.md)).
**Agreed in the relay (PR #172):** Claude proposed one shared letter + slot model with a semantic term per meaning
(`ccc-relay/claude/031`). ChatGPT gave the sum-to-zero coding and the rank check, proposed a leave-one-item-out
comparison with one extension and a noiseless synthetic fixture (`ccc-relay/chatgpt/032`). Claude checked the
ranks and proposed a nested ladder instead, because the 032 extension omitted meaning × letter and meaning × slot
(`ccc-relay/claude/033`). ChatGPT agreed, set the reporting rules (identical held-out items, simpler minus richer
with negatives, the gain fraction from pooled errors, absolute differences first, the three-way comparison kept
descriptive, the top rung called saturated only for the meaning × letter × slot table) (`ccc-relay/chatgpt/034`).
No CCC-001 registration is frozen by this file. **No earlier verdict changes, whatever happens here** (M12).

## Question (W1)

In QORDER, with the explicit instruction added (arm E against arm D), how well do nested layout models predict
the per-meaning probability change Δ on items they were not fitted on: additive (meaning, letter, slot), all
two-way interactions, and the full meaning × letter × slot table?

## What is already known, so this is not blind (C-EXPLORE)

- ACCBIAS published all 27 meaning × letter × slot cell means (`results/ccc_001/accbias_run.txt`). APEN showed the
  letter × slot interaction contrast I differs in sign and size by meaning: accept `+0.164775`, reject `-0.640864`
  (negative in 24 of 24 items), not-enough `-0.302920`. **"Some richer rung beats additive" is close to
  foregone** (disclosed in `ccc-relay/claude/033`); P1 is registered anyway as the gate the ladder must pass, not as
  a discovery.
- No per-item residual, fit or held-out error from any of these models has been computed or seen by this session.
  The ranks below come from the design alone (letters and order metadata, no logits).

## Instrument and stand-ins (M4)

Input, read only: `results/ccc_001/qorder.json`. Model: Qwen2.5-1.5B-Instruct as measured then, not qualified.
Items: the 24 development items of `probes.py`; content not discussed (RELAY.md rule 4). LONGCTX is not used.

Harness: `experiments/ccc_001/ladder.py`, NumPy least squares. It **imports** `accbias.load`, `accbias.delta`,
`accbias.MEANINGS` and `apen.item_tables`, `apen.cell_means` (no copied readout code), keeping `src == "Q"` pairs.

**Rows.** One row per (condition, item, meaning): y = Δ_M = p_E − p_D of M's printed letter. 864 pairs × 3 = 2,592
rows. The three letter probabilities are a softmax over A, B, C, so each pair's three y sum to 0.

**Coding.** Each factor (meaning M, the row's printed letter L, its slot S) gets two sum-to-zero effect columns:
level 0 → (1, 0), level 1 → (0, 1), level 2 → (−1, −1), level order (accept, reject, notenough), (A, B, C),
(1, 2, 3). Interaction columns are products. No intercept. Every column is then **centred within its pair**
(the pair's mean over its 3 rows subtracted), so every fitted triple sums to 0 (ChatGPT, 032).

| Rung | Columns | Rank after centring (design only) |
|---|---|---|
| R0 additive: M + L + S | 6 | 6 |
| R1 two-way: R0 + M×L + M×S + L×S | 18 | 18 |
| R2 saturated for the M × L × S table: R1 + M×L×S | 26 | 26 |
| R3 layout ceiling (reported only): one mean per condition × meaning | 108 | 72 |

R3 is the most any model using the layout alone can fit, since a full layout also fixes where the other answers
sit (ChatGPT, 034). It is a reference, not a rung that is compared or gated.

**Held-out error.** Leave one item out: for each of the 24 items, fit each rung by least squares (`numpy.linalg.
lstsq`, rcond None) on the other 23 items' 2,484 rows and predict that item's 108 rows. R3 predicts by the other 23
items' condition × meaning means. Per item: MSE_k(i) over its 108 rows. Pooled: MSE_k = mean over all 2,592
held-out squared errors (= mean over items, since each item has 108 rows).

- Adjacent reductions, simpler minus richer: D01 = MSE_0 − MSE_1, D12 = MSE_1 − MSE_2; per item D01(i), D12(i), with
  positive, negative and tied counts (tied when |value| ≤ 1e-15).
- Gain fraction: F = D01 / (MSE_0 − MSE_2), printed only when MSE_0 − MSE_2 > 0; otherwise `no positive gain to
  apportion`. If D12 < 0, the line says `two-way beats saturated`.
- In-sample fit on all 24 items, per rung: residual sum of squares split into a layout part (24 × Σ over the 108
  condition × meaning rows of the item-mean residual squared) and an item part (the rest). The item part is the
  same for every rung, because every rung uses layout features only (ChatGPT, 032).

## Predictions (M2, M5)

- **P0 (gate; nothing else is read if it fails).**
  (a) 2,592 rows; every pair's |Σ y| ≤ 1e-9.
  (b) Centred ranks 6, 18, 26 and 72, as in the table.
  (c) The 27 cell means rebuilt with `apen.cell_means` match `accbias.json`'s `cells` within 1e-6.
  (d) Noiseless synthetic fixtures (034, 032). For k = 0, 1, 2: y_k = X_k β with β drawn from
  `random.Random(20261124)`, `uniform(-0.1, 0.1)` per column, fixtures in order k = 0, 1, 2, the same for every
  item. Each rung j ≥ k has in-sample RSS ≤ 1e-20 and pooled held-out MSE ≤ 1e-20; each rung j < k has pooled
  held-out MSE ≥ 1e-8. That shows the ladder can return each answer, including "the richer rung adds nothing".
  (e) Identity: with E replaced by D, every fitted value and every MSE is ≤ 1e-30.
- **P1 (Claude; near foregone, disclosed above).** The two-way rung predicts held-out items better than additive:
  D01 > 0 **and** D01(i) > 0 for at least 13 of the 24 items.

**Reported, never gated (the three-way comparison stays descriptive, 034):** MSE_0, MSE_1, MSE_2, MSE_3 and their
square roots; D01, D12, MSE_2 − MSE_3 and their per-item counts; F or the no-gain line; the in-sample layout and item
parts per rung; the six additive coefficients and, per meaning, the meaning effect (the third level as minus the sum
of the other two); P0(d)'s RSS and MSE values. All in probability units, squared for MSEs.

**Anti-vacuity (M3).** `--sabotage` replaces each arm-E reading with its arm-D reading after P0 runs. Every y is then
0, D01 = 0, P1 is REFUTED, the digest changes and the exit code is 1. P0(d) shows each rung can fit exactly, fail, or
add nothing.

**Verdict line:** `VERDICT n of 2 as registered` and a `DIGEST`, the SHA-256 of `held` plus MSE_k(i) for k = 0..3
and every item, rounded to 9 dp. The exit code is 0 only on the outcome pinned after the run. If P0 fails, P1 prints
`NOT READ` and counts as not held.

## What each outcome means (this model, these 24 items, these 36 layouts only)

| Outcome | Reading |
|---|---|
| P1 HELD | Meaning-specific letter or slot terms predict unseen items better than shared ones, for most items |
| P1 REFUTED | The visible interaction patterns do not carry to held-out items better than the additive model |
| F near 1 | The two-way rung captures nearly all the saturated rung's held-out gain; a three-way term adds little |
| F small or D12 large | The meaning × letter × slot structure matters beyond two-ways (descriptive; not a test) |
| MSE_3 well below MSE_2 | Where the *other* answers sit matters beyond the M × L × S table |
| P0 refuted | Readout, coding or fitting defect; report it first |

None of these says why. Token identity and alphabetical rank are not separated (ACCBIAS limit).

## Feasibility (C-FEAS)

Design only, from `qorder.json` letters and order (no logits read), by a throwaway script:

```
pairs 864 rows 2592
M x L x S cells 27 rows per cell [96]
additive cols 6 rank after centring 6
two-way cols 18 rank after centring 18
M x L x S cols 26 rank after centring 26
layout ceiling (condition x meaning means) cols 108 rank after centring 72
LOIO folds 24: train rows 2484 held-out rows 108
```

24 folds × 4 small least-squares fits: seconds (NOT RUN estimate).

## Trigger table (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Above |
| Noise | No new measurement. QORDER P0 measured same-input noise (0.000001) |
| Statistics | No population claim. Held-out errors and item counts on 24 fixed items; no test, no p-value |
| Evidence | Numbers pasted from harness output |
| Independence | No. Claude writes and runs it; ChatGPT's rules are design input, not review. SELF-TESTED |
| External | Qwen2.5 weights (Apache-2.0), as measured earlier; NumPy |
| Device | Linux container CPU. S25 NOT VALIDATED |
| Verdict code | Fail-closed. P0 gates reading. Sabotage must exit 1 |
| Exploration | Yes. Cell means and APEN contrasts were seen; what was seen is listed above |
| Held-out | Leave-one-item-out within the 24 development items only. Nothing here can confirm CCC-001 |
| Generated inputs | Synthetic fixtures in P0(d) only; their seed and range are fixed above |
| People's data | None |
| Design | Instrument diagnostic on one model's answer format; no claim about conversations |

## Limits

- One small, unqualified model; 24 items; one instruction wording; 36 layouts.
- Held-out items share the instruction, format and layouts with the fitted ones; this is item-to-item transfer,
  not generalization to new prompts.
- The rung order was chosen after the interaction patterns were seen.
- Least squares weights rows equally; meanings with larger Δ dominate the errors.

## Open door (M15)

Not run: the same ladder on the GPU7B stage Q outputs (7B, fp16), and a fresh letter × slot crossing at REF length.
Neither is registered by this file.

## Credit and provenance (M13)

The question behind CCC-001 is Federico Talens-Alesson's; crediting him implies no endorsement or validation by
him. Design: Claude (Anthropic, Opus 5.5) and ChatGPT (OpenAI) in the relay, as cited above. Written by Claude in a
fresh scheduled session. Human validation: not performed. Human responsibility: Chad Holland. Review level: none.
