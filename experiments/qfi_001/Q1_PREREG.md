# QFI-001 Q1 registration: reference code for note #022's stated properties

**Status:** REGISTERED, NOT RUN, nothing built. Committed alone before any code (M2). Authority: Chad Holland's
delegation, recorded on PR #181 in comment 7141782954. **Authors:** design by Claude (Anthropic, Opus 5.5). Human
review: none. ChatGPT (OpenAI) is invited to attack it on PR #181 before the code runs.

## Question

Does a NumPy implementation of the quantum Fisher information (QFI), its split into a classical part and a rotation
part, and the Bures distance reproduce known closed-form values and textbook inequalities? This tests **code**, not
a claim about models. The properties are textbook results (Braunstein & Caves 1994; Helstrom 1976). It is the
instrument QFI-001 will use later on activations, so it must be right first.

## Definitions (fixed here)

For ρ(θ) with eigen-decomposition ρ = Σ p_k |k⟩⟨k| and derivative ∂ρ:

- **QFI:** F_Q = 2 Σ_{k,l: p_k + p_l > ε} |⟨k|∂ρ|l⟩|² / (p_k + p_l), with ε = 1e-12.
- **Classical part:** F_C = Σ_{k: p_k > ε} (⟨k|∂ρ|k⟩)² / p_k. This is the Fisher information of the eigenvalues.
- **Rotation part:** F_R = 2 Σ_{k≠l: p_k + p_l > ε} |⟨k|∂ρ|l⟩|² / (p_k + p_l). So F_Q = F_C + F_R term by term.
- **Bures distance:** d_B² = 2(1 − √F), with fidelity F = (tr √(√ρ σ √ρ))².
- **Classical Fisher information of a measurement** {Π_m}: Σ_m (tr Π_m ∂ρ)² / tr Π_m ρ, over outcomes with
  probability > ε.

## Cases and expected values (derived before running)

| ID | Family | Expected |
|---|---|---|
| C1 | qubit, ρ = (I + r(cos θ σx + sin θ σz))/2, r = 0.6, θ = 0.7 | F_Q = r² = 0.36, F_C = 0, F_R = 0.36 |
| C2 | commuting, ρ = diag(p(θ)), p = softmax(θ·a), a = (0, 1, 2, 3), θ = 0.4 | F_Q = F_C = Var_p(a), F_R = 0 |
| C3 | pure qubit, \|ψ⟩ = cos θ\|0⟩ + sin θ\|1⟩, θ = 0.3 | F_Q = 4 |
| C4 | 200 random full-rank d = 4 families (seed 4), 50 random projective bases each | every measurement FI ≤ F_Q + 1e-9 |
| C5 | same families; measurement in the SLD eigenbasis | measurement FI = F_Q within 1e-8 relative, on ≥ 195 of 200 |
| C6 | same families; Bures at step δ = 1e-4 | \|d_B²/δ² − F_Q/4\| / (F_Q/4) < 1e-3 on ≥ 195 of 200 |
| C7 | same families | \|F_Q − (F_C + F_R)\| < 1e-10 on all 200 |

The derivative ∂ρ is analytic for C1–C3 and a central finite difference (h = 1e-6) for C4–C7. For C4–C7, a random
family is ρ(θ) = U(θ) D(θ) U(θ)†, with U(θ) = exp(iθH) for a random Hermitian H and D(θ) a random positive diagonal
moving in θ, renormalised to trace 1, evaluated at θ = 0.

## Anti-vacuity (M3)

`--sabotage` replaces the QFI denominator (p_k + p_l) with 2·max(p_k, p_l). C1, C3 and C5 must then fail. If they
do not, the cases cannot tell a correct QFI from a wrong one.

## Verdict

PASS only if C1–C7 all hold. Exact numbers are printed. A failure is kept and reported first (M8).

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | NumPy only; under a minute on one CPU (NOT RUN estimate). |
| Noise | Deterministic, seeded. |
| Statistics | None; fixed tolerances above. |
| Evidence | Pasted output. |
| Independence | SELF-TESTED. Blind tests (Q2) by ChatGPT later. |
| External | Textbook definitions only. |
| Device | Linux container CPU. S25 NOT VALIDATED. |
| Verdict code | Fail-closed: any NaN or missing case fails. |
| Exploration | None. |
| Held-out | Not applicable (fixed cases). |
| Generated inputs | Random families: their eigenvalue range and the F_R/F_Q share are printed. |
| People's data | No. |
| Design | Verification of code against known results; supports no claim about models. |

## Provenance (M13)

Claude (Anthropic, Opus 5.5) → human validation: not performed → direction: Chad Holland, 2026-11-24 → human
responsibility: Chad Holland. Review level: direction only.
