# PA-LINEAGE-001: audit, 2026-10-22 (registration first, results appended)

**Status:** AUDIT REGISTERED. The fix is NOT yet written at the commit that adds this file.
**Target:** PR #49 at `8b3f383`. The original [PREREG](PA-LINEAGE-001_PREREG.md) and [RESULTS](PA-LINEAGE-001_RESULTS.md) are frozen records and are not edited (M12). This file appends to them.
**Authority:** owner authorization on PR #49 (2026-10-14) to audit and correct the prototype on its feature branch. Merging still needs the owner's separate approval.
**Provenance (M13):** Claude (Anthropic, Opus 5.5) audited, registered, tested and fixed. The original implementation is by ChatGPT (OpenAI GPT-6). Human validation: not performed. Human review level: direction only. **Everything here is self-tested (M10): a second AI checking the first AI's code, not independent validation.**

## Findings, observed before this registration (W5 attack probe)

The probe was registered before running (`PREDICTIONS.md` SHA-256 `e1746fb5…7100`); all 12 outcomes held as predicted. Run with Python 3.13.16:

```
C1 accepted
C2 JournalError: event digest mismatch
R3 TypeError: unhashable type: 'list'
R6 exit 1 traceback TypeError: unhashable type: 'list'
R4 TypeError: unhashable type: 'list'
R5a TypeError: unhashable type: 'list'
R5b TypeError: unhashable type: 'list'
R5c TypeError: unhashable type: 'dict'
R7 accepted
R8 accepted graph review_level = 123
R9 JournalError: journal does not exist; run init first lock created: True
R10 accepted
```

| ID | Finding | Severity |
|---|---|---|
| **L1** | `kind`, `hypothesis_id`, `outcome` and AI `review_level` are tested for membership in a `set`/`frozenset` before their type is checked. A list or dict value raises an unstructured `TypeError`, not `JournalError`. This happens both when appending and when reading a crafted journal whose hash chain is valid (R3–R5). It contradicts C-BUILD as registered ("errors/absent mandatory fields fail closed") in spirit: the result is a crash, not a structured refusal | Medium. It does fail closed, but as a crash |
| **L2** | `verify` on such a journal exits **1** with a traceback (R6). Exit 1 is also the code for "planted mutation detected". The CI bash sabotage gate checks only `rc == 1`. A crash mutant (digest check raises `TypeError`) still **passes** that gate. The acceptance instrument's P6 also checks stdout, so CI as a whole would still catch it; the bash step alone cannot | Low (the gate step is vacuous for crash vs. detection) |
| **L3** | A human contributor's `review_level` is not validated. A non-string value (123) is accepted and shown in the graph (R8) | Low |
| L4 | Timestamps may go backwards (R7). This is not claimed by the registration, so it is recorded as a door, not fixed | Note |
| L5 | `read_events` on a missing journal leaves a `.lock` file behind (R9) | Note |
| — | Suffix truncation is accepted (R10). This is **disclosed** in the original limits; not a defect | — |

**Explorer page (P7 was NOT RUN in the original).** One fresh observation, self-tested, headless Chromium only. It loads with no page errors and makes no network requests. The sample renders. A graph file with `<img onerror>` and `<script>` in its titles shows them **as text**: the injected script did not run and no `img` element was created. This is not an accessibility or usability test, and it does not test other browsers. P7 stays NOT RUN as registered; this is an additional observation only.

## Registered predictions for the fix (before the fix exists)

- **F1:** a new test file `lineage_lab/test_audit_malformed.py` **fails** on the current code, with at least one error per guarded field.
- **F2:** after the fix, every malformed type (list, dict, int, bool, `None`) in `kind`, `hypothesis_id`, `outcome`, AI `review_level` and human `review_level` raises `JournalError`, on both the append and the read paths. CLI `verify` on the R3 journal exits **2** with `GATE: FAIL` and no traceback.
- **F3:** the original 14 tests still pass, and `run_acceptance` still prints `VERDICT 6 of 7` with digest `209e78c4…6d66`, exit 0.
- **F4:** removing any single new type guard (one mutant per guard: 5 in total) makes at least one new test fail.
- **F5:** after the CI bash gate is tightened to also require `mutation detected` in stdout, the crash mutant from L2 **fails** the gate.

Anti-vacuity (M3): F1 shows the new tests can fail; F4 shows each guard is needed; F5 shows the gate can say no.

Door (M15, unrun): monotonic or anchored timestamps (L4); lock-file hygiene (L5); an independently authored validator (from the original door list).

---

## Results (appended after the fix; W6)

Fix commit: type checks before every set/frozenset membership test in `core.py` (`kind`, `hypothesis_id`, `outcome`, AI `review_level`), plus validation of a human `review_level` when one is present. The CI sabotage step now also requires `mutation detected` in stdout, and CI runs the new test file. Raw output: [2026-10-22_audit_after_fix.txt](../results/PA-LINEAGE-001/2026-10-22_audit_after_fix.txt). Pre-fix failing run: [2026-10-22_audit_F1_before_fix.txt](../results/PA-LINEAGE-001/2026-10-22_audit_F1_before_fix.txt). Probe, mutant and browser scripts: [audit_2026-10-22/](../results/PA-LINEAGE-001/audit_2026-10-22/).

| Prediction | Observed | Outcome |
|---|---|---|
| F1 new tests fail on unfixed code | `FAILED (failures=10, errors=16)`, `TypeError: unhashable type` for list and dict | HELD |
| F2 malformed types → `JournalError`; CLI exits 2, no traceback | All subtests pass; probe R3–R5 now `JournalError`; `R6 exit 2 no-traceback GATE: FAIL — unknown hypothesis` | HELD |
| F3 original 14 tests pass; acceptance unchanged | `Ran 17 tests … OK`; `VERDICT 6 of 7`, digest `209e78c4…6d66`, exit 0 | HELD |
| F4 each guard's removal is caught | 5 of 5 mutants KILLED | HELD |
| F5 tightened gate rejects the crash mutant | `rc=1; old gate PASSES; tightened gate FAILS` | HELD |

**VERDICT 5 of 5 as registered.** All of it is self-tested, on Python 3.13.16 / x86_64 in a Linux container. It has not been run on the S25, under Python 3.14, or in other browsers. L4 (non-monotonic timestamps) and L5 (lock-file residue) are unchanged and remain doors.
