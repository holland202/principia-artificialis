# TINY-ENGINE-003 results: training on repeated symbols (run 2026-11-20)

**Status:** run as registered at `f53eec6` ([REGISTRATION_003.md](REGISTRATION_003.md)), paired seeds 11–16.
Self-tested. **P1–P5 all HELD.** Training half of the copy examples on repeated-symbol strings (arm B, `CFG3`) beat
version 2 (arm A, `CFG2`) on the registered tests, at the same size and with the version 2 bar still met.

Raw output: [`results/tiny_engine/003/`](../../results/tiny_engine/003/) (`score.txt`, `ranges.txt`, per-seed JSON,
run logs, weight hashes).

## Failures and limits first

1. **Free-running copies of strings with heavy repeats still fail completely.** With an 8-symbol alphabet, no
   63-token copy was exactly right when the model wrote it alone: 0.00 in every seed of both arms. Teacher-forced
   accuracy rose, but not enough for long exact answers.
2. **Seed 16 of arm B went backwards on the main free-running test.** Its whole-copy rate on distinct 127-token
   strings was 0.68, below arm A's 0.90 on the same seed. It was also the weakest arm B seed on 8-symbol copies at
   127 tokens (0.568). P2 held at the minimum, 5 of 6.
3. **The limit I registered held (P4).** Arm B stayed below 0.90 on 8-symbol copies at 127 tokens in all six seeds
   (0.5680–0.7018). This is consistent with a 2-layer, 2-head model not matching enough context to copy long strings
   whose symbols repeat. That reading is not tested here.
4. **My exploration prediction E1 was refuted.** I expected version 2 to score below 0.50 on 8-symbol copies at 63
   tokens. It scored 0.6886 in exploration and 0.6546–0.6891 here.
5. **Self-tested.** Claude designed, ran and graded it. Nothing is independently reproduced. Linux container CPU only;
   S25 NOT VALIDATED.

## Registered verdicts (`score.txt`)

```
tf_alpha8_k63 11:A0.665/B0.834 12:A0.663/B0.868 13:A0.655/B0.852 14:A0.670/B0.857 15:A0.689/B0.855 16:A0.665/B0.821
tf_alpha8_k127 11:A0.467/B0.680 12:A0.472/B0.702 13:A0.455/B0.701 14:A0.473/B0.684 15:A0.499/B0.699 16:A0.474/B0.568
free_distinct_k127 11:A0.840/B0.940 12:A0.860/B0.970 13:A0.750/B1.000 14:A0.710/B0.990 15:A0.710/B0.990 16:A0.900/B0.680
P1 B>A tf_alpha8_k63: HELD (6/6 seeds; need 5)
P2 B>A free_distinct_k127: HELD (5/6 seeds; need 5)
P3 B meets the 002 bar: HELD (6/6 seeds; need 5)
P4 B tf_alpha8_k127 < 0.90: HELD (6/6 seeds; need 5)
```

**P5** (anti-vacuity) was checked before the run by `test_eval3.py`. An untrained model scores below 0.05 on every
new test, an exact-copy oracle scores 1.0, and off-by-one oracles score below 0.5 (teacher-forced) and 0.0
(free-running).

## Ranges over six seeds (`ranges.txt`)

| Test | Arm A (version 2) | Arm B (003) |
|---|---|---|
| Teacher-forced copy, 8 symbols, 63 tokens | 0.6546–0.6891 | **0.8214–0.8679** |
| Teacher-forced copy, 8 symbols, 127 tokens | 0.4548–0.4995 | 0.5680–0.7018 |
| Teacher-forced copy, 32 symbols, 127 tokens | 0.8789–0.9181 | 0.9464–0.9793 |
| Teacher-forced copy, distinct, 127 tokens | 0.9972–0.9989 | 0.9970–0.9999 |
| **Free-running whole copy, distinct, 127 tokens** | 0.7100–0.9000 | **0.6800–1.0000** (5 seeds ≥ 0.94) |
| Free-running whole copy, 32 symbols, 63 tokens (descriptive) | 0.1200–0.1800 | 0.4600–0.5800 |
| Free-running whole copy, 8 symbols, 63 tokens (descriptive) | 0.0000–0.0000 | 0.0000–0.0000 |
| Held-out periods, 1,024 tokens | 0.9940–0.9983 | 0.9944–0.9995 |
| Recall, 1,024 tokens | 0.9997–1.0000 | 0.9995–1.0000 |

## What this supports

- On these fixed cases, one cheap data change, at the same 165,120 parameters, raised repeated-symbol copying and made
  long free-running distinct copies exactly right more often in 5 of 6 seeds.
- It does not show why. The free-running gain on *distinct* strings, a task both arms trained on equally, is the
  least expected result. One untested guess: harder copy training makes the content match sharper. That is a
  question, not a finding.

## Next (unrun)

- **Why did distinct-string copying improve?** Compare attention sharpness of layer 1 between arms on the same seed.
- **Heavy repeats:** a third layer, or an exact-copy tool for agent use with neural copying measured separately.
- **Phone measurement on the S25:** cached generation, latency, memory.
- **Release:** the 12 weight files are hashed in `SHA256SUMS_weights.txt` and kept out of Git, as with version 2.
  Uploading arm B to Hugging Face is a separate step.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, ran and wrote this → human validation: not performed → human
editing/curation: direction by Chad Holland, 2026-11-20 → human responsibility: Chad Holland. Review level: direction
only.*
