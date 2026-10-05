# Note #067 — A signed safety bound says nothing about the true rate unless the evaluator is shown to detect

**Status:** Draft, verified reference code — 5 of 6 registered predictions held; **P2 REFUTED (kept)**, on a
threshold I set too tight. Registration committed at `21d5a98`, before the code existed; code and raw output
`6c76ca9`; `RECORDED` pinned `b641793`. Container only; NOT VALIDATED on the S25.
**Theme:** Statistics / Evaluation / Evidence
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's direction (2026-10-05); direction only,
no line review before this commit.
**Builds on:** [[note064_governed_outcome_feedback]] (an evaluator that shares the learner's blind spot);
the anti-vacuity rule (METHOD.md M3: the instrument can say the other thing); outside material: OVERT 1.1,
Glacis Technologies (CC BY 4.0), §19 and Annex B.7–B.8.
**Method:** [METHOD.md](../METHOD.md) at commit `3f837b3`.

## What broke (read first)

**P2 — REFUTED (kept).** I registered that with a perfect evaluator (s = 1) the S3P-alone miss rate would be
≤ 0.05, with a 99% upper bound ≤ 0.065. At p = 0.005 the observed miss rate was **0.0545** (99% interval
0.0433–0.0675). So both clauses failed. (At p = 0.04 it held: 0.0330.)

S3P is not at fault. The exact miss probability at p = 0.005 is **0.049414**, inside α. A diagnostic line
computing it was added after the first run; no registered computation changed and the digest is identical. With
n = 600, S3P misses there exactly when the judged count is 0, and its bound at 0 (0.004980) sits just below
p = 0.005. That makes the true miss rate a knife edge at α. With 2,000 epochs, the standard error of the estimate is about
0.005 (√(0.0494 × 0.9506 / 2000) = 0.00485), so a point-estimate rule of "≤ 0.05" can fail on Monte Carlo
noise alone. The registration error: I tested an
exact-coverage method with a rule that leaves no room for its own sampling error, at a parameter where coverage
is tight. The lesson for the OVERT comment is that S3P's arithmetic is exact as claimed. The issue is only
what it is a bound *on*.

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

## Results (run 2026-10-05, `results/note067/run.txt`)

```
note067 | registered run | python 3.13.16 | n=600 k=20 alpha=0.05 epochs=2000 seed=0
  s=1.0  p=0.005  S3P miss 0.0545 [99% 0.0433, 0.0675]  composed miss 0.0000 [99% 0.0000, 0.0023]  no-claim 0/2000  S3P bound 0.004980..0.028106  composed median 0.017488
  s=1.0  p=0.04   S3P miss 0.0330 [99% 0.0244, 0.0435]  composed miss 0.0035 [99% 0.0012, 0.0080]  no-claim 0/2000  S3P bound 0.026029..0.093289  composed median 0.070871
  s=0.9  p=0.005  S3P miss 0.0705 [99% 0.0578, 0.0849]  composed miss 0.0000 [99% 0.0000, 0.0023]  no-claim 0/2000  S3P bound 0.004980..0.028106  composed median 0.019357
  s=0.9  p=0.04   S3P miss 0.0895 [99% 0.0752, 0.1054]  composed miss 0.0015 [99% 0.0002, 0.0050]  no-claim 0/2000  S3P bound 0.023929..0.080330  composed median 0.078446
  s=0.5  p=0.005  S3P miss 0.2205 [99% 0.1993, 0.2429]  composed miss 0.0000 [99% 0.0000, 0.0023]  no-claim 0/2000  S3P bound 0.004980..0.019641  composed median 0.038026
  s=0.5  p=0.04   S3P miss 0.8525 [99% 0.8331, 0.8705]  composed miss 0.0010 [99% 0.0001, 0.0042]  no-claim 0/2000  S3P bound 0.007882..0.063425  composed median 0.127502
  s=0.1  p=0.005  S3P miss 0.7420 [99% 0.7185, 0.7645]  composed miss 0.0000 [99% 0.0000, 0.0023]  no-claim 243/2000  S3P bound 0.004980..0.012872  composed median 0.496356
  s=0.1  p=0.04   S3P miss 1.0000 [99% 0.9977, 1.0000]  composed miss 0.0010 [99% 0.0001, 0.0042]  no-claim 263/2000  S3P bound 0.004980..0.030164  composed median 0.970872
  s=0.0  p=0.005  S3P miss 1.0000 [99% 0.9977, 1.0000]  composed miss 0.0000 [99% 0.0000, 0.0023]  no-claim 2000/2000  S3P bound 0.004980..0.004980  composed median none
  s=0.0  p=0.04   S3P miss 1.0000 [99% 0.9977, 1.0000]  composed miss 0.0000 [99% 0.0000, 0.0023]  no-claim 2000/2000  S3P bound 0.004980..0.004980  composed median none
  distinguishable canaries (real s=0.1, canaries caught always), p=0.04: composed miss 1.0000 [99% 0.9977, 1.0000]  composed median 0.014417
  P5 p=0, s=1: S3P bound 0.004980, composed 0.007371, ratio 1.4799
  (unregistered diagnostic) s=1, p=0.005: S3P misses iff judged <= 0; exact miss probability 0.049414
  (unregistered diagnostic) s=1, p=0.04: S3P misses iff judged <= 15; exact miss probability 0.031792
  P1  HELD
  P2  REFUTED
  P3  HELD
  P4  HELD
  P5  HELD
  P6  HELD
VERDICT 5 of 6 as registered (P7 is --sabotage)
DIGEST 44e15cac2d627520307e0901e38f75c5b5669f598ff822a0daf523ae09a0725d
```

Sabotage (`results/note067/sabotage.txt`, composed bound replaced by S3P alone): P4 REFUTED, `VERDICT 4 of 6`,
exit 1.

| Prediction | Result |
|---|---|
| P1 always-pass evaluator: S3P bound 0.004980 every epoch, miss rate 1.000 | HELD |
| P2 perfect evaluator: S3P miss ≤ 0.05 (99% upper ≤ 0.065) | **REFUTED (kept)**: 0.0545 at p = 0.005; exact value 0.049414 (see above) |
| P3 s = 0.5, p = 0.04: S3P miss, 99% lower bound ≥ 0.50 | HELD: 0.8525 (99% lower 0.8331) |
| P4 composed bound covers in all 10 arms | HELD: worst miss 0.0035 (99% upper 0.0080) |
| P5 cost ratio 1.4799 ± 0.0005 | HELD: 1.4799 |
| P6 distinguishable canaries break the repair | HELD: miss 1.0000 |
| P7 sabotage exits 1 | HELD |

### What this shows

- **Mathematical, not new:** the S3P bound is exact for the judged rate (the diagnostic: 0.049414, 0.031792 ≤
  0.05), and says nothing about the true rate once the evaluator can miss. At s = 0.5 and p = 0.04 it failed to
  cover the true rate in 0.8525 of epochs. At s = 0.1, p = 0.04 it failed in 1.0000, while reporting bounds as tight
  as 0.004980.
- **The repair covers, and it is conservative:** composed misses were at most 0.0035 across all arms. The price
  is width: the median composed bound at s = 1, p = 0.04 was 0.070871, against a true 0.04. With an evaluator
  that catches little, the repair mostly declines to claim anything: at s = 0.1, 243 and 263 of 2,000 epochs
  made no claim, and the rest had medians of 0.496356 and 0.970872, which is close to no claim. That is the honest
  answer for a nearly blind evaluator.
- **The repair rests entirely on canaries being indistinguishable** (P6: miss rate 1.0000 when the evaluator
  recognises them). In a real deployment this is the hard part, and this note does not solve it.

### What it does not show

Anything about real OVERT implementations, Protocol Profile 1.0, or real evaluators. The model has no false
positives and assumes exchangeable canaries. One author, self-tested.

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
