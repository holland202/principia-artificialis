# Gemini Fisher information early-training demonstration — exploratory intake (2026-10-20)

**Status: EXPLORATORY / POST-HOC; NOT PREREGISTERED; NOT SCIENTIFICALLY VERIFIED.**

**Owner-directed intake:** Chad Holland. **Original proposed experiment and Python code:** Gemini (Google AI), as identified in the owner's October 2026 pasted response. **Local execution, diagnostic extension and critical review:** ChatGPT (OpenAI, GPT-6). **Independent human technical review:** not performed.

**Scope:** Public synthetic data only. No source, trace, or benchmark from Sovereign Veritas Dev was accessed or transferred.

## Known defects, caveats, and unperformed review (M8, M10)

- The proposal and intended thresholds were seen before execution: this is a retrospective demonstration, **not** a preregistered test or blind scientific replication.
- The program computes the expected Fisher metric for **four fixed inputs**, averaging over model-predicted output classes. This is not a study of unrestricted training data.
- The original Gemini script runs one step at learning rate 0.1. The three-rate sweep is a separately disclosed ChatGPT diagnostic using the same seeded initial weights each time.
- The 1e-5 positive-eigenvalue cutoff is a numerical convention, not a general analytic rank certificate.
- For four inputs, each with binary softmax output, the 24-parameter matrix has rank at most four. A numerical rank of four is therefore **structural**, not evidence of a newly formed low-dimensional manifold.
- A coordinate-dependent condition number is not an invariant geometric phase-transition detector. One seed, one small linear network and one gradient step cannot establish a universal transition.
- These scripts print values, but do **not** provide an official pass/fail instrument with sabotage controls (M3), pinned outcomes or independent validation.
- The submitted Gemini excerpt and exact model/version were not independently authenticated. Rights and MIT compatibility require review before merge.

## Observable question (W1)

For this fixed seeded linear network with two softmax output classes, how does the condition number of the numerically nonzero subspace of the empirical-input expected Fisher matrix change after one genuine cross-entropy gradient-descent step?

Model: W1 is 4×4, W2 is 2×4 (24 parameters). Inputs are the four identity-basis rows, labels alternate class 0/class 1, and the seed is 42.

The expected Fisher is the sample average over these four inputs of the probability-weighted outer products of score vectors for each of two classes:

\[
F(\theta) = \frac{1}{4}\sum_{i=1}^{4}\sum_{c=1}^{2}
p_\theta(c\mid x_i)\,\nabla_\theta\log p_\theta(c\mid x_i)
\nabla_\theta\log p_\theta(c\mid x_i)^\top.
\]

The reported metric is the after/before condition-number ratio, retaining only eigenvalues greater than 1e-5.

## Source and reproducibility (C-EXT; M6)

- **Original external code excerpt, unchanged in its calculations:** [Gemini's Fisher script](../../docs/external/gemini_fim_redesign_20261020.py). This preserves the Python source portion of the owner-pasted Gemini message; the surrounding private conversation has not been republished. Attribution acknowledges the external proposal, not any claimed endorsement or ownership transfer.
- **ChatGPT diagnostic extension:** [rerun and learning-rate sweep](gemini_fim_diagnostics_20261020.py).
- **Raw stdout:** [captured deterministic output](gemini_fim_stdout_20261020.txt).

Local execution date 2026-10-20, Python 3.13.5, NumPy 2.3.5. The scripts request no network resources. Run from repository root with:

    python experiments/information_geometry/gemini_fim_diagnostics_20261020.py

Original Gemini-script stdout, also preserved verbatim at the start of the raw output file:

    --- MATHEMATICALLY REDESIGNED RESULTS ---
    FIM Base Subspace Rank: 4
    Initial Cross-Entropy Loss: 0.6352
    Isolated Subspace Ratio: 0.9770

Additional **exploratory** diagnostic using identical initialization for each rate:

| Learning rate | Numerical nonzero rank | Condition ratio, after/before | Loss reduction |
|---:|---:|---:|---:|
| 0.01 | 4 | 0.99781771415784 | 0.44397662250948% |
| 0.10 | 4 | 0.97699796399309 | 4.36982679118421% |
| 0.50 | 4 | 0.86409491418111 | 20.29233287880907% |

The output also prints initial condition number 4.10699068080622 and the condition number after a 0.1 update 4.01252153328626. The rows are NOT statistically independent replications.

## Observation before interpretation; simplest rival (M9, M14)

**Observed:** This seed yields ratios below 1, not a sudden condition-number spike. A geometric discontinuity was not demonstrated.

**Not established:** intrinsic crystallization, physical phase transition, optimizer independence, learning-rate invariance, or a general law of early neural learning.

**Simplest rival:** smooth ordinary conditioning changes under gradient descent and existing rank deficiency caused by model non-identifiability and the tiny binary-class sample. This demonstration is consistent with the rival and does not discriminate it from a general crystallization theory.

The first Gemini proposal's greater-than-five ratio threshold applied to an invalid *different proxy*. It cannot be transferred retrospectively to this revised Fisher instrument. The revised proposal supplies no numeric acceptance threshold for a "significant" change. Therefore no universal hypothesis is declared confirmed or refuted.

Related speculative PA notes remain untouched: [Fisher information confidence](../../research_notes/003_fisher_information_confidence.md) and [Thermodynamic crystallization](../../research_notes/001_thermodynamic_crystallization_manifold.md).

## Trigger review (M16)

| Trigger | Control | Answer and handling |
|---|---|---|
| Feasibility | C-FEAS | No: fixed four-input construction, no eligibility count. |
| Noise | C-NOISE | No: deterministic seeded local run; platform float differences remain possible. |
| Statistics | C-STAT | No: no sampled population estimate or inferential significance. |
| Evidence | C-EVID | No: not a study of evidence freshness or provenance. |
| Independence | C-INDEP | Yes: explicitly no independent replication or human technical validation. |
| External | C-EXT | Yes: Gemini-supplied code excerpt preserved and credited separately from analysis. |
| Device | C-DEVICE | No: no hardware-performance claim. |
| Verdict code | C-BUILD | No: scripts report measurements, not binding verdicts. |
| Exploration | C-EXPLORE | Yes: outcomes were seen before registration; tracked as exploratory in FORKS.md. |
| Method comparison | C-METHCOMP | No: changing learning rate is not comparison of different testing methods. |

## Next unrun test (M15)

Preregister a **new**, genuinely prospective investigation before observing fresh cases. Use an explicit smooth-convergence rival, a coordinate-robust target where justified (for example Fisher–Rao prediction-space distance), multiple held-out initializations, learning-rate limit tests, benign/adversarial measurement controls, concrete numerical thresholds and error controls. Treat this intake and its seed as exploration, not independent confirmation.

**Governance:** Owner-directed review branch; no main-branch merge, official study, promotion of scientific claims, permission for reusing private work, or new license grant is implied. Publication rights and provenance should be reviewed before merging.
