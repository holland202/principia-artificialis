# PA-SIGMA-003: do SigmaHQ's static rule checks catch the weakened rules its behavioural jobs miss?

**State:** REGISTERED, NOT RUN. No mutant has been staged or checked. This registration is committed with its
feasibility counts, the unmutated-tree check (G1) and a ROUNDTRIP pre-check, before the harness is written.
**Authors:** Direction: Chad Holland (2026-10-30; choice of path delegated for the night). Design, scripts and this
text: Claude (Anthropic, Opus 5.5). Human review level: direction only. Everything run under this registration is
**self-tested** (M10).
**Method:** [METHOD.md](../../METHOD.md) (md5 `50e8a91a448251f8fc5d70f6971b74ae`), [WORKFLOW.md](../../WORKFLOW.md)
(md5 `8ab6970501f53cb288d35f19787be529`) and [CONTROLS.md](../../CONTROLS.md) (md5 `2a68368e99f87430bd15e8074811452c`),
as on `main` at `0fb892a`.
**Subject:** [SigmaHQ/sigma](https://github.com/SigmaHQ/sigma) at `05d1031f537e830b76da53bae2400c5814c89165`: the
three Python jobs of `.github/workflows/sigma-test.yml` (sha256 `1fe29813…d528`).
**Parents:** [PA-SIGMA-001](../pa_sigma_001/PREREG.md) (1,502 BROADENING mutants; the regression-test job catches
none) and [PA-SIGMA-002](../pa_sigma_002/PREREG.md) (the goodlog job catches 305; 1,197 pass both). This is
PA-SIGMA-002's registered door P5.

## W1: question

**The question (observable):** of the 1,502 BROADENING mutants, and of the 1,197 that pass both behavioural jobs,
which would make SigmaHQ's static rule checks fail if each replaced its original rule?

**What the code can express.** Read before registering (VERIFIED FROM SOURCE):
- `sigma-test.yml` runs, on every push and pull request: `yamllint` (strict), `python tests/test_logsource.py`,
  `python tests/test_rules.py`, `sigma check --fail-on-error --fail-on-issues --validation-config
  tests/sigma_cli_conf.yml rules*` with `pySigma-validators-sigmahq==0.21.*`, and a duplicate-id grep.
- None of these runs a rule against an event. They read a rule's fields and shape.
- Two of them can see the shape an edit leaves behind:
  - `test_rules.py`'s `test_selection_list_one_value` fails a field list holding one value (and a keyword list
    holding one non-string value).
  - The validator `sigmahq_invalid_all_modifier` fails a key carrying `|all` with fewer than two values.
- Dropping one value from a two-value list leaves exactly such a list. Sigma gives `[x]` and `x` the same meaning,
  and `|all` over one value the same meaning as no `|all`.

So the expectation, before any mutant meets a check: the static checks fail some DROP_VALUE mutants for their
shape, not for what they match. If a contributor wrote the same edit in house style, the checks would pass it.

## Design (C-DESIGN)

- **Design:** audit. Deterministic runs of a fixed, fully enumerated set, at one commit, in two arms.
- **Arm A:** each mutant exactly as PA-SIGMA-001 wrote it.
- **Arm B, the simplest rival as an arm (M14):** the same mutants in house style. A field list left with one value
  becomes that value. A key carrying `|all` over one value loses `|all`, unless that would duplicate a key already
  in the map (18 mutants; they keep `|all`). 350 mutants change. For the other 1,152 the arm-B text is the arm-A
  text, and arm B takes their arm-A verdict.
