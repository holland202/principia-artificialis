---
license: mit
library_name: pytorch
tags:
  - tiny-model
  - in-context-learning
  - induction-heads
  - rotary-embeddings
  - research
---

# tiny-engine-165k: 165,120 parameters that learn from their context

This is a very small transformer, **0.66 MB**, trained from scratch on a laptop-class CPU in about 6 minutes. It
does three different things using only what is in its input:

| Skill | At trained lengths | Beyond trained lengths |
|---|---|---|
| **Continue a repeating pattern**, including pattern lengths it never saw | 0.998–0.999 | 0.967–0.995 at **4× longer** inputs |
| **Look up a value** from key–value pairs given earlier | 1.000 | 0.948–0.972 at 2×, 0.825–0.883 at 4× |
| **Copy a string exactly** | 1.000 (up to 63 tokens) | 0.53–0.77 for 127-token strings: **the known weak spot** |

These are results across 6 independently trained seeds, against a pass bar
[written before training](https://github.com/holland202/principia-artificialis/blob/exp/tiny-engine-001/experiments/tiny_engine/REGISTRATION.md).
An untrained copy of the model scores about 0.01 on every test.

**Result: 2 of 3 registered criteria passed. Long-string copying failed and is reported, not hidden.**

## Try it

```bash
pip install torch safetensors numpy
python demo.py weights/engine_seed1.safetensors
```

Output:

```
1) continue a pattern of period 11 (never trained), after 300 tokens of context -> OK
2) look up 40 values from 40 key-value pairs given earlier: 40/40 correct
3) copy a 50-token string exactly: 50/50 tokens correct
```

Seed 1 is the best of the six on long copying; the other five weights are included.

## How it is built

- **Architecture:** attention-only (no MLPs), 2 layers × 2 heads, width 128.
- **Positions:** rotary (relative) positions, and no position embeddings. That is why it keeps working on longer
  inputs.
- **Output layer:** separate (untied). Tying it to the input embedding stopped learning completely in our tests.
- **Training:** a mix of three synthetic tasks over 128 content tokens; inputs of 32–128 tokens; AdamW at learning
  rate 1e-3, 6,000 steps.

## Honest limits

- **Not a language model:** it works on abstract tokens, not text.
- **Not a new mechanism:** induction heads, and relative positions helping them generalize, are known results
  (e.g. arXiv 2412.11459). This is a small, open, fully tested working instance of them.
- **Self-tested:** one AI designed, trained and graded it. It has not been independently reproduced.

## Files

| Path | What |
|---|---|
| `weights/engine_seed{1..6}.safetensors` | six independently trained models |
| `engine.py` | model, task generators, evaluation |
| `demo.py` | a quick hands-on test |
| `score.py` | applies the registered pass bar |
| `results/` | per-seed scores and the demo output |

## Provenance

AI participation: Claude (Anthropic, Opus 5.5) designed, built, trained and evaluated the model and wrote this card
→ human validation: not performed → human editing/curation: direction by Chad Holland, 2026-11-16 → human
responsibility: Chad Holland. Review level: direction only.
