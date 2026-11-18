# TINY-ENGINE-002 registration: fixing long-string copying

**Status:** REGISTERED, NOT RUN on seeds 1–6. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-17). Design and code: Claude (Anthropic, Opus 5.5). Human review level:
direction only.

## Why

TINY-ENGINE-001 ([RESULTS.md](RESULTS.md)) failed Q2. Copying a 127-token string, twice the longest trained, scored
0.529–0.767.

**Diagnosis (exploration, `diagnose.py`, seeds 1 and 2 of 001):**

| String length | Copy accuracy |
|---|---|
| up to 72 tokens | 1.00 |
| 80–112 tokens | 0.89–0.99 |
| 127 tokens | 0.77 and 0.59 |

The trained maximum was 63 tokens. Accuracy falls with copy distance beyond what training covered. That fits the
second layer's content match depending on rotary position: the layer that finds "where did this token appear before?"
was also seeing how far back, and had never seen distances that large.

## The fix (frozen at this commit: `engine.CFG2`)

- **Layer 1 gets no positional encoding at all.** This is the content-matching layer.
- **Layer 0 keeps rotary positions.** It needs order to look one token back.
- Everything else is unchanged: 165,120 parameters, same tasks, same training.

**Exploration (seed 900 only, `explore2.py`, C-EXPLORE)**, compared with 001's exploration seed:

| Arm | Copy @256 | Copy @512 | Recall @512 |
|---|---|---|---|
| **Fix: content-only layer 1** | **0.999** | **0.998** | **1.000** |
| Partial rotary (half of each head position-free) | 0.933 | 0.925 | 0.995 |

At 4× length, 001's exploration seed scored copy 0.725 and recall 0.843.

## Pass bar (all thresholds per seed; ≥ 5 of 6 seeds)

| ID | Length | Held-out periods | Recall | Copy |
|---|---|---|---|---|
| Q1 | 128 (trained) | ≥ 0.95 | ≥ 0.95 | ≥ 0.95 |
| Q2 | 256 (2×) | ≥ 0.95 | ≥ 0.95 | **≥ 0.95** (was ≥ 0.70 in 001, and failed) |
| Q3 | 512 (4×) | ≥ 0.95 | ≥ 0.95 | ≥ 0.95 |
| Q4 | **1024 (8×), never measured on any model before this commit** | ≥ 0.90 | ≥ 0.90 | — |
| Q5 | anti-vacuity: untrained model < 0.05 on every test | | | |

- **Q5 already measured:** the untrained model scores 0.006–0.010 on every test (`results/tiny_engine/002/q5_untrained.txt`).
- **Copy at 1024 is reported but not registered.** The vocabulary caps copy strings at 127 distinct tokens, so the
  string at 1024 is no longer than at 256.

**Seeds:** 1–6. Same seeds as 001, so each seed compares like with like.

## Prior work

Mixing rotary and no-position layers is a known design, for example in Yang et al., "Rope to Nope and Back Again: A
New Hybrid Attention Strategy" (Cohere; arXiv 2501.18795, NeurIPS 2025). This applies it to a 165K-parameter
in-context model. It is not a new idea.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) → human validation: not performed → human editing/curation:
direction by Chad Holland, 2026-11-17 → human responsibility: Chad Holland. Review level: direction only.*
