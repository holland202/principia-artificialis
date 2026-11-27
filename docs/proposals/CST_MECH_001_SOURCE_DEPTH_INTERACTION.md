# CST-MECH-001 — Source-lineage depth × instruction: a candidate empirical interaction

**Status: PROPOSAL / NOT REGISTERED / NOT RUN. Novelty NOT ESTABLISHED.**
**Date:** 2026-11-15.
**Owner and research direction:** Chad Holland. **Study-plan draft:** ChatGPT (OpenAI, GPT-6).
**Related:** [note074](../../research_notes/note074_conversational_style_transfer.md), [CST-001 design](../../experiments/cst_001/DESIGN.md), [CST-001 dev2](../../experiments/cst_001/AMENDMENT_HOP2.md), [coordination issue #150](https://github.com/holland202/principia-artificialis/issues/150).
**Method:** METHOD.md / WORKFLOW.md / CONTROLS.md at the exact commit to be pinned by the eventual registration. This proposal does not modify that method.

## One sentence that could be wrong

When a model is asked to verify whether *independent original observations*, rather than the number of agreeing reports, corroborate a claim, a source-specific tracing instruction changes **paired decision accuracy in opposite directions** for direct-source (one-hop) and indirect-source (two-hop) cases, compared with a neutral instruction, on fresh cases.

This is an **observable output effect**, not a claim that extra tokens constitute internal reasoning, that models learn a persistent skill, or that instruction generally harms easy problems.

## Why this deserves a test, not a discovery announcement

The exploratory, previously viewed Qwen2.5-7B-Instruct Q4_K_M development records report:

| Previous dev, 32 pairs per hop | Baseline D | Specific instruction E | E−D |
|---|---:|---:|---:|
| Hop 1 | 26/32 | 14/32 | −12/32 |
| Hop 2 | 0/32 | 12/32 | +12/32 |

The hop-dependent *difference of differences* is 24/32 in these **exploratory** data. On a second development split, hop-2 E scored 10/32 and no-exposure D scored 0/32; source-demonstration A scored 0/32. An independent **archive replay** checked these numbers, but no fresh non-author model run occurred. The existing original CST-001 128-pair test split has **not** been run and must remain sealed.

**Selection bias:** these unusual observations were noticed before this proposal. They cannot be used to confirm this new prediction. No p-value computed on them is confirmatory.

**Potential confounds:** changing the instruction also changes wording, model outputs, and response length. In the dev2 E arm, every correct matched pair had at least one completion longer than 20 tokens, but 13 such longer-response pairs were still incorrect. A token threshold is an association, not a measure or manipulation of internal reasoning.

**Novelty screen — prior art exists for broader claims.** Do not claim that reasoning harming accuracy or in-context skill transfer is new. Relevant primary sources reviewed at abstract level on 2026-11-15:
- Liu et al., *Mind Your Step (by Step)*, ICML 2025 — reasoning prompts can hurt particular tasks: https://proceedings.mlr.press/v267/liu25t.html
- Li et al., *When Thinking Fails*, NeurIPS 2025 — reasoning can impair instruction-following: https://papers.nips.cc/paper_files/paper/2025/hash/706338a08f9378b708f21cbf5686e617-Abstract-Conference.html
- Cloud et al., *Language models transmit behavioural traits through hidden signals in data*, Nature 2026 — fine-tuning transfer differs from tested in-context trait exposure: https://www.nature.com/articles/s41586-026-10319-8
- Li et al., *Language Models Can Easily Learn to Reason from Demonstrations*, EMNLP 2025 — demonstration-based improvement in supervised fine-tuning: https://aclanthology.org/2025.findings-emnlp.866/

These are adjacent, not evidence of novelty. A full claim-by-claim prior-art audit (including provenance/source retention under C-EXT) is a **blocker to any novelty label**. Also examine work directly on source dependence, duplicate evidence, multi-hop tracing, and attribution before publication.

## Proposed fresh design (do not execute before registration)

**Design:** within-model experiment using real Qwen2.5-7B-Instruct model inference, NOT a simulated agent. Freeze model file SHA-256, quantization, runner commit, hardware, decoding settings, context window and all literal prompts. Use temperature 0, top-k 1, maximum 320 output tokens for unconstrained conditions, and one fixed final-line parser. Record any backend deviations. No cloud service or unpublished model needed.

**Unit:** a base scenario block spanning one-hop/two-hop source representation and two otherwise matched versions:
- SHARED: agreeing reports ultimately depend on the same original source → INSUFFICIENT.
- INDEPENDENT: reports depend on distinct original sources → CONFIRMED.

The decision rule is printed in **every** test prompt, as in CST-001. This tests application of a stated rule, not discovering it. Equalize domains, item lengths where feasible, answer placement and AB/BA report order. Distinct root identifiers must differ clearly. The truth oracle counts distinct original-observation IDs, not report count.

**Four core conditions, same model and case content:**

| Condition | Pre-decision instruction | Output affordance |
|---|---|---|
| N-L | Neutral (no additional tracing directive) | Rationale permitted, same decision-line requirement |
| T-L | Explicitly trace every report to original observations | Rationale permitted, same decision-line requirement |
| N-S | Neutral | Final decision only; constrained short output |
| T-S | Explicitly trace every report to original observations | Final decision only; constrained short output |

L and S are separate, prospectively declared **format conditions**, not pure manipulations of internal thought. Test and record whether S can be enforced with the exact decoder; reject any invalid token or missing decision. Keep L the primary endpoint so successful prior longer responses remain possible. A neutral length-matched prefix is required; verify exact prompt tokens after freezing the tokenizer.

**Simple rival:** add *G-L*, a length- and style-matched generic “check the information carefully” directive with no source-tracing procedure. If G-L shows the same depth interaction as T-L, the claimed source-specific explanation is undermined. G-L is a secondary, independently disclosed comparison and must not displace the primary test.

**Sampling proposal:** build a **new** qualification split, development split, and sealed confirmatory split with independent seeds and full prompt-set hashes. Suggested confirmatory size is 64 independent scenario blocks, counterbalanced across 8 domains and 2 report orders, each rendered at both hops and both SHARED/INDEPENDENT versions. Four core conditions require 64 × 2 × 2 × 4 = **1,024 real-model responses**; optional G-L adds 256. No previous CST test prompts are consulted or consumed. Prove zero duplicate prompts across all CST old/new splits and all new internal splits. A fixed horizon with no inspection of outcomes until the archive is closed is required.

**Pilot:** first qualify parser, answer-key generator and context affordances using qualification cases. Measure same-input noise with ≥3 repeated inputs. Use only a *separate* development split for feasibility (including a positive-control check that source-specific instructions can score above floor on two-hop cases) and to decide whether running the confirmatory study is justified. Record every fork under C-EXPLORE. No change to confirmatory prediction after looking at confirmatory output.

## Proposed primary estimator and falsifiers

For block i and hop h, let Y(i,h,c) be 1 iff **both** matched versions have the correct, unambiguous final decision in condition c; otherwise 0. Missing, invalid, duplicate and truncated completions are failures, never silently excluded.

For the long-format conditions, define

- d(i,h) = Y(i,h,T-L) − Y(i,h,N-L)
- q(i) = d(i,2) − d(i,1)
- Δ = mean(q(i)) over the 64 frozen blocks

**Primary candidate P1:** on fresh confirmatory inference, Δ ≥ **0.25** and a one-sided exact sign test of nonzero q(i) favors q > 0 at p ≤ **0.05**. Report the exact positive, negative, tie counts, the precise p-value, Δ and its uncertainty interval. A result lacking **either** criterion is **NOT SUPPORTED**. A block with identical behavior across arms has q=0 and contributes no sign-test evidence. The sign test tests directional asymmetry of paired blocks, not a universal population mean. The effect threshold is an additional practical bound, not a substitute for inference. All values and decision code must be frozen and reviewed *before any new confirmatory outputs*.

**Killer observations:** no difference between T-L and N-L; the same-direction improvement at both depths; an effect of the wrong sign; always-confirmed/always-insufficient outputs (both yield zero paired correctness); or a generic diligence prompt G-L producing the same interaction, weakening the source-specific interpretation.

**Secondary, explicitly non-confirmatory diagnostics:**
- T-L vs N-L within each hop, SHARED and INDEPENDENT accuracy separately, and exact discordance counts.
- Generic diligence G-L vs T-L, and T-S/N-S vs T-L/N-L. Output format may cause changes independently; do **not** infer that observed reasoning text caused an outcome.
- Malformed/truncated rates, completion lengths, answer-order asymmetry, across-domain heterogeneity.
- Additional model family or second runtime only as a newly registered replication, **not** an unplanned rescue if P1 fails.

**Multiplicity:** P1 alone can earn the primary label; all other contrasts are diagnostic and cannot be promoted on this run without new registration and fresh data. State absence of evidence, evidence of absence, and assay failure differently. If pilot positive controls fail or the scorer cannot reject sabotage, do not run the confirmatory study.

## Anti-vacuity, provenance and controls

- **M3/C-BUILD:** build an independent scorer with exhaustive-key checks: missing/duplicate/out-of-scope rows, ambiguous decisions and unknown labels fail closed. Unit tests must include an always-one-label model, inverted gold IDs, swapped paired outputs, a duplicate key and a dropped row. An intentional oracle mutation must cause a nonzero exit. A benign fixture must pass.
- **C-FEAS/C-SYNTH:** print counts without truth leakage before freezing: domain × depth × order × version, unique source IDs, duplicates, prompt token lengths. Human visually reviews a preidentified qualification sample. Do not infer external-world behavior from synthetic evidence scenarios.
- **C-NOISE:** rerun a predeclared small qualification set at least 3 times and report exact agreement; temperature=0 alone is insufficient evidence of determinism.
- **C-STAT:** fixed horizon, all cases and arms predeclared, no optional early stopping based on results. Validate the exact sign-test implementation on known hand-computable fixtures. Report exact p, including ties.
- **C-HOLDOUT/M11:** fresh sealed prompts; preserve CST-001's older sealed test split; record model and prompt file hashes, commit SHA, execution command, environment and every raw response; independent replay of archived scoring **is not** fresh model inference.
- **C-EVID:** this instrument deliberately targets derived/shared-source evidence, with fresh evidence only. Stale, absent, contradictory, replayed or externally verified observations are out of scope, not silently considered tested.
- **C-EXT/M14:** primary-source and simplest-rival checks precede novelty claims. Preserve any external materials brought into the research in the required repository record.
- **C-PRIVATE/C-DEVICE:** synthetic cases only, no personal records; no S25/Termux portability claim without an S25 run.
- **M8/M10/M13:** raw failures remain visible; no model self-certifies an independent result. AI-assisted study design, self-tested inference, archive review and genuinely independent reproduction are labeled separately.

## Smallest next deliverable to Claude and Codex

1. Claude: critique *causal interpretability* and feasibility. In particular, test whether L/S formatting introduces an uncontrolled change in instruction intent. Propose exactly one fixed, non-leaking manifest structure and pilot gate; do not touch the old sealed test split.
2. Codex/ChatGPT: independently inspect the manifest and scorer before inference, check the exact sign-test code and all sabotage fixtures, and independently replay raw archives after a run.
3. Owner: review the fixed registration when its unresolved choices are closed. No automatic merge or confirmatory model run is authorized by this proposal.

**Publication ceiling:** a prospective, independently reproduced depth × instruction interaction on a pinned model and controlled synthetic source-lineage tasks could justify a **narrow model-specific empirical result**. It would **not** demonstrate a novel general intelligence mechanism, in-context learning of a persistent skill, a causal effect of internal reasoning, or external-world security assurance.

---
**Provenance:** Chad Holland requested a genuinely novel, falsifiable empirical result. ChatGPT (OpenAI, GPT-6) drafted this deliberately disconfirmable research proposal using archived CST-001 development observations and official abstracts of adjacent research. No new experimental responses were generated, no test seal was opened, no independent replication was performed, and human scientific review remains pending.
