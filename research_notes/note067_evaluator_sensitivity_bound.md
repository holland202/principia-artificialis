# Note #067 — A signed safety bound says nothing about the true rate unless the evaluator is shown to detect

**Status:** Speculative — registration only. Nothing below has been run. Registered 2026-10-05 before
`scripts/note067_reference.py` exists.
**Theme:** Statistics / Evaluation / Evidence
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's direction (2026-10-05); direction only,
no line review before this commit.
**Builds on:** [[note064_governed_outcome_feedback]] (an evaluator that shares the learner's blind spot);
the anti-vacuity rule (METHOD.md M3: the instrument can say the other thing); outside material: OVERT 1.1,
Glacis Technologies (CC BY 4.0), §19 and Annex B.7–B.8.
**Method:** [METHOD.md](../METHOD.md) at commit `3f837b3`.

## The claim

OVERT 1.1's Statistical Safety Signal Protocol (S3P) publishes an exact one-sided upper confidence bound on
the **evaluator-judged** violation rate over a provably fair sample. The standard says so itself (§19: "S3P
attests the *evaluator-judged* violation rate … S3P proves the sample was honest; verdict reproducibility
proves the judgments were"). Its 16-field attestation (Annex B.7) has no field for the evaluator's ability to
detect a violation, and its stated coverage property (Annex B.8: "P(p_true in [CI_lower, CI_upper]) >= 1 −
alpha for all p_true") holds only if `p_true` means the judged rate.

Claim, precisely: (1) with an evaluator of sensitivity s < 1, the S3P bound fails to cover the **true**
violation rate far more often than α, and with s = 0 it fails always while looking maximally safe; (2) seeding
k known violations ("canaries") per epoch, indistinguishable from real traffic, and dividing a Bonferroni-split
S3P bound by the canaries' one-sided Clopper-Pearson lower bound on sensitivity restores coverage of the true
rate at ≥ 1 − α in every arm, at a stated cost in tightness; (3) if the evaluator can recognise canaries, the
repair fails. Each part can be precisely wrong.

## Epistemic status (read first)

The repair is not new. Seeding known faults to estimate what a detector misses is Mills' error seeding
(1972), and correcting an apparent rate by a test's sensitivity is the Rogan–Gladen estimator (1978). What this
note adds is narrow: it applies that correction to S3P's exact-bound construction and measures the cost. Part
(1) is a direct consequence of S3P's definition. The value of running it is to put numbers on it, and to test
the assumption part (3) names. The reading of OVERT behind "no such field or requirement" is one search of the
full text (Markdown and PDF text, sha256 of the Markdown `f25c106b…6edda`) for sensitivity, recall, false
negatives, canaries, seeded or known positives, positive controls and detection probability. It found none
relevant. That reading is Claude's alone and has not been checked by anyone else.

## Model (registered)

- Per epoch: n = 600 sampled requests. Each is a true violation with probability p. The evaluator flags a true
  violation with probability s and never flags a non-violation (false-positive rate 0; a door below). So the
  judged count is Binomial(n, s·p).
- S3P alone: U = one-sided Clopper-Pearson upper bound at α = 0.05 on the judged count. It "covers" when U ≥ p.
- Canaries: k = 20 per epoch, each flagged with probability s (indistinguishable arm). Caught count c ~
  Binomial(k, s). L = one-sided Clopper-Pearson lower bound on s at α/2 = 0.025. U' = the S3P upper bound at
  α/2 = 0.025 (Bonferroni, joint 1 − α). Composed bound B = U'/L. If L = 0, B = ∞: no claim is made, which
  counts as covering and is reported separately.
- Why B is valid: the judged rate q = s·p, so p = q/s ≤ U'/L whenever U' ≥ q and L ≤ s. Each fails with
  probability ≤ 0.025.
- Arms: s ∈ {1, 0.9, 0.5, 0.1, 0} × p ∈ {0.005, 0.04}: 10 arms, 2,000 epochs each, NumPy seed 0. Plus one
  **distinguishable-canary** arm (s = 0.1 on real violations, canaries flagged with probability 1; p = 0.04).
- Miss rate = the fraction of epochs whose bound does not cover p. Decisions use the exact one-sided
  Clopper-Pearson bound at 99% on each miss rate over 2,000 epochs (fixed horizon, no early looks; C-STAT).

## Registered predictions

- **P1 (an always-pass evaluator looks safest).** s = 0, both p: the S3P bound is 0.004980 in every epoch
  (1 − 0.05^(1/600)), and its miss rate is 1.000.
- **P2 (S3P is honest when the evaluator is perfect).** s = 1, both p: the S3P-alone miss rate is ≤ 0.05, and
  its 99% upper bound is ≤ 0.065.
- **P3 (partial sensitivity breaks S3P coverage).** s = 0.5, p = 0.04: the S3P-alone miss rate has a 99% lower
  bound ≥ 0.50.
- **P4 (the composed bound covers the true rate).** In all 10 indistinguishable arms, the composed-bound miss
  rate is ≤ 0.05 with a 99% upper bound ≤ 0.065. In the s = 0 arms every epoch makes no claim (B = ∞), and that
  fraction is reported.
- **P5 (cost, derived).** At p = 0 with s = 1 (every canary caught, no violations), B / U = 1.4799 ± 0.0005: the
  repair loosens a perfect evaluator's bound by about 48% at k = 20.
- **P6 (indistinguishability is load-bearing).** In the distinguishable-canary arm, the composed-bound miss
  rate has a 99% lower bound ≥ 0.50.
- **P7 (sabotage, `--sabotage`).** The composed bound is replaced by the S3P bound alone. P4 must be REFUTED;
  exit 1.

## Anti-vacuity

P1 and P3 are the instrument showing it can report a miss, and P6 shows the repair itself can fail. P7 shows
the harness can tell the repair from its absence.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility (C-FEAS) | no: synthetic, no real data or records. |
| Noise (C-NOISE) | no: deterministic given the seed. Monte Carlo error is handled by the exact bounds in the decisions. |
| Statistics (C-STAT) | **yes**: miss rates are estimated from 2,000 epochs per arm. The rule is a fixed-horizon exact one-sided Clopper-Pearson bound at 99%, with no early looks. |
| Evidence (C-EVID) | yes: the question is whether a signed safety statistic carries the evidence it implies. Answered by the model; no real attestation is tested. |
| Independence (C-INDEP) | no claim of independence. One author (Claude). |
| External (C-EXT) | **yes**: OVERT 1.1 is quoted. CC BY 4.0, attribution Glacis Technologies, Inc.; quotations unchanged; the reading of it is Claude's own and unreviewed. No contact with Glacis, CHAI or AIGovOps. |
| Device (C-DEVICE) | no device claim. Container only; NOT VALIDATED on the S25. |
| Verdict code (C-BUILD) | yes: the harness prints HELD/REFUTED, a VERDICT and a DIGEST, and has `--sabotage`. |
| Exploration (C-EXPLORE) | **yes, disclosed**: before this registration, three closed-form values were computed in conversation: the sensitivity lower bounds 0.7411, 0.8609 and 0.9418 for 10, 20 and 50 canaries all caught at one-sided 95%. So was P5's ratio (arithmetic of the registered formula). No simulation was run. |
| Method comparison (C-METHCOMP) | yes, comparing S3P alone against the composed bound in the same arms, seeds and epochs. |

## What this does not test

- False positives (f > 0): the evaluator also flags non-violations. The composed bound stays valid
  (conservative); its tightness changes.
- Canaries that differ from real violations in difficulty. Sensitivity measured on canaries is then not
  sensitivity on real traffic. The model assumes they are exchangeable; real deployments cannot.
- Any real OVERT implementation or Protocol Profile. Profile 1.0 might specify something the standard text
  does not.

## Falsifiable next predictions (M15)

- **D1 (unrun).** With f = 0.01 and s = 0.9, the composed bound still covers at ≥ 1 − α, but the S3P-alone bound
  over-covers. Neither has been run.
- **D2 (unrun).** Canaries drawn from an easier distribution than real violations (canary sensitivity 0.95,
  real 0.6) break P4's coverage at p = 0.04. This is the realistic version of P6.
