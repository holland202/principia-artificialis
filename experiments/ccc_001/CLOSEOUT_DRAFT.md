# CCC-001 relay closeout: draft

**Status:** DRAFT, not frozen, not a result. Written at relay turn 037 (row 4 and the points agreed in turns 038–039 updated at turn 039) (the last turn was `ccc-relay/chatgpt/036`),
from the files on `claude/ccc-001-rendering` at `741b433`. The relay ends at turn 040, at a `RELAY STOP` from Chad
Holland, or on 2026-12-05. This file is revised then from that export. Proposed in `ccc-relay/claude/033`, agreed in
`ccc-relay/chatgpt/034`, contents asked for in `chatgpt/034` and `chatgpt/036`. Nothing in this file was run for it.
Every number is copied from the committed log it cites.

## Headline, if no primary checkpoint is ever read

Wording proposed by ChatGPT (OpenAI) in `ccc-relay/chatgpt/034`:

> The relay archived checkpoints 016 and 032. Neither checkpoint produced a model score for the original or
> shuffled conversation. The effect of conversation order at those checkpoints remains unmeasured.

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
| 040 | secondary | — | MISSING at the time of this draft | — |

Edited turns 0 in the 016, 024 and 032 snapshot runs. Each later snapshot's bodies equal every earlier one's. The 024 and 032 shuffle
permutations equal the synthetic ones printed before those turns existed.

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

Both AIs knew they were recorded and knew the hypothesis. Claude's turns came from fresh scheduled sessions and
ChatGPT's turns did not always come from the same kind of session. Both share Chad's standing instructions and
saved memory.

## Credit and provenance (M13)

The question behind CCC-001 is Federico Talens-Alesson's. Crediting him implies no endorsement or validation by him.
Draft by Claude (Anthropic, Opus 5.5), fresh scheduled session, relay turn 037; headline wording and section
requirements by ChatGPT (OpenAI), turns 034 and 036. Human validation: not performed. Human responsibility: Chad
Holland. Review level: none.
