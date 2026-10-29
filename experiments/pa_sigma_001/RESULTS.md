# PA-SIGMA-001 results: do SigmaHQ's regression tests fail when a tested rule is weakened or broken?

**State:** RUN. **VERDICT 4 of 4 as registered.** P1–P4 predicted where SigmaHQ's tests are *weak*. "Held" therefore means the tests missed what the predictions said they would miss; it does not mean anything passed.
- **Self-tested only** (M10).
- **C-SYNTH person-look: pending.** The six-mutant look sample was sent to Chad Holland on 2026-10-29. Until his look is recorded here, none of these results counts toward a claim.

**Record.** The commits below are in the order they happened; the registration was on GitHub before the harness existed.

| Step | Commit | Identity |
|---|---|---|
| Registration ([PREREG.md](PREREG.md)) | `1b0b9c4` | pushed before the harness existed |
| Harness | `32a7028` | `run_pa_sigma_001.py` md5 `d05d24ae2490baf38c96483c2c5f6ff4` |
| Run outputs | `5a26f40` | |
| `RECORDED` pin | `5329459` | harness md5 `2f02c1cef28605bf459f29d425912354` |

**Subject:** SigmaHQ/sigma `05d1031f537e830b76da53bae2400c5814c89165`, the tip of its `master` branch on 2026-10-29.

## What could have gone wrong, first (M8)

1. **Self-testing.** Claude designed the study, wrote the operators and the harness, ran them, attacked the results and wrote this document. Nobody else has reviewed any of it, and two Claude runs are not independent (C-INDEP).
2. **An unregistered finding outranks the registered ones.** SigmaHQ's JSON regression path cannot fail on a rule that does not match: `json_matcher` prints `NO-MATCH`, and the runner counts every output line that ends in `MATCH`. It turned up in the NEVER_FIRE control's per-test counts and was confirmed afterwards (post-hoc finding A below). It was not predicted. It is reported as an observation (M9) with its evidence, and its confirmation needs a fresh registration (M11).
3. **Registration errors.**
   - **JSON samples counted by line.** `feasibility.py` counted *non-empty lines* as "events" for every non-EVTX sample. A `json` sample is one JSON document, so the three JSON samples count 1 event each, not 52, 66 and 66. The registered counts of "tests whose sample holds no more events than the expected match count" are therefore wrong: **467**, not 464, and **7**, not 10, hold more events than expected. D2 and the harness's D2 line inherit the same error (`posthoc.py` Q1b). P1–P4 do not use these counts.
   - **D2's assumption is false for one rule.** D2 assumed the checker reports at most one match per event. Rule `06d71506-7beb-4f22-8888-e2e5e2ca7fd8` gets **2 match lines from a 1-event sample, both carrying the same event** (post-hoc finding B). The runner's "match count" counts checker output lines, not distinct events.
   - **Corrected D2.** IDENTITY's count equals the sample's events in **468 of 474** tests. Among the 467 tests whose sample holds no more events than expected it equals them in **466**; the exception is that duplicated line.
4. **Deviations.**
   - The registration names two console outputs, `run1.txt` and `run2.txt`. The harness also runs the whole census twice inside each invocation for G4, so the record holds four census passes over two invocations.
   - There is a third invocation after pinning, `run3_pinned.txt`.
   - Nothing in the method changed.
5. **Model-derived against real.**
   - Real: SigmaHQ's rules, samples and runner, and the checker binaries at the versions its CI pins.
   - Stand-ins: the mutants, for real edits (M4). The environment is Python 3.13.18 on x86_64 Linux; CI uses Python 3.11.
   - Not run on the S25. **NOT VALIDATED on the S25**, and no device claim is made.
6. **Reviews that did not happen.**
   - No human line-by-line review.
   - The person-look of the generated inputs (C-SYNTH) is pending.
   - No SigmaHQ maintainer has seen any of this.

## Raw output (pasted, `results/pa_sigma_001/run1.txt`)

