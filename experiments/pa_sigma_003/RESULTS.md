# PA-SIGMA-003: results

**State:** 1 of 4 as registered. P1, P2 and P4 are **REFUTED** and kept; P3 held. **Self-tested** (M10), in one
x86_64 container; NOT VALIDATED on the S25.
**Registration:** [PREREG.md](PREREG.md), commit `88eeaaf`, pushed before the harness existed.
**Runs:**
- Run 1: commit `bb3c81b` (harness md5 `bedb264dbcd0c3e23219b7e5a4cfc57f`).
- Run 2: commit `d8bfdbf`, with the same DIGEST `9bcbc280…` (G7).
- Pin: commit `4100ab0`.

The registered claim was that SigmaHQ's static checks see only an edit's shape. They would flag exactly the
edits that leave a one-value list, or `|all` over one value, and nothing else. Every one of those was flagged
(none missed), along with **8 more**:
- 6 were flagged by a validator that checks how a `User` field is localized;
- 2 were flagged by the test for duplicate detections.

The derivation from the source was right about what it covered, and it missed two checks that look at content.

In house style, the static checks flag 26 of the 1,502 broadening edits. Of the 1,197 that pass both behavioural
jobs (PA-SIGMA-002), **1,173 pass these three checks too.**

## What could have gone wrong, first

- **Self-tested.** Claude registered, built, ran and judged this. Claude also wrote the derivations the
  predictions test. Nothing here is independent.
- **The harness changed after registration, before any verdict (deviation D3).**
  - In run 0, test_logsource.py exited 1 on the BAD_LOGSOURCE controls, yet 0 files were attributed. The
    cause: it prints absolute paths, and the TR/TL matcher looked only for relative ones.
  - Run 0 was stopped during rounds 7–8. By then it had printed per-round flag counts, but no gate, prediction
    or DIGEST had been computed.
  - `stage.py` now also matches each path under the round root, and two selftest cases cover it.
  - The 30 positive controls were then run once on their own: each check attributed 10 of 10.
  - Run 0's output is kept in [`run0_stopped_tl_attribution.txt`](../../results/pa_sigma_003/run0_stopped_tl_attribution.txt),
    and the change is logged in FORKS.md as PA-SIGMA-003-X3.
- **Staged items collided with each other.** A round stages up to 282 rules at once. Of the 15 items flagged
  only by cross-rule checks, 13 passed when re-run alone, so those flags came from two staged mutants matching
  each other. Two more arm-A items (`526cc8bc…:4`, `acd74772…:4`) carry the same unconfirmed
  `test_duplicate_detections` reason. They were not re-run, because a per-rule reason (a one-value list) flags them
  anyway, and their arm-B forms, re-run alone, pass.
- **Stand-in and deviations** (registered): S1 loads MITRE data from local files, D1 expands `rules*` in the
  harness, and D2 turns off unittest's message truncation. D3 is above.
- **Tool versions are what `pip` resolves today:** pySigma 2.0.1, sigma-cli 4.0.0 and pySigma-validators-sigmahq
  0.21.0. SigmaHQ's CI may have resolved other versions when `05d1031` was tested.
- **House style is this study's rewrite.** 18 edits have no form inside one selection map.
- **Not covered:** `yamllint`, the schema workflow and human review.
- **Operational:** a first start of run 2 was stopped after 6 seconds, because it had been launched detached.
  No round had run.

## Raw output (run 1, [`run1.txt`](../../results/pa_sigma_003/run1.txt))

