# EGRR-DESC-001 — Fixed-Seed Descriptive Study

Status: DRAFT — DESIGN ONLY.
NOT FROZEN. NOT APPROVED FOR EXECUTION.

Originating investigator: sunny-kavixo.
Related: Issue #28, PR #37.
Original population P1: UNRESOLVED / NOT APPROVED.
Statistical-feasibility record: e930358.

## 1. Research scope

Describe the outcomes of exactly 100 predetermined synthetic
linear-layer cases without statistical population inference.

This is a finite-set descriptive exercise, not a test of
E[r] > 0.10 over the generating population.

No significance test, alpha claim, population confidence
interval, or population P1 success verdict is proposed.

## 2. Proposed case identities

Case IDs: 000 through 099.
Proposed seeds: 280000 through 280099, inclusive.

For each case use NumPy default_rng(case_seed), PCG64.

Proposed draw order, from the same generator:
1. W = rng.normal(size=(64, 32))
2. X_cal = rng.normal(size=(256, 64))
3. X_eval = rng.normal(size=(1024, 64))

Use float64 arrays, sequential draws, and no seed substitution.
Random correction arm uses default_rng(case_seed + 1000000).

All evaluation inputs remain inaccessible to selectors.

These seeds were previously proposed for the population
study; using them for this descriptive exercise would
make them ineligible as untouched future P1 confirmation
cases. Final seed choice requires maintainer review.

No cases have been generated for this draft.

## 3. Inspected environment and implementation identity

Python: 3.14.5
NumPy: 2.4.6
Default generator: PCG64
Platform: macOS-27.0.1-arm64-arm-64bit-Mach-O
Reference Git HEAD: e93035809897b10f6895168b51021f76e3fa79c3
METHOD.md Git blob:
6e4247ced1f2eef8b3c9917624d17d46d5bb80aa

Source SHA256:
egrr.py:
a1057838af2384f37029189e74ad59ce1a9d6f5d84b62ece9ae22b482992cd29
covariance_float16.py:
51389fda50ee09034806e6a4b12bb395de14de6ce8e29830ef12d64bbc8d5b6c
storage.py:
1a20b6ec271ec4bb7d47e3d0f65a284559efc83ab2f0a1457e09dbd349b4f6f1
primary_scoring.py:
10adfc9b3b13e58389e513ceab7a5f416dc062a5db9962b7b96c90a587fa3717

These are inspected reference identities, not frozen
execution identities. All hashes must be re-pinned
after any approved implementation changes.

## 4. Proposed parameters and storage

Weights: 64 x 32.
Calibration inputs: 256 x 64.
Evaluation inputs: 1024 x 64.
Quantization: symmetric per-tensor, 3 bits.
Corrected arms: K=128.
Serializer: EGR2 v1, 27-byte header, CRC32.
Store signed dense codes and float16 residual corrections.
Use actual serialized bytes, not modeled_bits(), for reporting.

## 5. Comparison arms

Primary descriptive pair:
- Float16-aware covariance greedy selection
- Largest original-residual magnitude selection

Additional arms:
- Input-RMS sensitivity
- Seeded random selection
- Uncorrected quantization
- Smallest-residual diagnostic, pending implementation

Currently magnitude and RMS rank original residual R.
Covariance gains use storable float16-rounded correction A.
This discrepancy requires an explicit review decision.
Ties are resolved by stable flattened index where specified.

Same-byte equality is required for corrected arms.
Runtime, temporary memory and covariance computation
cost are separate resources, not proved equivalent.

## 6. Descriptive outputs

For each of the 100 cases, retain:
- Seed, case ID, dimensions and implementation identity
- Actual serialized bytes per arm
- Successful decoding and integrity status
- Decoded reconstruction and calibration output MSE
- Decoded reconstruction and evaluation output MSE
- Paired r = 1 - MSE_cov / MSE_magnitude, if defined
- Zero and negative improvements
- Negative-gain selection count
- Diagnostic-arm outcomes
- Numerical and implementation failure categories

When all 100 paired ratios are valid:
report the exact finite-set arithmetic mean, minimum,
maximum, distribution and number of nonpositive cases.

If any ratio is undefined, the full 100-case arithmetic
mean is UNDEFINED. Preserve all case records and failures.

If an instrument or integrity gate fails, report
INSTRUMENT_FAILED; never omit or regenerate cases.

The MSE_magnitude <= 1e-12 tolerance is PROVISIONAL.
The maintainer must approve or replace it before freeze.

## 7. Numbered draft observational predictions

D1: Corrected arms should have equal EGR2 byte counts
under the specified dimensions, bit width and K.
Expected reference-container size: 1311 bytes.
A mismatch is an instrument failure, not hidden.

D2: Valid serialized payloads must decode to exactly
the recorded float16-rounded reconstructions.

D3: Benign structural gate must return GATE: PASS
and exit 0. Corrupted-CRC sabotage must return
GATE: FAIL and a nonzero exit.

D4: All generated cases must receive a visible
record or explicit failure category. No filtering.

D5: Descriptive covariance improvement may be
positive, zero or negative. No minimum gain is predicted.

These are proposed observations/instrument expectations,
not a registered population-improvement prediction.

## 8. Outstanding instrumentation

- Implement or explicitly exclude negative-gain diagnostics.
- Implement the smallest-residual diagnostic arm.
- Specify exact calibration-MSE arithmetic.
- Resolve R-versus-A ranking and tie behavior.
- Define structured per-case failure and verdict codes.
- Add benign and planted-sabotage cases for each
  applicable guard, including numerical failures.
- Pin source, exact commands, data formats, digests
  and resource definitions before any execution.

## 9. M16 triggered-control assessment — DRAFT

C-FEAS: No — no finite external eligibility pool.
C-NOISE: Review — deterministic arithmetic is intended;
  establish whether platform/BLAS behavior triggers it.
C-STAT: No population statistical decision is proposed;
  reassess if sample-derived inference is introduced.
C-EVID: No — evidence quality is not the outcome.
C-INDEP: No independent replication is claimed.
C-EXT: Yes — external prior art and reviews used.
C-DEVICE: Review — runtime is pinned for reproducibility;
  no device-performance claim is proposed.
C-BUILD: Yes — instrument returns fail-closed verdicts.
C-EXPLORE: Yes — prior exploratory work informed design.
C-METHCOMP: Yes — several selection methods compared;
  applicability of the referenced comparison protocol
  needs maintainer resolution.

All unresolved triggers must be resolved before freeze.
The canonical methodology is unchanged.

## 10. Provenance and prior research

Original investigator: sunny-kavixo.
AI assistance: OpenAI ChatGPT GPT-6, drafting/design.
Human review: investigator output checks and maintainer
direction-level review, not independent reproduction.

Preserve prior v0.4/v0.5 history, F-003 exploration,
unverified historical identities and negative findings.
Do not retrospectively describe exploratory outcomes
as held-out confirmation.

## 11. Freeze-and-run authorization gate

1. Submit this standalone DRAFT for review.
2. Resolve all open selector, failure and control rules.
3. Commit a separate freeze-ready registration.
4. Await explicit subsequent maintainer authorization.
5. Only then consider running the fixed study.

No descriptive 100-seed run or confirmatory P1 run
is authorized by the current review.

## 12. Next unrun checkpoint

Review the proposed descriptive case matrix and the
missing negative-gain/diagnostic instrumentation before
any research cases are generated.

Status remains DESIGN ONLY / NOT RUN.
