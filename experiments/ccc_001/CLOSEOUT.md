# CCC-001 relay closeout

**Status:** FINAL as the record of the relay, 2026-11-23. It is not a result about conversation order, because none
was measured. The relay closed at turn 040 (`ccc-relay/chatgpt/040`, comment 7091583361, 2026-11-23T04:26:32Z). The
draft was written at turn 037 and updated at 039 (last at `a3c4b81`, as `CLOSEOUT_DRAFT.md`). This version applies
the changes ChatGPT asked for in 040, after Chad Holland directed it in live chat on 2026-11-23. Proposed in
`ccc-relay/claude/033`, agreed in `ccc-relay/chatgpt/034`, contents asked for in `chatgpt/034`, `036` and `040`. The
only things run for this file are the export checks in `results/ccc_001/closeout_export_check.txt`. Every other
number is copied from the committed log it cites. The changes from the draft are listed at the end (W9).

## Finding, 2026-11-23

Wording from ChatGPT (OpenAI), `ccc-relay/chatgpt/034` and `040`:

> The relay reached its planned endpoint at turn 040. It archived primary checkpoints 016 and 032. No study model
> scored the original or shuffled conversation at either checkpoint. The effect of conversation order on
> consistency and correctness remains unmeasured.

The relay measured nothing about the question behind CCC-001. Below, failures come first (M8).

## 1. Model qualification: no model qualified at any length

| Check | Model | Outcome | Source |
|---|---|---|---|
| Stage Q, Q2 (gain ≥ 0.10) | Qwen2.5-1.5B | **REFUTED** `-0.0495`, 3 of 4 | `results/ccc_001/run.txt` |
| Stage Q, Q2 | Qwen2.5-7B | **REFUTED** `0.0379`, 3 of 4 | `results/ccc_001/gpu7b/stageq.txt` |
| LONGCTX REF, G5 / G6 | 1.5B | **REFUTED** `0.0523`; 12 of 24; 5 of 7 | `longctx_ref_run.txt` |
| LONGCTX REF, G5 | 7B | **REFUTED** `0.0973`; G6 held 20 of 24; 6 of 7 | `gpu7b/longctx_REF.txt` |
| LONGCTX N016, STRESS | 1.5B | NOT RUN (deviation D1) | `LONGCTX_DEVIATIONS.md` |
| LONGCTX N016 | 7B | ABSENT: CUDA out of memory on 2× T4 (tried 8.06 GiB) | `gpu7b/longctx_N016.txt` |
| LONGCTX STRESS | 7B | ABSENT: CUDA out of memory on 2× T4 (tried 33.94 GiB) | `gpu7b/longctx_STRESS.txt` |
| QUAL2 K3 / K4 (override) | 1.5B | **REFUTED** `0.0344` / `0.0210`, 1 of 3 | `qual2_run_1.5b.txt` |
| QUAL2 | 7B | NOT RUN | — |

**The ceiling found afterwards.** Q2's 0.10 gain was unreachable for 7B at stage Q: `headroom 1 - mean G(D) 0.0529`.
At REF it was reachable: `headroom 1 - mean over pi 0.1847` (`qual2_feasibility.txt`). The original verdicts stand
(M12). The ceiling explains why 7B's Q2 could not pass. It does not turn the failure into a pass.

N016 and STRESS are synthetic qualification lengths (`LONGCTX_PREREG.md`). Their resource limits are not missing
relay observations, and are listed apart from them.

## 2. Transfer prediction that failed on its own terms

ACCBIAS7B **T1 REFUTED**: `7B REF d_acc per pi [0.086268, -0.004510, 0.195446] (> 0 each)`. T2 held (`0.042487`).
`accbias7b_run.txt`. The positive mean shift in probability of accept seen at 1.5B REF did not hold for 7B under π1.

## 3. Archive

| Checkpoint | Role | Turns | File SHA-256 | Source |
|---|---|---|---|---|
| 008 | archival | 8 | `52308ddd809e331a97675506449e06240b23531ffb4820fbe3da5aeccf1db73d` | `relay_prefix_008_archival.json` |
| 016 | primary | 16 | `fe8775a1c48731844fb129ae71c759928bdb0cc8c32be69a455e9dc4ae23f6e6` | `relay_snapshot_016_run.txt` |
| 024 | secondary | 24 | `d5b261f2a0d7e621c9874d693bd82b1f15d5d63080b0921b7a61f9127518a1cb` | `relay_snapshot_024_run.txt` |
| 032 | primary | 32 | `9a9c07ad0f4f9cece4d5289eceb188dd8643405e71ef4772548b2be3b7715c3a` | `relay_snapshot_032_run.txt` |
| 040 | secondary | 40 | `b6b91710b0d06d3ae60e5ce54f78eff45b307a618069232e9b411cd4e173957a` | `relay_prefix_040.json`, `relay_export_040_run.txt` |

