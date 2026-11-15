# CST-001 feasibility, second model: Qwen2.5-7B-Instruct (4-bit, llama.cpp)

**State:** gate written 2026-11-15, before any 7B output was scored. Chad Holland chose a larger model run on this
machine (2026-11-15). Dev split only; the test split stays sealed. Self-tested.
**Model:** `Qwen/Qwen2.5-7B-Instruct-GGUF` revision `bb5d59e`, Q4_K_M, files `…00001-of-00002.gguf` (SHA-256
`dfce12e3…72db`) and `…00002-of-00002.gguf` (SHA-256 `539cf93f…d72a`). llama-cpp-python 0.3.37, temperature 0,
top-k 1, 2 CPU threads. The Q4 quantization is part of what is tested: results describe this file, not the
full-precision model.

## Gate, fixed before any 7B result is seen

Arms E (explicit instruction) and D (none) run first on the 64 dev pairs. Arms A, B and C run only if **both** hold:

1. E gets at least 16 of 64 pairs right (25%), so the assay can see the behaviour at all;
2. E gets more pairs right than D.

If the gate fails, CST-001 stops for this model too, and the result is recorded the same way as for the 1.5B model.
Two timing calls (arm D, first dev pair) were made before this gate was written. Their outputs were discarded and
not scored. Greedy decoding reproduces them.

## Result (appended after the run; the gate above is unchanged)

**Gate FAILED on condition 2, so arms A, B and C were not run.** E got 26 of 64 pairs, which passes condition 1
(≥ 16). D also got 26 of 64, so condition 2 (E above D) fails on a tie. The rule is applied as written, not loosened
after the fact. Raw outputs: [`dev_outputs_7b.jsonl`](../../results/cst_001/dev_outputs_7b.jsonl), 256 lines. Scores:
[`dev_analysis_7b.txt`](../../results/cst_001/dev_analysis_7b.txt). Pair patterns by hop:
[`dev_pair_patterns_7b.txt`](../../results/cst_001/dev_pair_patterns_7b.txt). Malformed answers: 0.

**The tie hides two opposite effects.** Pairs right, by difficulty, out of 32 each:

| Arm | Hop 1 (each report names its observation) | Hop 2 (one report goes through an intermediate document) |
|---|---|---|
| D, no instruction | **26** | **0** |
| E, explicit instruction | 14 | 12 |

- **Without instruction, 7B handles the easy cases and fails every hard one.** On hop 1 it gets 26 of 32 pairs.
  On hop 2 it says INSUFFICIENT to both versions 28 times out of 32: when a report cites an intermediate document, it
  treats the claim as unconfirmed whatever the document's note says.
- **The instruction helps the hard cases and hurts the easy ones.** Hop 2 goes from 0 to 12 pairs. Here 37 of the
  128 answers carry visible reasoning, all of them on hop 2. Hop 1 drops from 26 to 14. Its 18 errors are both
  versions CONFIRMED, given as a bare decision line with no reasoning. One read in full: the two reports cite the same
  `count sheet CS-903`, and the answer is `DECISION: CONFIRMED`.
- **Unlike the 1.5B model, 7B is not backwards.** In D it gets the direction right on hop 1 (26 correct, 0
  backwards), and the backwards pattern appears in only 5 of 128 pairs across both arms.

**What this means.** The 7B model can do the procedure: unprompted on simple cases, and with the instruction on some
two-step cases. But the registered positive control, measured over all pairs, does not separate E from D. So the
design as written cannot attribute a change to exposure in this model, because the instruction itself changes
behaviour in two opposite directions. This is exploration on dev (C-EXPLORE).

**Options (owner decision):**

1. **Hop 2 only.** Restrict the endpoint to hop-2 pairs, where the instruction clearly works (0 → 12 of 32) and the
   baseline is at zero. That is a design change made after seeing dev. It must be re-qualified on a **new** dev
   seed before the sealed test split is used, and the change has to be disclosed.
2. **Stop CST-001** at this capability level, and record both models' results in note074.
