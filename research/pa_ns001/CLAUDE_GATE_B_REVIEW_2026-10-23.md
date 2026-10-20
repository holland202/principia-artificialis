# Claude read-only review brief — Friday, October 23, 2026

> Updated 2026-10-20: the appended owner-brief update and the current 16-item
> material matrix govern external-review reconciliation. Earlier instructions are
> retained as the pre-brief record. This remains an unsent preparation document.

**Prepared 2026-10-20; UNSENT. Gate B OPEN. No approval is represented.**

Review only public PA-NS-001 at
`7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd` on
`research/pa-ns-001-protocol-v0-2`.
This package was prepared by ChatGPT (OpenAI GPT-6), the remediation author,
under Chad Holland’s direction. It is not Claude’s review. Do not approve on
behalf of Grok, Perplexity, another reviewer or the owner.

## Assignment and boundary

Decide whether this bounded analytic-profile oracle and its engineering fault
labels are adequate for Gate B, or identify a reproducible material defect.
This is a read-only source/specification/evidence review. Do not change source,
run an AI evaluation, generate held-out cases, freeze criteria, merge, contact
people, publish findings, or access private repositories. No general CFD solver
or Navier–Stokes theorem is proposed.

The owner names Grok and Perplexity reviews, but their original PA-NS-001 texts
were unavailable to the preparer. Their findings must not be invented from the
Work summary. The review-source reconciliation is therefore incomplete.
When originals are available, record their reviewed revision, exact material
finding, underlying evidence and handling rights; retain the original text
unchanged. Confidential originals must remain owner-only.

## Reading set, pinned to the reviewed source

| Material | Why read it |
|---|---|
| [STAGE2_HANDOFF.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/STAGE2_HANDOFF.md) | Exact Gate A/B/C/D definitions and bounded research objective. |
| [ORACLE_AND_FAULTS.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/ORACLE_AND_FAULTS.md) | Assumptions, governing ODEs, identifiability, rounding contract and fault taxonomy. Derive labels from these assumptions, not checker verdicts. |
| [analytic_oracle.py](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/analytic_oracle.py) and [ns001.py](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/ns001.py) | Separate polynomial constructor versus dimensionless binary64 checker; common specification/runtime risks remain. |
| [fault_cases.py](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/fault_cases.py) and [114-case construction manifest](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/evidence/stage2/fault-data1/manifest.jsonl) | Every construction, label and indistinguishable valid control; observed development material only. |
| [CALIBRATION_PLAN.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/CALIBRATION_PLAN.md) and [240-row calibration artifact](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/evidence/stage2/calibration-data1/cases.jsonl) | Prespecified finite engineering matrix and all accepted/unresolved outcomes. |
| [evaluate_faults.py](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/evaluate_faults.py), [test_stage2.py](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/test_stage2.py) and [gate_b_checks.py](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/gate_b_checks.py) | Result-envelope repair and focused malformed-result/sabotage controls. |
| [PREREGISTRATION_DRAFT.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/PREREGISTRATION_DRAFT.md) | Study A/B distinction, simplest rival and the dated amendment superseding §3’s derivative-veto requirement. Still a draft. |
| [GATE_B_REMEDIATION.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/GATE_B_REMEDIATION.md) and [STAGE2_REPORT.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/STAGE2_REPORT.md) | Existing defects, limitations, invalidated run and before/after evidence. These are author reports to challenge, not independent truth. |
| [pre-repair CI index](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/evidence/gate_b/pre_repair/INDEX.json) and [post-repair CI index](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/evidence/gate_b/post_repair/INDEX.json) | Exact commits, jobs, command outputs and expected failures. |
| [GATE_B_SOURCE_MANIFEST.json](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/GATE_B_SOURCE_MANIFEST.json) and [PROVENANCE.md](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/PROVENANCE.md) | Scoped byte identity, attribution and limits of same-author verification. |

Companion closure documents are newly prepared outside the scientific source pin:
[GATE_B_CLOSURE_REVIEW_2026-10-20.md](GATE_B_CLOSURE_REVIEW_2026-10-20.md)
and [closure evidence](evidence/gate_b/closure-2026-10-20.json).
They describe the pinned revision; they do not supersede its raw historical evidence.

