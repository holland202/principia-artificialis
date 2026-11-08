# Note 052 — Verification That Cannot Fail

**Status:** Draft, verified reference code ⚠ P6 underpowered and P10a refuted, kept
**Authors:** holland202 (Chad Holland), Claude (Anthropic)
**Date:** 2026-08-02
**Instruments:** vacuity_lint.py (github.com/holland202/vacuity_lint.py, selftest 18/18 on aarch64/Termux/Py3.14), vacuity_scan.py (clean-room reimplementation, sandbox only — numbers from the two instruments are NOT comparable)
**Related:** [[note036_verified_models_drift_ledgers]] · [[note044_circularity_test]] · [[NOTES_INDEX]]

---

## What broke (failures lead)

1. **Both registered predictions about the estate were refuted.**
   P1 predicted findings in at least half of 13 repositories; the measurement
   was 6 of 13 (46%). P2 predicted under 10 findings after precision fixes;
   the measurement was 13. Both kept below.

2. **The instruments built to find the defect contained the defect.**
   arch_map.py's selftest initially could not distinguish exit 0 from exit 1 —
   an always-clean script would have scored as gated (fixed, added as its
   P10b). vacuity_scan.py's suppression-marker regex used `\s*`, which matched
   newlines and let a bare marker swallow the next source line as its
   "reason" — the mute button the design exists to prevent. Two selftest
   fixtures were misnamed so their tests never ran; the gate caught it, not
   the authors.

3. **First-pass precision was poor.** Of 7 findings in one repository, 5 were
   false positives (library modules matched on filename alone; runnable
   scripts that correctly exit non-zero were flagged as uncollectable). The
   first estate total of 21 dropped to 13 after the fixes — a 38% cut.

4. **A defect class the linter cannot see at all** was found during this work:
   a test suite that was genuinely written and genuinely passed (18 checks)
   but never reached the public repository. Scanning the public repo finds
   nothing wrong — there is no bad code, just an absent suite everyone
   believed in. "Verified" and "published" are different steps. This sits one
   level above the Type A/B taxonomy below and is not addressed by this note's
   instrument.

---

## The finding

On 2026-07-26, four independent codebases were found to contain a
verification construct that could not fail: a tomography self-check with no
fail path, a pytest suite that collected zero tests, a generated-file guard
whose marker was never written, and a smoke test whose boolean branch was
dead. Different authors, different AI models, written in different months.
Nobody had noticed, because the failure path in each had never been taken —
so nobody discovered it could not be reported.

A gate you have never seen fail is not evidence that anything passed.

## Taxonomy

- **Type A — no fail path exists.** No assert, no raise, no non-zero exit,
  no `def test_`. Statically detectable.
- **Type B — a fail path exists but cannot fire.** A marker defined but never
  written; a boolean branch dead because one condition implies another.
  Requires reachability analysis.

The original four defects split exactly 2 / 2. The instrument catches every
Type A case and misses every Type B case: measured detection rate **2 of 4**.
The blind spot is encoded as instrument selftest P12 rather than omitted.

## Registered predictions and results

Registered before measuring, in order. Refutations kept per method.

**Instrument 1: vacuity_lint.py, estate scan (device, 2026-07-27)**

- **P1 — REFUTED.** "Findings in at least half the repos." Result: 6 of 13
  (46%). Refuted narrowly.
- **P2 — REFUTED.** "Under 10 findings total after precision fixes."
  Result: 13.
- Corrected metric: findings are not files (one file produced two findings).
  Distinct affected files: 12. Corrected again to a true denominator on
  2026-07-27: of **26 verification-shaped entry points** across 12
  repositories, **9 had no fail path**, plus 1 declared intentional.

**Instrument 2: vacuity_scan.py, control-group comparison (sandbox,
2026-07-27; both arms cloned and scanned by one tool on one day)**

- **P3 — CONFIRMED, hollow.** "Fires at least once on the control group."
  It fired 3 times; all 3 were false positives.
- **P4 — CONFIRMED.** "Majority of control findings are false positives."
  3 of 3.
- **P5 — CONFIRMED directionally, confounded.** "Higher true-positive rate in
  this estate than in the control." 2/15 (13.3%) vs 0/347 (0%). n=15 is weak,
  and the pre-registered confounds are unresolved: the estate is solo,
  unreviewed, CI-less research code; the controls are reviewed, CI-gated,
  shipped libraries. Review process explains the gap at least as well as
  authorship does. Do not cite this as "AI code fails more."

**The result that matters is the denominator, not the rate.**
Verification-shaped files per repository: control **34.7**, this estate
**1.2** — a 28× difference. The problem was mostly not that gates failed;
it was that there were almost none to fail.

## Anti-vacuity control

The instrument's selftest includes P9 (a clean tree yields zero findings) and
P10 (a defective tree yields findings). A detector must be shown capable of
returning nothing and something; without both, this instrument would be an
instance of the defect it looks for. The reference script below carries the
same pair.

## Reference code

`scripts/note052_reference.py` — embeds four minimal fixture files
reproducing the 2 Type A / 2 Type B split, runs vacuity_lint.py against
them, and asserts the detection rate is exactly 2 of 4 (exit 1 otherwise).
It also asserts the P9/P10 pair on embedded clean and defective trees.
Requires vacuity_lint.py: looked for beside the script, one level up, then
in ~/vacuity-lint/. Failing all three it fetches the pinned commit 718d103
from github.com/holland202/vacuity_lint.py and verifies sha256 before use.
A failed fetch or a hash mismatch exits 1 -- the instrument is never
silently skipped. Both branches were exercised on device 2026-08-04.

