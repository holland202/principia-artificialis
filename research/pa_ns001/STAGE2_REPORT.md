# PA-NS-001 Stage 2 engineering report — 2026-10-20

**Software validation only. AI study NOT RUN. Independent review pending.**

Failures and limits lead this report. The original three tests missed acceptance of
an incorrect zero profile with infinite tolerance, acceptance of stopped tiny flow,
and finite-difference spacing underflow. The repair is a bounded analytic checker,
not general CFD validation. Its fixed calibration leaves 39/240 correctly rounded
profiles unresolved (16.25% operational nonacceptance); do not call that zero false
rejection. The first mutation run is invalidated and a later full-gate failure is
retained. No independent reviewer has checked the specification or fault labels.

## Source and order of work
Repository: public `holland202/principia-artificialis`, ID 1302030647.
Branch: `research/pa-ns-001-protocol-v0-2` only.
Initial prototype `8a3194f56f400a306778f7a837b51216c3b71220` compared against
main `ae0afc07f8fae8b5f63657ed01b5fae988c777d6` (four added prototype files).
No open PR was returned for this development branch during the check.
Calibration plan recorded before measurements at
`4bdaa6535984716fa4816ad5d50c2c55a60e169f`. No held-out outcomes were used for thresholds.

Order: inspect/reproduce original tests; diagnose numerical and input failures;
fix calibration matrix/policy in a separate commit; implement and repeat analytic
calibration; derive identifiability/fault labels; generate deterministic fixtures;
test failure detection; prepare the draft preregistration and evidence package.
Environment: isolated public PA worktree and clean no-package Python 3.12.14 venv,
Linux container. There were no AI requests, model downloads, private inputs or costs.
Authorship/review details: [PROVENANCE.md](PROVENANCE.md).

## Observations and bounded repairs
| Observation in executed original code | Repair and practical meaning | Evidence / confidence |
|---|---|---|
| Infinite tolerance accepts all-zero Couette with U=1 | finite bounded configuration validation before reading candidate data | diagnostics/stdout.txt; directly reproduced |
| All-zero Couette with U=1e-12 is accepted because scale is floored at 1 | normalize by signed characteristic velocity; reject stopped nonzero flow across tested scales | diagnostics and test_dimensional_scale_changes_do_not_hide_stopped_flow; directly reproduced |
| h=1e-200 causes dy-squared underflow and ZeroDivisionError | exact rational dimensionless differences avoid physical spacing squaring | diagnostics; repaired regression passes |
| Unknown family plus NaN data bypasses configuration validation; strings raise incidental TypeError | validate configuration eagerly; malformed candidate data is explicit nonacceptance; bool excluded | original diagnostics plus invalid-input tests |
| Rounded valid profiles fail a fixed 1e-9 residual check | fixed declared rounding budget, derived 4*e*(N-1)^2 amplification bound and resolution caps | all calibration cases retained; finite-matrix evidence only |
| Some parameter changes cannot alter this observable | separate polynomial oracle marks 22 indistinguishable controls valid | fault manifest/construction facts; mathematics still needs independent review |
| Boundary veto duplicates a subset of profile veto | retain boundary diagnostics but do not count it as an independent third scientific test | same threshold and max over all profile samples; mathematical implication |

New numerical parameters remain proposed engineering settings. The finite matrix
does not prove universal stability or physically meaningful scientific cutoffs.
Rational arithmetic exactly checks supplied values, not whether physical assumptions,
coordinates, measurements, provenance or an AI's explanation are true.

## Executed evidence
All directories below are relative to `evidence/stage2/`. RUN.json stores exact
argv, start/end times, Python/platform, source hashes, exit code and stdout/stderr hashes.
A base commit plus source hashes identify uncommitted code exactly as run.