```
PA-SIGMA-003 harness
environment: Linux x86_64 | harness Python 3.13.18 | checks: pysigma 2.0.1 | sigma-cli 4.0.0 | pysigma-validators-sigmahq 0.21.0 | pyyaml 6.0.3 | colorama 0.4.6 | python 3.11.18 | SigmaHQ 05d1031 | ATT&CK 81113ba98afa
items: {'BAD_LOGSOURCE': 10, 'DANGLING': 10, 'IDENTITY': 282, 'MUTANT/A': 1502, 'MUTANT/B': 350, 'ONE_VALUE': 10, 'ROUNDTRIP': 282}; G6 equivalence {'parse': 6, 'query': 344}; built in 21s
rounds: 55 (+ G1), 2 at a time
solo re-runs for cross-rule-only flags: 15
G1 unmutated tree: SC exit 0; TR exit 0; TL exit 0
controls flagged (by any check): IDENTITY 0 of 282, ROUNDTRIP 0 of 282; positive controls flagged by their target: DANGLING/SC 10, ONE_VALUE/TR 10, BAD_LOGSOURCE/TL 10 (each of 10, need >= 9)
G1 PASS
G2 PASS
G3 PASS
G4 PASS
G5 PASS
G6 PASS
G8 PASS
G9 PASS
P1 arm A, test_rules.py flags 352; derived 350; registered: exactly the derived set -> REFUTED
P2 arm A, sigma check flags 217; derived 211; registered: exactly the derived set -> REFUTED
P3 test_logsource.py flags arm A 0, arm B 0; registered: none -> HELD
P4 arm B, test_rules.py flags 2, sigma check flags 24 (derived 18); registered: TR none, SC exactly the derived set -> REFUTED
mismatches: {'P1_flagged_not_derived': 2, 'P1_derived_not_flagged': 0, 'P2_flagged_not_derived': 6, 'P2_derived_not_flagged': 0, 'P3_flagged': 0, 'P4_tr_flagged': 2, 'P4_sc_flagged_not_derived': 6, 'P4_sc_derived_not_flagged': 0}
flag reasons on mutants: {'SC:SigmahqFieldUserIssue': 12, 'SC:SigmahqInvalidAllModifierIssue': 229, 'TR:test_duplicate_detections': 4, 'TR:test_selection_list_one_value': 350}
flagged by any static check: arm A 352 of 1502 (294 of 1197 SURV), by operator {'DROP_FIELD': 2, 'DROP_VALUE': 350}; arm B 26 (24 SURV), by operator {'DROP_FIELD': 2, 'DROP_VALUE': 24}
SURV mutants passing every check run (regression, goodlog, SC, TR, TL): arm A 903, arm B 1173 of 1197; rules keeping one (arm B): 271 of 273
VERDICT 1 of 4 as registered
DIGEST 9bcbc280ccf46938c55330e60607700a3c16598d83a7c0a49dc8e3b3ba4f83ca
RECORDED: not pinned yet
exit 0
```

The flag-reason counts cover both arms. `SigmahqInvalidAllModifierIssue` is 211 in arm A plus 18 in arm B, and
`SigmahqFieldUserIssue` is 6 plus 6.

## Predictions

| ID | Prediction | Result |
|---|---|---|
| P1 | Arm A: test_rules.py flags exactly the 350 DERIVED_TR mutants | **REFUTED**: 352. All 350 are flagged, plus 2 DROP_FIELD mutants flagged by `test_duplicate_detections` (each confirmed alone) |
| P2 | Arm A: sigma check flags exactly the 211 DERIVED_SC mutants | **REFUTED**: 217. All 211 are flagged, plus 6 DROP_VALUE mutants flagged by `SigmahqFieldUserIssue` |
| P3 | test_logsource.py flags no mutant, in either arm | **HELD**: 0 and 0 |
| P4 | Arm B: test_rules.py flags none, and sigma check flags exactly the 18 that keep `\|all` | **REFUTED**: test_rules.py flags the same 2 duplicates (house style does not change a DROP_FIELD edit); sigma check flags 24, the 18 plus the same 6 |

All registered gates pass in run 1 (G1–G6, G8, G9), and G7 passes with run 2:
- IDENTITY controls: 0 of 282 flagged; ROUNDTRIP controls: 0 of 282.
- Positive controls: 10 of 10 flagged by their target check, for each check.
- House style: all 350 changed texts are equivalent to their originals (344 by query, 6 by parse).

The pinned harness reproduced RECORDED ([`run3_pinned.txt`](../../results/pa_sigma_003/run3_pinned.txt), exit 0).

Under `--sabotage`, every mutant is staged as its original rule ([`sabotage.txt`](../../results/pa_sigma_003/sabotage.txt)):
- no mutant is flagged;
- every derived flag is missing (350, 211 and 18);
- the gates still pass.

The verdict is again 1 of 4, but for the opposite reason: the real run misses no derived flag and adds 8. The
DIGEST differs (`8402e7ab…`), and the harness exits 1.

## What the refutations teach

Two of SigmaHQ's static checks look at content, not only at shape. The derivation had read neither.

