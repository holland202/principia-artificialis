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

## Amendment 1 (2026-11-24, before any Q1 code was written or run)

Committed alone, before the code (M2). Nothing has been built or run. Two attacks prompted it, and both found the same
weakness. Claude raised it in note 003. ChatGPT (OpenAI) raised it in a message Chad Holland relayed in live chat
(CONTRIBUTOR REPORTED): C7 holds by construction. F_C and F_R are the diagonal and off-diagonal terms of the same sum,
so C7 passes even when both parts are wrong.

1. **C7 is kept, relabelled as a bookkeeping check.** It no longer counts as evidence that the split is right. It still
   gates the verdict, because a failure would mean a coding error.
2. **C8 is added as an independent route to the split.** F_C^fd = Σ_k (∂p_k)² / p_k, where ∂p_k is a central finite
   difference (h = 1e-6) of the sorted eigenvalues of ρ(θ ± h). These come from `eigvalsh` on the perturbed matrices,
   not from matrix elements of ∂ρ.
   - **Expected:** |F_C − F_C^fd| / max(F_C, 1e-12) < 1e-4 on ≥ 195 of 200 C4 families.
   - **Expected:** |F_R − (F_Q − F_C^fd)| / F_Q < 1e-4 on ≥ 195 of 200.
   - Also required for C1 (F_C^fd < 1e-8) and C2 (|F_C^fd − Var_p(a)| < 1e-6).
3. **Tolerances for C1 to C3 were not stated. They are fixed now:** absolute 1e-10 against the closed form.
4. **Sabotage scope.** `--sabotage` changes the denominator in F_Q and F_R only. The SLD used for C5 keeps the
   correct (p_k + p_l). So under sabotage, C5 compares a correct optimal measurement with a wrong F_Q. C1, C3 and C5
   must fail, as registered.

The verdict is PASS only if C1 to C8 all hold.

## Amendment 2 (2026-11-25, before the tie fix was written and before any Q1 run)

Committed alone, before code (M2). Q1 has never run. **Authority:** Chad Holland on PR #181 in his own words
(comment 7161037126, "proceed", after note 007), under the delegation in comment 7141782954.

**Why.** ChatGPT (OpenAI GPT-6, Codex) found the defect in note `qfi001/chatgpt/006`. Claude confirmed it in note 007
(SELF-TESTED): on a commuting path with an exact eigenvalue tie, the split counts 54% of F_Q as rotation. Note 007
proposed grouping eigenvalues with |p_k − p_l| ≤ 1e-8·max(p). ChatGPT's note `qfi001/chatgpt/008` refuted that rule
with a near-tie case. Claude reproduced it (SELF-TESTED, scratch script, not committed): ρ = diag(0.5 + 1e-9,
0.5 − 1e-9) with ∂ρ off-diagonal 0.1. Here the code at `e439899` gives F_C = 0 and F_R = 0.04, which is correct,
because the eigenvalue derivatives are 0. The note-007 rule gives F_C = 0.04 and F_R = 0, which erases a real
rotation. **The note-007 rule is withdrawn.**

**Exploration, disclosed (C-EXPLORE).** Before this amendment, Claude measured the floating-point gap of constructed
exact ties: trace-1 d = 3 states U·diag(0.5, 0.25, 0.25)·U†, 200 random U. `eigvalsh` gives a gap of at most
5.27e-16, with median 1.39e-16. That figure sets τ_tie below. No Q1 case was run.

1. **Total QFI is unchanged.** F_Q is computed in the eigenbasis `eigh` returns. It is invariant under a basis change
   inside a tied block.
2. **Numerical ties only.** A tie block is a maximal run of sorted eigenvalues whose neighbours differ by
   ≤ τ_tie = 1e-12 (absolute, trace-1 states). That is about 2,000× above the measured tie gaps, and 2,000× below
   ChatGPT's 2e-9 case. Inside each block the code rotates to the basis that diagonalises that block of ⟨k|∂ρ|l⟩,
   then splits. Gaps above τ_tie are never regrouped.
