# GROK-RAC-001 — Residual Autocorrelation Collapse as an Online Marker of Irreversible Reasoning Failure

**Status:** SPECULATIVE / PROPOSED / NOT RUN / NOT REGISTERED  
**Theme:** Dynamical systems / Information geometry / Learning theory  
**Author:** Grok (xAI; Grok 4.5 class)  
**Builds on:** Nothing — new thread. Related PA notes on residual dynamics, geodesic trajectories, and thermodynamic reasoning exist but address different observables.  
**Method:** METHOD.md at commit `7c11e92358c33f0c9b787834ddbd59d1f3bd395d` (main at branch creation). Rules cited by ID are defined there.  
**Location:** `docs/GROK-RAC-001_SPECULATIVE_PROPOSAL.md` (not yet a numbered research note).

> **Authorization note:** This file is a speculative research proposal only. It is not a formal SWAY registration (W2), not an executed experiment, and not a claim of empirical result. Owner review is required before any note number allocation, preregistration, or movement into `research_notes/`.

---

## Critical technical correction (addressing causal objection)

**Objection (owner):**  
> Your injection time is randomly selected independently of the preceding trajectory. If the system has no advance information about that injection, a causal detector cannot reliably predict the immediately preceding step.

**Response and redesign:**

The original formulation treated the injection step \(t^\star\) as an exogenous random variable independent of the trajectory. Under that construction a purely causal online detector cannot systematically flag the step *immediately before* an unpredictable future event at rates substantially above chance. That formulation is therefore withdrawn as stated.

**Corrected causal structure (preserves the scientific intent while restoring causality):**

1. The residual map is made *conditionally unstable*. Before any hard injection, the spectral radius of the local linear map \(A_t\) (or an effective gain) is allowed to drift upward according to a slow, observable process that is a deterministic function of the recent residual history (e.g., cumulative energy or a running estimate of the largest singular value of a trailing window of updates).  
2. When a pre-registered instability threshold is crossed, an irreversible perturbation of fixed magnitude \(\delta\) is applied at the *next* step. The crossing of the instability threshold is therefore a causal, observable precursor that is available to any online detector.  
3. The lag-1 autocorrelation statistic is hypothesized to detect the *onset of this instability* (the precursor), not the exogenous random time itself. The “early-warning” claim is therefore that the statistic falls below \(\tau\) in the step that coincides with, or immediately follows, the observable instability onset, and before the irreversible perturbation has permanently altered subsequent dynamics.

**Temporal indexing (clarified):**
- \(t\) indexes residual vectors *after* each map application.  
- Instability onset is defined as the first \(t\) at which a registered scalar function of the trailing window exceeds its threshold.  
- The irreversible injection occurs at the subsequent step.  
- The detector is evaluated strictly on information available at or before the onset step (no post-injection residual is used for the decision that is claimed to be predictive).

**What makes the injected error irreversible:**  
After injection the map is altered (or a permanent bias direction is added) so that the subsequent trajectory cannot return to the pre-injection attractor under the registered dynamics. Reversibility would require an explicit restorative intervention that is not present in the generator.

**Consequence for the original 70 % claim:**  
The 70 % figure is retained only as a *proposed* success rate under the corrected, causally grounded generator. It is not claimed to hold under the original exogenous-random-injection design. That design is acknowledged as methodologically defective for an online early-warning claim.

All subsequent sections use the corrected causal structure. The original (defective) formulation is preserved only in the “Historical record of the first draft” appendix so that the change is auditable (M12).

---

## The claim (corrected)

In a controlled synthetic residual-stream trajectory whose local linear map becomes progressively unstable according to an observable function of recent history, the lag-1 Pearson autocorrelation of the residual vectors (or of their leading principal-component time series) falls below a fixed, pre-registered threshold \(\tau = 0.65\) at or immediately after the observable instability onset and before the irreversible perturbation has permanently altered the subsequent dynamics. Under the registered design this detection occurs with higher precision (lower mean absolute step error relative to the onset) than either (a) a residual-norm growth threshold or (b) a scalar magnitude-based “entropy” proxy of identical lead-time budget.

The claim is precisely wrong if any of the following holds under the registered design: the autocorrelation statistic fails to flag the onset more accurately than both baselines on the majority of trials, or the threshold \(\tau\) produces more false positives than the registered anti-vacuity bound allows, or the effect vanishes under the registered noise and dimension settings.

## Epistemic status

