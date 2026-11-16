# RMT-IH-001 part C results (run 2026-11-16)

**Status:** run as registered at `d161753` ([REGISTRATION_C.md](REGISTRATION_C.md)). Self-tested.
**The bar was missed: Q1 FAILED and Q2 FAILED, each 4 of 6 seeds against the 5 of 6 required. Q3 HELD.**

## Failures first

1. **Two of six seeds learned a weaker solution.** Seeds 3 and 6 reached:

   | Seed | Never-trained periods (Q1) | Transfer task (Q2) | Trained periods |
   |---|---|---|---|
   | 3 | 0.800 | 0.658 | 0.977 |
   | 6 | 0.804 | 0.679 | 0.982 |

   The bar was ≥ 0.90 on Q1 and ≥ 0.70 on Q2.
2. **Longer training does not fix it.** In an exploratory check (disclosed, seed 3 retrained for 6,000 steps), the
   seed stayed stuck:

   | Steps | Never-trained periods | Transfer task |
   |---|---|---|
   | 3,000 | 0.800 | 0.658 |
   | 4,500 | 0.797 | 0.651 |
   | 6,000 | 0.787 | 0.638 |

   Seed 3 has settled into a different, worse solution; it is not under-trained. The 3,000-step values matched the
   registered run exactly, which also confirms determinism.

## What worked

Seeds 1, 2, 4 and 5 learned real in-context copying:

| Seed | Trained periods | Never-trained periods (Q1) | Transfer task, unseen distances (Q2) |
|---|---|---|---|
| 1 | 0.998 | 0.968 | 0.830 |
| 2 | 0.999 | 0.966 | 0.816 |
| 4 | 0.999 | 0.955 | 0.813 |
| 5 | 0.999 | 0.962 | 0.846 |

**Q3 (anti-vacuity) HELD:** an untrained model scores 0.015 on the transfer task
([`q3_random_init.txt`](../../results/rmt_ih_001/partC/q3_random_init.txt)).

Raw output is in [`results/rmt_ih_001/partC/`](../../results/rmt_ih_001/partC/): `log.txt`, plus one JSON per seed
holding the final scores and spectral traces every 50 steps.

## Open

- Why do two in six random starts settle into a worse solution, and what training change makes all six succeed?
- The fix should be registered before it is run.
