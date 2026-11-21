# TLM-001 registration: a 1M-parameter byte-level story model, against an n-gram rival

**Status:** REGISTERED, NOT RUN on seeds 11–12. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-21: "a 1M parameters build", "Tiny language model"). Design and code:
Claude (Anthropic, Opus 5.5). Human review level: direction only.

## Question

Can a 1.02M-parameter transformer, trained for about 40 minutes on 2 CPU cores, model TinyStories text better than
the simplest rival, a byte n-gram model, and write mostly real words without copying its training data?

**Not new.** The TinyStories paper (Eldan & Li 2023, arXiv 2305.07759) trained 1M–33M-parameter models on this data,
using a word-piece tokenizer and far more compute. This run is a small, open, CPU-only rebuild with registered
checks and a stated rival.

## Setup (frozen at this commit)

- **Data:** the first 209,715,200 bytes of `TinyStoriesV2-GPT4-train.txt` (license CDLA-Sharing-1.0) for training;
  `TinyStoriesV2-GPT4-valid.txt` for evaluation only. SHA-256 of both in `results/tiny_lm/001/DATA_SHA256.txt`.
- **Model (`gpt.py`):** byte-level (256 symbols), pre-LN, rotary positions, GELU MLP, tied embedding;
  width 128, 5 layers, 4 heads; 1,018,624 parameters (printed by code in each run's JSON).
- **Training (`train.py`):** 2,500 steps × 32 × 256 = 20,480,000 bytes seen (about 20 per parameter); AdamW
  (lr 1e-3, betas 0.9/0.95, weight decay 0.1), 100 warm-up steps, cosine decay, gradient clip 1.0.
- **Validation bits per byte (bpb):** the first 65,536 bytes of the valid file, in 256 fixed windows of 256.

## The rival (M14) and the instruments

- **n-gram rival (`ngram.py`):** interpolated absolute discounting (D = 0.75), orders 1–8. It is trained on the first
  30,000,000 bytes of the train slice, more than the transformer sees. Each valid byte is scored with the full
  preceding context in the valid stream, which is more context than the transformer's first window positions get.
  **The rival is the best of orders 1–8 on the same valid bytes.** Choosing its order on the evaluation set favours
  the rival. Already computed and seen (deterministic):

  ```
  order 1  valid bpb 4.4455   order 5  valid bpb 1.5034
  order 2  valid bpb 3.2946   order 6  valid bpb 1.3465
  order 3  valid bpb 2.3686   order 7  valid bpb 1.2535
  order 4  valid bpb 1.7982   order 8  valid bpb 1.2075
  ```
- **Generation checks (`gencheck.py`):** 20 stories sampled from the prompt "Once upon a time" (temperature 0.8,
  seeds 5000–5019, up to 1,000 bytes or the end-of-story marker).
  - *Known-word rate:* the share of generated words with 3 or more letters that occur anywhere in the train slice.
  - *Copied-span rate:* the share of generated 50-byte spans found verbatim in the train slice.
  - *Both directions shown:* 20 real validation stories score 1.0000 known and 0.0782 copied; an untrained model scores
    0.6667 known (60 words). So real text has some common 50-byte phrases, and random bytes still form some short
    "words".

## Exploration (C-EXPLORE: seen before registering)

Seed 901, a short 500-step schedule (4,096,000 bytes seen): valid bpb 2.1007, known-word rate
0.7488, copied-span rate 0.0000. Its samples look like English made of misspelled words ("Once upon a time the bird
hos eax."). This run used a shorter schedule than the registered one.

## Registered predictions (each must hold in both seeds 11 and 12)

| ID | Prediction | Seen so far |
|---|---|---|
| P1 | **Beats the rival:** valid bpb < 1.2075 (best n-gram, order 8) | 2.1007 at 500 steps (exploration) |
| P2 | Known-word rate ≥ 0.90 | 0.7488 at 500 steps |
| P3 | Not a copier: copied-span rate ≤ 0.20 (real held-out stories: 0.0782) | 0.0000 |
| P4 | Anti-vacuity: the untrained model's valid bpb ≥ 7.5 (uniform guessing = 8.0) | printed in each run's JSON |

- **P1 may well fail.** TinyStories is repetitive, and the 8-gram rival is strong. If it fails, the honest result is
  that 40 CPU-minutes of a 1M transformer do not beat a counting model on this text.
- **Verdict:** P1 and P4 from each run's JSON (`valid_bpb`, `untrained_valid_bpb`); P2 and P3 from `gencheck.py`
  output, pasted verbatim into the results.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Yes: 2 runs × about 40–60 minutes on 2 CPU threads; 20 generations each. |
| Noise | Two seeds; evaluation is deterministic. No variance claim. |
| Statistics | No population claim; both seeds must pass. |
| Evidence | Numbers come from the scripts' printed output, pasted verbatim. |
| Independence | No: Claude designed, ran and grades this. SELF-TESTED. The samples are published so people can read them. |
| External | TinyStories data and paper (CDLA-Sharing-1.0); the paper's numbers are not comparable (different tokenizer). |
| Device | Linux container CPU only. S25 NOT VALIDATED. |
| Verdict code | Thresholds applied by hand to printed numbers. Simple comparisons, stated above. |
| Exploration | Yes: seed 901, disclosed. |
| Held-out | Yes: the valid file is never trained on; training seeds 11–12 are fresh. |
| Generated inputs | Yes: the data are AI-written stories (GPT-4); 600 bytes were looked at before registering. |
| People's data | No personal data. |
| Design | Comparison to one fixed rival; supports "this model, this budget, this text". |

## Unrun door

- The same budget at 3.2M parameters.
- The model in the browser Space, next to the tiny engine.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, coded and wrote this → human validation: not performed →
human editing/curation: direction by Chad Holland, 2026-11-21 → human responsibility: Chad Holland. Review level:
direction only.*
