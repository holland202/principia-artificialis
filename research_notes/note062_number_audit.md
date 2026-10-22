# Research Note #062: Do the Notes' Numbers Appear in Their Own Code's Output?

**Status:** Draft, verified reference code; P2 refuted and kept — registered 2026-09-27, before the audit was run
**Theme:** Method / reproducibility
**Author:** Claude (Anthropic), for Chad Edward Holland
**Builds on:** the binding rule in NOTE_TEMPLATE.md ("numbers match code output"), [[note044_circularity_test]] (an instrument must be able to fail), [[note058_kv_vacuity]] (a check that lies about why it failed)
**Reference code:** `scripts/check_numbers.py` (writes `results/NUMBER_CHECK.md`)

## The claim

The program's first rule is that every number in a note's prose is printed by that note's reference
script. Nothing has ever checked the rule mechanically. This note builds the check and runs it once
over every note with a reference script. The claim that could be precisely wrong: **the rule already
holds, to within a few percent of the measured numbers.**

## Instrument

For each `scripts/noteNNN_reference.py`, the note that names it is paired with the script's output,
run with CI's arguments. A *measurement-like* number is a decimal or exponent literal with at least 3
significant digits. It is FOUND if the output prints it, or prints the same value to more decimal
places. Everything else is NOT FOUND and listed with its line, as a lead for a human reader.

## Registered predictions (written before the first full run)

- **P1 (anti-vacuity)** The self-test passes. A note that quotes its output shows 0 not found, and the
  same note with one digit changed (1.6398 → 1.6498) is flagged, and only that number.
- **P2** Across all notes with reference scripts, at least 90 % of measured numbers are FOUND.
- **P3** Every NOT FOUND number is classified by hand as (a) a parameter or a number quoted from
  elsewhere, (b) a derived value computed in prose from printed ones, or (c) drift: a number the code
  no longer prints. P3 predicts at least one (c), because a program with 20+ scripts edited over two
  months will have drifted somewhere.

## Results

**What broke first: the instrument.** Run 1 printed `TOTAL 125/195 found`. Reading the not-found list by
hand showed that the checker missed every negative number in prose. The notes write minus as U+2212
("−3.082") and the scripts print "-3.082". After the fix, run 2 printed:

```
self-test: honest note 0 not found; planted wrong number flagged: ['1.6498'] -> PASS
TOTAL 129/195 found; report: results/NUMBER_CHECK.md
```

- **P1 held.** The self-test passes and flags exactly the planted number.
- **P2 REFUTED (kept).** 129 of 195 measured numbers (66 %) appear in their script's output, against
  the registered ≥ 90 %.
- **P3 held.** Every one of the 66 NOT FOUND numbers was read by hand in context:

| class | count | what it is | notes |
|---|---|---|---|
| (a) quoted from elsewhere | 47 | pre-fix values kept as history, device-only runs (thermal, timings), another run size, a control corpus, and two instrument false positives (an arXiv id, a Python version) | 040, 048, 052, 053, 054, 055, 056, 059, 060, 061 |
| (b) derived in prose | 9 | computed from printed numbers: 2.15× = 1 + 1.1513, 12.0 % = 3/25, CI widths, a difference of two printed gains | 052, 054, 055, 059, 060 |
| (c) drift | 10 | numbers the code does not print | 043 |

**What P2's failure teaches.** The rule "every number in the prose is printed by the code" conflicts
with the program's other rule, "refutations and history stay on the page". Most not-found numbers are
honest history: pre-fix outputs kept so a reader can see what broke. The literal rule cannot hold for
them. A rule that can hold: *every number the note currently claims is printed by the code; every
historical or external number is marked as such where it appears.* The checker cannot tell the two
kinds apart yet. That is the next instrument.

**What P3's (c) found: note043's pasted output was not produced by its code.** The note shows
F = -8.7883 / 3.6652 and AUC 0.9950. Both the code pasted in the note and `scripts/note043_reference.py`
print F = -1.0232 / -0.6320 and AUC 1.0000, deterministically. The pasted block's line structure also
differs from anything the code prints. Its AUC is vacuous besides: every "hallucinated" trajectory
is identical. note043 now leads with a correction, and its status no longer says "verified reference
code". The original text is kept.

