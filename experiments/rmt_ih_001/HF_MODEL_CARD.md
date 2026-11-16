---
license: mit
library_name: pytorch
tags:
  - research
  - interpretability
  - random-matrix-theory
  - training-dynamics
  - toy-model
---

# rmt-ih-001: tiny copying transformers, with their QK spectra tracked through training

**Research artefact, not a useful model.** These are 24 tiny attention-only transformers of 575,232 parameters
each. They were trained from scratch to study how the attention weights' spectrum changes at the moment a model
learns to copy. Code, registrations and full results:
[principia-artificialis/experiments/rmt_ih_001](https://github.com/holland202/principia-artificialis/tree/main/experiments/rmt_ih_001).

## The main finding, failures first

- **These are not induction heads.**
  - The training data always repeated a 32-token segment exactly 32 positions later. The models learned that
    fixed offset from their position embeddings.
  - They copy perfectly at offset 32 (accuracy 1.00), and near chance (0.01–0.07) at any other offset or length.
  - So the study's original question, about induction heads, was not tested. It needs data with varying offsets.
- **The original hypothesis was killed:**
  - the spacing-ratio signal at the top edge of the QK spectrum did not move consistently (down in 3 of 6 seeds,
    up in 3);
  - it moved more in the control, where copying is impossible.
- **What held (registered in advance, tested on 6 fresh seeds):** the QK spectrum's top singular value, relative to
  the mean, briefly **dips** at the start of copying.
  - It dipped by 1.12–1.53 in 6 of 6 copying runs, and by 0.00 in 6 of 6 controls.
  - The dip came before the halfway point of learning in 6 of 6 seeds.
  - It is **not** an early warning: its lowest point fell on the onset of copying, not before it (only 1 of 6
    seeds was earlier).

All of this is **self-tested**: one AI designed, ran and graded it. Nothing has been independently reproduced.

## Files

| Path | What |
|---|---|
| `weights/repeat_seed{1..12}.safetensors` | trained on BOS + segment + the same segment (copying learnable) |
| `weights/norepeat_seed{1..12}.safetensors` | control: the second segment is independent (nothing to copy) |
| `metrics/all_runs.json`, `metrics/partB_runs.json` | every checkpoint (every 20 steps): ICL score, edge spacing ratio, top_norm, stable rank |
| `tinyih.py`, `rmt037.py` | model, data and measurement code (needs torch, numpy, scipy) |
| `analyze.py`, `dip.py` | the registered analyses |
| `config.json` | architecture and training settings |

Seeds 1–6 are part A; seeds 7–12 are part B. Only final weights are saved. The per-checkpoint statistics are in
`metrics/`.

## Model and training

- **Architecture:** 2 layers, 2 heads per layer, d_model 256, pre-LayerNorm, no MLPs, learned position embeddings.
- **Data:** vocabulary of 64 tokens; sequences of 65 tokens.
- **Training:** AdamW at learning rate 3e-5, batch 64, 2,000 steps, on CPU. It is deterministic: a rerun of seed 1
  was identical.

```python
from safetensors.torch import load_file
from tinyih import TinyAttnOnly, CFG
m = TinyAttnOnly(CFG)
m.load_state_dict(load_file("weights/repeat_seed7.safetensors"))
m.eval()
```

## Limits

- **Scale:** toy scale, synthetic data, one architecture.
- **Mechanism:** these models learned a positional shortcut, not induction.
- **Novelty:** not established. Spectral signals around induction-head formation are already reported for
  activations (arXiv 2605.24059).

## Provenance

AI participation: Claude (Anthropic, Opus 5.5) designed the study, wrote the code, trained the models and wrote this
card → human validation: not performed → human editing/curation: direction by Chad Holland, 2026-11-16 → human
responsibility: Chad Holland. Review level: direction only.
