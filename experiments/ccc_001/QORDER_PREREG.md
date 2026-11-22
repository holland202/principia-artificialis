# CCC-001 stage Q letter-by-position crossing on Qwen2.5-1.5B: is abstention about the letter A or the first place? (registration)

**Status:** REGISTERED, NOT RUN. Development-only diagnostic (C-EXPLORE). Self-tested.
**Date:** 2026-11-21. **Parent:** QDIAG, registered at `4726f42`, run at `7cffcbd`, outcome pinned at `b898f94`
([QDIAG_PREREG.md](QDIAG_PREREG.md), [QDIAG_RESULTS.md](QDIAG_RESULTS.md)).
**Agreed in the relay (PR #172):** Claude proposed separating letter from position in `ccc-relay/claude/005`;
ChatGPT proposed the full crossing and prediction P1 in `ccc-relay/chatgpt/006`; Claude accepted it, with the
additions marked below, in `ccc-relay/claude/007`. No CCC-001 registration is frozen by this file and no
confirmatory item is involved. **Stage Q's verdict does not change, whatever happens here** (M12).
**Method:** METHOD.md, WORKFLOW.md and CONTROLS.md as on this branch at `0dfeb90`.

## Question (W1)

QDIAG found that Qwen2.5-1.5B with no context abstains far more often when "not enough evidence" is labelled A
(modal on 12 and 10 of 24 items) than when it is labelled C (0 and 0). In QDIAG the option line always listed the
letters in A, B, C order, so A was also first. Does the effect follow the letter, the place in the line, or both?

## Instrument and stand-ins (M4)

Same model file (SHA-256 `dd924a11…c6d3ee`), bf16, CPU, the same 24 items in `probes.py`, the same meaning phrases
and closing line as `qdiag.question`. **Uncached** full forward pass per prompt (QDIAG's P1 found the cache path
drifts by up to 0.031). Probabilities are the softmax over token IDs 32, 33, 34, **unrounded** (float64 from the
float32 logits) for every contrast.

**Conditions.** A letter assignment maps the three meanings (accept, reject, not enough) to A, B, C (6 ways). A
display order sets which meaning appears first, second and third in the option line (6 ways). 6 × 6 = 36
conditions. Example: letters {accept B, reject C, not enough A}, order (not enough, accept, reject) renders
"A = not enough evidence to decide, B = accept the claim, C = reject the claim." Each item's key becomes the letter
of its meaning. The harness asserts that the condition (letters π0, order accept-reject-notenough) equals
`probes.QUESTION` byte for byte, and that each of the 36 lines contains every "letter = phrase" pair once.

**Cells.** For the abstention meaning, letter L ∈ {A, B, C} × display position j ∈ {1, 2, 3}: 9 cells, each holding
4 conditions (2 arrangements of the other two letters × 2 of the other two positions; counted by code, not 2 as
written in 006). Cell value m(L, j) = mean over 24 items × 4 conditions of p(abstention letter).

**Already observed.** The 6 conditions whose letters read A, B, C in display order are QDIAG's π0–π5. They sit in
cells (A,1), (B,2) and (C,3), 2 of 4 conditions each. The other 30 are unseen.

## Predictions (M2, M5) — primary analysis is arm D

- **P0 (cross-session reproduction).** The 6 already-observed conditions reproduce QDIAG's uncached arm-D per-item
  probabilities (`results/ccc_001/qdiag.json`) within 0.01.
- **P1 (letter effect; ChatGPT, 006, verbatim in substance).** m(A, j) − m(C, j) > 0 for each of j = 1, 2, 3.
- **P2 (P1 on unseen data only; Claude addition).** P1 recomputed over the 30 unseen conditions only holds at all
  three positions.
- **P3 (anti-vacuity, M3).** Under `--sabotage` (all logits set to zero) every contrast is exactly 0, all 864
  modal readings fall in the tie bucket, P1 and P2 are REFUTED, exit 1.

**Reported, never gated:** the position contrast m(L, 1) − m(L, 3) for each letter L; all 9 cell means; modal counts
with exact ties in their own bucket (fixes QDIAG defect 5 for this harness only); the 36-condition table.
**Secondary (arm E, reported, never gated):** the same 9 cells for arm E (instruction clause order fixed by meaning,
letters substituted as in QDIAG), and both Q2 components per cell.

**Verdict line:** `VERDICT n of 4 as registered`, a `DIGEST` (SHA-256 of all per-item probabilities rounded to 6 dp),
exit 0 only on the outcome pinned after the run.

## What each outcome means

| Outcome | Reading, this model and these items only |
|---|---|
| P1 and P2 hold, position contrasts ≈ 0 | The abstention bias follows the letter A |
| P1 and P2 hold, position contrasts > 0 | Both letter and first place contribute |
| P1 or P2 refuted, position contrasts > 0 | The bias follows first place, not the letter |
| P1 holds, P2 refuted | The letter effect rests on the conditions already seen; not established |
| P0 refuted | Cross-session drift above 0.01; report its size before reading anything else |

## Feasibility (C-FEAS)

864 uncached arm-D passes (prompts about 70 tokens) plus 864 arm-E passes (about 185 tokens). From
`results/ccc_001/feasibility.txt`, a 2,273-token prefill took 6.7 s on 2 threads; the short passes are estimated
at well under an hour in total (NOT RUN). The model must be downloaded again in a fresh container.

## Trigger table (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Above |
| Noise | P0 across sessions; deterministic forward passes within a session |
| Statistics | No population claim; signs of cell-mean differences on 24 fixed items, no threshold beyond > 0 |
| Evidence | Numbers come from the harness's printed output, pasted verbatim |
| Independence | No. Claude writes the code and runs it. ChatGPT proposed P1; that is not review of the run. SELF-TESTED |
| External | Qwen2.5 weights (Apache-2.0) |
| Device | Linux container CPU only. S25 NOT VALIDATED |
| Verdict code | Fail-closed; sabotage must exit 1 |
| Exploration | Yes, development-only; 6 of 36 conditions already seen, isolated by P2 |
| Held-out | The 24 items are development items already; none can confirm CCC-001 |
| Generated inputs | All 36 option lines printed and read before any number is read |
| People's data | None |
| Design | Instrument diagnostic on one model; no claim about conversations or commercial assistants |

## Limits

One small model, 24 items, one wording. A zero threshold means a tiny positive difference holds P1; the cell means
are printed so the size is visible. Letter and position are crossed, but each letter's token identity is not
separated from its alphabetical rank.

## Open door (M15)

Whatever the outcome, the next stage Q (Qwen2.5-7B-Instruct, 4-bit, items written by someone other than Claude)
reports the abstention cell means for at least the (A,1), (A,3), (C,1), (C,3) corners alongside S and G.

## Provenance (M13)

Question origin for CCC-001: Federico Talens-Alesson, credited as the question's originator only; no endorsement
or validation by him is implied. Crossing design and P1 proposed by ChatGPT (OpenAI) in the relay. Registration
written by Claude (Anthropic, Opus 5.5) in a fresh scheduled session under Chad Holland's standing direction of
2026-11-21. Human validation: not performed. Human editing/curation: direction only. Human responsibility: Chad
Holland.
