# TLM-001 results: the 1M story model loses to the n-gram rival, but writes real words (run 2026-11-21)

**Status:** run as registered at `aaf9b62` ([REGISTRATION_TLM001.md](REGISTRATION_TLM001.md)), seeds 11–12.
Self-tested. **P1 FAILED; P2, P3 and P4 HELD.**

Raw output: [`results/tiny_lm/001/runs/`](../../results/tiny_lm/001/runs/) (run logs and JSON, generation checks,
all 40 sampled stories, weight hashes).

## Failures first

1. **P1 FAILED in both seeds.** Valid bits per byte were 1.3633 (seed 11) and 1.3698 (seed 12). The best byte
   n-gram scored 1.2075 (order 8). After 48 minutes on 2 CPU threads (20,480,000 bytes seen), the 1,018,624-parameter
   transformer models this text worse than a counting model. The rival had more data and its order was picked on
   the evaluation bytes, so the gap is partly the rival's advantage. But the registered comparison is the
   comparison, and the transformer lost.
2. **The loss was still falling.** Seed 11's valid bpb went 1.4614 → 1.3866 → 1.3633 at steps 1500, 2000 and 2500,
   with the learning rate decaying to zero. A longer run might pass; that is untested.
3. **My anti-vacuity reasoning for P4 was wrong.** I expected an untrained model near uniform guessing (8.0 bpb). It
   scored 160.5915 and 166.1598. With a tied embedding and the default initialisation, its untrained logits are huge,
   so it is confidently wrong rather than unsure. P4 holds as worded (≥ 7.5), but not for the reason I gave.
4. **The stories are not coherent.** They are made of real words in plausible patterns, but the plots do not hold
   together ("The cat was very dog near the door, but Ben was not one know."). All 40 samples are published to
   read.
5. **Self-tested; Linux CPU only; S25 NOT VALIDATED.**

## Registered verdicts

| ID | Prediction | Seed 11 | Seed 12 | Verdict |
|---|---|---|---|---|
| P1 | valid bpb < 1.2075 | 1.3633 | 1.3698 | **FAILED** |
| P2 | known-word rate ≥ 0.90 | 0.9799 | 0.9701 | HELD |
| P3 | copied-span rate ≤ 0.20 | 0.0144 | 0.0318 | HELD |
| P4 | untrained valid bpb ≥ 7.5 | 160.5915 | 166.1598 | HELD (reason wrong; see failure 3) |

Generation checks, verbatim (`gencheck.py`):
```
seed 11: {"words": 1837, "known_word_rate": 0.9799, "spans": 208, "copied_span_rate": 0.0144, "valid_stories_reference": {"words": 3006, "known_word_rate": 1.0, "spans": 358, "copied_span_rate": 0.0782}}
seed 12: {"words": 1942, "known_word_rate": 0.9701, "spans": 220, "copied_span_rate": 0.0318, "valid_stories_reference": {"words": 3006, "known_word_rate": 1.0, "spans": 358, "copied_span_rate": 0.0782}}
untrained: {"words": 60, "known_word_rate": 0.6667, "spans": 400, "copied_span_rate": 0.0, ...}
```

## A sample (seed 11, story 3 of 20, unedited)

> Once upon a time there was an from the beach. He wanted to drive it and looking around the house. He could share
> his friendly cat and the blocks came button and wanted to play in the sail.

## What this supports

- At this budget, a 1M byte-level transformer learns spelling and common phrasing: 97–98% of its words are real,
  against 67% for an untrained model. It does not copy its training text: 1.4–3.2% of its 50-byte stretches appear
  verbatim, against 7.8% for real held-out stories.
- It does not beat a well-tuned byte 8-gram on prediction. Writing real words is not the same as modelling the text
  well.

## Next (unrun)

- **Longer training at 1M** (the loss had not flattened), registered against the same rival.
- **3.2M parameters** at about 2.7 hours.
- A word-piece tokenizer would put this closer to the TinyStories paper's setup.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, ran and wrote this → human validation: not performed → human
editing/curation: direction by Chad Holland, 2026-11-21 → human responsibility: Chad Holland. Review level: direction
only.*
