# PA-NS-001 Stage 2 engineering calibration plan v1

Status: pre-execution engineering plan; **not a frozen AI-study preregistration**.
Recorded 2026-10-20 by ChatGPT (OpenAI GPT-6), under Chad Holland's direction.
Human review of these additions: direction only. No independent reviewer has signed off.
Source prototype and canonical METHOD.md revision: `8a3194f56f400a306778f7a837b51216c3b71220`.
Existing three-test reproduction predates this plan and is retained separately.

## Scope, order and predictions
1. Preserve and diagnose the original prototype. Predict finite but infinite-tolerance
   configuration can accept an incorrect profile; dense/rounded correct profiles can fail
   its illustrative 1e-9 check. These are prospective diagnostic predictions, not observed results.
2. Calibrate on **correct analytic profiles only**, with the matrix below fixed before output.
3. Derive and generate labelled synthetic engineering faults only after calibration.
4. Draft (do not freeze or execute) the AI-study preregistration and owner decision register.

P1: original three tests rerun successfully (a retrodiction, baseline already observed).
P2: invalid or unsupported configuration is never accepted by the repaired verifier.
P3: each unrounded binary64 reference profile in the fixed matrix is accepted by the
   repaired verifier; outcomes on rounded cases are reported individually, including unresolved cases.
P4: demonstrably invalid, resolved faults are rejected; mathematically identical perturbations
   remain valid; specified sabotage controls must make an engineering gate exit 1.
These are implementation predictions, not hypotheses about AI reasoning or CFD accuracy.

## Fixed calibration matrix
Both families; grids N = 5, 21, 65, 257, 1025 samples including both walls.
Six scenarios per family, using decimal parameters exactly as printed:

| ID | h | U | mu | G |
|---|---:|---:|---:|---:|
| unit | 1 | 1 | 1 | 2 |
| small_velocity | 1 | 1e-8 | 1 | 8e-8 |
| large_velocity | 1 | 1e6 | 1 | 8e6 |
| short_channel | 1e-6 | 2 | 1e-3 | 8e9 |
| long_channel | 1e6 | 2 | 1e3 | 8e-9 |
| reverse | 0.5 | -3 | 0.25 | -24 |

Render each correct profile in four ways: nearest binary64; physical velocities
rounded to 10 decimal places; physical velocities rounded to 6 decimal places;
normalized velocities rounded to 10 decimal places then rescaled. Total: 240 cases.
Run each calibration three times; compare canonical result digests. No random sampling,
AI calls, population inference or held-out benchmark outcomes enter calibration.
Report all cases, max/median/95th percentile residuals by grid, false rejections and
unresolved precision separately. Percentiles describe this fixed matrix only.

## Proposed bounded numerical policy (fixed before measurements)
Uniform wall-inclusive grids, 5 <= N <= 4097; steady fully developed Newtonian channels.
Use signed characteristic velocity A=U (Couette) or G*h*h/(8*mu) (Poiseuille).
Check dimensionless profile and boundary error against 1e-9 plus declared rounding
allowance. Check dimensionless momentum residual against 1e-9 + 4*e*(N-1)^2,
where e is declared sample rounding allowance / |A| plus 16 binary64 epsilons.
The factor 4 is the sum of absolute second-difference coefficients (1,-2,1).
Use exact rational arithmetic on supplied binary64 values to avoid verifier arithmetic
roundoff; calibration still measures input/reference rounding amplification.
Reject malformed/nonfinite input; raise ValueError for invalid configuration.
Report UNRESOLVABLE (never accepted) if normalized sample rounding allowance >1e-6
or the momentum allowance exceeds 0.01. These are **proposed engineering resolution
caps**, not calibrated scientific validity criteria. Configured tolerance must be finite
and in (0,1e-4]. The study must approve/freeze its own policy and precision contract.
Zero drive is a separate exact-zero case. Nonzero subnormal/overflowing characteristic
velocity is unsupported. Negative drive is valid reversed flow, not automatically a fault.
Inactive parameters do not identify missing physics (mu for Couette; only G/mu for Poiseuille).

Do not change this matrix or policy in place after execution. Append a dated deviation
and a new plan/version if observations require changes. No tuning on fault cases.
Simplest rival: profile-only analytic comparison using the same input/precision policy;
the full check is not novel mathematical theory and may add no discrimination here.

## Trigger table for this engineering build
| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | yes: script prints the fixed 240 calibration cases and fault counts |
| Noise | C-NOISE | yes: three identical calibration executions, before any empirical bound changes |
| Statistics | C-STAT | no: exhaustive fixed engineering matrix; no population-rate claim |
| Evidence | C-EVID | yes: manifest/source integrity and altered/missing evidence controls |
| Independence | C-INDEP | yes: same-vendor AI self-testing; separate oracle is not independent authorship |
| External | C-EXT | yes: primary references recorded; no third-party source copied |
| Device | C-DEVICE | yes: record actual container/Python, no Android or other platform claim |
| Verdict code | C-BUILD | yes: explicit fail-closed conditions and sabotage tests |
| Exploration | C-EXPLORE | yes: pre-study engineering diagnostics; no future challenge/held-out data used |
| Method comparison | C-METHCOMP | no for this build: deterministic software diagnostics only; proposed AI comparison awaits applicability review |

Gate A is engineering only. Gate B requires an independent human/specification review.
Gate C requires owner-approved frozen model, tasks, precision, budget and analysis.
Gate D is independent review and release approval. No scientific study is authorized.