- **`sigmahq_field_user`** (`SigmahqFieldUserValidator`) flags a field whose name contains `user` when it holds one
  value containing `AUTHORI` or `AUTORI`. These are the English and French forms of `NT AUTHORITY`, and the
  validator expects both. Six mutants dropped one of the pair from a list. Example: `registry_set_add_port_monitor.yml`,
  where `User|contains: [AUTHORI, AUTORI]` lost `AUTHORI` in an exclusion, so the exclusion no longer covers
  English-language systems. This catch is in either style. It is narrow, but it does catch the weakening itself.
- **`test_duplicate_detections`** flags a rule whose detection and logsource equal another rule's. Two DROP_FIELD
  mutants dropped the one key that set them apart from a broader sibling rule, and became copies of it:
  - `file_event_win_dump_file_susp_creation.yml` lost its `Image|endswith` list and now equals
    `rules-threat-hunting/.../file_event_win_dump_file_creation.yml`;
  - `registry_set_pua_sysinternals_susp_execution_via_eula.yml` now equals
    `registry_set_pua_sysinternals_execution_via_eula.yml`.

  These catches are content too, and they hold in either style. They exist only because a broader sibling rule
  happens to be in the repository.

Both flags came from SigmaHQ's own checks, run as CI runs them. The mirrors in `feasibility.py` covered the two
shape checks only. Reading the code was not enough, which is the point of running it.

## What this shows, and what it does not

**Shows** (exact counts, this mutant set, SigmaHQ `05d1031`, the tool versions above):

- **As written (arm A),** the static checks flag 352 of the 1,502 broadening mutants, and 294 of the 1,197 that
  pass both behavioural jobs. 350 of the 352 are flagged for a one-value list or `|all` over one value. A
  contributor clears that by writing the value as a scalar, and the edit means the same.
- **In house style (arm B),** 26 are flagged (24 of them in SURV):

  | Why | Mutants | Kind of catch |
  |---|---|---|
  | `\|all` kept next to an existing key (no one-map house form) | 18 | shape |
  | `User` field left with one of `AUTHORI`/`AUTORI` | 6 | content (localization) |
  | detection became a copy of another rule's | 2 | content (duplicate) |

- **Across PA-SIGMA-001, -002 and -003:** of the 1,502 broadening edits, written in house style,
  **1,173 (78.1%)** pass the regression-test job, the goodlog job, `sigma check`, `test_rules.py` and
  `test_logsource.py`. As written, 903 do. In house style, 271 of the 273 rules with a SURV mutant keep at least
  one such edit.

**Does not show:**

- Anything about `yamllint`, the schema workflow or human review (door P6).
- That real rule changes weaken rules this way, or how often.
- Equivalence: a mutant equivalent to its original counts as passing, which flatters the gap.
- Other tool versions or other commits.

## Post hoc (EXPLORATORY, not registered)

[`posthoc.py`](posthoc.py), written after run 1, names the look sample: three arm-A FLAGGED, three arm-B FLAGGED
and three unflagged SURV mutants. The registration fixed the counts, not how to choose, so the rule below was set
before any diff was opened:
- arm A: the first three by mutant key, one per rule;
- arm B: the first for each reason a house-style edit was flagged (`|all` kept, `User` field, duplicate);
- unflagged: the first for each operator.

A first version took the first three of each by key. It drew three mutants of one rule more than once, and was
replaced before anyone looked at a diff. The identities are in
[`look_sample.json`](../../results/pa_sigma_003/look_sample.json). The diffs (SigmaHQ rule text) are kept out of
the repository and were sent to Chad.

## Still open

- **P6 (door):** `yamllint` and the schema workflow on house-style mutants written in SigmaHQ's YAML layout.
- **P7 (door):** an equivalent two-selection form for the 18 key-clash edits.
- **P8 (door):** PA-SIGMA-001's P6, negative samples.
- The person-look at the look sample (C-SYNTH). It is Chad's.
- Whether any of PA-SIGMA-001 to -003 goes to SigmaHQ as an issue. That is Chad's call.

## Provenance

AI participation: Claude (Anthropic, Opus 5.5) registered, built, ran and wrote this up on 2026-10-30, at Chad
Holland's direction → human validation: direction only → human editing/curation: none → responsibility: Chad
Holland.
