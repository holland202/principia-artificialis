# Note #065 — Can the outcome-source dependency be removed, or only moved?

**Status:** Draft, verified reference code — 7 of 8 registered predictions held; **Q2 REFUTED (kept)**. Registration committed at `2c4cb6d`, before the code existed.
**Theme:** Learning Theory / Evaluation / Evidence
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's request ("attack the remaining dependency on
the outcome source")
**Builds on:** [[note064_governed_outcome_feedback]] (its NC2: a corrupted outcome source shared by learner
and evaluator made every arm harmful, 1.00; its unrun door D1), [[note063_evidence_bound_learning_loop]]
(EBLL records), evidence-ledger EL-007 (counting independent roots, not documents)

## What broke (read first)

**Q2 — REFUTED (kept), on one clause.** I registered that learning only from cases where two sources agree
(R1f) would be harmful in ≥ 0.90 of seeds under one corrupted source. Observed: harmful **0.33**, mean gain
**0.0032** (against **0.1290** for the same arm with clean sources), median deployed τ **0.20**. Every other
clause of Q2 held.

What the failure taught: agreement filtering does not fill the corrupted region with false successes; it
*empties* it. In s ∈ [0.15, 0.45) true failures are dropped (the sources disagree) and true successes there
are rare, so the learner sees almost no evidence in that region, and the registered tie rule (ties go to
the τ nearest 0.70) stops it partway in, at 0.20 instead of 0.15. Whether τ = 0.20 counts as harmful is a
knife edge in this world: **U(0.20)=0.2922** equals **U(0.70)=0.2922** to four decimals (diagnostic line
added to the output after the first run; no computation changed, every other printed line was
byte-identical). The robust result is the gain collapse: requiring agreement destroyed the improvement
instead of protecting it.

**Registered to fail, and they did:**
- A false lineage declaration defeats root counting: COMMON_HIDDEN, R2r harmful **1.00**.
- A corrupted gold source defeats the audit: GOLD_CORRUPT, R3c harmful **1.00**. The dependency moved to
  the gold source; it was not removed.

**Not registered, worth stating:** two sources that share a root agree with each other, so the two-source
alarm (R1a) is silent and the arm is harmful (**0.99**) under common-mode corruption, even when the shared
root is declared. Only the root-aware arm reads the declaration.

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

## Results (from `python3 scripts/note065_reference.py`, pasted)

x86-64 container; Python 3.11.16, 3.12.3 and 3.13.15 print byte-identical output (digest
`bfa4d689c2e3429b45eb71d3b95c3e205e26e2bab0baa1aad19a33b16cbfd3c3`); the script exits 0 only if a run
reproduces this. **NOT VALIDATED on the S25.**

