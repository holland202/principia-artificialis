# PA #49 audit probe: registered before running (Claude, Opus 5.5), 2026-10-22
Target: PR #49 head 8b3f383 (lineage_lab). Self-tested probe, not independent.
R1  unittest lineage_lab.test_lineage: 14 tests OK.
R2  run_acceptance: VERDICT 6 of 7; digest matches pinned 209e78c4...; exit 0.
R3  A crafted journal with a valid chain and data.hypothesis_id = [] (result event) makes read_events raise TypeError, not JournalError.
R4  The same holds with event kind = [] (TypeError).
R5  append() with an AI contributor and review_level = [] raises TypeError (not JournalError). So does outcome = [].
R6  CLI verify on the R3 journal exits 1 with a traceback (uncaught TypeError). That is the same exit code as "sabotage detected".
R7  Timestamps that go backwards (event 2 earlier than event 1) are accepted.
R8  A human contributor with a non-string review_level (e.g. 123) is accepted, and the value appears in graph().
R9  read_events on a missing journal creates a .lock file as a side effect.
R10 Suffix truncation (drop the last line) is accepted. This is a disclosed limitation, not a defect.
Control C1: an unmodified demo journal verifies (exit 0).
Control C2: a one-character edit to a committed record is rejected with JournalError.
