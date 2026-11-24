# Freeze record: REGISTRATION_TLM005.md

**Frozen file:** [`REGISTRATION_TLM005.md`](REGISTRATION_TLM005.md) as committed at `d8800f5`, SHA-256
`4ba3449fa6a9292758e82c35553e3927012026007179175b9bfedf840e10b0fa`.
**Owner approval:** Chad Holland, on PR #179 in his own words, 2026-11-24T18:56:33Z
([comment 7141368092](https://github.com/holland202/principia-artificialis/pull/179#issuecomment-7141368092)),
replying to note `tlm005/claude/003`. Claude reads that comment as approving the draft as written and the next
steps: freeze, build the code (T3), and the development run (T4). Recorded by Claude (Anthropic, Opus 5.5).
**At the moment of freezing:** no document frequency had been computed, no code had been built, and the training
slice had not been fetched in this session.

## Disclosed before anything runs

- **The attack step (W5) did not happen before the freeze.** Note 003 asked ChatGPT to attack the draft. ChatGPT had
  not posted on PR #179 since note 002 (2026-11-23T03:22Z), about 39 hours before the freeze. Chad Holland chose to
  proceed. ChatGPT's later objections are answered as dated deviations, never by editing the frozen file.
- **The blind fixtures (T2) do not exist yet.** The development run reports the registered outcome on the 40
  samples. That outcome stays **provisional** until ChatGPT's fixtures, run against code whose hash is committed
  before the fixtures are shown, give the registered anti-vacuity results. The fixture run needs Chad Holland's go on
  this PR.
- **The registration's own open questions** (maximum-of-10 rule, the public fixture requirements) were put to
  ChatGPT in note 003 and remain unanswered.

## What is frozen

Inputs, window grid, masks, the df classes U/R/B/N, the longest-match measure, the fidelity check, the noise and
decision rule, the five outcomes, the sabotage switches and the public fixture requirements, all as written at
`d8800f5`. The frozen file is never edited. Errors found later are recorded as dated deviations here or in the
results.

## Provenance (M13)

Freeze record by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-24. Human validation: not
performed. Human responsibility: Chad Holland.

## Deviations and errors found after the freeze (dated; the frozen file is unchanged)

- **2026-11-24, ChatGPT note `tlm005/chatgpt/004`** (comment 7141477002, posted 19:01Z, after the freeze at
  `0668774` and before Claude's results note). It reviewed the draft at `d8800f5` and asked for changes before a
  freeze. The freeze had already happened, so each point is recorded here.
  1. **Missing row in the outcome table.** If neither u nor r is above its block maximum but the total masked copy
     rate is, no registered row applies. The code gives INCONCLUSIVE in that case (`tlm005_attrib.py` lines 248–261:
     fidelity first, then B, seed disagreement and drop-one, then the substantive rows, and a final `else` that
     gives INCONCLUSIVE). The table now reads as having that fallback. The development run does not hit this case:
     `excess u no | r disagree | masked copy rate no`. A decision-table unit test for it is NOT RUN. The decision
     is inline in `main`, and moving it into a testable function would change the code hash given for the blind
     fixtures. That waits for Chad Holland's go.
  2. **Wording.** The row "NO EXCESS" is read as "no excess detected by this rule". A rate at or below the block
     maximum does not show that the masks explain TLM-004's difference.
  3. **Before/after gap**, now reported in the results: each seed's copy rate minus block 1's, unmasked and masked.
  4. **Scope.** Even a 200-byte match together with a U excess shows only verbatim overlap with this slice, not how
     the model learned it.
  5. **T2 public requirement added:** the common-phrase control must give R ≥ 1 on the eligible grid as well as
     U = 0, so an empty control cannot pass.
- **Note numbering.** Claude's results note was headed `tlm005/claude/004`, but ChatGPT's `004` was posted first.
  Claude's note is `005` in the sequence. The comment is left as posted (M12).
