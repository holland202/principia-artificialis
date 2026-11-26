# QFI-001 Q4 registration: does the rotation part of the QFI predict output sensitivity beyond its rivals?

**Status:** REGISTERED, NOT RUN. Nothing covered here is built. The only thing run is the C-FEAS count script
[`q4_feasibility_counts.py`](q4_feasibility_counts.py), which tokenises template sentences and runs no model. Its output
is [`results/qfi_001/q4/feasibility_counts.txt`](../../results/qfi_001/q4/feasibility_counts.txt). This file is
committed alone, before the Q5 harness exists (M2). It is never edited. Errors found later go into the Q5 or Q6 results.

**Authority:** Chad Holland's delegation, PR #181 comment 7141782954. **Ask:** A21.2 (Claude 021) and the Q4 line of
#181's task list: path, model, endpoint and rivals; τ_flag from measured noise; withhold the split where it is not
resolved; count support-edge eigenvalues and kernel blocks below the cutoff (Q1 Amendment 4 item 6).

**Author:** Claude (Anthropic, Opus 5.5), fresh scheduled session. Human review: none. ChatGPT (OpenAI, Codex) is
asked to attack it in one note (FAST-1 item 4).

## Question

Along a one-token input path, ρ(θ) is the trace-normalised second moment of a layer's token vectors. Its QFI splits
exactly as F_Q = F_C + F_R. F_C is the classical part (eigenvalues) and F_R the rotation part (eigenvectors). **Does
log F_R at one layer predict how fast the model's next-token distribution moves along the same path, on fresh pairs,
better than a model that already has the classical part, the simplest movement statistic and the output entropy?**

- **Endpoint:** y = mean over θ of ln F_out(θ). F_out = Σ_v p_v (∂_θ ln p_v)² is the classical Fisher information of the
  next-token distribution p at the last position, along θ. It is the model's own behaviour along the same path. It is
  not a correctness label.
- **Design (C-DESIGN):** observational and correlational on one small public model, using generated inputs. The
  strongest claim it can carry is associational and predictive: "on pythia-14m and these templates, F_R adds held-out
  predictive value for F_out". It supports no causal claim, nothing about other models and nothing about "LLMs".

## Rivals (M14), all as arms

| Rival | Arm | What it says if it wins |
|---|---|---|
| R0, simplest | ln S, with S = ‖∂A‖²_F / ‖A‖²_F, the relative movement of the token vectors | geometry adds nothing to "how much A moved" |
| R1, classical | ln F_C, the eigenvalue part | the quantum framing adds nothing |
| R3, output entropy | H, the mean entropy of p over θ (nats) | the output alone suffices |
| R2, architecture | everything below repeated on the untrained step0 model | the gain reflects the architecture, not learning |

**Not tested here: #030's hypothesis.** It needs a labelled wrong-answer set, and pythia-14m on templates has none
that can be defended. R3 enters only as a rival predictor of F_out. The door is below.

## Design (fixed here)

- **Models:** pythia-14m, trained (`cf967c0a…`, main, step 143000) and untrained (`56079904…`, step0). Pinned by the
  identities in `q3_feasibility_counts.py`. Weights are never committed.
- **Forward pass, float64 throughout.** `GPTNeoXForCausalLM` in eval mode, cast to float64, 2 CPU threads,
  `attn_implementation="eager"`, called with `inputs_embeds`. The eager softmax's float32 cast is removed in memory,
  as in `q3_explore_step.py --softmax64` (Q3 results item 1). Gate G2 checks it.
- **Inputs (generated; C-SYNTH):** 6 frames × single-token word lists, fixed in `q4_feasibility_counts.py`. A pair
  is two fillings of one frame that tokenise to equal length and differ at exactly one position. Pairs that move a Q3
  word pair are excluded. 364 pairs qualify (list sha256 `ad19d827…c247a4`).
- **Split (C-HOLDOUT):** the first byte of sha256(`qfi001-q4-split|frame|w_a|w_b`) below 86 puts a pair in **dev**
  (123 pairs), otherwise in **test** (241). Fixed before any model output on these pairs exists.
- **Path, state, derivative:** as in Q3. e(θ) = (1−θ)E[w_a] + θE[w_b] at the slot row, θ = 0, 0.1, …, 1. A_ℓ(θ) ∈
  ℝ^{n×128} for ℓ = 0…6, and ρ = AᵀA / tr. ∂A is a central difference at h = 1e-4, with a second step h' = 1e-5 for
  gate G4. ρ and ∂ρ are symmetrised as (X + Xᵀ)/2 before the split. F_out uses the same central difference of
  `log_softmax` of the last-position logits, in float64.
- **Instrument:** `qfi_ref.qfi_split_ex` (code `5c6f772`), imported unchanged.

## The Q4 resolution flag (adopted here) and its controls

`split_resolved_q4` is True when all of these hold:
- `split_resolved_support` holds, exactly as in Q3: no tie outside the structural-zero block, every gap among
  eigenvalues above ε/2 is greater than τ_q4, and the kernel-to-support gap is greater than τ_q4;
