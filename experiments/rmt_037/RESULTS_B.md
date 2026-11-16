# RMT-037b results (run 2026-11-16)

**Status:** run as registered at `a8cc5c8` ([REGISTRATION_B.md](REGISTRATION_B.md)). Code committed at `743b2d7`
before any statistic of the OPT weights was computed; only layer names and shapes were inspected. SELF-TESTED.
**4 of 4 predictions held; 4 of 4 controls held.**

- **Digest:** `3f2625d3f8490f12ceb3e76dacdc0929a9bd33133ee4dd79c4a0d32270553828`. A rerun was byte-identical.
- **Weights:** `facebook/opt-125m` revision `27dcfa7`, `pytorch_model.bin` SHA-256 `2d74da66…74a9`;
  `facebook/opt-350m` revision `08ab08c`, SHA-256 `a5223ae6…2842`. Loaded with `torch.load(weights_only=True)`.
- **Raw output:** [`results/rmt_037/run_b.txt`](../../results/rmt_037/run_b.txt) and
  [`rerun_b.txt`](../../results/rmt_037/rerun_b.txt). The run took 29 s.

## What is weaker than it looks (M8)

- **One margin is thin.** E4 for OPT-125m (shuffled minus trained, edge) is +0.0272 against a threshold of 0.02.
  That difference is about 2 combined standard errors (0.0093 and 0.0097). The other three held with margins of
  about 4.5 to 5.5 standard errors.
- **This is a known pattern, not a discovery.** Thamm, Staats and Rosenow (2022) already reported that deviations
  from random-matrix statistics sit in the large singular values. A low-rank learned signal on top of a random bulk
  produces outlier singular values with irregular spacing. Weaker repulsion at the edge is the expected signature of
  that. What this run adds is a **registered, directional replication on transformer QK circuits across two model
  families**, with the threshold fixed on GPT-2 and judged on OPT.
- **The spacing ratio says nothing about what was learned.** It says the largest singular values stop behaving like
  a random matrix's; it does not say what they encode.

## Results (QK circuits, pooled ⟨r̃⟩ ± standard error)

| Model | Region | Trained | Init | Shuffled |
|---|---|---|---|---|
| OPT-125m | bulk | 0.5241 ± 0.0031 | 0.5352 ± 0.0030 | 0.5355 ± 0.0031 |
| OPT-125m | edge | **0.4814** ± 0.0097 | 0.5561 ± 0.0095 | 0.5086 ± 0.0093 |
| OPT-350m | bulk | 0.5308 ± 0.0019 | 0.5302 ± 0.0018 | 0.5293 ± 0.0019 |
| OPT-350m | edge | **0.4841** ± 0.0061 | 0.5226 ± 0.0059 | 0.5283 ± 0.0058 |

| ID | Prediction | Observed |
|---|---|---|
| E1 | OPT-125m edge: INIT − TRAINED ≥ 0.02 | HELD, +0.0747 |
| E2 | OPT-350m edge: INIT − TRAINED ≥ 0.02 | HELD, +0.0385 |
| E3 | bulk \|TRAINED − INIT\| ≤ 0.02, both models | HELD: 0.0110 (OPT-125m, about 2.5 SE, the trained bulk slightly lower) and 0.0006 |
| E4 | edge SHUF − TRAINED ≥ 0.02, both models | HELD: +0.0272 (thin, see above) and +0.0441 |

Controls: Poisson(64) 0.3855; GOE(64) 0.5309; QR route against full SVD, maximum relative difference 1.0e-15; weights
read twice identical.

## Across all four models (RMT-037 and 037b)

| Model | Edge: Init − Trained | Bulk: \|Trained − Init\| |
|---|---|---|
| GPT-2 small | +0.012 (RMT-037; found after the fact) | 0.0005 |
| GPT-2 medium | +0.039 (RMT-037; found after the fact) | 0.0024 |
| OPT-125m | **+0.075 (registered)** | 0.0110 |
| OPT-350m | **+0.039 (registered)** | 0.0006 |

In all four, training leaves the bulk spacing statistics where a random matrix puts them and lowers repulsion among
the largest QK singular values. In both OPT models, which were registered in advance, shuffling the trained values
removes the edge effect. **So the effect depends on how the trained weights are arranged, not on the
distribution of their values.**

## Doors (M15), unrun

- A rotary-embedding family (Pythia), where `W_Q W_Kᵀ` alone is not the QK circuit.
- The OV circuit.
- Which heads carry the edge effect, and whether it tracks known head types such as induction or previous-token
  heads.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) registered, wrote, ran and wrote this up → human validation: not
performed → human editing/curation: direction by Chad Holland, 2026-11-16 → human responsibility: Chad Holland.
Review level: direction only.*