```
note065_reference.py -- outcome-source dependency (synthetic; note064 world; one learned parameter)
world as note064: U(0.70)=0.2922 U(0.45)=0.4347 available gain 0.1426; source noise eta=0.05; gold audits 100+50; alarm band>=30 cases, disagreement>=0.25; 100 seeds; bootstrap 500
utility by tau: U(0.15)=0.2458  U(0.20)=0.2922  U(0.25)=0.3358  U(0.30)=0.3747  U(0.45)=0.4347  (harmful = below U(0.70)=0.2922)

[CLEAN]
  arm       deploy  harmful  mean gain  tau (median)  observations/batch
  NONE        0.00     0.00     0.0000          0.70  0.0
  R0          0.97     0.00     0.1327          0.45  882.0
  R1f         0.94     0.00     0.1290          0.45  1764.0
  R1a         0.94     0.00     0.1290          0.45  1764.0
  R2m         0.97     0.00     0.1330          0.45  2646.1
  R2r         0.97     0.00     0.1330          0.45  2646.1
  R3v         0.84     0.00     0.1133          0.45  1032.0
  R3c         0.84     0.00     0.1133          0.45  1032.0
  R3c_off     0.95     0.00     0.1302          0.45  882.0

[ONE_CORRUPT]
  arm       deploy  harmful  mean gain  tau (median)  observations/batch
  NONE        0.00     0.00     0.0000          0.70  0.0
  R0          1.00     0.99    -0.0459          0.15  882.0
  R1f         0.99     0.33     0.0032          0.20  1764.0
  R1a         0.00     0.00     0.0000          0.70  1764.0
  R2m         0.95     0.00     0.1277          0.45  2646.1
  R2r         0.95     0.00     0.1277          0.45  2646.1
  R3v         0.47     0.00     0.0625          0.70  1032.0
  R3c         0.45     0.00     0.0597          0.70  1032.0
  R3c_off     1.00     0.99    -0.0459          0.15  882.0

[COMMON_DECLARED]
  arm       deploy  harmful  mean gain  tau (median)  observations/batch
  NONE        0.00     0.00     0.0000          0.70  0.0
  R0          1.00     0.99    -0.0459          0.15  882.0
  R1f         1.00     1.00    -0.0464          0.15  1764.0
  R1a         0.99     0.99    -0.0459          0.15  1764.0
  R2m         1.00     1.00    -0.0464          0.15  2646.1
  R2r         0.00     0.00     0.0000          0.70  2646.1
  R3v         0.47     0.00     0.0625          0.70  1032.0
  R3c         0.45     0.00     0.0597          0.70  1032.0
  R3c_off     1.00     0.99    -0.0459          0.15  882.0

[COMMON_HIDDEN]
  arm       deploy  harmful  mean gain  tau (median)  observations/batch
  NONE        0.00     0.00     0.0000          0.70  0.0
  R0          1.00     0.99    -0.0459          0.15  882.0
  R1f         1.00     1.00    -0.0464          0.15  1764.0
  R1a         0.99     0.99    -0.0459          0.15  1764.0
  R2m         1.00     1.00    -0.0464          0.15  2646.1
  R2r         1.00     1.00    -0.0464          0.15  2646.1
  R3v         0.47     0.00     0.0625          0.70  1032.0
  R3c         0.45     0.00     0.0597          0.70  1032.0
  R3c_off     1.00     0.99    -0.0459          0.15  882.0

[AUDIT_AWARE]
  arm       deploy  harmful  mean gain  tau (median)  observations/batch
  NONE        0.00     0.00     0.0000          0.70  0.0
  R0          1.00     0.99    -0.0459          0.15  882.0
  R1f         0.99     0.33     0.0032          0.20  1764.0
  R1a         0.00     0.00     0.0000          0.70  1764.0
  R2m         0.95     0.00     0.1277          0.45  2646.1
  R2r         0.95     0.00     0.1277          0.45  2646.1
  R3v         0.98     0.90    -0.0405          0.15  1032.0
  R3c         0.45     0.00     0.0597          0.70  1032.0
  R3c_off     1.00     0.99    -0.0459          0.15  882.0

[GOLD_CORRUPT]
  arm       deploy  harmful  mean gain  tau (median)  observations/batch
  NONE        0.00     0.00     0.0000          0.70  0.0
  R0          1.00     0.99    -0.0459          0.15  882.0
  R1f         0.99     0.33     0.0032          0.20  1764.0
  R1a         0.00     0.00     0.0000          0.70  1764.0
  R2m         0.95     0.00     0.1277          0.45  2646.1
  R2r         0.95     0.00     0.1277          0.45  2646.1
  R3v         1.00     1.00    -0.0469          0.15  1032.0
  R3c         1.00     1.00    -0.0469          0.15  1032.0
  R3c_off     1.00     0.99    -0.0459          0.15  882.0

AS REGISTERED      Q1 CLEAN: every learning arm gain > 0 and harm <= 0.05; NONE gain 0
NOT AS REGISTERED  Q2 ONE_CORRUPT: R0, R1f harm >= 0.90; R1a deploy <= 0.05; R2m, R2r harm <= 0.05 and gain >= 0.8 x own CLEAN; R3v, R3c harm <= 0.05 and gain > 0
AS REGISTERED      Q3 COMMON_DECLARED: R2m harm >= 0.90; R2r deploy <= 0.05; R3c identical to ONE_CORRUPT
AS REGISTERED      Q4 COMMON_HIDDEN (registered FAIL of root counting): R2r harm >= 0.90; R3c identical to ONE_CORRUPT
AS REGISTERED      Q5 AUDIT_AWARE: R3v harm >= 0.90; R3c identical to ONE_CORRUPT
AS REGISTERED      Q6 GOLD_CORRUPT (registered FAIL of auditing): R3c harm >= 0.90; R2m identical to ONE_CORRUPT
AS REGISTERED      Q7 CLEAN: gain R3c <= gain R0 (price of the audit)
AS REGISTERED      Q8 ONE_CORRUPT: R3c_off harm >= 0.90; NONE gain 0 and harm 0 everywhere
VERDICT  7 of 8 as registered
```

