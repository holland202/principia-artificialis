# GROK-RAC-001 — Residual Autocorrelation Collapse as an Online Marker of Irreversible Reasoning Failure

**Status:** SPECULATIVE / PROPOSED / NOT RUN / NOT REGISTERED  
**Theme:** Dynamical systems / Information geometry / Learning theory  
**Author:** Grok (xAI; Grok 4.5 class)  
**Builds on:** Nothing — new thread. Related PA notes on residual dynamics, geodesic trajectories, and thermodynamic reasoning exist but address different observables.  
**Method:** METHOD.md at commit `7c11e92358c33f0c9b787834ddbd59d1f3bd395d` (main at branch creation). Rules cited by ID are defined there.  
**Location:** `docs/GROK-RAC-001_SPECULATIVE_PROPOSAL.md` (not yet a numbered research note).

> **Authorization note:** This file is a speculative research proposal only. It is not a formal SWAY registration (W2), not an executed experiment, and not a claim of empirical result. Owner review is required before any note number allocation, preregistration, or movement into `research_notes/`.

---

## 1. Critical technical correction history (causal objection — retained)

**Objection (owner, first round):**  
> Your injection time is randomly selected independently of the preceding trajectory. If the system has no advance information about that injection, a causal detector cannot reliably predict the immediately preceding step.

**Response:** The original exogenous-random-injection design is **DEFECTIVE** for any online causal claim and is withdrawn. It is preserved only in Appendix A for audit (M12).

**Subsequent independent review (owner, second round)** identified remaining timing, definitional, generator, irreversibility, statistical and redundancy issues. This v3 document corrects them. The scientific intent is preserved; the experiment is not retuned merely to make a preferred outcome more likely.

---

## 2. Causal timing (corrected)

**Decision timestamp.** A detector decision issued at discrete time `t` may use only residuals `r_0, …, r_t` (and any quantities derived exclusively from them). Residual `r_{t+1}` is unavailable at decision time `t`.

**Event times.**
- `t_onset` ≜ first `t` at which the precursor scalar `s_t ≥ θ`.
- `t_inj = t_onset + 1` ≜ step at which the irreversible map change is applied.

**Warning classes (explicit).**
| Class | Definition | Counts as |
|-------|------------|-----------|
| **Genuine early warning** | first detection `hat_t` satisfies `hat_t ≤ t_onset` | success for early-warning claim |
| **Detection at injection** | `hat_t = t_inj` | neither success nor automatic failure; reported separately |
| **Post-injection detection** | `hat_t > t_inj` | failure of early-warning claim |
| **Missed detection** | no detection before `T` | failure |
| **Premature alarm** | `hat_t` occurs while `s_u < θ` for all `u ≤ hat_t` (false positive before any instability) | counted against specificity |
| **Undefined statistic** | window too short or zero variance → detector returns UNDEFINED | neither success nor failure; excluded from binomial denominator or reported as a distinct category |

P1 (below) is scoped exclusively to the genuine-early-warning class. Detections at or after injection are reported but do not satisfy the early-warning success criterion.

---

## 3. Primary statistic: conventional temporal lag-1 autocorrelation (exact causal definition)

**Choice.** The primary statistic is **conventional temporal lag-1 autocorrelation** of a scalar series derived from the residual trajectory, not adjacent-vector centered cosine similarity. Classical critical-slowing-down (CSD) theory predicts a *rise* in temporal autocorrelation (and variance) as a bifurcation is approached; the present hypothesis concerns whether that (or a related) temporal statistic collapses or otherwise signals the registered onset under the specific generator. Adjacent-vector cosine similarity is retained only as a named alternative (Appendix C) and is not the primary claim.

**Construction (causal).**
1. At decision time `t` form the trailing window of residuals `W_t = {r_{t−w+1}, …, r_t}` (or the longest available prefix if `t < w−1`).
2. Reduce each residual to a scalar by projection onto the leading principal component of `W_t` (computed solely from `W_t`). This yields a scalar series `c_{t−w+1}, …, c_t`.
3. Compute the ordinary sample lag-1 autocorrelation of that scalar series:

