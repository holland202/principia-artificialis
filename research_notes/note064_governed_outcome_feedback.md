# Note #064 — Which separations in an outcome-feedback loop prevent which false improvements?

**Status:** Draft, verified reference code — 9 of 10 registered predictions held; **P5 REFUTED (kept)**. Registration committed at `99e666d`, before the code existed.
**Theme:** Learning Theory / Governance / Evaluation
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's request
**Builds on:** [[note063_evidence_bound_learning_loop]] (EBLL records and store), METHOD_SWAY.md + Amendment 1
**Origin of the question:** Amanda Saunders asked whether reviewed audit records plus actual outcomes could
become a learning or evaluation loop. That is an external research prompt, not evidence that any architecture
here works. Note063 built the bookkeeping; this note tests whether the loop *improves decisions on new cases*,
and which of its separations matter.

## What broke (read first)

**P5 — REFUTED (kept).** Two separate failures inside one registered prediction:

1. *My prediction about the naive learner was too strong.* Under leakage (NC6), B1 still improved:
   mean gain **0.0775**, against **0.1387** without leakage, and a median deployed τ of **0.60** instead of
   **0.45**. Leakage cost it most of its improvement but did not make it harmful. "Gain ≤ 0" was wrong.
2. *My "by construction" claim was wrong for B3, because of my instrument.* B2 (decision-time records only)
   is identical with and without leakage in 100 of 100 seeds, which is the mechanism the prediction was
   about. B3 differs on one seed (seed 87: 0.35 vs 0.70), although its inputs are byte-identical, because
   its bootstrap's random seed includes the condition label. So B3 has a condition-dependent random
   component, and "identical by construction" never held for it. The instrument was not re-seeded after the
   run to make P5 pass.

**Registered to fail, and they did:** with a corrupted outcome source shared by learner and evaluator (NC2),
every learning arm deployed a harmful change (harmful **1.00**, mean gain **-0.0464**). Under drift, the
governed arm deployed a harmful change in **0.98** of seeds (mean gain **-0.1785**). No separation in this
design detects either.

**A cost the registration did not foresee:** under missing failures (NC3), the completeness contract stopped
B3 from learning at all (deploy **0.00**, gain **0.0000**). B2, which learned from the biased data anyway, still
gained **0.1205** and was never harmful. In this world the contract protected against a harm that only the
naive arm suffered, and it cost the whole improvement.

**Arithmetic note:** the registration says "available gain +0.1425". That was 0.4347 − 0.2922 computed from
rounded values; the unrounded value the code prints and uses is **0.1426**.

## The claim

Feed post-action outcomes back to adjust one decision parameter. Four ways of doing it:

| Arm | What it is |
|---|---|
| **B0** | no feedback: the deployed threshold never changes |
| **B1** | naive: learn from every outcome as it currently stands in the system, treat a missing outcome as success, deploy what is learned |
| **B1s** | self-graded: like B1, but the learner also chooses the metric it optimizes and grades itself with it |
| **B2** | evaluated: learn only from decision-time records (EBLL `DecisionRecord`), missing outcomes are unknown (`success=None`), evaluate the proposal on a held-out randomized slice with a fixed utility metric, deploy if the point estimate improves |
| **B3** | governed: B2 plus (i) an outcome-completeness contract — no learning from a batch where < 95% of acted cases have an outcome — and (ii) deploy only if the 95% bootstrap lower bound of the held-out gain is > 0 |

**Claim, stated so it can be wrong:** each separation prevents a *specific*, measurable false improvement,
and none of them prevents a false improvement whose cause is shared by the learner and the evaluator.
B2 is the simplest serious rival: ordinary held-out evaluation, standard practice. B3 has to beat it
somewhere specific to earn its extra machinery.

## Epistemic status (read first)

Synthetic world, one learned parameter, deterministic seeds. Nothing here is about a real agent, model or
data stream. The unit of learning is a single action threshold τ, nothing else. Results say which mechanism
blocks which failure *in this world*; they do not say any real feedback loop is safe.

## Known mathematics / prior art

