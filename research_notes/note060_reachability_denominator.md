# note060 — The Reachability Denominator

**Status:** Draft — measured, INSTRUMENT LOST
**Reference code:** NONE. `scripts/note060_reference.py` was deleted on
2026-09-11 (see "The instrument is gone" below). The numbers in this note
were measured on the device named above and cannot currently be regenerated.
**Contributors:** Chad Edward Holland; Claude (Anthropic)
**Device:** Samsung Galaxy S25 Ultra, Termux, aarch64, Python 3.14
**Date:** 2026-08-27

---

## What broke

A mutation score published in [[note059_mutation_score_denominator]] was computed over a denominator
that included sites the target never executes.

`mutation_probe.py` reports `score = killed / (killed + survived)` over every
eligible site. A mutation on a line that never runs cannot change the target's
exit code, so it is recorded SURVIVED by construction. The score therefore
mixes a claim about test strength with a claim about coverage, and nothing in
the output separates them.

Measured on `sovereign-suite/tools/calibrate_governance.py` at `33ad55e`:

| invocation | eligible | reachable | unreachable |
|---|---|---|---|
| (no arguments) | 91 | 25 | 66 |
| `--sweep` | 91 | 30 | 61 |

`mutation_probe.py` invokes its target with **no arguments**. So note059's
corpus was measured under the 25-site invocation: 66 of 91 mutants could not
fire regardless of how good or bad the target's checks are.

The published figure is 3 killed / 90 resolved = **3.3%**. Over reachable
sites it is 3 / 25 = **12.0%**.

Neither number is wrong as arithmetic. The 3.3% is what the tool computed and
the tool computed it correctly. What was wrong is the reading: "the mutation
score is flat" was taken as evidence about the strength of the target's
checks, when most of it was evidence about which lines a no-argument run
touches.

## What this does not overturn

`mutation_probe.py` already prints, after any surviving mutant:

> the mutation landed somewhere unreachable from the verdict path. Read each
> one; a low score is a place to look, not a proven defect.

The tool names unreachability as a cause and warns against reading the score
as a proven defect. It does not **measure** it. The gap here is between a
prose caveat and a number — and note059 read past the caveat, which is the
part worth recording. A warning that is present in the output and absent from
the interpretation is a warning that did not work.

## Registered claims

**P1** — For `calibrate_governance.py` at `33ad55e`, a majority of eligible
mutation sites lie on lines never executed by the invocation
`mutation_probe.py` uses. Refuted if reachable ≈ eligible.
**RESOLVED:** 66 of 91 unreachable with no arguments; 61 of 91 under
`--sweep`. The claim survives its strongest challenge — even the deeper
invocation reaches only 30 of 91.

**P2** — `mutation_probe.py` does not report a reachability denominator, so
this discrepancy is invisible in its output for any target.
**RESOLVED, with a correction to its original wording.** The first draft of
P2 claimed the tool "gives no indication" of unreachability. That was wrong:
it prints the caveat quoted above. The corrected claim is narrower — the
warning is prose, not a measurement, and no number in the output separates
the two populations.

**P3 (anti-vacuity)** — The reachability filter must return *null* on a
target with complete coverage and *non-null* on a target with known dead
sites. A filter that always finds unreachable sites measures nothing.
**RESOLVED:** `full_cov.py` 3 eligible / 3 reachable / 0 unreachable;
`partial_cov.py` 6 eligible / 3 reachable / 3 unreachable. Both directions
sabotage-proven — forcing the filter to "everything reachable" fails the
signal direction and exits 1; forcing it to "nothing reachable" fails the
null direction and exits 1.

**P4 — OPEN, NOT RUN.** Across the other estate targets `mutation_probe.py`
has scored, what fraction of eligible sites is reachable under the
no-argument invocation it uses? If the pattern holds, every published
mutation score in this estate carries the same denominator. If it does not,
`calibrate_governance.py` is unusual and the finding is about that file
rather than about the tool.

## P7 of note059, resolved

note059 left P7 open: re-run post-fix line 513 alone at a longer timeout,
sequentially rather than in parallel — does it resolve to KILLED, SURVIVED,
or genuinely not terminate?

Line 513 is `record_crystallization(lv, 0.0, was_rejected=True)`, inside
`if lv < self.tc.fisher_threshold:`. It is eligible site **index 86**
(line 513, col 76, `True -> False`), the only eligible site on that line.

