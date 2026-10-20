# PA-NS-001 — Constraint-Preserving AI Scientific Reasoning

**Status: DRAFT / DEVELOPMENT PROTOTYPE — NOT AN EXECUTED AI STUDY.**

## Question and hypothesis
Can independent, deterministic mathematical verification reduce false acceptance of invalid AI-generated fluid-flow outputs? H1: a verified workflow has a lower false-acceptance rate than a matched unverified workflow. H0: no reduction. This repository addition does not claim support for either hypothesis.

## Analytical reference cases
- Plane Couette flow: steady, fully developed, incompressible, Newtonian flow with stationary lower wall and upper wall speed U, no pressure gradient; `u(y)=U*y/h`.
- Plane Poiseuille flow: stationary walls, steady fully developed pressure-driven flow, positive `G=-dp/dx`; `u(y)=G*y*(h-y)/(2*mu)`.

These cases are intentionally simple. Couette's profile does not depend on viscosity; Poiseuille adds a viscosity-sensitive case. The incompressibility constraint alone cannot detect arbitrary wrong unidirectional profiles.

## Prototype scope
`ns001.py` computes analytical reference values and checks profile error, wall boundary error and a finite-difference momentum-equation residual for equally spaced samples. The verifier compares against an exact profile, so it is a **reference-case oracle**, not a general CFD verifier. Tolerance 1e-9 is a demonstration constant, **not** a scientifically calibrated acceptance criterion. The Python standard library is sufficient.

Run from this directory: `python -m unittest -v`.

## Proposed preregistration, not yet authorized for experimental claims
- Debugging pilot: 20 cases, excluded from final inference.
- Initial main-study planning target: 200 cases, evenly split valid/invalid and across the two flow families; final sample size requires a power/precision analysis.
- Prespecify case-generation seeds, fault families, tolerances, primary false-acceptance metric, uncertainty intervals, prompt/model configuration, runtime and token budget.
- Separate ground-truth construction from AI-generated responses and verification decisions.
- Preserve all negative results and raw provenance; no selective threshold adjustment after outcomes are observed.
- Evaluate false rejection on valid cases and verification overhead, not just fault detection.

## Limitations and publication gate
Three local unit tests of the prototype passed during initial development; this is not an independent audit, main experiment, AI reasoning evaluation, or Navier–Stokes existence/smoothness proof. No AI runs or scientific results have been generated. Before promoting beyond draft: calibrate numerical tolerances; broaden and independently validate the fault oracle; freeze the preregistration; run controlled comparisons; independently reproduce and review evidence. Do not merge or present this draft as verified science without that review.

## Stage 2 engineering update — 2026-10-20
The preceding prototype description is retained as history. See the
[Stage 2 report](STAGE2_REPORT.md), [numerical/fault specification](ORACLE_AND_FAULTS.md),
[draft preregistration](PREREGISTRATION_DRAFT.md) and [owner decisions](OWNER_DECISIONS.md)
for the current development state. This remains a draft research candidate.

The updated checker uses dimensionless quantities, exact rational arithmetic on
binary64 inputs and an explicitly bounded rounding policy. It rejects malformed
inputs and reports insufficient precision as `UNRESOLVABLE`, never accepted.
Signed drive extends the original positive-G examples; no new physical evidence is
claimed. The fixed 240-case engineering calibration accepted 201 profiles and left
39 correctly rounded profiles unresolved. This is not zero false rejection.
The 114 construction-labelled engineering fixtures are public development data,
not fresh scientific evidence or an AI benchmark. Independent oracle review is pending.

From the repository root, with Python 3.11 or later and no added packages:

```sh
python -m unittest discover -s research/pa_ns001 -p 'test_*.py' -v
python research/pa_ns001/engineering_gate.py --output /tmp/pa-ns001-fresh-check
```

Use a new output directory for each run; previous evidence is never overwritten.
The full gate checks normal/optimized Python, three calibration digests, fixture
labels, positive/negative controls and selected mutations against `RECORDED.json`.
That file is a **post-observation software outcome pin**, not a preregistration.
An always-accept sabotage must fail:

```sh
python research/pa_ns001/engineering_gate.py --sabotage --output /tmp/pa-ns001-fresh-sabotage
```

The original three tests and source archive remain intact. Full command logs,
including invalidated/failed engineering attempts, are in `evidence/stage2/`.
No AI model request, official study, main merge or scientific release was performed.

## Gate B remediation update — 2026-10-20

See [the classified remediation record](GATE_B_REMEDIATION.md) and
[scope plan](GATE_B_SCOPE.md). The fixture evaluator now validates the operational
acceptance Boolean as well as its status label; the numerical verifier and
scientific thresholds are unchanged. Independent Gate B review is still pending.

The original MANIFEST.json belongs to its historical Stage 2 checkpoint. For the
explicitly scoped current Gate B source/evidence snapshot, run:

```sh
python research/pa_ns001/verify_package.py --root . --manifest research/pa_ns001/GATE_B_SOURCE_MANIFEST.json
```

This 24-file snapshot is not a complete repository/evidence inventory. The
before/after CI logs retain failed controls and the 39 unresolved calibration cases.
No AI study, main merge or scientific findings release is implied.
