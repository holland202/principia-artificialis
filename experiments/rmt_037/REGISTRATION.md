# RMT-037: do GPT-2's attention heads show random-matrix level statistics, and does training change them?

**State:** REGISTERED, NOT RUN. Committed before any model weights were downloaded and before any code for this
experiment exists.
**Authors:** Direction: Chad Holland (2026-11-14, pick a Principia topic and work on it). Design: Claude (Anthropic,
Opus 5.5). Human review level: direction only. Self-tested (M10).
**Note:** [note037, Random Matrix Theory Level-Spacing Statistics on Attention Weight Spectra](../../research_notes/037_random_matrix_theory_attention.md)
(Speculative; no registered predictions, no run on model weights).
**Method:** [METHOD.md](../../METHOD.md).

## Prior art: this is a replication, not a discovery

Found before writing this (2026-11-14 web search):

- Thamm, Staats and Rosenow, *Random matrix analysis of deep neural network weight matrices*, Phys. Rev. E (2022),
  arXiv:2203.14661. In trained MLPs and CNNs, the bulk of the singular values follows GOE nearest-neighbour spacing.
  Training changes it little; learned information sits in a few large singular values.
- Aarts, Hajizadeh et al., *Dyson Brownian motion and random matrix dynamics of weight matrices during learning*
  (2024), arXiv:2411.13512. In a nano-GPT, key-matrix spacings match the Wigner surmise, while the spectral density
  develops heavy tails.
- Atas, Bogomolny, Giraud and Roux (2013), arXiv:1212.5611: the consecutive-spacing ratio, which needs no unfolding.

So for weight matrices, note037's "Wigner-Dyson or Poisson?" question already has an expected answer: Wigner-Dyson
in the bulk, before and after training. What has not been done in this repository is a registered check of that on
a real pretrained transformer's QK circuits. Also untested here: whether the note's own pipeline (degree-5
polynomial unfolding with a KS test) can be trusted at the size of one head.

## Objects

GPT-2 small (12 layers × 12 heads, d_model 768, d_head 64) and, for replication, GPT-2 medium (24 × 16, d_model
1024, d_head 64). Weights come from the Hugging Face `openai-community/gpt2` and `gpt2-medium` safetensors files. The
SHA-256 of each file is recorded in the results. Per head h, `W_Q,h` and `W_K,h` are the d_model × 64 column blocks
of `c_attn`.

- **QK**: the 64 non-zero singular values of `W_Q,h W_K,hᵀ`, computed as the singular values of the 64 × 64
  matrix `R_Q R_Kᵀ` from thin QR factors. The non-symmetric eigenvalues are complex and are not used.
- **SYM**: the 128 non-zero eigenvalues of the symmetric part `(W_Q W_Kᵀ + W_K W_Qᵀ)/2`, computed exactly in the
  128-dimensional span of `[W_Q W_K]`.

## Statistic

The spacing ratio `r̃_i = min(s_i, s_{i+1}) / max(s_i, s_{i+1})` over consecutive spacings of the sorted levels.
No unfolding is needed. The **bulk** is the levels ranked from 10% to 90% of each head's sorted list, and the
**edge** is the top 10% (the largest levels). Values are pooled per model, object and region as the mean over all
ratios. Large-n references: GOE ≈ 0.5307 and Poisson 2 ln 2 − 1 ≈ 0.3863.

## Reference arms, computed in the run at matched shapes

| Arm | What |
|---|---|
| INIT | GPT-2's own initialisation: `c_attn` weights N(0, 0.02²), with every head's objects computed the same way. Seed 20261114 |
| SHUF | Each trained `W_Q,h` and `W_K,h` with its entries permuted (seed 20261114): same values, structure destroyed |
| GOE | 1,000 GOE matrices with the same level count as each object, giving finite-size references |
| POIS | 1,000 sets of sorted independent uniform levels, same count |

## Predictions (GPT-2 small unless stated; beliefs for calibration only)

