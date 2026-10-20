# PA-NS-001 Gate B remediation scope — 2026-10-20

Status: bounded engineering plan before new Python reproduction. Not a scientific
registration, study approval, independent review, or findings release.
Base: a7cc5b2f02044b7b6d148ad805de0afc123f1aa9.
Branch: research/pa-ns-001-protocol-v0-2 only.
ChatGPT (OpenAI GPT-6), Chad Holland's direction; human review: direction only.

## Change classification and stopping rule

| ID | Class | Source / observation | Minimal disposition |
|---|---|---|---|
| B1 | REQUIRED | evaluate_faults.py:evaluate compares only result['status'] with the expected label. It never validates the accepted Boolean. A status-preserving Boolean flip is therefore statically invisible. | Reproduce using wrappers around the real verifier, then require an explicit bool consistent with the status and construction label. Add focused negative controls. Do not change the numerical checker. |
| B2 | REQUIRED | PREREGISTRATION_DRAFT.md section 3 requires the profile-only rival to inherit identical precision limits, while ns001.py's momentum allowance includes (N-1)^2. | Append a draft clarification: identical data, scales, profile tolerance and shared input rules; no derivative-specific resolution cap in a method that takes no derivatives. Do not implement study arms or freeze criteria. |
| B3 | REQUIRED | MANIFEST.json authenticates listed bytes of the old checkpoint; editing the evaluator/tests makes its current-checkout hashes stale. | Keep that historical manifest unchanged. Add a small, explicitly scoped Gate B source/evidence manifest and retain actual CI commands/output and source hashes. A list-only manifest is not proof of package completeness or authenticity. |
| B4 | BENEFICIAL | The 39 unresolved rows are listed, but their two active precision caps are not separated. The distinction directly informs B2 and reviewer decisions. | Report sample-only, momentum-only and overlapping causes from the existing 240-row artifact, including IDs. No new parameter search, threshold tuning or reclassification as accepted. |
| B5 | DOCUMENT ONLY | The 16-epsilon allowance and engineering caps have finite-matrix support, not a universal bound. Acceptance has a tolerance; it is not exact PDE validity. | Retain these limits; require independent review of the declared domain/precision contract. |
| B6 | DOCUMENT ONLY | Couette cannot identify viscosity; Poiseuille identifies G/mu; boundary checking overlaps profile checking; V is nested within B. | Preserve existing statements and negative results. Do not claim three independent checks, novel mathematics, or improved AI reasoning. |
| B7 | DOCUMENT ONLY | No external Gate B review text was found in the inspected branch or matching public issues/PRs. | Do not invent findings, endorsements or attribution. Record original review text, provenance and dispositions when supplied and cleared for this public repository. Missing review material remains a closure dependency. |
| B8 | DEFER | General CFD solvers, additional flow families, model/prompt pipelines, extra frameworks, benchmark expansion and automatic review platforms. | No implementation: unnecessary for the demonstrated defect or this review gate. |
| B9 | DEFER | Main AI study, held-out/reserved cases, final sample size/model/cost choices, main merge and scientific release. | Separate Gate C/D decisions; none executed here. |

No private repository is accessed and no owner-only Library record is a public
source. Inputs to implementation are the public files at the pinned base plus
newly authored engineering controls. No dependency, numerical tolerance, analytic
solution, construction label, calibration matrix or historical evidence is changed.

## Prospective engineering checks

P1: before repair, status-preserving flipped/missing/non-Boolean acceptance fields
are wrongly counted as matches by the original evaluator. After repair, all those
contradictory/malformed records must fail matching. These wrappers do not invent
fault labels: they alter the real verifier's result envelope.

P2: honest results still match all 114 construction labels; their manifest and
outcome digests remain the Stage 2 pins. Existing 32 unittest methods remain, with
additional assertions in the existing gate-control method; test count is not a
claim about the number of individual checks.

P3: cap-cause classification recovers exactly the original 39 UNRESOLVABLE rows,
25 sample-cap exceedances and 37 momentum-cap exceedances, predicted to overlap
in 23 rows (2 sample-only and 14 momentum-only). This is an artifact audit, not
a new population estimate or threshold fit. Preserve any mismatch as a failure.

P4: the focused check must reject a deliberately restored status-only matcher.
The normal and optimized existing unit suites and selected mutation checks must
still pass the bounded engineering gate.

Local execution is unavailable at the start of this work. Python execution will
use the existing branch-scoped GitHub engineering CI, with commands/source identity
and raw output retained. Do not label CI execution as local or independently authored.

## Review gates and minimum closure work

Gate B remains open until a reviewer checks the analytic specification, fault
labels and precision contract independently of the implementation and actual
external findings have source-linked dispositions. The present work repairs
review instrumentation and prepares an inspectable package; it cannot certify
its own independence. Model/budget/sample-size approval belongs to Gate C, not
to an expanded Gate B software backlog.

Canonical METHOD.md / WORKFLOW.md / CONTROLS.md at the pinned base apply.
Engineering controls: C-BUILD yes (explicit failure); C-INDEP yes (same-author,
no replication claim); C-EVID yes (versioned sources/artifacts); C-EXPLORE yes
(public development cases only); C-DEVICE yes (CI versions recorded).
C-STAT no for deterministic artifact/control checks; no sampled scientific claim.
C-EXT no new outside scientific source is used in this plan; original reviews
are unavailable, not reconstructed. No methodology comparison or AI execution
takes place. Prior Stage 2 trigger tables and limitations remain intact.
