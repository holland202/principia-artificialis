# Freeze record: RELAY_CHECKPOINTS_PREREG.md

**Frozen file:** [`RELAY_CHECKPOINTS_PREREG.md`](RELAY_CHECKPOINTS_PREREG.md) as committed at `98798ba`, SHA-256
`cd2f3c895283ecd0c27c029262a96c2ab528812279a87245d002e716bab670ae`.
**Frozen at:** 2026-11-22T01:46Z (2026-11-21 evening, Central). Relay turn 012 was the latest turn. Checkpoint
016 had not been reached.
**Owner approval:** Chad Holland approved the freeze on 2026-11-22 at about 01:45 UTC, given directly to Claude in
chat (paraphrased, not quoted). Recorded here by Claude (Anthropic, Opus 5.5).

## What is frozen

- The checkpoint table: 016 and 032 primary, 024 and 040 secondary, 008 archival only.
- The MISSING rule: an unreached checkpoint stays MISSING, and nothing substitutes for it.
- Extraction rules 1 to 5: source, which comments count as relay turns, ordering and fail-closed checks, snapshot,
  and rendered text.
- The order-shuffle construction and the extractor predictions X1 to X3.

## What is not frozen

- **Rule 6, the speaker mapping.** ChatGPT objected in relay turn 012, posted before this freeze. Mapping ChatGPT's
  turns to the `assistant` role gives the measured model a history written in its own role, which could change the
  effect being measured. ChatGPT proposed rendering the transcript as quoted material with neutral speaker labels,
  inside one `user` message. Rule 6 stays in the file as written (append-only), but **no arm-A rendering is
  registered**. Choosing between rule 6 and the neutral-label rendering needs its own registration, approved by
  Chad, before any arm-A reading.
- Any endpoint, threshold or prediction about the measured model. The prereg registers none.
- Experimental use of any prefix. Extraction and snapshots are archival until Chad approves arm-A use.

## Errors found later

Errors in the frozen file are recorded as dated deviations here or in the results. The frozen file is never edited.

## Provenance (M13)

Freeze record written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-22. Human validation:
not performed. Human responsibility: Chad Holland. The question behind CCC-001 is Federico Talens-Alesson's;
crediting him implies no endorsement or validation by him.
