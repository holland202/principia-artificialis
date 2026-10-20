# PA-NS-001 Gate B closure preparation — 2026-10-20

**Gate B remains OPEN. Prepared for read-only review on Friday, October 23, 2026.**
Review target: `7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd`.
Branch: `research/pa-ns-001-protocol-v0-2`.
ChatGPT (OpenAI GPT-6), same remediation author; Chad Holland supplied direction.
No independent sign-off is recorded by this document.

## Review-source limitation

The owner requested reconciliation of Grok and Perplexity review texts. Their
original PA-NS-001 texts are not present in this conversation, the inspected branch,
or the relevant saved files located for this task. A source-location request
returned no text. This does not establish that the reviews do not exist.
Their contents, reviewed revisions, execution claims and publication permissions
cannot be reconstructed from the earlier Work summary.

The matrix below is a **provisional disposition of the public project record**,
not a claim-by-claim reconciliation of unseen external reviews. Do not attribute
these rows to Grok or Perplexity. When supplied, preserve originals unchanged,
record source revision and handling rights, and map their material findings to
these rows or add narrowly justified rows. Uncertain/private review content stays
out of this public branch.

Evidence classes: **OBSERVED** = directly inspected source/records or byte audit in
this pass; **CI-REPRODUCED** = recorded project-controlled engineering execution;
**REPORTED** = a claim lacking its underlying evidence here; **OPEN JUDGMENT** =
a question needing an actual independent review. CI uses the project's same-author
programs. It is not independent scientific reproduction. No external review finding
has independently reproduced status established in this pass.

## Concise review matrix

“Accepted limitation” below means retained in the bounded draft and disclosed;
independent reviewer and owner acceptance is still pending.

| ID / class | Finding and source at the pinned commit | Disposition | Evidence and remaining judgment |
|---|---|---|---|
| R1 REQUIRED | Grok original review unavailable. | OPEN | REPORTED: owner names a review. Need exact text, reviewed revision, scope and any execution evidence. No finding or endorsement inferred. |
| R2 REQUIRED | Perplexity original review unavailable. | OPEN | Same handling as R1. No source inspection or reproduction is credited without its record. |
| R3 REQUIRED | [evaluate_faults.py](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/evaluate_faults.py) formerly ignored the `accepted` field. | RESOLVED — engineering | CI-REPRODUCED before/after: four malformed-envelope modes falsely matched 114/114 before repair and 0/114 after; honest 114/114 unchanged. OBSERVED: current result-envelope checks and raw log provenance. Not an external sign-off. |
| R4 REQUIRED | [PREREGISTRATION_DRAFT.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/PREREGISTRATION_DRAFT.md) §3 gave profile-only R a derivative-specific precision veto. | RESOLVED — draft wording; independent judgment OPEN | Dated amendment explicitly supersedes that sentence, keeps common inputs/profile rules and removes momentum-specific vetoes from R. No study adapter is implemented or frozen. Reviewer must judge whether the proposed comparison is fair. |
| R5 REQUIRED | [GATE_B_SOURCE_MANIFEST.json](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/GATE_B_SOURCE_MANIFEST.json) and historical evidence need revision-specific interpretation. | RESOLVED — scoped consistency | OBSERVED: 24/24 SHA-256/size/Git-blob checks; six archived log segments match remote jobs verbatim; three original artifacts match historical hashes; Stage 2 evidence subtree unchanged. Historical 395-file manifest is retained, not advertised as passing against changed sources. Hashes are not scientific validity or authorship proof. |
| R6 BENEFICIAL / DOCUMENT ONLY | Calibration leaves 39/240 valid rounded profiles unresolved. [GATE_B_REMEDIATION.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/GATE_B_REMEDIATION.md) | ACCEPTED LIMITATION; precision adequacy OPEN | OBSERVED saved counts and CI-REPRODUCED audit: 201 accepted, 0 hard rejected, 39 unresolved = 2 sample-only + 14 momentum-only + 23 both. Keep all 39 as conservative operational nonacceptances. Review the finite domain and uncertainty contract; do not tune away this result. |
| R7 DOCUMENT ONLY | [ORACLE_AND_FAULTS.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/ORACLE_AND_FAULTS.md) records identifiability, overlapping boundary/profile checks and finite-grid limits. | ACCEPTED LIMITATION | OBSERVED disclosure: Couette cannot identify viscosity; Poiseuille identifies G/mu; finite samples do not specify off-grid flow or validate pressure metadata/explanations. No claim of general CFD or exact continuous-PDE validation. Independent mathematical review is OPEN. |
| R8 DOCUMENT ONLY | V accepts only when B accepts; profile-only R may be equally useful. [PREREGISTRATION_DRAFT.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/PREREGISTRATION_DRAFT.md) §§3,5,8 | ACCEPTED LIMITATION | OBSERVED draft restriction: veto nesting is not improved AI reasoning or scientific novelty; retain false rejection, coverage, cost and null results. Research target A/B and final study design belong to Gate C. |
| R9 REQUIRED | [analytic_oracle.py](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/analytic_oracle.py) is a separate program written by the same author; oracle/fault labels and precision policy lack recorded independent approval. | OPEN | Agreement, tests and CI cannot exclude shared specification error. Need the actual independent reviewer’s derivation, case/precision findings and stated review level. |