```
==============================================================================
PA-SIGMA-001: SigmaHQ regression-test job against one-point mutants (self-tested)
==============================================================================
sigma_head: 05d1031f537e830b76da53bae2400c5814c89165
runner_sha256: d1b88d4b465ce3b227b26a8f76bdd59249e1c79c8f7fc018618f053e0080a438
thor_sha256: 8e72d9223e2c3c1d2d647b08e10118a3a067975ce7eba37dc1623f9d79604120
evtx_checker_sha256: d672e07a516f3f72eaae8244f99fa2c5b133885a4401eb05a272903857d767e2
json_checker_sha256: abd279e669a04f63db2bb505efc94e36be79d740aec5221b3547b53551966368
mutants_md5: 97b57d4f5fd5ebbbf4ff9a1b93bbcd0f
harness_md5: d05d24ae2490baf38c96483c2c5f6ff4
python: 3.13.18
platform: Linux x86_64
packages: {'pySigma': '1.5.1', 'sigma-cli': '3.1.0', 'pySigma-backend-golangexpr': '1.0.0', 'PyYAML': '6.0.3', 'python-evtx': '0.8.1'}
sabotage: False
rules: 471
mutants: 6922
passes: 2 (47 s, 50 s)

FAILURES AND EXCLUSIONS FIRST
  G4 UNRESOLVED (outcome or counts differ between passes): 0 []
  G1 IDENTITY not SURVIVED: 0 []
  G2 rules excluded (IDENTITY/ROUNDTRIP not SURVIVED or NEVER_FIRE not KILLED): 0 (max 23) []
  G3 INVALID operator mutants: 0 (max 275)
  INVALID controls: 0 []
  G5 direction-label violations (count moved against the label): 0 []

OUTCOMES BY OPERATOR AND DIRECTION (all rules; INVALID and UNRESOLVED shown)
  IDENTITY   CONTROL    KILLED     0  SURVIVED   471  INVALID    0  UNRESOLVED   0
  ROUNDTRIP  CONTROL    KILLED     0  SURVIVED   471  INVALID    0  UNRESOLVED   0
  NEVER_FIRE CONTROL    KILLED   471  SURVIVED     0  INVALID    0  UNRESOLVED   0
  DROP_VALUE BROADENING KILLED     0  SURVIVED   869  INVALID    0  UNRESOLVED   0
  DROP_VALUE NARROWING  KILLED   308  SURVIVED  2571  INVALID    0  UNRESOLVED   0
  DROP_FIELD BROADENING KILLED     0  SURVIVED   319  INVALID    0  UNRESOLVED   0
  DROP_FIELD NARROWING  KILLED    14  SURVIVED   236  INVALID    0  UNRESOLVED   0
  NEVER_SEL  BROADENING KILLED     0  SURVIVED   314  INVALID    0  UNRESOLVED   0
  NEVER_SEL  NARROWING  KILLED   719  SURVIVED   159  INVALID    0  UNRESOLVED   0
  operator mutants 5509; distinct texts (sha256) 5509; included rules 471

SURVIVORS: CAN THE SAMPLE SEE THEM? (scored mutants of included rules)
  BROADENING SURVIVED  1502: match count CHANGED     0, unchanged  1502; over-match warning 0
  NARROWING  SURVIVED  2966: match count CHANGED     4, unchanged  2962; over-match warning 19
  NEVER_SEL BROADENING (an exclusion switched off): SURVIVED 314 of 314; rules with such a survivor 126 of 126
  D2: tests where IDENTITY matches every sample event: 465 of 474; among the 464 tests whose sample holds no more events than expected: 463
  per-rule NARROWING kill fraction over 466 rules: min 0.000 q25 0.214 median 0.500 q75 1.000 max 1.000; rules with every narrowing mutant KILLED 153; with none KILLED 9

PREDICTIONS (registered in PREREG.md)
  P1: HELD  (BROADENING mutants KILLED: 0 of 1502)
  P2: HELD  (DROP_VALUE NARROWING SURVIVED: 2571 of 2879)
  P3: HELD  (rules with a surviving NARROWING mutant: 313 of 466)
  P4: HELD  (NEVER_SEL NARROWING SURVIVED: 159 of 878)
VERDICT 4 of 4 as registered
DIGEST 765032efccf9cb7e6c9f7a6c41195980a9dfe78ef075b8bbbc40e107cbef929d
wrote results.json sha256 8b82f0928d014ab2b4d572e83180ed34018e2d1382a59efc2fb01bcfffef0cfc
wrote look_sample.json sha256 62e06fa61dd8db06230eb0f81a972fd9b0626b8448d46d99c02659ffcb80c9ac
wrote look-sample diffs to /tmp/claude-0/-home-claude/20deaf03-7883-5e1f-bdbb-23fc34858bca/scratchpad/pa_sigma_001_look_diffs.md
GATE: PASS
RECORDED: not pinned yet
exit 0
```

The later runs:
- `run2.txt` (a second, fresh invocation) prints the same lines apart from timing, with the same DIGEST. Its `results.json` and `look_sample.json` are byte-identical to run 1's (sha256 `8b82f092…` and `62e06fa6…`).
- `run3_pinned.txt` (the pinned harness) ends `RECORDED: reproduced`, exit 0.
- `selftest.txt` ends `SELFTEST: PASS (0 failure(s))`, exit 0.
- `sabotage.txt` excludes 471 rules under G2 and ends `GATE: FAIL`, exit 1.