## Questions requiring independent judgment

1. **Specification and observable.** Derive the two channel solutions and signed/
   zero-drive cases independently. Check every fault category and the 22
   indistinguishable controls against the actual observable. Is it defensible
   to claim only agreement with declared uniform-grid reference profiles?
   Does any remaining wording imply verification of pressure metadata, off-grid
   flow, physical truth or an AI explanation that the implementation cannot supply?
2. **Precision and nonacceptance.** Check the dimensionless residual and
   `4*e*(N-1)^2` amplification argument under its stated premise. Assess the
   16-epsilon conversion allowance, configuration restrictions and engineering caps
   for the declared finite domain; finite calibration is not a universal bound.
   Audit the unchanged 39 unresolved rows (2 sample-only, 14 momentum-only, 23 both).
   Are these limits acceptable for the bounded claim, or is there a concrete
   in-domain counterexample that invalidates it? Keep conservative denominators.
3. **Instrumentation.** Does the fixed evaluator require a genuine Boolean
   acceptance consistent with the expected status? Are the honest 114 cases,
   four malformed-envelope modes, optimized-mode sabotage and eight selected
   mutants sufficient for the stated engineering claims? Selected mutants are
   not exhaustive coverage. Boundary checking is not a third independent veto.
4. **Fair rival and validity.** Does the dated amendment give profile-only R
   identical data/profile information without V’s derivative-specific vetoes?
   Are V-only unresolved cases retained as operational nonacceptances?
   V’s nesting within B guarantees no larger false acceptance on the same inputs;
   it does not establish improved reasoning or benefit over R. The study
   adapter and final study design are separate Gate C work.
5. **Evidence and independence.** Which findings did you derive, inspect,
   reproduce, or only read as author-reported claims? Do the pinned sources,
   hashes and retained failures support the engineering statements? A separate
   model’s critique must be identified as AI-assisted review; it is not
   automatically independent human replication or owner acceptance. If source
   access, execution capability or domain expertise is insufficient, state the
   narrower conclusion rather than signing off.

Do not demand a general solver, universal theorem, new benchmark, extra framework
or wider scope merely because those might be useful. For any proposed change,
classify REQUIRED / BENEFICIAL / DOCUMENT ONLY / DEFER. REQUIRED needs a
demonstrated defect or material methodology problem, exact source location,
counterexample or derivation, consequence and smallest adequate correction.
A documented limitation is sufficient when the bounded claim remains accurate.

## Evidence already checked, not a substitute for your judgment

