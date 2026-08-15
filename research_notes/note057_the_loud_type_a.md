# note057 — The Loud Type A: a guard that announces the failure and passes

**Status:** Draft, verified reference code ⚠ refutation kept
**Reference code:** `scripts/note057_reference.py`
**Contributors:** Chad Edward Holland; Claude (Anthropic) — analysis, fixtures, and the refuted framing below.

---

## The refutation, first

The framing this note started from was **wrong, and it was mine.**

Working through the estate on 2026-08-14 I found three checks that could not
fail, and claimed they formed a third defect category beyond
[[note052_verification_that_cannot_fail]]'s Type A (no fail path) and Type B
(unreachable fail path). I called it *detection without consequence*: the check
computes the correct verdict and discards it.

Then I ran `vacuity_lint.py` against the two Python cases before their fix:

```
python files scanned    : 5
verification-shaped     : 2
findings                : 2
declared intentional    : 0

NO_FAIL_PATH  (2)
  igar/test1_coverage_survives_throttle.py
      verification-shaped but has no assert, raise, test function, or nonzero exit
  igar/test2_honest_failure.py
      verification-shaped but has no assert, raise, test function, or nonzero exit
```

The detector caught both, correctly, as **Type A**. There is no third category
here. A file with no `assert`, no `raise` and no nonzero exit is Type A whether
it says nothing about the failure or shouts about it. The claim is refuted and
is kept here rather than deleted, because what survives it is more useful than
what it replaced.

---

## What survives: severity varies within Type A

Two files can be identically classified and differ enormously in how they
mislead a reader. `scripts/note057_reference.py` builds three fixtures and runs
them:

```
  quiet  Type A   exit 0   alarm words in output: 0
  loud   Type A   exit 0   alarm words in output: 2
  gated           exit 1   alarm words in output: 3
  P1: CONFIRMED -- loud exits 0 while printing 2 alarm words
```

The `loud` fixture is the shape of `igar/test2_honest_failure.py` as it stood
before 2026-08-14. Under sabotage it printed:

```
Result: DANGER: returned {'Z1'} -- verify this is actually valid!
Double-checking validity directly: False
EXIT=0
```

It detected the wrong answer. It announced the wrong answer in alarming
language. It then ran an **independent** re-derivation confirming the answer was
invalid — and exited 0.

A silent Type A is useless. A loud Type A is worse than useless, because its
output is evidence of diligence. A reader scanning a log sees a check that
found something, investigated it, and reported. The `EXIT=0` is the only part
that carries downstream, and it says everything is fine. **The failure mode is
not the missing exit — it is the manufactured impression of rigour.**

A detector cannot see this. `NO_FAIL_PATH` is the same verdict for both, and
correctly so. The distinction is in the reader, not the file.

---

## Registered predictions

- **P1 — CONFIRMED.** A check can detect a real failure, announce it,
  independently re-verify it, and still exit 0.
- **P2 — CONFIRMED.** Severity varies within Type A: `quiet` and `loud` are the
  same class to a detector and different to a reader.
  `same exit code (0 vs 0), different reader signal: CONFIRMED`
- **P3 — ANTI-VACUITY, PASS.** The probe must be able to return null. A properly
  gated check must not be reported as defective.
  `gated exit code: 1 (expected 1 -- verdict propagated)`
  The instrument distinguishes gated from ungated; it does not flag everything.
- **P4 — CONFIRMED, and it caught the author.**

```
  direct         -> exit 1
  piped to tail  -> exit 0
  P4: CONFIRMED -- a verification harness that pipes its subject cannot see the subject fail
```

  While verifying the *fix* to the two igar tests, the first check used
  `python3 test.py | tail -3; echo $?`. A shell pipeline reports the status of
  its last command, so all four runs reported exit 0 and the fix would have been
  declared proven on evidence that could not have distinguished success from
  failure. The verification of the anti-vacuity fix was itself vacuous. Caught
  by re-running without the pipe.

---

## Where the detector genuinely cannot look

`vacuity_lint.py` scans `.py` files. The CI layer is outside its denominator
entirely, and two of the three cases lived there:

- `principia-artificialis/.github/workflows/ci.yml` — sole step
  `echo "Basic CI setup"`, running on every push and pull request to main,
  producing a green check that could not fail. Invisible to the scanner.
- `vacuity_lint.py/.github/workflows/gate.yml` — scan step ended in
  `|| echo "Findings detected; review above"`. The scanner returns 1 on findings
  by design; its own docstring says *"Exit 0 when nothing is found, 1 when
  findings exist, so it can gate a repo."* The workflow discarded it.

Reproduced with the scanner's own defect fixture:

```
bare scan                       EXIT 1   PRINTS_FAIL_ONLY (1)  ./vacuous_demo.py
same command through gate.yml   EXIT 0   "Findings detected; review above"
```

Estate-wide measurement, 13 public repositories cloned at HEAD on 2026-08-14:

| quantity | value |
|---|---|
| repositories cloned | 13 |
| repositories with any workflow | 4 |
| workflow files total | 5 |
| grep matches for `\|\| echo`, `\|\| true`, `continue-on-error: true` | 2 |
| genuine discards after inspection | **0** |

Both matches were benign, and the inspection matters more than the count.
One is the *comment text* in the repaired `gate.yml` describing the old defect —
a fix that mentions the bug it fixed will match a grep for the bug. The other is
`sentinel-batadal-validation/.github/workflows/verify.yml`, where `|| true` is
deliberate and labelled *"Math audit (exits 1 by design — pin the finding
count)"*; the step then runs
`grep -F "16 properties tested, 3 flaws found" audit_out.txt`, so it still fails
if the count changes. **A crude pattern match produces a finding count that is
100% false positives here.** That is the same error class as the note's own
refuted framing: a signal read without inspecting what produced it.

---

## Open, unrun

`ci.yml` was invisible to `vacuity_lint.py` because it is not Python. Extending
the scanner to YAML workflows is one obvious move, but the harder question is
whether the *loud* variant can be detected at all. A candidate rule: flag any
file that emits failure-associated text on a code path which cannot reach a
nonzero exit. That is stricter than `PRINTS_FAIL_ONLY` — it demands reachability
analysis rather than token presence, and it would need its own anti-vacuity
control on a gated file that legitimately prints "FAIL" before exiting 1.

Unrun. No implementation, no false-positive rate, no denominator.

---

*Vincit Omnia Veritas.*
