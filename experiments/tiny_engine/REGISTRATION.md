# TINY-ENGINE-001 registration: a 165,120-parameter model that learns from its context

**Status:** REGISTERED, NOT RUN on seeds 1–6. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-16). Design and code: Claude (Anthropic, Opus 5.5). Human review level:
direction only.

## Goal (engineering, pass/fail)

The goal is one very small model that does three different things using only what is in front of it:

- **continue a repeating pattern**, including pattern lengths it never trained on;
- **look up a value** from key–value pairs given earlier in the input;
- **copy a string exactly.**

It should keep working on inputs longer than any it trained on.

## Design (frozen at this commit, `engine.py`)

- **Model:** attention-only, 2 layers, 2 heads, d_model 128, with rotary (relative) positions and no position
  embeddings, and a separate output layer. **165,120 parameters**, 0.66 MB in float32.
- **Training:** a mix of the three tasks; input lengths 32/64/96/128; AdamW at learning rate 1e-3, batch 64,
  6,000 steps; loss only on predictable positions.
- **Held-out periods:** 7, 11, 15, 19 and 23 are never trained on.
- **Test lengths:** 128 (longest trained), 256 (2×) and 512 (4×). At 256 and above, the copy string is 127 tokens,
  twice the longest trained (63).
- **Seeds:** 1–6.

## Pass bar

| ID | Test | Thresholds (all must hold in a seed) | Seeds needed |
|---|---|---|---|
| Q1 | trained lengths (128) | held-out periods ≥ 0.95, recall ≥ 0.95, copy ≥ 0.95 | ≥ 5 of 6 |
| Q2 | 2× longer (256) | held-out periods ≥ 0.95, recall ≥ 0.90, copy ≥ 0.70 | ≥ 5 of 6 |
| Q3 | 4× longer (512) | held-out periods ≥ 0.90 | ≥ 5 of 6 |
| Q4 | anti-vacuity | an untrained model scores < 0.05 on every test | — |

**Q4 already measured** (untrained, seed 1): 0.007–0.010 on every test (`results/tiny_engine/q4_untrained.txt`).

## Exploration disclosed (seed 900, C-EXPLORE)

1. **Tied output layer: almost no learning.** The first version tied the output layer to the embedding, and learned
   almost nothing: 0.00–0.35 after 6,000 steps. In an ablation (`ablate.py`), RoPE d_model 256 periodic accuracy
   was 0.00 tied and 1.00 untied; untied d_model 128 also reached 1.00.
2. **Recall task was ambiguous.** Its first version let a key token also appear as a value. With keys and values
   from disjoint vocabulary halves, recall at length 128 went from 0.85 to 0.999.
3. **Final exploration run** (4,000 steps):

   | Length | Held-out periods | Recall | Copy |
   |---|---|---|---|
   | 128 | 0.998 | 0.999 | 1.000 |
   | 256 | 0.997 | 0.953 | 0.717 |
   | 512 | 0.994 | 0.843 | 0.725 |

   - **Copy beyond training length varied between runs:** 0.95 in one run and 0.72 in another. That is why Q2's
     copy threshold is 0.70.
   - The confirmatory runs use 6,000 steps, not 4,000.

## Novelty: not established

- **What is known:** relative positions are known to help induction heads keep working on longer inputs
  (arXiv 2412.11459). Copying with relative positions is studied too (arXiv 2607.16072).
- **What this run would add:** a working three-skill demonstration at 165K parameters, openly released. That is
  not a new mechanism.

## Unrun door

Pushing the size down (d_model 64, about 50K parameters) under the same bar.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) → human validation: not performed → human editing/curation:
direction by Chad Holland, 2026-11-16 → human responsibility: Chad Holland. Review level: direction only.*
