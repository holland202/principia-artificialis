# Freeze record: REGISTRATION_TOR001.md

**Frozen file:** [`REGISTRATION_TOR001.md`](REGISTRATION_TOR001.md) as committed at `3dbfed0`. SHA-256
`84c35a2c73ad900e00c521ae4655d1cd8d8b658e4d8ccb8663dbdf7376785ad4`, the same hash ChatGPT checked in note
`tor001/chatgpt/006`. The file's own status line still reads "DRAFT, NOT FROZEN". This record supersedes it, because
the frozen file is never edited.

**Owner approval:** Chad Holland on PR #186, 2026-11-26T15:40Z
([comment 7196600302](https://github.com/holland202/principia-artificialis/pull/186#issuecomment-7196600302)). In
first person, signed with his name and not in a note format, he approved the freeze at `3dbfed0` and said he will
decide on the run separately. That comment was posted from the `holland202` account, which ChatGPT's notes also use.
Claude reads it as Chad's own words because it is in the first person, signed and not in note format. Recorded by
Claude (Anthropic, Opus 5.5).

**At the moment of freezing:**
- No field had been generated.
- No code existed.
- Nothing had been trained or run.

## The attack step happened before the freeze (W5)

ChatGPT (OpenAI, Codex) attacked the draft in note 002 (comment 7195140245) and checked the revisions in notes 004
(7196003761) and 006 (7196069671). Every point was adopted before the freeze. The revisions are listed in the frozen
file's own "Revisions before freeze" section.

## Still open

- **The run (T6)** waits for Chad Holland's separate decision on PR #186.
- **The post's URL** for SOURCE_POST.md has not been supplied yet. The source record stands on the screenshot hash.
- **Building the code (T4) comes next.** It is committed before any run. It must show ChatGPT's interface condition:
  `test.npy` is opened only after every arm has finished fitting. Then the first frames of each field are looked at
  (C-SYNTH).

## What is frozen

Everything in the frozen file:
- fields F1 to F3 and their parameters;
- the training and test design, and the input interface;
- arms L4, L*, T2, K4, E2 and NP;
- P1 to P6;
- the precedence table, the gates and the diagnostics.

Errors found later are recorded as dated deviations here or in the results, never by editing the frozen file.
