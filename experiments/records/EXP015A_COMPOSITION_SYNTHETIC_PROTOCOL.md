# EXP015-A — Composition and hidden-history controls

**Status:** exploratory synthetic instrument; no model-based claims.
**Source:** [Research Note #015](../../research_notes/015_category_theoretic_compositionality.md)
**Implementation:** [exp015a_composition.py](../exp015a_composition.py)

## Question
Can exact finite stochastic transitions satisfy composition and identity while an observation-only state representation fails to admit one history-independent next-step kernel?

## Fixed protocol (registered with implementation; not prospectively preregistered)
- Use rational arithmetic, no RNG or floating-point tolerances.
- Construct three 2×2 row-stochastic kernels and check associativity and both identity laws.
- Negative control: two different histories map to the same observed state 0, but yield incompatible next-state distributions (1,0) and (0,1).
- Compute mean total-variation distance for common prediction (1/2,1/2).
- Fail on assertion errors; run `python experiments/exp015a_composition.py`.

## Expected outputs and interpretation
- Associativity: PASS, as guaranteed mathematically for valid matrix composition.
- Identity: PASS.
- Observation-only history independence: REFUTED for the constructed counterexample.
- Mean TV loss for the common prediction: 1/2. In fact any common Bernoulli prediction has mean TV loss 1/2 for these two equally weighted extreme targets.

## Boundaries
This checks an implementation of already-established mathematics and a synthetic state-aliasing counterexample. It is **not** a proof about transformer reasoning, empirical evidence of hidden state, or validation of a functor from real reasoning traces. A full history state could restore a Markov description. The note's categorical claims require a specified source category and actual functor mapping; matrix associativity alone does not supply one.

## Initial execution
Local execution in the assistant's isolated Python environment completed successfully with:
```json
{"associativity": "PASS", "history_independent_transition": "REFUTED for constructed example", "left_right_identity": "PASS", "mean_tv_error_common_prediction": "1/2"}
```
No independent device reproduction, CI result, or external review is claimed.

## Follow-on gates
1. Add negative tests for malformed matrices and dimension mismatches.
2. Pre-register a real-model state abstraction, dataset, held-out predictions, and a history-sensitive alternative.
3. Run a blinded comparison before drawing empirical claims.
