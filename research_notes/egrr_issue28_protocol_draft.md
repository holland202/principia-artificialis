# EGRR — Protocol Proposal v0.5 (Revision Under Review)

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

## Exact quantizer and EGR2 wire format (proposed v0.5)

This describes the locally inspected experimental Python scaffold,
not a frozen or independently verified reference implementation.
All corrected arms use the same quantizer and serializer.

### Symmetric quantizer

- Input: finite float64 matrix `W` of shape `(rows, cols)`.
- Supported bit widths: integers 2 through 8; proposed study uses `b=3`.
- `qmax = 2**(b-1)-1`; usable signed codes are `[-qmax, qmax]`.
  For three bits, the seven codes are `-3,-2,-1,0,1,2,3`;
  the eighth representable signed code `-4` is not generated.
- `scale = max(abs(W))/qmax` for any nonzero weight; otherwise 1.0.
- Codes: `clip(np.rint(W/scale), -qmax, qmax).astype(int16)`.
  NumPy `rint` rounds halfway cases to the nearest even integer.
- Reconstruction: `float64(codes) * float64(scale)`.
- Residual: `R = W - reconstruction`.
- Storable correction: `A = float64(float16(R))`;
  nonfinite float16 conversion is an invalid case.

### EGR2 version 1 container

- Dense codes are flattened in C row-major order and bit-packed
  least-significant-bit first, using signed two's-complement bit patterns.
- Dense payload length: `ceil(rows*cols*b/8)` bytes.
- Header: Python struct format `<4sBBBII d I` (27 bytes),
  little-endian and without alignment padding.
- Header fields, in order: `b'EGR2'` (4 bytes), version=1 (1),
  bits (1), index width (1), rows uint32 (4), cols uint32 (4),
  scale float64 (8), correction count uint32 (4).
- Indices refer to flattened row-major positions; index width is
  2 bytes when `rows*cols <= 65536`, otherwise 4 bytes when
  `rows*cols <= 2**32`, otherwise 8 bytes.
- Store `K` indices as little-endian unsigned integers in the
  selector's returned order, then `K` little-endian float16 corrections.
- Append a little-endian uint32 CRC32 of all preceding bytes.
  CRC32 detects accidental corruption; it is not authentication.
- Total length: `27 + ceil(rows*cols*b/8) + K*(index_width+2) + 4`
  bytes, subject to representable header fields.
- Decoder validates header/version/width, total length, unique in-range
  indices, positive finite scale, finite corrections and checksum.
- Reconstruction adds decoded float16 corrections (promoted to float64)
  at their stored flattened positions to decoded base weights.

### Selection and comparison conventions still requiring agreement

The existing magnitude and input-RMS selectors rank `abs(R)` and
`abs(R)*sqrt(mean(X_cal**2, axis=0))`, respectively; ties use stable
ascending flattened index. Random selection uses a seeded NumPy
generator without replacement; returned indices are sorted.
The covariance selector ranks gains using storable rounded `A`;
`np.argmax` resolves equal gains to the first flattened index.
All store float16 corrections; residual rank differences between
`R` and `A` must be explicitly approved before freezing.

A local structural check (not a held-out quality test) reported
1311 serialized bytes for each of magnitude, RMS, random and covariance
at shape 64x32, b=3, K=128; decoding matched the float16-rounded
reconstruction in that run. The structural regression test is now committed at
`experiments/egrr_issue28/test_matched_bytes.py`.
Its local passing result remains investigator-reported, not an
independent reproduction or a registered prediction.

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

## M3 anti-vacuity and sabotage controls (proposed v0.5)

The smallest-magnitude correction arm remains a diagnostic only.
It is not the guaranteed M3 killer.

The future verification harness MUST provide two independent
structural gate demonstrations before any confirmatory evaluation:

**Benign gate:**
- Serialize a valid fixed-seed quantized matrix with K corrections.
- Deserialize it and reconstruct using the decoded corrections.
- Check exact decoded-float16 reconstruction and actual byte count.
- Expected instrument result: `GATE: PASS`, process exit code 0.

**Planted corruption / sabotage gate:**
- Start from the same valid serialized EGR2 payload.
- Flip one bit in the dense-code payload without updating CRC32.
- Attempt to decode it through the normal public decoder.
- The decoder MUST raise a CRC32 mismatch.
- The verification harness MUST convert this detected corruption
  into `GATE: FAIL` and process exit code 1.
