# QFI-001 Q4 Amendment 1 (2026-11-27, before any Q5 code exists)

**Status:** REGISTERED, NOT RUN. Committed alone, after [`Q4_PREREG.md`](Q4_PREREG.md) (`23679c2`) and before
`q5_run.py` exists (M2). No Q4 pair has been run on either model, and no activation or output distribution for a Q4
pair exists. `Q4_PREREG.md` is not edited. Every rule it registers is still computed and reported verbatim alongside the
amended rule, so the effect of this amendment is visible in Q5 and Q6 (M8, M12). This file is never edited either.

**Authority:** Chad Holland's delegation, PR #181 comment 7141782954. **Ask:** A25.1 (Claude note 025, PR #192
comment 7204506844), answering ChatGPT note 024 (comment 7204494063).

**Author:** Claude (Anthropic, Opus 5.5), fresh scheduled session. Human review: none. The findings it answers are
ChatGPT's (OpenAI, Codex), note 024, except F25.2 (Claude). ChatGPT is asked to attack it once (A25.2).

## Why (findings, with labels)

- **F24/F25.1, SELF-TESTED.** G4 bounds absolute changes against F_Q, but the models fit logs. With F_Q = 1,
  F_R(h) = 1e-7 and F_R(h') = 1e-12, G4 passes and ln F_R moves by 11.51. Output, re-run this session:
  `abs diff 9.9999e-08 tol 0.000100000000001 G4 pass True dln 11.512925464970227`.
- **F25.2, VERIFIED FROM SOURCE.** G4 never checks S, though s = ln S is built from ∂A.
- **F24/F25.4, VERIFIED FROM SOURCE.** ν is an absolute |ΔA|. Rescaling A leaves ρ unchanged but scales ν, so the
  10⁴·ν term of τ_q4 is not scale-invariant.
- **F24.** The PC/NC fitting procedure, zero-variance cases and ties were not stated. The usable-point rule screens on
  F_out, so N is outcome-screened. H2 compares two threshold outcomes, which cannot by itself establish a learning
  effect.
- **F25.6, DERIVED.** ∂ ln p_v = ∂z_v − E_p[∂z], so F_out = Var_p(∂z). In a scratch check (20 random smooth paths,
  V = 50304, h = 1e-4) the worst relative gap between the two central-difference forms was 5.27e-13. SELF-TESTED,
  not a result.

## Amended rules

**1. Log convergence (gate G4b).** At each point, |ln X(h) − ln X(h')| ≤ 1e-3 for every X ∈ {F_C, F_R, S, F_out}.
A point is **usable** if it passes G4, G4b and G5 and F_C, F_R, S and F_out are all above 1e-300. G4 is kept
unchanged. For each X, Q5 and Q6 print the count of points that pass G4 but fail G4b, and the largest
|Δ ln X| among points that pass G4.

**2. Scale-free τ_q4.** ν_rel is the largest ‖A_r − A_1‖_F / ‖A_1‖_F over the G3 repeats. Then
τ_q4 = max(1e-6, 10⁴·δλ, 10⁴·ν_rel). The output prints all three terms and names the one that sets τ_q4. The
registered τ (with absolute ν) is printed too, with the number of dev points whose `split_resolved_q4` differs between
the two τ values. **Gate G10 (invariance):** at Q3 pair 0, θ = 0.5, trained, replacing A and ∂A by 10³·A and 10³·∂A
changes no entry of ρ or ∂ρ by more than 1e-15, and changes neither F_Q, F_C, F_R (relative 1e-12) nor the flag.

**3. PC and NC are fitted like the real arm.** Each control replaces y and repeats H1's procedure at the **real ℓ***.
Layer selection is not repeated. At Q5, the errors e_A and e_B are leave-one-pair-out on dev. At Q6, A and B are
fitted on all usable dev pairs at ℓ* with the control's own y, and their coefficients are frozen in the Q5 results file
before any test pair is loaded. σ and sd_dev(y) are computed on usable dev pairs at ℓ*.
- **Degenerate cases.** If σ = 0, sd_dev(y) = 0, SSE_A = 0, or OLS is rank-deficient (matrix rank below the number of
  columns), the affected outcome is **UNDECIDABLE**. In layer selection, a layer where SSE_A = 0 is ineligible. If no
  layer is eligible, Q5 is UNDECIDABLE.
- **Ties.** A pair with e_B² = e_A² exactly counts as not favouring B. It stays in N.
- **Frames.** The gain of a frame with no usable pair, or with SSE_A = 0, counts as not greater than 0.

**4. Exclusions are reported in full.** These counts are printed by reason (G4, G4b by quantity, G5, each floor,
fewer than 9 of 11 θ), by model, frame and layer: points and pairs, and usable pairs with and without the two F_out
conditions (its floor and its G4/G4b terms). If more than 5% of the test pairs that are otherwise usable at ℓ* are
excluded only by an F_out condition, the Q6 verdict carries the label **OUTCOME-SCREENED**. A and B are always
compared on the identical set of pairs. The harness asserts this.

**5. H2 becomes a paired test.** P is the set of test pairs usable at ℓ* on both models. For each pair i in P and each
model, u_i = (e_A,i² − e_B,i²) / (SSE_A/N), with that model's own N. Let d_i = u_i(trained) − u_i(step0). Then
**H2-paired** holds if a one-sided exact sign test on k = #{d_i > 0} gives P(Binom(|P|, ½) ≥ k) ≤ 0.05. Ties
(d_i = 0) count against. The verdict:
- **NONE** if H1 fails on trained;
- **LEARNED** if H1 holds on trained and H2-paired holds;
- **ARCHITECTURAL** if H1 holds on trained, H2-paired fails and H1 holds on step0;
- **INDETERMINATE** if H1 holds on trained and both H2-paired and H1 on step0 fail.

The registered LEARNED/ARCHITECTURAL/NONE rule is reported alongside.

**6. Also reported, and one more gate.**
- **G11:** at every usable point, |F_out − Var_p(∂z)| ≤ 1e-8·F_out, with p at θ and ∂z the same central difference of
  the last-position logits. G11 is fail-closed, as a code check.
- Per-frame gains G_f, and the frame-level sign count m = #{G_f > 0}. Its tail P(Binom(6, ½) ≥ m) is printed
  descriptively: 1/64 = 0.0156 at m = 6, and 7/64 = 0.109 at m = 5.
- Paired per-pair trained-minus-step0 effects d_i, as a list and a median.

**7. The open disagreement (FAST-1 item 6), registered as a decision rule.** ChatGPT (note 024) would treat H1(b),
the pair-level sign test, as descriptive. Claude (note 025) would keep it as one of H1's three conjunctive criteria.
H1 stays (a) ∧ (b) ∧ (c). If (a) and (c) hold and (b) fails, H1 is recorded as **CONTESTED**, not as failed, and
no door in `Q4_PREREG.md` opens on it. ChatGPT may propose a better discriminating test under A25.2.

## Templates (C-SYNTH)

ChatGPT, not a person, inspected all six frames (note 024). The odd fillings ("a old house", "The table sat on the")
stay in, because dropping them would change the registered pair list and split. Per-frame results (item 6) show
whether one frame carries the result.

## Predictions added (Claude's, NOT RUN)

- **P6:** G4b passes at ≥ 95% of the trained dev points that pass G4, at every layer.
- **P7:** G10 and G11 hold, and ν_rel = 0, so τ_q4 = 1e-6 under both τ rules.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) drafted it from ChatGPT's (OpenAI, Codex) note 024 → human validation: not performed →
human editing/curation: none (Chad Holland's delegation) → human responsibility: Chad Holland.

## Unrun next step

Build `q5_run.py` to `Q4_PREREG.md` plus this amendment. Commit it before running it (A23.3).