None of the mechanisms is new: held-out evaluation, randomized exploration for off-policy evaluation, the
**selective labels** problem (outcomes exist only for actions that were taken; Lakkaraju et al., KDD 2017),
missing-not-at-random data, label leakage / target leakage, Goodhart's law and reward hacking, confidence-gated
deployment as in A/B testing, concept drift. Novelty status: **OVERLAPS EXISTING WORK**. The question is
which of these this estate's EBLL design actually needs, measured, not whether they exist.

## The experiment

**World.** Each case has a decision-time score s ~ U(0,1). True success probability p(s) = 1/(1+e^(−12(s−c))),
c = 0.45. Acting yields +1 on success, −1 on failure; deferring yields 0. The best threshold is τ* = c.
The deployed threshold starts at τ0 = 0.70. Expected new-case utility (exact integral, not sampled):
U(0.70) = 0.2922, U(0.45) = 0.4347. Available gain: +0.1425 per case.

**Feedback period.** 2,000 cases. With probability 0.2 a case is a randomized exploration case (acted
regardless of s); otherwise act iff s > τ0. Outcomes exist only for acted cases (selective labels).
Exploration cases are split before any learning: half development (learner may use), half held-out
(evaluator only). Records go into EBLL's `AppendOnlyStore` as `DecisionRecord` + `OutcomeRecord`.

**Learner (same for every arm except B1s).** τ̂ = argmax over τ ∈ {0.00, 0.05, …, 0.95} of
Σ (2y − 1) over admitted acted cases with s > τ. **B1s** instead maximizes success rate among acted cases.

