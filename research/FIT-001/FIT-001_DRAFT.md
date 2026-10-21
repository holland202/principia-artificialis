# FIT-001 — Function-Invariant Tomography
## Working research dossier — v3.1, pending Stage 0 contract amendment

**Project ID:** FIT-001  
**Repository:** Principia Artificialis (PA)  
**Research lead / originating AI contributor:** Kimi (Moonshot AI)  
**Human project owner and responsibility:** Chad Holland  
**Independent critique and dossier assembly:** ChatGPT (OpenAI, GPT-6)  
**As-of date:** 2026-10-21  
**Research status:** DRAFT / DESIGN ONLY / NOT REGISTERED / NOT EXECUTED  
**Authorization:** Documentation on a review branch only. No training experiments, protocol registration, publication, or changes to main are authorized by this dossier.  
**Base methodology:** PA METHOD.md at commit 7c11e92358c33f0c9b787834ddbd59d1f3bd395d; read with WORKFLOW.md and CONTROLS.md.  
**Source basis:** FIT-001 v1 proposal; Kimi v2 revised specification; Kimi v3 final protocol review; Kimi v3.1 final corrected specification; subsequent ChatGPT technical reviews, all conveyed in project-owner conversations. These source messages are NOT yet preserved as commit-pinned, independently authenticated source artifacts in this repository.

> **Read this first.** This document is a reconstruction and working record of proposals and critiques, **not a registered experimental protocol or verified result**. Kimi reports having run local float64 mathematical counterexamples; their code, raw logs, machine manifest, and independent reproduction have not been supplied to this branch. No FIT-001 Stage 0, 1, or 2 training runs have been performed or verified here. Numerical observations below are explicitly **contributor-reported** unless otherwise stated.

---

## 1. Research question and scope

**Question:** At a specified post-memorization checkpoint, how much information about subsequent grokking/generalization can be attributed to (A) a model's observed function, (B) gauge-invariant but representation-dependent parameters, (C) optimization-landscape measurements, or (D) training trajectory summaries, under matched information and tuning budgets?

This replaces the original, overbroad ambition to claim the *first* state-based early prediction of grokking. Prior work already studies early prediction, training dynamics, circuit formation, and numerical-environment instability. The possible FIT contribution is a **controlled comparison of predictive information classes**, not priority over every existing grokking predictor.

The study is **associational**. Predictive incremental information does not imply the feature causes grokking. Task-specific behavior on a discrete modular-addition grid must not be conflated with behavior of the continuous neural function between valid inputs.

### Proposed falsifiable contrasts (not yet preregistered)

- **H-FUNC:** Frozen probe-output features (F1), and separately encoding-relative input-Jacobian features (F2), provide held-out incremental predictive signal over matched baselines.
- **H-PARAM:** Gauge-invariant, representation/parameter-dependent features (F3–F5 and tanh-specific spectra/norms) provide additional signal beyond F1/F2 and baseline models.
- **H-NULL:** Some or all information classes contribute no meaningful incremental signal at the tested checkpoint and resolution.
- **H-NOISE:** Changes in numerical reduction order or other execution details can change grokking events sufficiently to limit cross-run attribution claims.
- **H-CONTROL:** Required anti-vacuity, gauge-copy, initialization, target-randomization, and probe-resampling controls behave as predicted.

These are **research hypotheses and design targets**, not formal numbered PA predictions. Any formal registration must use M2/M3, freeze its thresholds and inputs in a separate commit, and happen **before** confirmatory execution.

## 2. Development history and correction record

| Version | Main development | Claims withdrawn or repaired |
| --- | --- | --- |
| v1 | Early grokking prediction using supposedly invariant model-state features | Priority claim, parameter NTK invariance, and normalized activation-spectrum invariance were challenged. |
| v2 | Redesigned to information attribution across function / landscape / trajectory; introduced numerical-environment replication arm | Identified incorrect tanh group, unnecessary bias-free ReLU restriction, representation-dependent features, and ill-defined projector inverse. |
| v3 | Corrected tanh signed permutations and bias-coupled ReLU rescaling; separated function-intrinsic F1/F2 from gauge-invariant parametrization F3–F5; corrected run-count arithmetic | Raw relative-threshold pseudoinverse was still not numerically gauge-invariant; “500 evaluations” confused with “500 training steps”; ceiling and controls needed repair. |
| v3.1 | Proposed column-normalized projector implementation, revised sustained-event definition, five-cell Stage 1 variance plan, equivalence criteria, correct negative controls, encoding-relative F2, and restricted thread-discordance tiers | Width-256 Fourier sufficiency withdrawn; previous “exact bit-identical projector” claim withdrawn; numerical projector equality replaced by tolerance-based acceptance. |
| Post-v3.1 review | Identified final Stage 0 execution-contract gaps | Optimizer/decay semantics, memorization-window arithmetic, unproven width-113 construction, split/evaluation details, near-horizon censoring, resource estimates, and feature-layer definitions still need explicit resolution. |