| ID | Prediction | Belief |
|---|---|---|
| R1 | QK bulk: trained pooled ⟨r̃⟩ is within 0.02 of INIT's | 0.70 |
| R2 | QK bulk: trained pooled ⟨r̃⟩ ≥ 0.50 (the GOE side, far from Poisson) | 0.85 |
| R3 | QK bulk: no layer's pooled ⟨r̃⟩ (12 heads) is below 0.45 | 0.75 |
| R4 | QK edge: trained pooled ⟨r̃⟩ differs from INIT's by more than 0.05 (if training leaves a trace in the spacings, it is at the edge) | 0.50 |
| R5 | note037's own pipeline (degree-5 polynomial unfolding, KS test against a sampled Wigner reference, p < 0.05) rejects more than 10% of 1,000 true GOE spectra of 64 levels | 0.55 |
| R6 | GPT-2 medium: R1 and R2 both hold | 0.65 |

SYM is reported descriptively, with no prediction.

**Interpretation, fixed now.**

- If R1 and R2 hold, the bulk spacing statistics of GPT-2's QK circuits are those of a random matrix, trained or
  not. Then "chaotic or integrable" carries no information about what a head learned, which answers note037's
  third open question (fancy vocabulary for nothing).
- If R1 fails with the trained value higher or lower, training left a measurable trace in the bulk. That contradicts
  the prior art for this architecture and gets reported first.
- R4 says where to look next, nothing more.
- R5 holding means the note's pipeline should not be used at head size.

## Controls (M3)

| ID | Control | Expected | If it fails |
|---|---|---|---|
| C1 | POIS pooled ⟨r̃⟩ at 64 levels, bulk | within 0.02 of 0.3863 | The statistic is wrong; void |
| C2 | GOE pooled ⟨r̃⟩ at 64 levels, bulk | within 0.02 of 0.5307 | The statistic is wrong; void |
| C3 | The QK object for a head with `W_Q = W_K` (a positive semi-definite case) is computed by both routes (QR, and the full 768 × 768 SVD) | the same 64 values to 1e-8 relative | The object code is wrong; void |
| C4 | The run reads the trained weights twice | identical digests | Determinism broken |

## Triggered controls (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | Yes; about 2 GB download, NumPy linear algebra on 64 × 64 and 128 × 128 matrices |
| Noise | C-NOISE | Deterministic given fixed seeds; INIT and SHUF depend on their seeds, which are fixed now |
| Statistics | C-STAT | Pooled means over thousands of ratios; per-layer pools of about 600. Standard errors are reported. No tests of significance decide anything; the thresholds above do |
| Evidence | C-EVID | Self-tested. Weights are outside material (C-EXT), used unchanged with hashes recorded |
| Independence | C-INDEP | Prior art is the independent evidence; this run is a self-tested replication |
| External | C-EXT | OpenAI's GPT-2 weights through Hugging Face, MIT licence; the hashes are recorded |
| Exploration | C-EXPLORE | The prior art told me the expected answer before registering (disclosed above). Nothing about these weights has been computed |
| Design | C-DESIGN | Observational measurement of two fixed models against matched null arms |
| Synthetic inputs | C-SYNTH | The INIT, SHUF, GOE and POIS spectra are printed in summary (min, median, max level) before any ratio |
| Others | C-DEVICE, C-PRIVATE, C-HOLDOUT, C-METHCOMP | Container run; no people's data; no tuned parameters; not a methodology comparison |

## Door (M15)

Unrun on purpose: the OV circuit (`W_V W_O`). Attention *activation* spectra, rather than weights (a preprint,
arXiv:2606.19404, claims Wigner-Dyson versus Poisson attention spectra separate valid from hallucinated reasoning;
that claim is not checked here). Induction heads against other heads. Models other than GPT-2.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) found the prior art, designed and wrote this registration → human
validation: not performed → human editing/curation: direction by Chad Holland, 2026-11-14 → human responsibility:
Chad Holland. Review level: direction only.*