- **Strongest claims it can carry:** exact counts and existence ("this edit passes the regression, goodlog and
  static jobs"), over this set, at this commit, with these tool versions.
- **Out of scope:**
  - `yamllint` checks layout, not meaning. The mutants are machine-dumped (PyYAML defaults), so a layout failure
    would say nothing about the edit.
  - The duplicate-id grep cannot fail, because an in-place edit keeps the rule's id.
  - The schema validation workflow (`sigma-validation.yml`) is a door (P6).
  - Human review.

## Instrument

**Real code (M4).** SigmaHQ's own test files and validation config, run from a copy of the checkout with the
workflow's commands:

| Check | Workflow job | Command | Pinned file |
|---|---|---|---|
| SC | `sigma-check` | `sigma check --fail-on-error --fail-on-issues --validation-config tests/sigma_cli_conf.yml rules*` | `tests/sigma_cli_conf.yml` sha256 `422c88c0…aea7` |
| TR | `test-sigma-legacy` | `python tests/test_rules.py` | sha256 `fdfca642…49f4` |
| TL | `test-sigma-logsource` | `python tests/test_logsource.py` | sha256 `27b9c036…e014` |

**Tools,** as `pip` resolves the workflow's install lines today, in a Python 3.11.18 venv (the workflow uses 3.11):
pySigma 2.0.1, sigma-cli 4.0.0, pySigma-validators-sigmahq 0.21.0, PyYAML 6.0.3, colorama 0.4.6.

**Staging ([`stage.py`](stage.py)).** A round is a hard-linked copy of the checkout. In it, each staged rule file is
unlinked and rewritten, so the checkout itself is never written. A round holds at most one item per rule. Item *j*
of every rule goes into round *j*: 55 rounds, 2 at a time.

**Attribution.** A staged file is FLAGGED by a check when that check exits non-zero and the file's path appears:
- for SC, on an output line (sigma-cli prints every issue and error with the rule's path);
- for TR and TL, inside a FAIL or ERROR block.

A flag whose only reasons are cross-rule checks could come from two staged files colliding with each other. Those
reasons are `IdentifierCollisionIssue`, `DuplicateTitleIssue` and `DuplicateFilenameIssue` for SC, and
`test_duplicate_detections` for TR. Such an item is re-run alone, and only that run counts. Since the unmutated tree
passes all three checks (G1), a FLAGGED item is one whose replacement of its original would fail that job.

**Stand-in and deviations:**
- **S1, MITRE data ([`sigma_offline.py`](sigma_offline.py)).** pySigma downloads MITRE data the first time a tag
  validator runs. Neither host is reachable from the container (the first `sigma check` here died with HTTP 403).
  The wrapper loads ATT&CK from `enterprise-attack.json` of mitre-attack/attack-stix-data at `c2494b29dd268c46a5d0ea0990553e4327cd2253` (sha256
  `81113ba98afa2928f3dcff62022539f7ce30c315c32e14422f11ff95ce534352`): the file CI downloads, at that commit. It
  loads D3FEND as an empty graph (sha256 `31fd111b…0828`). The D3FEND validator flags only `d3fend.` tags, and no
  rule file under `rules*` has one (count 0), so its result cannot depend on the data. Tags are never edited by a
  mutant.
- **D1:** `rules*` is expanded by the harness (sorted), not by bash.
- **D2 ([`unittest_full.py`](unittest_full.py)):** TR and TL run with `unittest.TestCase.maxDiff = None`, so
  assertion messages list every faulty file. No check changes, and the exit status is the file's own.

## Feasibility counts (C-FEAS)

From [`feasibility.py`](feasibility.py), output [`feasibility_output.txt`](feasibility_output.txt):

```
SigmaHQ 05d1031f537e830b76da53bae2400c5814c89165
0. broadening mutants rebuilt 1502 in 282 rules; identity 4bb6343d864618f43b895e98a711c7599f29e895173adaec5ef7621d5d596ba0 (registered 4bb6343d...: True)
   PA-SIGMA-002 caught 305; SURV (pass both behavioural jobs) 1197; SURV identity b0c45e1108bb89987bac7fb7b75a7d5fa1863aba3b237d8469d4f382ac11bc6b
1. by operator: all {'DROP_FIELD': 319, 'DROP_VALUE': 869, 'NEVER_SEL': 314}; SURV {'DROP_FIELD': 209, 'DROP_VALUE': 767, 'NEVER_SEL': 221}
2. originals with a derived TR or SC flag (must be 0, since the unmutated checks pass): TR 0, SC 0
3. arm A all : DERIVED_TR  350 {'DROP_VALUE': 350}
            DERIVED_SC  211 {'DROP_VALUE': 211}
            DERIVED_TR or SC  350 {'DROP_VALUE': 350}
3. arm A SURV: DERIVED_TR  292 {'DROP_VALUE': 292}
            DERIVED_SC  189 {'DROP_VALUE': 189}
            DERIVED_TR or SC  292 {'DROP_VALUE': 292}
4. arm B: 350 mutants change under house style (292 in SURV); |all kept because dropping it would duplicate a key: 18 (18 in SURV); arm B DERIVED_TR 0, DERIVED_SC 18 (18 in SURV)
5. arm B equivalence (G6): {'parse': 6, 'query': 344} (query: same Lucene query; parse: backend cannot convert, same pySigma detection)
6. staged items 2446 {'BAD_LOGSOURCE': 10, 'DANGLING': 10, 'IDENTITY': 282, 'MUTANT': 1852, 'ONE_VALUE': 10, 'ROUNDTRIP': 282}; rounds needed 55 (items per rule: min 3, median 6)
7. rule files under rules* with a d3fend tag: 0
8. tools: pysigma 2.0.1 | sigma-cli 4.0.0 | pysigma-validators-sigmahq 0.21.0 | pyyaml 6.0.3 | colorama 0.4.6 | python 3.11.18 | ATT&CK file sha256 81113ba98afa2928f3dcff62022539f7ce30c315c32e14422f11ff95ce534352 (pinned: True)
9. G1 unmutated tree: SC exit 0 completed True 14.0s; TR exit 0 completed True 9.4s; TL exit 0 completed True 5.6s
10. ROUNDTRIP pre-check, 282 rules in one round: SC exit 0 completed True flagged 0; TR exit 0 completed True flagged 0; TL exit 0 completed True flagged 0
```

DERIVED_TR and DERIVED_SC are not the checks. They are short mirrors of the two checks' source
(`derived_tr`, `derived_sc` in `feasibility.py`), applied to each mutant's parsed YAML. The predictions below say the
real checks agree with them exactly.

## Gates (instrument checks, not predictions)

Any gate failing → exit 2, no verdict.

- **G1:** in every run, the unmutated tree passes SC, TR and TL (exit 0).
- **G2:** the rebuilt broadening set has identity `4bb6343d…96ba0`, and SURV has identity `b0c45e11…bc6b`.
- **G3:** IDENTITY controls (each of the 282 rules staged as its own bytes): **0 FLAGGED** by any check.
- **G4:** ROUNDTRIP controls (each rule loaded and dumped again, unchanged, as the mutants are dumped):
  **0 FLAGGED** by any check. A flag would mean the dump path, not the edit, trips a check.
- **G5:** positive controls on the 10 lowest-id rules with a string-valued field. Each check must flag at least
  9 of its 10:
  - DANGLING (an unused selection added) must be flagged by SC;
  - ONE_VALUE (one string value wrapped in a one-element list, the same meaning) must be flagged by TR;
  - BAD_LOGSOURCE (an extra `logsource` key) must be flagged by TL.

  This shows each check can say FLAGGED through this harness.
- **G6:** every arm-B text that differs from its arm-A text means the same thing. It gives the same Lucene query
  (pySigma 1.5.1 with pySigma-backend-elasticsearch 2.1.1, the venv PA-SIGMA-002 ran with), or, where that
  backend cannot convert the rule (field references, 6 pairs), the same pySigma detection.
- **G7:** a second run gives the same DIGEST.
- **G8:** every check in every round ran to its end: exit 0 or 1, SC's summary printed, and TR and TL reporting
  `Ran 11 tests` and `Ran 3 tests`.
- **G9:** after the run, the SigmaHQ checkout is unchanged (`git status --porcelain` empty, HEAD `05d1031`).

## Predictions (registered before observing; M1, M2)

| ID | Prediction | Credence | Precisely wrong if |
|---|---|---|---|
| P1 | Arm A: TR flags **exactly** the 350 DERIVED_TR mutants and no other mutant | 0.75 | any mutant is in one set and not the other |
| P2 | Arm A: SC flags **exactly** the 211 DERIVED_SC mutants and no other mutant | 0.6 | any mutant is in one set and not the other |
| P3 | TL flags **no** mutant, in either arm | 0.9 | it flags one |
| P4 | Arm B: TR flags **no** mutant, and SC flags **exactly** the 18 that keep `|all` | 0.6 | any other outcome |

**Why these numbers.** The derivation above says that the static checks see shape, not meaning. P1 and P2 test that
reading of the source against the running tools. P2 and P4 carry less credence because sigma check runs 74 validators (80 installed,
6 turned off by the config). One I have not thought of could fire on an edit, for example on the value NEVER_SEL writes into a
`Hashes` or `User` field. P3 is near-certain from the source, because no operator touches the logsource or adds a
field name.

**What the four would mean together.** Of the 1,197 mutants that pass both behavioural jobs, the static checks would
stop 292 as written (arm A), all for shape, and 18 in house style (arm B). That would leave 905 or 1,179 edits that
pass every automated rule check this study and its parents ran.

## Simplest rival (M14), as arms

- **"The static checks catch weakening as such."** Arm B answers it. In house style the edits mean the same
  (G6). If the rival held, the catches would stay.
- **"The static checks see nothing, or this harness cannot hear them."** The positive controls (G5) answer it,
  and P1 is precisely wrong if they are silent.

## Pre-mortem (W2)

1. **Attribution misses or invents flags.** The path could be printed in a form the matcher does not find, or a
   message could be cut short. P1 and P2 would then fail by undercount. G5 checks the matcher on known positives,
   and D2 removes unittest's truncation.
2. **Two staged files collide** (duplicate detection) and each looks caught. Handled by the solo re-run of
   cross-rule-only flags.
3. **A check stops early** (a crash, a timeout, a missing data file) and reads as a pass. G8 fails the run.
4. **Hard links:** a write through a link would change the checkout for every later round. `stage()` unlinks
   first, and G9 checks the checkout after the run.
5. **The MITRE stand-in differs from CI's download.** Only tag validators read the data, and no mutant edits a tag,
   so any difference would show in G1 and G3, not as a flag on a mutant.

## Sabotage (anti-vacuity of the verdict)

`--sabotage` stages every mutant's original rule in place of the mutant, in both arms, and leaves the controls as
they are. Expected: no mutant FLAGGED. P1, P2 and P4 are then refuted, P3 holds (1 of 4), the gates still pass, and
the harness exits 1.

## Stopping rule, outputs, data handling (C-PRIVATE)

- One full run, then a second for G7. No run is discarded.
- RECORDED (the statuses and DIGEST) is pinned in its own commit. Then come the pinned run and the sabotage run.
- The harness writes per-item verdicts and per-round summaries to `results/pa_sigma_003/`. They hold SigmaHQ rule
  paths, issue names and test names only.

## Generated inputs (C-SYNTH)

The mutants, their house-style forms and the controls are generated. The results name three arm-A FLAGGED, three
arm-B FLAGGED and three unflagged SURV mutants for a person to look at, with diffs sent to Chad outside the
repository. That look is Chad's, and it is recorded as pending until he does it.

## Trigger table (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | yes: the counts above, G1 and the ROUNDTRIP pre-check, committed with this registration |
| Noise | C-NOISE | yes: the checks are deterministic programs on fixed inputs. G1 ran twice through `feasibility.py` before registering (both exit 0 on all three checks), and G7 repeats the whole run |
| Statistics | C-STAT | no: exact counts over an enumerated set; no sample is generalised from |
| Evidence | C-EVID | no: the question is CI sensitivity, not how a rule treats its evidence |
| Independence | C-INDEP | yes: self-tested. Claude designed, built and runs it, and wrote the derivations it tests |
| External | C-EXT | yes: SigmaHQ's rules, tests and validation config (Detection Rule License 1.1); pySigma (LGPLv2, per its package classifier), sigma-cli (LGPL-2.1-or-later) and pySigma-validators-sigmahq (LGPL 2.1 licence file); MITRE ATT&CK data. Pinned by commit or sha256. No outside text is quoted |
| Device | C-DEVICE | yes: x86_64 container only. NOT VALIDATED on the S25 |
| Verdict code | C-BUILD | yes: the harness returns FLAGGED / not flagged per check and fails closed (exit 2) on any gate or pin failure |
| Exploration | C-EXPLORE | yes: see below |
| Method comparison | C-METHCOMP | no |
| People's data | C-PRIVATE | no personal data: rule files, tool output and public ATT&CK data only |
| Design | C-DESIGN | yes: audit; existence and exact counts only |
| Held-out | C-HOLDOUT | no: nothing is chosen from the evidence judged. The derived sets, the arms and the controls are fixed here |
| Generated inputs | C-SYNTH | yes: see Generated inputs |

## Limits

- **Three of SigmaHQ's checks, not all of them.** `yamllint`, the schema validator and human review are not run.
- **One commit, one tool resolution, one MITRE snapshot.** `pip` gives a later run newer tools.
- **PA-SIGMA-001's mutant set,** with its cap of 25 per operator per rule. Equivalent mutants count as passing.
- **House style is this study's rewrite.** It is one equivalent form, not the only one, and 18 edits have none
  inside one selection map.
- **Self-tested only** (M10). The derivations and the harness are by the same author.

## Exploration before this registration (C-EXPLORE)

Logged in [FORKS.md](../../FORKS.md) as PA-SIGMA-003-X1 and X2.

- Read the sources: `sigma-test.yml`, `sigma-validation.yml`, `tests/test_rules.py`, `tests/test_logsource.py`,
  `tests/sigma_cli_conf.yml`, the validator list and the source of `SigmahqInvalidAllModifierValidator`.
- Installed the tools. The first `sigma check` failed on the MITRE download (HTTP 403), which led to S1.
- Ran SC, TR and TL on the unmutated checkout: all exit 0.
- A format probe in a hard-linked copy, with three hand-made defects in three rules: an unused selection, a
  `|contains|all` list cut to one value, and a `|contains` list cut to one value. SC flagged the first two
  (`DanglingDetectionIssue`, `SigmahqInvalidAllModifierIssue`); TR flagged the last two
  (`test_selection_list_one_value`); TL flagged none. This is close to the mechanism the predictions name, and it
  is disclosed as such. It used hand edits, not mutants.
- Converted two hand-made pairs with the Lucene backend to see whether one-value lists and `|all` over one value
  render like their house-style forms (they do). Checked the 6 field-reference pairs by parsed detection.
- Ran `feasibility.py` twice; the second version added the parse fallback to the equivalence count. The counts were
  otherwise identical.

No mutant was staged or checked by SC, TR or TL.

## Provenance and credit (M13)

AI participation: Claude (Anthropic, Opus 5.5) designed this and wrote the scripts and text on 2026-10-30, at Chad
Holland's direction → human validation: direction only → human editing/curation: none → responsibility: Chad
Holland. SigmaHQ's rules, tests and configuration are SigmaHQ's. pySigma, sigma-cli and the validators are the
SigmaHQ project's, and ATT&CK is MITRE's.

## Next unrun test (M15)

- **P6:** run the schema validator (`sigma-validation.yml`, schema v2.1.0) and `yamllint` on the house-style
  mutants written in SigmaHQ's own YAML layout.
- **P7:** give the 18 key-clash edits an equivalent two-selection form, and check them again.
- **P8:** PA-SIGMA-001's P6, negative samples. Not run.