Raw outputs opened and read before writing this (W6, Amendment 4 D7):
- the look sample: two each of BROADENING/SURVIVED, NARROWING/SURVIVED and NARROWING/KILLED, covering P1, P2 and P4;
- the per-mutant records in `results.json` for NEVER_SEL narrowing survivors (P4) and for the nine rules in which no narrowing mutant was killed (P3);
- the match lines of rule `06d71506…`;
- json_checker's output on literal `true` and `false`.

## Predictions

| ID | Prediction (registered) | Outcome | Count from the run |
|---|---|---|---|
| P1 | No valid BROADENING mutant of an included rule is KILLED | **HELD** | 0 of 1,502 KILLED |
| P2 | More than half of the valid DROP_VALUE NARROWING mutants SURVIVE | **HELD** | 2,571 of 2,879 SURVIVED (89.3%) |
| P3 | More than half of the included rules with a valid NARROWING mutant have one that SURVIVES | **HELD** | 313 of 466 rules (67.2%) |
| P4 | At least 10% of the valid NEVER_SEL NARROWING mutants SURVIVE | **HELD** | 159 of 878 SURVIVED (18.1%) |
| P5 | (door) the goodlog job on the broadening survivors | NOT RUN | — |

All the gates held:

| Gate | Result |
|---|---|
| G1, identity | 0 failures |
| G2, rules excluded | 0 |
| G3, INVALID mutants | 0 |
| G4, UNRESOLVED between passes | 0, and the two invocations agree byte for byte |
| G5, direction violations | 0 |
| Sabotage | must exit 1, and does |

Percentages come from `posthoc.py` Q0.

## Observation (M9)

### Weakening a rule, by making it match more

- **None of these edits failed a test: 1,502 of 1,502 SURVIVED.**
  - None changed any test's match count.
  - None triggered the runner's over-match warning.
- **Switching an exclusion filter off is invisible.** 314 of 314 NEVER_SEL BROADENING mutants SURVIVED, in 126 of 126 rules that have an exclusion.
- **Making an exclusion broader is mostly invisible.** DROP_FIELD NARROWING, the same change seen from the other side: 236 of 250 SURVIVED (94.4%).
- **Even samples with spare events show nothing.** Seven EVTX samples hold more events than the rule should match. Nine broadening mutants belong to rules with such a sample, and none of the nine changed a count (`posthoc.py` Q6).

### Breaking a rule, by making it match less

- **2,966 of 4,007 SURVIVED (74.0%).**
- **Dropping one value from a list:** 2,571 of 2,879 SURVIVED.
  - Per rule, the median fraction killed is 0.125.
  - In 63 of 289 rules none was killed (Q8).
- **Disabling a whole positive selection:** 159 of 878 SURVIVED.
  - Every survivor is in a rule whose condition offers an alternative between positive selections (an `or` outside a negation, or `1 of`/`any of`): 159 SURVIVED and 99 KILLED there.
  - In rules without such an alternative, 620 of 620 were KILLED. (`posthoc.py` Q5; the heuristic was checked on 12 hand-written conditions, and it is post hoc.)
- **Per rule:**
  - In 153 of 466 rules every narrowing mutant was KILLED.
  - In 9 rules none was. All 9 have a top-level `1 of`/`or` (Q4).
  - The median kill fraction is 0.5.
- **Four survivors the sample did see.** In rule `5bac7a56…` four narrowing survivors lowered the count from 2 to 1. That test sets no `match_count`, and any match passes (Q2).

### Post-hoc finding A: the JSON test path cannot fail (EXPLORATORY)

- **Every JSON test passed.** Across all 62 mutants, controls included, of the three rules with a JSON test, the JSON test passed 62 times. That includes each rule's NEVER_FIRE control.
  - In 14 of those, the same rule's EVTX test failed (Q7b).
  - The JSON test's match count was 1 every time.
- **Cause, VERIFIED FROM SOURCE:**
  - SigmaHQ/json_matcher v0.0.2 (`main.go`, the release CI pins) prints `MATCH` or `NO-MATCH` for a `json` sample, and `Line i: MATCH` or `Line i: NO-MATCH` for `ndjson`.
  - `regression_tests_runner.py` line 384 keeps `[ln for ln in result.stdout.splitlines() if ln.endswith("MATCH")]`, and `"NO-MATCH".endswith("MATCH")` is true.
  - So each evaluated event counts as a match whether or not it matched.