**Conditions.** TRUE (faithful, complete) · NC1 RANDOM (recorded outcome is a coin flip, independent of the
truth) · NC2 CORRUPTED SOURCE (the outcome source reports failures in s ∈ [0.15, 0.45) as successes — learner
and evaluator both see it) · NC3 MISSING FAILURES (60% of failure outcomes never recorded) · NC6 LEAKAGE (after
an outcome, the system's *current* score for a success is raised by 0.3; decision-time records are unchanged)
· DRIFT (feedback period has c = 0.45, the deployment world has c = 0.75). 100 seeds per condition.

**Measured per arm × condition:** deploy rate; harmful-deploy rate (deployed τ has lower new-case utility
than τ0 in the deployment world); mean new-case utility gain (0 when nothing is deployed).

### Registered predictions

- **P1 (real improvement, TRUE).** B1, B2 and B3 all have mean gain > 0; B3 deploys in ≥ 80 of 100 seeds.
- **P2 (simplest rival, TRUE).** |gain(B1) − gain(B2)| ≤ 0.1 × 0.1425: in clean conditions the evaluation
  layer adds nothing measurable over naive feedback.
- **P3 (NC1 random feedback).** Harmful-deploy rate: B3 ≤ 0.05, B1 ≥ 0.20, and B1 ≥ B2 ≥ B3.
- **P4 (NC3 missing failures).** B1 harmful-deploy rate ≥ 0.90 (missing becomes success → τ̂ → 0). B3
  deploys 0 times (completeness contract). B2 still gains, but less than its own TRUE gain (biased low τ̂).
- **P5 (NC6 leakage).** B1 mean gain ≤ 0. B2 and B3 results are identical to their TRUE results (they read
  decision-time records only — by construction; the run checks the construction).
- **P6 (NC2 corrupted source — registered to FAIL for governance).** B3 harmful-deploy rate ≥ 0.50. No
  separation helps when learner and evaluator share a corrupted outcome source.
- **P7 (DRIFT — registered to FAIL for governance).** B3 harmful-deploy rate ≥ 0.50. A held-out slice from
  the old world approves a change that is harmful in the new one.
- **P8 (price of governance, TRUE).** B3 mean gain ≤ B2 mean gain: the confidence gate forgoes some real
  improvement. The size of that price is the number to read.
- **P9 (self-grading, TRUE).** B1s harmful-deploy rate ≥ 0.90: a learner that picks its own metric drives
  τ up (fewer, safer actions) and loses utility. Related to [[note063_evidence_bound_learning_loop]]'s open
  P7; it does not close it.
- **P10 (anti-vacuity).** B0 has gain 0 and harm 0 in every condition, so P1 is what separates a working
  loop from one that never changes. `--selftest`: with B3's contract and confidence gate switched off, B3's
  numbers must equal B2's.

## Results (from `python3 scripts/note064_reference.py`, pasted)

x86-64 container; Python 3.11.16, 3.12.3 and 3.13.15 print byte-identical output (digest
`04d52f1c6a146aebbd7988ae9c0cca28123ec8dca69122fa85aa59b81f3f3b1f`). The script exits 0 only if a run
reproduces this recorded outcome, so CI catches drift. **NOT VALIDATED on the S25.**

```
note064_reference.py -- governed outcome feedback (synthetic; one learned parameter: tau)
world: p(s)=1/(1+exp(-12(s-c))), c=0.45; tau0=0.7; 2000 feedback cases, exploration 0.2; 100 seeds; bootstrap 500
U(0.70)=0.2922  U(0.45)=0.4347  available gain 0.1426  |  drift world c=0.75: U(0.70)=0.1352 U(0.45)=-0.0464

[TRUE]  mean outcome completeness 1.0000  (deployment world c=0.45, U(tau0)=0.2922)
  arm   deploy  harmful  mean gain  tau deployed (median)
  B0      0.00     0.00     0.0000  0.70
  B1      1.00     0.00     0.1387  0.45
  B1s     0.99     0.99    -0.1736  0.90
  B2      1.00     0.00     0.1367  0.45
  B3      0.98     0.00     0.1340  0.45

[NC1_RANDOM]  mean outcome completeness 1.0000  (deployment world c=0.45, U(tau0)=0.2922)
  arm   deploy  harmful  mean gain  tau deployed (median)
  B0      0.00     0.00     0.0000  0.70
  B1      0.98     0.73    -0.0847  0.65
  B1s     0.98     0.80    -0.1338  0.90
  B2      0.50     0.35    -0.0431  0.70
  B3      0.04     0.03    -0.0034  0.70

[NC2_CORRUPTED]  mean outcome completeness 1.0000  (deployment world c=0.45, U(tau0)=0.2922)
  arm   deploy  harmful  mean gain  tau deployed (median)
  B0      0.00     0.00     0.0000  0.70
  B1      1.00     1.00    -0.0464  0.15
  B1s     0.99     0.99    -0.1736  0.90
  B2      1.00     1.00    -0.0464  0.15
  B3      1.00     1.00    -0.0464  0.15

[NC3_MISSING]  mean outcome completeness 0.8743  (deployment world c=0.45, U(tau0)=0.2922)
  arm   deploy  harmful  mean gain  tau deployed (median)
  B0      0.00     0.00     0.0000  0.70
  B1      1.00     1.00    -0.1671  0.00
  B1s     0.92     0.92    -0.1323  0.85
  B2      1.00     0.00     0.1205  0.40
  B3      0.00     0.00     0.0000  0.70

[NC6_LEAKAGE]  mean outcome completeness 1.0000  (deployment world c=0.45, U(tau0)=0.2922)
  arm   deploy  harmful  mean gain  tau deployed (median)
  B0      0.00     0.00     0.0000  0.70
  B1      0.98     0.01     0.0775  0.60
  B1s     0.99     0.99    -0.1796  0.90
  B2      1.00     0.00     0.1367  0.45
  B3      0.97     0.00     0.1329  0.45

[DRIFT]  mean outcome completeness 1.0000  (deployment world c=0.75, U(tau0)=0.1352)
  arm   deploy  harmful  mean gain  tau deployed (median)
  B0      0.00     0.00     0.0000  0.70
  B1      1.00     1.00    -0.1787  0.45
  B1s     0.99     0.85    -0.0452  0.90
  B2      1.00     1.00    -0.1831  0.45
  B3      0.98     0.98    -0.1785  0.45

price of governance (TRUE): B2 gain 0.1367 - B3 gain 0.1340 = 0.0027 per case (0.0190 of the available gain)
AS REGISTERED      P1  TRUE: B1, B2, B3 mean gain > 0; B3 deploys >= 0.80
AS REGISTERED      P2  TRUE: |gain B1 - gain B2| <= 0.1 x available gain
AS REGISTERED      P3  NC1: harm B3 <= 0.05, B1 >= 0.20, B1 >= B2 >= B3
AS REGISTERED      P4  NC3: harm B1 >= 0.90; B3 deploys 0; 0 < gain B2 < its TRUE gain
NOT AS REGISTERED  P5  NC6: gain B1 <= 0; B2 and B3 identical to TRUE, seed by seed
AS REGISTERED      P6  NC2 (registered FAIL of governance): harm B3 >= 0.50
AS REGISTERED      P7  DRIFT (registered FAIL of governance): harm B3 >= 0.50
AS REGISTERED      P8  TRUE: gain B3 <= gain B2 (price of the confidence gate)
AS REGISTERED      P9  TRUE: harm B1s (self-graded) >= 0.90
AS REGISTERED      P10 B0 gain 0, harm 0 everywhere; B3 with governance off == B2, seed by seed
VERDICT  9 of 10 as registered
```

### Which separation prevents which false improvement (in this world)

| Separation | What it prevented | Evidence |
|---|---|---|
| Decision-time records (EBLL `DecisionRecord`) | leakage from later system state | B2 identical to TRUE in 100 of 100 seeds; naive gain fell from 0.1387 to 0.0775 |
| Missing outcome = unknown (`success=None`), not success | catastrophic over-acting | NC3: B1 harmful 1.00 (τ 0.00), B2 harmful 0.00 |
| Fixed metric chosen before learning | self-grading | B1s harmful 0.99 in TRUE (τ 0.90) |
| Held-out randomized slice | about half of the harm from uninformative feedback | NC1 harmful: B1 0.73 → B2 0.35 |
| 95% confidence gate | almost all of the rest | NC1 harmful: B3 0.03; price in TRUE 0.0027 per case (0.0190 of the available gain) |
| Completeness contract | nothing harmful in this world; cost the whole NC3 gain | B3 deploy 0.00 vs B2 gain 0.1205 |
| **none** | shared corrupted outcome source; drift | NC2 harmful 1.00 (all learning arms); DRIFT B3 harmful 0.98 |

**Simplest rival.** With clean, complete feedback, naive feedback did as well as the evaluated loop (B1 0.1387,
B2 0.1367, B3 0.1340; P2 held). The improvement comes from feedback itself. Every separation's value appears
only under the adverse conditions, and two of those conditions defeat all of them.

**Answer to the question asked.** In this synthetic world: converting outcomes into evaluated,
provenance-preserving feedback does improve decisions on new cases (B3 reaches 0.1340 of 0.1426 available).
The separations each block a specific, named false improvement, at a measurable price. They do not make
feedback trustworthy when the outcome source itself is wrong or the world has moved. Novelty status:
**OVERLAPS EXISTING WORK**.

## Reference code

`scripts/note064_reference.py` — stdlib only; builds every record with `ebll.records` and `ebll.store`
([[note063_evidence_bound_learning_loop]]). Prints every number in this note.

## Falsifiable next predictions

Recommended next, one only: **D1**. It tests the failure no separation caught (a corrupted outcome source)
with the estate's existing idea of independent corroboration (EL-007 counts independent roots, not documents).

- **D1 (unrun).** Two independent outcome sources (e.g. a second reviewer) would expose NC2. Prediction:
  disagreement rate between sources flags the corrupted region before deployment.
- **D2 (unrun).** A short fresh-data probe in the deployment world would catch DRIFT. Prediction: a 100-case
  post-drift randomized slice makes B3 reject the harmful change in ≥ 90% of seeds.
- **D3 (unrun).** Real data: a Sovereign Veritas decision/outcome export with genuine outcomes.

---
*Checklist before PR: [x] status label honest  [x] claims registered & numbered  [x] refuted claims kept
(P5)  [x] numbers match code output (pasted; pinned by digest)  [x] at least one open prediction (D1–D3)
[x] credit given, including to AIs  [x] outgoing wikilink*
