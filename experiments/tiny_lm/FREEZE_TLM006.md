# Freeze record: REGISTRATION_TLM006.md

**Frozen file:** [`REGISTRATION_TLM006.md`](REGISTRATION_TLM006.md) as committed at `834ff9b`. SHA-256
`681299b3f82920b46105553cfdb18740fcca819ed2b045a9e148225438975a86`, the same hash ChatGPT checked in note
`tlm006/chatgpt/006`. The file's own status line still reads "DRAFT, NOT FROZEN". This record supersedes it, because
the frozen file is never edited.

**Owner approval:** Chad Holland on PR #185, 2026-11-26T15:40Z
([comment 7196587042](https://github.com/holland202/principia-artificialis/pull/185#issuecomment-7196587042)). In
first person, signed with his name and not in a note format, he approved the freeze at `834ff9b` and said he will
decide on the confirmatory run separately. That comment was posted from the `holland202` account, which ChatGPT's
notes also use. Claude reads it as Chad's own words because it is in the first person, signed and not in note format.
Recorded by Claude (Anthropic, Opus 5.5).

**At the moment of freezing:**
- No new sample had been generated.
- No reference story beyond valid stories 0 to 199 had been read.
- No weights had been loaded or retrained.
- No driver code existed.

## The attack step happened before the freeze (W5)

ChatGPT (OpenAI, Codex) attacked the draft in note 002 (comment 7195139725) and checked the revisions in notes 004
(7196002770) and 006 (7196068674). Every point was adopted before the freeze. The revisions are listed in the frozen
file's own "Revisions before freeze" section.

## Not authorized by this freeze

- **The confirmatory run (T7).** It waits for Chad Holland's separate decision on PR #185.
- **The weights.** Whether TLM-004's `t41.pt` and `t42.pt` still exist (Source A) or must be retrained (Source B) is
  still open.

Building the driver and the pure decision function (T5) comes next. It is committed before any run, together with the
R fixture. ChatGPT's blind decision-table cases (T6) are welcome before the run, with SHA-256 values only on GitHub.

## What is frozen

Everything in the frozen file:
- inputs, generation seeds 5020 to 5219, and reference stories 200 to 2,399;
- gates G0 to G3 and the per-model scope labels;
- the measures, and the frozen sensitivity analyses S1 and S2;
- the decision rule and the precedence table;
- the controls and the sabotage.

Errors found later are recorded as dated deviations here or in the results, never by editing the frozen file.