**Preservation rule:** Do not erase the withdrawn claims or the failed reasoning. The above is a correction history, not evidence that all defects have been experimentally eliminated.

## 3. Mathematical objects and stated symmetry classes

### 3.1 Architecture symmetries — analytical claims to preserve and independently check

For a conventional feed-forward tanh model, hidden-unit permutations together with coordinated sign flips of incoming weights, hidden biases, and outgoing weights preserve the computed function: tanh(-z) = -tanh(z). In the generic architecture considered, this signed-permutation (hyperoctahedral) action is a guaranteed symmetry; do not assert it is the **complete** equivalence group of all possible parameterizations without qualifying degeneracies.

For a ReLU hidden unit, multiplying the incoming weights **and bias** by d > 0 and dividing its outgoing weights by d preserves the function because ReLU(dz) = d ReLU(z). Permutations and such positive diagonal rescalings are guaranteed symmetries; negative signs generally are not.

Exact mathematical invariance is distinct from floating-point output identity. Hardware order of operations may affect even nominal gauge-copy outputs.

### 3.2 Proposed feature classes

| Code | Feature | Scientific classification | Principal qualification |
| --- | --- | --- | --- |
| F1 | Spectrum of output kernel Y Yᵀ, with Y = f(X_probe) | Function-level, intrinsic to the **fixed input-domain readout** | Depends on chosen probe inputs, output convention, and preprocessing. On the finite task grid it can be studied as a task-relative functional. |
| F2 | Singular values of input Jacobian Df at probes | Gauge-invariant network-function measurement, **encoding-relative** | The discrete modular-addition problem does not canonically determine off-grid derivatives; freeze the continuous input encoding and derivative convention. |
| F3 | Readout alignment norm(P_l y)² / norm(y)² | Gauge-invariant **subspace/representation-dependent** | P_l projects onto col(H_l), not a unique property of f; define the target vector y and whether labels are accessible. |
| F4 | Normalized overlap tr(P_l P_m)/sqrt(r_l r_m) | Gauge-invariant **representation-dependent** | Must name two valid representation matrices with common probe axis; define rank-zero and degenerate cases. |
| F5 | ReLU path norm, including bias paths, where appropriate | Gauge-invariant parametrization functional | Requires exact architecture, path definition, and treatment of biases; **not** universally determined by f. |
| Additional tanh | Activation Gram spectra and per-layer Frobenius norms | Signed-permutation invariant | Invariant under the specified tanh symmetry, not necessarily unique to the input-output function. |

Parameter-space NTK and uncorrected ReLU activation spectra are **excluded as general gauge invariants**. A gauge-invariant measurement need not be function-intrinsic: different nonequivalent networks may implement the same function.

### 3.3 Projection theorem versus computational implementation

Mathematically, for an activation matrix H and invertible diagonal D,

    col(HD) = col(H), hence P_col(HD) = P_col(H).

However, a **numerically truncated** SVD with a relative singular-value threshold can retain different directions after column scaling. Kimi reported the following unreplicated numerical examples for a 2048×256 activation matrix with singular values near the cutoff:

- Condition-number 2 gauge: retained rank 253 → 252, projector difference norm approximately 5.8e-3.
- Condition-number 10 gauge: retained rank 253 → 250, difference norm approximately 9.2e-3.
- Column normalization before thresholding: stable rank under those examples, deviation approximately 4.5e-8.

**Status:** reported computational observations, not independently reproduced or established as universal bounds.

