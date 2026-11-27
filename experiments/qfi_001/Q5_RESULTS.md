# QFI-001 Q5 results: development run (dev pairs only)

**Status:** RUN. **INFEASIBLE as registered** (first failure: the feasibility rule at trained layer 0). VERDICT 4 of 5
as registered (P1 REFUTED; P2, P3, P6, P7 HELD). Q6 waits for an amendment registration (Q4_PREREG, "Q5"). No test pair
has been loaded. F_R is not interpreted: ChatGPT's D1 agreement on the interchange subset is not posted yet.

**Authority:** Chad Holland's delegation, PR #181 comment 7141782954. **Registration:** `Q4_PREREG.md` (`23679c2`),
`Q4_AMENDMENT1.md` (`d9337c3`), `Q4_AMENDMENT2.md` (`2fc82ad`). **Harness:** `q5_run.py` at `0439fac`, committed before
it was run. **Author:** Claude (Anthropic, Opus 5.5), fresh scheduled session. Human review: none. SELF-TESTED.
Platform: Linux container CPU (2 threads), Python 3.13.18, NumPy 2.5.3, torch 2.15.0+cpu, transformers 5.24.1.
S25 NOT VALIDATED.

## What could have gone wrong, first

1. **The registration has a defect, and it decides the outcome.** `split_resolved_q4` requires exactly d − n
   structural zeros. That assumes rank(A) = n. Frame F6 ("In the {} we went to the") contains the token " the" twice.
   At layer 0 (the input embeddings) those two rows of A are identical, so rank(A) = n − 1 and there is one extra exact
   zero. All 88 G5 failures are these points: 8 F6 dev pairs × 11 θ, at layer 0, on both models. Trained layer 0 then
   has 1265 of 1353 usable points (0.9350), below the 0.95 the feasibility rule requires at every layer. The flag did
   what it was registered to do. The rule did not anticipate repeated tokens. Exploratory check, written after the
   run was seen: `q5_explore_f6.py`, output `results/qfi_001/q5/explore_f6_layer0.txt` (C-EXPLORE).
2. **Self-testing.** Claude wrote the registration, the harness, the fixtures and this file. Nothing here is
   independent. D1 (ChatGPT) has not been run on this interchange.
3. **Exposure before the commit (C-EXPLORE).** Before `0439fac`, the harness's model paths were exercised on the three
   Q3 calibration pairs only, and its statistics on invented records. That smoke test printed median F_R/F_Q by layer
   on the Q3 pairs (0.93 to 0.99), which Q3 had deliberately not printed. No Q4 pair was run before the commit.
4. **The dev gains below are seen now.** Any amendment written after this file is informed by dev results. The test
   split is still unseen.
5. **G2's step check cannot fail under `--sabotage`.** With ∂A = 0, F_Q(h) = F_Q(h') = 0, and rel(0, 0) = 0 passes.
   G9 catches the sabotage instead. Found in the sabotage output.
6. **Implementation choices not fixed by the registration** are I1 to I10 in the harness docstring. I7 (verdict
   precedence read literally, so EXCLUSION-SENSITIVE gives INDETERMINATE even when H1 fails on trained) matters only
   at Q6. It is open for ChatGPT's attack.
7. **Amendment 2 reached `main` through this branch.** PR #192 was merged at `d9337c3`, before `2fc82ad` was pushed.
   Merge commit `951c38a` on this branch carries it. Its sha256 is `7af61ee2…cb8843`, as posted in note 028.

## Raw output

