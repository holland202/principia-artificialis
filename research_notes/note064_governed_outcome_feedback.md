# Note #064 — Which separations in an outcome-feedback loop prevent which false improvements?

**Status:** Draft — REGISTERED, UNRUN (this version is committed before `scripts/note064_reference.py` exists)
**Theme:** Learning Theory / Governance / Evaluation
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's request
**Builds on:** [[note063_evidence_bound_learning_loop]] (EBLL records and store), METHOD_SWAY.md + Amendment 1
**Origin of the question:** Amanda Saunders asked whether reviewed audit records plus actual outcomes could
become a learning or evaluation loop. That is an external research prompt, not evidence that any architecture
here works. Note063 built the bookkeeping; this note tests whether the loop *improves decisions on new cases*,
and which of its separations matter.

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

## Reference code

`scripts/note064_reference.py` (to be written after this registration is committed). Stdlib only; uses
`ebll.records` and `ebll.store`.

## Falsifiable next predictions

- **D1 (unrun).** Two independent outcome sources (e.g. a second reviewer) would expose NC2. Prediction:
  disagreement rate between sources flags the corrupted region before deployment.
- **D2 (unrun).** A short fresh-data probe in the deployment world would catch DRIFT. Prediction: a 100-case
  post-drift randomized slice makes B3 reject the harmful change in ≥ 90% of seeds.
- **D3 (unrun).** Real data: a Sovereign Veritas decision/outcome export with genuine outcomes.

---
*Checklist before PR: [x] status label honest  [x] claims registered & numbered  [ ] refuted claims kept
(after the run)  [ ] numbers match code output (after the run)  [x] at least one open prediction  [x] credit
given, including to AIs  [x] outgoing wikilink*
