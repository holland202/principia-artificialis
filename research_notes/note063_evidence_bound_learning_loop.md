# Note #063 — Evidence-Bound Learning Loop (EBLL)

**Status:** Draft, verified reference code
**Theme:** Learning Theory / Governance / Epistemic Architecture
**Author:** Chad Edward Holland, with Grok (xAI)
**Builds on:** METHOD_SWAY.md, METHOD_SWAY_AMENDMENT_1.md, PROVENANCE.md

## The claim

There exists a mechanically checkable architectural boundary between
(1) immutable historical decision/outcome records (Sovereign Veritas side)
and (2) hypothesis-driven evaluation of candidate improvements (Principia
side) such that:

- the evaluation layer cannot rewrite the original decision history,
- every candidate change carries an explicit hypothesis registered before evaluation,
- outcomes are reported in the SWAY Amendment 1 vocabulary
  (SUPPORTED / REFUTED / INSUFFICIENT_EVIDENCE / ...),
- a failed hypothesis is retained rather than deleted,
- a promotion record is only an admission proposal, never a deploy instruction,
- the same deterministic inputs produce the same evaluation result.

This note demonstrates the boundary with a tiny synthetic reference
experiment. It does **not** claim autonomous learning, training, or
production deployment.

## Epistemic status (read first)

| Axis | Status |
|------|--------|
| Mathematical | The append-only / immutability invariants are definitional and hold by construction of the frozen records and store API. |
| Implementation | Reference code in `ebll/` and `scripts/note063_reference.py` runs and prints the claimed numbers. |
| Empirical | Synthetic history only. No real Sovereign Veritas decision stream was consumed. No claim is made about real-world agent improvement. |

The overall "learning loop" is **not validated**. The reference code is
verified to print the numbers below.

## Known mathematics / prior art

- SWAY (METHOD_SWAY.md) + Amendment 1: registered predictions, outcome
  vocabulary, three validity axes, refutations kept, simplest rival.
- Immutable logs / append-only stores (standard systems practice).
- Registered reports / pre-registration literature (the hypothesis-before-
  evaluation rule is the same discipline applied to candidate code changes).

No claim of novelty beyond the concrete boundary drawn for this estate.

## The experiment

### Registered predictions (written before the run)

- **P0 (anti-vacuity):** Baseline and candidate functions can return False
  on cases whose evidence is "noisy" or "unknown". The instrument is not
  forced to always return True.
- **P1:** On the synthetic development set, candidate v2 (evidence contains
  "stable" or "partial") achieves a strictly higher success rate than
  baseline v1 (evidence contains "stable" only). Result expected: SUPPORTED.
- **P2:** On the synthetic held-out set, the same ordering holds. Result
  expected: SUPPORTED.
- **P3:** Candidate v3 (always predict success) does **not** achieve a
  higher match-to-observed-success rate than baseline on held-out data.
  Result expected: REFUTED; the refutation is retained.
- **P4:** Attempting to promote a REFUTED evaluation yields PromotionStatus
  REJECTED.
- **P5:** Fingerprints of all decision and outcome records are identical
  before and after evaluation (history is immutable).

### Printed numbers (from `python scripts/note063_reference.py`)

```
n_decisions: 15
n_outcomes: 15
n_dev: 8
n_heldout: 7
H1_dev_result: SUPPORTED
H1_held_result: SUPPORTED
H2_held_result: REFUTED
H2_refutations_retained: True
H2_promotion: REJECTED
history_immutable: True
```

### What the experiment demonstrates

- historical evidence → hypothesis registration → candidate evaluation
  (dev + held-out) → SUPPORTED / REFUTED → retained result → promotion
  as admission proposal only.
- Original DecisionRecord / OutcomeRecord objects are never mutated by
  the evaluator.
- A deliberately failing candidate (v3) produces REFUTED and that record
  remains in the store.

### What the experiment does NOT demonstrate

- Training of any model.
- Automatic production deployment.
- Improvement of a real agent on real data.
- That the learning loop as a whole is "validated."
- That SUPPORTED is equivalent to a governance ALLOW or a deploy order.

## Reference code

- Package: `ebll/` (records, store, evaluator, experiment)
- Script: `scripts/note063_reference.py`
- Tests: `ebll/test_ebll.py`

Run:

```
python scripts/note063_reference.py
python -m pytest ebll/test_ebll.py -q
```

## Falsifiable next predictions

- **P6 (OPEN):** When the same evaluator is pointed at a real Sovereign
  Veritas decision/outcome export (format TBD), the immutability and
  hypothesis-before-evaluation invariants still hold and no original
  record is rewritten. Unrun.
- **P7 (OPEN):** A candidate whose only advantage is that it defines the
  metric will be rejected by the Circularity Test conventions already
  present in the estate. Unrun.

---
*Checklist before PR: [x] status label honest  [x] claims registered &
numbered  [x] refuted claims kept  [x] numbers match code output
[x] at least one open prediction  [x] credit given, including to AIs*
