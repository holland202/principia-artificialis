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
