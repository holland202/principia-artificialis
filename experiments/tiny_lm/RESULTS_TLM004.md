# TLM-004 results: tokens beat bytes by a wide margin at the same size and compute (run 2026-11-21)

**Status:** run as registered at `99f677d` ([REGISTRATION_TLM004.md](REGISTRATION_TLM004.md)), seeds 41–42.
Self-tested. **P1–P4 all HELD.**

Raw output: [`results/tiny_lm/004/runs/`](../../results/tiny_lm/004/runs/) (logs, JSON, checks, all 40 samples,
weight hashes).

## Limits first

1. **The copied-span rate is now above real stories'.** 10.99% (seed 41) and 9.23% (seed 42) of generated 50-byte
   spans appear verbatim in the training text, against 7.82% for real held-out stories. That is within the
   registered bound (P3, ≤ 20%), but above the reference for the first time in this line. Whether it is
   memorisation or formulaic openings ("Once upon a time, there was a little girl named …" is common, and the prompt
   itself is inside the first span) is not tested.
2. **The arms differ in two ways, by design:** units (bytes vs tokens) and width (128 vs 120, to keep parameters
   within 3%). The width change costs the token model capacity, so it does not explain the gain. But the gain is
   strictly that of "this tokenizer at this width".
3. **Arm A was not retrained.** It is TLM-002's weights, rescored with the common evaluator before registration.
4. **Plots still wander**, though less than before (from reading the samples, not measured).
5. **Self-tested; Linux CPU only; S25 NOT VALIDATED.**

## Registered verdicts

| ID | Prediction | Seed 41 | Seed 42 | Verdict |
|---|---|---|---|---|
| P1 | common-evaluator bpb < 1.0484 | 0.8487 | 0.8571 | HELD |
| P2 | known-word rate ≥ 0.90 | 0.9963 | 0.9974 | HELD |
| P3 | copied-span rate ≤ 0.20 | 0.1099 | 0.0923 | HELD (above the real-story 0.0782; see limit 1) |
| P4 | shuffled-text bpb ≥ 4.0 | 9.9752 | 9.7513 | HELD |

Checks, verbatim:
```
seed 41: valid 0.8487 shuffled 9.9752
seed 42: valid 0.8571 shuffled 9.7513
t41 gencheck: {"words": 2404, "known_word_rate": 0.9963, "spans": 273, "copied_span_rate": 0.1099, "valid_stories_reference": {"words": 3006, "known_word_rate": 1.0, "spans": 358, "copied_span_rate": 0.0782}}
t42 gencheck: {"words": 2290, "known_word_rate": 0.9974, "spans": 260, "copied_span_rate": 0.0923, "valid_stories_reference": {"words": 3006, "known_word_rate": 1.0, "spans": 358, "copied_span_rate": 0.0782}}
```
Runs: 989,520 parameters, 51,200,000 tokens seen, 6,313 s and 6,317 s on 1 thread each (in parallel).

## Same text, same evaluator (bits per byte, lower is better)

| Model | Parameters | Units | bpb |
|---|---|---|---|
| TLM-002, seeds 21 / 22 | 1,018,624 | bytes | 1.0812 / 1.0648 |
| TLM-003, seed 31 | 3,215,872 | bytes | 0.9917 |
| **TLM-004, seeds 41 / 42** | **989,520** | **BPE-1024 tokens** | **0.8487 / 0.8571** |

The 1M token model beats the 3.2M byte model by 0.13–0.14 bpb, at under a third of the parameters and less
training time.

## A sample (seed 41, story 1 of 20, unedited)

> Once upon a time, there was a little boy named Tim. Tim loved to play with his toys. One day, he saw a little on
> the ground. He wanted to learn how to teach it to his friend, Lily. "Help!" Tim said. "Hi, Lily! I will buy this
> toy!" Lily said, "Me too! I want to play with you." They played with the toy and became friends. They played
> together every day, and Lily was very happy.

## What this supports

- At about 1M parameters and the same 6,250 steps of 32 × 256 units, a byte-level BPE-1024 tokenizer cut bits per
  byte by 0.21–0.22 against the byte model, in both seeds (the registered margin was 0.0164). Each step covers about
  3.2× more text, which on this CPU is the cheapest gain found so far.

## Next (unrun)

- Check whether the higher copied-span rate is memorisation (for example, exclude the prompt and count spans that
  occur in only one training story).
- The tokenizer with a 3.2M model.
- Publish the token model and add it to the browser demo (needs the tokenizer in JavaScript).

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, ran and wrote this → human validation: not performed → human
editing/curation: direction by Chad Holland, 2026-11-21 → human responsibility: Chad Holland. Review level: direction
only.*
