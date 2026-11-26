# TLM-005 collaboration: Claude and ChatGPT on one question

**Status:** protocol and question, 2026-11-23. Nothing is registered or run. Chad Holland asked for Claude and
ChatGPT to work this way on a new line of inquiry and left the choice of question to Claude (live chat, 2026-11-23,
paraphrased). This is the second Claude–ChatGPT line, after the CCC-001 relay ([RELAY.md](../ccc_001/RELAY.md)).
It follows Chad's GitHub coordination protocol, with one change: the work is shared, not split strictly by role.

## The question

TLM-004's token model copies more than real stories do. 10.99% (seed 41) and 9.23% (seed 42) of its generated
50-byte spans occur verbatim in the training text, against 7.82% for real held-out stories
([RESULTS_TLM004.md](RESULTS_TLM004.md), limit 1). **Is that excess memorisation of particular training stories,
or formula shared by many stories** ("Once upon a time, there was a little girl named …", plus the prompt
itself)? TLM-004 listed this as its first unrun next step.

- **Simplest rival (M14):** formula. If every excess copied span is common in the training text, or overlaps the
  prompt, then the model copies no more than a fluent writer of this genre would.
- **What would tell them apart (to be registered, not decided here):** for each copied span, how many training
  stories contain it; spans found in exactly one story; the longest verbatim match per sample; all with the
  prompt span excluded, and the same measures on real held-out stories as the reference.
- **Anti-vacuity (M3):** the instrument must flag memorised text when it is there. A fixture with planted
  single-story passages has to be detected, and one with only common phrases must not be.
- **Cost:** no training. The 40 samples and both weights files are committed under `results/tiny_lm/004/runs/`.
  The training slice is `data/v2_train_200MB.txt`: the first 209,715,200 bytes of `TinyStoriesV2-GPT4-train.txt`
  (CDLA-Sharing-1.0), checked against `results/tiny_lm/001/DATA_SHA256.txt` (REGISTRATION_TLM001.md).

## How the two work

- **One shared task list** in the PR description, kept current by whoever changes it. Either AI may take a task.
- **Author is never tester.** Whoever writes a piece of code does not write or see its independent tests. Blind
  fixtures are committed as SHA-256 digests only. Their text goes to Chad Holland, never to the code's author,
  until the registered run.
- **Each AI pushes only to its own branches** (`claude/tlm-005-*`, `chatgpt/tlm-005-*`) and reviews the other's
  PRs on GitHub.
- **Notes** are PR comments in Chad's format:

  ```yaml
  note: tlm005/<claude|chatgpt>/<NNN>     # NNN counts all notes in this line: 001, 002, ...
  by: <model>; session: <fresh scheduled | interactive>; human review: <none | level>
  re: "<what this answers, with the commit SHA>"
  verdict: <SHORT_OUTCOME>
  next: "<who does what next>"
  ```

  The body holds pasted output, evidence labels (VERIFIED FROM SOURCE, SELF-TESTED, NOT RUN, CONTRIBUTOR
  REPORTED, REFUTED) and a one-line **EN:** summary for Chad.
- **Pace:** each side runs about twice a day. If the newest note is your own and nothing waits on you, post
  nothing.
- **Disagreement becomes a test.** After two rounds without resolution, record CONTESTED and ask Chad.

## What waits for Chad Holland

Freezing a registration, any blind or confirmatory run, merging and tagging, all in his own words on the PR. A
decision relayed by the other AI is PENDING until he says it himself. Development runs, fixes and documentation
inside this question go ahead.

## Stopping

The line ends when the question is answered and closed (W8), on a PR comment from Chad containing
`COLLAB STOP`, or on 2026-12-07, whichever comes first.

## Known limits

Both AIs share Chad's standing instructions and saved memory. Agreement between them is not independent
validation (M10). Claude wrote TLM-001 to TLM-004, so Claude is not independent of the code under test.

## Provenance (M13)

Direction: Chad Holland, 2026-11-23. Question chosen and protocol written by Claude (Anthropic, Opus 5.5), from
Chad's GitHub coordination protocol and the CCC-001 relay. Human validation: not performed. Human
responsibility: Chad Holland.
