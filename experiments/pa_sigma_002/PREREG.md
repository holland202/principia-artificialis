# PA-SIGMA-002: does SigmaHQ's goodlog job catch the weakened rules its regression tests cannot?

**State:** REGISTERED, NOT RUN. No mutant has been staged or run against any baseline. This registration is committed
with its feasibility counts and the unmutated-job check (G1) before the harness is committed.
**Authors:** Direction: Chad Holland (2026-10-29; choice of path delegated). Design, feasibility script and this text:
Claude (Anthropic, Opus 5.5). Human review level: direction only. Everything run under this registration is
**self-tested** (M10).
**Method:** [METHOD.md](../../METHOD.md) (md5 `50e8a91a448251f8fc5d70f6971b74ae`), [WORKFLOW.md](../../WORKFLOW.md)
(md5 `8ab6970501f53cb288d35f19787be529`) and [CONTROLS.md](../../CONTROLS.md) (md5 `2a68368e99f87430bd15e8074811452c`),
as on `main` at `3cb359c`.
**Subject:** [SigmaHQ/sigma](https://github.com/SigmaHQ/sigma) at `05d1031f537e830b76da53bae2400c5814c89165`: its
goodlog workflow `.github/workflows/goodlog-tests.yml`, `matchgrep.sh` (sha256 `23412b02…f373`) and `known-FPs.csv`
(sha256 `10bfaf96…bbce4`).
**Parent:** [PA-SIGMA-001](../pa_sigma_001/PREREG.md), whose registered door P5 this is. PA-SIGMA-001 found that
none of the 1,502 BROADENING mutants (edits that let a rule match more) fails SigmaHQ's regression-test job.

## W1: question

**The question (observable):** of PA-SIGMA-001's 1,502 BROADENING mutants, how many would make SigmaHQ's goodlog job
fail if each replaced its original rule?

**What the code can express.** Read before registering (VERIFIED FROM SOURCE):
- The goodlog workflow has seven jobs, one per evtx-baseline v0.8.5 archive (Windows 7, 10, 11, 11-2023, Server
  2022, 2022 domain controller, 2022 Azure). Each runs `evtx-sigma-checker --log-source tests/thor.yml --evtx-path
  <baseline>/ --rule-path rules/windows/ --rule-path rules-emerging-threats/ --rule-path rules-threat-hunting/ >
  findings.json`, then `matchgrep.sh findings.json known-FPs.csv`.
- `matchgrep.sh` drops every finding of a rule whose level is `low`. It drops each finding matching a
  `known-FPs.csv` row: `"RuleId":"<id>".*<pattern>`, case-insensitive. It exits 3 when findings remain (the job
  fails) and 0 otherwise.
- An empty findings file passes (`No matches found.`, exit 0). A checker that silently produced nothing would look
  like a clean pass.

So a broadening mutant can only fail this job by matching a baseline event, at a level other than `low`, that no
known-FP row for its rule filters out.

## Design (C-DESIGN)

- **Design:** audit. A deterministic run of a fixed, fully enumerated mutant set against fixed baselines, at one
  commit.
- **Strongest claims it can carry:** existence ("this edit to this rule passes both the regression-test and the
  goodlog jobs") and exact counts over this set.
- **Out of scope:** SigmaHQ's other jobs (`sigma check`, `test_rules.py`, `test_logsource.py`), review by
  maintainers, rules without regression tests, and how often real rule changes are weakening.

## Instrument

**Real code (M4).** The checker binary, `tests/thor.yml`, the baselines and `matchgrep.sh` are SigmaHQ's own, run
with the workflow's arguments. The mutants are rebuilt with PA-SIGMA-001's `mutants.py` (md5
`97b57d4f5fd5ebbbf4ff9a1b93bbcd0f`), and the set must equal PA-SIGMA-001's.

**Two deviations from the workflow, both needed to run 1,502 mutants at once:**
1. Every mutant is staged as its own rule file under a fourth `--rule-path`, with a fresh id, so the checker cannot
   confuse it with its original. The workflow's three rule paths are loaded unchanged.
2. Each staged finding gets its original rule id back (one exact substring replacement, aborting unless it occurs
   exactly once). The findings then go through the real `matchgrep.sh`, so known-FP rows keyed on the original id
   apply as in CI. A finding's staged file name (in `RulePath`, which precedes `RuleId` in each line, so no known-FP
   pattern can reach it) attributes it to its mutant.

A mutant is **CAUGHT** when `matchgrep.sh` leaves at least one of its findings on at least one baseline. Since the
unmutated job passes on every baseline (G1), a CAUGHT mutant is one whose replacement of its original would fail
SigmaHQ's goodlog workflow.

**Tools:** evtx-sigma-checker v0.8.5 (sha256 `d672e07a516f3f72eaae8244f99fa2c5b133885a4401eb05a272903857d767e2`),
`tests/thor.yml` (sha256 `8e72d922…4120`). The evtx-baseline v0.8.5 archives (sha256 of each archive as
downloaded on 2026-10-29) are:

| Baseline directory | Archive | sha256 |
|---|---|---|
| `win7-x86` | win7-x86.tgz | `e755f3cd48f8a3dc8877c46622339cd44fa0929981fcfd79ada63c2bafb62b9f` |
| `Logs_Client` | win10-client.tgz | `d48f1b328d48db6c6dfaa9b6e232dbb454d93e833c6e1248efc0faf690b6808e` |
| `Logs_Win11` | win11-client.tgz | `6caab8391ac3cf7135e2fd5f545c7b116a2b445ec061f83d05873f8081ff0202` |
| `Logs_Win11_2023` | win11-client-2023.tgz | `739079e63fc8a81d0b20eff6ee76b2f104a0cf6df115802c9bca128417c1e117` |
| `win2022-evtx` | win2022-evtx.tgz | `29406757f9761b56372d40550c9bef4eb2bf82ec21ba15115910742b03c4aab2` |
| `Win2022-AD` | win2022-ad.tgz | `dde89557c8dd19756d1fb4797f566aaa94509847c2740968bf04b5bea0b34ec1` |
| `win2022-0-20348-azure` | win2022-0-20348-azure.tgz | `4b3337d857f8e03273f831ad25db75e02a5a8b26b5ec14bb63727459250a5a73` |

## Feasibility counts (C-FEAS)

From [`feasibility.py`](feasibility.py) (no mutant run), output [`feasibility_output.txt`](feasibility_output.txt):

```
0. broadening mutants rebuilt 1502; PA-SIGMA-001 recorded 1502; identical sets: True
1. broadening mutants by what limits the goodlog job (bucket x operator):
   out_of_scope  total     0 in   0 rules | {'DROP_VALUE': 0, 'DROP_FIELD': 0, 'NEVER_SEL': 0}
   level_low     total    32 in   3 rules | {'DROP_VALUE': 14, 'DROP_FIELD': 15, 'NEVER_SEL': 3}
   known_fp_all  total     8 in   3 rules | {'DROP_VALUE': 0, 'DROP_FIELD': 6, 'NEVER_SEL': 2}
   catchable     total  1462 in 276 rules | {'DROP_VALUE': 855, 'DROP_FIELD': 298, 'NEVER_SEL': 309}
2. catchable mutants whose rule has a known-FP row with a narrower pattern: 41 mutants in 6 rules
3. catchable mutants by logsource product: {'windows': 1462}
4. identity of the broadening set (sha256 of sorted rule:k:sha lines): 4bb6343d864618f43b895e98a711c7599f29e895173adaec5ef7621d5d596ba0
```

So 40 of the 1,502 cannot be caught by construction (32 in `low`-level rules, 8 in rules whose known-FP row is
`.*`), and the predictions below are over the other **1,462**, in 276 rules.

**G1, the unmutated job, run before registering** ([`g1_unmutated_output.txt`](g1_unmutated_output.txt)): the
workflow's command on each baseline with the unmodified rules, then `matchgrep.sh`.

```
win7-x86 checker_exit=0 11s raw_findings=252 matchgrep_exit=0 No matches found.
Logs_Client checker_exit=0 53s raw_findings=4146 matchgrep_exit=0 No matches found.
Logs_Win11 checker_exit=0 93s raw_findings=5911 matchgrep_exit=0 No matches found.
Logs_Win11_2023 checker_exit=0 107s raw_findings=8194 matchgrep_exit=0 No matches found.
win2022-evtx checker_exit=0 17s raw_findings=731 matchgrep_exit=0 No matches found.
Win2022-AD checker_exit=0 30s raw_findings=2823 matchgrep_exit=0 No matches found.
win2022-0-20348-azure checker_exit=0 96s raw_findings=7575 matchgrep_exit=0 No matches found.
```

## Gates (instrument checks, not predictions)

Any gate failing → exit 2, no verdict.

- **G1:** on every baseline, the unmutated rules' findings from the staged run pass `matchgrep.sh` (exit 0, `No
  matches found.`).
- **G1b:** on every baseline, the unmutated rules give the same number of raw findings in the staged run as in the
  G1 run above. This catches a checker that silently produced nothing, which G1 alone would pass.
- **G2:** the rebuilt broadening set has the identity `4bb6343d…96ba0`.
- **G3:** IDENTITY controls (each of the 276 rules staged unchanged, with a fresh id): **0 CAUGHT**. Since the
  originals pass, a CAUGHT identity control would mean the id restoration or the known-FP filtering is broken.
- **G4:** MATCH_ALL controls (10 process-creation rules, level not `low`, no known-FP row, with detection replaced
  by `Image|contains: '\'`): **at least 9 of 10 CAUGHT**. This shows the instrument can say CAUGHT.
- **G5:** NEVER_FIRE controls (PA-SIGMA-001's, one per rule): **0 raw findings**.
- **G6:** the harness run twice gives the same DIGEST.

## Predictions (registered before observing; M1, M2)

| ID | Prediction | Credence | Precisely wrong if |
|---|---|---|---|
| P1 | The goodlog job leaves most weakened rules unseen: **fewer than 50%** of the 1,462 catchable mutants are CAUGHT | 0.8 | 50% or more are CAUGHT |
| P2 | It is not blind either: **at least 5%** are CAUGHT | 0.75 | fewer than 5% |
| P3 | Switching a whole exclusion off (NEVER_SEL, broadening) is CAUGHT at a **higher** rate than dropping one excluded or OR-ed value (DROP_VALUE, broadening) | 0.8 | NEVER_SEL's rate ≤ DROP_VALUE's |
| P4 | **At least half** of the 276 rules keep a broadening mutant that passes both jobs | 0.85 | fewer than 138 rules do |

**Why these numbers.** Exclusions exist to keep benign events from firing, and the goodlog baselines are one place
such events turn up. So switching a whole exclusion off (NEVER_SEL) should re-surface baseline events more often
than dropping one value of a list, which needs that particular value's events to be in the baselines. This is a
reason for the prediction, not a fact checked here. The 50% and 5% bounds are wide on purpose: no earlier
measurement exists, and this study's first job is to say which side of each the job falls on.

## Simplest rival (M14), as arms

- **"The goodlog job covers what the regression tests miss."** This is P1's failure case, measured directly.
- **"Any broadening is equally visible, whatever the edit."** This is P3's failure case.
- **"The instrument can only say PASSED."** The MATCH_ALL controls (G4) answer it.

## Pre-mortem (W2)

1. **Staged rules never load** (wrong path, YAML rejected). Every mutant would read as uncaught, flattering P1. G4
   would fail.
2. **Id restoration breaks known-FP filtering.** Mutants would be CAUGHT on findings CI filters out, flattering P2.
   G3 would fail.
3. **The checker silently produces nothing on a baseline** (seen once while preparing: a missing `/usr/bin/time`
   meant the checker never ran, and `matchgrep.sh` still printed `No matches found.`). G1b would fail.

## Stand-ins (M4)

None for the rules, baselines, checker or filter: they are SigmaHQ's own. The stand-ins are the two deviations
above: the extra rule path and the id restoration. G3 tests them.

## Stopping rule, outputs, data handling (C-PRIVATE)

- One full run, then a second for G6; no run is discarded.
- The harness writes counts and mutant identities to `results/pa_sigma_002/`.
- Raw findings stay out of the repository. They hold event text from public lab baselines.

## Generated inputs (C-SYNTH)

The mutants are generated, as in PA-SIGMA-001. The results report CAUGHT counts by operator and by baseline, and
name five CAUGHT and five uncaught mutants for a person to look at. That look is Chad's, and it is recorded as
pending until he does it.

## Trigger table (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | yes: the counts above and the G1 run, committed with this registration |
| Noise | C-NOISE | yes: the checker is one binary run per baseline. The G1 runs were single runs; G1b compares the staged run's raw counts with them, and G6 repeats the whole run |
| Statistics | C-STAT | no: exact counts over an enumerated set; no sample is generalised from |
| Evidence | C-EVID | no: the question is CI sensitivity, not how a rule treats its evidence |
| Independence | C-INDEP | yes: self-tested. Claude designed, built and runs it |
| External | C-EXT | yes: SigmaHQ's rules, workflow, filter and known-FP list (Detection Rule License 1.1), and NextronSystems' checker and evtx-baseline archives, pinned by sha256. No outside text is quoted |
| Device | C-DEVICE | yes: x86_64 container only. NOT VALIDATED on the S25 |
| Verdict code | C-BUILD | yes: the harness returns CAUGHT / not caught and fails closed (exit 2) on any gate or pin failure |
| Exploration | C-EXPLORE | yes: see below |
| Method comparison | C-METHCOMP | no |
| People's data | C-PRIVATE | the baselines are lab machines' logs published by NextronSystems; no event text is published, only counts and rule or mutant identities |
| Design | C-DESIGN | yes: audit; existence and exact counts only |
| Held-out | C-HOLDOUT | no: nothing is chosen from the evidence judged. The 5% and 50% bounds and the control choices are fixed here |
| Generated inputs | C-SYNTH | yes: see Generated inputs |

## Limits

- **Two of SigmaHQ's jobs, not all of them.** A mutant passing both may still be caught by `sigma check`,
  `test_rules.py` or a reviewer.
- **One commit, one checker build, one set of baselines.**
- **PA-SIGMA-001's mutant set,** with its cap of 25 per operator per rule. Equivalent mutants count as uncaught.
- **Self-tested only** (M10).

## Exploration before this registration (C-EXPLORE)

Logged in [FORKS.md](../../FORKS.md) as PA-SIGMA-002-X1 and X2.

- Read the goodlog workflow, `matchgrep.sh` and `known-FPs.csv`.
- Downloaded and extracted the seven baselines.
- Ran the unmutated job on all seven (G1, above).
- Looked at the format of the findings lines and the known-FP patterns.
- Wrote a harness draft (md5 `322b81d5b7fb0325fec71f29a0f14d4c`), kept outside the repository and not run.

No mutant or control was staged or run.

## Provenance and credit (M13)

AI participation: Claude (Anthropic, Opus 5.5) designed this and wrote the scripts and text on 2026-10-29, at Chad
Holland's direction → human validation: direction only → human editing/curation: none → responsibility: Chad
Holland. SigmaHQ's rules, workflow and filter are SigmaHQ's; the checker and baselines are NextronSystems'.

## Next unrun test (M15)

- **P5:** run `sigma check` and `test_rules.py` on the mutants that pass both jobs, and count what remains invisible
  to all of SigmaHQ's automated checks.
- **P6:** PA-SIGMA-001's P6, negative samples. Not run.
