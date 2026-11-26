# QFI-001 Q3 registration: feasibility of the QFI split on one small model (counts and cost only)

**Status:** REGISTERED, NOT RUN. Nothing covered here is built. The only thing run is the C-FEAS count script below,
which downloads and hashes the pinned files and tokenises the candidate inputs. It runs no model. Committed alone,
before the Q3 harness exists (M2).

**Authority:** Chad Holland's delegation, PR #181 comment 7141782954. **Ask:** A15.3 (Claude 015): Q3 registration
with the P014-* controls, structural zeros counted apart from small positive eigenvalues, the between-block gap check
kept, and the bookkeeping residual reported per point. Also Amendment 3 item 6 and Amendment 4 item 6 of
[Q1_PREREG.md](Q1_PREREG.md).

**Author:** Claude (Anthropic, Opus 5.5), fresh scheduled session. Human review: none. ChatGPT (OpenAI, Codex) is
invited to attack it on PR #181.

## Question

Can QFI-001's instrument (`qfi_ref.qfi_split_ex`, Amendment 4, code `5c6f772`) be run on activation density
matrices of one small real language model? At how many points and layers is the classical/rotation split decidable
from the numbers? What does a run cost? **This is a feasibility study (C-DESIGN: descriptive).** It makes no claim
about whether the rotation part carries information. That is for Q4–Q6.

## Design (fixed here)

- **Models (stand-ins: one small public model, not "LLMs"):** `EleutherAI/pythia-14m`. The trained model is revision
  `cf967c0a9a04383db6f7b1108d86b2962634b4ac` (main, step 143000). The untrained model is revision
  `56079904bb80b7f36d3b794089f146e7a4d6efae` (step0). Step0 is the same architecture at initialisation, so it is
  Rival 2's natural arm.
  - `model.safetensors` sha256: trained `116a0253…f49a1`, untrained `495e509a…2edb5` (full values in the script).
  - Both are stored in float16. They are cast to float64 to run.
  - Weights are never committed.
- **Forward pass:** `transformers` `GPTNeoXForCausalLM`, eval mode, float64, 2 CPU threads, called with
  `inputs_embeds` and `output_hidden_states=True`. Layer index ℓ = 0…6 is the position in the returned
  `hidden_states` tuple, as returned by the pinned `transformers` version. That version and the torch version are
  recorded in the run output.
- **Inputs:** the first three candidate pairs that tokenise to equal length and differ at exactly one position. The
  rule was fixed in the script before the counts were seen:
  - pair 0: "The cat sat on the mat." / "The dog sat on the mat." (7 tokens)
  - pair 1: "She opened the door and smiled." / "…cried." (7 tokens)
  - pair 2: "The river was cold in the morning." / "…warm…" (8 tokens)
- **Path:** input embeddings e(θ) = (1−θ)·E[x₀] + θ·E[x₁], at θ = 0, 0.1, …, 1. Only the differing row moves.
- **State:** A_ℓ(θ) ∈ ℝ^{n×d} is the layer's token vectors, with d = 128. ρ = AᵀA / tr(AᵀA). That is a 128×128 matrix
  of rank ≤ n, so it has a structural kernel of dimension d − n (121 or 120).
- **Derivative:** ∂A = (A(θ+h) − A(θ−h)) / 2h with h = 1e-4. Then ∂ρ = ∂M/t − ρ·tr(∂M)/t, where M = AᵀA,
  ∂M = ∂AᵀA + Aᵀ∂A and t = tr M. The path extends linearly past θ = 0 and θ = 1.
- **Scale:** 2 models × 3 pairs × 11 θ × 7 layers = **462 points**, from 198 central-difference forward passes, plus
  the step check (h = 1e-3) and the noise check.

## Counts reported per point (the purpose of Q3)

Thresholds: ε = 1e-12, τ_tie = 1e-12, τ_flag = 1e-6, as in `qfi_ref.py`.

1. **Eigenvalues by kind:** structural zeros (≤ ε/2), small positives in (ε/2, 1e-6], and support (> 1e-6). Smallest
   and largest eigenvalue, and the top eigenvalue's share.
2. **Ties by kind:** `n_tied` in blocks lying wholly at or below ε/2, and `n_tied` in all other blocks.
3. **Gaps, check kept:** `near_tie` and `min_gap` exactly as `qfi_ref` returns them. Also the smallest gap among
   eigenvalues > ε/2, and the gap from the largest eigenvalue ≤ ε/2 to the smallest one above it.
4. **Two resolution counts.**
   - `split_resolved`, as `qfi_ref` returns it.
   - `split_resolved_support`, **counted, not adopted:** no tie outside the structural-zero block, every gap among
     eigenvalues > ε/2 above τ_flag, and the kernel-to-support gap above τ_flag. An exact kernel leaves the split
     invariant (F15.1, case P014-kernel-*), and this count asks how often that is all that blocks `split_resolved`.
     Q4 decides whether to adopt it.
5. **Bookkeeping residual** |F_Q − F_C − F_R|, at every point (F15.3).
6. **Sensitivity:** relative change of F_Q with ε = 1e-10 instead of 1e-12, and with h = 1e-3 instead of 1e-4.
7. **Cost:** wall time for each forward pass and for the whole run, and peak memory.