- Established mathematics: lag-1 autocorrelation, empirical covariance spectra, discrete dynamical systems on Euclidean space, and linear residual maps with additive noise are classical.  
- Derived / conjectured: the particular threshold \(\tau = 0.65\) and the claim of superiority under the exact corrected synthetic generator defined below.  
- Unverified: any numerical behaviour; transfer to real transformer residual streams.  
- No experiment has been run. No numbers claimed have been observed. All predictions remain unexecuted.

## Prior art

Spectral geometry and rank collapse in residual streams and attention have been studied (Naderi et al., “Mind the Gap,” 2024; Fernando & Guitchounts, “Dynamics of the Transformer Residual Stream,” 2026; Tao et al. on topologically regularized side-paths; Seq-VCR on intermediate representation collapse for arithmetic). Mutual-information objectives for CoT distillation also exist.

None of the cited works registers a lag-1 residual autocorrelation statistic as an *online early-warning detector of an observable instability onset that precedes irreversible error*, under a controlled synthetic collapse schedule, nor compares it head-to-head against residual-norm and scalar-magnitude baselines with the exact pass/fail criteria required by SWAY. Overlap with existing spectral analyses is acknowledged; the novelty claim is restricted to the online detection framing under the corrected causal structure and the registered experimental contrast.

## Mathematical formulation (corrected)

Let \( r_t \in \mathbb{R}^d \) be the residual vector at discrete step \( t = 0,1,\dots,T \).

**Corrected generator (stand-in named “SyntheticResidualMap-Causal”):**

\[
r_{t+1} = A_t r_t + \varepsilon_t, \qquad \varepsilon_t \sim \mathcal{N}(0,\sigma^2 I),
\]

where the local map \(A_t\) has spectral radius that is a non-decreasing function of a registered scalar statistic of the trailing window of residuals (e.g., cumulative squared norm or a running estimate of the dominant singular value). When this scalar first exceeds a fixed instability threshold \(\theta\), an irreversible perturbation of magnitude \(\delta\) is applied at the subsequent step and the map is thereafter held in the post-injection regime.

Lag-1 autocorrelation statistic (scalar reduction):

\[
\rho_t = \frac{(r_t - \bar{r})^\top (r_{t+1} - \bar{r})}{\|r_t - \bar{r}\| \,\|r_{t+1} - \bar{r}\|},
\]

or the same quantity computed on the leading principal-component time series of a trailing window of length \(w\).

Registered threshold: \(\tau = 0.65\) (inclusive).  
Baselines remain residual-norm growth and a scalar magnitude proxy.  
All constants (\(d, \sigma, \delta, T, w, \theta, \gamma, N\)) are to be fixed in any future registration before any run.

## Numbered predictions (proposed; NOT REGISTERED)

These are candidate predictions only. They have not been committed under W2 and must not be treated as frozen.

**P1 (candidate).** On \(N = 200\) independent trials with the corrected generator, the first step at which \(\rho_t < 0.65\) coincides with or immediately follows the observable instability onset on at least 70 % of trials (exact binomial test against null 0.5, two-sided, \(\alpha = 0.05\)).

**P2 (candidate).** Mean absolute error \(|\hat{t} - t_{\text{onset}}|\) of the autocorrelation detector is strictly smaller than that of both the residual-norm baseline and the scalar-magnitude baseline (paired comparison, same trials).

**P3 (anti-vacuity, candidate).** When the instability threshold is set so high that it is never crossed, the statistic \(\rho_t\) remains \(\ge 0.65\) for all \(t\) on at least 95 % of trials.

**P4 (candidate).** Under a 2\(\times\) increase in noise variance \(\sigma^2\), P1 still holds (robustness).

Falsification of the central claim would occur if P1 or P2 fails under the (still-to-be-frozen) registered constants.

## Simplest rival hypothesis (M14)

The residual-norm growth baseline alone is sufficient; any apparent advantage of autocorrelation is an artefact of the particular map or of the chosen threshold. The experiment therefore runs the norm baseline on identical trajectories and requires a strict improvement.

## Experimental design (outline only)

- **Cases:** 200 independent trajectories, length \(T = 40\), instability onset occurring in a mid-range window.  
- **Constants:** to be frozen only at formal registration.  
- **Outputs:** per-trial detected step, absolute error relative to onset, confusion counts, mean absolute error for each detector.  
- **Boundaries:** linear (or mildly non-normal) map, additive isotropic noise, fully observable instability precursor.  
- **Stand-in named:** SyntheticResidualMap-Causal (explicit NumPy implementation to be written only after registration authorization).

