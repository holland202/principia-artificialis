# QFI-001 Q1 results: the reference code reproduces the closed forms after a verdict-code fix; the first registered run said FAIL

**Status:** development run, SELF-TESTED by Claude, who wrote the code. The blind cases (Q2, ChatGPT, `9f5f2897…7147a`)
have not run. Linux container CPU, NumPy 2.5.3. S25 NOT VALIDATED. Registration:
[Q1_PREREG.md](Q1_PREREG.md) (`bc44b2e`), Amendment 1 (`0f01126`), Amendment 2 (`088c544`). Authority: Chad
Holland on PR #181, comment 7161037126, under the delegation in comment 7141782954.

## What could have gone wrong, first

1. **The first registered run gave VERDICT FAIL** ([`q1_run.txt`](../../results/qfi_001/q1_run.txt), code `ccf805d`,
   SHA-256 `d980b3ba…48b0`). Every printed case met its threshold. The verdict code rejected C5, C6 and C7
   anyway. The pass counters become `numpy.int64`, so the comparisons give `numpy.bool_`. The fail-closed test
   `ok.get(k) is True` is False for `numpy.bool_`. The defect was already in `e439899`. It failed closed, so it reported
   a pass as a failure, never the other way round. **Fix:** `e35b744` casts every check to a Python `bool`. No
   threshold, case or measurement changed. The rerun's measurement lines are byte-identical to the first run's.
   The PASS below is a post-fix rerun, not the first registered verdict.
2. **Self-tested.** Claude wrote the registration, the code and this file. ChatGPT found the tie defect (note
   `qfi001/chatgpt/006`) and refuted Claude's first repair (note `qfi001/chatgpt/008`). Neither ChatGPT nor any human
   has run this code.
3. **C10 has no sabotage switch.** It guards against the withdrawn note-007 grouping rule, which Claude showed
   erases the rotation in a scratch reproduction (Amendment 2). The code never contains that rule, so C10 passes under
   both switches.
4. **The Q2 blind cases were written for `e439899`.** The tie fix changed the code under them.

## Raw output after the fix ([`q1_rerun.txt`](../../results/qfi_001/q1_rerun.txt), code `e35b744`, SHA-256 `b29f72a4…66ce`, verbatim)

```
C1 qubit rotation: F_Q=0.360000000000 F_C=5.800e-34 F_R=0.360000000000 F_C^fd=3.852e-21 (expect 0.36, 0, 0.36)
C2 commuting: F_Q=1.095899531823 F_C=1.095899531823 F_R=0.000e+00 Var_p(a)=1.095899531823 F_C^fd=1.095899531697
C3 pure qubit: F_Q=4.000000000000 F_C=4.749e-35 F_R=4.000000000000 (expect F_Q = 4)
generated inputs: 200 families, d=4; eigenvalue min 0.0030 max 0.9177; F_Q range 0.4369..15.4055; F_R/F_Q share min 0.0377 median 0.8601 max 0.9999
C4 measurement FI <= F_Q + 1e-9: violations 0 of 10000; worst (FI - F_Q) -1.399e-01
C5 SLD basis attains F_Q (rel < 1e-8): 200 of 200; worst rel 2.372e-15
C6 Bures d^2/delta^2 vs F_Q/4 (rel < 1e-3): 200 of 200; worst rel 1.630e-04
C7 F_Q = F_C + F_R (abs < 1e-10, bookkeeping): 200 of 200; worst abs 3.553e-15
near_tie flags (min gap <= 1e-06) among the 200 families: 0
C8 eligible (min eigengap > 1e-3): 196 of 200 (floor 150); need 192 per half
C8 F_C vs F_C^fd (rel < 1e-4): 196 of 196; worst 5.169e-09
C8 F_R vs F_Q - F_C^fd (rel < 1e-4): 196 of 196; worst 3.804e-10
C8 C1 F_C^fd < 1e-8: True; C2 |F_C^fd - Var| < 1e-6: True
C9 exact tie: F_Q=0.080000000000 F_C=0.080000000000 F_R=1.322e-32 tied=2 (expect 0.08, 0.08, 0)
C9 basis invariance over 20 in-block unitaries: worst abs difference 1.249e-16 (< 1e-10)
C10 near tie: F_Q=0.040000000000 F_C=0.000e+00 F_R=0.040000000000 near_tie=True min_gap=2.000e-09 (expect 0.04, 0, 0.04, True)
VERDICT PASS
```

## Cases

| Case | Required | First run (`ccf805d`) | After fix (`e35b744`) | `--sabotage` | `--no-tie-fix` |
|---|---|---|---|---|---|
| C1 rotating qubit | 0.36, 0, 0.36 | PASS | PASS | **FAIL** (F_Q 0.225) | PASS |
| C2 commuting | F_Q = F_C = Var | PASS | PASS | PASS | PASS |
| C3 pure qubit | F_Q = 4 | PASS | PASS | **FAIL** (F_Q 2) | PASS |
| C4 measurement FI ≤ F_Q | 0 violations | PASS | PASS | FAIL (242) | PASS |
| C5 SLD attains F_Q | ≥ 195 | 200, reported **FAIL** | PASS | **FAIL** (0) | PASS |
| C6 Bures ≈ F_Q/4 | ≥ 195 | 200, reported **FAIL** | PASS | FAIL (0) | PASS |
| C7 bookkeeping | 200 | 200, reported **FAIL** | PASS | PASS | PASS |
| C8 independent split | eligible ≥ 150; ≥ 192 of 196 | PASS | PASS | PASS | PASS |
| C9 exact tie + invariance | 0.08, 0.08, < 1e-10 | PASS | PASS | PASS | **FAIL** (F_R 0.043) |
| C10 near tie (ChatGPT 008) | 0.04, 0, 0.04, flagged | PASS | PASS | PASS | PASS |
| Verdict | | **FAIL** | **PASS** | FAIL, exit 1 | FAIL, exit 1 |

Anti-vacuity holds as registered. `--sabotage` breaks C1, C3 and C5, and `--no-tie-fix` breaks C9.

## What this shows

The code computes the QFI, its eigenvalue and rotation parts, the SLD, the measurement Fisher information and the
Bures distance in agreement with closed forms and textbook inequalities on these cases. It also handles exact ties
without inventing rotation and without erasing rotation at near-ties. **That is a statement about code.** It says
nothing about models, activations or note #022's hypotheses.

## Open (M15)

- Q2: ChatGPT's sealed cases, on the commit ChatGPT names.
- Q3: feasibility on one small model. Q4 sets τ_flag from measured activation noise and reports how often ties occur.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) wrote the code, ran it and wrote this. The tie defect was found by
ChatGPT (OpenAI GPT-6, Codex), note 006, and the first repair was refuted by ChatGPT, note 008. Human validation: not
performed. Direction: Chad Holland, 2026-11-24 and 2026-11-25. Human responsibility: Chad Holland. Review level:
direction only.*
