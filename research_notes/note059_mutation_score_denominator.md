# Note #059 — A mutation score without its denominator is not a measurement

**Status:** Draft, verified reference code
**Theme:** Verification / vacuity detection
**Author:** Chad Edward Holland, with Claude (Anthropic, Opus 4.6)
**Builds on:** [[note057_the_loud_type_a]], [[note052_verification_that_cannot_fail]], [[note058_kv_vacuity]]

## What failed first

The registered gate in this note's own reference script **failed on its first
run**, and it failed because of the author's fixtures, not the tool.

Every fixture scored 0.0%, including one built specifically to score 100%. The
cause: a comparison-boundary mutation (`>=` → `>`) only changes behaviour when
the operand sits **at** the boundary. The fixtures used `value = 5, limit = 10`,
so both the original and the mutant took the same branch. Moving the operands
to `value = 10, limit = 10` made the same fixtures behave as intended.

This is a second confound underneath the one the note was written to record:
**a surviving mutant can mean the input never exercised the boundary, rather
than that the code is vacuous.** Mutation survival is evidence about the pair
(code, input), never about the code alone. The gate caught this before any
number reached prose, which is what a gate is for.

**P3 was also refuted** — see below. It is kept.

## The claim

[[note057_the_loud_type_a]] left an open question: is the *loud* variant of
Type A detectable at all, given that it requires reachability analysis rather
than token presence? `vacuity_lint.py` asks whether a reachable nonzero exit
exists. `mutation_probe.py` asks the harder question — whether the verdict
depends on the logic it claims to check.

The claim here: **mutation score answers note057's question, but the score
alone is not a verdict.** It is a ratio, and the denominator — how many
eligible mutation sites the file contains — carries as much information as the
ratio does. Reported without it, the score is not falsifiable.

## Epistemic status

Mutation testing is established (Kupferman/Li/Seshia, FMCAD 2008; the ACTL
vacuity line from Beer/Ben-David/Eisner/Rodeh; the operator sets in mutmut and
PIT). Nothing here is new mathematics. What is new is a small controlled
before/after on a corpus with **known ground truth**, because the defects and
their fixes were both produced deliberately, on 2026-08-16, and both SHAs are
recorded. The external corpus numbers below were produced by the real tool, not
by this note's reference script; the reproduction commands are given so anyone
can re-derive them.

## The corpus (external — not reproduced by the reference script)

Two files in `sovereign-suite` were Loud Type A at `a1c990d` and gated at
`33ad55e`. Reproduce with:

```
git show a1c990d:verify_quantum_claims.py > pre.py
git show 33ad55e:verify_quantum_claims.py > post.py
python3 mutation_probe.py pre.py --timeout 60
python3 mutation_probe.py post.py --timeout 60
```

Measured, verbatim:

| target | baseline exit | mutants | killed | survived | score |
|---|---|---|---|---|---|
| `verify_quantum_claims.py` @ `a1c990d` | 0 | 7 | 0 | 7 | 0.0% |
| `verify_quantum_claims.py` @ `33ad55e` | 0 | 7 | 2 | 5 | 28.6% |
| `engine_diagnostic_patch.py` @ `33ad55e` | 0 | 1 | 0 | 1 | 0.0% |

The first two rows are the result: **same file, same mutation set, same
denominator (7), score moves 0.0% → 28.6% across a fix whose ground truth is
known.** The operator is held fixed; only the exit wiring changed. That is
affirmative evidence that the loud variant is detectable.

The third row is not evidence of anything. 317 lines produced **one** eligible
mutation. At n = 1, 0.0% and 100.0% are one coin-flip apart.

## Registered predictions

Registered before the run, against fixtures built inside the reference script.

**GATE (anti-vacuity, not a prediction).** The operator must separate LOUD from
GATED — two fixtures with identical logic differing only in whether the verdict
reaches the exit code — at equal mutant count. If it cannot, it is measuring
nothing and **no prediction is reported in either direction**, exit 1.

Measured: `equal mutant counts: True (1 vs 1)`, `LOUD=0.0% and GATED>0.0%:
True`, `GATE PASS`. Sabotage-proven: making GATED byte-identical to LOUD gives
`GATE FAILED` and exit 1.

**P1 — CONFIRMED (external).** A Loud Type A scores 0.0% and its fix scores
above 0.0% at fixed denominator. Corpus rows 1–2 above: 0.0% → 28.6%.

**P2 — CONFIRMED.** At n = 1 the score cannot distinguish a vacuous file from a
correctly gated one. Two fixtures, both correctly gated, both n = 1:

```
  SPARSE_LOAD  baseline_exit=0  mutants= 1  killed=1  survived=0  score=100.0%
  SPARSE_DEAD  baseline_exit=1  mutants= 1  killed=0  survived=1  score=0.0%
```

Both are gated. The score separates them anyway. A low score at small n is
evidence of a small denominator, not of vacuity.