## Anti-vacuity controls (M3)

- Benign: instability threshold never crossed \(\to\) detector must stay silent (P3).  
- Failure-triggering: rapid instability onset \(\to\) detector must fire.  
- Sabotage switch: force \(\rho_t \equiv 1\) for all \(t\) \(\to\) instrument must report GATE: FAIL / exit 1.  
- Instrument can return null: zero-variance trajectory yields a defined “undefined / skip” verdict rather than a false positive.

## Triggered-controls table (M16)

| Trigger | Answer (yes / no + reason) |
|---|---|
| Feasibility | No — pure synthetic; no real-data unit counts. |
| Noise | Yes — additive Gaussian noise present; same-input noise measurement required before bounds are interpreted (C-NOISE). |
| Statistics | Yes — binomial and paired comparisons proposed; fixed-horizon tests to be registered in advance if the study proceeds (C-STAT). |
| Evidence | No — no external evidence streams. |
| Independence | No — single implementation; no replication claim. |
| External | Yes — prior-art citations; any later imported numerical claims will carry sha256 (C-EXT). |
| Device | No — pure NumPy, platform-independent. |
| Verdict code | Yes — detector returns explicit PASS / FAIL / UNDEFINED; missing input must deny (C-BUILD). |
| Exploration | No — no exploratory runs on candidate cases have been performed. |
| Method comparison | No — internal contrast of detectors is part of a single proposed study design; C-METHCOMP is not automatically activated by the presence of baselines (owner instruction 7). |

## Reference-code design

A self-contained NumPy script is contemplated but **has not been written**. It will be produced only after formal registration authorization. Expected surface: NumPy only; wall-clock < 2 s.

## Limitations and possible confounders

- Synthetic linear / mildly non-normal map may not capture real transformer residual dynamics.  
- Threshold \(\tau = 0.65\) is arbitrary (chosen for falsifiability).  
- Window length and dimension are not yet frozen.  
- No claim is made about real language-model residuals until a separate, registered follow-up is authorized and executed.  
- The original exogenous-injection design was causally defective; the correction introduces an observable precursor whose own detectability must be verified.

## Attribution and provenance (M13)

- Entire proposal (original and corrected) drafted by Grok (xAI).  
- Human review level actually performed: none (owner review pending).  
- No code executed, no numbers observed, no private repositories consulted.  
- METHOD.md, WORKFLOW.md, CONTROLS.md, NOTE_TEMPLATE.md and CLAUDE.md inspected at the commit of branch creation.

## Smallest experiment that could refute the main prediction

Once a reference script is authorized and written, a single run under the frozen constants. If the fraction of trials on which the autocorrelation detector flags the onset is < 0.70, or if its mean absolute error is not strictly better than both baselines, the corresponding candidate prediction is refuted.

## Open, unexecuted next prediction (M15)

**P5 (unrun, candidate).** When the same autocorrelation statistic is computed on residual streams extracted from a publicly available small transformer trained on modular arithmetic, the lag-1 autocorrelation still precedes irreversible digit errors under an analogous observable instability definition.  
This prediction is deliberately left unexecuted and unregistered.

---

## Appendix — Historical record of the first draft (auditable change)

The initial proposal (chat of 2026-10-21) used an exogenous random injection time independent of the trajectory and claimed a 70 % early-warning rate for the step immediately preceding that injection. That construction is causally invalid for an online detector and is hereby marked DEFECTIVE. The scientific intent (testing whether lag-1 residual autocorrelation can serve as an early marker of impending irreversible failure) is preserved; the mechanism has been rewritten so that the detector reacts to an observable instability precursor rather than to an unpredictable future event. No silent rewriting of the original claim has occurred; the defect and the correction are recorded above.

---

*Checklist (proposal stage):*  
[x] status label honest (SPECULATIVE / NOT RUN / NOT REGISTERED)  
[x] claims can be precisely wrong (M1)  
[x] numbered candidate predictions present  
[x] anti-vacuity path described (M3)  
[x] trigger table answered (M16)  
[x] simplest rival stated (M14)  
[x] at least one open door (M15)  
[x] AI attribution and review level stated (M13)  
[x] causal objection addressed and original defect preserved for audit (M12)  
[ ] formal registration (W2) — blocked pending owner authorization  
[ ] reference code written — blocked pending registration  
[ ] any experiment executed — forbidden without separate authorization

*Vincit Omnia Veritas.*
