# TLM-002 results: trained 2.5× longer, the 1M model beats the refit n-gram rival (run 2026-11-21)

**Status:** run as registered at `d8955dc` ([REGISTRATION_TLM002.md](REGISTRATION_TLM002.md)), seeds 21–22.
Self-tested. **P1–P5 all HELD.**

Raw output: [`results/tiny_lm/002/runs/`](../../results/tiny_lm/002/runs/) (run logs and JSON, shuffled-valid checks,
generation checks, all 40 sampled stories, weight hashes).

## Failures and limits first

1. **The margin over the rival is small:** 0.0314 bpb (seed 21) and 0.0494 bpb (seed 22) below the n-gram's 1.1736.
   The rival was capped at order 8 because of how keys are packed (8 bytes into one int64). A higher-order or better
   smoothed n-gram might close the gap; that is untested.
2. **The stories are still not coherent.** Words and short phrases are right; the plots drift ("They heard a loud and
   forgot together."). All 40 samples are published to read.
3. **The loss had nearly flattened:** seed 21 went 1.1482 → 1.1422 over its last 750 steps, and seed 22 went
   1.1299 → 1.1242. More steps at this size would add little; capacity is now the likely limit (untested).
4. **TLM-001's main prediction (P1) failed at 20.5M bytes and is kept.** Both results together say this model needs
   roughly 50M bytes, not 20M, to pass this rival on this text.
5. **Self-tested; Linux CPU only; S25 NOT VALIDATED.**

## Registered verdicts

| ID | Prediction | Seed 21 | Seed 22 | Verdict |
|---|---|---|---|---|
| P1 | valid bpb < 1.1736 (n-gram refit on 60 MB, order 8) | 1.1422 | 1.1242 | HELD |
| P2 | known-word rate ≥ 0.90 | 0.9960 | 0.9948 | HELD |
| P3 | copied-span rate ≤ 0.20 | 0.0281 | 0.0451 | HELD |
| P4 | shuffled-valid bpb ≥ 4.0 | 10.5733 | 10.5605 | HELD |
| P5 | valid bpb ≤ 1.3133 | 1.1422 | 1.1242 | HELD |

Checks, verbatim:
```
s21 shufcheck: {"valid_bpb": 1.1422, "shuffled_valid_bpb": 10.5733}
s22 shufcheck: {"valid_bpb": 1.1242, "shuffled_valid_bpb": 10.5605}
s21 gencheck: {"words": 2224, "known_word_rate": 0.996, "spans": 249, "copied_span_rate": 0.0281, "valid_stories_reference": {"words": 3006, "known_word_rate": 1.0, "spans": 358, "copied_span_rate": 0.0782}}
s22 gencheck: {"words": 2295, "known_word_rate": 0.9948, "spans": 266, "copied_span_rate": 0.0451, "valid_stories_reference": {"words": 3006, "known_word_rate": 1.0, "spans": 358, "copied_span_rate": 0.0782}}
```

## TLM-001 vs TLM-002 (same model, same data slice)

| | Bytes seen | Valid bpb | Real words | Copied spans |
|---|---|---|---|---|
| TLM-001 (seeds 11, 12) | 20,480,000 | 1.3633 / 1.3698 | 0.9799 / 0.9701 | 0.0144 / 0.0318 |
| TLM-002 (seeds 21, 22) | 51,200,000 | 1.1422 / 1.1242 | 0.9960 / 0.9948 | 0.0281 / 0.0451 |
| Byte 8-gram rival | 30,000,000 / 60,000,000 | 1.2075 / 1.1736 | — | — |

## A sample (seed 21, story 5 of 20, unedited)

> Once upon a time, there was a boy. The cat was scared of the other side of the people on the boat. The cat said,
> "Hello, that was a race!" He said the bird with his friends finished the big bathtub and ran towards him. They all
> played together every day.

## What this supports

- With 51.2M bytes of training (about 2 hours on 2 CPU threads), a 1,018,624-parameter byte-level transformer predicts
  TinyStories text better than a byte 8-gram given more text, in both seeds. It writes real words (99.5%) and does
  not copy its training data (2.8–4.5% copied spans, against 7.8% for real held-out stories).
- Not shown: coherent stories, or any advantage over stronger non-neural baselines.

## Next (unrun)

- 3.2M parameters, to test whether capacity is now the limit.
- A stronger rival (n-gram above order 8, or better smoothing).
- Publish this model (seed 22) to Hugging Face and the browser Space.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, ran and wrote this → human validation: not performed → human
editing/curation: direction by Chad Holland, 2026-11-21 → human responsibility: Chad Holland. Review level: direction
only.*
