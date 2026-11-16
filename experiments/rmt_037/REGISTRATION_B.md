# RMT-037b: does training lower spacing repulsion at the spectral edge? A registered test on a new model family

**State:** REGISTERED, NOT RUN. Committed before any OPT weights were downloaded and before any code for this part
exists.
**Authors:** Direction: Chad Holland (2026-11-16, "make the best decision for me"). Design: Claude (Anthropic,
Opus 5.5). Human review level: direction only. Self-tested (M10).
**Parent:** [RMT-037](RESULTS.md). Its R4 (|edge difference| > 0.05 in GPT-2 small) was REFUTED at 0.012. Both GPT-2
models moved the same way, toward less repulsion among the largest QK singular values after training: small
0.4895 against 0.5016, and medium 0.4882 against 0.5271.

## Decide and judge on different data (C-HOLDOUT)

The direction and the threshold below come from GPT-2, which is already viewed. They are judged on a model family
whose weights Claude has never computed anything on: **Meta's OPT-125m and OPT-350m**
(`facebook/opt-125m`, `facebook/opt-350m`). Like GPT-2, OPT has separate query and key projections, learned
positional embeddings and no rotary embedding, so `W_Q W_Kᵀ` per head is the same object as in RMT-037.

## Objects, statistic and arms: unchanged from RMT-037 unless stated

- Per head h: `W_Q,h` and `W_K,h` are the d_model × 64 blocks of `q_proj.weight.T` and `k_proj.weight.T`. Biases
  and OPT's query scaling are ignored; the spacing ratio does not change under scaling.
- **QK**: the 64 non-zero singular values of `W_Q,h W_K,hᵀ`. Bulk: ranks 10–90%. Edge: top 10%.
- Statistic: the pooled mean spacing ratio ⟨r̃⟩.
- **INIT:** OPT's initialisation, N(0, 0.02²) (its `init_std`). **SHUF:** entries permuted within each W. Seed
  20261114, as in RMT-037.
- OPT-350m has d_model 1024 and 16 heads per layer, with 24 layers. OPT-125m has 768, 12 heads and 12 layers.

## Predictions (directional, registered now; beliefs for calibration only)

| ID | Prediction | Belief |
|---|---|---|
| E1 | OPT-125m QK edge: INIT − TRAINED ≥ 0.02 | 0.55 |
| E2 | OPT-350m QK edge: INIT − TRAINED ≥ 0.02 | 0.6 |
| E3 | Both OPT models, QK bulk: \|TRAINED − INIT\| ≤ 0.02, replicating RMT-037's R1 in a second family | 0.8 |
| E4 | Both OPT models, QK edge: SHUF − TRAINED ≥ 0.02. Shuffling, which keeps the values and destroys the structure, also removes the effect | 0.5 |

Standard errors (expected, from ratio counts): about 0.009 for OPT-125m's edge (720 ratios) and about 0.006 for
OPT-350m's (1,920). A threshold of 0.02 is roughly 2 SE for 125m.

**Interpretation, fixed now.**

- **E1 and E2 holding:** the edge effect survives in a second model family under a direction and threshold fixed on
  GPT-2. That turns RMT-037's lead into a registered result for two families. It still says nothing about *what*
  was learned.
- **E4 holding as well:** the effect needs the trained arrangement of the weights, not just their value
  distribution.
- **E1 or E2 failing:** the GPT-2 lead does not generalise at this threshold, and the claim stays at "GPT-2 only,
  found after the fact".
- **E3 failing:** the bulk null from RMT-037 is GPT-2-specific. That would be reported first.

## Controls (from RMT-037, re-run here)

C1 Poisson(64) bulk within 0.02 of 0.3863; C2 GOE(64) bulk within 0.02 of 0.5307; C3 QK via QR equals the full SVD;
C4 weights read twice identical. Any control failing makes the run void.

## Triggered controls (M16)

| Control | Answer |
|---|---|
| C-HOLDOUT | Decided on GPT-2 (already viewed), judged on OPT (never computed on) |
| C-EXPLORE | The lead was found after the fact in RMT-037; disclosed above |
| C-EXT | OPT weights from Hugging Face (Meta's OPT licence, research use); SHA-256 of every file recorded |
| C-STAT | Thresholds of about 2 SE; one run, no peeking; standard errors reported |
| C-NOISE | Deterministic, fixed seeds |
| C-INDEP | Claude-written and self-tested; the prior art (Thamm et al. 2022) is the only outside evidence |
| C-SYNTH | The INIT, SHUF, GOE and POIS level summaries are printed before any ratio |
| C-DESIGN | Observational measurement of fixed models against matched random arms |
| Others | C-DEVICE (container), C-PRIVATE (no people's data), C-METHCOMP: not triggered |

## Door (M15)

A family with rotary embeddings (Pythia, where `W_Q W_Kᵀ` is not the whole QK circuit). The OV circuit. What the
edge directions encode.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) → human validation: not performed → human editing/curation: direction
by Chad Holland, 2026-11-16 → human responsibility: Chad Holland. Review level: direction only.*
