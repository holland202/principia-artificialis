# PA-SIGMA-001: do SigmaHQ's regression tests fail when a tested rule is weakened or broken?

**State:** REGISTERED, NOT RUN. No mutant has been run against any test. This registration is committed with its feasibility counts and its same-input noise check, before the harness exists.
**Authors:** Direction: Chad Holland (2026-10-29: blue-team tests and simulations for Principia; choice of path delegated). Design, mutation operators, feasibility and noise scripts, and this text: Claude (Anthropic, Opus 5.5). Human review level: direction only. Everything run under this registration is **self-tested** (M10).
**Method:** [METHOD.md](../../METHOD.md) at `46034aa` (md5 `50e8a91a448251f8fc5d70f6971b74ae`), [WORKFLOW.md](../../WORKFLOW.md) (md5 `8ab6970501f53cb288d35f19787be529`) and [CONTROLS.md](../../CONTROLS.md) (md5 `2a68368e99f87430bd15e8074811452c`), as on `main` at `78726b8`.
**Subject:** [SigmaHQ/sigma](https://github.com/SigmaHQ/sigma) at `05d1031f537e830b76da53bae2400c5814c89165`: its runner `tests/regression_tests_runner.py` (sha256 `d1b88d4b465ce3b227b26a8f76bdd59249e1c79c8f7fc018618f053e0080a438`) and its CI workflow `.github/workflows/regression-tests.yml`.
**Sibling:** [PA-HONEY-001](../pa_honey_001/PREREG.md), the first blue-team study in this repository.

This study uses mutation testing as its instrument for a question about someone else's test suite. It does not adopt mutation testing into SWAY: that stays a door in CONTROLS.md until M18 says otherwise.

## W1: question

**The question (observable):** for each of the 471 SigmaHQ rules that has a regression test at `05d1031`, when one small edit lets the rule's detection logic match more events (broadening) or fewer (narrowing), does SigmaHQ's own regression-test job report a failure for that rule?

**What the code can express.** Read before registering; this is VERIFIED FROM SOURCE, not run:
- A test's sample holds events the rule must match. The CI job is named `true-positive-tests`. No sample holds events a rule must *not* match.
- The pass rule is in `run_tests` (lines 561–572) and `run_json_checker` (lines 388–401):
  - fewer matches than `match_count` is an error and the test fails;
  - more matches than `match_count` prints a `Warning` and the test passes;
  - a test without `match_count` passes on any match.
- CI runs: `python tests/regression_tests_runner.py --rules-paths rules rules-emerging-threats rules-threat-hunting --evtx-checker ./evtx-sigma-checker --thor-config tests/thor.yml --ignore-validation --json-checker ./json_checker`.

The source therefore says broadening cannot fail a test. What it cannot say is how much narrowing the samples catch, and that is what this study measures.

**The interpretation it might support, kept separate (M9):** how much of a detection rule's logic its test actually pins down, and so how much weakening or tampering a positive-only detection test suite can see. That belongs in the results, not here.

## Design (C-DESIGN)

- **Design:** audit. A deterministic census of a fixed, fully enumerated set of mutants, at one commit.
- **Strongest claims it can carry:** existence ("this one-point edit to this rule passes the regression-test job") and exact counts over this enumerated set.
- **Out of scope:**
  - rates of real-world rule regressions or tampering;
  - the 3,028 test/stable rules that have no regression test at all;
  - SigmaHQ's other CI jobs (the goodlog baselines, `sigma check`, `test_rules.py`, `test_logsource.py`), any of which may catch a mutant this study counts as SURVIVED;
  - other rule repositories, and detection quality in production.

## Instrument (W3)

**Real code (M4).** The harness will import SigmaHQ's runner and call its own `find_rules_with_tests`, `run_tests`, `run_evtx_batch`, `run_json_checker` and `compile_rule_to_expr`, copying none of them. A mutant's verdict is the runner's verdict.

**Tools,** as SigmaHQ's CI pins them at `05d1031`:

| Tool | Version | Source | sha256 |
|---|---|---|---|
| evtx-sigma-checker | v0.8.5 | NextronSystems/evtx-baseline GitHub release | `d672e07a516f3f72eaae8244f99fa2c5b133885a4401eb05a272903857d767e2` |
| json_checker (json_matcher) | v0.0.2 | SigmaHQ/json_matcher GitHub release | `abd279e669a04f63db2bb505efc94e36be79d740aec5221b3547b53551966368` |
| `tests/thor.yml` | at `05d1031` | SigmaHQ/sigma | `8e72d9223e2c3c1d2d647b08e10118a3a067975ce7eba37dc1623f9d79604120` |
| sigma-cli, pySigma, pySigma-backend-golangexpr, PyYAML | 3.1.0, 1.5.1, 1.0.0, 6.0.3 | PyPI, inside the pins of `tests/regression_requirements.txt` | — |
| Python | 3.13.18 (CI uses 3.11) | this container | — |

**Mutants:** [`mutants.py`](mutants.py) (md5 `97b57d4f5fd5ebbbf4ff9a1b93bbcd0f`).
- A mutant is the rule with exactly one change in its `detection` section, loaded and dumped again with PyYAML (comments dropped, key order kept).
- Its direction follows Sigma's semantics and the polarity of the selection in the condition. A selection reached through an odd number of `not` is negative (an exclusion).

| Operator | The change | In a positive selection | In a negative selection (an exclusion) |
|---|---|---|---|
| DROP_VALUE | remove one value from a list of two or more values | NARROWING (OR list); BROADENING (`\|all` list) | BROADENING (OR list); NARROWING (`\|all` list) |
| DROP_FIELD | remove one key from a selection map with two or more keys | BROADENING | NARROWING |
| NEVER_SEL | make one whole selection unable to match, by adding a key whose value is `PA-SIGMA-001-NEVER-MATCH-7f3a` | NARROWING | BROADENING (the exclusion is switched off) |

- **Controls, one each per rule:**
  - IDENTITY: the original file, byte for byte. No rule file contains a carriage return or a BOM, so the decoded text re-encodes to the same bytes.
  - ROUNDTRIP: the rule loaded and dumped with no change.
  - NEVER_FIRE: the condition ANDed with a selection that cannot match.
- At most 25 mutants per operator per rule, sites taken in YAML order. Identical mutant texts are kept once (sha256).
- Rules whose condition is a list, contains an aggregation, or names one selection with both polarities are skipped. At `05d1031` none is.

**Rounds.** Round *k* stages the *k*-th mutant of every rule that has one, giving 76 rounds. Each round is one call of the runner's `run_tests` over those rules, so one checker invocation per round, as in CI.

**Outcome per mutant, fail-closed (C-BUILD):**
- **KILLED:** `run_tests` reports a failure for at least one of the rule's tests.
- **SURVIVED:** `run_tests` reports every test of the rule passing.
- **INVALID:** a tool the runner uses for that rule cannot load the mutant. Either the pre-check names the mutant's file in `could not add rules from …`, or, for a rule with a JSON test, `compile_rule_to_expr` raises. The pre-check is the same checker binary with the same arguments and an empty sample directory. An INVALID mutant is neither KILLED nor SURVIVED.
- **Anything else aborts the run** with exit 2 and records no outcome:
  - a checker failure the pre-check cannot attribute to one file;
  - a batch failure inside `run_tests`;
  - a timeout;
  - a test that is neither passed nor failed;
  - a staged file whose sha256 differs from the bytes the harness wrote for that mutant.

**Observation taps.** The harness wraps `run_evtx_batch` and `run_json_checker` to record every test's match count, calling the real function unchanged. For each mutant it also records:
- whether any test has more matches than `match_count`, which is the runner's warning condition;
- **CHANGED:** whether any test's match count differs from IDENTITY's.

## Case matrix and feasibility counts (C-FEAS)

[`feasibility.py`](feasibility.py) (counts only; it runs no rule against a sample). Its output, [`feasibility_output.txt`](feasibility_output.txt), pasted verbatim:

```
SigmaHQ/sigma HEAD 05d1031f537e830b76da53bae2400c5814c89165
evtx-sigma-checker sha256 d672e07a516f3f72eaae8244f99fa2c5b133885a4401eb05a272903857d767e2
json_checker sha256 abd279e669a04f63db2bb505efc94e36be79d740aec5221b3547b53551966368
rules with regression tests (runner discovery): 471
tests: 474 by type {'evtx': 471, 'json': 3}
rules by test types: {('evtx',): 468, ('evtx', 'json'): 3}
rule files containing a carriage return: 0; starting with a UTF-8 BOM: 0
test/stable rules without regression_tests_path (runner's own count): 3028
match_count values: {1: 436, 2: 2, 3: 3, 4: 2, 7: 1, None: 30}
sample events per test: n=474 min=1 median=1 max=66
tests whose sample holds no more events than the expected match count: 464
tests whose sample holds more events than the expected match count: 10
tests with no sample file found: 0
rules mutated: 471; skipped: 0 {}
  DROP_FIELD BROADENING mutants   319  rules  128
  DROP_FIELD NARROWING  mutants   250  rules   48
  DROP_VALUE BROADENING mutants   869  rules  182
  DROP_VALUE NARROWING  mutants  2879  rules  289
  IDENTITY   CONTROL    mutants   471  rules  471
  NEVER_FIRE CONTROL    mutants   471  rules  471
  NEVER_SEL  BROADENING mutants   314  rules  126
  NEVER_SEL  NARROWING  mutants   878  rules  464
  ROUNDTRIP  CONTROL    mutants   471  rules  471
rules reaching the per-operator cap of 25: {'DROP_VALUE': 53, 'DROP_FIELD': 1}
mutants per rule incl. controls: max 76 (rounds needed), total 6922
mutants incl. controls of the 3 rules that also have a json test: 62
```

From these counts:
- There are 5,509 operator mutants: 1,502 BROADENING (319 + 869 + 314) and 4,007 NARROWING (250 + 2,879 + 878). The other 1,413 are controls (3 × 471).
- Three rules have both an EVTX and a JSON test. A mutant of one of them is KILLED if either test fails.
- "Sample events" counts every record in the sample; it does not depend on any rule.

**Derived expectations,** stated before running:
- **D1 (source and semantics).** A BROADENING mutant matches a superset of the original's events, so each of its tests' match counts is at least IDENTITY's. The runner never fails a test for matching more. Expected: no BROADENING mutant KILLED.
- **D2 (sample counts).** In 464 of 474 tests the sample holds no more events than the expected count. IDENTITY passes every test, so if the checker reports at most one match per event, IDENTITY already matches every event in those 464 samples. No broadening can then change their counts. On these samples a count-based test cannot see broadening at all, whatever the runner did with over-matches. The harness reports how many tests this holds for (IDENTITY's count equal to the sample's events).
- **D3 (single-event samples).** Take a positive OR list of *k* values on the path that matched, in a test whose sample has one event. At most one of those values can be the only one the event matches, so at most one of the list's DROP_VALUE mutants can be KILLED and at least *k* − 1 survive.

## Same-input noise (C-NOISE), measured before registering

[`noise_check.py`](noise_check.py) runs the runner's own `run_evtx_batch` and `run_json_checker` on the **unmutated** rules three times. Its output, [`noise_check_output.txt`](noise_check_output.txt), pasted verbatim:

```
run 1: evtx tests 471, match lines 494, tests with zero matches 0; json tests 3, passing 3, match lines 3
run 2: evtx tests 471, match lines 494, tests with zero matches 0; json tests 3, passing 3, match lines 3
run 3: evtx tests 471, match lines 494, tests with zero matches 0; json tests 3, passing 3, match lines 3
evtx tests whose match count differs across the 3 runs: 0
evtx tests whose match lines differ across the 3 runs, as printed: 471
fields that differ between run 1 and run 2 in any match line: ['File', 'MatchStrings', 'RulePath']
evtx tests whose match lines differ with ['File', 'RulePath'] removed and ['MatchStrings'] sorted: 0
json tests whose (pass, match count) differs across the 3 runs: 0
evtx match count distribution (run 1): {1: 460, 2: 5, 3: 3, 4: 2, 7: 1}
```

The match counts and JSON verdicts were the same in all 3 runs. The match lines differed only in two ways:
- their temporary file paths, because the runner stages files in a new temporary directory each call;
- the order of the `MatchStrings` list.

This study's outcomes use counts only.

## Gates (M3; instrument gates, not predictions)

- **G1, identity.** IDENTITY is SURVIVED in 471 of 471 rules, with staged bytes identical to the original file.
  - This is a retrodiction: the unmutated suite passed 474 of 474 before registration (X1 below).
  - If G1 fails, the run is IMPLEMENTATION_ERROR and nothing is scored. A harness fix is a disclosed deviation, followed by a fresh run.
- **G2, anti-vacuity per rule.** NEVER_FIRE is KILLED and ROUNDTRIP is SURVIVED.
  - A rule that fails either control, or has either one INVALID, is excluded from P1–P4 and listed first.
  - If more than 23 rules are excluded (5% of 471), P1–P4 are COULD NOT RUN AS REGISTERED.
- **G3, validity.** INVALID operator mutants are excluded and listed. If there are more than 275 (5% of 5,509), P1–P4 are COULD NOT RUN AS REGISTERED.
- **G4, determinism (C-NOISE).** The full run is executed twice, and every mutant's outcome and match counts must agree, so the DIGESTs are equal. A mutant that differs is UNRESOLVED, listed first and excluded.
- **G5, direction labels (monotonicity).** No BROADENING mutant may have a lower match count than IDENTITY on any test, and no NARROWING mutant a higher one.
  - Violators are listed first.
  - P1–P4 are scored as registered. P2–P4 are also reported with the violators excluded, as a disclosed sensitivity check.
- **Sabotage (M3).** `--sabotage` replaces every mutant's text with the IDENTITY text before it is hashed and staged. The pipeline then believes it is running each mutant while it is running the original, which is pre-mortem failure 1. NEVER_FIRE must then SURVIVE, G2 must fail, and the harness must exit 1.
- `--selftest` must exit 0. It covers polarity and direction on hand-written conditions and rules (both polarities, `|all`, keyword lists, lists of maps, `1 of`/`all of`/`them`, nested `not`), every skip reason, and each abort path.

## Predictions (registered before observing; M1, M2)

Some definitions first:
- **valid:** not INVALID.
- **included rule:** IDENTITY SURVIVED, ROUNDTRIP SURVIVED and NEVER_FIRE KILLED.
- UNRESOLVED mutants (G4) are excluded.
- All comparisons are exact integer counts, with no rounding.

| ID | Prediction | Credence before running | Precisely wrong if |
|---|---|---|---|
| **P1** | No valid BROADENING mutant of an included rule is KILLED | about 0.97 | at least one is KILLED |
| **P2** | More than half of the valid DROP_VALUE NARROWING mutants of included rules SURVIVE | about 0.9 | SURVIVED × 2 ≤ their total |
| **P3** | Of the included rules with at least one valid NARROWING mutant, more than half have at least one NARROWING mutant that SURVIVES | about 0.85 | (rules with a surviving narrowing mutant) × 2 ≤ (rules with a valid narrowing mutant) |
| **P4** | At least 10% of the valid NEVER_SEL NARROWING mutants of included rules SURVIVE: a whole positive selection is made unable to match, and the rule's test still passes | about 0.55, genuinely uncertain | SURVIVED × 10 < their total |
| P5 (door, unrun) | See "Next unrun test" | — | — |

Why the predictions sit where they do:
- **P1** is near-certain from the source (D1). It is registered because a refutation would mean that a direction label, or the checker's semantics, is not what this design assumes.
- **P2 and P3** follow mostly from D3 and from the rules that reach the cap.
- **P4** carries the most information: it measures how often a positive selection can be removed without its test noticing.

The harness will print one outcome per prediction, `VERDICT n of 4 as registered`, and a `DIGEST`.

**Descriptive outputs** (not predictions):
- KILLED, SURVIVED and INVALID by operator × direction.
- Among survivors, CHANGED against unchanged: survivors the sample can see, against survivors that no count-based test on this sample could see.
- BROADENING survivors that triggered an over-match warning.
- The per-rule distribution of narrowing kill fractions.
- NEVER_SEL BROADENING survivors (an exclusion switched off), by rule.
- How many tests D2's condition holds for.

## Simplest rival (M14), as arms

- **Rival A:** mutants survive because the harness runs the original rule, not the mutant.
  - Arms: NEVER_FIRE in every rule through the same path (G2), and the staged-bytes check.
  - `--sabotage` reproduces this rival and must exit 1.
- **Rival B:** outcomes come from YAML serialization, not from the mutation. Arm: ROUNDTRIP in every rule (G2).
- **Rival C:** a surviving narrowing mutant is equivalent to the original, so its survival says nothing about the test.
  - No arm here can separate it. It is stated as a limit.
  - The C-SYNTH look sample puts survivors' diffs in front of a person.

## Pre-mortem (W2)

1. **The harness stages the original rule instead of the mutant,** and everything SURVIVES. It would show as NEVER_FIRE SURVIVED in every rule: G2 fails and the harness exits 1. `--sabotage` demonstrates this case.
2. **A direction label is wrong,** inflating narrowing survival or falsely refuting P1. It would show in G5's monotonicity violations, in the polarity unit tests under `--selftest`, and in the look sample. A wrong label that changes no count on the sample stays invisible to G5; the unit tests and the look sample are the only defence there.
3. **An invalid mutant aborts a whole checker batch,** and every rule in that round looks KILLED. The pre-check names the file, and that mutant becomes INVALID. A checker failure the pre-check cannot attribute aborts the run with exit 2, and no outcome is recorded.

## Stand-ins (M4)

- **The mutants** stand in for real edits that weaken or break a rule: a regression, a careless filter, deliberate tampering. They are small, single-point and chosen by rule. Real edits can be multi-point or semantic, such as changing a value or adding a filter.
- **The environment** is an x86_64 Linux container with Python 3.13.18. CI uses `ubuntu-latest` and Python 3.11.
- **The validity pre-check** has no counterpart in SigmaHQ's CI. There, an invalid rule fails the whole batch, and other jobs reject it.

## Stopping rule, outputs and data handling

- **No early stopping.** Each full run completes all 76 rounds or aborts. No partial run is scored.
- **Outputs,** committed exactly as produced:
  - `results/pa_sigma_001/run1.txt` and `run2.txt`;
  - `results/pa_sigma_001/results.json`: per mutant, the rule id, operator, direction, site, sha256, outcome, and each test's match count and expected count;
  - `results/pa_sigma_001/look_sample.json`.
- **Nothing copied from SigmaHQ is committed:** no rule text and no event content. Mutant texts can be regenerated from `mutants.py` and the pinned commit (C-EXT).
- **DIGEST:** the sha256 of the canonical per-mutant outcome table and the gate results. It is pinned as `RECORDED` in a separate commit (W4).

## Generated inputs (C-SYNTH): what a person looks at

- **The sample.** In each cell (BROADENING, SURVIVED), (NARROWING, SURVIVED), (NARROWING, KILLED), (BROADENING, KILLED) and (any, INVALID), take the 2 mutants with the smallest sha256: at most 10 mutants.
- Their identities go into `look_sample.json`. Their diffs against ROUNDTRIP are shown to Chad Holland and are not committed.
- Until a person has looked and the look is recorded in the results, the results carry the label **person-look pending** and count toward no claim.
- The results also report the outcome distribution by operator × direction, and distinct mutants (by sha256) against repeats.

## Trigger table (M16)

| Trigger | Answer yes if … | Control | Answer (yes / no + reason) |
|---|---|---|---|
| Feasibility | the design depends on how many inputs, units or records have some property (real data, logs, corpora, model outputs) | C-FEAS | yes: the counts above, from `feasibility.py`, committed with this registration |
| Noise | any arm can give different outputs for the same input (model sampling, nondeterministic hardware, network, timing) | C-NOISE | yes: the checker is a separate binary whose output order varies. Same-input runs were measured three times before registering (counts identical), and G4 repeats the full run |
| Statistics | a claim states a rate, probability, mean or difference estimated from samples | C-STAT | no: nothing is estimated from a sample. Every fraction is an exact count over a finite, fully enumerated mutant set at one commit, not an estimate of a rate in any population, and no test statistic is computed |
| Evidence | the question is whether a rule or system handles its evidence correctly (freshness, source, provenance of inputs) | C-EVID | no: the question is how sensitive a test suite is, not how a rule handles the freshness, source or provenance of its inputs |
| Independence | a claim says independent, replicated, reproduced or externally reviewed, or counts more than one implementation as confirmation | C-INDEP | yes: self-tested. Claude designed, built and runs it; replication level is self-tested; there is no independent review, and nothing here replicates prior work |
| External | the work quotes, cites or relies on material from outside the repository (a critique, a question, a message, a dataset, another system's figures) | C-EXT | yes: SigmaHQ's rules, samples and runner (rules under the Detection Rule License 1.1), the NextronSystems checker and the SigmaHQ json_matcher binaries, pinned by commit and sha256. No outside text is quoted, and no lineage claim is made |
| Device | a claim is about behaviour on a specific device or platform, or files move between machines | C-DEVICE | yes: it runs only in an x86_64 Linux container (the checker is an x86_64 Linux binary). It makes no S25 claim and is NOT VALIDATED on the S25 |
| Verdict code | the artifact returns a verdict (a gate, guard, verifier, check or lint) | C-BUILD | yes: the harness returns KILLED, SURVIVED or INVALID, and fails closed (exit 2, no outcome) on anything it cannot attribute |
| Exploration | anything run before registration produced outputs on the registered cases, or the claim came out of exploratory search | C-EXPLORE | yes: four pre-registration moves, X1–X4 below, are logged in FORKS.md. G1 is a retrodiction. No mutant was run |
| Method comparison | the study compares methods | C-METHCOMP | no: no research methods are compared |
| People's data | the work collects, stores or publishes data about identifiable people (IP addresses, names, messages included), or handles material marked private or restricted | C-PRIVATE | no: the samples are public lab recordings in SigmaHQ's repository. Only counts, rule IDs and mutant identities are published, with no event content. The look-sample diffs hold rule text only and are not committed |
| Design | a claim goes beyond "this code, on these inputs, gives this output": a cause, a population, people's behaviour, or a field | C-DESIGN | yes: an audit carrying existence claims and exact descriptive counts; stronger claims are out of scope (see Design) |
| Held-out | the same evidence could be used both to choose something (a selection, tuning, training, a threshold, or a change to a generator or harness) and to judge the claim | C-HOLDOUT | no: nothing is chosen from the evidence judged. Operators, cap, gates and thresholds were fixed before any mutant ran; only counts and the unmutated suite had been seen |
| Generated inputs | generated or synthetic inputs (generators, mutators, scenarios, synthetic datasets) feed a result | C-SYNTH | yes: the mutants are generated. The results report the outcome distribution by operator × direction and distinct mutants against repeats, and a named sample is looked at by a person (see above) |

## Limits

- **One CI job.** The study covers the regression-test job only. A mutant counted as SURVIVED may still be caught by SigmaHQ's goodlog job, `sigma check`, or `test_rules.py`.
- **A capped census.** DROP_VALUE reaches the cap of 25 in 53 rules, and DROP_FIELD in 1; the later sites in those rules are not mutated. Per-mutant counts weight rules with long lists heavily, which P3 and the per-rule distribution counter.
- **Equivalent mutants.** A mutant equivalent to the original counts as SURVIVED. Nothing here adjusts for it.
- **One of everything.** One commit, one environment, one checker build. The checker's semantics are taken as given: this tests SigmaHQ's job as it runs, not Sigma's specification.
- **Self-tested only** (M10).

## Exploration before this registration (C-EXPLORE)

Logged in [FORKS.md](../../FORKS.md) as PA-SIGMA-001-X1 to X4:
- **X1.** SigmaHQ's own suite, unmutated, run once with the CI command: 474 of 474 passed, with one over-match warning. G1 is therefore a retrodiction.
- **X2.** One rule's condition hand-edited to name an undefined selection, to see how the checker fails: exit 1, `could not add rules from <file>`, and the whole batch aborted.
- **X3.** The checker run with an empty sample directory: a valid rule exits 0, and a hand-broken rule exits 1 and names its file. This is the basis of the pre-check.
- **X4.** The noise check above, three unmutated runs.

No registered mutant was run, and no outcome of any operator mutant has been seen.

## Provenance and credit (M13)

- **Chain:** Claude (Anthropic, Opus 5.5) designed and drafted → human validation: not performed → human editing/curation: direction by Chad Holland → human responsibility: Chad Holland. Human review level: direction only.
- **Outside material:**
  - SigmaHQ's rules, regression samples and runner are the subject of the study. The NextronSystems evtx-sigma-checker and SigmaHQ's json_matcher are its instruments.
  - Nothing here implies their endorsement or validation, and their maintainers have not been contacted.
  - SigmaHQ rules are under the Detection Rule License 1.1.

## Next unrun test (M15)

- **P5 (door, unrun):** run every BROADENING survivor through SigmaHQ's goodlog job (the evtx-baseline v0.8.5 baselines with `.github/workflows/known-FPs.csv`) and count how many that job catches. This needs the baseline archives and a registration of its own. No credence is stated yet.
- **P6 (door, unrun):** a negative-sample extension. For each rule with an exclusion, add one event the exclusion must remove, and test whether that kills the rule's NEVER_SEL BROADENING mutants.

*Vincit Omnia Veritas.*