```
γ̂_t =  Σ_{k=t−w+1}^{t−1} (c_k − c̄)(c_{k+1} − c̄)   /   Σ_{k=t−w+1}^{t} (c_k − c̄)²
```

where `c̄` is the mean of the same window. If the denominator is zero the statistic is UNDEFINED.

**Notation.** The lag-1 autocorrelation is written `γ̂_t` (gamma-hat). The spectral-gain variable of the generator is written `ρ_t` (rho). The two are never given the same symbol.

**Detection rule.** The first `t` at which `γ̂_t < τ` (inclusive) and the statistic is defined is reported as `hat_t`. If no such `t` occurs, the detector returns “no detection”.

**Threshold.** Proposed `τ = 0.65` (inclusive). Still unfrozen until any future W2 registration.

---

## 4. Fully frozen generator specification (SyntheticResidualMap-Causal v3)

Stand-in name: **SyntheticResidualMap-Causal**. One exact specification; unused alternatives moved to Appendix C.

**State.** Residual vector `r_t ∈ ℝ^d`.

**Initial conditions.**
- `r_0 ∼ 𝒩(0, σ₀² I)` with `σ₀ = σ`.
- Spectral gain `ρ_0 = ρ_init < 1`.

**Pre-onset map.**
```
r_{t+1} = ρ_t · Q · r_t + ε_t ,   ε_t ∼ 𝒩(0, σ² I)
```
where `Q` is a fixed orthogonal matrix (the identity is admissible and is the default; any other fixed orthogonal matrix is an equivalent re-labeling of coordinates). The gain evolves deterministically:
```
ρ_{t+1} = min( ρ_t + α · ‖r_t‖² , ρ_cap )
```
with `α > 0` and a registered upper cap `ρ_cap` that prevents numerical overflow before threshold crossing. The precursor scalar is identical to the gain:
```
s_t ≜ ρ_t
```
`t_onset` is the first `t` with `s_t ≥ θ`. The irreversible change is applied when the map that produces `r_{t_inj}` is evaluated, i.e. at step `t_inj = t_onset + 1`.

**Post-injection map (permanent).**
```
A_post = ρ_post · R_φ · Q ,   ρ_post > θ ,   φ = π/6 fixed
r_{t+1} = A_post r_t + ε_t    for all t ≥ t_inj − 1
```
`R_φ` is the plane rotation by angle `φ` in the first two coordinates (and identity elsewhere). Once applied, `A_post` remains fixed for the remainder of the trajectory.

**Proposed constants (still unfrozen until W2).**

| Symbol    | Proposed value | Role |
|-----------|----------------|------|
| `d`       | 32             | residual dimension |
| `T`       | 40             | trajectory length |
| `N`       | 200            | independent trials |
| `ρ_init`  | 0.85           | initial spectral radius |
| `α`       | 0.008          | gain-drift coefficient |
| `ρ_cap`   | 1.2            | numerical ceiling |
| `θ`       | 0.97           | instability threshold |
| `ρ_post`  | 1.05           | post-injection radius |
| `σ`       | 0.05           | noise standard deviation |
| `φ`       | π/6            | irreversible rotation angle |
| `w`       | 8              | trailing-window length |
| `τ`       | 0.65           | autocorrelation detection threshold |

**Observation timing.** Residuals are observed after each map application. The detector at time `t` sees only `r_0 … r_t`.

---

## 5. Irreversibility — what the model actually guarantees

A permanent change of the linear operator does **not** by itself prove that a stochastic trajectory can never re-enter a previously visited region of state space. Under additive Gaussian noise the state space remains fully reachable in principle.

**Guaranteed property.** After `t_inj` the expected one-step map is the affine system with linear part `A_post` whose spectral radius exceeds 1 (or exceeds the pre-onset radius by a registered margin). Consequently:

