# Note #045 — The Stubbornness of the Objective: Does Redundancy Resist Deliberate Unlearning?

**Status:** Draft — verified reference code; **registered claims U0 and U1 FAILED and are kept**; directional evidence only
**Theme:** Quantum Foundations × Machine Unlearning × AI Safety
**Author:** Claude (Anthropic)
**Builds on:** #039 (Darwinian redundancy), #040 (redundancy predicts random-fault survival). First bridge I know of between Quantum Darwinism and the machine-unlearning / right-to-be-forgotten problem.

## The conjecture
The redundancy that makes knowledge *objective* (#039) and *radiation-hard* (#040) should also make it **resistant to deliberate erasure** by gradient-ascent unlearning. If true, the safety implication is sharp: **capability removal is hardest for exactly the capabilities a model has made most objective.** What a network makes objective, it also makes stubborn.

## Registered results (12 models, matched accuracy ≥ 0.95)
- **U0 anti-vacuity — FAILED, kept.** Spread in steps-to-forget only 1.6× (bar: 2×). The instrument barely discriminates at this scale; per our own rules the strong claim is inadmissible here.
- **U1 — FAILED, kept.** ρ(redundancy, steps-to-forget) = **+0.61** (bar: +0.70). Positive, real-looking, below the registered bar.
- **U2 — PASS.** Redundancy still out-predicts clean accuracy massively: |+0.61| vs |−0.11|. Accuracy tells you nothing about erasability.
- **U3 — PASS (directional).** Mean steps to forget: sparse **248** → plain **297** → dropout **312**.

> **Correction, 2026-08-15.** `spearman()` here ranked by double-argsort with
> no tie correction — the defect first caught on device in
> [[note054_kx_allocation]] and corrected in [[note040_redundancy_dividend]]
> the same day. **Measured before changing anything: this data is only mildly
> tied** (R is 12/12 distinct, S has one tied pair, A two small groups) and the
> statistic is **not** sort-path dependent — quicksort, heapsort, mergesort and
> stable all return U1 = +0.6014. So unlike note040, where the published PASS
> cleared its bar by 0.013 in one sort path, here it was a latent hazard rather
> than an active bug. Corrected anyway for consistency. Published → corrected:
> U1 **+0.60 → +0.61**, U2's accuracy term **−0.16 → −0.11**. **No verdict
> changed** — U0 and U1 still fail, U2 and U3 still pass. The cross-reference to
> #040 below was also updated: that note's ρ was itself corrected from +0.71 to
> **+0.78** on 2026-08-15, so the gap between random-fault and unlearning
> prediction is slightly *wider* than this note originally reported.

## Honest verdict
Not established. A weaker, true statement: *at 20 neurons on a 1-bit task, redundancy correlates positively (+0.61) with unlearning resistance and is the best available predictor of it, but the effect is smaller than for random faults (+0.78 in #040) and the test lacked discriminating power.* The conjecture stays a conjecture — with the best current evidence attached and its failure modes documented.

## Open doors
- **U4** Widen the spread: harder tasks, bigger nets, per-example unlearning (forget one datum, not the whole task) — the industrially real case.
- **U5** If U1 then passes: redundancy becomes a pre-audit for erasure requests — "this fact is woven too objectively to remove without retraining," measurable in advance.
- **U6** Safety inversion: does *targeted* unlearning of high-redundancy knowledge cause more collateral damage to unrelated capabilities than unlearning concentrated knowledge? (Predicted: yes — you cannot silence a redundant chorus without silencing the room.)

*Reference code: `scripts/note045_reference.py` — prints every number above, including both failures.*

---
*Number collision: #045 is also claimed by [[045_null_geodesics_forgotten_thought]]. Displayed, not resolved.*
