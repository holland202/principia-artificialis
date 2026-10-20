# Analytic construction and engineering fault oracle

Status: implementation specification awaiting independent review (Gate B).
ChatGPT (OpenAI GPT-6) wrote both implementations; this is **not independent authorship**.
Only public PA files and cited public mathematics/documentation were consulted.

## Assumptions and derivation
Steady, fully developed, unidirectional, incompressible, constant-viscosity Newtonian
flow between infinite plane walls at y=0 and y=h. No transverse velocity, entrance
effects, turbulence or moving geometry. This reduces the momentum equation to an ODE.

Couette: u''=0, u(0)=0, u(h)=U, hence u=(U/h)y. Viscosity cannot be inferred
from this velocity profile. The API's G argument is inactive for this family;
the physical problem itself assumes zero pressure gradient.

Poiseuille: mu*u''=-G, u(0)=u(h)=0. Write u=a*y^2+b*y+c; then
a=-G/(2*mu), b=G*h/(2*mu), c=0. Only G/mu is identified. A simultaneous
equal scaling of G and mu changes neither velocity nor this reference-case verdict.
Signed U and G permit reversed flow; reversal is a fault only relative to a fixed,
nonzero signed reference specification. With zero drive, reversal changes nothing.

`analytic_oracle.py` constructs physical-coordinate polynomial coefficients using
exact decimal/rational parameters. `ns001.py` instead uses dimensionless shapes and
exact rationals for binary64 inputs. Neither construction asks an AI for truth.
They still share the mathematical assumptions, Python and Fraction implementation;
agreement cannot exclude a common specification error. Hand-derived five-point
vectors and polynomial identities provide additional checks, not independent review.

## Normalization, rounding and resolution
Let eta=y/h, A=U for Couette or G*h^2/(8*mu) for Poiseuille, q=u/A.
The target shapes are eta and 4*eta*(1-eta); q'' in eta is respectively 0 and -8.
Thus profile and momentum metrics are dimensionless. This removes the original
unit-dependent floor of 1 physical velocity or 1 physical second derivative.

The central second difference is exact for linear/quadratic polynomials in exact
arithmetic: no O(dy^2) truncation term exists for these particular analytic profiles.
If each normalized sample has error at most e, its second-difference error is at most
(1+2+1)*e*(N-1)^2. Dense grids amplify input rounding, even with an exact checker.
The fixed engineering policy adds a 16-epsilon conversion allowance and explicit
resolution caps; the finite calibration matrix is not a universal error proof.
Rounding allowance is fixed by the experiment configuration, never accepted from
an AI reply. Reference-only acceptance is also a required simple competing method.

`UNRESOLVABLE` is fail-closed nonacceptance, not evidence of wrong physics. Report it
separately and include it in conservative operational false-rejection totals for valid
inputs. Never remove such cases after seeing results. Zero drive requires exact zero
samples; nonzero rounding allowance there is unresolved. Nonzero subnormal or
overflowing characteristic velocity is outside this bounded prototype's scope.

## Expected outcomes fixed by construction
| Construction | Couette | Poiseuille | Reason |
|---|---|---|---|
| Correct samples | accept | accept | ODE and both wall conditions |
| Add constant wall shift | reject | reject | wall mismatch even though second derivative is unchanged |
| Negate velocities with original specification | reject | reject | nonzero signed drive was fixed |
| Reverse generating G only | accept, indistinguishable | reject | G inactive in Couette; curvature sign changes in Poiseuille |
| Double generating mu only | accept, indistinguishable | reject | Couette independent of mu; Poiseuille amplitude halves |
| Double generating G and mu | accept, indistinguishable | accept, indistinguishable | same analytic solution |
| Perturb one interior sample | reject | reject | local curvature and profile mismatch |
| Nonfinite or Boolean sample | reject | reject | invalid representation; Boolean is not a physical measurement |
| Sample at eta^2 but declare uniform grid | reject | reject | wrong coordinates, despite legitimate underlying profile |
| Round normalized values to ten decimals | accept with bound | accept with bound | declared bounded representation error |
| Three-node piecewise linear interpolant | accept, identical | reject under this exact-profile contract | not a general claim that approximate CFD is invalid |
| Drop last wall sample and declare a new uniform grid | reject | reject | domain/sample mapping changes |
| Replace nonzero flow by zeros | reject | reject | normalized profile differs by order one, even for tiny velocities |
| Zero-drive sign reversal | accept, indistinguishable | accept, indistinguishable | identical zero solution |

Fixtures are engineering examples, not secret/held-out challenges or population samples.
The fixed string seed is `PA-NS-001:STAGE2:ENGINEERING:2026-10-20:v1`.
SHA-256(seed + case identity) selects interior index and perturbation magnitude;
no PA reserved numeric seeds are used. Each case stores parameters, values, exact
construction facts, expected status, identity and content hash. The evaluator imports
the actual verifier. Labels are produced by construction, not its decisions.

## Anti-vacuity limits and next review
Always-accept and always-reject checkers must both fail the case gate. Selected
source mutations test tolerance validation, nonfinite rejection, precision handling,
profile checking and momentum checking. The boundary acceptance condition is
dominated by the profile condition with the same threshold: removing it alone cannot
change acceptance. Boundary metrics are tested, but are not a third independent
scientific test. No claim of exhaustive mutant coverage is made.

Next unrun review: a fluid-mechanics/numerical-analysis reviewer checks the ODE,
the signed/zero-drive cases, resolution contract and all construction labels without
using verifier outputs to decide correctness. Gate B remains pending until recorded.
