# CST-001 amendment: hop-2 pairs only, Qwen2.5-7B-Instruct (4-bit)

**State:** written 2026-11-15, before any output on the new split exists. Chad Holland chose this option after the
7B feasibility result ([FEASIBILITY_7B.md](FEASIBILITY_7B.md)). Self-tested. **This is a design change made after
seeing dev data, and is disclosed as such (C-EXPLORE, C-HOLDOUT).**

## What changes, and why

On dev, the explicit instruction moved hop-2 pairs from 0 to 12 of 32 and *lowered* hop-1 pairs. The primary
endpoint becomes **pairs correct on hop-2 pairs only**, the cases where one report goes through an intermediate
document. That is where tracing matters and where the positive control showed it can work. Everything else in
[DESIGN.md](DESIGN.md) is unchanged: arms A–E, the exposures, the scorer, greedy decoding and the model file.

Because the old dev split chose this change, it cannot also confirm it. So:

1. **Re-qualification on a new split, dev2** (seed 7404; seal `c3a0cd1b…c71a`; 32 hop-2 pairs; it shares no prompt
   with qual, dev or test). Arms E and D run first.
2. **Gate, fixed now:** E gets at least 8 of 32 hop-2 pairs right, **and** E beats D by at least 6 pairs. If the
   gate fails, CST-001 stops for this model.
3. If the gate passes, arms A, B and C also run on dev2, which serves only to set the minimum meaningful gain. The
   confirmatory registration (endpoint, test, threshold and stopping rule) is then written and committed **before**
   the sealed test split's 64 hop-2 pairs are run. The test split's seal (`f92ac0fa…0ec4`) is unchanged; its hop-1
   pairs are not used.

## What this costs

- 64 test pairs per arm detect only a large difference between A and B. That limit gets a number in the
  registration.
- Restricting to hop 2 narrows the claim. A result would be about two-step source tracing only.
