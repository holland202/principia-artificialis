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

## Result on dev2 (appended after the run; everything above is unchanged)

Raw outputs: [`dev2_hop2_7b.jsonl`](../../results/cst_001/dev2_hop2_7b.jsonl), 320 lines (5 arms × 32 pairs × 2 versions). Scores:
[`dev2_hop2_analysis.txt`](../../results/cst_001/dev2_hop2_analysis.txt). Split by reply length:
[`dev2_hop2_length.txt`](../../results/cst_001/dev2_hop2_length.txt). Malformed answers: 0.

**Gate PASSED.** E got 10 of 32 hop-2 pairs (needed at least 8). D got 0 of 32, so E beat D by 10 (needed at least 6).

**But exposure to the procedure did nothing, and was no better than the other conversations.**

| Arm | Hop-2 pairs right | SHARED right | INDEPENDENT right | Replies with reasoning |
|---|---|---|---|---|
| A procedure | **0/32** | 32/32 | 0/32 | 0 |
| B other procedure | 0/32 | 31/32 | 1/32 | 0 |
| C neutral | 3/32 | 29/32 | 5/32 | 0 |
| D none | 0/32 | 25/32 | 1/32 | 0 |
| E explicit | 10/32 | 16/32 | 23/32 | 38 |

- **After the demonstration, the model answers INSUFFICIENT to all 64 hop-2 cases.** That is the same blanket
  caution as the no-exposure baseline, and slightly stronger.
- **Every pair E got right came with visible reasoning:** 10 of 23 pairs with a reply over 20 tokens, against 0 of
  9 pairs where both replies were short. No exposure arm ever produced a reasoned reply. **The instruction works by
  making the model reason, and seeing a partner reason did not make it reason.**
- This matches ChatGPT's (Codex) replay of the dev run, posted on issue #150: all 12 successful hop-2 pairs there
  also had a long reply.

**What this means for the confirmatory run.** dev2 sets the minimum meaningful gain of A over B, and dev2 shows A
and B both at 0 of 32. A registered run on the sealed test split would test a predicted null. That is legitimate,
but it would probably add little. It waits on Chad's decision, along with stopping here.

This is exploration on dev2. It is not a test of note074's hypothesis on the sealed split, and it covers one model
(4-bit 7B), one exposure topic and one procedure.
