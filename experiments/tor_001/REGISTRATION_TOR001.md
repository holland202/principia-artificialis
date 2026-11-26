# TOR-001 registration (DRAFT): does a torus-constrained latent beat linear and Euclidean latents at long rollouts?

**Status:** DRAFT, NOT FROZEN, NOTHING BUILT OR RUN. No field has been generated. Written for ChatGPT's attack before
any freeze ([COLLAB_TOR001.md](COLLAB_TOR001.md)). Changes before the freeze are new commits on this file. The freeze
waits for Chad Holland's own words on this line's PR. **Authors:** Direction: Chad Holland, 2026-11-26. Design:
Claude (Anthropic, Opus 5.5). Human review: none. The question comes from Sushil Pershad's public post
([SOURCE_POST.md](SOURCE_POST.md)), with no endorsement implied.

## Question

When a field's states lie on a 2-torus, does an autoencoder whose latent is projected onto T² and evolved at constant
phase speed predict 1,000-step rollouts better than these rivals?
- **The simplest rival (M14):** POD + DMD (linear modes, linear dynamics).
- **A Koopman autoencoder:** a free latent in R⁴ with learned linear dynamics.
- **An R² latent:** this cannot hold a torus without tearing it.

## Fields (32 × 32 grid on [0, 2π)², all synthetic)

Phases θᵢ(t) = θᵢ(0) + ωᵢ t, with ω = (1, √2) (F3 adds ω₃ = √3). Δt = 0.1.

| Field | Definition | State space | Role |
|---|---|---|---|
| F1 | 0.6 sin(x + y − θ₁) + 0.4 sin(2x − y − θ₂) (the post's field) | T², embedded linearly (rank 4) | the post's case |
| F2 | exp(κ(cos(x + y − θ₁) − 1)) + exp(κ(cos(2x − y − θ₂) − 1)), κ = 8 | T², curved embedding | main test |
| F3 | F2 plus exp(κ(cos(x − 2y − θ₃) − 1)) | T³ | wrong topology: the torus arm must fail |

- **Training:** one trajectory of 4,000 steps from θ(0) = 0, with additive pixel noise σ = 0.01 (seed 1).
- **Test:** 20 noise-free trajectories of 1,000 steps from random initial phases (seed 7), never trained on.
- **Error:** the relative L2 error ‖û − u‖ / ‖u‖, averaged over the 20 test trajectories at horizons 1, 10, 100 and
  1,000. Each learned arm uses 3 training seeds (0, 1, 2). The median over seeds is reported, and so is every seed.

## Arms (named stand-ins, M4)

| Arm | Encoder → latent | Dynamics | Decoder |
|---|---|---|---|
| L4 | POD, 4 modes | DMD (least-squares linear map) | POD modes |
| L* | POD, the fewest modes holding 99.9% of training energy (r* printed) | DMD | POD modes |
| T2 | MLP 1024→128→4; each pair normalised onto a unit circle (P_M) | θ ← θ + ωΔt, with ω learned (2 numbers) | MLP 4→128→1024 on (cos θ₁, sin θ₁, cos θ₂, sin θ₂) |
| K4 | MLP 1024→128→4, unconstrained | z ← A z, with A learned (4 × 4) | MLP 4→128→1024 |
| E2 | MLP 1024→128→2, unconstrained | MLP 2→32→2 | MLP 2→128→1024 |

All learned arms use the same training: Adam at 1e-3, 20,000 steps, batch 64, and a loss summing 1-step and 10-step
rollout errors. They run in PyTorch on CPU, with the version pinned when the code is committed. MLPs are used instead of
the post's convolutional layers. That is a stand-in, named here.

## Predictions (fixed before any field is generated)

| ID | Prediction | Pass criterion |
|---|---|---|
| P1 | On F1, linear is enough | L4's 1,000-step error < 0.01 |
| P2 | On F2, the torus beats a free latent and a 4-mode linear model | T2's 1,000-step error < 0.10, and both K4's and L4's are ≥ 3× T2's |
| P3 | On F2, does the torus beat a high-rank linear model? | T2's 1,000-step error ≤ L*'s |
| P4 | On F2, R² tears the torus | E2's 1-step error ≥ 3× T2's |
| P5 | Anti-vacuity (M3): on F3, the torus arm fails | T2's 100-step error > 0.30 |

**Claude's expectation, recorded and not a criterion (M1):** P1, P2, P4 and P5 hold. P3 is a genuine open question.
Koopman theory says a quasi-periodic signal is linear in enough Fourier modes, so L* may match T2.

## Outcomes

| Order | Condition | Outcome |
|---|---|---|
| 1 | a gate fails, or any number is missing or NaN | INCONCLUSIVE |
| 2 | P5 fails | INSTRUMENT CANNOT FAIL. No torus claim is made |
| 3 | P2 and P3 hold | TORUS EARNS ITS PLACE (on F2) |
| 4 | P2 holds and P3 fails | TORUS BEATS SMALL MODELS ONLY: a high-rank linear model is as good |
| 5 | P2 fails | NO TORUS ADVANTAGE DETECTED |

P1 and P4 are reported with whichever outcome applies. A P1 failure is named first, because it would contradict the
algebra in SOURCE_POST.md.

## Gates and sabotage (C-BUILD, M3)

- **G1:** each generated field is regenerated from its phases and must match to 1e-12. On F1, the POD spectrum must
  have exactly 4 modes above 1e-8 of total energy.
- **G2:** the phases recovered by T2's encoder on the training trajectory are printed, and so is the learned ω beside
  (1, √2).
- **`--no-project`:** removes T2's normalisation, which turns T2 into a K4-like arm with rotation dynamics. P2's margin
  is reported both with and without it.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | NOT RUN estimate: 3 fields × 3 learned arms × 3 seeds = 27 trainings of small MLPs, each a few minutes on CPU, so about 1–2 hours. POD and DMD take seconds. |
| Noise | 3 training seeds. Noise σ = 0.01 on training data. The test is noise-free. |
| Statistics | No p-values. Fixed ratios on medians over seeds. Every seed is reported. |
| Evidence | Numbers pasted from the run's output. |
| Independence | SELF-TESTED by Claude. ChatGPT may seal blind fields (a hidden T² or T³ field with its expected outcome) before the run. |
| External | A public post; question credited; nothing from it is run. |
| Device | Linux container CPU. S25 NOT VALIDATED. |
| Verdict code | Fail-closed precedence table above. |
| Exploration | None. The only computation so far is the algebra in SOURCE_POST.md. |
| Held-out | The test trajectories start from unseen phases. |
| Generated inputs | Every field is synthetic. The first frames are rendered to PNG and looked at before training (C-SYNTH). |
| People's data | None. The screenshot is not committed. |
| Design | Controlled comparison on synthetic fields. Nothing about language models. |

## Unrun door

- Persistent homology of the snapshots: are the Betti numbers (1, 2, 1) on F1 and F2, and (1, 3, 3, 1) on F3? This is a
  model-free check that the state space is a torus, linked to note #041.
- Learned latents' topology, and fields with a curved torus *and* phase-dependent speed.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) drafted → human validation: not performed → direction: Chad Holland,
2026-11-26 → human responsibility: Chad Holland. Review level: none.*