3. **Near-ties are flagged, not repaired.** If the smallest gap between distinct blocks is ≤ τ_flag = 1e-6, the split
   is computed as registered but returned with a `near_tie` flag. Any later study withholds the split at flagged
   points and reports how often they occur (Q4 sets its own τ_flag from measured noise). Q1 prints the count.
4. **C9, exact tie (closed form).** ρ(t) = U·diag(0.5, 0.25 + 0.1t, 0.25 − 0.1t)·U†, with U a random unitary from
   seed 0, evaluated at t = 0, with ∂ρ analytic. The required result is F_Q = F_C = 2·0.1²/0.25 = 0.08 and
   F_R < 1e-10, all absolute 1e-10. **Basis invariance:** the split computed in V·R must agree with the split in V
   within 1e-10, where V is the eigenbasis and R is any of 20 random unitaries acting only inside the tied block
   (seed 9).
5. **C10, near-tie (ChatGPT's case).** The required result is F_Q = 0.04, F_C = 0 and F_R = 0.04 (absolute 1e-10),
   with `near_tie` set. Repairing the near-tie fails this case.
6. **C8 scope.** C8 applies only to families whose minimum eigengap at θ = 0 is > 1e3·h = 1e-3. The eligible count is
   printed. C8 holds only if at least 150 of the 200 families are eligible, and each half of C8 passes on at least
   ⌈0.975 × eligible⌉ of them. So exclusions cannot produce an empty pass. C1 and C2's C8 parts are unchanged.
7. **Second sabotage, `--no-tie-fix`.** It skips the block rotation. C9 must then fail. If it does not, C9 cannot tell
   the fix from its absence. `--sabotage` must still break C1, C3 and C5.
8. **Q2.** ChatGPT's sealed cases (`9f5f2897…7147a`) were written for `e439899`. The tie fix changes the code under
   them. Which commit they run against is ChatGPT's call. Claude has not seen them.

The verdict is PASS only if C1 to C10 all hold.

## Amendment 3 (2026-11-25, after the Q1 rerun and Q2; before this change was coded)

Committed alone, before code (M2). **Why:** ChatGPT (OpenAI, Codex) note `qfi001/chatgpt/010`. Claude reproduced it
(SELF-TESTED, scratch script importing `qfi_ref.py` at `71eb582`). ρ = diag(0.5 + g/2, 0.5 − g/2), with ∂ρ off-diagonal
0.1:
```
gap 4e-13 FQ 0.04000 FC 0.04000 FR 0.00000 tied 2 flagged False
gap 4e-12 FQ 0.04000 FC 0.00000 FR 0.04000 tied 0 flagged True
```
The analytic split is F_C = 0, F_R = 0.04 at both gaps. Below τ_tie, the in-block repair gives the opposite, and
`near_tie` stays False. This follows Amendment 2 as written: the flag looked only at gaps between blocks. From numbers
alone, a gap of 4e-13 cannot be told apart from an exact tie. Q1's PASS (`71eb582`) stands for the cases it
registered. This amendment changes the flag and adds a case. It changes no registered value.

1. **One flag for "the split cannot be decided from the numbers": `split_resolved`.** It is False if any tie block
   was resolved (`n_tied > 0`), or if the smallest gap between blocks is ≤ τ_flag. `near_tie` is kept as it was.
   Consumers withhold the split wherever `split_resolved` is False, unless the tie is analytically known. C9 is the
   only such case here. Total F_Q is always reported.
2. **C9** also requires `split_resolved` False. Its values are correct only because the tie is known to be exact.
3. **C10** also requires `split_resolved` False.
4. **C11 (ChatGPT's two gaps):** g = 4e-13 and g = 4e-12 must both give `split_resolved` False and F_Q = 0.04
   (absolute 1e-10). The split values at g = 4e-13 are recorded, not required.
5. **Random families:** the count with `split_resolved` False is printed.
6. **Q3 and Q4 count both kinds:** resolved tie blocks and near-ties.

The verdict is PASS only if C1 to C11 all hold.
