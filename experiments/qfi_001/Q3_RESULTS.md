# QFI-001 Q3 results: 3 of 3 as registered, but the forward pass was not all float64, so the F values are not usable

**Status:** development run, SELF-TESTED by Claude, who wrote the registration, the harness and this file. Linux
container CPU (2 threads), Python 3.13.18, NumPy 2.5.3, torch 2.15.0+cpu, transformers 5.24.1. S25 NOT VALIDATED.
Registration: [Q3_PREREG.md](Q3_PREREG.md) (`e533438`). Harness [`q3_run.py`](q3_run.py) committed before it was run
(`a2979e1`). Authority: Chad Holland's delegation, PR #181 comment 7141782954. Ask: A19.3 (Claude 019).

## What could have gone wrong, first

1. **The forward pass was not all float64 (deviation from the registration, found by item 6).** The registration says
   "float64". The harness uses transformers' eager GPT-NeoX attention. That path computes the attention softmax in
   float32 and casts it back (`softmax(..., dtype=torch.float32)` in `eager_attention_forward`, transformers 5.24.1).
   Choosing "eager" was Claude's implementation choice. The registration did not fix it. The float32 rounding makes
   A(θ) slightly rough along the path. A central difference divides that roughness by h, and every term that couples
   a support mode to the 120- or 121-dimensional kernel picks it up.
   - **Registered signal:** the h = 1e-3 step check (item 6) moved F_Q by up to 8.99e-01 (relative) at trained layer
     6 and 2.83e-02 at layer 5. Layer 0 has no attention and moved by at most 4.11e-13 in either model.
   - **Exploratory (C-EXPLORE, not registered, designed after seeing the run):** [`q3_explore_step.py`](q3_explore_step.py)
     scans h from 1e-3 to 1e-6 at four points. As registered, F_Q does not settle as h shrinks. At trained pair 2, θ 0.4, layer 6
     it grows from 1.7 to 7.7e3. With the softmax kept in float64 (patched in memory), it settles to within 2.5e-7 at every point. At
     that point the registered h = 1e-4 value is 11.24 times the settled one (1.716581 against
     0.1527323).
   - **Consequence:** the per-point F_Q, F_C, F_R and `rel_h` at layers 1–6 in `results.json` measure rounding as well
     as geometry. Do not use them. The eigenvalue counts, ties, gaps and both resolution flags depend only on ρ, so the
     derivative noise does not reach them. A float32 perturbation of A could still move ρ's eigenvalues by about 1e-7.
     The smallest gap that matters is 5.59e-05, so the counts should not change. That is an inference. It was not
     measured.
2. **R7 measured the wrong noise (registration error, kept).** It repeats the same input and finds 0 difference, as
   predicted. Same-input runs are bitwise identical, so R7 cannot see roughness along θ, and roughness along θ is what
   a finite difference amplifies. R7 held and is not evidence that ∂A is clean.
3. **Self-tested.** Neither ChatGPT nor a human has run this. The D1 crossing (A19.2, ChatGPT reads the interchange
   file) has not happened. The interchange `dA` carries the same float32 roughness. That does not matter for D1, where
   both readers get the same arrays, but those arrays are not a float64 derivative.
4. **ChatGPT's review of the registration (note 020), checked against these points.**
   - F20.1: the flag can clear a point that has lost a positive mode below the cutoff. On these 462 points no mode is
     lost that way. Structural zeros equal d − n exactly at 462 of 462, there are no small positives, and the smallest
     kernel-to-support gap is 8.10e-04. That is a fact about these inputs. It does not fix the flag.
   - F20.2: S3 is a feature-space control only. No negative control for `split_resolved_support` was registered.
   - F20.3: each pair's coverage is printed. It is 11/11/11 at every layer of both models.
5. **Other implementation choices the registration does not fix** (listed in the harness docstring):
   - the checkpoint key `embed_out.weight` is loaded as `lm_head.weight`, with a strict load;
   - S1 uses p(θ) = softmax(log p₀ + θa) with a = (1, 0, −1);
   - R5 is judged on the main run, and the R6 repeat is timed separately;
   - the digest covers every per-point field at 10 significant digits;
   - `hidden_states[6]` is taken after the final layer norm. In this transformers version it equals
     `last_hidden_state` (scratch check, SELF-TESTED).

## Raw output ([`q3_run.txt`](../../results/qfi_001/q3/q3_run.txt), sha256 `1c9d4e1f…ec6f1`; excerpt, verbatim)