- If decoding succeeds, or the corruption check never executes,
  the gate MUST fail closed and report an implementation error.

The planned sabotage specifically challenges payload-integrity
verification. It does NOT prove that the statistical test can
reject a false quality-improvement claim. A separate seeded-null
or deliberately degraded-candidate statistical control is required
for C-STAT and must be specified before protocol freeze.

Record stdout, stderr, exit codes, source revision and environment.
Both controls must be executable and their output preserved.
No held-out evaluation inputs may be inspected during gate setup.

Status: proposed instrument design only; this v0.5 section
does not claim a committed or executed sabotage harness.

## Storage and scoring

All corrected arms use K=128 and equal EGR2 byte counts.
Each payload is serialized, decoded, and reconstructed
before output-MSE evaluation.

Report serialized bytes, float16 rounding differences,
calibration MSE, and evaluation MSE separately.

The uncorrected arm has fewer bytes and is reported
separately, not called a matched-size comparator.

## Precise scoring and numerical failure policy (proposed v0.5)

For each independent synthetic case:

- `W`: float64 matrix `[64, 32]`.
- `X_eval`: float64 held-out matrix `[1024, 64]`.
- `W_hat_m`: decoded and reconstructed float64 matrix `[64, 32]`
  for method `m`.
- Compute the matrix difference `D_m = W - W_hat_m` in float64.
- Define `MSE_m = mean((X_eval @ D_m)**2)` using NumPy float64
  matrix multiplication, multiplication and reduction.
- Evaluate all methods on the identical held-out input matrix
  within each case. Selection must not access `X_eval`.

The primary per-case quantity is:

`r_t = 1 - MSE_covariance_t / MSE_magnitude_t`

The primary summary is the arithmetic mean of the 100 paired
case-level relative improvements. It is NOT:

`1 - sum(MSE_covariance) / sum(MSE_magnitude)`.

Proposed numerical-failure policy, requiring maintainer agreement:

1. Require finite float64 weights, calibration inputs, evaluation
   inputs, decoded weights and MSE values.
2. Reject negative or nonfinite MSE; report the case and fail the
   primary instrument rather than deleting or replacing the case.
3. If `MSE_magnitude <= 1e-12`, mark the ratio UNDEFINED and fail
   the primary instrument. This threshold is provisional and must
   be justified or replaced before protocol freeze.
4. If division, `r_t`, or the across-case summary is nonfinite,
   fail the primary instrument without omitting any cases.
5. If a payload cannot serialize, decode or round-trip correctly,
   report IMPLEMENTATION_ERROR; do not silently regenerate a case,
   alter the seed, or substitute an alternative method.
6. No failed or undefined case is excluded from the denominator.
   Publish every generated case ID and its failure category.

A numerical/instrument failure is distinct from a genuine
negative scientific outcome. A finite zero or negative relative
improvement is retained and scored normally.

Every tolerance, numeric failure category and verdict transition
must be agreed and frozen before held-out evaluation.

## Statistical decision status and unresolved alternatives

**NO CONFIRMATORY STATISTICAL DECISION RULE IS FROZEN.**

The original research question concerns mean paired relative improvement.
The percentile-bootstrap rule below is an earlier proposal, not a
validated finite-sample hypothesis test. It MUST NOT be applied as an
approved confirmatory success criterion.

The C-STAT binomial alternative elsewhere in this draft instead tests
the probability that an independent case attains at least 10% gain.
This is a DIFFERENT estimand and does not establish a 10% mean gain.

Before registration, the investigator and maintainer must select the
primary estimand, null/alternative, alpha, fixed-horizon test, failure
handling and exact verdict rule. If the estimand changes, record that
change explicitly against Issue #28's original P1.

Neither alternative may be chosen after inspecting held-out outcomes.
Until agreement, the primary prediction and verdict are NOT RUN.

## Primary analysis proposal

For case t, define:

improvement_t = 1 - MSE_covariance_t/MSE_magnitude_t

Primary summary: arithmetic mean improvement across
100 independently generated cases.

Uncertainty: paired case-level percentile bootstrap,
10000 resamples, 95% two-sided interval, using
the fixed bootstrap seed.

Historical v0.4 proposed success rule (NOT APPROVED):
mean improvement >= 0.10 AND bootstrap 95% interval
lower bound > 0.10.

This is retained for proposal history only, NOT as an
authorized confirmatory verdict rule. C-STAT review is pending.

