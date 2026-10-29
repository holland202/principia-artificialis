# PA-SIGMA-002: results

**State:** 4 of 4 as registered. **Self-tested** (M10), in one x86_64 container; NOT VALIDATED on the S25.
**Registration:** [PREREG.md](PREREG.md), commit `ea348e0`, pushed before the harness was committed. **Run:** commit
`97b552b` (harness md5 `f23fbffc0675ef508455ca88f51a5087`). **Run 2:** `d3534a9`, the same DIGEST `e79ce1e5…` (G6). **Pin:** `9038fe9`.

The predictions were that SigmaHQ's goodlog job would catch some broadening mutants, but not most of them. They held.
"4 of 4" says the gap PA-SIGMA-001 found is real, though narrower than that study alone could show. It does not say
SigmaHQ's checks work.

## What could have gone wrong, first

- **Self-tested.** Claude designed the study, wrote the harness, ran it and judged it. Nothing here is independent.
- **The harness changed after registration, before any verdict.** Both stopped runs are kept, with notes
  (`results/pa_sigma_002/run0*.txt`, FORKS.md PA-SIGMA-002-X3 and X4). Each ran one baseline (win7-x86) and gave
  identical numbers there.
  1. An import fix: both studies have a `feasibility.py`, and the names clashed. The selftest failed before
     anything ran.
  2. **P4's denominator.** The harness first counted all 282 rules that have any broadening mutant, against a
     threshold of half. The registration says the 276 rules with catchable mutants, threshold 138. Run 0 was
     stopped after one baseline and P4 was fixed to the registered definition. No P4 outcome had been computed.
  3. **A two-stage filter.** In run 0b, one `matchgrep.sh` call on 278 MB of staged findings was still running
     after more than 4 minutes, so the run was stopped. The harness now sends each item's first 20 lines, then every
     remaining line of the items not yet caught. It is the same script with the same per-line decision. A selftest
     checks on a constructed case that this gives the same caught set as one call. That check is self-tested, not a
     proof.
- **Controls staged for 282 rules, not 276.** G3's text names "each of the 276 rules"; the harness staged IDENTITY
  and NEVER_FIRE controls for all 282 rules with broadening mutants. This is a superset, and both gates hold on all
  282.
- **A leftover process.** A `matchgrep.sh` from stopped run 0b kept running through run 1's first three baselines.
  It shared the CPU, so it affects run 1's timings, which are not part of the DIGEST. Run 2 had no such competition and gave the same DIGEST.
- **The staged rules could have changed the checker's results for the original rules.** G1b shows they did not: on
  all seven baselines, the unmutated rules gave exactly the raw findings of the G1 run (252, 4146, 5911, 8194, 731,
  2823, 7575).
- **Not covered:** SigmaHQ's other jobs (`sigma check`, `test_rules.py`), human review, and baselines other than
  these seven.
- **Not done:** the person-look at the ten named mutants (C-SYNTH) is pending; it is Chad's.

## Raw output (run 1, `results/pa_sigma_002/run1.txt`)

```
PA-SIGMA-002 harness
environment: Linux x86_64 | Python 3.13.18 | PyYAML 6.0.3 | SigmaHQ 05d1031 | checker d672e07a516f
staged items: {'MUTANT': 1502, 'IDENTITY': 282, 'NEVER_FIRE': 282, 'MATCH_ALL': 10}
  win7-x86                  22.0s unmutated raw   252 (G1 run   252) G1 matchgrep exit 0 | staged items with raw findings  115 | caught   96
  Logs_Client               83.9s unmutated raw  4146 (G1 run  4146) G1 matchgrep exit 0 | staged items with raw findings  205 | caught  165
  Logs_Win11               179.9s unmutated raw  5911 (G1 run  5911) G1 matchgrep exit 0 | staged items with raw findings  214 | caught  191
  Logs_Win11_2023          204.5s unmutated raw  8194 (G1 run  8194) G1 matchgrep exit 0 | staged items with raw findings  255 | caught  222
  win2022-evtx              20.4s unmutated raw   731 (G1 run   731) G1 matchgrep exit 0 | staged items with raw findings  123 | caught  113
  Win2022-AD                37.7s unmutated raw  2823 (G1 run  2823) G1 matchgrep exit 0 | staged items with raw findings  137 | caught  123
  win2022-0-20348-azure    106.3s unmutated raw  7575 (G1 run  7575) G1 matchgrep exit 0 | staged items with raw findings  199 | caught  171
G1 PASS
G1b PASS
G3 PASS
G4 PASS
G5 PASS
controls caught on any baseline: {'IDENTITY': 0, 'MATCH_ALL': 10, 'NEVER_FIRE': 0} (IDENTITY must be 0, MATCH_ALL >= 9 of 10); NEVER_FIRE raw findings 0 (must be 0)
P1 catchable mutants caught by the goodlog job: 305 of 1462 (20.86%); registered < 50% -> HELD
P2 same fraction >= 5% -> HELD
P3 NEVER_SEL caught 30.10% vs DROP_VALUE 11.93% (by operator {'DROP_VALUE': [102, 855], 'DROP_FIELD': [110, 298], 'NEVER_SEL': [93, 309]}); registered NEVER_SEL > DROP_VALUE -> HELD
P4 rules with at least one broadening mutant passing both jobs: 267 of 276 rules with catchable mutants; registered >= 138 of 276 -> HELD
broadening mutants passing both jobs: 1197 of 1502 (uncatchable by construction: {'level_low': 32, 'known_fp_all': 8})
caught per baseline: {'win7-x86': 86, 'Logs_Client': 155, 'Logs_Win11': 181, 'Logs_Win11_2023': 212, 'win2022-evtx': 103, 'Win2022-AD': 113, 'win2022-0-20348-azure': 161}
VERDICT 4 of 4 as registered
DIGEST e79ce1e58c59f945d9f53d9a6d02c49f3dfc0965a2473f1739fc0e8b9c6766f9
RECORDED: not pinned yet
exit 0
```