**A second, smaller drift, found on the way:** `scripts/note055_reference.py` printed "v1 already passed
its analogue (rho=+0.117)", but note054's tie fix changed that value to +0.1480, as note055's own prose
says. The printed line now gives both.

After these corrections, the committed report reads `TOTAL 145/216 found`. The total grew because the
note043 correction pastes the true output, and quotes the wrong numbers once more so a reader can
compare.

Not covered: notes 038, 041 and 050. The checker found no unique note naming their script (number
collisions, see the index's ⚡).

## Falsifiable next predictions

- **P4 (open)** Adding `check_numbers.py` to CI as a *warning* (not a gate) reduces new class-(c) drift
  to zero over the next ten notes. Unrun.

## Update 2026-10-16: the audit's own self-test was not binding (registered before the repair was run)

Everything above is unchanged. This section is appended (M12).

**What was observed first (exploratory, disclosed under C-EXPLORE).** Read-only runs on `f623fd2`, before this
section was written:

- CI runs `python scripts/check_numbers.py || true`. Breaking the self-test in memory makes the script exit 1, and
  the CI step still exits 0. So P1, the anti-vacuity control above, has never been able to fail the build. "Report
  only" was meant for NOT FOUND numbers, which may be honest history. It was not meant for a broken instrument.
- The docstring promises exit 2 for "could not run". No path produces it. A reference-script timeout and a missing
  `results/` directory both end in a traceback with exit 1, the same code as a failed self-test.
- note067's text never names `scripts/note067_reference.py`, so the checker skips it. The report row reads "no
  unique note names note067_reference", the same wording used for real number collisions.
- For the four post-062 notes that have reference scripts (063, 064, 065, 067), every NOT FOUND number was read in
  context. None is class (c) drift: note064's three are the registered value 0.1425, which the note itself explains
  against the printed 0.1426, and note067's five are a value derived in prose and three closed-form values the note
  discloses as computed before registration. **This is not a P4 result.** P4 counts ten notes. Eight notes have
  landed since note062, and only four have reference scripts.

**Repair.** A separate CI step runs `check_numbers.py --plant` and fails the build if the self-test fails. The
report step stays report-only. A reference script that times out or cannot start is recorded as "not run", and
the script exits 2. `results/` is created if missing. When no note names a script, a note is paired by filename
only if exactly one note file starts with that number, and the report says so.

**Predictions for the repair (registered before it is run):**

- **P5** `--plant` prints exactly the P1 line pasted above, unchanged, and exits 0.
- **P6** A full run at the repair commit pairs note067 by filename, and still leaves 038, 041 and 050 unpaired
  (each number is claimed by more than one note file).
- **P7** The full run's TOTAL is the earlier 374/448 plus note067's 77 measured numbers, 72 of them found:
  **446/525**.
- **P8** The new unit tests fail when, in memory: the self-test is broken (exit must be 1), a reference script
  times out (row "not run", exit 2), or the filename fallback is removed (note067 unpaired).

P4 stays open.

### Results of the repair (2026-10-16, run after the predictions above were committed in `3775172`)

Run in a Linux container with Python 3.13 (NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2), not on the S25.

```
# lines from each command's stdout; "exit=" lines are the shell's echo of its exit code.
# The full run prints one line per note; only note067's line and the total are shown here.
$ python scripts/check_numbers.py --plant
self-test: honest note 0 not found; planted wrong number flagged: ['1.6498'] -> PASS
exit=0

$ python scripts/check_numbers.py
note067: note067_evaluator_sensitivity_bound.md (paired by filename; the note does not name its script): exit 0, 77 measured numbers, 5 not found in the output
TOTAL 446/525 found; report: results/NUMBER_CHECK.md
exit=0

# three rows copied from results/NUMBER_CHECK.md, written by the same run
| 038 | (no unique note names note038_reference, and the number is shared by several note files) | - | - | - | - |
| 041 | (no unique note names note041_reference, and the number is shared by several note files) | - | - | - | - |
| 050 | 050_seasonal_memory_governance.md (paired by filename; the note does not name its script) | 0 | 0 | 0 | 0 |

# stdout of: python scripts/mutate_check_numbers.py scripts
mutants of check_numbers.py run against scripts/test_check_numbers.py (in memory, one at a time):
KILLED   M1 checker accepts every number (self-test can no longer flag)
KILLED   M2 main ignores a failed self-test
KILLED   M3 timeout not caught
KILLED   M4 not-run does not exit 2
KILLED   M5 filename fallback removed
KILLED   M6 results/ not created
mutants killed: 6/6
```

- **P5 held.** The `--plant` line is the P1 line, unchanged.
- **P6 REFUTED (kept).** note067 is paired by filename and 038 and 041 stay unpaired, but **050 was paired too**.
  P6 relied on this note's earlier line "Not covered: notes 038, 041 and 050 … number collisions", and that line
  was wrong about 050. Only one note file carries the number 050, and its script's docstring names the same note,
  "Seasonal Memory Governance". 050 was skipped because its text never names its script, the same gap as note067.
  It has no measured numbers, so the total does not change.
- **P7 held.** 446/525.
- **P8 held.** All six mutants are killed.

**Found while building the tests: sentence-final numbers are invisible to the checker.** The number pattern refuses
a trailing period, so "slope 1.6398." yields no token at all. The self-test's own honest note ends "falling to
0.00030.", so that number has never been checked. A one-off scan, which is not committed and so not reproducible from this repository (M6), and has not been reviewed
by hand, counted 9 measured numbers in that position across notes 043, 044, 045, 048, 055, 064 and 067. Treat that
count as a lead. The pattern is **not**
changed here, because P7 was registered against it.

- **P9 (open)** Allowing a sentence-final period, with the scan committed beside it, raises the measured count by
  at most 9 and adds no class (c) drift. Unrun.

P4 is still open: eight notes since note062, four with reference scripts. `results/NUMBER_CHECK.md` in the
repository is still the 2026-09-27 copy; CI regenerates it on every run without committing it.

Provenance: Claude (Anthropic, Opus 5.5) observed, registered, built and ran this update → human validation: not
performed → human editing/curation: direction by Chad Holland, 2026-10-16 → human responsibility: Chad Holland.
Human review level: direction only. Self-tested.

## Update 2026-10-16 (2): one correction, P10 registered, P9 run plan (written before either is run)

**Correction (W9).** The section above says "The self-test's own honest note ends 'falling to 0.00030.', so that
number has never been checked." That is wrong. `0.00030` has two significant digits, so `measured()` skips it
whatever comes after it:

```
$ python3 -c "import sys; sys.path.insert(0,'scripts'); import check_numbers as C; print(C.sig_digits('0.00030'), C.measured('0.00030'))"
2 False
```

The sentence-final blind spot is real, but the self-test is not an instance of it. The sentence is kept above, as
written.

**P10 (registered here).** Adding a `**Reference code:**` header line to note050 and note067 changes their
report rows from "paired by filename" to an ordinary pairing, leaves 038 and 041 unpaired, and leaves the full
run's TOTAL at **446/525**.

**P9 run plan.** `NUM`'s closing lookahead changes from `(?![\w.])` to `(?![\w])(?!\.\d)`. A number followed by a
period then counts, unless a digit follows the period, so `3.11.2` still yields no token. The checker itself is
the committed scan that P9 asks for: the measured count is the TOTAL denominator before and after the change.
P9 as registered: the denominator rises by at most 9, and no new NOT FOUND number is class (c) drift.

### Results of update (2) (run after `73f8a30` registered them; Linux container, Python 3.13, not the S25)

```
# P10: after the two header lines; lines from the full run's stdout
note050: 050_seasonal_memory_governance.md: exit 0, 0 measured numbers, 0 not found in the output
note067: note067_evaluator_sensitivity_bound.md: exit 0, 77 measured numbers, 5 not found in the output
TOTAL 446/525 found; report: results/NUMBER_CHECK.md
# rows from results/NUMBER_CHECK.md as written by the P9 run below; the P10 run printed the same two rows
| 038 | (no unique note names note038_reference, and the number is shared by several note files) | - | - | - | - |
| 041 | (no unique note names note041_reference, and the number is shared by several note files) | - | - | - | - |

# P9: after the pattern change; lines from the full run's stdout that differ from the P10 run
note043: note043_free_energy_of_reasoning.md: exit 0, 32 measured numbers, 17 not found in the output
note044: note044_circularity_test.md: exit 0, 3 measured numbers, 0 not found in the output
note045: note045_stubbornness.md: exit 0, 1 measured numbers, 1 not found in the output
note048: note048_the_governor_is_the_dynamics.md: exit 0, 14 measured numbers, 9 not found in the output
note055: note055_kx_marginal_utility.md: exit 0, 19 measured numbers, 8 not found in the output
note064: note064_governed_outcome_feedback.md: exit 0, 83 measured numbers, 3 not found in the output
note067: note067_evaluator_sensitivity_bound.md: exit 0, 90 measured numbers, 5 not found in the output
TOTAL 463/544 found; report: results/NUMBER_CHECK.md

# stdout of: python scripts/mutate_check_numbers.py scripts
KILLED   M1 checker accepts every number (self-test can no longer flag)
KILLED   M2 main ignores a failed self-test
KILLED   M3 timeout not caught
KILLED   M4 not-run does not exit 2
KILLED   M5 filename fallback removed
KILLED   M6 results/ not created
KILLED   M7 sentence-final period rejected again (pre-P9 pattern)
mutants killed: 7/7
```

- **P10 held.** 050 and 067 pair by name; 038 and 041 stay unpaired; TOTAL 446/525.
- **P9 REFUTED in part (kept).** The measured count rose from 525 to **544**, not by at most 9. The one-off scan
  counted the 9 sentence-final numbers correctly, but the new pattern also accepts a number followed by `..`,
  so it picks up the left endpoint of every range in note067's pasted output (`S3P bound 0.004980..0.012872`),
  10 more numbers. All 10 are FOUND. The right endpoint of a range is still never extracted: the lookbehind
  refuses a number preceded by a period. That asymmetry is pinned in a unit test (`test_range_left_endpoint_only`)
  rather than fixed here.
- **P9's second half held.** Two numbers are newly NOT FOUND, and both are kept history, class (a), not drift:
  note043's `0.2561` is the wrong pasted value quoted beside its correction ("not 0.7333 against 0.2561"), and
  note045's `+0.6014` is U1 before the tie correction (the script now prints `+0.6130`).
- The pattern change is guarded by mutant M7; the suite now kills 7/7.

- **P11 (open)** Extracting both endpoints of a range adds only FOUND numbers. Unrun.

P4 is still open.

**CI did not reproduce the container's total, and the cause is note055, not the checker.** On the PR head, GitHub CI
printed `TOTAL 459/544 found` (run 38948441621), against `463/544` in the container. The only differing row is
note055, with 12 not found in CI against 8 in the container. The two CI runs since this morning used the same
package versions (`numpy-2.4.6 scipy-1.17.1`). Run 38944808763's note055 output matches the container's
byte for byte. Run 38948441621's differs from the fourth or fifth decimal on, for example:

```
container / run 38944808763:     pred       mean loss 0.062687   vs uniform -0.2086
run 38948441621:                 pred       mean loss 0.062694   vs uniform -0.2087
```

In the container the script prints identical output on five runs, with and without single-threaded BLAS.
So note055's printed numbers depend on the machine that runs them. *Interpretation, not verified:* different
GitHub runner CPUs take different floating-point paths in the BLAS kernels. The P9 pattern change exposes this,
because it newly checks note055's sentence-final "-0.2086." That number is FOUND or NOT FOUND depending on the
runner.

- **P12 (open)** note055's output is identical across GitHub runners once the BLAS core type is pinned (for
  example `OPENBLAS_CORETYPE=Haswell`). If it is not, the machine dependence is in note055's own arithmetic, and
  its four-decimal claims need a stated tolerance (M5). Unrun.