**Under the no-argument invocation the answer is vacuous.** Three sequential
trials at a 900 s timeout: rc 1 → 1, no crash, 0.20 s / 0.21 s / 0.45 s.
All SURVIVED — but the run's own report gives `fisher_fail_count: 0`,
`total_crystallizations: 0`, `total_rejections: 0`. The branch is never
taken. The mutation lands on dead code, and dead code always survives. The
180 s ERROR recorded in note059 was parallel load on a throttling phone, not
non-termination: sequential runs complete in under half a second.

**Under `--sweep` the line executes, and the answer is real.** Baseline
rc 0, no crash, 467.8 s. Mutant rc 0, no crash, 445.9 s. **SURVIVED on live
code.**

That is the finding. Flipping `was_rejected=True → False` records every
Fisher-rejected crystallization as accepted — inverting the tool's own
rejection bookkeeping — and the sweep runs to completion with an unchanged
exit code. The verdict is insensitive to the accounting it reports on.

Recorded without interpretation: the mutant ran ~5% faster than baseline
(445.9 s vs 467.8 s), directionally consistent with skipping rejection
bookkeeping, but n=1 on a thermally-throttling device. Not a claim.

## Why this matters beyond one file

The defect class is the one this program keeps finding, one level up. A
vacuous check computes a correct verdict and fails to let it reach anything.
A vacuous *measurement* computes a correct number over a population that
cannot exhibit the property being measured. In both cases the output looks
like evidence and is not, and in both cases the failure is invisible unless
you ask what the instrument could have returned.

The general form: **any score reported as a ratio needs its denominator
stated in terms of what was actually exercised, not what was enumerated.**

## Reproduce

```
cd sovereign-suite/tools
python3 -m trace --count --coverdir=$HOME/cov calibrate_governance.py
# then intersect eligible-site line numbers with the .cover hit lines
python3 scripts/note060_reference.py    # fixtures + anti-vacuity gate
```

The reference script builds every fixture inline and depends on no
repository state. The corpus numbers above are quoted from the device run,
not recomputed by the script.

## Related

- [[note059_mutation_score_denominator]] — the mutation-probe result whose denominator this corrects,
  and the origin of P7
- [[note052_verification_that_cannot_fail]] — the same defect class one level
  down: checks that cannot fail, rather than measurements that cannot fail

*Vincit Omnia Veritas.*

---

## The instrument is gone

`scripts/note060_reference.py` no longer exists. It was written on 2026-08-27,
run on the device named above, and kept only in the device's Downloads folder.
It was never committed. On 2026-09-11 an overly broad `rm -f` glob, issued by
Claude while clearing stale copies of an unrelated note, deleted it along with
them.

Recovery was attempted and failed, and the search was exhaustive rather than
cursory:

- every unreachable git blob scanned for `reachab`, `mutation_probe`,
  `eligible` — no match
- `git log --all --diff-filter=A -- 'scripts/note060*'` — empty, so the file
  was never added in any commit on any ref
- the four dangling commits in the object store are from 2026-07-16 and
  contain no note060 files
- filesystem search across `$HOME` and `/sdcard` — no match

**The numbers above stand. They were measured.** What is lost is the ability
to regenerate them, which under this repository's own method means they are
now testimony rather than evidence. This note is kept at that lower standard
rather than deleted, and its status says so.

### The defect class this belongs to

An artifact that exists only outside version control is indistinguishable
from one that does not exist. This estate has now produced that failure three
times: the BATADAL smoke suite that was written and passing but never pushed,
`vacuity_scan.py` whose 0/347 control result is unreproducible because the
scanner was never committed, and this. In every case the measurement was real
and the instrument never reached a repository.

That is the same failure as a claim that cannot be reproduced, arriving by a
different route, and no linter detects it — there is no bad code to find,
only an absent file that everyone believed in.

## Left unrun

**P13 — REBUILD.** Reconstruct the reachability filter from the methodology
described above, commit it BEFORE running it, and re-measure
`calibrate_governance.py` at commit `33ad55e`. Registered prediction: the
rebuilt instrument reproduces 91 eligible / 25 reachable under the
no-argument invocation. If it does not, this note's numbers are withdrawn
rather than adjusted.

P5 and P8 both need that instrument, so rebuilding it is the gate on the rest
of this line of work.

## Related

[[note059_mutation_score_denominator]] carries the score this note corrects.
[[note057_the_loud_type_a]] carries the reading retracted above at P11.
