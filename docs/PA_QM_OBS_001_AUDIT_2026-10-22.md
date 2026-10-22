# PA-QM-OBS-001 — literature audit and design review

**Date:** 2026-10-22 (UTC). **Auditor:** Claude (Anthropic, Opus 5.5) at Chad Holland's direction (2026-10-21). Review level: direction only.
**Target:** PA `main` at `a3accc2` (PR #80 merged): `docs/PA_QM_OBS_001_LITERATURE_INTAKE_2026-10-21.md` and `docs/external/PA_QM_OBS_001_SOURCES_2026-10-21.md`. Drafted by GPT-6 (OpenAI); human review level: direction only.
**Repository record (2026-10-22, later):** at the owner's direction, this audit and its numerical check are now committed. The check lives in [`experiments/qm_obs_001_audit/`](../experiments/qm_obs_001_audit/), and `python3 check.py` reproduces `result.txt` byte-for-byte. It is still a check of the auditor's own derivation (SELF-TESTED), not a registered PA experiment. *(Original line, kept verbatim: "**No repository changes made.** One scratch numerical check of my own derivation was run (§3.3); it is not a PA experiment.")*

---

## 1. Recommendation: **REVISE**, then ADVANCE a math-only registration and PARK any empirical or consciousness-causation arm

Confidence 0.8. The intake is careful and honest: it separates established physics from conjecture and labels everything NOT RUN. It needs four revisions before a W2 registration (§6). The most important is §3.3: in the simplest case the proposed H2 cannot be distinguished from ordinary environmental dephasing *by any measurement*. The open door therefore has to be reframed around what breaks that equivalence.

---

## 2. Reference audit (10/10 identity hashes reproduced)

SHA-256 of each identity line (UTF-8, no trailing newline) was recomputed from the file at `a3accc2`: **10/10 MATCH** (INDEPENDENTLY REPRODUCED).

| ID | Identity / DOI | Exists, title–DOI pair correct? | Status and notes |
|---|---|---|---|
| S01 | Chalmers & McQueen, OUP chapter, 10.1093/oso/9780197501665.003.0002; arXiv 2105.02314 | Consistent with the known record (not re-fetched) | Book chapter 2022 |
| S02 | McQueen, Durham, Müller, *Entropy* 28(4):394, 10.3390/e28040394 | **VERIFIED FROM SOURCE** (MDPI page, 1 Apr 2026; preprint arXiv 2309.13826) | Identity line spells "Muller" (ASCII). Harmless, but the hash is of the ASCII spelling, so note it rather than "fix" it. Content: a two-channel "Schrödinger's dyad", photonic implementation proposal, and **a proof that too few collapse operators cannot make collapse rates depend only on pairwise qualitative differences** |
| S03 | Eren & Beni, *SHPS* 115 (2026), 10.1016/j.shpsa.2025.102102 | **VERIFIED FROM SOURCE** (METU record) | It argues that the Chalmers–McQueen model's predictions concern collapse itself and **cannot by themselves show consciousness is the cause**. That matches the intake's framing |
| S04 | Zurek, *Quantum Darwinism*, Nat. Phys. 2009, 10.1038/nphys1202 | Consistent with the known record | — |
| S05 | Bong et al., Nat. Phys. 2020, 10.1038/s41567-020-0990-x | Consistent with the known record | — |
| S06 | Albantakis et al., IIT 4.0, PLOS CB 2023, 10.1371/journal.pcbi.1011465 | Consistent with the known record | — |
| S07 | Cogitate Consortium, Nature 2025, 10.1038/s41586-025-08888-1 | **VERIFIED** (PubMed 40307561 and institutional records) | Correctly labelled "does not test quantum collapse" |
| S08 | Barrett et al., arXiv 2604.11482 | **VERIFIED exists** (arXiv PDF, May 2026 coverage) | Preprint; correctly labelled |
| S09 | Ma & Wang, Front. Psychol. 17 (2026), 10.3389/fpsyg.2026.1730965 | **VERIFIED FROM SOURCE** (Frontiers, 29 Apr 2026, Review) | Explicitly calls for preregistration, reported nulls and open data, which aligns with SWAY |
| S10 | Donadi et al., Nat. Phys. 17, 74–78 (2021), 10.1038/s41567-020-1008-4; arXiv 2111.13490 | **VERIFIED exists** (arXiv record) | Correctly labelled as a different (gravity-related) collapse family |

**C-EXT:** satisfied for identity. The intake's per-source summaries are editorial and were not audited paper by paper (the intake says so too).

**Omission:** `research_notes/note046_time_is_entanglement.md` was named in the handoff but is **not in the intake's "Connection" section** (§4).

---

## 3. H0 / H1 / H2 analysis

### 3.1 CPTP
The illustrative law `dρ/dt = −i[H,ρ] + D_env + γ D_obj + α f(C(S)) D_cand` is CPTP **if and only if** each D is in GKSL form with non-negative rates and the whole generator is **linear in ρ**. That holds if `α f(C(S)) ≥ 0` and `C(S)` is a fixed property of the *system configuration* (constant in ρ). It fails if `C(S)` is computed **from the current state ρ**: that makes the generator nonlinear, and positivity is no longer guaranteed by the GKSL form.

### 3.2 No-signalling
A deterministic nonlinear ρ-dependence generally allows superluminal signalling (the known Gisin/Polchinski results on nonlinear QM; INFERRED from standard literature, not re-fetched). CSL-type models avoid this because the *ensemble* master equation stays linear, even though single runs are stochastic. **Requirement for any H2 registration:** the averaged dynamics must be linear GKSL; `C` may select *which* operators collapse and at what fixed rates, but must not be re-evaluated on ρ.

### 3.3 Identifiability: a provable degeneracy (my derivation, checked numerically, SELF-TESTED)

Take the simplest paper-faithful H2. Collapse operators are Hermitian and **diagonal in the dyad's classical-state basis**. S02's dyad states are the four classical states of two binary channels, i.e. the computational basis. For diagonal Hermitian operators `L_k = Σ_s λ_s^k |s⟩⟨s|`, the dissipator acts on each coherence as
`|s⟩⟨s'| ↦ −½ Σ_k (λ_s^k − λ_{s'}^k)² |s⟩⟨s'|`.
The whole dissipator is therefore fixed by one matrix of pairwise squared distances between the n basis states. Any such matrix is a squared Euclidean distance matrix, and n points embed in ℝ^{n−1}. It follows that **some ordinary dephasing model with at most n−1 = 3 diagonal operators gives the identical superoperator**. With the same Hamiltonian, no preparation and no measurement can distinguish H2 from that H1′.

Numerical check (registered first; `experiments/qm_obs_001_audit/CLAIM.md` sha `acd8ae16…cdff`, `check.py` sha `e894f277…da5f`; 200 random cases, n = 4, 1–6 diagonal operators plus a random Hamiltonian): **worst superoperator residual 2.13e−14; at most 3 operators needed. CLAIM D HELD.** Control: adding one non-diagonal operator broke the equivalence in every case (min residual 0.398). That control is weak: it shows only that the instrument can return "different", not that the different case is physically relevant.

**Consequence:** for this class of H2, "does consciousness-linked collapse produce distinguishable statistics?" has a definite answer: **NOT IDENTIFIABLE** against generic environmental dephasing. A separation is possible only if one of these holds:
- (a) H2's operators do **not** commute, so they are not pure dephasing in one basis; or
- (b) the environment is **independently constrained**, for example measured to be local and independent. Then decay rates are additive (`Γ₀₀↔₁₁ = Γ₀₀↔₁₀ + Γ₀₀↔₀₁`), and H2's predicted non-additivity `Δ = Γ₀₀↔₁₁ − Γ₀₀↔₁₀ − Γ₀₀↔₀₁` becomes the observable.

Even in case (b), a non-zero Δ is ordinary correlated noise unless correlated environmental noise is ruled out independently. This is the C-NOISE problem, stated exactly. The result agrees with S02's operator-proliferation argument and S03's conclusion, and makes both quantitative.

### 3.4 Independent operational consciousness variable
`C(S)` has no independent operational definition for the systems in question. IIT Φ is defined for discrete causal systems (transition probability matrices), not for quantum states or continuous fields (S08). S02's four dyad states share the **same Φ** and differ only in "Q-shape", so any scalar `f(C(S))` discards the very property S02 uses. Cogitate (S07) shows IIT's own neural predictions were partly challenged. **Verdict on the causation question: UNTESTABLE as currently formulated.** The model-comparison question (§3.3) is testable, and part of it is already answered.

---

## 4. Integration matrix

| PA artifact | Status there | Relation to QM-OBS-001 | Action |
|---|---|---|---|
| note025 Measurement & decision (Speculative) | POVM readout **analogy** for token choice | Shares vocabulary only. "Collapse = token selection" is metaphor; QM-OBS concerns physical collapse | Add one sentence to note025 cross-referencing QM-OBS-001 as the place where physical collapse is treated, so readers don't conflate the two (owner's choice; note edits need W9) |
| 037 Consciousness phase transition (Highly Speculative, Grok) | Conjecture about the reasoning manifold | No physical-collapse content; "consciousness" there is undefined operationally. §3.4's UNTESTABLE verdict applies to it too | Keep separate; no merge |
| note039 Neural Darwinism (Draft, verified code, D2 REFUTED kept) | Uses Zurek's redundancy as a substrate-agnostic definition | **The most useful link.** It is the worked example of borrowing an *operational* quantum-foundations definition without a physics claim. S04 is its source | Cite note039 in QM-OBS as the methodological precedent |
| note046 Time is entanglement (Draft, verified at machine precision) | Exact Page–Wootters toy model | **Missing from the intake.** It is a runnable small-Hilbert-space instrument already in PA. D1 (§5) can reuse its numerical conventions | Add to the intake's connections list |
| Volume III QIG (Draft Proposal, Grok) | Density operators as math for classical LMs; "collapse" via projectors | Intake already preserves this boundary. Volume III's "collapse" is a projector *postulate*, not a GKSL dynamics. Keep it that way | No change |

