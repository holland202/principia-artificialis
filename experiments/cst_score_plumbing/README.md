# CST score plumbing check (2026-11-16)

**What:** can the model's log-odds between two answer codes be read at the decision position, for the AUC estimand
proposed in issue #150 (note cst001/claude/006)? It uses the Qwen2.5-7B-Instruct Q4_K_M GGUF from the CST runs,
with llama-cpp-python 0.3.37, temperature 0, and the full next-token distribution read through `logits_all`.

**Scope:** toy arithmetic yes/no prompts only. No CST case, split, exposure or holdout was used. This qualifies an
instrument; it is not an experiment. Run by Claude (Anthropic, Opus 5.5) at Chad Holland's direction.
SELF-TESTED.

**Raw output:**
- [`run.txt`](../../results/cst_score_plumbing/run.txt): registered checks P1–P4 in `plumbing.py`;
- [`followup_long.txt`](../../results/cst_score_plumbing/followup_long.txt): a follow-up written after the run.

## Result: `PLUMBING FAIL` as written. The readout works; the failing check was badly specified, and it found a real effect

| Check | Result |
|---|---|
| P4 `" A"` and `" B"` are single tokens (362, 425) | pass |
| P2 the same prompt gives a bit-identical log-odds | pass (29.52101707458496 twice) |
| P3 the log-odds at the model's own `DECISION:` matches the letter it wrote | pass, 3 of 3. **But those replies were 11 characters, with no reasoning.** The follow-up forced two sentences of reasoning (74–154 characters): 6 of 6 consistent |
| P1 the sign of the log-odds is right on all 12 toy prompts, and flips when the A/B mapping is swapped | **fail**: 11 of 12; flips on 5 of 6 |

**Why P1 failed.** P1 mixed up "the readout is right" with "the model is right". The readout was right. The
*model* was wrong on one item under one mapping. For "Is 100 less than 10?", with A meaning yes it correctly
answered B, meaning no. With B meaning yes it answered B again: a log-odds of −14.6, and −14.1 in the follow-up
with reasoning. So the answer-code mapping changed the model's answer on 1 of 6 easy questions. **That is direct
evidence that the A/B mapping has to be balanced and recorded in any CST pilot.**

## Two consequences for the estimand

1. **The scores are saturated.** The log-odds ran from 11 to 30 nats in absolute size, and P(A)+P(B) was 1.000 every
   time. AUC is computable, since it only uses the ordering, but probabilities from these scores are not calibrated
   confidences. The ordering among near-certain answers may be noise, not graded evidence, so report the AUC
   together with how many scores fall near zero.
2. **Long format works mechanically.** The score is read after the model's own text, so in the long format it is a
   post-treatment output measure, as noted on #150.
