# TINY-ENGINE-004 results: position coupling fixes repeats but costs the other skills (run 2026-11-20)

**Status:** run as registered at `b2c32ad` ([REGISTRATION_004.md](REGISTRATION_004.md)), seeds 21–26, three arms.
Self-tested. **P4 FAILED; P1, P2, P3, P5 and P6 HELD.** Coupling, isolated from its hint, solved copying with heavy
repeats. But in 4 of 6 seeds it broke the version 2 bar on pattern continuation and look-up. **Version 3 stays the
released model;** no version 4 is published.

Raw output: [`results/tiny_engine/004/`](../../results/tiny_engine/004/) (`score.txt`, `ranges.txt`, per-seed JSON,
run logs, weight hashes).

## Failures first

1. **P4 FAILED (2 of 6 seeds; needed 5).** Coupled models (arm C) fell below the version 2 bar on the tasks coupling
   does not touch. Seeds 21–24 failed on held-out patterns (0.9325–0.9491 at 128–512 tokens, bar 0.95) and on look-up
   (0.8202–0.9441 at 256–512 tokens; 0.8165–0.8760 at 1,024 tokens). Only seeds 25 and 26 passed.
2. **The exploration seed misled me.** Seed 903 met the bar (held-out periods at 1,024 exactly 0.9900), so I
   registered P4 expecting it to hold. Six seeds show it usually does not. One exploration seed was too few to
   predict this.
3. **Seed 26 collapsed on long distinct copies written freely:** 0.04 exactly right at 127 tokens, against 0.86–0.99
   for version 3 (arm A) on the same seeds. Its per-token score on the same test was 0.9792, so the drop comes from
   errors compounding while it writes.
4. **The answer label alone (arm B) damaged almost everything.** B scored 0.1472–0.1679 on 8-symbol copies at 127
   tokens (A: 0.5242–0.7228) and 0.1372–0.6605 on distinct copies at 1,024 tokens (A: 0.9989–0.9999). P5 predicted
   the direction and held, but the size of the damage was not predicted.
5. **Self-tested; Linux CPU only; S25 NOT VALIDATED.** The 18 runs were interrupted once at 4 of 18 (the session
   stopped background jobs while idle) and resumed. Completed seeds were kept, and the rest trained from scratch.

## Registered verdicts (`score.txt`)

```
tf_alpha8_k127 21:A0.524/B0.151/C0.983 22:A0.686/B0.158/C0.999 23:A0.708/B0.168/C1.000 24:A0.679/B0.153/C1.000 25:A0.685/B0.153/C1.000 26:A0.723/B0.147/C0.971
free_alpha8_k63 21:A0.000/B0.000/C0.880 22:A0.000/B0.030/C1.000 23:A0.000/B0.000/C1.000 24:A0.000/B0.000/C0.990 25:A0.000/B0.000/C1.000 26:A0.000/B0.020/C1.000
tf_alpha8_k127_uncoupled 21:A0.524/B0.151/C0.151 22:A0.686/B0.158/C0.122 23:A0.708/B0.168/C0.131 24:A0.679/B0.153/C0.134 25:A0.685/B0.153/C0.118 26:A0.723/B0.147/C0.140
P1 C>B tf_alpha8_k127 (coupling isolated): HELD (6/6 seeds; need 5)
P2 C tf_alpha8_k127 >= 0.95: HELD (6/6 seeds; need 5)
P3 C free_alpha8_k63 >= 0.50: HELD (6/6 seeds; need 5)
P4 C meets the 002 bar: FAILED (2/6 seeds; need 5)
P5 B<A tf_alpha8_k127 (label alone hurts): HELD (6/6 seeds; need 5)
P6 C uncoupled tf_alpha8_k127 < 0.50: HELD (6/6 seeds; need 5)
```

**P7** (anti-vacuity) was checked before the run: untrained models score below 0.05 (`test_eval3.py`), and
`test_eval4.py` shows the scorer can return both HELD and FAILED.

## Ranges over six seeds (`ranges.txt`)

| Test | A (version 3) | B (+ label) | C (+ label + coupling) |
|---|---|---|---|
| Teacher-forced copy, 8 symbols, 127 tokens | 0.5242–0.7228 | 0.1472–0.1679 | **0.9709–0.9998** |
| Whole 8-symbol 63-token copy written freely | 0.0000–0.0000 | 0.0000–0.0300 | **0.8800–1.0000** |
| Whole 32-symbol 63-token copy written freely | 0.1400–0.6400 | 0.0100–0.2400 | **0.9800–1.0000** |
| Whole distinct 127-token copy written freely | 0.8600–0.9900 | 0.0000–0.0000 | 0.0400–1.0000 |
| Held-out periods, 1,024 tokens | 0.9943–0.9998 | 0.9165–0.9873 | 0.9466–0.9871 |
| Look-up, 1,024 tokens | 0.9998–1.0000 | 0.8250–0.9993 | 0.8165–0.9998 |
| C with coupling switched off at test time (P6) | — | — | 0.1176–0.1513 |

Parameters: A 165,120; B and C 165,376.

## What this supports

- **Coupling itself causes the repeat fix.** C beat B in 6 of 6 seeds with the same parameters, label and starting
  weights. Switching coupling off at test time drops C to 0.1176–0.1513 (P6), so the trained model depends on the
  coupled ids.
- **It is not free.** In this 165K-parameter, 2-layer model, adding the label and coupling degraded pattern
  continuation and look-up in most seeds.
- **Why it costs the other skills is not tested here.** One question to test: the coupled ids change what the
  shared rotary layer 0 sees on copy rows, and the same layer serves the other tasks.

## Decision

Version 3 remains the released model and the browser demo. Version 4 weights are hashed in `SHA256SUMS_weights.txt`,
kept out of Git, and not published.

## Next (unrun)

- **Coupling without the label:** B shows the label alone is harmful. C without it isolates whether the label causes
  C's damage to other skills.
- **Keep the old ids for some heads:** give coupled ids to one layer-0 head only, so the other keeps ordinary
  positions for patterns and look-up.
- **Phone measurement on the S25** of version 3.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, ran and wrote this → human validation: not performed → human
editing/curation: direction by Chad Holland, 2026-11-20 → human responsibility: Chad Holland. Review level: direction
only.*