- the deterministic skeleton (`σ = 0`) diverges from the origin along the dominant eigenspace of `A_post`;
- the second-moment matrix of the noisy process satisfies a linear recurrence whose homogeneous part is unstable;
- sample paths exhibit a positive Lyapunov exponent associated with that eigenspace (to be verified by the reference implementation if the study proceeds).

**What is *not* claimed.** Almost-sure non-return to any particular bounded set, or topological conjugacy to a different dynamical system. The operational meaning of “irreversible” for the experiment is that the post-injection linear operator remains permanently altered and the second-moment dynamics become expansive; recovery of the pre-injection attractor would require an external restorative intervention that the generator does not provide.

---

## 6. Competing hypotheses and baselines (M14)

**H0 — residual-norm growth.**  
`‖r_t‖ / ‖r_{t−1}‖ > γ` (γ set so that the baseline has the same decision opportunities as the autocorrelation detector). Claim: this alone is sufficient.

**H1 — classical critical-slowing-down (CSD).**  
Near a bifurcation the dominant eigenvalue approaches the unit circle from below, producing a characteristic *rise* in both lag-1 temporal autocorrelation and variance (Scheffer et al., “Early-warning signals for critical transitions,” Nature 2009; Dakos et al., subsequent methodological literature). The CSD rival therefore predicts that a variance (or residual-energy) threshold, or a threshold on *increasing* `γ̂_t`, already captures the approach to instability; a claim of “autocorrelation collapse” must be tested against this rising-autocorrelation baseline. The experiment therefore includes:
- a residual-variance detector `v_t > v_thresh`;
- an optional rising-autocorrelation detector that fires when `γ̂_t` exceeds a high threshold (the classical CSD direction).

The present hypothesis is *not* required to deny CSD; it must show that the chosen statistic and direction (crossing of a low threshold `τ`) supplies information about the registered onset that the classical rising-variance / rising-autocorrelation signatures do not already supply under this generator.

**H2 — direct-precursor oracle.**  
Threshold on the known gain `s_t = ρ_t`. This is the strongest causal baseline. Autocorrelation does not receive `ρ_t` as an explicit input; any useful claim is that it recovers onset timing from the residual trajectory alone. Performance relative to the oracle is reported for calibration, not as a superiority claim.

**Baseline set.**
1. Residual-norm growth (H0).  
2. Residual variance (CSD).  
3. Rising lag-1 autocorrelation (classical CSD direction).  
4. Direct-precursor oracle (H2).  
5. Falling lag-1 autocorrelation (proposed primary statistic).

---

## 7. Numbered candidate predictions (NOT REGISTERED)

**P1 (candidate — genuine early warning).**  
On `N = 200` independent trials, the first *defined* detection `hat_t` of the primary statistic satisfies `hat_t ≤ t_onset` on at least 70 % of the trials for which the statistic is defined at least once before `T`. Exact binomial test against null success probability 0.5, two-sided, α = 0.05.  
- Trials on which the statistic is never defined are excluded from the denominator and reported separately.  
- Detections at `t_inj` or later do not count as successes for P1.

**P2 (candidate — superiority over non-oracle baselines).**  
Mean absolute error `|hat_t − t_onset|` (computed only on trials that produce a defined detection) of the primary statistic is strictly smaller than that of both the residual-norm baseline and the residual-variance baseline (paired comparisons, same trials).

**P3 (anti-vacuity).**  
When `θ` is set so high that `s_t` never reaches it, the primary statistic remains ≥ `τ` (or UNDEFINED) for all `t` on at least 95 % of trials; the detector issues no genuine-early-warning false positive on those trials.

**P4 (robustness).**  
Under a 2× increase in `σ²`, the success rate defined in P1 remains ≥ 0.60.

