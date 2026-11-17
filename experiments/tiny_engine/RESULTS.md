# TINY-ENGINE-001 results (run 2026-11-16)

**Status:** run as registered at `0b479db` ([REGISTRATION.md](REGISTRATION.md)), seeds 1–6. Self-tested.
**Q1 HELD (6/6). Q3 HELD (6/6). Q2 FAILED (1/6): exact copying does not extend reliably beyond the trained string
length. Q4 HELD.**

## Failure first

**Q2: copying a string twice as long as any trained string is unreliable.**

- At length 256, the copy string is 127 tokens; the longest trained copy string was 63.
- Copy accuracy was 0.529–0.767, and only seed 1 cleared the 0.70 threshold. So Q2 fails, even though pattern
  continuation and recall at that length passed in every seed.
- This matches the literature: exact copying beyond the trained length is a known weakness of rotary positions
  (arXiv 2607.16072 needs a 2-D variant to fix it).
- **Plain-language limit:** this model copies strings up to about 63 tokens perfectly, and longer ones only partly.

## What held

| Seed | Held-out periods @128 | Recall @128 | Copy @128 | Held-out periods @256 | Recall @256 | Copy @256 | Held-out periods @512 |
|---|---|---|---|---|---|---|---|
| 1 | 0.998 | 1.000 | 1.000 | 0.999 | 0.972 | 0.767 | 0.985 |
| 2 | 0.998 | 1.000 | 1.000 | 0.999 | 0.948 | 0.576 | 0.975 |
| 3 | 0.998 | 1.000 | 1.000 | 0.999 | 0.954 | 0.563 | 0.995 |
| 4 | 0.998 | 1.000 | 1.000 | 0.998 | 0.953 | 0.529 | 0.967 |
| 5 | 0.998 | 1.000 | 1.000 | 0.997 | 0.961 | 0.625 | 0.988 |
| 6 | 0.999 | 1.000 | 1.000 | 0.998 | 0.959 | 0.538 | 0.985 |

- **Q1 HELD (6/6):** at trained lengths, every seed continues never-trained pattern periods (0.998–0.999), recalls
  values (1.000) and copies (1.000).
- **Q3 HELD (6/6):** at 4× the longest training input, pattern continuation at never-trained periods stays at
  0.967–0.995.
- **Recall beyond training** (registered only as part of Q2): 0.948–0.972 at 2×, and 0.825–0.883 at 4× (reported,
  no threshold).
- **Q4 HELD:** an untrained model scores 0.007–0.010 on every test.
- **Size:** 165,120 parameters (0.66 MB in float32), trained in about 6 minutes per seed on 2 CPU cores.

**Demo with seed 1** (`demo_seed1.txt`):

- it continued a never-trained period-11 pattern after 300 tokens, with all 22 tokens correct;
- it looked up 40 of 40 values;
- it copied a 50-token string with 50/50 tokens correct.

**Disclosed:** seed 1 is used for the demo because it was the best on Q2. That is a selection, not a typical seed.

## What this does not show

- **Novelty:** these mechanisms are known (induction heads; relative positions helping length generalization). What
  is shown is a working three-skill model at 165K parameters.
- **Independence:** self-tested.
- **Determinism:** a rerun of a seed was not repeated for this experiment. The training code sets deterministic
  algorithms.
- **Real text:** the inputs are synthetic tokens. This is not a language model.

## Next (unrun)

- 2-D or position-coupled encodings for long-string copying.
- Halving the width under the same bar.
