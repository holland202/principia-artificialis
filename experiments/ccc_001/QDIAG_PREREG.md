# CCC-001 stage Q diagnostics: cache parity, off-letter mass and answer-label permutation on Qwen2.5-1.5B (registration)

**Status:** REGISTERED, NOT RUN. Development-only diagnostic (C-EXPLORE). Self-tested.
**Date:** 2026-11-21. **Parent:** stage Q, registered at `ec1c422`, run at `9251d6a`, outcome pinned at `dae6f73`
([QUALIFICATION_PREREG.md](QUALIFICATION_PREREG.md), [QUALIFICATION_RESULTS.md](QUALIFICATION_RESULTS.md)).
**Agreed in the relay:** ChatGPT proposed these checks in `ccc-relay/chatgpt/002` (PR #172); Claude accepted them in
`ccc-relay/claude/003`. No CCC-001 registration is frozen by this file and no confirmatory item is involved.
**Method:** METHOD.md, WORKFLOW.md and CONTROLS.md as on this branch at `17487c8`.

**Stage Q's verdict does not change, whatever happens here** (M12). Its registered decision rule already stopped
the stage for this model. This diagnostic only narrows or widens what the recorded refutation means.

## Question (W1)

Three things could make stage Q's reading of Qwen2.5-1.5B wrong or narrower than written:

1. **Cache path.** Arms E, F16, F64 and EF64 were read through a reused KV cache. The only check,
   `results/ccc_001/cache_check.txt`, covers 4 of 24 items of arm E (largest difference 0.00178), and no script in
   the repository produces it (an M6 gap, recorded here). The long arms were never checked.
2. **Off-letter mass.** S and G renormalise over the three letter tokens (IDs 32, 33, 34). If the model puts most of
   its next-token mass elsewhere, S and G describe a minority of its behaviour.
3. **Letter, not meaning.** "The model never chose C" may be about the letter C (stage Q's arm D was modal A on 14
   items) rather than about the meaning "not enough evidence".

## Instrument and stand-ins (M4)

Same model file (SHA-256 `dd924a11…c6d3ee`), bf16, CPU, the same 24 items in `probes.py`, the same arms D, E, F16,
F64, EF64 built by the same functions in `common.py`. The harness imports `common` and `probes`; it does not copy
them. Two read-out paths:

- **cached:** `common.measure` as run in stage Q;
- **uncached:** one full forward pass over the complete rendered prompt per item, nothing reused.

**Relabelings.** The three meanings stay fixed (accept, reject, not enough evidence) and the letters move. With
π0 = stage Q (accept A, reject B, not-enough C):

| π | accept | reject | not enough |
|---|---|---|---|
| π1 | B | C | A |
| π2 | C | A | B |
| π3 | B | A | C |
| π4 | A | C | B |
| π5 | C | B | A |

Under πk the option line lists A, B, C in letter order, each followed by its own meaning phrase exactly as in
`probes.QUESTION` ("accept the claim", "reject the claim", "not enough evidence to decide"). The instruction in arm E
keeps its wording and clause order with the letters substituted ("Answer ⟨accept⟩ only when …, ⟨reject⟩ only when
…, and ⟨not enough⟩ whenever …"). Each item's key becomes the letter of its meaning. The harness asserts that the π0
strings equal `probes.QUESTION` and `common.EXPLICIT` byte for byte, and stops otherwise.

## Predictions (M2, M5)

All differences are absolute differences of per-item probabilities over {A, B, C}.

- **P0 (cross-session reproduction).** π0, cached path, arms D and E reproduce every per-item probability in
  `results/ccc_001/qualify.json` within 0.01.
- **P1 (cache parity).** For arms E, F16, F64, EF64 (96 item-arm pairs), cached versus uncached: largest difference
  ≤ 0.01, and the same modal letter on 96 of 96.
- **P2 (Q2 survives the uncached path).** Mean G(E) − mean G(D), both uncached, is < 0.10.
- **P3 (anti-vacuity for P1, M3).** Arm E's 24 probe suffixes run on arm F16's cache, compared with arm E uncached:
  largest difference > 0.01. This shows the P1 comparison can see a wrong cache.
- **P4 (letter mass).** Uncached, π0: in each of the 5 arms, the median over 24 items of the full-vocabulary softmax
  mass on token IDs 32, 33, 34 is ≥ 0.90.
- **P5 (abstention is about meaning).** For each of π1–π5, uncached arm D: the modal letter is the not-enough
  letter on ≤ 2 of 24 items.
- **P6 (Q2's failure survives relabeling).** For each of π1–π5, uncached: mean G(E) − mean G(D) < 0.10.

P2 and P6 are predictions that stage Q's failure reproduces; holding them is not a pass for the model.

**Sabotage (`--sabotage`):** the full logit vector is replaced by zeros before every read-out. Expected: P4 REFUTED
(mass 3/V at every item), P0 REFUTED, exit 1.

**Verdict line:** `VERDICT n of 7 as registered`, a `DIGEST` (SHA-256 of all per-item probabilities rounded to 4
dp), exit 0 only on the outcome pinned after the run.

## What each outcome means

| Refuted | Reading |
|---|---|
| P0 | Results differ across sessions by more than 0.01; report the size; cross-session comparisons need a tolerance |
| P1 | Stage Q's context-arm numbers are re-reported from the uncached path as a new run; the original record is kept |
| P2 | The Q2 refutation was a cache artefact; recorded; the stage Q verdict still stands as registered |
| P3 | The parity check is blind; P1 says nothing |
| P4 | S and G describe the letter-conditional choice only; the next stage Q reports mass and gates on it |
| P5 | "Never chose C" was at least partly a letter effect; stage Q's results get a dated correction note |
| P6 | Q2's refutation is label-dependent; recorded; the next stage Q includes relabelings |

## Feasibility (C-FEAS)

Forward passes: 120 cached (P0, P1) + 120 uncached π0 + 24 mismatched-cache (P3) + 5 × 2 × 24 = 240 uncached
relabeled. Context lengths from committed output: E 114, F16 569, F64 2,273, EF64 2,366 tokens
(`results/ccc_001/run.txt`, `feasibility.txt`); a 2,273-token prefill took 6.7 s on 2 threads, so the 48 long
uncached passes take about 6 minutes.

## Trigger table (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Above |
| Noise | P0 across sessions; stage Q's Q1 within a session |
| Statistics | No population claim; fixed thresholds on 24 fixed items |
| Evidence | Numbers come from the harness's printed output, pasted verbatim |
| Independence | No. Claude wrote the items, the code and these predictions and will run them. SELF-TESTED. ChatGPT proposed the checks; that is not review of the run |
| External | Qwen2.5 weights (Apache-2.0) |
| Device | Linux container CPU only. S25 NOT VALIDATED |
| Verdict code | Fail-closed; sabotage must exit 1 |
| Exploration | Yes, development-only |
| Held-out | The 24 items are development items already; none can confirm CCC-001 |
| Generated inputs | Relabeled prompts for π1 will be printed and read before the run's numbers are read |
| People's data | None |
| Design | Instrument diagnostic on one model; no claim about conversations or commercial assistants |

## Limits

One small model, 24 items, bf16 on CPU. The relabelings move letters, not wording; a model sensitive to the order
of meanings in the option line is not separated from one sensitive to letters.

## Open door (M15)

Whatever the outcome, re-register stage Q on Qwen2.5-7B-Instruct (4-bit) with new items written by someone other
than Claude, reporting letter mass and at least the π1 relabeling alongside S and G.

## Provenance (M13)

Question origin for CCC-001: Federico Talens-Alesson, credited as the question's originator only; no endorsement
or validation by him is implied. Checks proposed by ChatGPT (OpenAI, GPT-6) in the relay. Registration written by
Claude (Anthropic, Opus 5.5) in a fresh scheduled session under Chad Holland's standing direction of 2026-11-21.
Human validation: not performed. Human editing/curation: direction only. Human responsibility: Chad Holland.