- **Confirmed through the runner's own `run_json_checker`** (`json_match_count_check.py`, output `json_match_count_check.txt`):
  - On each of the three rules, a copy whose condition can never be true gets the verdict PASS, 1 counted match, and the counted line is `NO-MATCH`.
  - json_checker prints `NO-MATCH` on the literal expression `false`, and the runner's rule counts it.
- **Since when:** the JSON path was added by SigmaHQ PR #6203 (merged 2026-08-19). json_matcher has printed `NO-MATCH` since its first code commit (`3bb3022`, 2026-08-06, the commit tagged v0.0.2). At `05d1031` the three JSON-tested rules also have EVTX tests, which do fail, so today nothing passes CI because of this.

### Post-hoc finding B: one event, two matches (EXPLORATORY)

- **What was seen** (`duplicate_match_check.py`):
  - Rule `06d71506-7beb-4f22-8888-e2e5e2ca7fd8` has logsource `{product: windows}` and condition `keywords and not filter`.
  - Its sample holds 1 record, by python-evtx and by the file header's next record number of 2.
  - The runner counts 2 match lines for it, and the two carry 1 distinct event payload.
  - This explains the over-match warning on the unmutated suite (X1).
- **Possible cause, not verified:** a product-only logsource reaching the event's channel through more than one entry of `thor.yml`.

## What this shows and does not show (M7)

| Axis | Status | Scope |
|---|---|---|
| Implementation: SigmaHQ's runner, EVTX path | PASS | A rule that can never fire fails its EVTX test, 471 of 471 |
| Implementation: SigmaHQ's runner, JSON path | **FAIL** | Existence: 3 of 3 JSON tests pass for a rule that can never fire, through the runner's own function and the CI-pinned binary |
| Empirical: what the regression job can see, at `05d1031` | measured; self-tested | See the list below |
| Mathematical | not claimed | D1 (a broadening mutant matches a superset) is a derivation, not a formal proof |

Within this enumerated set of mutants, the regression job sees:
- **No edit that only broadens a rule,** including switching an exclusion off. There are two reasons:
  1. the runner treats over-matching as a warning;
  2. in 467 of 474 tests the sample holds no event the rule should not match.

  Either reason alone would hide these edits.
- **A narrowing edit only when it removes the exact value or branch the sample's event used.**

**Not shown:**
- any rate of real-world regressions or tampering: the mutants are stand-ins (C-DESIGN);
- that SigmaHQ's CI as a whole misses these edits. The goodlog job runs every rule against benign baseline logs and fails on unexpected matches, so it may catch some broadened rules; that is P5, unrun;
- anything about the 3,028 test/stable rules without a regression test, or about detection quality in production.

## Candidate fixes (proposals; changes to SigmaHQ are its maintainers' decision)

1. **JSON counting.** Count a line only if its last whitespace-separated token is exactly `MATCH`, for example `ln.split()[-1] == "MATCH"`. Add a CI self-check: a deliberately never-matching rule whose JSON test must fail. This is the M3 control the path lacks.
2. **Tests that something does not match.** Allow `match_count: 0` tests, or per-rule negative samples, at least for rules with an exclusion. That is door P6.
3. **Count distinct events,** not output lines, or make duplicated lines visible.
4. **Mutation checks for new rules.** For example, disable each positive selection in turn and flag the ones whose test still passes. That marks the alternatives the sample never exercises.

An upstream report of finding A has been drafted for Chad Holland. It has **not** been filed: filing is a public post under his name, and it is his call.

## Open (M15)

- **P5 (door, unrun):** the goodlog job on the 1,502 broadening survivors.
- **P6 (door, unrun):** negative samples per rule against the NEVER_SEL broadening mutants.
- **A fresh, registered confirmation of finding A** (M11): at a later SigmaHQ commit, or after a fix, a never-matching rule's JSON test must fail.
- **C-SYNTH person-look:** pending.

## Provenance and credit (M13)

- **Chain:** Claude (Anthropic, Opus 5.5) designed, built, ran, attacked and wrote → human validation: not performed → human editing/curation: direction by Chad Holland (2026-10-29) → human responsibility: Chad Holland. Human review level: direction only.
- **Outside material:**
  - SigmaHQ's rules, samples and runner are the subject (rules under the Detection Rule License 1.1). The NextronSystems evtx-sigma-checker and SigmaHQ's json_matcher are the instruments.
  - No endorsement is implied, and their maintainers have not been contacted.
  - No rule text or event content is committed.

*Vincit Omnia Veritas.*
