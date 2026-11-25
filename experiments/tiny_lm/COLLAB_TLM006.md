# TLM-006 collaboration: is seed 41's extra shared-phrase copying real?

**Status:** protocol and question, 2026-11-25. Nothing is registered, frozen or run. Chad Holland asked Claude in live
chat on 2026-11-25 to start a new line from TLM-005's open door (paraphrased). Claude chose the question. The rules
are TLM-005's ([COLLAB_TLM005.md](COLLAB_TLM005.md)) with the changes listed below.

## The question

TLM-005 ended INCONCLUSIVE because its two seeds disagreed ([RESULTS_TLM005.md](RESULTS_TLM005.md), Open). After the
prompt and end marker were masked, 4.05% of seed 41's eligible 50-byte windows occurred in two or more training
stories (r). The highest rate among ten 20-story blocks of real held-out stories was 2.6%. Seed 42's rate was 2.12%.
Those figures come from 20 samples per seed. **With 200 fresh samples per seed, is seed 41's multi-story rate
still above the real-story spread?**

- **Simplest rival (M14), sampling noise:** 20 samples were too few. TLM-005's drop-one test removed one sample of
  20, which says little about a fresh draw. With 200 samples, seed 41 sits inside the spread of real stories.
- **The other readings it can separate:** an excess in seed 41 only (a property of one trained model), in both
  seeds (the recipe), or in neither (the rival).

## What changes from TLM-005

- **Branches:** `claude/tlm-006-*` and `chatgpt/tlm-006-*`. Notes: `tlm006/<claude|chatgpt>/<NNN>`.
- **The attack comes before the freeze.** TLM-005 froze before ChatGPT's attack arrived (FREEZE_TLM005.md). Here, the
  registration is not frozen until ChatGPT has posted an attack note, or has had 36 hours to do so after being asked.
- **Authority.** Chad's delegation for TLM-005 (PR #179 comment 7141779917) does not extend to this line. Freezing,
  the confirmatory run, merging and tagging wait for his own words on this line's PR.
- **Stopping:** the question is answered and closed (W8), Chad posts `COLLAB STOP` on the PR, or 2026-12-20,
  whichever comes first.

## Known limits

The same as TLM-005's: shared instructions mean that agreement between the AIs is not independent (M10). Claude wrote
the code under test and TLM-001 to TLM-005.

## Provenance (M13)

Direction: Chad Holland, 2026-11-25. Question and protocol: Claude (Anthropic, Opus 5.5), from TLM-005's open door.
TLM-005's rules were shaped by ChatGPT (OpenAI GPT-6, Codex), notes tlm005/chatgpt/002 and 004. Human validation: not
performed. Human responsibility: Chad Holland.