- Final [engineering CI 39461927066](https://github.com/holland202/principia-artificialis/actions/runs/39461927066)
  passed Python 3.11.17, 3.12.15, 3.13.16. Each: 32 unit methods in
  normal/-O/-OO, 114 construction labels, eight selected mutants and the scoped
  24-file manifest; both sabotage gates fail as intended.
- Final [repository-wide CI 39461926988](https://github.com/holland202/principia-artificialis/actions/runs/39461926988)
  completed success on the same source. Its number-audit report is non-gating.
- Fresh preparation audit: all 24 scoped SHA-256/size/Git-blob identities match;
  all six saved pre/post CI segments occur verbatim and contiguously in the indexed
  remote job logs. Original calibration/fixture/outcome artifacts match historical
  SHA-256 values. Original Stage 2 evidence tree and numerical checker are unchanged.
- Original failures, the invalidated mutation run and all 39 precision nonacceptances
  remain visible. A post-observation software pin is not a scientific prediction.
- No new Python execution occurred in this preparation. No independent external
  reproduction or sign-off is credited from the available evidence.

The following are reproduction references for already executed engineering work,
not commands to run an AI study. For this read-only review, inspect the existing
commands/output and identify any extra execution evidence you consider essential:

```text
python research/pa_ns001/gate_b_checks.py
python -O research/pa_ns001/gate_b_checks.py --sabotage
    expected process exit: 1

python research/pa_ns001/engineering_gate.py --output <fresh-external-output-directory>
    expected process exit: 0
python research/pa_ns001/engineering_gate.py --sabotage --output <different-fresh-external-output-directory>
    expected process exit: 1

python research/pa_ns001/verify_package.py --root . --manifest research/pa_ns001/GATE_B_SOURCE_MANIFEST.json
    expected: accepted true, checked_files 24, failures [], exit 0
```

The original 395-file `MANIFEST.json` belongs to the historical checkpoint; its
source rows intentionally do not all match remediated sources. Do not call this
evidence loss, silently regenerate it, or claim a fresh full historical audit.
The current 24-file manifest is limited in scope and not an authenticity proof.

## Requested return, to the owner only

Give a concise finding matrix: source/revision, finding, severity, evidence
classification, RESOLVED / ACCEPTED LIMITATION / OPEN, and remaining judgment.
For execution claims, include exact command, environment, exit code and raw output;
otherwise explicitly say “not executed.” Record model/reviewer identity and
scope. Do not silently inherit another system’s verdict.

Recommend **ready for owner Gate B decision**, **narrow remediation required**,
or **inconclusive**, with the minimum blockers. Your recommendation is your own
review record, not owner approval. The missing original-review reconciliation and
owner disposition remain explicit. Gate C selection/freeze/resources/execution and
Gate D findings release remain unauthorized regardless of this review’s outcome.

## Owner-brief update — 2026-10-20

Chad supplied a condensed review account, preserved in
[reconciliation-2026-10-20.json](evidence/gate_b/reconciliation-2026-10-20.json).
Use G01–G07 and P00–P08 in the appended current matrix of
[GATE_B_CLOSURE_REVIEW_2026-10-20.md](GATE_B_CLOSURE_REVIEW_2026-10-20.md).
This account is not either full report or a formal sign-off. The original full
texts and Grok’s source/environment/commands/raw output were not inspected here.

Grok’s reported disposition remains **CONDITIONAL**. Its 240-case reproduction
and 114-label confirmation are reported external claims, distinct from project CI.
Perplexity remains **CONDITIONAL, evidence access blocked**. Its mathematical
derivation/challenges do not establish implementation inspection, 39-case
reproduction, 114-label validation or an evaluator defect. Current artifact access
does not retroactively upgrade either earlier review.

The earlier review questions remain. Focus the remaining judgment on:

- Deriving fault-label truth, including the 22 indistinguishable controls, rather
  than inheriting expected statuses or CI success.
- Adequacy of the bounded precision contract and all 39 unresolved outcomes;
  engineering caps are not physical uncertainty limits.
- The pressure-only G=-dp/dx definition and absence of an independent streamwise
  body-force input. Decide if a minimal assumption clarification is needed.
- V⊆R⊆B guarantees non-increase in false acceptance, not strict benefit. Judge the
  corrected R precision rules and false-rejection/coverage/cost accounting.
- Existing wall-shift, nonfinite, signed-drive and scale/rounding tests versus
  out-of-scope continuum, absolute-pressure and symbolic-expression challenges.
  A mathematical challenge is not an executed failure.

The pinned
[calibration plan](https://github.com/holland202/principia-artificialis/blob/7beb5e646ee1d00ce5a2eae9568e5b869abf2ddd/research/pa_ns001/CALIBRATION_PLAN.md#L83)
requires “an independent human/specification review.” Record your contribution as
AI review, with actual sources/derivations/executions and expertise limits.
Do not silently treat AI-only critique as human review or amend the gate.

Return your own evidence-linked disposition. Distinguish reported claims,
independently derived mathematics and actually reproduced implementation behavior.
Substantiate Grok’s execution claims if relying on them for independent credit;
otherwise keep them reported and uncredited. Full-report coverage remains
unverified. An automatic Perplexity rerun is unnecessary if fresh adequate review
provides the required evidence.

No new implementation defect is demonstrated by the condensed brief. Recommend
only the smallest correction for a material in-scope counterexample; classify
other proposals DOCUMENT ONLY or DEFER. Preserve disagreement and negative results.
Only after the independent requirements are met should the package go to Chad
for his Gate B decision. Do not seek owner approval to replace missing review.

Prepared for Friday, October 23, 2026; **UNSENT**. Gate B remains open; Gate C/D
study execution, merge and findings release remain unauthorized.