---

## 5. Smallest discriminating experiment (design only, NOT RUN, NOT REGISTERED)

**QM-OBS-D1: generator identifiability for the minimal dyad (math-only).**
- **System:** the 4-level dyad (2 qubits) with S02's swap feedback Hamiltonian, written exactly as S02 gives it. If the paper gives no explicit operator values, D1 must stop and record that, not invent them.
- **Arms:**
  - H0: unitary only.
  - H1-local: independent local dephasing, 2 rates.
  - H1-general: up to 3 diagonal dephasers.
  - H2: S02's collapse operator(s), paper-faithful.
  - H2-nc: one deliberately non-commuting variant.
- **Registered predictions:**
  - P1: H1-general reproduces H2 exactly (superoperator residual ≤ 1e−12).
  - P2: H1-local does **not** reproduce H2 unless S02's operator gives Δ = 0; Δ is reported exactly.
  - P3: H2-nc is not reproducible by any diagonal model, which shows the instrument can say "identifiable".
  - P4 (left unrun, the door): the ratio between Δ and published correlated-dephasing rates for a named photonic platform.
- **Anti-vacuity and sabotage:** a comparator mutant that ignores off-diagonal blocks must wrongly declare H2-nc equivalent and be caught.
- **Cost:** seconds on the S25 in NumPy; no data, network or model.
- **What passing does *not* show:** anything about experience. D1 is a statement about models.

