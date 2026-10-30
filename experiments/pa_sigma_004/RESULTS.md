# PA-SIGMA-004: results

**State:** 4 of 4 as registered. **Self-tested** (M10), in one x86_64 container; NOT VALIDATED on the S25.
**Registration:** [PREREG.md](PREREG.md), commit `77ee154`, pushed before the harness existed.
**Runs:**
- Run 1: commit `8e471f2` (harness md5 `19f33c05cf44f5922ac27a1a1a358878`).
- Run 2: commit `59808c9`, with the same DIGEST `6f598a26…` (G7).
- Pin: commit `1ef5c26`.

**The predictions:**
- `yamllint` and SigmaHQ's schema check add no catches for edits written in house style and SigmaHQ's layout.
- `yamllint` rejects every mutant as PA-SIGMA-001 wrote it, for layout alone.

All four held. With PA-SIGMA-001 to -003, this closes the series' count: **1,173 of the 1,502 broadening edits
pass all seven automated rule checks** in SigmaHQ's CI at `05d1031` that the series ran:
- the regression-test job;
- the goodlog job;
- `sigma check`;
- `test_rules.py`;
- `test_logsource.py`;
- `yamllint`;
- the schema check.

**"4 of 4" here means nothing was caught.** Three of the four predictions were predictions that a check stays
silent.

## What could have gone wrong, first

- **Self-tested.** Claude registered, built, ran and judged this. Nothing here is independent.
- **Silence is hard to sabotage.** `--sabotage` stages originals, which are also silent, so it can only move P3.
  P1, P2 and P4 rest on the positive controls instead (G5: `yamllint` flags 10 of 10 layout-broken files, and the
  schema check flags 10 of 10 files with `level: bogus`), and on G8 (no flagged path goes unattributed).
- **Stand-ins (registered):** `yamllint` 1.38.0 from PyPI, not the runner image's (S1); the schema file fetched by
  `git` at tag `v2.1.0` (S2); SigmaHQ's layout written by `ruamel.yaml` 0.19.1 (S3). Both checks run on the staged
  folder or files rather than the whole tree (D1, D2); their rules are per file.
- **The house layout drops comments and changes quoting.** A person's file would differ. G4 shows the writer
  passes both checks on all 282 originals.
- **One staged pass.** Every file is checked in one run of each tool. Arm A, flagged 1,502 of 1,502, shows
  `yamllint` did not stop early.
- **The combined count reuses PA-SIGMA-003's pinned results.** It is not re-measured here.

## Raw output (run 1, [`run1.txt`](../../results/pa_sigma_004/run1.txt))

```
PA-SIGMA-004 harness
environment: Linux x86_64 | harness Python 3.13.18 | checks: yamllint 1.38.0 | check-jsonschema 0.39.0 | jsonschema 4.26.0 | python 3.11.18 | SigmaHQ 05d1031 | schema eb95ddb1bc25
items: {'IDENTITY': 282, 'LAYOUT_BAD': 10, 'MUTANT/A': 1502, 'MUTANT/B4': 1502, 'ROUNDTRIP4': 282, 'SCHEMA_BAD': 10}
G1 unmutated checkout: yamllint exit 0; schema exit 0 over 3804 rule files
staged run: yamllint exit 1, files flagged 1512; schema exit 1, files flagged 10; flagged paths not staged here: 0
controls flagged (either check): IDENTITY 0 of 282, ROUNDTRIP4 0 of 282; LAYOUT_BAD by yamllint 10 of 10; SCHEMA_BAD by schema 10 of 10 (each needs >= 9)
G1 PASS
G2 PASS
G3 PASS
G4 PASS
G5 PASS
G6 PASS
G8 PASS
G9 PASS
P1 B4, yamllint flags 0 of 1502; registered: none -> HELD
P2 B4, schema flags 0 of 1502; registered: none -> HELD
P3 arm A, yamllint flags 1502 of 1502; registered: every one -> HELD
P4 arm A, schema flags 0 of 1502; registered: none -> HELD
yamllint rules on arm A: {'indentation': 1502}
combined (house style): of 1197 SURV, PA-SIGMA-003 arm B flags 24, this study's B4 flags 0; pass all seven checks: 1173 of 1502 broadening mutants; rules keeping one: 271 of 273
VERDICT 4 of 4 as registered
DIGEST 6f598a26ae03548b91f6ac0becaee7aedad4fedc36e38f8b0d38373898ae7890
RECORDED: not pinned yet
exit 0
```

