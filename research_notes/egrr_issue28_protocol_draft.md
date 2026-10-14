# EGRR — Clean Protocol Proposal v0.4

Issue: https://github.com/holland202/principia-artificialis/issues/28

STATUS: DRAFT FOR MAINTAINER REVIEW.
NOT APPROVED, FROZEN, OR CONFIRMATORY.

## Research question

Does float16-aware covariance-greedy residual selection
reduce independent held-out output MSE relative to
largest-magnitude selection at equal EGR2 serialized bytes?

## Candidate rule

R = W - Q_b(W)
A = float64(float16(R))
C = X_cal.T @ X_cal / n_cal
E = R initially

For each unselected correction (i,j):

gain(i,j) = 2*A[i,j]*(C@E[:,j])[i] - C[i,i]*A[i,j]**2

Select maximum gain globally, with flattened-index
tie-breaking. Update E[i,j] -= A[i,j].
Repeat exactly K times, recording negative gains.
Only calibration inputs may affect selection.

## Proposed synthetic design

- Independent cases: 100
- Weight shape: 64 x 32
- Calibration input shape: 256 x 64
- Evaluation input shape: 1024 x 64
- Weight/input distribution: independent standard normal
- Base quantizer: existing symmetric per-tensor 3-bit
- Correction count: K=128
- Case seeds: 280000 through 280099 inclusive
- Within each case: one seeded generator, sequential draws
  for weights, calibration and evaluation inputs
- Random-control seed: case seed + 1000000
- Bootstrap seed: 282828
- Bootstrap replicates: 10000
- Covariance regularization: none
- No hyperparameter tuning on evaluation data

All specifications remain proposals until approved.

## Arms and controls

Primary: float16-aware covariance-greedy versus magnitude.

Secondary: RMS sensitivity, random, and uncorrected
quantization. Adversarial diagnostic: smallest absolute
residual selection, exactly K corrections.

The adversarial control is a diagnostic, not a guaranteed
failure case. Its behavior must be reported objectively.

## Storage and scoring

All corrected arms use K=128 and equal EGR2 byte counts.
Each payload is serialized, decoded, and reconstructed
before output-MSE evaluation.

Report serialized bytes, float16 rounding differences,
calibration MSE, and evaluation MSE separately.

The uncorrected arm has fewer bytes and is reported
separately, not called a matched-size comparator.

## Primary analysis proposal

For case t, define:

improvement_t = 1 - MSE_covariance_t/MSE_magnitude_t

Primary summary: arithmetic mean improvement across
100 independently generated cases.

Uncertainty: paired case-level percentile bootstrap,
10000 resamples, 95% two-sided interval, using
the fixed bootstrap seed.

Proposed success: mean improvement >= 0.10 AND
bootstrap 95% interval lower bound > 0.10.

Otherwise no primary success claim.

This decision rule is NOT yet agreed or registered.

## Stopping and reporting

Run exactly 100 cases after approval and protocol freeze.
No interim inspection, adaptive stopping, or changing
methods after observing evaluation results.

Report raw per-case outputs, all controls, failures,
environment, source hashes, and exact execution commands.

## Scope and limitations

This is synthetic linear-layer research only.
It does not establish real-LLM quality, inference
latency, practical memory advantage, or novelty.

Calibration selection runtime, covariance memory,
decoder allocations, and inference latency need
separately approved measurement procedures.

Prior-art review and independent replication are pending.
Earlier calibration-only exploratory results were
inspected before designing this proposal and must
not count as confirmatory evidence.

AI-assisted research planning and code drafting:
OpenAI ChatGPT GPT-6.

NO CONFIRMATORY RUN BEFORE MAINTAINER APPROVAL.


## Technical review clarifications

These are proposals for maintainer review, not frozen rules.

- Primary success criterion: the preregistered paired-bootstrap
  95% confidence interval lower bound for mean per-case relative
  improvement must exceed 0.10.
- Bootstrap resampling unit: independent synthetic matrix case.
- Report every case, including zero or negative improvements.
- Record the number of negative-gain selections made by the
  fixed-K covariance selector.
- Separately record calibration MSE, decoded evaluation MSE,
  actual EGR2 bytes, and selection runtime.
- Do not tune K, seeds, distributions, or decision thresholds
  after examining confirmatory evaluation outcomes.
- Treat smallest-magnitude corrections as a diagnostic control,
  not as guaranteed evidence of evaluation validity.
- Define numerical-failure handling and the real-model
  extension before protocol freeze.


## Prior-art review and numerical safeguards

This proposal makes no claim that sparse corrections,
activation-aware quantization, or covariance-based
optimization are fundamentally new.

Relevant prior work:

1. GPTQ (Frantar et al., 2022):
   https://arxiv.org/abs/2210.17323
   Approximate second-order post-training quantization.

2. AWQ (Lin et al., 2023):
   https://arxiv.org/abs/2306.00978
   Activation-aware identification and protection
   of important model weights/channels.

3. SpQR (Dettmers et al., ICLR 2024):
   https://arxiv.org/abs/2306.03078
   Sparse higher-precision outlier storage alongside
   low-bit quantized weights.

The candidate must be assessed against these existing
ideas before claiming any methodological novelty.

Numerical safeguards proposed for protocol review:

- Reject non-finite weights or calibration inputs.
- Reject float16 correction overflow.
- Validate serialized payload integrity before scoring.
- Record non-finite evaluation outputs as failures;
  do not silently discard unfavorable cases.
- Preserve raw outputs and execution errors.
- Report calibration selection cost separately from
  reconstruction and inference cost.
- Do not treat CRC32 as cryptographic authentication.
- Establish exact failure-handling and numerical
  tolerances with the maintainer before protocol freeze.

Research status: protocol development only.
No confirmatory experiment authorized.