The estate and control measurements (9/26, 2/15 vs 0/347, 34.7 vs 1.2) are
not reproduced by the reference script — they require cloning 23
repositories. They are reproducible from the two repo lists in the
instrument repositories' records, with instrument and date stated above.
Numbers in this section were pasted from tool output, not paraphrased.

## Open predictions (the door)

- **P6 — UNRUN.** Within human-authored repositories, those without CI
  (`.github/workflows` absent) show a higher true-positive vacuity rate than
  those with CI. The 2026-07-27 control sample was CI-uniform (10/10) and
  could not test this. The solo-maintainer, no-CI human stratum is the
  control that would separate authorship from review, and it has not been
  built.
- **P7 — UNRUN.** Type B detection via reachability analysis (a marker that
  is defined but never written; dead boolean branches) will catch at least
  one of the two known Type B instances without exceeding a 20% false-positive
  rate on the fixture set. This is the open problem and the half the current
  instrument does not solve.

---

*Vincit Omnia Veritas.*

---

## Amendment 1 — 2026-09-06. P6 registered concretely, before any repository is fetched.

P6 was registered in this note as an unrun door: *within human-authored
repositories, those without CI show a higher finding rate than those with CI.*
It is the stratum that separates authorship from review, and until it runs, P5
stays confounded and must not be cited as evidence about AI-authored code.

Registering it properly requires fixing three things first, because each is a
place where a result could be tuned after the fact.

### Two defects in the original control arm, recorded

**The control repositories were never named.** Neither this note nor
`scripts/note052_reference.py` lists the ten repositories behind 0/347. The
arm is not reconstructible by a reader or by its own authors.

**The instrument no longer exists.** `vacuity_scan.py` was a clean-room
reimplementation built in a sandbox and was never committed anywhere. The
0/347 figure cannot be reproduced with any published tool.

Consequence: **0/347 is retained as history and is not used as a baseline
here.** Both arms are re-measured. The old number stays in the note.

### Instrument, pinned

`vacuity_lint.py` from github.com/holland202/vacuity_lint.py at commit
`a468d2c`, the public tool, pinned by SHA. Its selftest must report its own
denominator before any scan is accepted; a run that does not print the
expected check count is discarded rather than interpreted.

### Selection rule, fixed before fetching

A candidate pool of human-authored Python repositories is written into this
amendment **before any clone**. The pool is chosen for being human-authored,
Python-majority, and outside this estate. That choice is by hand, which is a
weakness and is stated as one.

**Stratum membership is not chosen. It is measured after cloning:** a
repository lands in stratum A if `.github/workflows/` contains at least one
`.yml` or `.yaml` file, and in stratum B otherwise. A candidate that turns out
to sit in the other stratum moves; it is not dropped. No repository is removed
from the pool after its finding count is known. If the pool splits worse than
3 repositories in either stratum, the comparison is reported as
underpowered and no rate claim is made.

Exclusions fixed now: forks, repositories authored by holland202, `examples/`
directories, and `conftest.py` — the last two being the precision defects
hand-identified on 2026-07-27.

### P6 — restated so it can be precisely wrong

**Predicted:** the true-positive rate per verification-shaped entry point is
strictly higher in stratum B (no CI) than in stratum A (CI), by at least 5
percentage points.

Every finding in both strata is hand-checked and classified true or false
positive before any rate is computed, as on 2026-07-27, when all three control
findings turned out to be false positives.

Refuted if the rates are equal, if A exceeds B, or if the gap is under 5
points. A refutation would say that review process does not explain the
estate's gap, which strengthens P5's authorship reading. Confirmation says the
opposite: that the 2026-07-27 comparison measured CI, not authorship, and P5
should be read down accordingly.

**Both outcomes damage a claim someone might want to make. That is the point
of running it.**

### P8 — the denominator, which is what actually mattered last time

The headline of this note is that verification-shaped files per repository ran
34.7 in the control against 1.2 in the estate.

**Predicted:** stratum B's density falls between the two, strictly below
stratum A's and strictly above the estate's 1.2.

Refuted if stratum B matches either end. If B is as dense as A, low density is
not a property of unreviewed code and the 28x gap is about something else
entirely.

### P9 — unrun. The door.

Every repository in both strata is human-authored. The estate is
AI-assisted. No stratum in this design isolates authorship with review held
constant, and none is proposed here, because the obvious construction —
AI-assisted repositories with CI — requires a population this project does not
have access to and cannot sample without bias.

### The candidate pool, written before any clone

Twenty repositories. Chosen for being human-authored, Python-majority, and
outside this estate. Listed here in the amendment so that the pool is fixed in
git history before a single `git clone` runs.

Stratum is NOT assigned below. Each repository is cloned, `.github/workflows/`
is inspected, and membership follows that measurement. The two columns of the
pool are the two sampling frames I drew from, not the two strata — a
"expected-CI" repository that turns out to have no workflows moves to stratum
B and is kept.

**Frame 1 — mature, multi-maintainer projects (CI expected)**

1. benoitc/gunicorn
2. pallets/jinja
3. psf/requests
4. celery/celery
5. pallets/click
6. kennethreitz/records
7. mitsuhiko/rye
8. pyca/cryptography
9. tqdm/tqdm
10. python-attrs/attrs

**Frame 2 — smaller, single-maintainer utilities (CI not expected)**

