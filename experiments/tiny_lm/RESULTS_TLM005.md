# TLM-005 results (blind controls passed; DONE): after masking the prompt and end marker, the excess copying is gone in seed 42 and multi-story in seed 41, so the registered verdict is INCONCLUSIVE

**Status:** run as frozen ([REGISTRATION_TLM005.md](REGISTRATION_TLM005.md) at `d8800f5`,
[FREEZE_TLM005.md](FREEZE_TLM005.md)). Code `tlm005_attrib.py` committed at `66966b7` before any run (SHA-256
`93948c3c…0590`). **VERDICT INCONCLUSIVE as registered.** The blind controls (T5) passed when ChatGPT ran them on 2026-11-24
(CONTRIBUTOR REPORTED, section below), so the verdict is no longer provisional. Development run SELF-TESTED by Claude,
who wrote the code. Linux container CPU, 2 processes, 2 m 18 s. S25 NOT VALIDATED.

Raw output: [`tlm005_dev_run.txt`](../../results/tiny_lm/005/tlm005_dev_run.txt),
[`tlm005_dev.json`](../../results/tiny_lm/005/tlm005_dev.json) (every window's class, df and raw story count),
[`tlm005_dev_run_nomask.txt`](../../results/tiny_lm/005/tlm005_dev_run_nomask.txt),
[`dev_fixtures_run.txt`](../../results/tiny_lm/005/dev_fixtures_run.txt),
[`dev_fixtures_run_dfany.txt`](../../results/tiny_lm/005/dev_fixtures_run_dfany.txt).

## What could have gone wrong, first

1. **The registered outcome is INCONCLUSIVE.** The seeds disagree on the multi-story rate r: seed 41 is above every
   reference block, and seed 42 is not.
2. **The attack step did not happen before the freeze** (FREEZE_TLM005.md). ChatGPT has not reviewed the
   registration or this code.
3. **The blind controls are CONTRIBUTOR REPORTED.** ChatGPT wrote and ran them. Claude has not seen the fixture text
   or the answer key and cannot rerun them. The private key left one longest-match value unscored. Claude's own
   development fixtures are not blind.
4. **"Duplicated stories count once" cannot be exercised on this slice.** The only exact duplicates among the 256,019
   pieces are 12 copies of `\n\n` (2 bytes). There are 256,008 distinct pieces. Collapsing changes no window's df
   here. A fixture made only of text cannot test it.
5. **Reporting deviation, longest match:** values below 99 bytes are lower bounds, not exact. The code finds matches
   by extending around matching grid windows, which finds every match of 99 bytes or more. Texts with no matching
   window are reported as `<99`. The registered summary (the share of texts ≥ 200 bytes) is unaffected.

## Raw output (`results/tiny_lm/005/tlm005_dev_run.txt`, excerpt, verbatim)

```
training stories 256019 unique by sha256 256008
distinct windows searched 3532
FIDELITY HELD {'t41': '30/273', 't42': '24/260', 'block01': '28/358'} want {'t41': '30/273', 't42': '24/260', 'block01': '28/358'}
t41: E 247 U 3 R 10 B 0 | u 0.0121 r 0.0405 b 0.0000 copy 0.0526 | longest>=200 share 0.00
t42: E 236 U 4 R 5 B 0 | u 0.0169 r 0.0212 b 0.0000 copy 0.0381 | longest>=200 share 0.00
block01: E 338 U 7 R 8 B 0 | u 0.0207 r 0.0237 b 0.0000 copy 0.0444 | longest>=200 share 0.00
block maxima {'u': 0.0354, 'r': 0.026, 'b': 0.0, 'copy': 0.0591, 'share200': 0.0}
t41 drop-one r min 0.0373 max 0.0442
t42 drop-one r min 0.0135 max 0.0233
excess u no | r disagree | masked copy rate no | B total 0
longest-match share >= 200 above block maximum in both seeds: False (agrees with SINGLE-STORY only if True)
VERDICT INCONCLUSIVE
```

The longest match in any model text is 92 bytes (seed 42). Per-text values are in the log.

## Controls

| Control | Required | Result |
|---|---|---|
| Fidelity (C-BUILD) | masks off: 30/273, 24/260, 28/358 | **HELD**, exact |
| B after masking | 0 | **0** (unmasked: 1 window in seed 41, the one carrying end-marker bytes) |
| `--no-mask` | must change E (20 opening windows per seed) | E 247 → 273 and 236 → 260 (20 opening + 6 and 4 end-marker windows) |
| `--df-any` | must turn common-phrase U above 0 | Claude's dev fixture 2: U 0 → **2** |
| Planted single-story passage (Claude's dev fixture 1, 150 bytes, count 1 in the slice) | U ≥ 1, longest ≥ 150 | U **3**, longest **150** |
| Common phrases only (dev fixture 2; counts 5,087 and 28 in the slice) | U = 0 | U **0**, R 2 |
| Blind fixtures (T2/T5, ChatGPT) | as registered and per note 004 | **8 of 8 sealed checks matched** (CONTRIBUTOR REPORTED) |

## What this shows, on these 40 samples

- **No single-story excess.** The share of windows found in exactly one training story (u: 0.0121 and 0.0169) is
  inside the range of real held-out stories (block maximum 0.0354). No model text has a verbatim match of 99 bytes
  or more.
- **After the masks, the overall copy rate is inside the real-story spread:** 0.0526 and 0.0381 against a block
  maximum of 0.0591.
- **Seed 41 alone has a multi-story excess:** r 0.0405 against a block maximum of 0.026, and above it on every
  drop-one. Seed 42 does not (0.0212).
- **Post-hoc, not registered:** with the masks off, the copied windows fall from 30 to 13 (seed 41) and from 24 to 9
  (seed 42). Most of TLM-004's flagged excess sat in the prompt window and the end-marker window. With masks off,
  the block maximum is 0.1058, which already exceeds seed 42's 0.0923
  ([`tlm005_dev_run_nomask.txt`](../../results/tiny_lm/005/tlm005_dev_run_nomask.txt)). One 20-story reference was
  too small to call TLM-004's difference an excess.

## Before and after the masks (added after ChatGPT note 004; computed from `tlm005_dev.json` and TLM-004's counts)

```
t41 minus block01 copy rate: unmasked +0.0317 masked +0.0083
t42 minus block01 copy rate: unmasked +0.0141 masked -0.0062
```

"Inside the spread" means *no excess detected by this rule* (maximum of 10 blocks). It does not show that the masks
explain the whole of TLM-004's difference.

## Blind controls (T5), run by ChatGPT

Authority: Chad Holland on PR #179 in his own words
([comment 7141840265](https://github.com/holland202/principia-artificialis/pull/179#issuecomment-7141840265)), after
ChatGPT asked for it in note `tlm005/chatgpt/010`. Fixture commitments: real-slice `1ed6d540…` and private bundle
`af0d1ca5…` (note 008), synthetic duplicate control `799b1710…` (note 007). Output as posted in note
`tlm005/chatgpt/011` ([comment 7141873152](https://github.com/holland202/principia-artificialis/pull/179#issuecomment-7141873152));
HTML entities in the relayed comment decoded to braces:

```
masked
FIXTURE real_slice.txt text 1: E 3 U 3 R 0 B 0 N 0 longest 155 | U windows raw story counts [1, 1, 1]
FIXTURE real_slice.txt text 2: E 1 U 0 R 1 B 0 N 0 longest 50 | U windows raw story counts []
FIXTURE real_slice.txt text 3: E 1 U 0 R 0 B 0 N 1 longest <99 | U windows raw story counts []
--df-any
FIXTURE real_slice.txt text 1: E 3 U 3 R 0 B 0 N 0 longest 155 | U windows raw story counts [1, 1, 1]
FIXTURE real_slice.txt text 2: E 1 U 1 R 0 B 0 N 0 longest 50 | U windows raw story counts [11]
FIXTURE real_slice.txt text 3: E 1 U 0 R 0 B 0 N 1 longest <99 | U windows raw story counts []
--no-mask
FIXTURE real_slice.txt text 1: E 4 U 3 R 0 B 0 N 1 longest 155 | U windows raw story counts [1, 1, 1]
FIXTURE real_slice.txt text 2: E 2 U 0 R 1 B 0 N 1 longest 50 | U windows raw story counts []
FIXTURE real_slice.txt text 3: E 3 U 0 R 1 B 0 N 2 longest <99 | U windows raw story counts []
synthetic False 1 {'eligible': 2, 'U': 2, 'R': 0, 'longest': 127, 'raw_per_U': [2, 2]}
synthetic False 2 {'eligible': 1, 'U': 0, 'R': 1, 'longest': 50, 'raw_per_U': []}
synthetic True 2 {'eligible': 1, 'U': 1, 'R': 0, 'longest': 50, 'raw_per_U': [2]}
sealed checks 8 / 8 [True, True, True, True, True, True, True, True]
```

Claude's check against the public requirements, without the fixture text (VERIFIED FROM SOURCE against the posted
output only):
- The planted single-story text gives U ≥ 1 (3).
- The common-phrase text gives U = 0 and R ≥ 1 (note 004's addition).
- `--df-any` turns that text's U above 0 (1, with 11 raw stories).
- `--no-mask` changes E (3 texts: 3→4, 1→2, 1→3).
- In the synthetic corpus, duplicated stories give 2 raw hits per window and count once: U, not R. This was run by
  calling the scoring functions on a supplemental corpus, not through the CLI (disclosed in note 007). It covers the
  requirement the real slice could not exercise.

## Closeout (W8): DONE for the scope below

- **Scope.** `tlm005_attrib.py` attributes 50-byte copied windows of TLM-004's 40 committed samples and 200 real
  held-out stories to one or several TinyStories training stories, and gives the registered outcome.
- **Gate both ways (M3).** The fidelity gate reproduces TLM-004's counts exactly. `--no-mask` and `--df-any` move
  their numbers. The blind controls passed, 8 of 8 (CONTRIBUTOR REPORTED).
- **Cold clone.** A fresh clone of `4cb8a9e` with the training slice downloaded again (hashes OK) gave run output
  identical to `tlm005_dev_run.txt`, apart from the JSON path line, and the same JSON SHA-256
  `779dd9fc464f532783b4037bdcfcbeebc469b975daa6ebe623d2e95fe117ec0f`. No untracked state was used.
- **No known defect inside the scope.** Limits outside it: longest-match values under 99 bytes are lower bounds; the
  outcome table lacks a row for ChatGPT's counterexample, which the code sends to INCONCLUSIVE (FREEZE_TLM005.md).
- **DONE:** code `tlm005_attrib.py` at `66966b7`, SHA-256
  `93948c3c4f96ff7c67e006f24f5096b7a92319ade5a53aacbe132effa7a10590`, md5 `bf1a1b471cb5531fd99aab314c244025`.
- **The claim:** TLM-004's flagged excess copying is **not** shown to be single-story copying. No sample has a
  verbatim match of 99 bytes or more. Post-hoc, not registered: most of the flagged excess sat in the prompt and end-marker windows. Whether
  seed 41's multi-story excess is real stays open, because the seeds disagree.

## What this does not show

Any match found here shows verbatim overlap with this training slice, not how the model learned it. Nothing about memorisation in general, other seeds, larger models or other prompts. The development run is
self-tested; the blind controls were run by ChatGPT, not independently of Chad Holland's shared instructions (M10).

## Open (M15)

- The door this line ends with: seed 41's multi-story excess (r 0.0405 against a block maximum of 0.026) is the one
  unexplained number. More samples per seed, under a new registration, would settle it.

- Near-duplicate stories as one document (unrun door in the registration).

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) wrote the code, ran it and wrote this, under a registration revised
after ChatGPT (OpenAI GPT-6, Codex) note tlm005/chatgpt/002 → human validation: not performed → direction and freeze
approval: Chad Holland, 2026-11-24 → human responsibility: Chad Holland. Review level: direction only.*

## Changes (W9)

- **2026-11-24, closeout:** status changed from PROVISIONAL to DONE after the blind controls passed. Edited: the title, the
  status paragraph, item 3 of "What could have gone wrong", the blind-fixture row of Controls, "What this does not
  show" and Open. Added: Blind controls (T5) and Closeout (W8). Superseded wording, verbatim: title "(development run,
  PROVISIONAL)"; status "Provisional: ChatGPT's blind fixtures (T2) have not been run."; item 3 "**No blind fixture
  has run.** The anti-vacuity evidence so far is Claude's own development fixtures, which Claude built knowing the
  code. They are not blind."; Controls row "**NOT RUN** (they do not exist yet)". Edit by Claude (Anthropic, Opus
  5.5) under Chad Holland's delegation (PR #179 comment 7141779917).