This decision rule is NOT yet agreed or registered.

## C-STAT fixed-horizon alternative (proposed v0.5)

The existing percentile-bootstrap confidence interval is descriptive
only until its finite-sample error-control properties are justified.
Do not use its lower bound as a confirmatory p-value.

A possible alternative primary claim is about the probability that
an independent synthetic case achieves at least 10% relative gain,
rather than the arithmetic mean of relative gains.

Define `success_t = 1` if a finite, valid case satisfies
`r_t >= 0.10`; otherwise `success_t = 0` for a finite valid case.
Numerical or instrument failures are reported separately and
block a confirmatory success verdict; they cannot be silently
treated as ordinary failures or removed.

Proposed fixed-horizon statistical hypotheses:

- H0: P(r_t >= 0.10) <= 0.50.
- H1: P(r_t >= 0.10) > 0.50.
- Sample: exactly 100 independent generated synthetic cases.
- One-sided alpha: 0.05.
- Test: exact binomial upper-tail test of observed success count
  against p0=0.50.
- Report the integer success count, all 100 per-case outcomes,
  and the exact one-sided p-value.
- No interim data inspection, optional stopping or retuning.
- A passing result requires p <= 0.05 and all structural,
  numerical and sabotage gates passing.
- Under independence and the stated null, the upper-tail
  binomial procedure controls type-I error at or below 0.05.

This test does not prove mean improvement >=10%, and it does not
establish a gain on real models. The original mean-based P1
remains unresolved; the maintainer must explicitly choose or
approve a different valid test before preregistration.

A seeded null/sabotage control must demonstrate that the
statistical gate can return a non-success verdict and nonzero
process exit; a benign passing control must also be exercised.

Status: statistical design proposal, not registered or run.

## Stopping and reporting

Run exactly 100 cases after approval and protocol freeze.
No interim inspection, adaptive stopping, or changing
methods after observing evaluation results.

Report raw per-case outputs, all controls, failures,
environment, source hashes, and exact execution commands.

## M16 triggered-control assessment (v0.5 draft)

The canonical control definitions remain in METHOD.md and
CONTROLS.md. This table does not redefine those requirements.

| Trigger | Control | Assessment and reason |
|---|---|---|
| Feasibility | C-FEAS | No — synthetic cases are generated rather than filtered from a finite real-data pool; reconsider if eligibility screening is added. |
| Noise | C-NOISE | No — intended measurements are seeded CPU computations; reassess if repeated identical inputs differ or timing claims are added. |
| Statistics | C-STAT | Yes — primary prediction estimates an improvement from sampled cases; valid fixed-horizon inference required. |
| Evidence | C-EVID | No — the primary claim tests numerical approximation error rather than evidence handling; revisit if provenance becomes the measured outcome. |
| Independence | C-INDEP | No — no independent replication is claimed; locally repeated tests remain self-tested. |
| External | C-EXT | Yes — GPTQ, AWQ, SpQR, maintainer feedback and outside ideas inform the proposal; source identity and provenance required. |
| Device | C-DEVICE | No — no device-performance claim in the synthetic primary study; Apple Silicon extension needs a separate assessment. |
| Verdict code | C-BUILD | Yes — scoring and sabotage harnesses will produce PASS/FAIL verdicts and must fail closed. |
| Exploration | C-EXPLORE | Yes — calibration-only exploratory work preceded this design and must be disclosed in the append-only fork ledger. |
| Method comparison | C-METHCOMP | Review needed — covariance and magnitude algorithms are compared, but the cited C-METHCOMP procedure is specific to a separate methodology-comparison study. Do not claim exemption without maintainer agreement. |

This assessment must be reviewed before preregistration.
Blank or unresolved triggers cannot silently be treated as exempt.

### Remaining registration obligations

- Name and pin the adopted METHOD.md revision.
- Prepare numbered P1/P2 predictions and corresponding controls.
- Complete the historical exploratory-fork ledger with code/data
  identity, environment, observations and `EXPLORATORY` status.
- Pin NumPy/Python implementation and random generator/draw order.
- Include a fresh, unrun prediction before any held-out evaluations.
- Record M13 AI assistance, human review level and responsibility.
- Preserve revisions and deviations without rewriting history.

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

- Historical v0.4 bootstrap threshold remains an unapproved
  proposal; it is NOT the registered primary success criterion.
- Primary estimand and statistically justified fixed-horizon
  decision rule require explicit maintainer agreement.
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
