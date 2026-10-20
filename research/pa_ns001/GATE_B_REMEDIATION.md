# PA-NS-001 Gate B remediation — 2026-10-20

Status: required corrections implemented and freshly CI-validated; Gate B independent review remains open.
This is same-author engineering work, not independent scientific review.
Base a7cc5b2f02044b7b6d148ad805de0afc123f1aa9; scope plan
68f460cc32a6f25cd50bbd268100e42292fb0aef. The numerical checker, thresholds,
calibration matrix, 114 fixture labels and original evidence are unchanged.

## Dispositions

| ID / class | Evidence and disposition |
|---|---|
| B1 REQUIRED | Pre-repair CI 0333ad6ed9a9d2fd72af59bbc61003d1134d1edb falsely matched all 114 cases for each of four malformed result envelopes: flipped, missing, integer 1 and integer 0 accepted fields. The evaluator now requires a real bool consistent with the construction label/status. Regression assertions cover all four in the existing gate-control test. |
| B2 REQUIRED | The old draft gave R a momentum-specific resolution penalty despite taking no derivatives. An appended draft amendment shares data, scale and profile rules while removing derivative-specific vetoes from R. No study arm is implemented or criterion frozen. |
| B3 REQUIRED | Original MANIFEST.json remains tied to its historical checkpoint. GATE_B_SOURCE_MANIFEST.json identifies 24 current source/pin/draft/pre-repair evidence files using hashes measured in all three CI jobs. Its limited scope is explicit; it is not a complete inventory or authenticity proof. |
| B4 BENEFICIAL | Audit the original 240-row artifact, not new cases. All 39 unresolved rows are explained: 2 sample-only, 14 momentum-only, 23 both. The case IDs are in timestamped CI reports. No thresholds were tuned and no unresolved result became accepted. |
| B5/B6 DOCUMENT ONLY | Finite calibration does not prove a universal rounding bound or exact PDE validity. Couette viscosity and joint G/mu changes can be unidentifiable; the boundary check overlaps profile checking; adding a veto guarantees nesting, not better AI reasoning. Existing limits and negative results remain. |
| B7 DOCUMENT ONLY | No original external Gate B review text was available in the inspected public branch/issues. No review findings, endorsement, consent or authorship are invented. Preserve supplied original reviews and add claim-by-claim dispositions when their provenance/publication status is established. |
| B8/B9 DEFER | No general CFD, new flow families, frameworks, benchmark expansion, AI/prompt adapter, main study, reserved cases, main merge or findings release. |

## Reproduction and evidence

The pre-repair check ran on Python 3.11.17, 3.12.15 and 3.13.16 in the existing
branch-scoped GitHub engineering CI:
[run 39460470381](https://github.com/holland202/principia-artificialis/actions/runs/39460470381).
The expected diagnostic step exited 1 on all three jobs; honest fixture results
and the original outcome digest still matched. Timestamped command/output lines
are kept verbatim in evidence/gate_b/pre_repair/, with an index of source commits,
job IDs, executed Python versions and exit codes. Setup/cleanup text is omitted
and is not represented as retained raw step output.

The old artifact SHA-256 is
b1a80952aa41e38300055c386cb4505a4e122254632b2e19e6ec4450f7a2c1bb.
The independent cap counts are 25 sample-cap and 37 momentum-cap exceedances,
overlapping in 23 rows; their union remains 39. The unchanged 201 accepted,
0 hard rejected and 39 unresolved counts describe the fixed calibration matrix,
not AI accuracy. All 39 remain conservative operational nonacceptances.

Local execution was unavailable in this turn. Runs described here are actual
GitHub CI executions, not local runs or independent authorship. The repair retains
32 unittest methods and adds assertions for four result-envelope controls; a test
method count is not a count of checks. The focused Gate B script has a status-only
matcher sabotage that must fail, including under optimized Python.

## Minimum work to close Gate B

1. Complete fresh post-repair engineering CI and the scoped source/evidence audit.
2. Obtain the original external review records with source revision, reviewer
   identity/scope and permitted publication/handling; preserve them unchanged.
3. A qualified independent reviewer resolves the analytic/oracle/fault-label and
   precision-contract questions, including the 39 unresolved cases and fair rival.
   Record each material finding's evidence and disposition. Another execution of
   the same-author programs cannot substitute for that review.
4. Record owner acceptance of the bounded Gate B disposition. Gate B is not
   closed by this self-review.

Choosing/funding the AI model, final sample size, prompts, held-out task generator,
and frozen preregistration belongs to Gate C. Those decisions are not turned into
new Gate B implementation tasks.

Provenance: ChatGPT (OpenAI GPT-6), owner direction only. Implementation inputs are
the pinned public PA source and new synthetic result-envelope controls. No private
repository, private-derived code, confidential review text, contributor snapshot,
new dependency or external contact is used. CI logs contain this public code's
outputs on GitHub-hosted runners. New artifacts get a source/provenance review,
not a claim of independent certification.

## Post-repair validation — 2026-10-20

The earlier pending status in repair commit
6a3c40a267a9fb495d1542009b8f0f7ff59d47b6 is superseded by this dated record.
Actual [engineering CI run 39461263112](https://github.com/holland202/principia-artificialis/actions/runs/39461263112)
passed Python 3.11.17, 3.12.15 and 3.13.16.

- All four malformed-envelope controls now match 0/114, rather than 114/114.
- Honest results still match 114/114 and retain the original outcome digest
  e0c09b0409f96adaf02a827cd34711b58bb7e64fef0e0def76b109bff2e35aa5.
- All 32 unit methods pass in normal, -O and -OO modes in each Python job,
  including the new malformed-envelope assertions.
- The eight selected source mutants cause real assertion failures after a passing
  unmutated baseline; no child errors and no source changes occurred during each run.
- Both the existing whole-gate sabotage and the new status-only evaluator sabotage
  exit exactly 1. The latter was also run with optimized Python.
- Three repetitions of the original calibration still reproduce its recorded
  digest and 201 accepted / 39 unresolved outcome. No case was tuned or relabelled.
- Every inventoried source/evidence hash agrees across all three CI Python jobs.

Timestamped executed step output, raw unit logs and mutant summaries are kept in
evidence/gate_b/post_repair/, with exact source revisions, interpreter versions,
commands, job IDs and exit statuses. The pre-repair failed steps remain unchanged.
GATE_B_SOURCE_MANIFEST.json is a **24-file source/evidence snapshot**, covering
top-level Python modules, the original outcome pin, scope/preregistration drafts
and pre-repair CI records. It excludes the final report, workflow and post-run
records to avoid recursive hashes; those remain tied to the Git commit. The old
MANIFEST.json is still the original checkpoint's historical full inventory and
is not advertised as passing against changed current sources.

The numerical verifier ns001.py is byte-identical to the Stage 2 source (MD5
55480877c0f0408dfd666555393ab2d4). The 114 construction labels, calibration matrix,
thresholds and original RECORDED.json remain unchanged.

A finite sample array does not determine a continuous velocity field between grid
points. Nor does this checker validate a model's pressure metadata or explanation.
This is DOCUMENT ONLY: restrict the claim to the declared reference-profile object;
do not respond by adding a general CFD/PDE solver.

**Minimal remaining Gate B work:** preserve the original external review texts
when available, assign their evidence-linked dispositions, obtain independent
approval of the bounded oracle/fault/precision contract and corrected rival design,
and record the owner's Gate B disposition. No additional feature implementation
is currently justified. Gate C model/budget/study choices remain a separate gate.