**v3.1 proposed algorithm:** normalize nonzero activation columns to unit norm before a singular-value decomposition; use a predeclared relative cutoff 1e-10, with sensitivity cuts at 1e-8 and 1e-12; test gauge copies with condition number ≤ 10; require feature deviation no greater than 1e-6 times a *precisely defined feature scale*; record a singular-value “flip-window” statistic. Need to specify zero-column handling, sign convention, near-zero denominators, numerical precision, norm choice, and scaling when feature magnitude is zero. Column normalization addresses positive column scaling in the ideal case but does **not** by itself prove tolerance under all ill-conditioned inputs.

**No execution acceptance claim may be made until the invariant implementation and adversarial tests have independently inspectable code and output.**

## 4. Candidate tasks, architecture and measurement setup

**Canonical feasibility cell (proposed, not yet executable):**

- Task: modular addition modulo p = 113 on 113² = 12,769 ordered pairs.
- Inputs: one-hot encoding of each summand, concatenated (nominal input dimension 226).
- Candidate architecture: two-layer tanh multilayer perceptron, nominal hidden width 256, biases included; precise layer-counting convention and output head remain to be frozen.
- Proposed optimization: full-batch Adam **claimed**, learning rate 1e-3, weight decay 1.0. **Open blocker:** Adam with coupled L2 decay and AdamW with decoupled decay differ materially; freeze the exact implementation, parameters, epsilon, precision and framework before use.
- Training fraction r = 0.4; freeze actual integer train/probe/test indices and sampling convention. Probe set target m = 2048 disjoint from training and evaluation sets; do not sample with leakage or allow probe-derived labels into label-free features.
- Horizon H = 100,000 optimizer updates; numerical execution pinned to one thread for canonical runs with CPU, BLAS and library manifests.
- Stage 0 seed proposal: 1, 2, 3, 4, 5. Seed handling must cover all randomness sources and data splits.

**Capacity caution:** Kimi withdrew a purported 224-unit Fourier generalization construction for tanh. Kimi's replacement width-113 “exact indicator-basis memorization” claim was challenged in subsequent review and is **not established** by the supplied argument. Stage 0 is a feasibility test precisely because width-256 training dynamics and generalization are not guaranteed.

### Timing definitions and unresolved boundary conditions

- **Training step:** one optimizer update. **Evaluation:** measurement without an optimizer update.
- **Proposed generalization time t_g:** first evaluated training step t for which held-out accuracy is at least 99% at **each** of t, t+100, t+200, t+300, t+400, t+500, i.e. a 500-training-step window sampled at six evaluations. A 95% threshold is a separately reported robustness variant. Freeze threshold comparisons exactly.
- **Proposed memorization time t₂:** sustained 100% training accuracy across consecutive evaluations nominally 10 steps apart. **Correction still required:** ten evaluations cover 90 training-step intervals, not 100; either use eleven observations including both endpoints or define a 90-step window.
- **First-hit time t_m** and t₂ must have unambiguous separate meanings and recorded output names.
- **Right censoring:** runs not observed to satisfy the complete t_g window by H are censored. Define whether a window starting at H-500 may be confirmed, whether training/evaluation extends beyond H, the minimum event-observation horizon, and how missing final windows are classified.
- **Near-horizon censoring** and numerical instabilities must be logged distinctly, never silently labeled “did not grok.”

## 5. Proposed experimental stages — NO EXECUTION AUTHORIZED

### Stage 0 — feasibility, canonical cell

**Exactly five canonical runs**, seeds 1–5, *only after approval*. Proposed per-run output: full environment manifest and hashes; seed/split identity; t_m and t₂ as defined; t_g or exact censor reason; final test accuracy; numeric failure indicator; evaluation logs; wall time and measured overhead; implementation/source commit identity.

Proposed decision: at least 3/5 runs exhibit a fully observed grokking event within the horizon for feasibility. If two or more runs are numerically unstable, stop and report separately. Kimi proposed a fallback ladder to width 512, width 1024, then a small transformer, each with five runs; **these fallbacks are explicitly not authorized** by creation of this dossier and need separate owner approval and a documented amendment.

Kimi estimated 12–40 CPU-hours for five canonical runs, but this is a **planning estimate only**, unsupported by a committed benchmark or measured FLOP model. Define a wall-time/CPU ceiling and what happens if exceeded.

