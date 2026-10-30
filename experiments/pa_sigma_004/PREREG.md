# PA-SIGMA-004: do SigmaHQ's layout and schema checks catch the weakened rules the other checks miss?

**State:** REGISTERED, NOT RUN. No mutant has been staged or checked. This registration is committed with its
feasibility counts, the unmutated-checkout check (G1) and a control pre-check, before the harness is written.
**Authors:** Direction: Chad Holland (2026-10-30; choice of path delegated for the night). Design, scripts and this
text: Claude (Anthropic, Opus 5.5). Human review level: direction only. Everything run under this registration is
**self-tested** (M10).
**Method:** [METHOD.md](../../METHOD.md) (md5 `50e8a91a448251f8fc5d70f6971b74ae`), [WORKFLOW.md](../../WORKFLOW.md)
(md5 `8ab6970501f53cb288d35f19787be529`) and [CONTROLS.md](../../CONTROLS.md) (md5 `2a68368e99f87430bd15e8074811452c`).
**Subject:** [SigmaHQ/sigma](https://github.com/SigmaHQ/sigma) at `05d1031f537e830b76da53bae2400c5814c89165`:
- the `yamllint` job of `.github/workflows/sigma-test.yml`, with the repository's `.yamllint`;
- `.github/workflows/sigma-validation.yml`, the JSON-schema check.

**Parent:** [PA-SIGMA-003](../pa_sigma_003/PREREG.md), whose door P6 this is. Its branch is this branch's base, and
its PR (#100) should be merged first.

## W1: question

**The question (observable):** of PA-SIGMA-001's 1,502 BROADENING mutants, which would fail SigmaHQ's `yamllint`
job or its schema check? Each is asked twice: as PA-SIGMA-001 wrote it, and in house style written in SigmaHQ's
own layout.

**What the code can express.** Read before registering (VERIFIED FROM SOURCE):
- The `yamllint` job runs `ibiqlik/action-yamllint@2576378`. That action is composite and runs
  `yamllint -f parsable -s .` with the runner's `yamllint` and the repository's `.yamllint`. The config extends
  `default` and sets 4-space indentation, `indent-sequences: whatever`, no document start and no line-length limit.
- The schema workflow runs `SigmaHQ/sigma-rules-validator@aa3561c`. It installs `check-jsonschema` and runs it
  against `sigma-detection-rule-schema.json` from sigma-specification tag `v2.1.0`. The rule files come from
  SigmaHQ's `tests/validate-sigma-schema/validate.py`, under six `rules*` folders.
- Both check one file at a time. Neither reads what a rule matches. Layout is all `yamllint` sees; the schema
  sees fields and types.

## Design (C-DESIGN)

- **Design:** audit. One deterministic pass over a fixed, enumerated set, at one commit.
- **Arm A:** each mutant exactly as PA-SIGMA-001 wrote it (PyYAML's default layout: 2-space indentation).
- **Arm B4:** each mutant in PA-SIGMA-003's house style (its arm B), written in SigmaHQ's own layout:
  - mappings indented 4;
  - list dashes 4 under their key, with one space after the dash.

  That layout is written by `ruamel.yaml` 0.19.1 (stand-in S3). Comments are not kept.
- **Strongest claims it can carry:** exact counts and existence over this set, at this commit, with these tool
  versions. Combined with PA-SIGMA-001 to -003, it says how many of the 1,502 edits pass every automated rule check
  the series ran.
- **Out of scope:** human review. The duplicate-id grep cannot fail, because an in-place edit keeps the id.

## Instrument

**Real code (M4).** `yamllint` with SigmaHQ's own `.yamllint`, run from the root of a hard-linked copy of the
checkout, and `check-jsonschema` with the pinned schema file.

**Tools** (Python 3.11.18 venv): yamllint 1.38.0, check-jsonschema 0.39.0, jsonschema 4.26.0.
**Schema:** sigma-specification tag `v2.1.0` (commit `0c857d07`), `json-schema/sigma-detection-rule-schema.json`,
sha256 `eb95ddb1bc2503145a6e84511e38990f74fe9a843067065a23d3763457fb2d95`.

**Staging.** Every item is written as its own file, `rules/pa_sigma_004/item_NNNNN.yml`, in one copy of the
checkout. Both checks then run once:
- `yamllint -f parsable -s rules/pa_sigma_004`;
- `check-jsonschema --schemafile <schema> <the staged files>`.

A staged file is FLAGGED by `yamllint` when it appears on any `[error]` or `[warning]` line (strict mode fails on
both). It is FLAGGED by the schema check when it appears on any `<file>::<json path>` error line.

**Stand-ins and deviations:**
- **D1:** `yamllint` runs on the staged folder, not on `.`. Its rules are per file and the config is the same.
- **D2:** `check-jsonschema` is given the staged files, not `validate.py`'s list. The check is per file and the
  schema is the same.
- **S1:** `yamllint` from PyPI. The workflow uses whatever the runner image has.
- **S2:** the schema file is fetched by `git` at its tag. The workflow downloads the same path over HTTP.
- **S3:** SigmaHQ's layout is written by `ruamel.yaml`, as a stand-in for a person's hand layout. G4 checks it on
  all 282 originals.

## Feasibility counts (C-FEAS)

From [`feasibility.py`](feasibility.py), output [`feasibility_output.txt`](feasibility_output.txt):

```
0. items 3588 {'IDENTITY': 282, 'LAYOUT_BAD': 10, 'MUTANT/A': 1502, 'MUTANT/B4': 1502, 'ROUNDTRIP4': 282, 'SCHEMA_BAD': 10}
1. B4 texts that parse back to their house-style rule: 1502 of 1502; SURV 1197; by operator {'DROP_FIELD': 319, 'DROP_VALUE': 869, 'NEVER_SEL': 314}
2. tools: yamllint 1.38.0 | check-jsonschema 0.39.0 | jsonschema 4.26.0 | python 3.11.18 | schema sha256 eb95ddb1bc2503145a6e84511e38990f74fe9a843067065a23d3763457fb2d95 (pinned: True)
3. G1 yamllint over the unmutated checkout: exit 0, files flagged 0, 14s
4. G1 schema check over 3804 rule files: exit 0, files flagged 0, 9s; last line: 'ok -- validation done'
5. IDENTITY control pre-check, 282 files: yamllint flagged 0, schema flagged 0
5. ROUNDTRIP4 control pre-check, 282 files: yamllint flagged 0, schema flagged 0
5. LAYOUT_BAD control pre-check, 10 files: yamllint flagged 10, schema flagged 0
5. SCHEMA_BAD control pre-check, 10 files: yamllint flagged 0, schema flagged 10
   yamllint reasons on controls: {'indentation': 10}
```

## Gates (instrument checks, not predictions)

Any gate failing → exit 2, no verdict.

- **G1:** the unmutated checkout passes `yamllint` (exit 0), and the schema check passes over all 3,804 rule files
  (exit 0).
- **G2:** the mutant set is PA-SIGMA-003's: identity `4bb6343d…96ba0`, SURV `b0c45e11…bc6b`.
- **G3:** IDENTITY controls (each original's bytes): **0 FLAGGED** by either check.
- **G4:** ROUNDTRIP4 controls (each original in SigmaHQ's layout through S3): **0 FLAGGED** by either check. A flag
  would mean the layout writer, not the edit, trips a check.
- **G5:** positive controls on the 10 lowest-id rules:
  - LAYOUT_BAD (the original in PyYAML's default layout, as arm A is written): at least 9 of 10 flagged by
    `yamllint`;
  - SCHEMA_BAD (the original in SigmaHQ's layout with `level: bogus`): at least 9 of 10 flagged by the schema check.
- **G6:** every B4 text parses back to its house-style rule (1,502 of 1,502). The layout does not change the rule.
- **G7:** a second run gives the same DIGEST.
- **G8:** both checks ran to their end, each exiting 0 or 1. When the schema check exits 0 it printed
  `ok -- validation done`, and when it exits 1 at least one error line was parsed.
- **G9:** after the run, the SigmaHQ checkout is unchanged (`git status --porcelain` empty, HEAD `05d1031`).

## Predictions (registered before observing; M1, M2)

| ID | Prediction | Credence | Precisely wrong if |
|---|---|---|---|
| P1 | `yamllint` flags **none** of the 1,502 B4 mutants | 0.85 | it flags one |
| P2 | The schema check flags **none** of the 1,502 B4 mutants | 0.9 | it flags one |
| P3 | `yamllint` flags **every one** of the 1,502 arm-A mutants (layout) | 0.9 | one passes |
| P4 | The schema check flags **none** of the 1,502 arm-A mutants | 0.9 | it flags one |

**Why these numbers.**
- `yamllint` reads layout, and B4 uses the layout that passes on all 282 originals (G4's pre-check), so P1 expects
  silence. Its 0.85 leaves room for a detection value that some default rule (for example `truthy`) objects to
  once rewritten.
- The schema constrains fields and types, not what a value matches, so P2 and P4 expect silence.
- Every arm-A file has nested mappings indented 2, and LAYOUT_BAD (the same writer) is flagged 10 of 10, so P3
  expects every arm-A file to fail on layout. That would mean PA-SIGMA-001's machine-written mutants could never
  have passed SigmaHQ's CI as written, whatever their content. The realistic arm is B4.

**What the four would mean together.** Layout and schema add no catches in house style. Of the 1,502 broadening
edits, the 1,173 that PA-SIGMA-003 found passing five jobs would then pass all seven checks: the regression-test
job, goodlog, `sigma check`, `test_rules.py`, `test_logsource.py`, `yamllint` and the schema check.

## Simplest rival (M14), as arms

- **"Layout or schema checks catch weakening edits."** P1 and P2, measured on B4.
- **"These checks would have caught PA-SIGMA-001's mutants anyway."** P3 measures it on arm A. If it holds, the
  as-written counts of PA-SIGMA-001 to -003 describe files that CI would reject for layout. That is why B4 is the
  arm the combined count uses.
- **"The instrument cannot say FLAGGED."** G5.

## Pre-mortem (W2)

1. **The layout writer trips a rule** that the originals do not, and B4 is flagged for layout. G4 would fail.
2. **Attribution misses lines:** `check-jsonschema` could report a file under another path form. G5's
   SCHEMA_BAD and G8 would show it.
3. **A check stops early and reads as a pass.** G8 checks exit codes and closing lines.
4. **One run, all files at once:** if a check aborted on the first bad file, later files would read as passes.
   The mutant files follow the controls in staging order. Arm A is expected to be flagged throughout, so a check
   that stopped early would refute P3.

## Sabotage (anti-vacuity of the verdict)

`--sabotage` writes every mutant's original rule bytes in place of both its arm-A and its B4 text. The controls are
left as they are. Expected: `yamllint` flags no arm-A file, so P3 is refuted and the verdict is 3 of 4. The DIGEST
differs and the harness exits 1.

## Stopping rule, outputs, data handling (C-PRIVATE)

- One full run, then a second for G7. No run is discarded.
- RECORDED is pinned in its own commit, then the pinned run and the sabotage run follow.
- The outputs are counts, mutant identities, `yamllint` rule names and JSON paths, all on SigmaHQ rule text. No
  personal data.

## Generated inputs (C-SYNTH)

The B4 texts are generated. Three B4 files, one per operator, will be named for a person to compare with their
originals. The diffs go to Chad outside the repository. That look is Chad's and stays pending until he does it.

## Trigger table (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | yes: the counts, G1 and the control pre-check above, committed with this registration |
| Noise | C-NOISE | yes: both checks are deterministic on fixed files; G7 repeats the run |
| Statistics | C-STAT | no: exact counts over an enumerated set |
| Evidence | C-EVID | no: the question is CI sensitivity |
| Independence | C-INDEP | yes: self-tested. Claude designed, built and runs it |
| External | C-EXT | yes: SigmaHQ's rules and `.yamllint` (Detection Rule License 1.1); sigma-specification's schema; yamllint (GPL-3.0-or-later), check-jsonschema (Apache-2.0) and ruamel.yaml (MIT), as their package metadata states them; pinned by version or sha256. No outside text is quoted |
| Device | C-DEVICE | yes: x86_64 container only. NOT VALIDATED on the S25 |
| Verdict code | C-BUILD | yes: the harness returns FLAGGED / not flagged per check and fails closed (exit 2) on any gate or pin failure |
| Exploration | C-EXPLORE | yes: see below |
| Method comparison | C-METHCOMP | no |
| People's data | C-PRIVATE | no personal data |
| Design | C-DESIGN | yes: audit; exact counts only |
| Held-out | C-HOLDOUT | no: nothing is chosen from the evidence judged |
| Generated inputs | C-SYNTH | yes: see Generated inputs |

## Limits

- **One `yamllint` version and one schema version.** The runner image's `yamllint` may differ from 1.38.0.
- **House layout is one writer's,** with comments dropped. A person's file would differ in quoting and comments.
- **PA-SIGMA-001's mutant set,** capped at 25 per operator per rule. Equivalent mutants count as passing.
- **Self-tested only** (M10).

## Exploration before this registration (C-EXPLORE)

Logged in [FORKS.md](../../FORKS.md) as PA-SIGMA-004-X1.

- Read `action-yamllint@2576378` (`action.yml`, `entrypoint.sh`), `sigma-rules-validator@aa3561c` (`action.yaml`)
  and `tests/validate-sigma-schema/validate.py`, all fetched by `git`.
- The first house layout was PyYAML with `indent=4`. In the ROUNDTRIP4 pre-check, `yamllint` flagged 179 of 282
  originals written that way, all for `hyphens`: PyYAML puts three spaces after each dash. The layout was then
  switched to `ruamel.yaml` (S3), and ROUNDTRIP4 passed 282 of 282.
- Ran G1 and the control pre-check, including the positive controls, through `feasibility.py`.

No mutant was checked by `yamllint` or the schema.

## Provenance and credit (M13)

AI participation: Claude (Anthropic, Opus 5.5) designed this and wrote the scripts and text on 2026-10-30, at Chad
Holland's direction → human validation: direction only → human editing/curation: none → responsibility: Chad
Holland. SigmaHQ's rules and configuration are SigmaHQ's. The schema is the Sigma specification project's.

## Next unrun test (M15)

- **P5:** the same seven checks on a later SigmaHQ commit and the tool versions of that day.
- **P6:** an equivalent two-selection form for PA-SIGMA-003's 18 key-clash edits (PA-SIGMA-003's P7).
- **P7:** PA-SIGMA-001's P6, negative samples, the remedy the series points at.
