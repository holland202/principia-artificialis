# Sovereign Veritas SEC-004 — a scored verdict recorded about 22 days late, and a pinned probe that could not confirm the fix

**Date recorded:** 2026-11-03
**Record status:** Documentation-only record (W9). **No rule is adopted by this file.** The two rules below are
proposals under M18; adopting either needs Chad Holland's decision and a dated amendment.
**Incident repository:** [holland202/sovereign-veritas](https://github.com/holland202/sovereign-veritas), which
stays the canonical source for the evidence. Research discussion: [note073](../../research_notes/note073_repair_verification_intake.md).

## Observation 1 — the verdict, as opposed to the CI failure, went unrecorded

Checked from sources on 2026-11-03:

| Fact | Source |
|---|---|
| The SEC-004 workflow run (id 38160250976, commit `8338e83`) started 2026-10-11 17:34:58 UTC, finished 17:46:27 UTC, conclusion `failure` | GitHub Actions API |
| On failure, the workflow prints `GATE=SECURITY_FAIL` in its log and annotates the job "SEC-004 SECURITY_FAIL" | `.github/workflows/sec004-release-race.yml` at `8338e83` |
| The same day's records say only that the SEC-004 CI **failed** | Sovereign Veritas `docs/research-log/2026-10-11_0500-1700_CDT.md` line 20; `docs/handoffs/2026-10-11_CLAUDE_HIATUS_READ_ONLY.md` line 10; Principia note 071 line 23 |
| The scored verdict `SECURITY_FAIL` first appears in a checked repository in commit `7e40c12`, 2026-11-02 15:40:56 UTC | `git log -S` over Sovereign Veritas; a search of Principia |

The run finished 21.9 days before the verdict was written down. The failure itself was not hidden: it was logged
the same day as a CI failure. What was lost is the difference between "the instrument failed" and "the instrument
found a security failure". The SEC-004 workflow exits red in both cases, so a red check alone does not say which.

"Checked" means the Sovereign Veritas and Principia repositories. Other records were not searched.

## Observation 2 — a probe pinned to the vulnerable source cannot confirm a fix

`docs/SEC004_RESULTS.md` (2026-11-02) predicted that a registered re-run of the SEC-004 probe would flip P2 after a
fix. It could not. The probe refuses to run when the source changes (`GATE=INCONCLUSIVE_SOURCE_CHANGED`, exit 2),
and its forced schedule cannot finish against a lock. SEC-005 needed a new probe that imports the old cases and keeps
a no-lock arm that reproduces the original failure. The wrong prediction is corrected in an appended, dated update
in that file.

## Classification

- **The method as written did not catch observation 1.** W6 requires results to be written but sets no time limit,
  and nothing requires a red CI check that carries a verdict to be read past "failed".
- **Observation 2 is a design lesson, not a violation.** Pinning a probe to its source is correct (it is how the
  probe refuses to measure the wrong thing). The gap is that nothing in the method says how a fix is confirmed once
  the pinned probe stops running.
- The SEC-004 commits carry Chad Holland's name. Which assistant, if any, drafted them or the 2026-10-11 records
  is not shown by the sources checked, so it is not stated here. This record assigns no blame. It records what the
  sources show.

## Proposed rules (PROPOSALS ONLY — not adopted)

- **Proposal A (for W6).** A registered run whose verdict is not written into the results within a fixed number of
  days gets a dated `VERDICT NOT RECORDED` placeholder that links the raw run. The number of days is for Chad Holland
  to set. A red check from a verdict-bearing workflow is recorded with the verdict line it printed, not as "failed".
- **Proposal B (for W3/W6).** When a fix is made for a failure found by a source-pinned probe, the fix is confirmed
  by a new registered instrument that (i) reuses the old probe's cases by import, (ii) includes an arm with the fix
  removed that must reproduce the old failure, and (iii) records the old probe's refusal on the new source as an
  expected outcome.

Under M18 a rule is adopted only after a real failure shows the method missed something. This file is that
evidence for Proposal A. Proposal B rests on one case, so it should stay a door until a second case appears.

**Prepared by:** Claude (Anthropic, Opus 5.5), from GitHub API data and the files named above.
**Human review level:** Direction only; no line-by-line review claimed.
**Human responsibility:** Chad Holland.