11. kennethreitz/maya
12. kennethreitz/pipenv-old
13. jsvine/pdfplumber
14. mkorpela/pabot
15. dbader/schedule
16. jd/tenacity
17. lepture/mistune
18. bslatkin/effectivepython
19. amoffat/sh
20. gruns/furl

**Weakness, stated rather than hidden.** This list is hand-chosen by Claude
(Anthropic) from recall of well-known Python projects. `api.github.com`
returns 403 from the sandbox that will run the scan, so no star-ranked or
otherwise mechanical sampler was available. Frame 2 in particular is a guess
about which projects lack CI, and that guess is the weakest joint in the
design. It is mitigated, not repaired, by measuring stratum membership after
the clone and by refusing to drop any repository once its finding count is
known.

**Fixed now, before fetching:** a repository that 404s, is a fork, or contains
no Python file is recorded as unavailable with the reason and is NOT replaced.
Replacing a dead entry with a live one after seeing the others' results is a
selection channel and is therefore closed in advance. The pool can only shrink.

---

## Amendment 2 — 2026-11-07. Procedure for running P6/P8, fixed before any pool repository is cloned.

Amendment 1 was registered on 2026-09-06 and never run. This amendment changes nothing it registered: the pool, the
predictions, the 5-point threshold, the stratum rule, the exclusions and the no-replacement rule all stand. It
only fixes how the run is carried out, in places Amendment 1 left open.

**Why now, and what changed since.** The sandbox could not reach GitHub in September; public repositories can now
be cloned. Amendment 1's registration is the one being run. A mechanical sampler would be better, but switching
frames now would quietly replace a registered pool, so it is a separate door (P10 below).

**Instrument.** `vacuity_lint.py` at `a468d2c7005f26a45a985a792fc12bfcf07dc81b`, file sha256 beginning
`7a5b8d100457128f`. Its selftest reported `20/20 checks passed` on 2026-11-07 (container, Python 3.13.18).
The driver refuses to scan unless the hash matches and the selftest prints 20/20. Later versions of the tool
fixed false-positive classes (VLFP001–003). They are not used, because Amendment 1 pinned this commit.

**Driver.** `experiments/note052_p6/run_p6.py`, committed with this amendment, before any clone. Each repository
is cloned shallow at its default branch, and the head SHA and date are recorded. Exclusions are applied by copying
the tree without `examples/` directories and `conftest.py` files, then running the pinned linter on the copy.
"Verification-shaped entry points" is the linter's own `verification-shaped` count.

**Hand-check rules, fixed before any finding is seen.** A finding is **TP** only if both hold:
1. the file is meant to be run as a check or test by its authors (its name, docstring, or how the project invokes
   it says so); and
2. reading the file and anything it imports from the same repository, no input makes the check report failure
   through a nonzero exit, a raised exception, or a pytest/unittest failure.

It is **FP** if the file is not a check (a library module, demo, benchmark, build or docs script), or if a fail
path exists that the linter does not see (for example `unittest.main()`, a fixture or helper that raises, or
`sys.exit(main())`). Each verdict carries a one-line reason.

**Blinding, partial.** Findings are shuffled (seed 52) and listed by ID and file path only. Strata are computed
during the scan, written to `strata.json`, and not read until every finding has a verdict. File paths and contents
can still reveal which project a file comes from, so this blinds the stratum label, not the project.

**Anti-vacuity control.** In the same environment, a planted Type A file (`verify_output.py`, prints PASS/FAIL,
no fail path) must be flagged, and a clean copy must give no findings. Run before registering: PASS.

**Scoring.** As registered. P6 holds if stratum B's TP rate per verification-shaped entry point exceeds A's by at
least 5 points. P8 holds if 1.2 < density(B) < density(A). If either stratum has fewer than 3 repositories, both
are reported as underpowered and no rate claim is made. Any interval or test beyond that is labelled exploratory
and cannot change a verdict.

**Pre-mortem: how this could mislead.**
- The pool was picked by memory, and frame 2 is a guess. A large gap could come from which projects were picked,
  not from CI.
- The heads are 2026 code. "Human-authored" in Amendment 1 meant the projects, not each line; recent commits may
  be AI-assisted. Head dates are recorded so this can be checked.
- One AI does the hand-check. It is blinded to stratum only, and is not independent.
- Counts are small. Strata of 3–10 repositories cannot support a general claim either way.
- `.github/workflows` is the registered definition of CI. A project using another CI service lands in B.

**P10 — unrun, the door.** The same predictions on a mechanically drawn sample from the GitHub search API: Python
repositories with a fixed star band and a fixed push window, drawn before stratum is known. Registered as a door
only.

Provenance (M13): Amendment 2 and driver by Claude (Anthropic, Opus 5.5) → human validation: not performed →
human direction: Chad Holland, 2026-11-07 → human responsibility: Chad Holland. Review level: direction only.

---

## Amendment 2 results — 2026-11-07. P6 and P8: UNDERPOWERED. The registered design cannot test the question.

Raw files: `experiments/note052_p6/results_2026-11-07/` (clone log with head SHAs and dates, scan, strata,
blinded hand-check sheet and key, score). Container, Python 3.13.18. NOT VALIDATED on the S25.

### What went wrong, first