## Predictions

| ID | Prediction | Result |
|---|---|---|
| P1 | fewer than 50% of the 1,462 catchable broadening mutants are CAUGHT | **HELD**: 305 (20.86%) |
| P2 | at least 5% are CAUGHT | **HELD** |
| P3 | NEVER_SEL is CAUGHT at a higher rate than DROP_VALUE | **HELD**: 30.10% vs 11.93% |
| P4 | at least 138 of the 276 rules keep a broadening mutant that passes both jobs | **HELD**: 267 |

Gates: G1, G1b, G2 (set identity), G3 (IDENTITY 0 of 282 CAUGHT), G4 (MATCH_ALL 10 of 10) and G5 (NEVER_FIRE 0 raw
findings) all pass.

The pinned harness reproduced RECORDED ([run3_pinned.txt](../../results/pa_sigma_002/run3_pinned.txt), exit 0). Under `--sabotage`, every mutant is staged as its unmodified original. That run catches 0 of 1,462, gives **2 of 4** (P2 and P3 refuted) and exits 1 ([sabotage.txt](../../results/pa_sigma_002/sabotage.txt)); its gates still pass, because only the mutation step is disabled. G6 passes: run 2 gives the same DIGEST.

## What this shows, and what it does not

**Shows (exact counts, this mutant set, this commit, these baselines):**

- SigmaHQ's goodlog job catches **305 of the 1,462** catchable broadening mutants, about one in five. The
  regression-test job catches none of them (PA-SIGMA-001). So **1,197 of the 1,502 pass both jobs**: 1,157
  catchable mutants plus the 40 that cannot be caught by construction (32 in `low`-level rules, 8 in rules with a
  `.*` known-FP row).
- The rate depends on the edit:

  | Operator | CAUGHT | Of | Rate |
  |---|---|---|---|
  | DROP_FIELD (a constraint removed from a positive selection) | 110 | 298 | 36.9% |
  | NEVER_SEL (a whole exclusion switched off) | 93 | 309 | 30.1% |
  | DROP_VALUE (one value dropped from a list) | 102 | 855 | 11.9% |

- **267 of 276 rules** keep at least one broadening mutant that passes both jobs. Post hoc (exploratory,
  [`posthoc.txt`](../../results/pa_sigma_002/posthoc.txt)): 133 rules have at least one CAUGHT mutant, and 143
  have none.
- PA-SIGMA-001's headline, "the regression tests catch 0 of 1,502", stands. Seen next to the goodlog job, it
  narrows: SigmaHQ's CI as a whole catches about a fifth of these edits, not none.

**Does not show:**

- That the 1,197 would reach production. `sigma check`, `test_rules.py` and maintainers' review are not tested
  here.
- That real rule changes are weakening this way, or how often.
- Anything about baselines other than these seven. A mutant counts as CAUGHT only if its newly matched events are
  in them.
- Equivalence. A mutant equivalent to its original counts as passing, which flatters the gap.

## Post hoc (EXPLORATORY, not registered)

[`posthoc.py`](posthoc.py) (written after run 1) builds the look sample and the per-rule counts above. Its output is
in [`results/pa_sigma_002/posthoc.txt`](../../results/pa_sigma_002/posthoc.txt).

The look sample is five CAUGHT and five uncaught mutants, the first five of each by sha256. Their identities are in
[`look_sample.json`](../../results/pa_sigma_002/look_sample.json). Their diffs (SigmaHQ rule text) are kept out of
the repository and were sent to Chad.

## Still open

- **P5 (door):** run `sigma check` and `test_rules.py` on the 1,197 mutants that pass both jobs.
- **P6 (door):** negative samples (PA-SIGMA-001's P6).
- The person-look at the look sample.
- Whether this belongs in the SigmaHQ issue draft. The draft is about the JSON path; this finding is separate, and
  it is Chad's call.

## Provenance

AI participation: Claude (Anthropic, Opus 5.5) registered, built, ran and wrote this up on 2026-10-29, at Chad
Holland's direction → human validation: direction only → human editing/curation: none → responsibility: Chad
Holland.
