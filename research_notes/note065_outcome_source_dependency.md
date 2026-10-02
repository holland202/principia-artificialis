# Note #065 — Can the outcome-source dependency be removed, or only moved?

**Status:** Draft — REGISTERED, UNRUN (committed before `scripts/note065_reference.py` exists)
**Theme:** Learning Theory / Evaluation / Evidence
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's request ("attack the remaining dependency on
the outcome source")
**Builds on:** [[note064_governed_outcome_feedback]] (its NC2: a corrupted outcome source shared by learner
and evaluator made every arm harmful, 1.00; its unrun door D1), [[note063_evidence_bound_learning_loop]]
(EBLL records), evidence-ledger EL-007 (counting independent roots, not documents)

## The claim

No learning loop can remove its dependence on *some* source of truth about outcomes. It can only (a) detect
disagreement between sources, (b) adjudicate between sources whose independence is real, or (c) shrink the
trusted part to a small, randomly chosen, independently measured audit whose selection the source cannot
anticipate. Each of these fails in a specific, nameable way. Stated so it can be wrong: if some arm below
stays safe **and** keeps its gain under every attack, including a corrupted audit, the claim is refuted.

## Epistemic status (read first)

Same synthetic world as note064 (one learned parameter, τ). Every mechanism here is standard; the question
is which of them earns its cost in this estate, and what each still depends on. Nothing is measured on a
device or on real outcome data.

## Known mathematics / prior art

- Two noisy labellers can expose disagreement but cannot say which is right; with three or more labellers
  that are conditionally independent given the truth, error rates become identifiable without ground truth
  (Dawid & Skene, *Applied Statistics* 1979; identifiability: Allman, Matias & Rhodes, *Annals of Statistics*
  2009 — both cited from memory, not re-checked in this session).
- **Prediction-powered inference** (Angelopoulos, Bates, Fannjiang, Jordan & Zrnic, *Science* 382:669–674,
  2023): a large set of cheap, possibly biased labels plus a small random set of gold labels gives a
  rectified estimate whose validity rests on the gold set alone.
- **Risk-limiting audits** (Stark, "Conservative statistical post-election audits", *Annals of Applied
  Statistics* 2008): results are committed first, then a random sample is checked against an independent
  record. The audit is only as good as the commitment and the randomness.
- Correlated sources counted as independent: EL-007 P5 (one root, eight documents).

Novelty status: **OVERLAPS EXISTING WORK**.

## The experiment

