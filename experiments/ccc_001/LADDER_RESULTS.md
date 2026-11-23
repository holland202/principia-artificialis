# CCC-001 LADDER results: nested layout models for the QORDER instruction shift

**Status:** RUN, 2 of 2 as registered. Development-only, SELF-TESTED, not blind. Registration
[LADDER_PREREG.md](LADDER_PREREG.md) committed alone at `536e49c` and pushed before the harness existed; run at
`b173d31`; outcome pinned in the commit that adds this file. **Date:** 2026-11-23.

## What could have gone wrong, first

- **Not independent.** Claude designed, coded, ran and reads this. ChatGPT's rules (`ccc-relay/chatgpt/032`, `034`)
  are design input, not review. No human checked any line.
- **Not blind.** All 27 cell means and the APEN contrasts were public before registration. P1 was disclosed as close
  to foregone and is the ladder's gate, not a discovery.
- **The rung order was chosen after the interaction patterns were seen.** The three-way comparison is descriptive,
  as agreed in 034.
- **Post-hoc, not registered:** the shares of total variance and of the R0 → R3 gap below come from
  `ladder_posthoc.py`, written after the run. They change no verdict.
- **Held-out means item-to-item** within 24 development items sharing one instruction, one format and 36 layouts.
  Nothing here is generalization to new prompts, and nothing here can confirm CCC-001.
- One small, unqualified model (Qwen2.5-1.5B-Instruct, as measured in QORDER). No deviation from the registration.

## Raw output

[`results/ccc_001/ladder_run.txt`](../../results/ccc_001/ladder_run.txt), pasted:

```
P0a rows 2592 (2592); max |pair sum of y| 2.85e-16 (<= 1e-9)
P0b centred ranks [6, 18, 26, 72] (want [6, 18, 26, 72]); columns [6, 18, 26, 108]
P0c 27 rebuilt cell means vs accbias.json: max |diff| 4.89e-07 (<= 1e-6)
P0d synthetic k=0: R0 rss 2.84e-29 mse 1.79e-32; R1 rss 3.84e-29 mse 2.94e-32; R2 rss 2.92e-29 mse 3.62e-32; R3 rss 4.08e-30 mse 1.24e-33
P0d synthetic k=1: R0 rss 3.91e+01 mse 1.51e-02; R1 rss 2.51e-28 mse 7.17e-32; R2 rss 3.64e-28 mse 7.71e-32; R3 rss 7.07e-30 mse 1.99e-33
P0d synthetic k=2: R0 rss 2.14e+01 mse 8.25e-03; R1 rss 7.65e+00 mse 2.95e-03; R2 rss 2.49e-28 mse 8.28e-32; R3 rss 5.47e-30 mse 2.19e-33
P0e identity E:=D: max |fitted| or MSE over 4 rungs 0.00e+00 (<= 1e-30)
P0 HELD rows, ranks, rebuild, synthetic and identity gate (a-e all required)
P1 HELD two-way beats additive held out: D01 +0.011175580 (> 0); items with D01(i) > 0: 16 of 24 (>= 13)
REPORT R0 additive: held-out MSE 0.126875646 RMSE 0.356196
REPORT R1 two-way: held-out MSE 0.115700066 RMSE 0.340147
REPORT R2 MxLxS: held-out MSE 0.108456292 RMSE 0.329327
REPORT R3 layout ceiling: held-out MSE 0.101093657 RMSE 0.317952
REPORT D01 (R0 - R1) +0.011175580 items +/-/tied 16/8/0
REPORT D12 (R1 - R2) +0.007243774 items +/-/tied 20/4/0
REPORT D23 (R2 - R3) +0.007362635 items +/-/tied 20/4/0
REPORT gain fraction F = D01 / (MSE0 - MSE2) = +0.011175580 / +0.018419353 = 0.606730
REPORT in-sample R0 additive: RSS 322.886857938 = layout part 82.233406474 + item part 240.653451465
REPORT in-sample R1 two-way: RSS 288.505501189 = layout part 47.852049724 + item part 240.653451465
REPORT in-sample R2 MxLxS: RSS 267.405687887 = layout part 26.752236422 + item part 240.653451465
REPORT in-sample R3 layout ceiling: RSS 240.653451465 = layout part 0.000000000 + item part 240.653451465
REPORT additive coefficients (all 24 items): meaning accept +0.085803 reject -0.083559 notenough -0.002245 | letter A -0.152549 B +0.044386 C +0.108163 | slot 1 +0.090954 2 -0.118363 3 +0.027409
VERDICT 2 of 2 as registered
DIGEST a69d1bfa561bdfe704dd135bafbaaccb77d01ab88c72e36dcd607544f6d393be
```

Sabotage ([`ladder_run_sabotage.txt`](../../results/ccc_001/ladder_run_sabotage.txt)): `P1 REFUTED ... D01
+0.000000000`, `VERDICT 1 of 2`, digest `7a75fe57…`, exit 1. With the pin, the plain run exits 0.

Post-hoc, not registered ([`ladder_posthoc.txt`](../../results/ccc_001/ladder_posthoc.txt)):

```
POSTHOC total sum of squares of y 387.102466408
POSTHOC R0 in-sample share of total SS explained 0.1659
POSTHOC R1 in-sample share of total SS explained 0.2547
POSTHOC R2 in-sample share of total SS explained 0.3092
POSTHOC R3 in-sample share of total SS explained 0.3783
POSTHOC R1 share of the R0 -> R3 gap: in-sample layout part 0.4181; held-out MSE 0.4335
POSTHOC R2 share of the R0 -> R3 gap: in-sample layout part 0.6747; held-out MSE 0.7144
```

## Predictions

| ID | Prediction | Outcome |
|---|---|---|
| P0 | Rows, ranks, rebuild, noiseless fixtures, identity | HELD |
| P1 | Two-way beats additive held out, D01 > 0 and ≥ 13 of 24 items | HELD (16 of 24; 8 items lose) |

## What this shows (this model, these items, these layouts)

- **Implementation:** the ladder can fit exactly, fail, or add nothing (P0d). Each rung fits its own fixture to
  ~1e-28 and misses the richer fixtures.
- **Empirical, descriptive:** every rung predicts held-out items better than the one below it. Absolute reductions:
  D01 `+0.011176` (16 of 24 items), D12 `+0.007244` (20 of 24), D23 `+0.007363` (20 of 24). F = `0.606730`: the
  two-way rung captures about 61% of the saturated rung's held-out gain over additive. So the three-way term is not
  negligible, and the layout beyond the M × L × S table (where the other answers sit) adds about as much again.
- **The item part dominates.** In-sample, 240.65 of the additive rung's 322.89 residual is item-to-item variation
  within layouts, which no layout model can reach. Post-hoc: even the layout ceiling explains `0.3783` of the total
  sum of squares. Held-out RMSE stays between `0.356196` and `0.317952` probability points.
- **Not shown:** why. Token identity and alphabetical rank are not separated. The 8 items where two-way loses were
  not examined.

## Open door (M15)

Not run: the ladder on the GPU7B stage Q outputs, and which item features carry the item part. Neither is
registered.

## Credit and provenance (M13)

The question behind CCC-001 is Federico Talens-Alesson's; crediting him implies no endorsement or validation by
him. Design: Claude (Anthropic, Opus 5.5) and ChatGPT (OpenAI) in the relay (PR #172, turns 031–034). Code, run and
this file: Claude, fresh scheduled session. Human validation: not performed. Human responsibility: Chad Holland.
Review level: none.