### Stage 1 — information and numerical-environment feasibility

**Design proposal: 54 runs total.** Five weight-decay cells {0.3, 0.5, 1.0, 2.0, 4.0} × six seeds = 30 canonical runs, plus a 12-seed paired 1-thread/4-thread comparison = 24 runs. Specify whether paired seeds duplicate canonical seeds and whether run counts reflect new executions, not just distinct seeds.

Kimi proposed the configuration-level statistic

    rho_max² = sigma_between² / (sigma_between² + sigma_within²).

**Open interpretation:** this ratio is not a general proven ceiling for run-specific feature prediction. Five configuration cells provide only four between-cell degrees of freedom, with broad uncertainty; grouping, outcomes, censoring and allocation determine what can actually be inferred. Treat this as an exploratory heterogeneity diagnostic unless a valid gate interpretation and estimation procedure are demonstrated.

**Proposed numerical-discordance tiers (n = 12 paired seeds):** under 5% observed discordance → proceed; 5–25% → proceed with numerics modeled and canonical runs single-thread; above 25% → stop the cell. At n = 12, rates are quantized in 8.33 percentage-point increments; the “under 5%” tier is equivalent to **zero flips**. Zero flips does not establish low population discordance. This is a coarse screen only.

Any Stage 1 approval requires a separate review after Stage 0, along with frozen predeclared gates and uncertainty treatment.

### Stage 2 — pilot attribution

**Design proposal:** 100 training runs total, comprising 60 new seeds at r=0.4, 20 at r=0.3, and 20 at r=0.5. Distinct feature pipelines are evaluated on shared runs and should **not** be multiplied into the training-run count. Total proposed program: 5 + 54 + 100 = **159 executions** before optional extension/fallbacks.

Arms: fixed-probe F1/F2; gauge-invariant representation features; landscape comparator such as an independently implemented commutator-defect measurement; trajectory-only comparator as a separately budgeted ablation. Training and prediction tasks, information access and tuning budgets must be matched fairly.

**Exploratory statistics proposed:** logistic classifier for grok-by-H and regression of log t_g among observed generalizers; secondary Weibull accelerated-failure-time/survival analysis including censored runs. Complete-case regression conditions on a selected event group; the classifier alone does not automatically remove that selection bias. Freeze out-of-sample splits, calibrations, censoring procedure, covariates, baselines, and metric computations before any confirmatory claims.

**Power caution:** Fisher-z single-correlation heuristics are not a valid power calculation for incremental held-out differences between fitted models under censoring and model selection. Use an explicitly simulated design or defensible analytic comparison that respects dependence and estimated model uncertainty.

### Outcome labels (proposed, not registered)

- **Success:** preregistered features deliver a practically meaningful, statistically supported held-out incremental gain over relevant comparators, with all required controls behaving correctly.
- **No detectable benefit:** pilot confidence interval overlaps zero, without asserting absence of an effect.
- **Negligible benefit established:** equivalence criterion passes for a prespecified margin using a valid inferential procedure (Kimi suggested Δcorrelation ±0.10 and ΔAUC ±0.03 as margins; not independently justified).
- **Inconclusive:** insufficient events, unstable environment, low power, censoring or missingness preventing an interpretable result.
- **Protocol failure:** an execution invariant, safety gate, or predeclared stop rule fails; report the failure distinctly from a negative scientific result.

The “Tier A negative” language in Kimi v3.1 must not turn “CI includes zero” into evidence of absence. State what the evidence supports, not more.

## 6. Controls and methodological threats