**P5 removed.**  
The earlier oracle-comparison prediction is dropped as largely redundant with P1 once the oracle is retained as a calibration baseline rather than a hypothesis under test. Oracle performance is reported descriptively; no formal success threshold is attached to it.

Falsification of the central claim occurs if P1 or P2 fails under the (still-to-be-frozen) constants.

---

## 8. Statistical controls, null hypotheses, and noise measurement

**Null for P1.** Exact binomial test of success count against `p_0 = 0.5`. Justification: under a completely uninformative detector the probability of landing inside the early-warning window by chance, given the relative lengths of the pre-onset and post-onset intervals under the proposed constants, is not known a priori to be far from ½; 0.5 is therefore a conservative, pre-specified null. If a tighter analytic null becomes available it may be substituted only by an explicit deviation note after registration.

**Paired comparisons for P2.** On each trial the absolute errors of the primary statistic and of each baseline are computed; the paired differences are tested by an exact or sign-based procedure (no parametric assumption required). Multiple baselines are compared; a simple Bonferroni correction across the two primary paired tests (norm and variance) is applied, or an explicit statement that the family-wise error rate is uncontrolled is recorded. The rising-autocorrelation CSD baseline is treated as a descriptive rival, not as a third formal paired test, unless a later registration elevates it.

**Noise measurement (C-NOISE).** Variability is measured across *independent realizations* of the full generator (independent draws of the noise sequence and of `r_0`), not by repeating an identical deterministic seed. At least three independent realizations are examined before any threshold is interpreted; the observed spread of `γ̂_t` at matched time indices is recorded. A registered bound smaller than that spread is declared unresolvable at the chosen `N`.

**C-STAT.** All tests are fixed-horizon. No sequential peeking. e-process machinery remains available for any later empirical stage that introduces sampling over real-model residuals.

**Sabotage / anti-vacuity (M3, C-BUILD).**
- Force `γ̂_t ≡ 1` for every `t` → instrument returns GATE: FAIL and exits 1.  
- Zero-variance window → UNDEFINED, never a false-positive detection.  
- Missing or malformed residual sequence → DENY / UNVERIFIED.

**Verdict line required of any future reference script.**
```
VERDICT k of m as registered
DIGEST: <sha256 of rounded numerical vector>
```

---

## 9. Epistemic status

- Established mathematics: temporal lag-1 autocorrelation, spectral radius of linear maps, second-moment dynamics of linear SDEs / maps with additive noise, classical CSD early-warning signatures (rising autocorrelation and variance).  
- Derived / conjectured: that a *fall* of lag-1 residual autocorrelation below a fixed threshold supplies early-warning information about the registered onset that residual-norm and residual-variance baselines do not already supply under this generator.  
- Unverified: every numerical prediction; behaviour under real transformer residuals.  
- No experiment has been run. No numbers have been observed.

---

## 10. Prior art (summary)

Spectral geometry of residual streams (Naderi et al. 2024; Fernando & Guitchounts 2026; Tao et al.; Seq-VCR). Classical critical-slowing-down literature (Scheffer et al. 2009 and methodological successors). None of the cited works registers a *falling* lag-1 residual autocorrelation as an online detector of an observable instability onset that causally precedes an irreversible map change, under a fully specified synthetic generator, with the exact baseline contrast required here. Overlap is acknowledged; novelty is restricted to the online causal framing and the experimental contrast.

---

## 11. Limitations and confounders

- Synthetic linear map may not capture non-normal or attention-induced residual dynamics of real transformers.  
- `τ = 0.65` is arbitrary.  
- The precursor `s_t = ρ_t` is an internal generator variable; a real system needs an operational analogue.  
- Window length, dimension and noise interact; sensitivity is a door.  
- Irreversibility is defined via permanent operator change and expansive second-moment dynamics, not via almost-sure non-return of sample paths.  
- Original exogenous-injection design remains on the permanent record as DEFECTIVE.

---

## 12. Attribution and provenance (M13)