High confidence applies to the inspected code, hashes, preserved records and CI
status. Scientific adequacy and external-review coverage remain unresolved.
No additional implementation is currently justified.

## Final CI and evidence check

Both workflows on `7beb5e6` completed successfully:

- [PA-NS-001 engineering, run 39461927066](https://github.com/holland202/principia-artificialis/actions/runs/39461927066):
  Python 3.11.17, 3.12.15 and 3.13.16; 32 methods pass in normal/-O/-OO modes;
  114 construction labels; eight selected mutants; two expected-failure sabotage
  gates; 24-file manifest checks. These are existing executed CI records read now.
- [Repository-wide verify-all-notes, run 39461926988](https://github.com/holland202/principia-artificialis/actions/runs/39461926988):
  completed success at 2026-10-20T17:01:26Z. The final number-audit report uses
  `|| true`; green CI does not establish correctness of every numerical claim.

This pass reran no Python tests. Local execution was unavailable. It recomputed
UTF-8 byte lengths, SHA-256 and Git blob SHA-1 through a separate transient
JavaScript audit, checked against standard empty/abc vectors. That is a second
implementation of byte checking by the same author, not independent science.
Current CI separately verified MD5 too.

The six retained pre/post-repair step segments are contiguous verbatim parts of
their indexed GitHub job logs. Setup/cleanup is omitted as originally disclosed.
The complete original Stage 2 evidence subtree retains Git object
`11cf9e409115048b53163679cad752f3c6cbf910`.
The numerical checker retains SHA-256
`4aaf992c2df62abb225b92607f65ddf4808d57afd5a313c1799743581c822518`.
The original manifest retains SHA-256
`fa0f608f15fb26fb7b94ccf47008c567c040953435811a0c6708c0a0126cdc8a`.
The source commit is unsigned; the audit establishes consistency through authenticated
GitHub retrieval and pinned Git objects, not a cryptographic author attestation.

Machine-readable observations: [closure-2026-10-20.json](evidence/gate_b/closure-2026-10-20.json).
Read-only review brief: [CLAUDE_GATE_B_REVIEW_2026-10-23.md](CLAUDE_GATE_B_REVIEW_2026-10-23.md).

## Minimum remaining blockers and scope

1. Obtain both original review texts and reconcile every material finding against
   the pinned remediation. Record execution claims as reported until supported.
2. Obtain actual independent judgment on the ODE/oracle/fault labels, precision
   domain/39 nonacceptances, bounded claim and corrected profile-only rival.
   Any material counterexample receives only the smallest demonstrated correction.
3. Record Chad Holland’s Gate B disposition after reviewing those records.
   No one’s approval is inferred by this preparation.

REQUIRED in this pass: finish pending CI/evidence accounting and disclose the
missing review sources. BENEFICIAL: this pinned matrix and Claude brief reduce
review ambiguity without adding software. DOCUMENT ONLY: stated numerical,
observability and independence limitations. DEFER: solvers, extra flow families,
frameworks, study adapters, main AI evaluation, final Gate C choices and findings release.

Only new closure documents/evidence records are prepared. Original sources,
thresholds, fixture labels, calibration results, historical records and contributor
material remain untouched. The source/evidence manifest's 24-file scope does not
expand to include this review package; its new files are bound by the containing
Git commit. No private repository or private-derived material is an input.
No reviewer has been contacted and no review or future run has been scheduled.
