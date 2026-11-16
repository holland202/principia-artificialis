# RMT-IH-001 part B registration: a dip in the top singular value, found after the first run

**Status:** REGISTERED, NOT RUN. Written after part A's run, and **prompted by an observation in its data**. So
part A's seeds 1–6 cannot test it, and fresh seeds are used. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-16). Design: Claude (Anthropic, Opus 5.5). Human review level:
direction only.

## The observation (exploratory, seeds 1–6, C-EXPLORE)

While reading part A's raw trajectories (`results/rmt_ih_001/trajectories.txt`), I noticed something in
`top_norm`, which is the largest QK singular value over the mean, pooled over heads:

- **In the repeat arm,** it fell below its running maximum by 1.18–2.08, at steps 920–1120. That is 120–140 steps
  before each seed's 50% point of the in-context-learning score.
- **In the norepeat arm,** it never fell (0.00 in all 6 seeds).

A fall of this kind was not looked for, and this is one pass over six seeds. **It needs fresh seeds.**

## Design

Identical to part A: same code at the commit that adds this file, same configuration, both arms. **Seeds 7–12.**

**Dip definition (`dip.py`, tested):** after step 400, the dip is the largest fall of `top_norm` below its running
maximum, recorded as a size and a step.

## Predictions

| ID | Prediction | Rule | Claude's prior |
|---|---|---|---|
| P6a | A dip occurs only when induction is possible | repeat dip ≥ 0.5 in ≥ 5 of 6 seeds **and** norepeat dip < 0.2 in ≥ 5 of 6 | 0.7 |
| P6b | The dip comes before the 50% point of the induction jump | in ≥ 5 of 6 repeat seeds | 0.7 |
| P6c | The dip comes before the jump's **onset** (the 10% point of the ICL score, same timing rule) | in ≥ 5 of 6 repeat seeds | 0.3 |

**Reading the outcome:**

- **P6a and P6b hold, P6c fails:** the dip marks the jump as it starts. That would be a signature of the transition,
  not an early warning.
- **P6c also holds:** it is a warning ahead of the onset.
- **P6a fails:** the observation was noise or a fluke of seeds 1–6.

**Prior work:**

- Spectral signals at or before induction-head formation are already reported: Xu (arXiv 2605.24059) uses the
  participation ratio of each head's activations, in Pythia-scale models. My part A search missed it.
- A dip in the normalised top singular value of the QK *weights* is what is being tested here. I have not found
  it in prior work, but have not searched beyond that.

## Unrun door

Whether the dip is carried by the layer-1 heads alone, and whether it appears at GPT-2 scale in Pythia's public
training checkpoints.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) → human validation: not performed → human editing/curation:
direction by Chad Holland, 2026-11-16 → human responsibility: Chad Holland. Review level: direction only.*
