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

> **⚠ QUALIFIED by Amendment 4 (P11).** This sentence claims more than P1
> registers. P1 is directional — the score moves above 0.0% at fixed
> denominator — and that stands. The *magnitude* does not: at n = 7 the 95%
> Clopper-Pearson intervals are [0.00%, 40.96%] and [3.67%, 70.96%], which
> overlap across most of their range. The fix is real and was made
> deliberately; the score is not what establishes it. Kept, not deleted.

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

## Amendment 2 (2026-08-21) — P6 answered, P4's refutation survives

**P6 — RESOLVED.** Re-scored both commits with the crash-detecting
`mutation_probe.py` (`a468d2c`). Measured on device, both runs in parallel:

| target | commit | killed | survived | errored | score |
|---|---|---|---|---|---|
| `calibrate_governance.py` | `a1c990d` | 2 | 85 | 0 | 2.3% |
| `calibrate_governance.py` | `33ad55e` | 3 | 87 | 1 | 3.3% |

**P4's refutation stands, and is now known to be real rather than
instrumental.** The corrected scores are 2.3% → 3.3%; the vqc-style jump
(0.0% → 28.6%) still does not reproduce. The flat result was not an artifact
of the broken oracle that first measured it. This is the outcome P6 was
registered to distinguish, and it came out on the side that makes P4 worse
news, not better.

**Scope of the masked-crash confound, now quantified.** Exactly one survivor
was reclassified: post-fix `survived` fell 89 → 87 and `killed` rose 2 → 3
(the third moved to `errored`, see below). That one is the `args.out or f"..."`
site already hand-verified in Amendment 1. The pre-fix run is byte-identical
to its P4 result — 2 killed, 85 survived, 2.3%, unchanged. So across 176
mutants over two file versions, the confound masked **one**. It is a real
defect in the instrument and worth having fixed; it was not concealing a
population of missed kills. Recording this because the opposite would have
been the more flattering finding and is not what the numbers say.

**One mutant unresolved.** Post-fix line 513, `was_rejected=True → False`,
exceeded the 180 s timeout and is reported `ERROR`, not a verdict. The 3.3%
is therefore computed over 90 resolved mutants, not 91. The same site
returned SURVIVED at the same timeout during the P4 run, so the difference
may be load (both probes ran in parallel on a thermally-throttling phone) —
but line 513 sits in the Fisher-threshold rejection path, and flipping
`was_rejected` to `False` records every rejected crystallization as accepted,
which plausibly lengthens the calibration loop on its own merits. Load versus
genuine slow-down is not distinguished here and is not claimed either way.

**P7 — OPEN, NOT RUN.** Re-run post-fix line 513 alone at a longer timeout,
sequentially rather than in parallel. Does it resolve to KILLED, SURVIVED, or
genuinely not terminate? A mutation that makes a governance loop run
unboundedly is a different finding from one it ignores.

## Amendment 3 (2026-08-27) — P7 answered, and this note's own denominator narrowed

**P7 — RESOLVED, in two parts, because the answer depends on how the target
is invoked.**

Registered: re-run post-fix line 513 alone at a longer timeout, sequentially
rather than in parallel. KILLED, SURVIVED, or genuinely non-terminating?

Line 513 is `record_crystallization(lv, 0.0, was_rejected=True)`, inside
`if lv < self.tc.fisher_threshold:`. It is eligible site index **86** (line
513, col 76, `True -> False`) and the only eligible site on that line.

*Under the invocation `mutation_probe.py` actually uses — no arguments — the
answer is vacuous.* Three sequential trials at a 900 s timeout: baseline
rc 1, mutant rc 1, no crash either side, 0.20 s / 0.21 s / 0.45 s. All
SURVIVED. But the run's own report gives `fisher_fail_count: 0`,
`total_crystallizations: 0`, `total_rejections: 0`. The branch is never
taken. The mutation lands on dead code, and dead code always survives.

The 180 s ERROR recorded in Amendment 2 was **load, not slow-down**.
Sequential runs complete in under half a second. Amendment 2 declined to
claim either way; the answer is load.

*Under `--sweep` the line executes, and the answer is real.* Baseline rc 0,
no crash, 467.8 s. Mutant rc 0, no crash, 445.9 s. **SURVIVED on live code.**

That is the finding. Flipping `was_rejected=True → False` records every
Fisher-rejected crystallization as accepted — inverting the tool's own
rejection bookkeeping — and the sweep runs to completion with an unchanged
exit code. The verdict is insensitive to the accounting it reports on.

Recorded without interpretation: the mutant ran ~5% faster than baseline
(445.9 s vs 467.8 s), directionally consistent with skipping rejection
bookkeeping, but n = 1 on a thermally-throttling device. Not a claim.