| Check | Observed result | Raw evidence |
|---|---|---|
| Original unchanged tests | 3 methods, exit 0 | baseline/RUN.json, tests.stderr |
| Fixed analytic calibration, three runs | each 240 cases; 201 accepted, 0 hard rejected, 39 UNRESOLVABLE; all 60 unrounded accepted | calibration-run1/2/3 and calibration-data1/2/3 |
| Calibration reproducibility | same canonical digest all three runs | `73258fb30a5b2743c775c895a1d535782105affa5779a46851b6385022d27ce9` |
| Constructed faults and valid controls | 114/114 labels matched: 76 rejected, 38 accepted, including 22 indistinguishable controls | fault-run1/, fault-data1/manifest.jsonl, outcomes.jsonl |
| Fixture reproducibility identity | manifest SHA-256 `27efb1366b885da80ada136afaf770997f6f41b629b06ee3b441048f9f832f44` | fault-data1/summary.json |
| Latest complete local gate | 32 tests in each of normal/-O/-OO, three matching calibrations, 114 fixtures; exit 0 | full-gate-run2/, full-gate-data2/ |
| Selected source mutations in latest gate | 8/8 produce test assertion failures after passing unmutated baseline; no child test errors; source hashes unchanged | full-gate-data2/mutants/summary.json and child logs |
| Always-accept / always-reject fixture controls | respectively only 38/114 and 76/114 labels match; both exit exactly 1 | fault-always-accept/, fault-always-reject/ |
| Canonical method checks | lint 0 violations; selftest and 232-item coverage exit 0; duplicate sabotage exit exactly 1 | method-lint/, method-selftest/, method-coverage/, method-sabotage/ |
| Existing surrounding regressions | 8 numerical-audit tests and 46 synthetic experiment tests pass; number-audit planted control passes | number-audit-tests/, number-audit-control/, experiment-regressions/ |
| Main-study feasibility | 0 main cases generated, 0 AI requests; model/token/cost feasibility not established | counts-only/ |
| Prospective sample-size arithmetic | closed-form and NIST-root tests pass; output is planning arithmetic, not AI data | planning-arithmetic/, test_study_design.py |

Calibration by representation: binary64 60/60 accepted; normalized ten-decimal
60/60 accepted; physical ten-decimal 50/60 accepted and 10 unresolved; physical
six-decimal 31/60 accepted and 29 unresolved. Original illustrative checker accepted
183/240 overall and 59/60 unrounded. These totals use different numerical contracts;
they are not a scientific superiority comparison or estimates of AI accuracy.
Per-grid min/median/nearest-rank 95th percentile/max residuals are in each calibration
summary; every profile result is retained. Linear/quadratic exact samples have no
central-difference truncation error; the observed artifacts concern rounding and
coordinate/representation assumptions, not generic CFD convergence.

## Failures, corrections and deviations retained
1. `mutations-run1/` overlapped with a test-file update: children ran 23 then 27 tests
   and some saw an unrelated overly strict test of NIST's approximate printed root.
   That run is invalidated, not credited. See MUTATION_RUN1_INVALIDATED.md. The fresh
   runner requires a passing baseline and unchanged before/after Python source hashes.
2. The NIST example's approximate upper bound differs by about 9e-7 from numerical
   CDF inversion. The corrected test checks both the published approximation and its
   defining binomial equations. Raw failures remain in the first mutation logs.
3. An added extreme-finite rounding-budget regression required nullable reported
   metrics when a ratio exceeds binary64 range; the decision remains UNRESOLVABLE.
   `full-gate-run1/` then refused to credit the precision-disabled mutant because
   disabling that guard caused both an assertion failure and a reporting overflow.
   The same finite-metric formatter is now used on both report paths. No tolerance,
   calibration matrix, fault label or acceptance rule changed. The complete fresh
   `full-gate-run2/` passes the strict no-child-error mutation criterion.
4. This is pre-study engineering exploration, not a frozen scientific registration.
   Its append-only entry is in root FORKS.md; all observed cases are excluded from
   any future confirmatory study. No historical PA results/registrations were edited.

## Preregistration and review readiness
[PREREGISTRATION_DRAFT.md](PREREGISTRATION_DRAFT.md) specifies the proposed unit,
paired baseline/full/profile-only arms, costs, model/prompt controls, primary FAR,
conservative FRR, exact intervals, meaningful-effect proposal and sample-size logic.
It explicitly distinguishes AI profile generation from review of constructed profiles.
The original question cannot be answered by silently substituting the latter.

Nested acceptance means V cannot increase false acceptance relative to B on the same
data by construction. The relevant open questions are useful effect size, cost,
false rejection, advantage over the simplest profile check, and generalization. The
draft proposes 800 main units only for owner review; it authorizes none. Model,
task/domain distribution, held-out construction, budget, independent reviewer,
method-control applicability and final precision contract remain unresolved.

| Gate | Current disposition |
|---|---|
| A: software/calibration | Local evidence complete within stated scope; pushed-commit cold-clone result recorded separately in POST_COMMIT_VERIFICATION.md when available |
| B: independent oracle/fault review | Package ready to review; review NOT performed |
| C: frozen preregistration + execution approval | NOT satisfied; draft only, decisions in OWNER_DECISIONS.md |
| D: independent evidence review + findings release | NOT satisfied; no scientific findings release or main merge authorized |

Software validity: tested bounded implementation. Mathematical status: analytic
derivations/identities inspected by the same AI, independent review pending.
Empirical AI/physical validity: **NOT RUN**. Highest current review level: same-author
self-testing/re-runs, not independent replication. Do not label the inquiry DONE or
the scientific hypothesis supported because engineering tests pass.

Next bounded action: independent Gate B review of the ODE, fault labels, rounding
policy and the proposed research target. No new official experiment is the next step.