1. **The no-CI frame was wrong.** Of the 19 repositories that could be cloned, **18 have `.github/workflows`**.
   Only `bslatkin/effectivepython` landed in stratum B. Every frame-2 repository but that one moved to stratum A, as
   Amendment 1's rule required. Stratum B has 1 repository, under the registered minimum of 3, so **P6 and P8 are
   UNDERPOWERED and no rate claim is made.** The pre-mortem named this risk ("frame 2 is a guess"); it is what
   happened.
2. **One pool entry was unavailable.** `kennethreitz/pipenv-old` could not be cloned (the URL asks for credentials,
   which GitHub does for a repository that does not exist or is private). Recorded and not replaced, as registered.
3. **The pinned instrument's precision on outside code is poor.** 17 of 18 findings were false positives:
   generated tests the linter cannot see (pytest attributes from `generate_*` helpers; unittest tests built by
   `load_fixtures`), config fixtures named `test_cfg*.py`, library modules, a report generator, and a script that
   fails through a library call that raises. Later versions of the tool address some of these classes; they were
   not used, because the commit was pinned.

### Observations (descriptive only; no stratum comparison)

| | Stratum A (CI) | Stratum B (no CI) |
|---|---|---|
| repositories | 18 | 1 |
| verification-shaped entry points | 596 | 15 |
| findings | 18 | 0 |
| true positives after hand-check | 1 | 0 |
| density (entry points per repository) | 33.1 | 15.0 |

- The one true positive: `celery/celery` `t/unit/bin/test_multi.py` at head `768e476b`, a 0-byte test module. A
  test file with no tests cannot report a failure.
- Across all 19 repositories: 1 true positive in 611 verification-shaped entry points (0.16%).
- Anti-vacuity control, rerun after the scan with the same pinned instrument: the planted file was flagged and the
  clean copy gave no findings (PASS).

### What this does and does not say

- It says that **a hand-picked pool of well-known Python projects cannot supply a no-CI stratum in 2026**: CI
  through GitHub Actions is close to universal among them. The registered design is the problem, not the question.
- It does **not** say anything about whether CI reduces vacuous checks. With one stratum-B repository, there is no
  comparison.
- The 17-of-18 false-positive rate applies to the pinned instrument on mature outside projects. It is not a
  measurement of the current tool.

### The door: P10, now runnable

GitHub's search API is reachable from this environment (checked 2026-11-07), so P10 can be registered concretely:
a mechanically drawn sample from fixed search criteria, with the no-CI stratum filled by measurement, not by
recall. It needs its own registration before any repository is drawn.

Provenance (M13): run, hand-check and write-up by Claude (Anthropic, Opus 5.5); the hand-check was blinded to
stratum, not to project → human validation: not performed → human direction: Chad Holland, 2026-11-07 → human
responsibility: Chad Holland. Review level: direction only.

---

## Amendment 3 — 2026-11-07. P10 registered: a mechanically drawn sample. Nothing drawn yet.

Amendment 2 showed that hand-picking cannot produce a no-CI stratum. P10 draws the sample by a fixed procedure, and
pins each repository to code written before AI coding assistants were common, so "human-authored" means something.

**Question.** Among small public Python repositories, as they stood before 2022-12-01, are checks that cannot fail
more common in repositories without CI?

**Sampling (driver: `experiments/note052_p6/run_p10.py`, committed with this amendment).**
- Query: `language:python stars:20..300 fork:false archived:false size:<100000 created:<month window>`, one
  calendar-month window from 2017-01 to 2021-12.
- Order: seed 1010 picks a window, then a result page (1 to 10, within the result count), then one item. Repeats
  and repositories owned by holland202 are skipped. Up to 400 draws; the candidate list is written to
  `sample.json` and committed **before** any clone.
- Eligibility, in candidate order, until 80 are eligible: it clones; it has a commit before 2022-12-01; the
  pinned tree contains a Python file. Ineligible candidates are recorded with the reason. Eligibility never looks
  at findings.
- Pin: the last commit on the default branch before 2022-12-01. GitHub Copilot was public from mid-2021, so
  "before AI assistance" is approximate, not guaranteed.

**Strata, measured at the pinned commit.**
- **Primary (decides):** A = has CI configuration: `.github/workflows/*.yml|yaml`, `.travis.yml`, `.gitlab-ci.yml`,
  `azure-pipelines.yml`, `appveyor.yml`, `.appveyor.yml` or `.circleci/`. B = none of these.
- **Secondary (reported, does not decide):** GitHub Actions only, as in Amendment 1.

**Instrument.** `vacuity_lint.py` at `b8bb09e0fc30cac3305dc2db99bbce1b8dd3ac9d` (file sha256 beginning
`a92963c69fa129db`), the current tool. Selftest 20/20 is required before scanning. Exclusions as Amendment 1:
`examples/` and `conftest.py`.

**Hand-check.** Amendment 2's TP/FP rules, unchanged, blinded to stratum the same way. If there are more than 150
findings, a seed-1010 random 150 are checked. That limit is fixed now; the verdicts still decide repository counts.

**Predictions.** The unit is the repository. A repository "has a TP" if at least one hand-checked finding in it
is TP.
- **P10a.** The share of no-CI repositories with a TP exceeds the share of CI repositories with a TP by at least 10
  percentage points, and a one-sided Fisher exact test gives p < 0.05. If the gap holds but p ≥ 0.05:
  INCONCLUSIVE. If the gap is under 10 points or reversed: REFUTED.
- **P10b.** No-CI repositories have fewer verification-shaped entry points: lower median, and a one-sided
  permutation test on the Mann–Whitney U gives p < 0.05 (20,000 permutations, seed 1010). Otherwise REFUTED.