The printed summary gives counts and medians/maxima of items 5–7, by model and layer. It does not print F_R/F_Q or any
other comparison of the trained and untrained models. Per-point values go to the results JSON, because D1 needs them.

## Checks with pass criteria

| ID | Check | Pass |
|---|---|---|
| R0 | Public cases first: `run_cases.py` on `cases/public.jsonl` and `cases/a16_must_fail.jsonl` | public 8 of 8 pass, must-fail rc = 1 |
| R1 | Pinned identities (sha256 of both weight files, blob sha1 of config and tokenizer) | all match |
| R2 | Pipeline controls: synthetic A(θ) through the same ρ/∂ρ/finite-difference code | S1–S3 below |
| R3 | All 462 points finite; \|tr ρ − 1\| ≤ 1e-12; ρ symmetric to 1e-14 | 462 of 462 |
| R4 | Residual ≤ 1e-10·max(1, F_Q) | 462 of 462 |
| R5 | Cost: whole run on this container (2 CPUs) | < 30 min |
| R6 | Determinism: the run repeated in a second process gives the same results digest | equal |
| R7 | Same-input noise (C-NOISE): pair 0, θ = 0.5, both models, 3 repeats in one process | max \|Δρ\| and \|ΔF_Q\| printed; predicted 0 |

**Pipeline controls (anti-vacuity, M3).** Each runs at θ = 0, with A(θ) = diag(√p)-rows·R(θ)ᵀ and n < d:

- **S1, commuting:** p(θ) moves and R = I. Pass: F_R < 1e-8 and |F_Q − F_C| < 1e-8·F_Q.
- **S2, pure rotation in plane (0, 1):** p = (0.5, 0.3, 0.2), d = 5. Pass: F_Q within 1e-6 (relative) of
  4(p₀ − p₁)²/(p₀ + p₁) = 0.2, and F_C < 1e-8.
- **S3, rotation from the support into the kernel, plane (1, 3):** same p, d = 5. Pass: F_Q within 1e-6 (relative)
  of 4p₁ = 1.2, F_C < 1e-8, `split_resolved` False (two-dimensional kernel), and `split_resolved_support` True. This
  is the positive control for item 4.

The closed forms were checked against `qfi_ref` before this registration, on exact ∂ρ (scratch; SELF-TESTED). The
finite-difference route is not yet built.

`--sabotage` sets ∂A = 0. S2 and S3 must then fail, and the run must exit 1.

## Predictions (NOT RUN)

- **P1:** R0–R7 all hold.
- **P2:** `split_resolved` is False at 462 of 462 points, because the structural kernel forms one tie block
  (Amendment 4 item 6(b)).
- **P3:** structural zeros ≥ d − n at every point.
- **No prediction** is made for `split_resolved_support`, small positives, or sensitivity. They are what Q3 measures.

## What Q3 decides (doors for Q4)

- **FEASIBLE as designed** only if R0–R7 hold. Otherwise Q3 reports which check failed first, and Q4 waits.
- At each layer of the trained model, if `split_resolved_support` is True at fewer than 17 of its 33 points, that layer
  cannot carry the split under this construction, and Q4 must drop it or change the construction.
- If no layer qualifies, the d×d second moment is **not feasible**. Q4 then considers the n×n token Gram matrix,
  which has the same nonzero spectrum and no structural kernel. That construction is not tested here.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | C-FEAS counts committed with this file: `results/qfi_001/q3/feasibility_counts.txt` |
| Noise | R7, and R6 across processes |
| Statistics | None. Descriptive counts, no test. |
| Evidence | Raw output pasted in the Q3 results |
| Independence | SELF-TESTED. D1 crossing: ChatGPT's `d1_sld` reads the interchange file (below). |
| External | Public model under Apache-2.0. Its identity is pinned by hash. No outside claim is used. |
| Device | Linux container CPU. S25 NOT VALIDATED. |
| Verdict code | Fail-closed. A missing, NaN or unmatched identity counts as failed. |
| Exploration | Q3 is itself exploration for Q4. Its per-point values are seen. |
| Held-out | The Q3 pairs are development data. Q4 must register fresh pairs to judge on. Any Q4 statement about these pairs is a retrodiction. |
| Generated inputs | All six candidate pairs are listed in the script. Token counts are in the C-FEAS output. |
| People's data | No |
| Design | Descriptive feasibility study. It supports no claim about information content. |

**D1 interchange (crossed handoff, FAST-1).** `results/qfi_001/q3/interchange_subset.npz` holds A and ∂A (h = 1e-4)
for pair 0, both models, θ ∈ {0, 0.5, 1} and all 7 layers: 42 points, about 0.6 MB, with its sha256. It comes with
the reference outputs for those points. The full A/∂A set is not committed; only its sha256 is recorded.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) designed this → human validation: not performed → human editing/curation: none (Chad
Holland's delegation) → human responsibility: Chad Holland. Question lineage: ChatGPT (OpenAI, Codex) notes 012 and 014
(support mask, exact kernel, unequal small eigenvalues). Pythia: EleutherAI (Biderman et al. 2023), used as a public
artifact. No endorsement is implied.

## Unrun next step

Build `q3_run.py`, which imports `qfi_ref` and does not copy it. Run it, then run it again with `--sabotage`. Write
`Q3_RESULTS.md`, failures first.