**World and loop** — exactly note064's: p(s)=1/(1+e^(−12(s−0.45))), τ0 = 0.70, 2,000 feedback cases, 20%
randomized exploration split into development and held-out halves before learning, utility +1/−1/0,
100 seeds, the same grid learner (ties to τ0), deployment only if the 95% bootstrap lower bound (500
resamples) of the held-out gain is > 0. **Changed on purpose:** bootstrap randomness is seeded by seed and
arm only, never by condition (note064 P5's instrument flaw), so identical inputs give identical outputs.

**Outcome sources.** Three cheap sources: src1 (root A), src2 (root B), src3 (root C). Each reports its
root's upstream value, then flips it with its own independent noise, η = 0.05. An honest root's upstream
is the true outcome; a corrupted root reports **success for every failure with s ∈ [0.15, 0.45)** (note064's
NC2). A **gold** source (an expensive, independent measurement) is perfect unless stated. Gold audits: 100
random acted learning cases and 50 random acted held-out cases per batch, the same cases in every arm that
uses them.

**Arms**

| Arm | Mechanism |
|---|---|
| NONE | no feedback |
| R0 | src1 only (note064's single-source loop) |
| R1f | src1 + src2, learn only from cases where they agree |
| R1a | R1f + disagreement alarm: any 0.1-wide score band with ≥ 30 cases and ≥ 0.25 disagreement → DEFER |
| R2m | src1 + src2 + src3, majority vote |
| R2r | root-aware: majority vote only if the sources declare ≥ 3 distinct roots; otherwise R1a between one source per root |
| R3v | src1 + gold audit, prediction-powered (rectified) learning and evaluation; the audit selection is **visible** to the outcome source before it reports |
| R3c | same, but **commit-then-audit**: the selection is drawn after the source's reports are fixed |

**Conditions**

| Condition | src1 | src2 | src3 | gold |
|---|---|---|---|---|
| CLEAN | honest A | honest B | honest C | honest |
| ONE_CORRUPT | corrupted A | honest B | honest C | honest |
| COMMON_DECLARED | corrupted A | copies A's upstream, declares root A | honest C | honest |
| COMMON_HIDDEN | corrupted A | copies A's upstream, declares root **B** | honest C | honest |
| AUDIT_AWARE | corrupts only cases it can see are unaudited (R3v); with nothing visible, all (= ONE_CORRUPT) | honest | honest | honest |
| GOLD_CORRUPT | corrupted A | honest | honest | **shares A's corruption** |

**Measured per arm × condition:** deploy rate, harmful-deploy rate, mean new-case utility gain (as note064),
and the outcome observations each arm consumes per batch (its cost).

### Registered predictions

- **Q1 (anti-vacuity, CLEAN).** Every learning arm has mean gain > 0 and harmful ≤ 0.05. NONE gains 0.
- **Q2 (ONE_CORRUPT).** R0 harmful ≥ 0.90 (note064's NC2 reproduced with noisy sources). **R1f harmful ≥
  0.90: requiring two sources to agree keeps the bias**, because it drops exactly the failures the corrupted
  source mislabels. R1a deploys ≤ 0.05 (detects, cannot fix). R2m and R2r harmful ≤ 0.05 with mean gain ≥ 0.8
  × their own CLEAN gain. R3v and R3c harmful ≤ 0.05 with mean gain > 0.
- **Q3 (COMMON_DECLARED).** R2m harmful ≥ 0.90 (two of three sources share the corrupted root). R2r deploys
  ≤ 0.05 (counts two roots, alarms). R3c identical to its ONE_CORRUPT result, seed by seed.
- **Q4 (COMMON_HIDDEN — registered to FAIL for root counting).** R2r harmful ≥ 0.90: a false lineage
  declaration defeats it. R3c identical to its ONE_CORRUPT result.
- **Q5 (AUDIT_AWARE).** R3v harmful ≥ 0.90: a source that knows which cases are audited corrupts only the
  others. R3c identical to its ONE_CORRUPT result: committing before the audit draw is what protects.
- **Q6 (GOLD_CORRUPT — registered to FAIL for auditing).** R3c harmful ≥ 0.90: the dependency moved to the
  gold source; it was not removed. R2m identical to its ONE_CORRUPT result (it never reads gold).
- **Q7 (price, CLEAN).** R3c mean gain ≤ R0 mean gain. Observations per batch printed for every arm.
- **Q8 (anti-vacuity of the audit).** R3c with the rectifier switched off (gold replaced by the cheap label)
  is harmful ≥ 0.90 under ONE_CORRUPT: the audit, not something else, is what protects. NONE: gain 0 and
  harm 0 in every condition.

## Reference code

`scripts/note065_reference.py` (written after this registration is committed); stdlib only; outcome reports
stored as EBLL `OutcomeRecord`s with each source's declared root in `provenance`.

## Falsifiable next predictions

- **D1 (unrun).** R3c's protection is exactly as strong as the commitment. If the source can revise
  unaudited reports after the draw (no external witness of the committed reports, cf. EL-007 P8), R3c
  degrades to R3v. Prediction: same harmful rate as R3v.
- **D2 (unrun).** A Dawid–Skene estimator would beat majority vote when the honest sources have unequal noise.
- **D3 (unrun).** Applying R3c to Sovereign Veritas evidence (not learning outcomes): randomly audit
  committed packages against an independent measurement, as in V12/V13's position cross-check.

---
*Checklist before PR: [x] status label honest  [x] claims registered & numbered  [ ] refuted claims kept
(after the run)  [ ] numbers match code output (after the run)  [x] at least one open prediction  [x] credit
given, including to AIs  [x] outgoing wikilink*