```
S1 commuting: F_Q=0.609999998717 F_C=0.609999998717 F_R=0.000e+00 (Var_p(a)=0.610000000000) -> PASS
S2 rotation (0,1): F_Q=0.199999999333 F_C=0.000e+00 F_R=0.199999999333 (expect F_Q 0.200000000000) -> PASS
S3 rotation into kernel (1,3): F_Q=1.199999996000 F_C=0.000e+00 F_R=1.199999996000 split_resolved=False split_resolved_support=True (expect F_Q 1.200000000000, False, True) -> PASS
R3 finite, |tr rho - 1| <= 1e-12, symmetric to 1e-14: 462 of 462; worst tr_err 4.441e-16 sym_err 0.000e+00
R4 residual <= 1e-10 max(1, F_Q): 462 of 462; worst residual 1.332e-14
R7 same-input noise (pair 0, theta 0.5, both models, 3 repeats): max|d rho| 0.000e+00 max|d F_Q| 0.000e+00 (predicted 0)
trained (main, step143000)   5   33  0  33    0        120         0 1.46e-16 1.33e-15 0.00e+00 0.00e+00 5.36e-03 2.83e-02
trained (main, step143000)   6   33  0  33    0        120         0 6.66e-16 3.11e-15 0.00e+00 0.00e+00 1.46e-01 8.99e-01
R5 cost: main run wall 19.5 s; forward passes 330, median 8.74 ms, max 29.40 ms, total 3.0 s; peak RSS 849 MiB
R6 second process: rc=0 digest c8986b1406807421fcd48a73ee9786fb7a76a5a37312281eb7ad51468de6bdf4 (19.4 s); this process c8986b1406807421fcd48a73ee9786fb7a76a5a37312281eb7ad51468de6bdf4
P2 detail: split_resolved False at 462 of 462
P3 detail: structural zeros >= d - n at 462 of 462
  trained layer 6: split_resolved_support 33 of 33 -> can carry
  layers that qualify: 7 of 7
VERDICT 3 of 3 as registered
```

`--sabotage` (∂A = 0, [`q3_run__sabotage.txt`](../../results/qfi_001/q3/q3_run__sabotage.txt)): S1, S2 and S3 FAIL,
P1 REFUTED, `VERDICT 2 of 3 as registered`, exit 1, as registered.

Exploratory scan, from the two files `explore_step.txt` and `explore_step__softmax64.txt` (verbatim):

```
arm: as registered (eager softmax in float32)
trained (main, step143000) pair 2 theta 0.4 layer 6: F_Q at h=1e-3,1e-4,1e-5,1e-6: 1.739226e-01 1.716581e+00 7.793171e+01 7.674262e+03 | rel(1e-4 vs 1e-5) 9.78e-01 rel(1e-5 vs 1e-6) 9.90e-01
arm: softmax kept in float64 (patched)
trained (main, step143000) pair 2 theta 0.4 layer 6: F_Q at h=1e-3,1e-4,1e-5,1e-6: 1.527319e-01 1.527323e-01 1.527323e-01 1.527323e-01 | rel(1e-4 vs 1e-5) 3.47e-08 rel(1e-5 vs 1e-6) 1.80e-07
```

## Predictions

| ID | Registered | Outcome |
|---|---|---|
| P1 | R0–R7 all hold | HELD. R7 held vacuously for the noise that matters (item 2 above) |
| P2 | `split_resolved` False at 462 of 462 | HELD. A prediction that the current flag fails everywhere |
| P3 | structural zeros ≥ d − n everywhere | HELD, with equality at 462 of 462 |

"3 of 3 as registered" is not "the instrument works on this model". P2 predicted a failure of the current flag.

## What this shows and does not show

- **Shown (implementation, SELF-TESTED):** the pipeline runs on pythia-14m in 19.5 s. It is deterministic across two
  processes, and its controls catch a zeroed derivative.
- **Shown (counts):** `split_resolved` is blocked only by the structural kernel. `split_resolved_support` is True at
  462 of 462 points. By the registered door, all 7 trained layers can carry the split under this construction.
- **Not shown:** any F value at layers 1–6. Nothing here compares the trained and untrained models, and nothing is
  claimed about information content.

## Proposals for Q4 (not adopted; Q4's registration decides)

1. Run the forward pass with float64 attention throughout. Use an attention implementation verified to stay in
   float64, or a registered patch.
2. Make step convergence a pass criterion at every point, for example rel(F_Q(h), F_Q(h/10)) below a registered bound,
   and register a C-NOISE check along θ in place of R7.
3. Register a negative control for `split_resolved_support` (F20.2).

## Open

- A19.2: the D1 crossing on `interchange_subset.npz` (sha256 `ca6191b2…8d45f`, 480,896 bytes, 42 points). The full
  A/∂A set is not committed; its sha256 is `946ef5ca…96bdb`.
- Measure, rather than infer, that the counts survive float64 attention.

## Provenance (M13)

Claude (Anthropic, Opus 5.5), fresh scheduled session, built, ran and wrote this → human validation: not performed →
human editing/curation: none (Chad Holland's delegation) → human responsibility: Chad Holland. Review inputs: ChatGPT
(OpenAI, Codex) notes 019–020. Pythia: EleutherAI, used as a public artifact. No endorsement is implied.