### What each mechanism protects against, what it still depends on, and what it costs

| Arm | Protects against | Still fails when | Observations per batch | Gain, one corrupted source |
|---|---|---|---|---|
| R0 one source | nothing | that source is corrupted (harmful 0.99) | 882.0 | -0.0459 |
| R1f two sources, agreement | nothing | always: gain collapses (0.0032) | 1764.0 | 0.0032 |
| R1a two sources, alarm | one corrupted source: detected, never fixed (deploy 0.00) | the two share a root, even declared (harmful 0.99) | 1764.0 | 0.0000 |
| R2m three sources, majority | one corrupted source (harmful 0.00) | two share a root (harmful 1.00) | 2646.1 | 0.1277 |
| R2r three sources, root-aware | also a declared common root (deploy 0.00) | the lineage is declared falsely (harmful 1.00) | 2646.1 | 0.1277 |
| R3v gold audit, selection visible | corruption that ignores the audit (harmful 0.00) | the source can see which cases are audited (harmful 0.90) | 1032.0 | 0.0625 |
| R3c gold audit, commit-then-audit | every cheap-source attack tried: one corrupted, common root declared or hidden, audit-aware (identical results, seed by seed) | the gold source is corrupted (harmful 1.00) | 1032.0 | 0.0597 |

**The answer to the question in the title: moved, not removed.** Two end states survive their own attacks
in this world, and each rests on a different, explicit assumption:

1. **Three or more independent roots, with truthful lineage** (R2r): nearly the clean gain (0.1277 vs
   0.1330) at 2646.1 outcome observations per batch. It rests on lineage being true; a lie defeats it.
2. **A small committed random audit against a trusted measurement** (R3c): unaffected by anything the cheap
   source does, at 1032.0 observations per batch, but it keeps less of the gain (0.0597 under corruption;
   0.1133 vs 0.1327 even with clean sources, because the audit's noise makes the gate cautious, deploy
   0.84). It rests on two things: the gold measurement, and the reports being committed before the audit
   draw. Making the gold source wrong, or the draw visible, defeats it.

What cannot be bought at any price here is independence from *every* source. The engineering choice is
which assumption is cheaper to make true and to check in a given deployment: lineage (who measured what,
from which upstream) or gold integrity plus commitment. For this estate the second maps onto parts that
already exist: an append-only, witnessed ledger is a commitment (EL-007 P8: without an external witness a
rollback is invisible, so commitment needs the witness).

## Reference code

`scripts/note065_reference.py` — stdlib only; every report is an EBLL `OutcomeRecord` with its source in
`source` and its declared root in `provenance`; arms read the store, not the generator.

## Falsifiable next predictions

Recommended next, one only: **D1** — it tests the one assumption R3c adds that this estate can actually
enforce (a witnessed commitment), rather than the one it cannot (gold integrity).

- **D1 (unrun).** R3c's protection is exactly as strong as the commitment. If the source can revise
  unaudited reports after the draw (no external witness of the committed reports, cf. EL-007 P8), R3c
  degrades to R3v. Prediction: same harmful rate as R3v.
- **D2 (unrun).** A Dawid–Skene estimator would beat majority vote when the honest sources have unequal noise.
- **D3 (unrun).** Applying R3c to Sovereign Veritas evidence (not learning outcomes): randomly audit
  committed packages against an independent measurement, as in V12/V13's position cross-check.

---
*Checklist before PR: [x] status label honest  [x] claims registered & numbered  [x] refuted claims kept
(Q2)  [x] numbers match code output (pasted; pinned by digest)  [x] at least one open prediction (D1–D3)
[x] credit given, including to AIs  [x] outgoing wikilink*