| Control or threat | Intended measurement | Still to resolve |
| --- | --- | --- |
| Gauge-copy tests | Confirm numerical invariance of proposed feature computation | Zero columns, signed permutations, ill-conditioned matrices, both raw and normalized SVD, precise tolerances. |
| Random targets for F3 | Alignments approach chance expectation under a correctly defined isotropic target null | The expected rank/m expression depends on normalization and target distribution; specify null exactly. |
| Initialization-time readout | Test whether predictive information is already present before learning | Prediction at initialization would weaken the “learning-emergent” story, but need not falsify general predictive utility. |
| Random-label training | Prevent false “generalization” claims where labels lack task structure | Define data generation and distinguish random-label effects on training from test-set metrics. |
| Probe resampling | Stability of predictive readouts to probe choice | Predefine strata, sample sizes, tolerance and whether probes can be reused. |
| Time-to-memorization confound | Compare readouts to t_m and early loss information | Must freeze equal information budgets and avoid future leakage. |
| Numerical reduction-order test | Quantify reproducibility across thread counts | Pair exact seeds/splits and record environment; do not assume bit-identical matrices. |
| Held-out task families | Assess cross-task transfer | Only one task family in pilot: general cross-family claims remain untested. |
| Landscape and trajectory baselines | Compete against simplest credible alternatives | Confirm baseline implementation, original license/derivation, and feature access times. |
| Encoding-transfer arm | Whether F2 signal survives input encoding changes | Training a new encoding is a distinct experiment and **not included** in the current fixed run counts. |

**Additional feature-definition blocker:** A nominal two-layer MLP may supply only one hidden activation space. F4 cross-layer overlap requires two specified comparable representation spaces; F3 and F4 must name their actual layer inputs and shapes, or be omitted from the Stage 0 implementation. Stage 0 need not implement F1–F5 if it is strictly a grokking-feasibility test, but future feature-stage contracts must.

## 7. Literature and novelty ledger (source IDs supplied by Kimi)

The following are *bibliographic leads and contributor-reported interpretations*, not a statement that this branch has independently reproduced their results or completed a systematic novelty search.

| Work | Locator | Relevance / qualification |
| --- | --- | --- |
| Power et al. (2022), grokking | https://arxiv.org/abs/2201.02177 | Establishes the phenomenon and modular-arithmetic context. |
| Thilak et al. (2022), slingshot | https://arxiv.org/abs/2206.04817 | Optimization dynamics. |
| Nanda et al. (2023) | https://arxiv.org/abs/2301.05217 | Progress measures and circuit formation. |
| Notsawo Jr et al. (2023) | https://arxiv.org/abs/2306.13253 | Early loss-curve spectral warning. |
| Varma et al. (2023) | https://arxiv.org/abs/2309.02390 | Circuit efficiency. |
| Merrill et al. (2023) | https://arxiv.org/abs/2303.11873 | Competing circuit account. |
| Unterthiner et al. (2020), StatNN | https://arxiv.org/abs/2002.11448 | Weight-statistics model performance prediction; some statistics are permutation-invariant. |
| Neural functional networks | https://arxiv.org/abs/2302.14040 | Learned weight-space models. |
| Universal neural functionals | https://arxiv.org/abs/2402.05232 | Symmetry-aware weight-space representation. |
| Prieto et al. (2025) | https://arxiv.org/abs/2501.04697 | Numerical stability and grokking. |
| Xu (2026), integrability / commutator defect | https://arxiv.org/abs/2602.16746 | Strong adjacent landscape-level warning and intervention claims. |
| Xu (2026), other families | https://arxiv.org/abs/2602.16967 | Claimed cross-task early-warning analysis. |
| Xu (2026), multi-task | https://arxiv.org/abs/2602.18523 | Further comparator lead. |
| Xu (2026), functional modes | https://arxiv.org/abs/2604.06256 | Function-space theory. |
| Ootani (2026), Glimmer-1 | https://arxiv.org/abs/2607.05104 | Seed and numerical-environment reproducibility. |
| Statistical Vignettes (2026) | https://arxiv.org/abs/2610.18811 | Recent plateau-duration theory, revisit novelty. |

A claim of “first” remains **unverified**. Before publication: cross-check the original papers, exact tasks, result definitions, code and license; obtain commit-pinned references and note any source corrections. The claimed external Verma permutation-symmetry study and Omnigrok were not fully authenticated in the supplied materials.

## 8. Final Stage 0 execution-contract blockers (owner review required)

A narrow addendum was requested after v3.1, but its completed content has **not** been supplied in the source conversation used to prepare this file. Before approval:

1. Freeze **exact optimizer** (coupled Adam vs. decoupled AdamW), hyperparameters, framework/library versions, initialization, dtype and hardware thread control.
2. Correct the **t₂ 90-versus-100-training-step** evaluation-window arithmetic and avoid mixing t_m, t₂, and t_g.
3. Prove or withdraw the **width-113 exact memorization** claim. Do not silently replace it with a different capacity claim.
4. Provide the **five seeds**, complete disjoint split/label indices (or reproducible generator), deterministic sample/evaluation protocols, output schema, and exact horizon-edge censoring.
5. Produce a **Stage 0 run manifest**, evidence retention and independent replay procedure, resource ceiling, exact stop/failure conditions, and decision rubric.
6. Reconcile Stage 0-only feasibility measurement with future F3/F4 representation definitions and the proposed cross-encoding extra run budget.

The prior review explicitly restricted any prospective approval to **five canonical Stage 0 seeds**, not the width fallbacks, Stage 1, Stage 2, or repo registration. **As of this dossier, even Stage 0 is not authorized.**

## 9. Proposed provenance and evidence ledger

| Artifact / assertion | Source or authority | Status |
| --- | --- | --- |
| FIT v1 proposal | Kimi conversation, supplied by owner | Historical design, source transcript not committed |
| FIT v2 revised specification | Kimi conversation, supplied by owner | Historical design |
| FIT v3 final protocol review | Kimi conversation, supplied by owner | Historical design |
| FIT v3.1 corrected specification | Kimi conversation, supplied by owner | **Current candidate**, not approved |
| Numeric projector/NTK/gauge counterexamples | Kimi self-reported float64 calculations | **Not independently reproduced; no code/trace attached** |
| ChatGPT technical objections | ChatGPT conversation and review | Independent **critique of text**, not independent empirical reproduction |
| Literature table | Kimi bibliography and subsequent review | Source leads; validation incomplete |
| Stage 0 five-run outputs | None | **NOT RUN** |
| Stage 1/2 outputs | None | **NOT RUN** |
| Human technical validation | No line-by-line or executed outcome review evidenced | **Direction / project supervision only** |
| Formal PA registration | None | **NOT REGISTERED** |

**AI provenance chain under M13:** Kimi (Moonshot AI) originated and repeatedly revised the research specification; ChatGPT (OpenAI GPT-6) criticized mathematical and experimental assumptions and assembled this archival dossier; Chad Holland directed scope and authorized **documentation on a review branch**. Human review is **direction only**; technical or empirical validation is not inferred.

## 10. Triggered control applicability (planning screen only)

The authoritative definitions and rule text remain in PA METHOD.md / CONTROLS.md; this table is a planning checklist, **not** a registration.

| Trigger | Control | Applicable? | Why |
| --- | --- | --- | --- |
| Feasibility | C-FEAS | Yes | Unknown grok rate and architecture capacity. |
| Noise | C-NOISE | Yes | Same-seed numerical-environment differences and model stochasticity. |
| Statistics | C-STAT | Yes | Event rate, predictive contrasts, confidence/equivalence intervals. |
| Evidence | C-EVID | Yes | Logs, source identities, manifests, repeatable event classifications. |
| Independence | C-INDEP | Yes | Self-tests vs. independent replay and external paper reproduction. |
| External | C-EXT | Yes | Multiple external research references and baselines. |
| Device | C-DEVICE | Not for desktop-only Stage 0; review if phone claims are added | Hardware-specific claims require evidence. |
| Verdict code | C-BUILD | Yes once gate code is implemented | Gates must admit benign and sabotage cases. |
| Exploration | C-EXPLORE | Yes | Kimi has already described unregistered numerical mathematical exploration. |
| Method comparison | C-METHCOMP | Yes | Multiple information-class prediction baselines. |

## 11. Next decision / open scientific door

**Current recommendation:** Retain FIT-001 as a **draft working project**. Obtain and independently review the missing Stage 0 execution-contract addendum, then ask the owner for explicit approval **limited to five canonical feasibility runs**. Only later consider Stage 1 and Stage 2.

**Unrun, falsifiable next test (M15):** Given a frozen implementation and five canonical seeds, does the specified width-256 tanh model achieve held-out accuracy ≥99% sustained across the frozen 500-step evaluation window for at least three of the five runs by the defined horizon, without a forbidden numerical instability? A “no” is a legitimate feasibility result, **not** a refutation of the general information-attribution question.

**No experiment, reference code execution, new run, artifact promotion, public claim, or merge to main is effected by creating this file.**

---

*Vincit Omnia Veritas — preserve the question, the corrections, the failures, and the limits of the evidence.*
