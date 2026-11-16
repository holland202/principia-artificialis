# RMT-IH-001 registration: does the QK edge signal move before a tiny transformer learns to copy?

**Status:** REGISTERED, NOT RUN. Frozen in this commit, before any confirmatory training run. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-16). Design and code: Claude (Anthropic, Opus 5.5). Human review level:
direction only.

## Question

RMT-037 found that, at the top edge of each attention head's QK spectrum (the largest 10% of singular values), the
spacing ratio ⟨r̃⟩ is lower after training than at initialisation, in GPT-2 and OPT. Its results ended with an open
door: does this track known head types such as induction heads?

Small transformers learn induction (copying a repeated sequence) in a sudden jump during training. **Does the edge
⟨r̃⟩ start to move before that jump (an early warning), only after it, or not at all? And does it move earlier
than simpler spectral measures?**

**Prior work (2026-11-16 search):**

- Spacing statistics have been tracked during training before (Dyson Brownian motion analysis of nano-GPT weights,
  arXiv 2411.13512).
- RMT deviations have been used to locate learned structure (Staats, Thamm & Rosenow).
- The timing of induction-head formation can be predicted from batch and context size (Aoyama & Wilcox, arXiv
  2511.16893).

I found no work timing the edge spacing ratio against the induction jump. That is an absence in a short search,
not proof of novelty.

## Design (frozen)

- **Model:** attention-only transformer, built and trained from scratch (`tinyih.py`). Specification:
  - 2 layers, 2 heads per layer, d_model 256, so 128 QK levels per head;
  - pre-LayerNorm, no MLPs;
  - vocabulary 64; AdamW, learning rate 3e-5, no weight decay, batch 64;
  - 2,000 steps, with a checkpoint every 20 steps (101 checkpoints).
- **Data:** BOS, then a random 32-token segment A, then segment B.
  - Arm **repeat:** B = A, so induction is possible.
  - Arm **norepeat:** B is drawn independently, so induction is impossible. This is the control.
- **Seeds:** 1–6 for both arms. Exploration used seeds 900 and 101–120 only.
- **Per checkpoint:**
  - **ICL score:** held-out loss on segment A minus loss on segment B;
  - **edge ⟨r̃⟩:** pooled over all 4 heads, top 10% of each head's levels, 44 ratios. It uses RMT-037's own
    `ratios` and `qk_levels`;
  - **two simpler rivals:**
    - `top_norm`, the largest singular value over the mean;
    - `stable_rank`, Σσ² / σ_max².
- **Timing rule (`analyze.py`, tested, 4/4 mutants caught):**
  - **Baseline and final:** the baseline is the mean of the first 5 checkpoints, and the final value the mean of
    the last 5.
  - **t_X:** the first step at which statistic X has moved 25% of its total change (50% for ICL) and stays there
    for 3 consecutive checkpoints.
  - **No time:** t_X is undefined if X's total change is below its minimum: edge 0.02 (RMT-037's threshold),
    top_norm 0.023, stable_rank 0.57 (each rival's across-seed SD at initialisation), ICL 1.0.
  - **The induction jump:** t_IH is the ICL score's time.
  - **Limit:** the rule uses each run's final value, so it measures the *order* of changes. It is not a deployable
    alarm.

## Predictions

| ID | Prediction | Verdict rule | Claude's prior |
|---|---|---|---|
| P1 | Training lowers the edge ⟨r̃⟩ at this scale too (repeat arm) | mean drop ≥ 0.02 and a drop in ≥ 4 of 6 seeds | 0.6 |
| P2 | **Early warning:** the edge moves before the induction jump | t_edge < t_IH in ≥ 5 of 6 seeds | 0.4 |
| P3 | **Beats the simplest rivals:** the edge moves before top_norm *and* stable_rank | in ≥ 5 of 6 seeds | 0.25 |
| P4 | **Tied to induction, not generic training:** the norepeat arm's mean edge drop is less than half the repeat arm's | pooled over seeds | 0.5 |

If P1 fails, P2 and P3 are recorded as NOT TESTABLE, because a statistic that doesn't move has no time. **The lead
is killed if P2 or P3 fails.** If the edge moves only after the jump, it is not a warning. If a rival moves
first, the edge adds nothing.

## Controls

| ID | Control |
|---|---|
| C1/C2 | The statistic returns ≈0.5307 on GOE spectra and ≈0.3863 on Poisson spectra (test, ±0.01) |
| C3 | **Anti-vacuity: the induction detector can say "no".** The norepeat arm's final ICL is < 0.1 in every seed, and the repeat arm's is > 3.0 in every seed |
| C4 | QK levels via QR equal the full SVD (test, relative error < 1e-12) |
| C5 | Determinism: rerunning repeat seed 1 gives byte-identical rows |

## Noise and exploration (disclosed)

- **Noise at initialisation (C-NOISE),** over 20 seeds (101–120), with no training:

  | Statistic | Mean | SD |
  |---|---|---|
  | edge ⟨r̃⟩ | 0.5284 | 0.0444 |
  | top_norm | 2.3307 | 0.0228 |
  | stable_rank | 30.7970 | 0.5713 |

  The edge statistic is noisy across seeds. The timing rule compares each run with its own baseline for that
  reason.
- **Exploration (C-EXPLORE)** used ICL only (`explore_icl.py`, seed 900).
  - At lr 1e-3, induction formed within 100 steps: too fast to time.
  - At 1e-4 the jump came at about 240–360 steps.
  - At **3e-5**, the ICL score stayed near 0 until about 700 steps, then rose to 3.89 by 1,200. That rate was chosen
    so the plateau is long enough to see a lead.
- **One spectral value was seen before registering:** a 100-step smoke run at lr 1e-3 printed edge ⟨r̃⟩ 0.549. That
  is a different learning rate and a different seed, and nothing was chosen from it.

## Pre-mortem: how this could mislead

1. **44 ratios per checkpoint is few.** The edge series may flicker. The 3-checkpoint persistence rule and the
   0.02 minimum guard against that. A null here may be a power problem rather than a true absence.
2. **The 25% threshold uses the final value.** A slow drift starting at step 0 will "lead" any jump. The norepeat
   arm (P4) and the rivals (P3) are the checks against that.
3. **The model is tiny and synthetic.** Nothing here transfers to GPT-2/OPT scale without a new run.
4. **The prediction and the analysis are both Claude's.** This is self-tested, not independent.

## Open door, left unrun

**P5:** is the effect carried by the layer-1 (induction) heads rather than the layer-0 (previous-token) heads? The
per-layer split is not part of this registration.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed and wrote this → human validation: not performed → human
editing/curation: direction by Chad Holland, 2026-11-16 → human responsibility: Chad Holland. Review level:
direction only.*