- Entire proposal (original draft + all corrections through v3) authored by Grok (xAI).  
- Human review level actually performed: **none** (independent owner read-only reviews have occurred; they do not constitute co-authorship or elevation of review level for the AI contribution).  
- No code executed, no numbers observed, no private material consulted.

---

## 13. Smallest experiment that could refute the main prediction

Once a reference script is authorized and constants frozen under W2, a single run of the `N = 200` trial matrix. If the genuine-early-warning success rate falls below 0.70, or if mean absolute error is not strictly smaller than both the residual-norm and residual-variance baselines, the corresponding candidate prediction is refuted.

---

## 14. Open, unexecuted next prediction (M15)

**P6 (unrun, candidate).** When the same lag-1 residual autocorrelation statistic is computed on residual streams extracted from a publicly available small transformer trained on modular arithmetic, under an operational definition of instability onset analogous to the synthetic precursor, the statistic still yields genuine early warnings of irreversible digit errors on a majority of held-out problems.  
Left deliberately unexecuted and unregistered.

---

## Appendix A — Historical record of the first draft (DEFECTIVE, M12)

The initial proposal (2026-10-21) used an exogenous random injection time independent of the trajectory and claimed a 70 % early-warning rate for the step immediately preceding that injection. That construction is causally invalid for an online detector and is marked **DEFECTIVE**. The scientific intent is preserved; the mechanism has been rewritten so that the detector reacts to an observable instability precursor. No silent rewriting of the original claim has occurred.

---

## Appendix B — Change log

**v1 → v2:** causal precursor introduced; exogenous injection marked defective.  
**v2 → v3 (this document):**  
- Timing inconsistency corrected: detector at `t` uses only `r_0…r_t`; genuine early warning strictly `hat_t ≤ t_onset`.  
- Primary statistic redefined as conventional temporal lag-1 autocorrelation of a leading-PC scalar series; adjacent-vector cosine similarity demoted to Appendix C.  
- Variable clash resolved: gain = `ρ_t`, autocorrelation = `γ̂_t`.  
- Generator frozen to one exact specification (drift law, Q = I default, rotation construction, initial conditions).  
- Irreversibility restated as permanent operator change + expansive second-moment dynamics; almost-sure non-return not claimed.  
- P1 scoped to genuine early warning; detection-at-injection and post-injection reported separately.  
- Binomial null, paired tests, multiple-comparison handling, and independent-realization noise measurement specified.  
- Classical CSD (rising autocorrelation + variance) retained as explicit rival.  
- Redundant oracle-threshold prediction (old P5) removed; oracle retained as calibration baseline only.  
- Original defective hypothesis preserved in Appendix A.

---

## Appendix C — Alternatives retained as future research proposals (not part of the primary claim)

- Adjacent-vector centered cosine similarity as a primary statistic.  
- Non-identity fixed orthogonal matrices Q.  
- Alternative drift functions g(‖r‖²) other than identity.  
- Singular-value tracking of the recent update operators as precursor instead of the explicit gain `ρ_t`.  
- Almost-sure non-return arguments under additional assumptions (e.g., large-deviation bounds).

---

*Checklist (proposal stage):*  
[x] status label honest (SPECULATIVE / NOT RUN / NOT REGISTERED)  
[x] claims can be precisely wrong (M1)  
[x] numbered candidate predictions present and scoped to genuine early warning  
[x] anti-vacuity path described (M3)  
[x] trigger table principles respected (M16)  
[x] simplest rival + CSD rivals + oracle baseline stated (M14)  
[x] at least one open door (M15)  
[x] AI attribution and review level stated (M13)  
[x] causal objection and subsequent review issues addressed; original defect preserved (M12)  
[x] exact generator, causal statistic, irreversibility property, timing classes specified  
[ ] formal registration (W2) — blocked  
[ ] reference code written — blocked  
[ ] any experiment executed — forbidden without separate authorization

*Vincit Omnia Veritas.*
