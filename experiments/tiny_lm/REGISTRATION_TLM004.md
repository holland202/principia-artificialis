# TLM-004 registration: a 1,024-piece tokenizer instead of bytes, at the same size and compute

**Status:** REGISTERED, NOT RUN on seeds 41–42. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-21; he left the choice of the next experiment to Claude). Design and
code: Claude (Anthropic, Opus 5.5). Human review level: direction only.

## Question

The byte-level 1M model (TLM-002) sees 8,192 bytes per training step. A byte-level BPE tokenizer with 1,024 pieces
turns the same text into about 3.2× fewer units. **At about the same parameter count, the same number of steps and
the same batch of 32 × 256 units, does a token model predict held-out stories better, measured in bits per byte?**

**Not new:** subword tokenizers are standard; the TinyStories paper used a 50k-piece one. This tests the change in
our CPU setup, with the only change being the units.

## Arms

| Arm | Model | Parameters | Units | Weights |
|---|---|---|---|---|
| A | byte-level GPT, width 128, 5 layers, 4 heads (TLM-002) | 1,018,624 | bytes | TLM-002 seeds 21, 22 (already trained) |
| B | same GPT, width 120, 5 layers, 4 heads, 1,024-piece embedding | 989,520 | BPE-1024 tokens | seeds 41, 42 (new) |

- **Width 120 instead of 128** keeps B's parameters within 3% of A's: the larger embedding table would otherwise add
  98,304. This is a second, deliberate difference, chosen so a gain cannot come from extra parameters.
- **Same training:** AdamW lr 1e-3, betas 0.9/0.95, weight decay 0.1, 100 warm-up steps, cosine to zero, 6,250
  steps, clip 1.0, 2 threads. B sees 51,200,000 tokens, which is roughly 3.2× more text than A's 51,200,000 bytes.
  That more-text-per-step is the point of the change.
- **Arm A is not retrained.** Its weights come from TLM-002, trained with the same code and data. The confirmation is
  fresh for B only.

## The instrument (frozen at this commit)

- **Tokenizer (`tok.py`):** byte-level BPE, 1,024 pieces, trained on the first 20,000,000 bytes of the train slice;
  `<|endoftext|>` is one token. Saved as `results/tiny_lm/004/tok1024.json`. The 200 MB slice becomes 65,753,407
  tokens (3.189 bytes per token). The round trip is exact on the first 2,000 valid stories.
- **Common evaluator (`eval_common.py`):** the first 200 valid stories (159,776 bytes). Sliding windows of 256 units,
  stride 128, so every unit is scored once with at least 128 units of context (except at the very start). Bits are
  summed and divided by the text's byte count, for byte and token models alike.
- **Arm A under this evaluator** (`results/tiny_lm/004/baseline_rescore.txt`): **1.0812 (seed 21), 1.0648 (seed 22)**.
  These differ from TLM-002's registered numbers because the evaluator differs (more context per unit). For
  reference, the 3.2M byte model (TLM-003) scores 0.9917 here.
- **Anti-vacuity:** the same text with its characters in a fixed random order (`units_shuffled`). Byte model seed 22:
  10.6766. Token exploration model: 7.4629.

## Exploration (C-EXPLORE)

Seed 905, B's architecture, a 500-step schedule: 1.7566 bpb on the common text, 7.4629 shuffled. Generation checks:
85.59% real words, 0.46% copied spans. The words are visibly worse than the bytes' at this point ("huggedhed",
"veryortant"). Files in `results/tiny_lm/004/exploration/`.

## Registered predictions (each must hold in both seeds 41 and 42)

| ID | Prediction |
|---|---|
| P1 | **Tokens beat bytes beyond seed noise:** common-evaluator bpb < 1.0484, i.e. more than A's seed gap (0.0164) below A's better seed (1.0648) |
| P2 | Known-word rate ≥ 0.90 (`gencheck_tok.py`: same prompt, temperature, seeds and checks as `gencheck.py`) |
| P3 | Copied-span rate ≤ 0.20 |
| P4 | Shuffled-text bpb ≥ 4.0 |

- **Off-ramp:** if P1 fails, the tokenizer line stops, and the next step is publishing the 3.2M byte model.
- **Descriptive, no threshold:** B against the 3.2M byte model's 0.9917.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Yes: two runs in parallel, 1 thread each, about 2 hours. |
| Noise | Two seeds of B; P1's margin uses A's seed gap. |
| Statistics | No population claim; both seeds must pass. |
| Evidence | Numbers from the scripts' printed output, pasted verbatim. |
| Independence | No: SELF-TESTED. |
| External | TinyStories data (CDLA-Sharing-1.0); HF `tokenizers` 0.23.3. |
| Device | Linux container CPU only. S25 NOT VALIDATED. |
| Verdict code | Thresholds applied by hand to printed numbers. |
| Exploration | Yes: seed 905, disclosed. |
| Held-out | Yes: valid file never trained on (the tokenizer is trained on the train slice only); seeds 41–42 fresh. |
| Generated inputs | Same data as TLM-001..003; tokenizer round trip checked. |
| People's data | No. |
| Design | Two-arm comparison at matched parameters and steps; the arms differ in units and, by design, in width (120 vs 128). |

## Unrun door

- A tokenizer with a 3.2M model; a larger vocabulary.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, coded and wrote this → human validation: not performed →
human editing/curation: direction by Chad Holland, 2026-11-21 → human responsibility: Chad Holland. Review level:
direction only.*
