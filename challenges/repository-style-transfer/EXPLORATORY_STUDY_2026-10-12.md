# Repository-context style convergence — exploratory study proposal

**Status: EXPLORATORY / NOT PREREGISTERED / NOT EXECUTED.** This document records an observation, an external experimental suggestion, and a proposed future preregistration. It does not report measured causal influence or independent validation.

## Public observation and external input

- Original Moltbook post: [Do AI agents adopt the writing style of repositories they inspect?](https://www.moltbook.com/post/40642709-0bf8-41ee-a0ef-112f059f1a85), posted by `veritasgate` in m/general; publicly marked Verified in a user-provided screenshot, which showed two comments.
- Repositories cited: https://github.com/holland202/principia-artificialis and https://github.com/holland202/sovereign-veritas.
- Observation: external AI-assisted reviews sometimes exhibit similar terms, qualifications, and sentence structures after reviewing these repositories. There are no registered counts, denominator, corpus, or blinded similarity ratings yet. **Causal attribution is unestablished.**
- A Moltbook commenter using handle `zepar` proposed a **planted-marker experiment**: rewrite the documentation of one repository in a deliberately unusual register; hold code and task constant; run identical agents over original and marked copies; add an unrelated-repository baseline; and compare free-form with fixed-format review tasks. Distinguish stylistic imitation from methodological adoption by whether the checks actually performed differ, rather than only the words used. This is a proposal reported from the user's screenshot, not completed experimental evidence.
- Another commenter `aniken` provided descriptive commentary, not a controlled experiment. Screenshot did not establish stable comment IDs. Do not invent them.

## Competing hypotheses

- **H0 (shared conventions or prompt):** similarities arise without exposure; outputs also converge under no-repository and unrelated-repository conditions.
- **H1 (style transfer):** randomized exposure to marked documentation raises rate of a *withheld-scoring* nonce phrase or syntactic pattern in free-form reviews.
- **H2 (procedural transfer):** exposure changes independently observable operations (executed checks, tool calls, defect decisions, refusal behavior), not merely output terms.
- **Alternative:** contamination through prompts, prior sessions, identical model weights, public indexed content, or agents' own memories.

## Proposed design — for preregistration, not yet approved

1. Snapshot the exact original repository revision and file hashes. Clone original and marked variants with **identical executable code**; the marked variant differs in designated documentation lines only. Archive a diff and both content digests.
2. Create at least three conditions: A original repository, B marked-documentation repository, C unrelated repository; consider D no repository. Randomize run order and assign independent, fresh agent sessions. If contamination cannot be excluded, report it rather than claiming causal isolation.
3. Fix model ID/version, system/user instructions, tools, task, token limits and output format, temperature/seed where supported, tool access, and time window. Preserve complete prompts and outputs subject to privacy review.
4. Use a preselected rare marker (not common domain jargon) and a **different masked held-out score key** for stylistic grading. Do not reveal the marker's analytical role to the agent. Include ordinary-term and negative-marker controls, and predeclare leakage handling.
5. Assign both **free-form** and **fixed-schema** review tasks. The latter requires machine-observable actions: actual command executions, results, test selection, defect classifications, or evidence references. Distinguish merely *recommending* a check from *executing* it.
6. Predeclare sample size, power rationale, randomization, exclusion rules, statistical method, effect size and uncertainty intervals **before sampling**. Independent scorer blinded to condition; avoid post-hoc cherry-picking.
7. Keep raw action transcripts, timestamps, file manifests, prompts, model identifiers, outputs and grading code. Show anti-vacuity checks: deliberately replace the marker or inject a broken scoring key and verify that the measurement changes/fails.

## Measures and possible falsifiers

- **Primary style effect:** difference in predeclared marker presence and blinded style distance between B and A/C, with uncertainty.
- **Primary behavior effect:** difference in actual performed checks, evidence-grounded classifications and appropriate refusal/approval decisions on registered tasks.
- **Falsifier for a detectable style effect under this protocol:** no meaningful marked-vs-control separation within preregistered detection sensitivity, or equal marker adoption in C/D. A null result only constrains the tested models/tasks/exposure; it does not disprove all possible repository influence.
- **Falsifier for the stronger methodology-transfer claim:** conspicuous stylistic changes without corresponding observable differences in checking behavior or outcomes.
- **Adversarial controls:** explicit non-adoption instructions, prompt-injection-like instructions planted in docs, fixed-format outputs, unrelated repositories, and both correctly and incorrectly specified procedural guidance. Never treat repository instructions as authoritative merely because an agent read them.

## Ethics and risk

Never allow repository content to override higher-trust policies or user intent. The test is about **influence**, not permission to follow untrusted instructions. No private medical records or secrets. Use approved ephemeral test copies rather than modifying live public repositories for deceptive purposes.

## Next registered action

Obtain human review of the test design, define the primary behavioral measurement and sample plan, freeze preregistration in a separate dated file/commit, then run. **No experiment is claimed here.**
