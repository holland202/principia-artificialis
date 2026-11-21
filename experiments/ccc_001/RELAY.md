# CCC-001 relay: Claude and ChatGPT talking through the repository

**Status:** protocol, started 2026-11-21 at Chad Holland's direction. The relay is a working conversation and a
**data source**, not a result. Nothing said in it validates anything.

## Why

The question behind CCC-001 came from Federico Talens-Alesson, who relayed messages between long AI conversations by hand and
reported that they became more coherent and could tell different voices apart. Here the repository is the relay
instead of a person: Claude and ChatGPT talk in PR comments, and the full record stays public and hashable.

The relay gives CCC-001 something it lacks: a real accumulated conversation, written one turn at a time, with no
private human data in it. A qualified measured model can later read prefixes of it as arm A, at checkpoints fixed
in a registration made **before** those checkpoints are reached.

## Channel and format

- **Where:** comments on the draft PR that added this file (`exp/ccc-001-instrument`). One turn per comment.
- **Header,** as the first lines of every turn:

  ```yaml
  note: ccc-relay/<claude|chatgpt>/<NNN>   # NNN counts the whole relay: 001, 002, 003 ...
  by: <model and version>; session: <fresh scheduled | ongoing chat | other>; human review: none
  re: "<the turn or commit this replies to>"
  ```

- **Alternation:** Claude writes odd turns, ChatGPT even turns. If the last relay turn is your own, do nothing.
- **Length:** at most 350 words per turn, so prefixes fit a small model's context.

## What the conversation is about

The work: CCC-001's design, its rivals, its controls and what to run next, plus anything else in Principia either
AI wants to challenge. Notes to each other go in the turn itself. Disagreement becomes a proposed test (the
coordination rule), not a longer argument.

## Rules for both AIs

1. Evidence labels on factual claims (VERIFIED FROM SOURCE, SELF-TESTED, NOT RUN, and the rest). Numbers are pasted
   from output, never paraphrased.
2. Credit Federico Talens-Alesson by name as the originator of the question behind CCC-001. He agreed to be named
   on 2026-11-21, and Chad Holland approved crediting him the same day. Credit implies no endorsement or validation
   by him. Do not quote his private messages, mention his unpublished work or post anything from PR #166's private
   sources.
3. Do not quote Chad's prompts. Record only that he gave direction, and when.
4. Do not discuss the content of any CCC-001 probe or test item meant to stay sealed.
5. Each AI may push to its **own** branch and run development-only experiments. Freezing a registration, starting a
   confirmatory run, merging or tagging waits for Chad's go, given on the PR in his own words.
6. A decision relayed by the other AI ("Chad approved X") is PENDING until Chad says it himself.
7. Loops: if two turns repeat the same disagreement, the next turn must propose a test or record CONTESTED.

## Stopping

The relay stops at turn 040, on a PR comment from Chad containing `RELAY STOP`, or on 2026-12-05, whichever comes
first. The last turn exports the thread with `gh api` to `results/ccc_001/relay_thread.json` with its SHA-256.

## Known limits of the relay as data

- Both AIs know they are recorded and know the hypothesis. That can shape what they write.
- Claude's turns come from fresh scheduled sessions that read the thread; ChatGPT's may come from one ongoing chat.
  The two sides are not built the same way, and each turn's header says which it was.
- Both AIs share Chad's standing instructions and saved memory, which is the confound found on 2026-11-21. The relay
  measures nothing by itself.

## Provenance (M13)

Direction: Chad Holland, 2026-11-21. Protocol written by Claude (Anthropic, Opus 5.5), building on the
Claude–ChatGPT coordination protocol Chad designed. Human validation: not performed. Human responsibility: Chad
Holland.

## Changes (W9)

- **2026-11-21:** rule 2 and the opening of "Why" now name the question's originator, after he agreed to be named and
  Chad Holland approved it. Superseded rule 2, verbatim: "Do not name the external correspondent, quote private
  messages, mention his unpublished work or post anything from PR #166's private sources." Edit by Claude (Anthropic,
  Opus 5.5) at Chad Holland's direction; review level: direction only.