**THE DENOMINATOR IN THIS NOTE'S TITLE WAS NOT THE LAST ONE.**

This note argues that a score reported without its denominator is not
falsifiable, and takes the denominator to be the count of eligible mutation
sites. Chasing P7 showed that count is itself insufficient by the note's own
reasoning: a mutation on a line the target never executes cannot change the
exit code, so it is recorded SURVIVED by construction, whatever the quality
of the target's checks.

Measured on `calibrate_governance.py` at `33ad55e`, intersecting
eligible-site line numbers with lines a traced run actually executed:

| invocation | eligible | reachable | unreachable |
|---|---|---|---|
| (no arguments) | 91 | 25 | 66 |
| `--sweep` | 91 | 30 | 61 |

`mutation_probe.py` invokes its target with no arguments. So every corpus
number in this note was measured under the 25-site invocation: 66 of 91
mutants could not fire regardless of what the target does.

Amendment 2's 3.3% is 3 killed / 90 resolved. Over reachable sites it is
3 / 25 = **12.0%**.

Neither figure is wrong as arithmetic, and the tool computed 3.3% correctly.
What was wrong is the reading. "The mutation score is flat" was taken as
evidence about the strength of the target's checks; most of it was evidence
about which lines a no-argument run touches. P4's refutation is unaffected —
both commits were scored the same way, and the comparison stands — but the
*explanation* offered in Amendment 1 for why the score stayed flat ("what
fraction of a large file's comparisons sit on the verdict path versus in
unrelated machinery") is now measured rather than speculated: 66 of 91.

The corpus row that changes most is one already flagged as weak.
`engine_diagnostic_patch.py` @ `33ad55e` produced one eligible mutation and
0.0%, and the note says at n = 1 that is not evidence of anything. Whether
that single site is *reachable* was never asked. If it is not, the row is
not weak evidence — it is none.

**What the tool already said, and what it did not.** `mutation_probe.py`
prints, after any surviving mutant, that the mutation may have landed
"somewhere unreachable from the verdict path," and that a low score is a
place to look rather than a proven defect. That caveat is real, correct, and
was in the output the whole time. What the tool does not do is **measure**
it — no coverage pass, no reachable denominator, and `score` computed over
all sites. The gap here is between a prose warning and a number, and this
note read past the warning across two amendments. A caveat present in the
output and absent from the interpretation is a caveat that did not work.

**Anti-vacuity control for the reachability filter.** A filter that reports
unreachable sites on every input measures nothing. Added as a second gate in
`scripts/note059_reference.py`, independent of the existing LOUD/GATED gate;
both must pass or no prediction is reported in either direction:

```
full_cov.py    eligible=3 reachable=3 unreachable=0
partial_cov.py eligible=6 reachable=3 unreachable=3
returns null on full coverage       : True (expected True)
returns non-null on partial coverage : True (expected True)
```

Sabotage-proven in both directions: forcing the filter to treat every site
as reachable fails the signal direction and exits 1; forcing it to treat
every site as unreachable fails the null direction and exits 1.

**P5 — SHARPENED, still open.** P5 asked whether reporting n alongside the
score changes any verdict already recorded in this estate. It should now be
read with the stronger denominator: not "was n reported," but **what
fraction of each target's eligible sites is reachable under the no-argument
invocation `mutation_probe.py` uses.** If the 25/91 pattern holds across the
estate, every published mutation score here carries the same correction. If
it does not, `calibrate_governance.py` is unusual and this is a finding
about one file rather than about the tool. NOT RUN.

**P8 — OPEN, NOT RUN.** Is `engine_diagnostic_patch.py`'s single eligible
site reachable under a no-argument run? One command answers it, and it
decides whether that corpus row is weak evidence or no evidence.

Reproduce the reachability numbers:

```
cd sovereign-suite/tools
python3 -m trace --count --coverdir=$HOME/cov calibrate_governance.py
# then intersect eligible-site line numbers with the .cover hit lines
python3 scripts/note059_reference.py   # both gates + fixture values
```


## Amendment 4 — the intervals, and what they bound

**The n = 1 argument this note already makes was qualitative. It is now a
number.** Above, the third corpus row is dismissed because "at n = 1, 0.0% and
100.0% are one coin-flip apart." The exact Clopper-Pearson interval for 0/1 is
[0.00%, 97.50%] — 97.50% of the unit interval. The reasoning was right; the
bound makes it checkable.

Applying the same instrument to the first two rows costs something. The
sentence above the registered predictions — "that is affirmative evidence that
the loud variant is detectable" — claims more than P1 does. P1 registers a
*directional* result and the corpus satisfies it. The *magnitude* 0.0% → 28.6%
is not resolvable at n = 7: the intervals are [0.00%, 40.96%] and
[3.67%, 70.96%] and overlap heavily. P1 stands as registered. The prose
overstates it, and is marked in place rather than rewritten.

### Why Amendment 4 and not Amendment 3

P5 already forward-references Amendment 3 as the reachability correction —
what fraction of eligible sites the no-argument invocation actually reaches,
measured at 25 of 91 on `calibrate_governance.py`. That run has not happened.
Resolving an existing forward reference to different work would be exactly the
drift this note exists to prevent, so intervals take the next free slot and
Amendment 3 stays reserved.

### Measured intervals

n is the count of **eligible** mutation sites, the denominator as published.

| target | k/n | score | 95% CI | width |
|---|---|---|---|---|
| `engine_diagnostic_patch.py` | 0/1 | 0.00% | [0.00%, 97.50%] | 97.50% |
| `verify_quantum_claims` pre-fix `a1c990d` | 0/7 | 0.00% | [0.00%, 40.96%] | 40.96% |
| `verify_quantum_claims` post-fix `33ad55e` | 2/7 | 28.57% | [3.67%, 70.96%] | 67.29% |
| `calibrate_governance` pre-fix `a1c990d` | 2/87 | 2.30% | [0.28%, 8.06%] | 7.78% |
| `calibrate_governance` post-fix `33ad55e` | 3/90 | 3.33% | [0.69%, 9.43%] | 8.74% |

### Registered predictions

P1–P8 are claimed above; these continue the series.

- **P9 — CONFIRMED.** The n = 1 interval spans more than 90% of [0,1].
  Measured width 97.50%. This is P2's claim restated as a measurement.
- **P10 — CONFIRMED.** The `calibrate_governance` pre/post intervals overlap:
  [0.28%, 8.06%] vs [0.69%, 9.43%]. P4's refutation survives at 95%; the
  2.3% → 3.3% shift is not detectable.
- **P11 — CONFIRMED.** The `verify_quantum_claims` pre/post intervals overlap:
  [0.00%, 40.96%] vs [3.67%, 70.96%]. This is the prediction that qualifies
  the prose sentence above P1. It does **not** refute P1, which registers a
  directional claim the corpus satisfies.
- **P12 — OPEN, NOT RUN.** Recompute with a cluster bootstrap that resamples
  whole functions rather than individual mutants. Registered before running:
  no verdict above changes, because correlation widens intervals and every
  current verdict is an overlap.

### Anti-vacuity control

Four gates, all of which can fail, proven by `--sabotage-a4` — which collapses
every interval to a point, fails all four, exits 1, and prints no verdicts:

- **G1** — for k = 0 the upper bound is exactly 1 − (α/2)^(1/n), and for k = n
  the lower bound is exactly (α/2)^(1/n). Real expected values, not a
  self-comparison.
- **G2** — the returned bounds must satisfy their defining tail equations.
- **G3** — the interval must be wide at n = 1 **and** tight at n = 1000. An
  instrument that only ever returns wide intervals proves nothing.
- **G4** — the overlap test must return False on a separated pair
  (2/87 vs 60/90). Without this, "the intervals overlap" is a log line.

G4 is the one that matters. Every verdict in this amendment is an overlap, so
a test incapable of reporting non-overlap would make all of them vacuous.

### Sensitivity to P5 (assumption, not measurement)

A killed mutant is necessarily reachable — it changed the verdict, so it
executed. P5's correction therefore shrinks n and leaves k fixed. Applying the
25/91 ratio to survivors only:

| target | k/n | score | 95% CI |
|---|---|---|---|
| `calibrate_governance` pre-fix | 2/25 | 8.00% | [0.98%, 26.03%] |
| `calibrate_governance` post-fix | 3/27 | 11.11% | [2.35%, 29.16%] |

Still overlapping, by a wider margin. The direction is fixed by arithmetic:
smaller n gives wider intervals, so every overlap verdict here can only
strengthen when P5 runs. A non-overlap would have been the fragile one.

### Stated limitation

Clopper-Pearson assumes independent Bernoulli trials. Mutants inside one
function share a code path, so kills are positively correlated and these
intervals are anti-conservative — too narrow. Every overlap reported is a
lower bound on the true overlap. Same direction as the P5 correction: both
widen.

### Reproduction

`python3 scripts/note059_reference.py` — 4/4 Amendment 4 gates, exit 0.
`python3 scripts/note059_reference.py --sabotage-a4` — 4/4 fail, exit 1.

Standard library only (`math.comb`), no NumPy. Verified bit-identical on
x86_64/glibc/py3.12 and aarch64/Termux/py3.14; every figure above matched
across both architectures. The stdlib-only choice was deliberate: a sibling
experiment in this program lost a statistic to an unstable sort, and exact
integer arithmetic removes that class.

Related: [[note044_circularity_test]], [[note036_verified_models_drift_ledgers]]