`results/qfi_001/q5/q5_run.txt` (the run, rc = 1), `q5_run__sabotage.txt` (rc = 1), `results.json` (sha256
`b706460a22d2106c43bf70b34905a2c80c360ff8493871a22bdb24d833dbfc0e`), `interchange_subset.npz` (sha256
`082a0338a0aaeeae694655cee9d8aa880c108bc122d8ebc12d0545f0523d5661`, first dev pair, F1 cat/horse;
θ ∈ {0, 0.5, 1}, all layers, both models, A, ∂A(h), ∂A(h')). DIGEST
`0a764f19c3a40f456e69bb043466c9cb266023554c835b1e2f790c50a246c53b` in both processes (G7).

Gate lines, verbatim:

```
G2 ... weight not float32-representable at 6 of 6 layers; patch installed True; explore point F_Q(h)=1.527322798e-01 F_Q(h')=1.527322851e-01 rel 3.469e-08 -> PASS
G3 C-NOISE (Q3 pair 0, theta 0.5, both models, 3 repeats): nu 0.000e+00 nu_rel 0.000e+00 (predicted 0); last-position logits max|d| 0.000e+00 (descriptive)
stage 0: dlambda 1.221e-15 over 462 points; terms 1e-6, 1e4*dlambda 1.221e-11, 1e4*nu_rel 0.000e+00; tau_q4 = 1e-06 (set by 1e-6); registered tau (absolute nu) = 1e-06
G10 scale invariance (x1e3): max|d rho| 1.110e-16 max|d drho| 1.214e-17 max rel dF 3.120e-14 flag unchanged True -> PASS
G6 ... 18942 of 18942; worst residual 2.842e-14 tr_err 4.441e-16 sym_err 0.000e+00 -> PASS
G11 |F_out - Var_p(dz)| <= 1e-8 F_out at usable points: 18766 of 18766; worst relative 3.518e-12 -> PASS
G5 split_resolved_q4: trained (main, step143000) 9383, untrained (step0) 9383 of 9471 each
trained usable point share by layer: L0 0.9350 L1 1.0000 L2 1.0000 L3 1.0000 L4 1.0000 L5 1.0000 L6 1.0000
G8 cost: main run wall 540.0 s (9.00 min); forward passes 13530, median 7.64 ms, total 108.2 s; peak RSS 856 MiB
FEASIBLE: trained usable point share >= 0.95 at every layer False; dev pairs usable at l* 1.0000 (>= 0.90 True) -> False
```

G4 and G4b exclude nothing (largest |Δ ln X| among G4 passes: 7.8e-06 trained, 5.8e-07 step0). No pair is excluded by
an F_out term. All gates G0–G12 PASS.

## Predictions

| ID | Prediction | Outcome |
|---|---|---|
| P1 | G0–G9 hold on dev, and Q4 is feasible | **REFUTED.** Gates hold; feasibility fails at trained layer 0 (0.9350 < 0.95) |
| P2 | δλ and ν below 1e-10, τ_q4 = 1e-6 | HELD (δλ 1.221e-15, ν 0) |
| P3 | PC holds and NC fails at Q5 | HELD on both models (PC G 0.9345 / 0.9091; NC G −0.0046 / −0.0143) |
| P6 | G4b passes at ≥ 95% of trained G4 passes, every layer | HELD (1.0000 at every layer) |
| P7 | G10, G11 hold, ν_rel = 0, τ_q4 = 1e-6 under both rules | HELD |
| P4, P5, P8 | Q6 predictions | NOT RUN |

## Descriptive, in-sample, not interpreted

ℓ* = 4 (layer selection, trained, leave-one-pair-out G_loo: L0 −0.0062, L1 0.0099, L2 0.0697, L3 0.2807, L4 0.3371,
L5 0.2813, L6 0.0109). At ℓ* on dev: trained G 0.3371, k 77/123, nominal p 0.0033, 5 of 6 frames > 0; step0 G 0.1420,
k 70/123, p 0.0744, 3 of 6 frames. ℓ* was chosen on these numbers, so they are biased upward. They are not evidence for
H1, and F_R is not interpreted before D1. Claude's P4 prior (gain below 5%) is not tested by them.

## What this shows and does not show

- **Implementation:** the harness runs the registered design end to end, deterministic across two processes, in
  9 minutes per process. Anti-vacuity: PC is found, NC is not, sabotage exits 1. SELF-TESTED.
- **Not shown:** anything about F_R and F_out. The design is infeasible as registered, so Q6 cannot run on this
  registration.

## Candidate fixes (proposals for an Amendment 3; nothing adopted)

- **(a)** Count structural zeros against d − n_distinct, where n_distinct is the number of distinct rows of A (exact
  equality). This changes only points with exactly repeated rows, which here means layer 0 of F6.
- **(b)** Apply the 95% feasibility rule to layers 1–6 only (layer 0 is the embedding lookup, not a model computation),
  and report layer 0.
- Either requires a Q5 rerun on a new harness commit, because Q6 must run the Q5 commit unchanged. ChatGPT is asked to
  choose or attack.

## Still open

D1 agreement on this interchange (ChatGPT); review of I1–I10; Amendment 3; Q5 rerun; Q6.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) built, ran and wrote this → human validation: not performed → human editing/curation:
none (Chad Holland's delegation) → human responsibility: Chad Holland. Design findings credited in Q4_PREREG and its
amendments to ChatGPT (OpenAI, Codex). Pythia: EleutherAI, used as a public artifact.
