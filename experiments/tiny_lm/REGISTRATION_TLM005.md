# TLM-005 registration (DRAFT): is TLM-004's excess copying single-story or shared formula?

**Status:** DRAFT, NOT FROZEN, NOTHING BUILT OR RUN. Written for ChatGPT's attack (T1 in PR #179). Changes before
the freeze are new commits on this file, so the history shows them. The freeze waits for Chad Holland's own words on
PR #179. **Authors:** Direction: Chad Holland, 2026-11-23. Design: Claude (Anthropic, Opus 5.5), revising its note
tlm005/claude/001 after ChatGPT (OpenAI GPT-6, Codex) note tlm005/chatgpt/002. Human review: none.

## Question

TLM-004's committed samples copy more 50-byte windows from the training text than real held-out stories do (0.1099
seed 41, 0.0923 seed 42, 0.0782 reference). **After the prompt is excluded, is the excess in windows found in one
training story, or in windows found in many?**

- **Simplest rival (M14), formula:** the excess sits in the prompt window and in windows that many stories share.
- **What this cannot show:** a window found in one story is not proof of memorisation. A formula can occur once in
  this slice, and a near-duplicate story is counted as a different story. The longest-match measure (M3 below) is
  the second line of evidence, and the result will say "single-story", never "memorised", unless both agree.

## Inputs (fixed; no generation, no training)

- **Model text:** the 40 committed samples, `results/tiny_lm/004/runs/t41.samples.txt` and `t42.samples.txt`, split
  on `\n\n=====\n\n` (20 each).
- **Reference:** the first 200 stories of `data/v2_valid.txt`, split on `<|endoftext|>` exactly as `gencheck.py`
  does, as 10 consecutive blocks of 20. Block 1 is TLM-004's reference.
- **Training slice:** `data/v2_train_200MB.txt`, SHA-256 checked against `results/tiny_lm/001/DATA_SHA256.txt`
  before use, split on `<|endoftext|>` into stories. Exact duplicate stories are collapsed (by SHA-256 of the story
  bytes) for document frequency; raw counts are reported too.

## Measures

1. **Window grid:** `gencheck.py`'s, unchanged: 50 bytes, stride 50, offset 0.
2. **Masks, applied to model and reference alike:** drop any window that overlaps the first 16 bytes after leading
   whitespace (the prompt "Once upon a time" in model text; the same opening bytes in real stories), and any window
   that contains bytes of a `<|endoftext|>` the generator appended. E = eligible windows left.
3. **Document frequency** df(w) = number of distinct training stories containing w. Classes: U (df = 1), R (df ≥ 2),
   B (in the concatenated slice but df = 0, i.e. only across a story boundary), N (not found).
   Rates u = U/E, r = R/E, b = B/E. Then u + r + b is the masked copy rate.
4. **Longest match** per text: the longest substring found inside a single training story (prompt bytes excluded),
   in bytes. Reported per text; summarised as the share of texts with a longest match ≥ 200 bytes.

## Fidelity check (C-BUILD, before any verdict)

With masks off and df ignored, the code must reproduce TLM-004's counts exactly: 30 / 273, 24 / 260 and 28 / 358
(rates 0.1099, 0.0923, 0.0782). If not, stop and report. B must be 0 after masking; if not, it is reported as its own
row and no verdict is given.

## Noise and decision rule (C-NOISE, C-STAT)

The search is deterministic. The variation is in which 20 stories are drawn, so the 10 reference blocks give the
spread. A model rate shows **excess** when it is above the **maximum** of the 10 block rates, in both seeds, and stays
above it when any one of the 20 model texts is dropped (all 20 drop-one subsets, per seed).

## Registered outcomes (exactly one is reported)

| Outcome | u excess | r excess |
|---|---|---|
| SINGLE-STORY | yes | no |
| FORMULA | no | yes |
| MIXED | yes | yes |
| NO EXCESS (prompt and ending explain it) | no | no, and the masked copy rate is not above the block maximum |
| INCONCLUSIVE | seeds disagree, or an excess fails the drop-one test, or B ≠ 0 |

Longest match is reported alongside and labelled agreeing or not: "agrees with SINGLE-STORY" needs the ≥ 200-byte
share above the block maximum in both seeds.

## Anti-vacuity (M3) and sabotage

- **Blind fixtures (T2, ChatGPT; text to Chad only, SHA-256 on GitHub):** public requirements only. A text with a
  planted passage of at least 100 bytes from one distinct training story, outside the opening bytes, must give U ≥ 1
  and a longest match at least the passage length. A text of phrases each in two or more stories must give U = 0.
  Duplicated stories must count once. Claude, who writes the code, never sees fixture text.
- **Sabotage switches:** `--no-mask` must change E on the 40 samples (20 opening windows per seed);
  `--df-any` (any match counts as df = 1) must turn the common-phrase fixture's U above 0.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | NOT RUN estimate: about 4,100 windows searched in 200 MB, minutes on one CPU. Counts printed first. |
| Noise | Deterministic search; sampling spread from 10 reference blocks. |
| Statistics | No p-value; maximum-of-10 rule, both seeds, drop-one. |
| Evidence | Numbers pasted from the script's output. |
| Independence | Code SELF-TESTED by Claude; blind fixtures by ChatGPT; not independent of Chad's shared instructions (M10). |
| External | TinyStories V2 (CDLA-Sharing-1.0). |
| Device | Linux container CPU. S25 NOT VALIDATED. |
| Verdict code | Rule above, coded fail-closed: any missing count gives INCONCLUSIVE. |
| Exploration | None on training data. Window counts on the samples alone (273, 260; 20 opening windows each; 6 and 4 with appended end-marker bytes) were computed for this draft. |
| Held-out | Thresholds fixed here before any df is computed. |
| Generated inputs | The 40 samples are TLM-004's, committed and unedited. |
| People's data | No. |
| Design | Observational re-analysis of fixed outputs; no causal claim about training. |

## Unrun door

- Near-duplicate stories (for example, 90% overlap) as one document; a TLM-003 byte-model comparison.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) drafted, revising after ChatGPT (OpenAI GPT-6, Codex) note 002 →
human validation: not performed → human editing/curation: direction by Chad Holland, 2026-11-23 → human
responsibility: Chad Holland. Review level: none.*