**P3 — REFUTED (kept).** Registered: *a correctly gated file still leaves
survivors, so an exit code keyed to "any survivor" fires on correct code too.*

Measured: `GATED survived=0` — the fixture left none. Refuted as registered.

What the failure taught: the fixture has exactly one comparison and it is
load-bearing, so it **structurally cannot** exhibit the phenomenon. The corpus
does — post-fix `verify_quantum_claims` leaves 5 survivors beside its 2 kills.
The claim appears true of real files and false of minimal fixtures. A minimal
fixture cannot demonstrate a property that only appears at scale, and building
one that "passes" would have meant fitting the fixture to the claim.

The practical consequence stands regardless: `mutation_probe.py` currently
exits 1 whenever any mutant survives, so the *fixed* file also exits 1. It
cannot gate CI without a score threshold — and per P2, a threshold is only
meaningful once n is reported alongside it.

## Reference code

`scripts/note059_reference.py`. Stdlib only. Builds every fixture, implements a
minimal comparison-boundary operator, prints every number above that is not
marked external. Exit 0 when the gate passes — including when a prediction is
refuted, because a refutation is a kept finding and not a build failure. Exit 1
only when the gate fails.

## Falsifiable next predictions

**P4 — OPEN, NOT RUN.** Does the 0.0% → nonzero shift reproduce on a large
target? `calibrate_governance.py` is 1,071 lines at `a1c990d` and 1,125 at
`33ad55e`, same Loud Type A fixed the same day. Not run here because every
mutant re-runs a full calibration. If the shift does *not* appear, the vqc
result is a small-file artifact.

**P5 — OPEN, NOT RUN.** Does reporting n alongside the score change any verdict
already recorded in this estate? 11 vacuity findings across 180 Python files
were scored by presence, not by reachability.

## Amendment 1 (2026-08-21) — P4 answered, and a new confound found

**P4 — REFUTED (kept).** Registered: does the 0.0% → nonzero shift reproduce
on a large target? Tested against `calibrate_governance.py` in
`sovereign-suite`, same commit pair that fixed the note's own corpus file
(`a1c990d` pre-fix → `33ad55e` post-fix). Measured on device:

| target | commit | baseline exit | mutants | killed | survived | score |
|---|---|---|---|---|---|---|
| `calibrate_governance.py` | `a1c990d` | 0 | 87 | 2 | 85 | 2.3% |
| `calibrate_governance.py` | `33ad55e` | 1 | 91 | 2 | 89 | 2.2% |

The exit-wiring fix was real and comparable to the vqc fix — baseline itself
correctly shifted 0 → 1 (Loud Type A → reaches an "UNHEALTHY, exit 1"
verdict; matches the commit's own claim of "shipped defaults rc=1, 3
issues") — but the mutation score did not move. Refuted as registered: the
vqc jump does not generalize to this target. Whether that is a property of
file size, or of what fraction of a large file's comparisons sit on the
verdict path versus in unrelated machinery (thermal monitoring, mock
engines, argument parsing), is not established by n=2.

**MASKED-CRASH CONFOUND, found while checking why.** One SURVIVED result
(`args.out or f"..."`, post-fix line 1095) was hand-verified to be a real
crash, not a non-dependency: mutating `or` to `and` makes `out` evaluate to
`None` when `--out` is unset (the default, and what both runs above used);
`open(None, "w")` then raises an uncaught `TypeError`; Python's default
crash exit status is 1, which happens to equal this target's own legitimate
"UNHEALTHY" exit code — also 1. Exit-code-only comparison cannot distinguish
"correctly computed failure" from "blew up before computing anything." The
mutation was completely load-bearing — the crashed run never even reaches
`save_report` or the verdict block — and it scored as if it were not.

`mutation_probe.py` fixed same day: `run_source` now also reports whether
stderr shows an uncaught traceback, and `probe` verdicts a mutant KILLED if
either the exit code changes OR the crash-state changes, even at matched
exit code. New selftest Fixture C encodes the exact confound (baseline
exits 1 deliberately via a clean `sys.exit(1)`, mutant exits 1 via an
uncaught `AttributeError`) and is sabotage-proven: the unpatched tool
reports Fixture C SURVIVED (wrong), the patched tool reports it KILLED.
Targeted re-check of the one discovered real-world site confirms the fix
against the actual target, not just the synthetic fixture: same mutation,
same file, now correctly verdicts `KILLED (masked -- crash introduced)`
instead of `SURVIVED`.

**What this does NOT establish:** whether the other 88 SURVIVED results in
the post-fix run are genuine non-dependencies or more instances of the same
masking artifact. Re-running the full sweep with the fixed tool costs
roughly the same ~2.5 hours the original run did; not done here.

**P6 — OPEN, NOT RUN.** Re-score `calibrate_governance.py` at both commits
with the fixed `mutation_probe.py`. Does the corrected score move enough to
change P4's verdict, or does it stay near-zero — confirming the flat score
is real and not an artifact of the instrument that measured it?
