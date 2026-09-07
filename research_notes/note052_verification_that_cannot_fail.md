# Note 052 — Verification That Cannot Fail

**Status:** Draft, verified reference code
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