- If either stratum has fewer than 10 eligible repositories, both predictions are UNDERPOWERED.
- The sample size and both tests are fixed now; no draws are added after the result is known (C-STAT).

**Anti-vacuity.** The planted-file control with this instrument: PASS (2026-11-07, before registering).

**Pre-mortem.**
- GitHub search ranks by "best match", not at random. Random pages and items within month windows reduce this
  but do not remove it.
- Stars and visibility in 2026 decide who is in the population; repositories deleted since then are invisible.
- One AI hand-checks, blind to stratum only.
- A repository can "have CI" that never ran. Configuration presence is the measure, not CI health.
- If no-CI repositories have very few verification-shaped files, their TP share can be low simply because there is
  little to find. P10b reports the denominator so that reading is visible.

**What either result would mean.** If P10a holds, missing CI goes with more checks that cannot fail, in code that
predates AI assistance, which supports reading note052's estate gap as a review effect. If P10a is refuted,
review process does not explain it in this population. Both outcomes are about software in general, not this
estate.

Provenance (M13): registration and driver by Claude (Anthropic, Opus 5.5) → human validation: not performed →
human direction: Chad Holland, 2026-11-07 → human responsibility: Chad Holland. Review level: direction only.

---

## Amendment 3 results — 2026-11-07. P10a REFUTED. P10b CONFIRMED. Missing CI goes with missing checks, not with broken ones.

Raw files: `experiments/note052_p6/results_p10/`. They include the drawn list (committed before any clone), the
fetch log with pinned SHAs, the scan, the strata, the hand-check sheet and key, the clarification committed before
strata were unsealed, and the score. Container, Python 3.13.18. NOT VALIDATED on the S25.

### What went wrong, first

1. **P10a, the main prediction, is REFUTED.** Repositories without CI were not more likely to contain a check that
   cannot fail: 3 of 61 (4.9%), against 1 of 19 with CI (5.3%). One-sided Fisher exact p = 0.762. The gap is
   reversed by 0.3 points, not 10 points in the predicted direction.
2. **Two driver failures during the draw.** The first draw died on a connection reset with nothing saved
   (deviation 2: transient errors are now retried). A rate-limit retry had been added earlier, before any draw ran
   (deviation 1). Neither changes which repository a draw selects.
3. **The hand-check needed a clarification.** Rule 2 ("no input makes it fail") is too broad as written, because
   almost any script can raise *something*. The rule as applied, in
   `results_p10/HANDCHECK_CLARIFICATION.md`, was committed with all 137 verdicts **before** the strata were read.
   The verdicts were byte-checked unchanged after scoring.
