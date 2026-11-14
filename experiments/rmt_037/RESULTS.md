# RMT-037 results (run 2026-11-14)

**Status:** run as registered at `6e995ea` ([REGISTRATION.md](REGISTRATION.md)). Code and tests committed at
`c9cc9fc` before any statistic of the model weights was computed. SELF-TESTED. **4 of 6 predictions held; R4 and R5
refuted. 4 of 4 controls held.**

- **Digest:** `9dcb02306944ed98c035781fe09c9f090403aa794acc350654bc45896b97a97a`. A rerun was byte-identical.
- **Weights:** `openai-community/gpt2`, SHA-256 `248dfc39…a707`; `openai-community/gpt2-medium`, SHA-256
  `fc5a354a…c9cd`.
- **Raw output:** [`results/rmt_037/run.txt`](../../results/rmt_037/run.txt), with the rerun, the test log and the
  exploratory check.
- **Environment:** Python 3.13.18, NumPy 2.5.3, SciPy 1.18.1, x86_64 container. About 34 s for both models.
- **Not in CI:** it needs a 2 GB weight download.

## Failures first

1. **R4 REFUTED.** At the edge (the top 10% of singular values), GPT-2 small's trained ⟨r̃⟩ differed from its random
   initialisation by 0.012 (0.4895 against 0.5016), not by more than 0.05.
   - The direction is the same in both models: trained is lower, meaning less level repulsion among the largest
     singular values.
   - In GPT-2 medium the gap is 0.039 (0.4882 against 0.5271, roughly 4.6 standard errors).
   - That consistency is a description, not a registered result.
2. **R5 REFUTED, in the opposite direction to the worry.**
   - **False alarms:** note037's own pipeline (degree-5 polynomial unfolding, KS test against a sampled Wigner
     reference) rejected only **0.7%** of true GOE spectra of 64 levels, not more than 10%.
   - **Power (exploratory check, after the run, not registered):** the same pipeline rejected the Wigner
     reference on only **58%** of Poisson spectra of 64 levels.
   - **Comparison:** a plain cut on the spacing ratio (⟨r̃⟩ below 0.458) separates a single 64-level spectrum
     better: 92.3% of Poisson spectra caught, against 4.9% of GOE spectra flagged.
   - **So the note's pipeline is conservative and weak at head size.** It rarely cries wolf, but it misses about
     two in five integrable spectra. Use the ratio instead.
3. **Prior art predicted the main result before the run** (disclosed in the registration). R1–R3 and R6 replicate
   Thamm et al. (2022) and Aarts et al. (2024) on GPT-2's QK circuits; they are not new.

## What held

| ID | Prediction | Observed |
|---|---|---|
| R1 | small QK bulk: trained within 0.02 of initialisation | 0.5322 ± 0.0030 against 0.5317 ± 0.0031 (difference 0.0005) |
| R2 | small QK bulk trained ≥ 0.50 | 0.5322 (GOE reference at 64 levels: 0.5309; Poisson: 0.3855) |
| R3 | no small layer's QK bulk below 0.45 | lowest layer 0.5100 (layer 6) |
| R6 | medium: R1 and R2 | 0.5328 ± 0.0019 against 0.5304 ± 0.0019; lowest of 24 layers 0.4977 |

Shuffled weights (SHUF) gave 0.5279 (small) and 0.5282 (medium) in the QK bulk. That is the same as the trained and
random arms, within about 1.5 standard errors.

## Controls

| ID | Result |
|---|---|
| C1 Poisson(64) bulk ⟨r̃⟩ within 0.02 of 0.3863 | HELD, 0.3855 |
| C2 GOE(64) bulk ⟨r̃⟩ within 0.02 of 0.5307 | HELD, 0.5309 |
| C3 QK levels via QR equal the full 768 × 768 SVD | HELD, max relative difference 1.0e-15 |
| C4 Weights read twice identical | HELD |

## Descriptive, no prediction registered

| Model | Object | Region | Trained | Init | Shuffled |
|---|---|---|---|---|---|
| small | SYM | bulk | 0.5106 | 0.5195 | 0.5247 |
| small | SYM | edge | 0.5217 | 0.5240 | 0.5328 |
| medium | SYM | bulk | 0.5170 | 0.5201 | 0.5217 |
| medium | SYM | edge | 0.5180 | 0.5300 | 0.5213 |

- **Scale changes and the statistic does not.** Training changes the *scale* of the QK levels hugely. In GPT-2
  small the median singular value goes from 0.30 at initialisation to 12.6 after training, with a maximum of 269. The
  spacing ratio is scale-free and barely moves.

## What this shows (C-DESIGN: observational measurement of two fixed models against matched random arms)

1. **In the bulk, GPT-2's attention QK circuits have the level statistics of a random matrix, trained or not.**
   Trained, freshly initialised and shuffled weights are indistinguishable in the bulk spacing ratio, in both model
   sizes. **So the bulk spacing statistic says nothing about what a head learned.** This answers note037's third open
   question: describing heads as "chaotic or integrable" through their weights' bulk spacings is a new vocabulary for
   a null result. It agrees with the prior art.
2. **If training leaves a trace in the spacings, it is among the largest singular values.** Both models show slightly
   less repulsion there after training. That is consistent with Thamm et al.'s "learned information in a few large
   singular values". It fell short of the registered size in GPT-2 small, so it stays a lead, not a finding.
3. **The note's suggested pipeline should not be used at head size.** It is conservative (0.7% false alarms) but
   weak (58% power). The spacing ratio is the better instrument for one 64-level spectrum.

## Doors (M15), unrun

- **The edge, registered properly.** A threshold set from GPT-2 medium's 0.039, then tested on a third model
  (Pythia-160M, for example). This separates decide-data from judge-data (C-HOLDOUT).
- **The OV circuit** (`W_V W_O`).
- **Attention activation spectra.** arXiv:2606.19404 claims Wigner-Dyson against Poisson separates valid from
  hallucinated reasoning. That is a different object (activations, not weights) and is not checked here.
- **Induction heads against the rest.**

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) found the prior art, registered, wrote, ran and wrote up this
experiment → human validation: not performed → human editing/curation: direction by Chad Holland, 2026-11-14 → human
responsibility: Chad Holland. Review level: direction only.*
