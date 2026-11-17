# TINY-ENGINE-002 results: long-string copying fixed (run 2026-11-17)

**Status:** run as registered at `e16e462` ([REGISTRATION_002.md](REGISTRATION_002.md)), seeds 1–6. Self-tested.
**All five registered criteria HELD, Q1–Q4 in 6 of 6 seeds.** The fix (no positional encoding in the second layer)
repaired TINY-ENGINE-001's failed criterion without changing the model's size.

Raw output is in [`results/tiny_engine/002/`](../../results/tiny_engine/002/).

## Failures and limits first

1. **One wrong token can derail a long answer when the model writes on its own.**
   - The registered score checks each next token with the true earlier tokens in place. When the model writes a
     whole answer itself, one mistake can throw off everything after it.
   - Descriptive measurement, not registered (`freegen.py`, 50 trials per test, `freegen_descriptive.txt`):

     | Free-generation test | Whole answer exactly right |
     |---|---|
     | Pattern, never-trained period 7 | 0.98–1.00 |
     | Pattern, never-trained period 19 | 0.96–0.98 |
     | Copy a 63-token string | 0.94–1.00 |
     | **Copy a 127-token string** | **0.66–0.84** |

   - The 127-token figure is roughly what about 0.998 per-token accuracy implies over 127 tokens.
   - In the single-example demo, seed 3 continued a period-19 pattern correctly for only 10/38 tokens, and seed 4
     copied 95/127 (`demo2_all_seeds.txt`).
2. **My first demo was unfair, and it scored 4/63.** The "facts, then 700 unrelated tokens, then questions" demo
   drew its filler from the same tokens as the keys. Every key reappeared in the filler next to a random token, so
   each question had no single right answer. With filler that never repeats a key, the same model scored 63/63
   (`demo_ambiguous_filler.txt`). The demo was corrected; the failed version is kept here.
3. **The fix is not new.** Mixing rotary and no-position layers comes from published work (arXiv 2501.18795).

## What held

| Seed | Patterns @128 / 256 / 512 / 1024 | Recall @128 / 256 / 512 / 1024 | Copy @128 / 256 / 512 |
|---|---|---|---|
| 1 | 0.998 / 0.999 / 0.999 / 0.996 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 0.996 / 0.997 |
| 2 | 0.998 / 0.999 / 0.998 / 0.997 | 1.000 / 0.999 / 0.999 / 0.999 | 1.000 / 0.999 / 0.998 |
| 3 | 0.999 / 0.999 / 0.999 / 0.995 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 0.998 / 0.997 |
| 4 | 0.998 / 0.999 / 0.999 / 0.996 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 0.999 / 0.999 |
| 5 | 0.999 / 0.999 / 0.998 / 0.997 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 0.998 / 0.998 |
| 6 | 0.998 / 0.999 / 0.998 / 0.996 | 1.000 / 1.000 / 1.000 / 1.000 | 1.000 / 0.998 / 0.998 |

Patterns use never-trained periods only. Lengths are in tokens; 128 was the longest training input.

- **Q1–Q3 HELD (6/6):** every skill ≥ 0.995 at the trained length, 2× and 4×.
- **Q2, the criterion that failed in 001:** copying a 127-token string now scores 0.996–0.999, against 0.529–0.767
  for the same seeds with the old design.
- **Q4 HELD (6/6):** at **8× the longest training input**, never measured before registration, pattern continuation
  scores 0.995–0.997 and recall 0.999–1.000.
- **Q5 HELD:** an untrained model scores 0.006–0.010 on every test.
- **Reproducible:** rerunning seed 1 gave identical scores and byte-identical weights (`determinism.txt`).
- **Demo** (`demo2_all_seeds.txt`, corrected version):
  - **63 facts, 700 unrelated tokens, then 63 questions:** 62–63 of 63 correct, at about 830 tokens of context.
  - **Period-19 pattern after 900 tokens:** 38/38 in five seeds; the sixth (seed 3) got 10/38, see limit 1.

## Size

165,120 parameters (0.66 MB in float32). About 10.5 minutes of training per seed on one CPU thread.

## Next (unrun)

- Lowering the free-generation error on long copies: train on longer copy strings, or add a check that re-reads
  the source.
- Halving the width under the same bar.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, ran and wrote this → human validation: not performed → human
editing/curation: direction by Chad Holland, 2026-11-17 → human responsibility: Chad Holland. Review level: direction
only.*