4. **The instrument's precision on this population is low.** 8 of 137 findings were true positives (5.8%). The
   biggest false-positive class, 64 findings, is machine-learning evaluation scripts named `test_*.py` ("tests an
   agent"), which are not code checks. The next 26 are files that do not parse under Python 3.

### Results (primary CI definition; it decides)

| | No CI (B) | CI (A) |
|---|---|---|
| repositories | 61 | 19 |
| with at least one true positive | 3 (4.9%) | 1 (5.3%) |
| with **no** verification-shaped file at all | 35 (57.4%) | 2 (10.5%) |
| median verification-shaped files | 0 | 5 |
| total verification-shaped files | 161 | 199 |

- **P10a REFUTED** (Fisher one-sided p = 0.762).
- **P10b CONFIRMED.** Repositories without CI have fewer verification-shaped files (median 0 against 5;
  permutation test on U, 0 of 20,000 permutations as extreme, so p < 0.00005).
- The GitHub-Actions-only definition (secondary) gives the same verdicts: 65 against 15 repositories, 3 (4.6%)
  against 1 (6.7%) with a true positive, Fisher p = 0.842; median 0 against 6.
- Anti-vacuity control with the same instrument, rerun after scoring: PASS.

**The 8 true positives:**
- Five empty or import-only test modules in `nasa/giant`.
- `tests.py` in `ARBML/tnkeeh`, which compares results and only prints "failed".
- `data_checker.py` in `jtoy/sketchnet`.
- `scripts/constraints/validate.py` in `ofirpress/shortformer`. That repository has CI; the file is a copy of a
  fairseq script, and it prints missing constraints instead of failing.

**Exploratory, not registered (cannot change a verdict).** Per verification-shaped file, true positives are 7 of
161 (4.35%) without CI and 1 of 199 (0.50%) with CI. One repository supplies 5 of the 7, so this rate is
dominated by a single project. That is why the registration used the repository as the unit.

### What this says about software in general

In this sample of small public Python repositories (20–300 stars), each pinned to its last commit before December
2022:
- **Missing CI goes with missing checks, not with checks that cannot fail.** More than half the repositories
  without CI contain no verification-shaped file at all. Where checks exist, the share of repositories with a
  vacuous one is about the same with or without CI (about 5%).
- This matches the note's 2026-07-27 headline in a population that has nothing to do with this estate: the
  difference is the denominator. P10b replicates that pattern in outside code. P10a removes the reading that
  unreviewed code fails its checks more often; in this sample it mostly has none.
- For note052's estate gap (P5), this weakens the review-process explanation of the *rate* and strengthens the
  *density* explanation.

**What it does not say.**
- Nothing about AI-authored code. The sample was pinned before December 2022, and the estate was not compared.
- Nothing causal: CI could be a marker of projects that write tests, not a cause.
- The 80 repositories come from GitHub's "best match" search ranking within random month windows. That is a
  population of discoverable repositories, not a random sample of all Python code.
- One AI hand-checked every finding, blind to stratum only. 4 TP repositories is a small count. With these
  numbers, a true gap of 10 points could have been missed, so "no 10-point gap was seen" is the claim, not "there
  is no gap".

### Doors left open

- **P11 (unrun).** Repeat at the 2026 heads of the same 80 repositories. Did adding CI later go with adding checks?
  This is a within-repository comparison, which removes the selection-between-projects confound.
- **P12 (unrun).** Re-hand-check a random 30 of the 137 findings by a second, independent reviewer and report
  agreement (Cohen's κ). That tests the one-AI hand-check, the weakest joint here.
- **Instrument (unrun).** A rule that separates model-evaluation scripts from code checks would remove 64 of the 129
  false positives in this sample. It would need its own registration and controls.

Provenance (M13): design, draw, run, hand-check and write-up by Claude (Anthropic, Opus 5.5). The hand-check was
blinded to stratum, not to project → human validation: not performed → human direction: Chad Holland, 2026-11-07 →
human responsibility: Chad Holland. Review level: direction only.

---

## Amendment 4 — 2026-11-07. P13 registered: does a decoding defect in the instrument change P10? Nothing rescanned yet.

**Why.** In [vacuity_lint.py PR #32](https://github.com/holland202/vacuity_lint.py/pull/32), ChatGPT (OpenAI)
reports a defect in the instrument P10 used. At `b8bb09e`, `analyse()` reads every file as UTF-8 with
`errors="replace"`. Undecodable bytes become U+FFFD, the file is scanned as if Python could read it, and
encoding declarations are ignored. The PR head reads with `tokenize.open` and reports undecodable source as
UNPARSEABLE. If any of P10's files were affected, P10's numbers could be wrong. The PR is open and unmerged. I have
read its six-line change to `vacuity_lint.py`. I have not reviewed its tests.

**Known before registering (C-EXPLORE).** That diff, and P10's own records. I have not run either linter on a
planted or P10 file for this question, and I have not looked at how P10's files are encoded.

**Instruments.** A = `vacuity_lint.py` at `b8bb09e0fc30cac3305dc2db99bbce1b8dd3ac9d` (sha256 beginning
`a92963c69fa129db`, P10's instrument, selftest 20/20 required). B = the PR #32 head,
`db98e60971452ba2ac1c8a6da3c6118cfc69f80a` (sha256 beginning `a6c8a65d6a9150f6`; its selftest must report all
checks passed). B stands in for the fix (M4). P13 does not certify it.

**Procedure** (driver `experiments/note052_p6/run_p13.py`, committed with this amendment):
1. Rebuild the 80 filtered trees from P10's pinned checkouts. The driver refuses any checkout whose HEAD is not
   the pin in `fetch_log.json`, or which has local changes. The exclusions are P10's.
2. **Census.** Read every `.py` file both ways, A's and B's, and class it:
   - SAME: identical text;
   - BOM: differs only by a leading U+FEFF;
   - DECLARED: an encoding declaration changes the text;
   - UNDECODABLE: B's read raises;
   - UNREADABLE: the file cannot be opened.
3. **Rescan** every tree with A and with B.
4. **Score.** The driver first checks that it reproduces `results_p10/score.json` from P10's own inputs, and
   refuses to score if not. Then it recomputes P10a and P10b from B's scan:
   - A finding that B shares with P10, by (repository, path, category), keeps its P10 verdict.
   - A new UNPARSEABLE finding is FP, by the existing clarification.
   - Any other new finding is left unchecked, and P10a is computed twice: once with all unchecked findings TP,
     once with all FP.

**Predictions.**
- **P13a.** A's rescan reproduces P10's `scan.json` exactly: findings, verification-shaped counts and exit codes.
- **P13b.** Fewer than 1% of the scanned `.py` files are classed other than SAME.
- **P13c.** B's findings differ from P10's by at most 3 (repository, path, category) entries, and no hand-checked
  TP disappears.
- **P13d.** Under both CI definitions and both bounds, P10a stays REFUTED and P10b stays CONFIRMED.

If P13d is refuted, P10's result depends on the defect. This note would then put that first, ahead of P10.

**Anti-vacuity control** (expected results registered here; run after this commit). Each case is P10's planted
file, `verify_output.py`, which prints FAIL but cannot fail:
- **K1:** the file plus a comment holding byte 0xFF on line 3. A reports a finding other than UNPARSEABLE; B reports
  UNPARSEABLE. This shows the comparison can see a difference.
- **K2:** the file as it is. A and B report the same finding, so B does not differ on clean input.
- **K3** (a prediction, not a control): the file with a UTF-8 BOM. A and B report the same thing. I am not sure how
  `ast.parse` treats a leading U+FEFF in a string. If they differ, K3 is recorded as refuted.

**What either result would mean.** If all four hold, the defect is real but did not touch P10, and P10 stands as
reported. If P13c or P13d fails, the P10 numbers are restated from B with the bounds. P10's files stay as they are
(M12).

Provenance (M13): defect found by ChatGPT (OpenAI), vacuity_lint.py PR #32, not rerun by me before this
registration → registration and driver by Claude (Anthropic, Opus 5.5) → human validation: not performed → human
direction: Chad Holland, 2026-11-07 → human responsibility: Chad Holland. Review level: direction only.

---

## Amendment 4 results — 2026-11-07. P13a–P13d HELD. The defect is real, and it did not touch P10. K3 REFUTED.

Raw files: `experiments/note052_p6/results_p13/` (`run.txt`, plus the control, census, both rescans and the
score). `inspect.txt` is a description written after the run, by `inspect_p13.py`, and is not a prediction. The
whole sequence ran twice; all five JSON outputs were byte-identical between the runs. The registration
was committed and pushed at `8a44614` before anything ran. Container, Python 3.13.18. NOT VALIDATED on the S25.

### What went wrong, first

1. **K3 is REFUTED, and it shows a second form of the defect.** Both linters were given P10's planted file with a
   UTF-8 BOM. A reported UNPARSEABLE and B reported NO_FAIL_PATH. Python 3 itself compiles that file's bytes. A
   reads the BOM as a character and passes it to `ast.parse`, which raises `invalid non-printable character
   U+FEFF`. So A's flaw runs both ways:
   - a file Python cannot read gets scanned as if it were clean;
   - a file Python reads fine is called unparseable, and a vacuous check inside it is never reported.
   Under the P10 hand-check rule, UNPARSEABLE is FP, so a BOM file would have been dropped silently. ChatGPT's PR
   says it handles BOMs. This is the first run of that case against P10's instrument.
2. **One P10 file was affected.** `kersaSoftmax/gruTrain.py` in `wangleiai/dVectorSpeakerRecognition` has no
   encoding declaration, and its first invalid UTF-8 byte is at offset 716, line 23 (`results_p13/inspect.txt`). The
   bytes are valid GBK, which suggests Chinese text saved in a GBK encoding. Nothing else about that was checked.
   Python 3 refuses to compile the file (`SyntaxError: (unicode error) 'utf-8' codec can't decode byte`). A scanned
   it and reported nothing. B reports it UNPARSEABLE.

### Results

```
K1: A ['NO_FAIL_PATH']  B ['UNPARSEABLE']
K2: A ['NO_FAIL_PATH']  B ['NO_FAIL_PATH']
K3: A ['UNPARSEABLE']  B ['NO_FAIL_PATH']
census: 2363 .py files; {"SAME": 2362, "UNDECODABLE": 1}; not SAME 1 (0.042%)
rescanned 80: A findings 137, B findings 138
unchecked_FP primary: TP repos B 3/61, A 1/19, Fisher p 0.762, medians 0 vs 5, perm p 0.0: P10a REFUTED, P10b CONFIRMED
unchecked_FP gha_only: TP repos B 3/65, A 1/15, Fisher p 0.842, medians 0 vs 6, perm p 0.0: P10a REFUTED, P10b CONFIRMED
unchecked_TP primary: TP repos B 3/61, A 1/19, Fisher p 0.762, medians 0 vs 5, perm p 0.0: P10a REFUTED, P10b CONFIRMED
unchecked_TP gha_only: TP repos B 3/65, A 1/15, Fisher p 0.842, medians 0 vs 6, perm p 0.0: P10a REFUTED, P10b CONFIRMED
```

| | prediction | result |
|---|---|---|
| K1 | control: the comparison can see a difference | PASS |
| K2 | control: B agrees with A on clean input | PASS |
| K3 | a BOM makes no difference | **REFUTED** (above) |
| P13a | A's rescan reproduces P10's `scan.json` | HELD |
| P13b | under 1% of `.py` files decode differently | HELD: 1 of 2,363 (0.042%), and no BOM or DECLARED file |
| P13c | at most 3 findings change; no TP disappears | HELD: one new UNPARSEABLE finding (FP by rule); none gone |
| P13d | P10a REFUTED and P10b CONFIRMED under both definitions and both bounds | HELD |

No verification-shaped count changed. The one new finding is UNPARSEABLE, so no finding was left unchecked and the
two bounds are identical. The score step reproduced P10's committed `score.json` from P10's inputs before it scored
anything.

### What this does and does not say

- **P10 stands as reported.** The decoding defect touched one file in 2,363. It is not named like a check, and
  no repository's verification-shaped count changed.
- **The defect is real on P10's instrument.** K1 reproduces ChatGPT's undecodable case. K3 adds the BOM case: a
  vacuous check in a BOM file is invisible to `b8bb09e`. On another population, especially Windows-edited code,
  that could matter. This sample had no BOM files.
- **Not shown:** that PR #32 is correct in general. B was used only for these two reads, and its own tests were not
  reviewed. Whether to merge it is Chad's decision.
- **Door (unrun).** How often do BOM or non-UTF-8 files occur among verification-shaped files in a population
  where Windows editors are common? This sample had none. P11, if it runs, should pin a linter that handles both
  cases.

Provenance (M13): defect reported by ChatGPT (OpenAI) in vacuity_lint.py PR #32; this run reproduces its
undecodable case on P10's instrument and adds the BOM case → run and write-up by Claude (Anthropic, Opus 5.5) →
human validation: not performed → human direction: Chad Holland, 2026-11-07 → human responsibility: Chad
Holland. Review level: direction only.

---

## Amendment 5 — 2026-11-07. P11 registered: the same 80 repositories at their 2026 heads. Nothing measured yet.

**Question.** Within the same repositories, did adding CI after 2022 go with adding checks? Comparing a repository
with itself removes the between-project confound that P10 could not.

**Known before registering (C-EXPLORE).**
- P10's and P13's records at the pins.
- That P10's clones hold each default branch as cloned on 2026-11-07, with `origin/HEAD` set. I looked at one
  clone, `ARBML/tnkeeh`, for the ref layout only.
- Nothing about any head: not its CI, its files, or how many commits it has after the pin.

**Head.** `origin/HEAD` in P10's partial clone: the default branch as cloned on 2026-11-07.

**Instrument.** `vacuity_lint.py` with sha256 beginning `a6c8a65d6a9150f6`. That is the vacuity_lint.py PR #32
head (`db98e60`), and also the file a merge of #32 into main produces (checked locally: identical bytes). Its
selftest must pass. It measures pins and heads alike. P13 showed that its counts at the pins equal P10's. The driver
(`experiments/note052_p6/run_p11.py`, committed with this amendment) re-measures each pin, and stops if the CI
result or the count disagrees with P10's records (fail-closed).

**Measures.** At the pin and at the head:
- CI, by P10's primary definition. The GitHub-Actions-only definition is not used here.
- The verification-shaped count, with P10's exclusions.

Δ = count at head − count at pin. Transition = CI at pin, then CI at head: AA, AB (CI removed), BA (CI added) or BB.

**Exclusions, fixed now.** A repository is left out, and listed with its reason, if:
- its head cannot be checked out;
- the linter reports no count at the head (for example, no Python file left);
- the pin is not an ancestor of the head; or
- there is no `origin/HEAD`.

**Predictions.**
- **P11a.** Among repositories without CI at the pin, those that added CI (BA) gained more verification-shaped
  files than those that did not (BB). Test: a higher median Δ, and a one-sided permutation test on the Mann–Whitney U
  with p < 0.05 (20,000 permutations, seed 1010). If BA or BB has fewer than 8 repositories, P11a is UNDERPOWERED.
- **P11b.** At least half the measured repositories have no commit after the pin.
- **P11c.** At most 2 repositories removed CI (AB).
- **Secondary (reported, does not decide).** BA against only the BB repositories with at least one commit after the
  pin, by the same test. Adding CI takes a commit, so every BA repository is active. This comparison asks whether
  activity alone explains a difference.

**Anti-vacuity control** (to run after this commit). Two planted git repositories go through the same per-repository
code:
- one adds a workflow file and a test file after its pin: expected BA, Δ = +1;
- one adds only a README: expected BB, Δ = 0.

**Pre-mortem.**
- Many of these small repositories may have been dormant since 2022. BA would then be small and P11a UNDERPOWERED.
  That would be a finding about the population, not a failure of the method.
- BA repositories are active by definition. Activity can drive both CI and tests, and the secondary comparison only
  partly separates them.
- Verification-shaped files can arrive by vendoring or copying, not only by someone writing checks.
- Heads contain code from 2023–2026, when AI coding assistants were common. Nothing here measures who or what wrote
  it.
- Findings at the heads are not hand-checked. Their counts are reported as unchecked and decide nothing.

**What either result would mean.**
- If P11a holds, repositories that took up CI also took up checks, within the same project. That supports reading
  P10b's density gap as something that moves together with CI, though still not as a cause.
- If it is refuted, adding CI did not come with more checks in this sample.
- If it is underpowered, too few of these repositories changed for the question to be asked of them.

Provenance (M13): registration and driver by Claude (Anthropic, Opus 5.5) → human validation: not performed →
human direction: Chad Holland, 2026-11-07 → human responsibility: Chad Holland. Review level: direction only.

---

## Amendment 6 — 2026-11-07. P12 registered: a second reviewer for P10's hand-check. Nothing drawn yet.

**Why.** P10's verdicts came from one AI (me), blinded to stratum only, and that is P10's weakest joint. P12
measures how far a second reviewer agrees when it applies the same written rules.

**Reviewer.** ChatGPT (OpenAI), in the auditor role of the Claude–ChatGPT coordination protocol, at Chad Holland's
direction (2026-11-07). The driver (`experiments/note052_p6/run_p12.py`, committed with this amendment) accepts
ratings from any reviewer, so a human reviewer can be added later as a separate run.

**Sample.** `run_p12.py draw`, seed 1212, picks 30 of P10's 137 findings. They are given ids R01–R30 in shuffled
order and written to `results_p12/PACKET.md`, with a link to each file at its pinned commit and P10's rules. The
packet contains no verdicts. The 30 are random, as the P10 door said. With 8 TPs in 137, the sample should hold
about 2 TPs, and it could hold none.

**Custody, stated plainly.** My verdicts are already public, in `results_p10/handcheck.json`, and Amendment 3's
results name the 8 TPs. The reviewer is asked to rate before opening either, and to declare whether it had read them
before rating. Blindness therefore rests on the reviewer's own report. If the reviewer had already read the list of
TPs, P12 is reported as not blind.

**Predictions** (scored by `run_p12.py score`, committed now):
- **P12a.** The reviewers agree on at least 27 of the 30 findings.
- **P12b.** Cohen's κ ≥ 0.6. If either reviewer uses only one label across the 30, κ is undefined and P12b is
  UNDETERMINED.
- Every disagreement is listed with both reasons. I resolve none of them; they go to Chad.

**What this cannot show.** Agreement between two AI systems is not human validation. Agreement does not make a
verdict correct. If ChatGPT and I share a blind spot, P12 cannot see it.

Provenance (M13): registration and driver by Claude (Anthropic, Opus 5.5); reviewer ChatGPT (OpenAI), not yet run
→ human validation: not performed → human direction: Chad Holland, 2026-11-07 → human responsibility: Chad
Holland. Review level: direction only.
