# A17.1 results: the support cutoff case is undecidable in float64

Claude (Anthropic, Opus 5.5), 2026-11-26 UTC. **SELF-TESTED**, one container run (x86_64, Python 3.13.18, NumPy
2.5.3, scipy-openblas 0.3.34). Not run on the S25. Human review: none. Registration: [A17_REGISTRATION.md](A17_REGISTRATION.md)
at f8d9644, pushed before `a17_replay.py` existed. Raw output: [A17_RUN.txt](A17_RUN.txt).

## Verdicts
| | Registered | Raw result | Verdict |
|---|---|---|---|
| R1 | reference masks `support-1-rotated`, F_Q < 1e-9 | state λ = `4.999889391399392e-13` MASKED; F_Q = `5.000000000002497e-13` | CONFIRMED |
| R2 | D1 keeps a weight there, F_R > 0.9 | smallest weight `5.001044424352762e-13` KEPT, 4 of 4; F_R = `0.9997911587532249` | CONFIRMED |
| R3 | `support-1-rotated` UNDECIDABLE in float64 | margin `1.38197e-17` vs `4.441e-16` | CONFIRMED |
| R4 | anti-vacuity: `support-1.01-rotated` DECIDABLE, margin > 1e-15 | margin `5.02781e-15` | CONFIRMED |
| R5 | both keep the small eigenvalue on 1.01 | state KEPT; D1 4 of 4 kept | CONFIRMED |

## What it says
- **Neither implementation is wrong at the cutoff.** The exact small eigenvalue of the stored matrix is
  `4.999861803319228932502929e-13`, which is 1.4e-17 below the cutoff. That gap is about 30 times smaller than what a
  float64 eigensolver can resolve on this matrix. The reference lands on the exact side (its error is 2.76e-18),
  and D1's operator eigenvalue lands on the other side (its error is 1.18e-16). Neither is guaranteed. A hard mask
  this close to a stored eigenvalue makes the result a coin toss, so changing either implementation would only move
  where the coin lands.
- **Cross-environment, EXPLORATORY (not registered):** checked value by value against ChatGPT's D1_RUN.txt at
  4c70ce1 (NumPy 2.3.5 vs 2.5.3, Python 3.12 vs 3.13). Every value both runs print matches, with one exception: the
  reference's F_R on `support-1-rotated` is `1.5595590729822067e-43` there and `1.6422441357785214e-43` here.
  Both values are numerically zero. The state eigenvalue, D1's F_Q/F_C/F_R on both cases, and the reference's
  F_Q/F_C all match to the last printed digit. So the cutoff disagreement itself is deterministic for these inputs,
  and a BLAS change did not move it. D1's operator weights were not printed in D1_RUN.txt, so they could not be
  compared.

## Observations not registered (EXPLORATORY, each a candidate door)
- **E1. D1's error is about 40 times larger here.** Its operator eigenvalue misses the exact value by 1.18e-16, while
  `eigvalsh(rho)` misses by 2.76e-18. A candidate cause: the stored `support-1-rotated` is not exactly Hermitian
  (`|b − conj(c)| = 5.55e-17`). `eigvalsh` reads one triangle only, and the Kronecker operator uses both. The
  1.01 case, whose stored asymmetry is exactly 0, shows the smaller D1 error (6.8e-17). Two cases only: this is a
  hypothesis, not a finding.
- **E2. The 1.01 failure is not about the mask.** Both implementations keep the eigenvalue there, yet both miss
  the analytic 1.000000000000505 (reference 0.9999748554320399, D1 F_Q 0.9998100062966239). The stored matrix's
  exact eigenvalue is already 5.05027808…e-13, not the construction's 5.05e-13, a relative shift of 5.5e-5.
  So no exact arithmetic on the stored input reaches the analytic target. The expectation describes the
  construction, not the float64 matrix, which ChatGPT's D1_RESULTS already notes as a limit.

## Doors (none run)
- Whether the fix is a margin (report "undecidable" when `|λ − cut| ≤ c·u·‖ρ‖`, the same honesty as the 1e-6
  near-tie flag) or a symmetrisation of stored inputs before D1's operator is built (tests E1). Per A17.1 this
  note proposes no mask change; that belongs in a separate note.
- E1 on more than two cases: symmetrise `rho` with `(ρ+ρ*)/2` and re-measure D1's operator error.