## Predictions

| ID | Prediction | Result |
|---|---|---|
| P1 | `yamllint` flags none of the 1,502 B4 mutants | **HELD**: 0 |
| P2 | The schema check flags none of the 1,502 B4 mutants | **HELD**: 0 |
| P3 | `yamllint` flags every one of the 1,502 arm-A mutants | **HELD**: 1,502, all `indentation` |
| P4 | The schema check flags none of the 1,502 arm-A mutants | **HELD**: 0 |

- **Gates:** all pass in run 1, and G7 passes with run 2.
- **Pinned run:** the pinned harness reproduced RECORDED ([`run3_pinned.txt`](../../results/pa_sigma_004/run3_pinned.txt),
  exit 0).
- **Sabotage** ([`sabotage.txt`](../../results/pa_sigma_004/sabotage.txt)): every mutant is written as its
  original rule. `yamllint` then flags none of arm A, P3 is refuted, and the result is **3 of 4**. The DIGEST
  differs (`0bdee4b9…`) and the harness exits 1.

## What this shows, and what it does not

**Shows** (exact counts, this set, SigmaHQ `05d1031`, these tool versions):

- **Neither check sees the edit.** `yamllint` reads layout and the schema reads fields and types. Neither flags
  any of the 1,502 weakening edits once they are written the way SigmaHQ's own files are.
- **PA-SIGMA-001's mutants could not have passed CI as written.** All 1,502 fail `yamllint` on indentation (PyYAML's
  2-space default against SigmaHQ's 4). The as-written counts in PA-SIGMA-001 to -003 therefore describe files that
  CI rejects for layout. The house-style, house-layout arm is the realistic one.
- **The series' count:**

  | Job | Catches among the 1,502 (house style) | Source |
  |---|---|---|
  | regression tests | 0 | PA-SIGMA-001 |
  | goodlog | 305 | PA-SIGMA-002 |
  | `sigma check`, `test_rules.py`, `test_logsource.py` | 24 more: 18 shape (`\|all` kept next to an existing key), 4 localization and 2 duplicates. The other 2 localization catches are among the 305 | PA-SIGMA-003 |
  | `yamllint`, schema | 0 more | this study |
  | **pass all seven** | **1,173 (78.1%), in 271 of the 273 rules with a SURV mutant** | |

**Does not show:**
- Human review, which SigmaHQ also has.
- That real rule changes weaken rules this way, or how often.
- Other commits or tool versions.
- Equivalence: a mutant equivalent to its original counts as passing, which flatters the gap.

## Post hoc (EXPLORATORY, not registered)

[`posthoc.py`](posthoc.py), written after run 1, names the three B4 files the registration promised, the first by
key for each operator. Their identities are in [`look_sample.json`](../../results/pa_sigma_004/look_sample.json).
The diffs (original file against its B4 file) are kept out of the repository and were sent to Chad. They are the
same three edits as PA-SIGMA-003's unflagged sample, chosen by the same rule.

## Still open

- **P5 (door):** the same seven checks at a later SigmaHQ commit, with that day's tool versions.
- **P6 (door):** an equivalent two-selection form for PA-SIGMA-003's 18 key-clash edits.
- **P7 (door):** PA-SIGMA-001's P6, negative samples. It is the remedy the series points to: a test that
  something must *not* match.
- The person-look at the three B4 files (C-SYNTH). It is Chad's.
- Whether the series goes to SigmaHQ. That is Chad's call.

## Provenance

AI participation: Claude (Anthropic, Opus 5.5) registered, built, ran and wrote this up on 2026-10-30, at Chad
Holland's direction → human validation: direction only → human editing/curation: none → responsibility: Chad
Holland.
