---
license: mit
library_name: pytorch
tags:
  - tiny-model
  - in-context-learning
  - induction-heads
  - length-generalization
  - research
---

# tiny-engine-165k: 165,120 parameters that learn from their context

A very small transformer, **0.66 MB**, trained from scratch on a CPU. Using only what is in its input, it
**continues patterns, looks up facts and copies text**, and keeps working on inputs **8× longer** than anything it
trained on.

**Version 2 (2026-11-17)** fixed the one skill that failed in version 1: long-string copying. The original
version 1 files are still here (see Files).

## What it can do (version 2, 6 independently trained models)

| Skill | At trained length (128 tokens) | 2× longer | 4× longer | **8× longer (1,024 tokens)** |
|---|---|---|---|---|
| Continue a repeating pattern of a length it **never saw** | 0.998–0.999 | 0.999 | 0.998–0.999 | **0.995–0.997** |
| Look up a value from key–value pairs given earlier | 1.000 | 0.999–1.000 | 0.999–1.000 | **0.999–1.000** |
| Copy a string exactly | 1.000 | 0.996–0.999 (127 tokens, 2× the longest trained) | 0.997–0.999 | — |

- **Scoring:** each score is the share of next tokens predicted correctly with the correct earlier tokens in place.
- **Pass bar:** all 6 models met every threshold of a bar
  [written before training](https://github.com/holland202/principia-artificialis/blob/exp/tiny-engine-002/experiments/tiny_engine/REGISTRATION_002.md),
  including the 8× test, which had never been run on any model before the bar was set.
- **Untrained baseline:** an untrained copy scores about 0.01 on every test.
- **Reproducible:** retraining a model from the same seed gives byte-identical weights.

## Try it

```bash
pip install torch safetensors numpy
python demo2.py weights/engine2_seed1.safetensors
```

Every test in the demo uses inputs longer than any training input:

```
1) continue a pattern of period 19 (never trained) after 900 tokens: 38/38 tokens correct
2) learn 63 key->value facts, read 700 unrelated tokens, then answer all 63: 63/63 correct
3) copy a 127-token string exactly (2x the longest trained): 127/127 correct
```

## The fix

- **The cause:** in version 1, the layer that finds "where did I see this before?" also tracked how far back that
  was. It had only trained on distances up to 64, so copying fell apart on longer strings.
- **The change:** in version 2, that layer matches on content alone, with no positional encoding. The first layer
  keeps rotary positions, because it needs order to look one token back.
- **The effect:** copying a 127-token string went from 0.53–0.77 to 0.996–0.999, with the same 165,120 parameters.
- **Prior work:** this hybrid design comes from published work (Yang et al., "Rope to Nope and Back Again",
  arXiv 2501.18795).

## Honest limits

- **Free generation:** the scores above check each token with the correct earlier tokens in place. When the model
  writes a whole long answer by itself, one wrong token can derail the rest. Measured over 100 tries per test
  (`results/002/freerun_v1_v2.txt`):

  | Whole answer exactly right | Version 1 | Version 2 |
  |---|---|---|
  | Continue a pattern of a never-trained length (period 19) | 74–85% | **98–100%** |
  | Copy 63 tokens | 99–100% | 95–100% |
  | Copy 127 tokens | **0%** | **58–85%** |

  Version 2 is slightly worse than version 1 at 63-token copies, a small cost of the fix.
- **Not a language model:** it works on abstract tokens, not words.
- **Not a new mechanism:** induction heads and mixed position encodings are known. This is a small, open, fully
  tested working instance.
- **Self-tested:** one AI designed, trained and graded it. It has not been independently reproduced.

## Files

| Path | What |
|---|---|
| `weights/engine2_seed{1..6}.safetensors` | **version 2**: six independently trained models |
| `demo2.py`, `freegen.py`, `score2.py` | version 2 demo, free-generation test, registered pass bar |
| `results/002/` | version 2 scores, demo outputs, reproducibility check, diagnosis |
| `engine.py` | model, tasks and evaluation, for both versions (`CFG` = v1, `CFG2` = v2) |
| `weights/engine_seed{1..6}.safetensors`, `demo.py`, `score.py`, `results/seed*.json` | version 1, kept for the record |

## Architecture

- Attention-only (no MLPs), 2 layers × 2 heads, width 128.
- Layer 0 uses rotary positions; layer 1 uses no positions.
- Separate output layer.
- Trained on a mix of three synthetic tasks over 128 content tokens, with inputs of 32–128 tokens; AdamW,
  6,000 steps.

## Provenance

AI participation: Claude (Anthropic, Opus 5.5) designed, built, trained and evaluated the model and wrote this card
→ human validation: not performed → human editing/curation: direction by Chad Holland, 2026-11-16 and 2026-11-17 →
human responsibility: Chad Holland. Review level: direction only.