- the structural zeros number exactly d − n;
- no eigenvalue lies in (ε/2, 1e-6].

The last two conditions answer ChatGPT's F20.1: a positive mode that falls below the cutoff must not clear. F_C and F_R
at a point where the flag is False are withheld, never repaired. Kernel blocks, support-edge eigenvalues and small
positives are counted at every point, as in Q3.

**Controls (exact ∂ρ, no model). Pass means the stated flag value:**
- **S3:** rotation into the kernel. Expected `split_resolved_q4` True. It is the positive control.
- **N1:** a support tie, p = (0.4, 0.4, 0.2), d = 5. Expected False.
- **N2:** F20.1's path, n = 2, d = 4, p = (1 − δ, δ, 0, 0), δ = 2.5e-13. Expected `split_resolved_support` True and
  `split_resolved_q4` False. This is the negative control F20.2 asked for.

A scratch check of the three flag values was run on these synthetic inputs before this registration. It is
SELF-TESTED, and not a result.

**τ_q4, from measured noise (stage 0).** On the three Q3 calibration pairs (462 points, float64 attention), δλ is the
largest |λ_i(AᵀA/t) − λ_i(AAᵀ/t)| over the n nonzero eigenvalues: the same spectrum, rounded two ways. ν is the
largest |ΔA| over the C-NOISE repeats (G3). Then τ_q4 = max(1e-6, 10⁴·δλ, 10⁴·ν). Stage 0 runs before any dev pair is
run. The Q3 pairs are already development data.

## Q5: development run (dev pairs only)

Each of these gates is fail-closed. If any fails, Q5 reports INFEASIBLE with the first failure, and Q6 waits for an
amendment registration.

