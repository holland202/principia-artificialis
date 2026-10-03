# Methodology comparison: status (appended 2026-10-03)

**Status: UNRUN — independent task construction and scoring not available.** Stage 2 is **PARKED** at
revision 4. It is not frozen and not committed as a Stage 2 registration. Nothing has been
constructed, run or scored, and the comparison has demonstrated nothing.

Stage 1, [`../METHODOLOGY_COMPARISON_PREREG.md`](../METHODOLOGY_COMPARISON_PREREG.md) (`aef769e`), is
unchanged and stays immutable.

## Files

| File | md5 | What it is |
|---|---|---|
| `STAGE2_SPEC_REV4_PARKED.md` | `2f1d6213ad0f229c224aa088b2f8bbad` | The Stage 2 specification, revision 4, verbatim. It is the last revision, and it passed its own self-audit as "ready for human review" (not "ready to freeze") |
| `STAGE2_SPEC_REV3.md` | `d9cecd913553e330cf2b56be8c5455ac` | Revision 3, verbatim. A conformance audit found blockers B1–B7 in it, and revision 4 closes them. B1 is that, read literally, A could never win a directional verdict |

**Revision 2 is not preserved.** It existed only in a working session and was lost when that session's
context was compacted. Revision 3 §0 and revision 4 §0 describe what each revision changed.

## Why it is parked

- Chad Holland's direction on 2026-10-03: stop expanding the study while independent task construction
  and scoring are unavailable. Its specification had grown to about the length of the method it tests
  (Amendment 3, F10).
- Stage 1 and both revisions require the constructor/sealer and the primary scorer to be two distinct
  humans who did not design Condition B or the study. Chad Holland and Claude are excluded. No such
  people are available.

## What changed around it

SWAY Amendment 3 (principia-artificialis, registered `0c634a1`) consolidated the method into
`METHOD.md`, `WORKFLOW.md` and `CONTROLS.md`, and retired the experiment-first skill's eight-word
status list. Condition B is therefore **a superseded method**. Its texts stay pinned by md5 in Stage 1,
and verbatim copies are kept on `main` in `methodology/record/skills/` (md5 `e5fa5a56…` and
`0992bc29…`).

If the study ever runs, it compares the frozen Stage 1 texts, not the current method. Its relevance to
current practice is lower than when it was registered. Under Amendment 3, the study is the
experiment-specific protocol C-METHCOMP and never general procedure.

**Provenance:** Claude (Anthropic, Opus 5.5) wrote this status file and copied the two revisions from
the session scratchpad, checking the md5s. Human review: direction only. Responsibility: Chad Holland.

**Door:** the study runs only if two independent human scorers become available. Until then, the
cheaper informative test is the one Amendment 3 names: score Amendment 1's P5 on its closed window.
