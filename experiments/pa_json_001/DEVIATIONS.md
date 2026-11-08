# PA-JSON-001 — Deviations and unperformed review

Recorded November 7, 2026, America/Chicago. Append-only research history.

1. **No committed preregistration (M2 / W2).** The first systematic execution
   happened outside Principia Artificialis. Its local plan and source hashes were
   written before that execution, but were not committed or externally timestamped.
   The local timestamp is self-reported by the host. Importing the plan after
   the run does not make it a PA registration. It is retained as received; no
   predictions are retroactively numbered or scored as registered.
2. **Prior observations (M11 / C-EXPLORE).** A small exploratory probe exposed
   rounded SQLite JSON outputs before the local plan. The protocol discloses the
   examples. The broader corpus was fixed locally before its one systematic run,
   but this does not repair the missing committed preregistration.
3. **Known upstream correction (M8 / C-EXT).** Inspection of SQLite's history
   found commit `5b98467d28aa1ceff5602b54a0cd7c0d3f1c8fb0`, dated
   2026-05-29, changing the JSON formatter from `%!0.15g` to `%!0.17g`.
   Any claim to have discovered a new SQLite defect is rejected. Newer SQLite
   behavior was inspected in source, not executed. Do not extrapolate the old
   build's observations to current upstream.
4. **Self-testing (M10 / C-INDEP).** The exact-rational observer and the
   JavaScript bit-pattern observer were written by the same ChatGPT agent.
   They agreed on the stored observations ([verification output](results/verification.json)). No independent person, different
   model family, different machine, or independent implementation author has
   reproduced the study.
5. **Human look missing (C-SYNTH).** Input-class counts and a named look sample
   are included. No person is recorded as inspecting it. The record remains
   EXPLORATORY and cannot be promoted by this import.
6. **Instrument additions after execution.** The original `run.py`,
   `node_transform.mjs`, `PROTOCOL.md`, `FREEZE.json`, uncompressed observations,
   and summaries are preserved byte-for-byte. `verify.mjs` was extended to accept
   gzip and inject an in-memory observation error. The new reference script checks
   archive integrity and the stored observations only. Profile and sample files
   are post-hoc analyses. None is a second run of the subjects.
7. **Checks scoped to this contribution (W7).** Archive checks, their sabotage
   control, document integrity checks, method lint, and applicable repository
   unit tests are run. The scientific campaigns behind unrelated reference
   scripts are not re-executed to publish this archival record. A pinned
   `vacuity_lint` installation is not specified or present in this checkout;
   it is not reported as run. Repository CI has its own reference-code job.

No status promotion or rule change is proposed. No merge authorization is inferred.
