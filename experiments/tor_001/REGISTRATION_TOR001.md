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

- **Training:** one trajectory of 4,000 steps from θ(0) = 0, with additive pixel noise σ = 0.01. One noise
  realization (seed 1) is generated per field and shared by every arm.
- **Test:** 20 noise-free trajectories of 1,000 steps from random initial phases (seed 7), never trained on.
- **Error:** the relative L2 error ‖û − u‖ / ‖u‖, averaged over the 20 test trajectories at horizons 0
  (reconstruction only), 1, 10, 100 and 1,000. Each learned arm uses 3 training seeds (0, 1, 2). The median over seeds is reported, and so is every seed.

## Arms (named stand-ins, M4)

| Arm | Encoder → latent | Dynamics | Decoder |
|---|---|---|---|
| L4 | POD, 4 modes | DMD (least-squares linear map) | POD modes |
| L* | POD, the fewest modes whose squared singular values reach 99.9% of their sum, on the noisy training data only (r* printed) | DMD | POD modes |
| T2 | MLP 1024→128→4; each pair normalised onto a unit circle (P_M) | θ ← θ + ωΔt, with ω learned (2 numbers) | MLP 4→128→1024 on (cos θ₁, sin θ₁, cos θ₂, sin θ₂) |
| K4 | MLP 1024→128→4, unconstrained | z ← A z, with A learned (4 × 4) | MLP 4→128→1024 |
| E2 | MLP 1024→128→2, unconstrained | MLP 2→32→2 | MLP 2→128→1024 |
| NP | as T2, but the pairs are **not** normalised | the same two block rotations by ωΔt (ω learned), applied to the raw pairs; no renormalisation anywhere | as T2, on the raw pairs |

All learned arms use the same training: Adam at 1e-3, 20,000 steps, batch 64, and a loss summing 1-step and 10-step
rollout errors. NP differs from T2 only in the projection, which separates projection from rotation dynamics
(ChatGPT note 002). They run in PyTorch on CPU, with the version pinned when the code is committed. Every arm reports
its latent size or rank, its parameter count and its fit time. MLPs are used instead of
the post's convolutional layers. That is a stand-in, named here.

## Predictions (fixed before any field is generated)

| ID | Prediction | Pass criterion |
|---|---|---|
| P1 | On F1, linear is enough | L4's 1,000-step error < 0.01 |
| P2 | On F2, the torus beats a free latent and a 4-mode linear model | T2's 1,000-step error < 0.10, and both K4's and L4's are ≥ 3× T2's |
| P3 | On F2, does the torus beat a high-rank linear model? | T2's 1,000-step error ≤ L*'s |
| P4 | On F2, the R² latent predicts worse | E2's 1-step error ≥ 3× T2's. This is consistent with a torn embedding but does not show one; no topology claim is made from it |
| P5 | Anti-vacuity (M3): on F3, the torus arm fails | T2's 100-step error > 0.30 |
| P6 | On F2, the advantage comes from the projection | T2's 1,000-step error ≤ ½ × NP's (medians), and lower than NP's in at least 2 of 3 paired seeds |

**Claude's expectation, recorded and not a criterion (M1):** P1, P2, P4 and P5 hold. P3 is a genuine open question.
Koopman theory says a quasi-periodic signal is linear in enough Fourier modes, so L* may match T2.

## Outcomes

| Order | Condition | Outcome |
|---|---|---|
| 1 | a gate fails, or any number is missing or NaN | INCONCLUSIVE |
| 2 | P5 fails | WRONG-TOPOLOGY CONTROL DID NOT SEPARATE. Topology claims withheld; P2 and P3 still reported |
| 3 | P2, P3 and P6 hold | TORUS PROJECTION EARNS ITS PLACE (on F2) |
| 4 | P2 and P3 hold, P6 fails | T2 BEATS THE NAMED BASELINES; NO PROJECTION BENEFIT MET P6. No component is credited, because no arm removes only the rotation dynamics |
| 5 | P2 holds and P3 fails | TORUS BEATS SMALL MODELS ONLY: a high-rank linear model is as good |
| 6 | P2 fails | NO TORUS ADVANTAGE DETECTED |
| 7 | anything else | INCONCLUSIVE (fallback) |

No claim is made about rarely visited phases. The test starts are random, not drawn from a held-out phase region.

P1 and P4 are reported with whichever outcome applies. P1 tests a **fitted rollout on noisy training data**, while G1
tests the **clean** field's rank. So a P1 failure with G1 passing does not contradict the algebra in SOURCE_POST.md. It
would mean noise or fitting broke the linear rival, and it is named first. A G1 failure stops the run.

## Input interface (for every field, including blind fields)

A field is a directory holding three files:
- `train.npy`: float64, shape (4000, 32, 32).
- `test.npy`: float64, shape (20, 1001, 32, 32), where frame 0 of each trajectory is its start.
- `meta.json`: {"dt": …}.

Training reads only `train.npy`. `test.npy` is opened only after every arm has finished fitting, and the code checks
this (it records the order of file opens). It is used only for scoring. Blind fields follow the same interface, with
SHA-256 values of all three files posted before the run.

## Gates and sabotage (C-BUILD, M3)

- **G1 (revised after ChatGPT note 002):** each generated field is regenerated from its phases and must match to
  1e-12. **Rank oracle:** the clean, noise-free F1 training trajectory (4,000 snapshots, uncentred). Its squared
  singular values, divided by their sum, must have exactly 4 values above 1e-8.
- **Diagnostic, not a gate:** the phases recovered by T2's encoder on the training trajectory are printed, and so is
  the learned ω beside (1, √2). Phase origin, orientation and order are arbitrary, so no pass criterion is set.
- **NP arm:** it replaces the earlier `--no-project` switch, so the comparison is a registered arm with identical
  training.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | NOT RUN estimate: 3 fields × 4 learned arms (T2, K4, E2, NP) × 3 seeds = 36 trainings of small MLPs, each a few minutes on CPU, so about 1.5–3 hours. POD and DMD take seconds. |
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

## Revisions before freeze (W9)

- **2026-11-26, after ChatGPT (OpenAI, Codex) note tor001/chatgpt/002** (PR #186, comment 7195140245). No field
  generated, nothing run.
  - G1's rank oracle now runs on clean, uncentred F1, with the threshold on normalised squared singular values. One
    shared noise realization is used per field. L*'s rank is chosen from the noisy training data alone.
  - The NP arm (identical to T2 apart from the projection) replaces `--no-project`. P6 and a separate outcome row now
    keep a win by the rotation dynamics from being credited to the projection.
  - Horizon 0 (reconstruction) is reported, and so are rank, parameter count and fit time.
  - No rare-phase claim is made.
  - A P5 miss is now labelled "wrong-topology control did not separate".
  - P4 is narrowed: it makes no claim about tearing.
  - G2 becomes a diagnostic.
  - A fallback row is added, and the feasibility count is updated for the fourth learned arm.
  - Superseded text is in this file's history at `687e6f8`.
- **2026-11-26, after ChatGPT note tor001/chatgpt/004** (comment 7196003761):
  - Outcome row 4 no longer credits rotation dynamics. It reports the observed comparisons only. Superseded, verbatim:
    "ROTATION DYNAMICS HELP; THE PROJECTION IS NOT SHOWN TO".
  - P1 is separated from the clean G1 rank oracle. Superseded, verbatim: "A P1 failure is named first, because it would
    contradict the algebra in SOURCE_POST.md."
  - An input interface that separates training and test arrays is added for blind fields.
