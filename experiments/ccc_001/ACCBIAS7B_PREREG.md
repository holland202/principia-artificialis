# CCC-001 accept-shift decomposition on the GPU7B outputs (registration, written before any 7B output is seen)

**Status:** REGISTERED, NOT RUN. Nothing is built. Development-only secondary analysis (C-EXPLORE). Self-tested
design. **Date:** 2026-11-22, drafted from 18:10Z; the commit time is the registration time.
**Parents:** [ACCBIAS_PREREG.md](ACCBIAS_PREREG.md) (`f416f86`, results at `5543cce`) and
[GPU7B_AMENDMENT.md](GPU7B_AMENDMENT.md) (`5b4807c`). No CCC-001 registration is frozen by this file.
**No qualification verdict changes, whatever happens here** (M12). Stage Q's and LONGCTX's gates are read only from
their own harness output, as registered.

**Agreed in the relay (PR #172):** Claude asked whether this decomposition should be registered before the 7B outputs
return (`ccc-relay/claude/027`). ChatGPT said yes, asked for prior exposure and the commit time to be recorded, and
asked that the shifts be reported even if qualification fails (`ccc-relay/chatgpt/028`).

## Prior exposure (C-EXPLORE)

- **7B outputs: none seen.** At drafting, the amendment's last entry records Kaggle "Version #1 … Queued". No
  returned file, log, digest or summary line is on any branch of this repository (checked with `git ls-remote`
  and the PR #177 comments at 18:10Z). The author has seen no 7B number.
- **1.5B outputs: all seen.** The author wrote and read ACCBIAS, QORDER, QDIAG, stage Q and LONGCTX REF. In
  particular 1.5B LONGCTX REF Δ_acc per π was `[0.105711, 0.093951, 0.313284]`, and QORDER cell (A, 1) was
  `+0.091547`. T1 and T2 below are transfer predictions from those numbers, not blind guesses.
- 1.5B **stage Q** Δ per meaning (π0, short context, `qualify.json`) has not been computed. The dry run below will
  compute it, and it will be reported as a regression number, not as a prediction check.

## Inputs (M4)

From the returned run (`kaggle_gpu7b.py`): `qualify_7b.json` (arms D, E, F16, F64, EF64; π0 only, accept = A, slot 1)
and `longctx_{REF,N016,STRESS}_7b.json` (cells D0–D2, E0–E2), with their logs `stageq.txt`, `longctx_*.txt` and
`runner.txt`. Probabilities `p` are rounded to 6 dp. Items are the 24 development items; their content is not
discussed (RELAY.md rule 4). Harness: `experiments/ccc_001/accbias7b.py`, pure Python, reusing `accbias.py`'s
definitions of Δ_M, equal item weights and the stored-key assertion.

## Gates (fail-closed; nothing below them is read if one fails)

- **V (custody).** `runner.txt` shows the four registered shard hashes `OK`. Each JSON, canonicalised exactly as its
  harness does (`qualify.py` and `longctx.py` `canon`), hashes to the `DIGEST` in its own log. Until V holds, every
  7B number is CONTRIBUTOR REPORTED and this analysis is not run.
- **P0 (bookkeeping).** Every stored key equals the letter of the item's meaning under that cell's mapping. Every `p`
  is finite. |Δ_acc + Δ_rej + Δ_ne| ≤ 5e-6 per pair. With E replaced by D, every cell value is exactly 0.

A missing length (for example STRESS not finished in Kaggle's 12 h) is printed `ABSENT`. It is not a failure of V.

## Predictions (Claude; M2, M5)

- **T1 (REF transfer).** In 7B LONGCTX REF, Δ_acc = mean over items of p_E(accept letter) − p_D(accept letter) is
  > 0 in each of π0, π1 and π2. REFUTED if any π is ≤ 0. NOT READ if REF is absent.
- **T2 (stage Q transfer).** In 7B stage Q, Δ_acc (E against D, π0) is > 0.

**Reported, never gated:** for every length present and each π, Δ_acc, Δ_rej, Δ_ne and items up/down of 24; for
stage Q, the same for E − D and for EF64 − F64; the 1.5B values beside the 7B ones, from the files already
committed. A qualification failure does not stop the report (ChatGPT, 028).

**Not claimed:** any letter × slot interaction. In LONGCTX the option lines are always A, B, C, so π, letter and slot
are one factor. A claim about the A penalty at REF needs its own crossing there, a separate development proposal.
No shuffle null is registered, because each cell has one mapping.

## Anti-vacuity (M3)

`--sabotage` replaces each arm-E reading by its arm-D reading: P0 holds, T1 and T2 are REFUTED, exit 1. Before any
7B file is read, a **dry run on the committed 1.5B files** must reproduce ACCBIAS's LONGCTX REF values above to 6 dp.
The verdict line is `VERDICT n of 3` (P0, T1, T2) plus a DIGEST. Exit 0 only on the outcome pinned after the 7B run.

## Outcomes (this model, these 24 items, synthetic text only)

| Outcome | Reading |
|---|---|
| T1 and T2 HELD | The 1.5B sign pattern of the accept shift transfers to 7B at REF and short context |
| T1 REFUTED | At REF, at least one mapping shows no accept shift in 7B |
| T2 REFUTED | At short context with accept as A in slot 1, 7B shows no accept shift |
| V or P0 refuted | Custody or readout defect; reported first, nothing else read |

## Trigger table (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Arithmetic on at most 4 files × 144 pairs; seconds (NOT RUN estimate) |
| Noise | Same-input noise is the amendment's Q1 and G2, read from their logs |
| Statistics | No population claim; signs of means on 24 fixed items |
| Evidence | Numbers pasted from harness output. 7B inputs are CONTRIBUTOR REPORTED until V holds |
| Independence | No. Claude registers and will run it; ChatGPT's 028 is design input, not review. SELF-TESTED |
| External | Qwen2.5-7B-Instruct weights (Apache-2.0), pinned in the amendment |
| Device | Kaggle 2× T4 fp16 for the readings; this analysis on Linux CPU. S25 NOT VALIDATED |
| Verdict code | Fail-closed: V, then P0, then T1–T2. Sabotage exits 1 |
| Exploration | Yes; prior exposure listed above |
| Held-out | None. Development items only |
| Generated inputs | None new |
| People's data | None |
| Design | Instrument diagnostic on one model's answer format; no claim about conversations |

## Open door (M15)

NOT RUN: a fresh letter × slot crossing at REF on a qualified model, which would test the A penalty that
`ccc-relay/chatgpt/028` proposes for QORDER.

## Provenance (M13)

Claude (Anthropic, Opus 5.5), fresh scheduled relay session. Rules on exposure and reporting: ChatGPT (OpenAI),
relay turn 028. Direction for the relay and the GPU7B run: Chad Holland, 2026-11-21 and 2026-11-22. Human
validation: not performed. Human responsibility: Chad Holland. The question behind CCC-001 is Federico
Talens-Alesson's; crediting him implies no endorsement or validation by him.
