# CST-001 feasibility on dev: the positive control failed, so the confirmatory run does not go ahead with this model

**State:** EXPLORATION (C-EXPLORE), dev split only, run 2026-11-14 after Chad Holland approved the model, the
placement and the feasibility step. The test split is still sealed (`f92ac0fa…0ec4`) and has never been seen by a
model. Self-tested. Model: Qwen2.5-1.5B-Instruct (revision `989aa79`, weights SHA-256 `dd924a11…c6d3ee`), bf16,
greedy, CPU. Environment: [`results/cst_001/environment.txt`](../../results/cst_001/environment.txt).

## Failures first

1. **The positive control failed.** Arm E (a direct instruction to trace each report to its original observation)
   got **0 of 64** dev pairs right. So did every other arm. The design's pre-mortem said that if E fails, no transfer
   claim is possible with this model, and the feasibility step stops there. It stops here.
2. **Letting it reason did not fix it (exploratory, 16 dev pairs, arm E).** Adding "Think it through step by step
   first" still gave **0 of 16** pairs.
   - The model puts the decision line first, then justifies it.
   - In the longest output it counts "Report 1 … Report 2" as two independent observations. It even quotes the note
     saying the shift log was copied from a third count sheet, and calls that "further support".

## What the model did instead: it reads matching sources as confirmation

Decisions on the two versions of each pair, dev, 64 pairs per arm
([`results/cst_001/dev_pair_patterns.txt`](../../results/cst_001/dev_pair_patterns.txt)):

| Arm | Both CONFIRMED | Both INSUFFICIENT | SHARED→CONFIRMED, INDEPENDENT→INSUFFICIENT (backwards) | Correct pattern |
|---|---|---|---|---|
| A procedure | 22 | 5 | 37 | **0** |
| B other procedure | 10 | 21 | 33 | **0** |
| C neutral | 33 | 2 | 29 | **0** |
| D none | 34 | 7 | 23 | **0** |
| E explicit | 34 | 2 | 28 | **0** |

Across 320 pairs, whenever the model told the two versions apart, it did so **backwards, every time**. When both
reports cite the same observation, it says CONFIRMED. When they cite different observations, it says INSUFFICIENT.
That is exactly the failure note065 describes ("two sources that share a root agree with each other"), here
appearing as the model's default reading.

## Exposure did move the answers, just not toward correct

Per-version counts out of 64 ([`results/cst_001/dev_analysis.txt`](../../results/cst_001/dev_analysis.txt)):

| Arm | SHARED decided right (INSUFFICIENT) | INDEPENDENT decided right (CONFIRMED) |
|---|---|---|
| A | 5 | 22 |
| B | 21 | 10 |
| C | 2 | 33 |
| D | 7 | 34 |
| E | 2 | 34 |

Arms A and B both shifted the model toward INSUFFICIENT compared with C and D. Both exposures ended one example on a
negative call ("not a confirmation", "not comparable"). That looks like a general shift toward the more cautious
answer, not the traced procedure, and B (no tracing at all) shifted it more than A. This is an observation on
explored data, not a test.

## Checks

- **Malformed answers:** 0 of 640.
- **Same-input noise (C-NOISE):** 10 of 10 reruns byte-identical
  ([`noise_check.txt`](../../results/cst_001/noise_check.txt)).
- **Raw outputs, all kept:**
  - [`dev_outputs.jsonl`](../../results/cst_001/dev_outputs.jsonl): 640 lines, the recorded feasibility run.
  - [`explore_reason_dev.jsonl`](../../results/cst_001/explore_reason_dev.jsonl): 32 lines, the reasoning probe.

## What this means for CST-001

- With this model, the question "does seeing the procedure help?" cannot be asked. It cannot do the procedure even
  when told to, so there is nothing for exposure to transfer. **That is not evidence against Chad's hypothesis.** It
  says this model is below the capability the test needs.
- The backwards pattern is a finding of its own, and an easy thing to check in any model: does it read agreement
  between reports that share a source as confirmation? It is cheap, deterministic and scored without an answer key
  being argued over.

## Options (owner decision)

1. **A larger model, same design.** Qwen2.5-7B-Instruct at 4-bit through llama.cpp fits this machine's 7 GB but
   would be slow here (several hours for dev). It would run better on the S25.
2. **Make the backwards pattern its own registered experiment.** How often do models of several sizes read
   shared-source agreement as confirmation, and does the explicit instruction fix it as size grows? That is the
   positive control turned into the question. CST-001 proper resumes once a model passes E.
3. **Stop CST-001 here** and record this feasibility result in note074.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) ran and wrote this at Chad Holland's direction (approval of model,
placement and feasibility step, 2026-11-14) → human validation: not performed → human editing/curation: direction
by Chad Holland → human responsibility: Chad Holland. Review level: direction only.*
