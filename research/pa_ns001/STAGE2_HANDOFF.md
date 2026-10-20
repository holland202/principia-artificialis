# PA-NS-001 — Stage 2 verification and preregistration handoff

**Status:** DEVELOPMENT PLAN ONLY. No AI experiment executed; no scientific result established.
**Branch:** `research/pa-ns-001-protocol-v0-2` in `holland202/principia-artificialis`.
**Scope:** Public PA research only. Do not access or copy private research.

## First: inspect and reproduce
1. Read `research/pa_ns001/README.md`, `ns001.py`, and `test_ns001.py` from the current branch; compare to current `main`.
2. Run `python -m unittest discover -s research/pa_ns001 -p 'test_*.py' -v` in a clean environment. Record Python version, commit SHA, exit status, and complete output. Do not describe tests as passed unless independently executed.
3. Check for numerical sensitivity: `dy` and second differences can amplify roundoff as grid density increases. Current `1e-9` tolerance is illustrative only. Verify residual normalization and explicit physical assumptions.
4. Check whether all invalid inputs are rejected (e.g., nonfinite parameters, invalid sample types, negative grid length, unknown flow family) and whether false rejection occurs for legitimate rounded numerical profiles.

## Build Stage 2 evidence
1. Implement a separate, clearly documented calibration script using analytic Couette/Poiseuille reference profiles across preselected grids and physical parameter ranges. Measure floating-point residual distributions and error amplification; do not tune thresholds using held-out challenge outcomes.
2. Independently derive/verify expected outcomes for at least: correct profiles, wall shifts, sign reversal, pressure-gradient sign errors, viscosity mismatch, interior profile perturbation, nonfinite values, and discretization artifacts. Identify cases that are mathematically indistinguishable under given inputs.
3. Add deterministic fault generation with fixed, recorded seeds, case manifests, and a ground-truth oracle distinct from the candidate AI.
4. Draft a preregistration that specifies the sampling unit, baseline vs verified workflow, AI model/prompt controls, budget parity or explicit cost accounting, primary false-acceptance rate, false-rejection rate, confidence intervals, minimum meaningful effect, and sample-size justification.
5. Preserve raw evidence, limitations, failures, and exact command logs. Separate unit-test evidence from claims about AI performance.

## Decision gates
- **Gate A:** reproducible local software tests and documented calibration.
- **Gate B:** independent oracle and fault-case review.
- **Gate C:** frozen preregistration and owner approval for AI study execution.
- **Gate D:** independent evidence review before any claim of verified findings or public release.

Do not alter historical PA studies or reserved seeds. Work on the isolated branch; do not merge into `main` or announce scientific results without explicit release review. If you discover a substantive methodological ambiguity, document it and request a decision.