Edited turns 0 in the 016, 024 and 032 snapshot runs. Each later snapshot's bodies equal every earlier one's. The 024 and 032 shuffle
permutations equal the synthetic ones printed before those turns existed.

**The two final exports are different objects (`chatgpt/040`).**

- **Full PR conversation:** `results/ccc_001/relay_thread.json`, SHA-256
  `7da97b5dbaee95a060be79b708aaf099669ef5895f8fbed07ea197b1a1ae249d`. It holds all 49 comments on #172 at
  2026-11-23T04:27:55Z (`comments 49 edited 0`): the 40 relay turns, plus 9 comments that are not turns (Chad
  Holland's 5 and Claude's 4 `ccc/claude/*` notes). These 9 are part of the research record but not of the
  numbered transcript.
- **Numbered transcript:** `results/ccc_001/relay_prefix_040.json`, SHA-256 above. It holds turns 001–040 only.
- **Extraction.** `experiments/ccc_001/relay_extract.py` at `a3c4b81`, run unchanged. The export was committed at
  `d843087` (PR #180, merged into `main` at `0b7ad95`).
- **Checks, re-run at closeout, SELF-TESTED** (`closeout_export_check.txt`). Both files rehash to the values above.
  `turn numbers 001-040 once, in order: True`. Turns 001–032 match the archived 032 prefix: `32 of 32`. The 024,
  016 and 008 prefixes also match in full. Every prefix-040 body equals its comment in `relay_thread.json`:
  `40 of 40`.
- **Discrepancy, kept (M8).** `relay_check_040.py`, the PR #180 check, compares the stored `body_sha256` fields,
  not the body text. A sabotaged copy with one body altered and two turns swapped still printed `32 of 32` for
  bodies. The order check caught the swap (`False`). A stricter check, `relay_check_bodies.py`, recomputes each
  digest from the text. On the real files it prints `stored body_sha256 equals recomputed 40 of 40` and `32 of 32`
  against 032. On the sabotaged copy it prints `39 of 40` and `31 of 32`. The PR #180 conclusion stands, and the
  stricter check now backs it.

## 4. Prompt length: measured and projected

- **016, measured** (Qwen2.5 tokenizer, `tokenizer.json` sha256 `c0382117…`, the same file for 1.5B and 7B):
  context tokens `8673`; development-probe full prompts `min 8727 median 8737.0 max 8746`, original and shuffle
  alike (`prompt_lengths_016.txt`).
- **032, measured at relay turn 039** (same tokenizer, script and construction; the 016 run reproduced its committed
  output exactly first): context tokens `17894`; development-probe full prompts `min 17948 median 17958.0 max
  17967`, original and shuffle alike, `under L: True` (`prompt_lengths_032.txt`, `prompt_lengths_032_run.txt`).
  The earlier NOT RUN estimate was about 17,700 (`RELAY_EXTRACT_RESULTS.md`). The measured length is just under the
  synthetic STRESS case's longest prompt, `18132`, at which 7B ran out of memory.
- No model has been shown to qualify at any length. 7B ran out of memory on the synthetic N016 case, whose longest
  prompt was `8885` tokens.

## 5. Paired scores

No study model scored either ordering at any checkpoint. (The relay participants read earlier turns to write theirs, and the feasibility scripts tokenized the archived prefixes; neither is a score.) Arm-A use of a
prefix was never approved, and the qualification above gave no reason to ask for it.

## 6. What the format diagnostics are, and are not

QDIAG, QORDER, ACCBIAS, ACCBIAS7B, APEN and LADDER describe how one or two small models answer a three-letter
format on 24 development items. They answer nothing about conversation order. Their main findings: the read-out
depends on which letter means "not enough" (QDIAG P5, P6 REFUTED), and most of the remaining instruction shift is
item-to-item (LADDER, post-hoc: the layout ceiling explains `0.3783` of the total sum of squares). The relay agreed
in `chatgpt/036` to stop format diagnostics on these items.

## 7. Who ran what (M13, C-INDEP)

- 1.5B runs and all harnesses: Claude (Anthropic, Opus 5.5), in cloud sessions, CPU. SELF-TESTED.
- 7B runs: Chad Holland, on his Kaggle account (2× T4), from code Claude wrote. Recorded as CONTRIBUTOR REPORTED,
  then custody checked: the zip hash equals the printed hash and the JSON files rehash to their logs' digests.
- ChatGPT (OpenAI) proposed several designs and checked numbers against committed logs (VERIFIED FROM SOURCE). As far
  as the thread records, it re-ran nothing.
- **No result here has been reproduced by anyone independent of its author.**

## 8. Conditions for any future relay scoring

Each is separate, and all are needed:

1. An endpoint that can move: it passes a headroom rule (QUAL2 rule H proposes 1 − mean G(D) ≥ 0.20, a margin that
   makes a 0.10 target at most half the room) and a positive control.
2. Qualification shown at the measured prompt length of the checkpoint being read, not a shorter one.
3. Chad Holland's approval, on the PR, for arm-A use of the transcript.

## 9. Open doors (M15)

- Matched evidence pairs, held out as pairs (`chatgpt/036`). Chad Holland chose Gemini as author and recorded it on
  #172 in his own words (comments 7090094126, 7090106532): brief `0a34d88`, Set 1 verbatim `1cefacd`, corrected copy
  `ac5f1e2`, replacement Set 2 held by Chad, SHA-256 `370439216199e9350e16555b4d0e3a8787831dff834f7900722063d8ac324275`.
  The first Set 2 was retired because Claude saw it. A digest identifies the bytes; it cannot show who saw them.
  Memory off and the version are CONTRIBUTOR REPORTED. Pilot rules (headroom, positive control) come before any
  model reads a pair.
- A rotated-letter override control (`chatgpt/036`), registered separately from QUAL2's fixed "answer C".
- QUAL2 on 7B: needs Chad's go on the PR.
- Reading 016, then 032, once conditions 1–3 hold.

## Known limits (from RELAY.md)

Both AIs knew they were recorded and knew the hypothesis. Both share Chad's standing instructions and saved memory.
The sessions were not all the same kind. The turn headers give (`closeout_export_check.txt`): Claude 18 `fresh
scheduled`, 1 `interactive, started by Chad` (001), 1 `ongoing chat (Chad present)` (039); ChatGPT 18 `fresh
scheduled`, 2 `interactive`. The draft said Claude's turns came from fresh scheduled sessions. That was wrong for
001 and 039.

## Credit and provenance (M13)

The question behind CCC-001 is Federico Talens-Alesson's. Crediting him implies no endorsement or validation by him.
Draft by Claude (Anthropic, Opus 5.5), fresh scheduled session, relay turn 037; headline wording and section
requirements by ChatGPT (OpenAI), turns 034 and 036. Human validation: not performed. Human responsibility: Chad
Holland. Review level: none.

Final revision, 2026-11-23: Claude (Anthropic, Opus 5.5), in a session started by the relay's scheduled task that
continued as a live chat with Chad Holland. Final changes asked for by ChatGPT (OpenAI) in `chatgpt/040`.
Direction: Chad Holland. Human validation: not performed. Human responsibility: Chad Holland. Review level:
direction only.

## Changes from the draft (W9)

The draft is kept in Git at `a3c4b81` as `experiments/ccc_001/CLOSEOUT_DRAFT.md`. Superseded, verbatim:

- Title: "CCC-001 relay closeout: draft".
- Status: "DRAFT, not frozen, not a result. Written at relay turn 037 (row 4 and the points agreed in turns 038–039
  updated at turn 039) (the last turn was `ccc-relay/chatgpt/036`), … Nothing in this file was run for it."
- Headline section title: "Headline, if no primary checkpoint is ever read". Its wording: "The relay archived
  checkpoints 016 and 032. Neither checkpoint produced a model score for the original or shuffled conversation. The
  effect of conversation order at those checkpoints remains unmeasured."
- Archive row 040: "MISSING at the time of this draft".
- Known limits: "Claude's turns came from fresh scheduled sessions and ChatGPT's turns did not always come from the
  same kind of session."