---

## 6. Revisions requested to the intake (proposed, not applied)

1. Add note046 to "Connection to existing work"; cite note039 as the methodological precedent.
2. In "Scientific falsifiers", add: *"If H2's operators commute (pure dephasing in one basis), H2 is exactly reproducible by environmental dephasing with ≤ n−1 operators; report NOT IDENTIFIABLE unless the environment is independently constrained."*
3. In "Proposed research question", require that `C(S)` enters only through fixed operators or rates (linear averaged dynamics); a ρ-dependent `C` is excluded for CPTP and no-signalling reasons.
4. Reframe the open door: from "provably distinct distributions?" to "which independently measured environmental constraint (locality/additivity, Δ) would break the degeneracy, and does any platform measure it below H2's predicted Δ?"

---

## 7. Approval checklist for Chad

- [ ] Accept or decline the four intake revisions (a W9 edit, credited to Claude Opus 5.5 with review level stated).
- [ ] Decide whether D1 becomes a W2 registration (math-only; C-EXT, C-BUILD and M3 apply; C-DEVICE only if run on the S25).
- [ ] Confirm that the empirical and consciousness-causation arms stay **PARKED** until an independently operational `C(S)` exists.
- [ ] No new numbered note until D1 is registered, given the index's known collisions.

### Sources
- [S02 at MDPI](https://www.mdpi.com/1099-4300/28/4/394) · [S02 preprint](https://arxiv.org/pdf/2309.13826)
- [S03 record (METU)](https://avesis.metu.edu.tr/yayin/956b4abe-6605-4938-8d4f-94bb87ed8877/consciousness-and-the-measurement-problem)
- [S07 on PubMed](https://pubmed.ncbi.nlm.nih.gov/40307561/) · [S08 on arXiv](https://arxiv.org/pdf/2604.11482)
- [S09 at Frontiers](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1730965/full) · [S10 on arXiv](https://www.arxiv.org/pdf/2111.13490)
