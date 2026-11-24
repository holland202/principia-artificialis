# TLM-005 results (development run, PROVISIONAL): after masking the prompt and end marker, the excess copying is gone in seed 42 and multi-story in seed 41, so the registered verdict is INCONCLUSIVE

**Status:** run as frozen ([REGISTRATION_TLM005.md](REGISTRATION_TLM005.md) at `d8800f5`,
[FREEZE_TLM005.md](FREEZE_TLM005.md)). Code `tlm005_attrib.py` committed at `66966b7` before any run (SHA-256
`93948c3c…0590`). **VERDICT INCONCLUSIVE as registered.** Provisional: ChatGPT's blind fixtures (T2) have not been
run. SELF-TESTED by Claude, who wrote the code. Linux container CPU, 2 processes, 2 m 18 s. S25 NOT VALIDATED.

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
3. **No blind fixture has run.** The anti-vacuity evidence so far is Claude's own development fixtures, which Claude
   built knowing the code. They are not blind.
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
| Blind fixtures (T2) | as registered | **NOT RUN** (they do not exist yet) |

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

## What this does not show

Any match found here shows verbatim overlap with this training slice, not how the model learned it. Nothing about memorisation in general, other seeds, larger models or other prompts. The verdict is provisional until
the blind fixtures run, and it is self-tested.

## Open (M15)

- T2 blind fixtures (ChatGPT), then their run on code `93948c3c…`, needs Chad Holland's go on PR #179.
- More samples per seed would decide seed disagreement; that needs its own registration.
- Near-duplicate stories as one document (unrun door in the registration).

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) wrote the code, ran it and wrote this, under a registration revised
after ChatGPT (OpenAI GPT-6, Codex) note tlm005/chatgpt/002 → human validation: not performed → direction and freeze
approval: Chad Holland, 2026-11-24 → human responsibility: Chad Holland. Review level: direction only.*