| ID | Gate | Pass |
|---|---|---|
| G0 | `run_cases.py` on `public.jsonl` and `a16_must_fail.jsonl` | 8 of 8 pass; must-fail rc = 1 |
| G1 | pinned identities | all match |
| G2 | float64 attention: `output_attentions` dtype at all 6 layers; Q3's explore point re-run | float64 ×6; F_Q at h and h' within 1e-6 relative |
| G3 | C-NOISE: Q3 pair 0, θ = 0.5, both models, 3 repeats in one process | ν printed (predicted 0) |
| G4 | step convergence per point: \|X(h) − X(h')\| ≤ 1e-4·F_Q(h') + 1e-15 for X ∈ {F_Q, F_C, F_R}, and \|ΔF_out\| ≤ 1e-4·F_out(h') + 1e-15 | see "usable" |
| G5 | `split_resolved_q4` (τ_q4 from stage 0) | see "usable" |
| G6 | residual ≤ 1e-10·max(1, F_Q); \|tr ρ − 1\| ≤ 1e-12; symmetric | all points |
| G7 | second process gives the same digest | equal |
| G8 | dev run wall time, 2 CPUs | < 60 min |
| G9 | S1–S3 (Q3), N1, N2 | as stated |

**Usable.** A point is usable if it passes G4 and G5 and F_C, F_R, S and F_out are all above 1e-300. A pair is usable
at layer ℓ if at least 9 of its 11 θ are usable there. **Feasible** means at least 95% of trained dev points are usable
at every layer, and at least 90% of dev pairs are usable at ℓ* (below).

**Features, per usable pair at layer ℓ (means over its usable θ):** c = ln F_C, r = ln F_R, s = ln S, h = H, and
y = ln F_out. Two ordinary least-squares models with an intercept:
- **A (rivals):** y ~ 1 + c + s + h
- **B (adds rotation):** y ~ 1 + c + s + h + r

**Layer choice (decided on dev only).** For each ℓ = 0…6 on the trained model, G_loo(ℓ) is the leave-one-pair-out
reduction of A's squared error, (SSE_A − SSE_B)/SSE_A. Then ℓ* = argmax G_loo, with ties going to the higher ℓ. The
coefficients of A and B are then fitted on all usable dev pairs at ℓ*, separately for each model. Q5 writes ℓ*, τ_q4
and the coefficients to its results file, and its sha256 is posted. Q5 prints dev gains and layer profiles
(descriptive, in-sample). It never loads test pairs: the harness refuses `--split test` unless the Q5 results file is
given.

**D1 before interpretation (FAST-1).** Q5 writes an interchange subset (A, ∂A, float64 attention). Q5's results do not
interpret F_R until ChatGPT's `d1_sld` agreement on that subset is posted. Q6 waits for it as well.

## Q6: confirmatory run (test pairs, run once)

Q6 runs the Q5 harness commit unchanged, with `--split test`, reading ℓ*, τ_q4 and the coefficients from the Q5 results
file. It repeats G0–G9 on the test pairs. N is the number of usable test pairs. It is fixed by the gates, before any y
is read. For each pair, e_A and e_B are the out-of-sample errors.

- **H1 (trained):** holds if all three of these hold:
  - (a) G_test = (SSE_A − SSE_B)/SSE_A ≥ 0.05;
  - (b) a one-sided exact sign test on k = #{e_B² < e_A²} gives P(Binom(N, ½) ≥ k) ≤ 0.05;
  - (c) the frame-level gain is greater than 0 in at least 4 of the 6 frames.
- **H2 (R2, learning):** the same test on step0 at ℓ*, with step0's own dev coefficients and its own y. The verdict
  is LEARNED if H1 holds on trained and fails on step0, ARCHITECTURAL if it holds on both, and NONE if it fails on
  trained.

**Anti-vacuity (M3), both run at Q5 and at Q6:**
- **PC:** y is replaced by y_pc = r + 0.3·σ·z. Here σ is the dev standard deviation of r after regressing it on
  (1, c, s, h), and z comes from `numpy.random.default_rng(20261126)`, drawn in pair-list order. H1's procedure must
  hold.
- **NC:** y_nc = c + s + h + 0.3·sd_dev(y)·z, with the same z. H1's procedure must fail.
- If PC fails or NC holds, H1's outcome is reported as **UNDECIDABLE**, not as null.
- `--sabotage` sets ∂A = 0. G9 must fail and the run must exit 1.

**Statistics (C-STAT):** a fixed-horizon exact sign test with one look and N fixed by the gates. Pairs share frames and
words, so they are not independent. The p-value is therefore nominal, and (c) is the guard against one frame carrying
the result.

## Predictions (Claude's, NOT RUN)

- **P1:** G0–G9 hold on dev, and Q4 is feasible.
- **P2:** δλ and ν are below 1e-10, so τ_q4 = 1e-6.
- **P3:** PC holds and NC fails, at Q5 and at Q6.
- **P4:** H1 does not hold on trained. Claude's prior is that r adds less than 5% over c, s and h.
- **P5:** H1 does not hold on step0.
- **Not predicted:** ℓ*, the rotation share F_R/F_Q by layer, and the dev gains. They are reported descriptively.

## What Q6 decides (doors)

- **H1 holds and PC/NC behave:** this result is SUPPORTED for this stand-in only. Q7 updates note #022's experiment 2
  with this code, labelled as one model and generated inputs.
- **H1 fails and PC holds:** NOT SUPPORTED at this endpoint. On this stand-in, the rotation part adds no held-out
  predictive value over its rivals.
- **UNDECIDABLE or INFEASIBLE:** Q7 says so, and the claim stays Speculative.

**Doors, unrun in any case:**
- #030 on a labelled wrong-answer set, with output entropy as the rival;
- a word-disjoint split (here, 46 of 49 test words also appear in dev);
- a larger pinned model;
- the n×n token-Gram construction.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Yes. C-FEAS output committed with this file; G4/G5 define feasibility on dev |
| Noise | Yes. G3 (same input), G4 (along θ, which R7 missed in Q3), G7 (across processes) |
| Statistics | Yes. One fixed-horizon exact sign test at Q6; dependence disclosed |
| Evidence | No. The question is not about evidence handling |
| Independence | Yes. SELF-TESTED. D1 crossing by ChatGPT (partly independent: it has read `qfi_ref.py`) |
| External | Yes. Public model under Apache-2.0, pinned by hash; no outside claim used |
| Device | Linux container CPU. S25 NOT VALIDATED |
| Verdict code | Yes. Fail-closed gates. A missing, NaN or unmatched value fails |
| Exploration | Yes. Q3's values were seen, including the float64 scan (C-EXPLORE) at 4 points. No Q4 pair has been run |
| Held-out | Yes. Dev decides ℓ*, τ_q4 and the coefficients; test judges once. Identities above |
| Generated inputs | Yes. 6 frames, 364 pairs, per-frame counts in the C-FEAS output. A person has not looked at a sample (Chad is out of the loop); ChatGPT is asked to |
| People's data | No |
| Design | Yes. Observational and correlational, as above |

## Limits

"Quantum" means a non-commuting matrix geometry built from classical activations. One model of 14M parameters and six
templates is a stand-in for nothing larger. F_out measures sensitivity, not quality. The test pairs are fresh pairs,
not fresh vocabulary.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) designed this → human validation: not performed → human editing/curation: none (Chad
Holland's delegation) → human responsibility: Chad Holland. Question lineage:
- ChatGPT (OpenAI, Codex): notes 012, 014, 019, 020 and 022 (support mask, F20.1's lost mode, F20.2's control, the
  D1 crossing);
- note #022 (proposed experiment 2), #030 and #034 credit their own authors.

Pythia: EleutherAI (Biderman et al. 2023), used as a public artifact. No endorsement is implied.

## Unrun next step

Build `q5_run.py`, importing `qfi_ref` and the Q3 helpers rather than copying them. Commit it before running it. Run
stage 0 and the dev split, then `--sabotage`. Write `Q5_RESULTS.md`, failures first.
