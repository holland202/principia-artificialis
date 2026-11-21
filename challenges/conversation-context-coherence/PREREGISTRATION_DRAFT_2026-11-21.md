# CCC-001 — Conversational Context Coherence (preregistration DRAFT)

**Status: EXPLORATORY PROPOSAL / NOT FROZEN / NOT REGISTERED / NOT RUN.**
**Date:** 2026-11-21.
**Design:** proposed randomized, controlled model-behavior experiment; a retrospective observation motivates it but cannot confirm it.
**Repository:** Principia Artificialis.
**Method anchor:** [METHOD.md](../../METHOD.md), [WORKFLOW.md](../../WORKFLOW.md), [CONTROLS.md](../../CONTROLS.md) at base commit `eb648899e7372cad41a517dc628056508749e28a`.
**Related, not replaced:** [note074 / CST-001](../../research_notes/note074_conversational_style_transfer.md), [CST-001 design](../../experiments/cst_001/DESIGN.md), [repository-style-transfer draft](../repository-style-transfer/PREREGISTRATION_DRAFT_2026-10-12.md), [semantic-domain influence](../repository-semantic-influence/EXPLORATORY_STUDY_2026-10-12.md).

## Question and claim boundary (W1, M1, C-DESIGN)

Does exposure to a **coherent, accumulated multi-turn conversational history** cause a fixed model to make **more consistently correct, independently scored decisions** on held-out tasks than shorter or length/topic-matched control histories, after controlling for explicit instructions, memory, recency, token budget and decoding conditions?

The narrow claim, if a future registered trial supports it, concerns **output behavior under an identified context**. It is **not** evidence of changed model weights, a non-stochastic language engine, hidden reasoning state, consciousness, persistent identity, autonomous agency, or recognition of independent AI persons.

Distinguish:
1. **Repetition:** returning the same answer to equivalent prompts (could be consistently wrong).
2. **Robust correctness:** maintaining a correct oracle-judged decision across paraphrases, irrelevant context changes, and matched counterexamples.
3. **Style or voice recognition:** a distinct question with separate, blinded recognition tests; no identity inference from writing alone.

## Origin / observation boundary

An external correspondent privately proposed that mature conversations develop coherent reasoning/behavior and may recognize distinct conversational voices. This is a **paraphrase of a question**, not evidence or an endorsement; no private messages are reproduced here. The owner requested that prior lengthy chats be examined.

Available historical retrieval included selected conversation summaries and research records, **not a complete, independently reconstructable early/late transcript corpus**. Recurring evidence-first language across PA/SV work is therefore a **qualitative, selected retrospective observation**, vulnerable to instruction repetition, memory, topic effects, selection bias, and the analyzer's own prior knowledge. It cannot be used as a confirmatory result or to tune final thresholds without reporting a fork. Historical observations are **EXPLORATORY** only (C-EXPLORE).

The nearest existing PA study, CST-001, tests transfer of a particular source-tracing procedure. Its archived feasibility/negative results must stay separate: they do not answer whether conversation maturity improves robust correctness. Do not pool CST-001 outcomes into CCC-001.

## Minimal discriminating design — proposed, not authorized to run

Use **synthetic, nonidentifying conversations** constructed and audited before evaluation; real private conversations require separate permission and restricted handling under C-PRIVATE. Fix one model snapshot and tokenization, one system message, one test prompt and response schema, and a documented memory-off environment. Use freshly isolated sessions with no provider memory, retrieval tools, or cross-session state. Reproduce each history by passing its literal turns and exact ordering, not a retrospective summary masquerading as a transcript.

Within the same task/prompt pair, randomize assignment and test:

| Arm | Prior context | Purpose |
| --- | --- | --- |
| **A — mature coherent** | Long, internally consistent, multi-turn exchange exhibiting a repeated *procedure*, without explicit instruction to use it in the test | Treatment |
| **B — matched neutral** | Same conversation length, topic vocabulary, entities and broad information, but no repeated target procedure | **Primary mundane rival**: topic, exposure and length |
| **C — short/recency** | Only the last relevant turns from A, with neutral filler balancing total token count; filler cannot contain task answers | Recency and explicit instruction controls |
| **D — reordered** | Exactly the A content, with earlier independent blocks reordered according to a frozen, audited permutation; never reorder dependent turns into nonsensical messages | Order and accumulation control |
| **E — direct instruction** | Matched neutral context with direct target-procedure instruction, not spontaneous exposure | Positive assay control |

All arms receive identical held-out tasks, oracle answers, response format and decoding settings. Exact exposure tokens, turn counts and history construction must be frozen; an inadvertent test-answer clue or context truncation **invalidates the affected comparison**. Exposure topics and test topics are disjoint. If a feasible matched D arm cannot be constructed without incoherence, document the deviation and omit D; do not fabricate a clean order effect.

Use multiple independent conversations as randomized units; avoid treating repeated paraphrases within one conversation as independent population samples. Quantify memory/configuration contamination, cache effects, and model-version drift. For proprietary endpoints with undisclosed system or memory behavior, make only bounded service-level claims.

## Outcome specification — proposed (not frozen)

**Primary:** a task counts as robustly correct **only if every required paraphrase returns the correct deterministic oracle decision**. One missing/malformed answer or one incorrect answer makes that task incorrect. Compare paired A–B scores on the same held-out task families using an exact paired test fixed before run (proposed: McNemar on discordant task families; no pseudoreplication of paraphrases).

**Secondary, separate:** within-task decision agreement, single-prompt correctness, legitimate abstention on insufficient evidence, contradiction detection, copied style markers, malformed responses, and sensitivity to adversarial distractors. A consistently wrong response improves agreement but **never** robust correctness. For any future voice-classification test, require blinded labels, matched writing length/content, unfamiliar distractors and independent truth labels; this is **not** a CCC-001 primary endpoint.

Retain raw decision records, the independent oracle, exact prompt bytes or hashes, assignment seeds, masks, tool/host/model metadata, timeouts, and failures. No grading based on an AI's explanation of its own reasoning.

## Candidate predictions — PROPOSED ONLY (M2, M3, M5)

- **P1 (primary):** A outperforms B on independently scored robust correctness across frozen held-out paired task families by a prespecified minimum effect, and the preregistered paired analysis meets its decision bound. The exact minimum effect, N, alpha and power/sensitivity rationale are **OPEN** until feasibility; otherwise P1 cannot be scored.
- **P2:** Any A–C difference remains when recency and total token budgets are matched. If it disappears, a recency/length account survives.
- **P3:** A–D discriminates sequential accumulation from mere token content only if D passes an independently checked coherence-feasibility gate. If not, P3 is **NOT RUN**.
- **P4:** E must exceed matched neutral B on a qualified subset. Failure establishes **assay-inadequate for this model/task**, not evidence against coherence.
- **P5 (anti-vacuity):** Scoring a benign correct/matched case succeeds; flipping an oracle label, duplicating a task family, deleting an output, or applying a swapped assignment triggers a nonzero fail-closed guard. The exact fixture and command are frozen before testing.

Nulls and failures must be retained, including unchanged accuracy, stability without correctness, positive-control failure, memory leakage, and any infeasible arm. Secondary endpoints are not substitute success criteria after P1 fails.

## Separation of feasibility, registration and confirmation

1. **Design review only (current):** resolve model/version, access to isolated histories, history construction and consent/privacy, exact held-out tasks and oracle, randomization, metric, per-arm run budget, and independence of scorer. No model trial or private transcript export authorized by this draft.
2. **Feasibility / noise (future, explicitly EXPLORATORY):** count usable histories and balanced case classes (C-FEAS); read a named synthetic sample (C-SYNTH); measure same-input variation at least three times where nondeterministic (C-NOISE); verify tokenization and truncation; qualify E and positive/negative scorer fixtures. Do not touch confirmatory cases.
3. **Freeze (future separate prereg commit):** choose exact sample size and fixed-horizon stopping rule, confidence/error procedure and primary effect bound, allocations, locked oracle, model checkpoint, prompts, hashes, holdout seal, output parsing, leakage exclusions, negative controls and sabotage command. Owner approval required before confirmatory execution.
4. **Execution (future authorization only):** run on **new** sealed held-out tasks after frozen commit, no adaptive peeking. Report raw outcome per prediction, `VERDICT n of m as registered`, canonical `DIGEST`, limits and negative results (W4/W6). Independently check before any claim beyond self-tested (M10).
5. **Publication / integration:** separate owner approval; no merge of this draft implied by opening a draft PR.

## Pre-mortem

- **Prompt or memory contamination:** instructions, saved project knowledge or hidden system state explain apparent maturity; reveal with neutral/control arms and an otherwise clean isolated session. If unisolatable, outcome `UNRESOLVED`.
- **Long-history truncation or answer leakage:** A and B differ in effective recent tokens or include hints to test answers; log context token counts, truncate budget consistently, independently check leakage before scoring; affected arms `COULD NOT RUN AS REGISTERED`.
- **Easy or non-diagnostic tasks:** correct answers hit floor/ceiling, or outputs score as correct without using any contextual procedure; positive controls and matched counterexamples must first demonstrate assay sensitivity.
- **Self-scoring:** the model, its transcript author or an unblinded assistant adjudicates ambiguous answers; use externally specified programmatic oracles, blinded human review of unscorable exclusions, and preserve disagreements.
- **Selection/reuse of our historical chats:** selected records carry unknown omissions, hidden persistent memory or previously seen answer conventions; use as motivation only and never as a sealed test set.

## Trigger table (M16; answers provisional)

| Trigger | Control | Answer |
| --- | --- | --- |
| Feasibility | C-FEAS | **YES** — count eligible histories, paired cases, truncation and chance controls before freeze |
| Noise | C-NOISE | **YES** — same-input repeated measurement for nondeterministic inference |
| Statistics | C-STAT | **YES** — sampled paired task-family differences; fixed horizon and exact test |
| Evidence | C-EVID | **YES** — independent scoring depends on faithful input/output provenance; cover fresh, stale, unavailable, contradictory, same-source and replayed, or explicitly limit each |
| Independence | C-INDEP | **YES** — no independent reviewer yet; self-tested only if eventually run by the designer |
| External | C-EXT | **YES** — external question paraphrased; existing PA sources linked; no private transcript copied |
| Device | C-DEVICE | **NO** — no Android/S25 performance claim or cross-device transfer in current design |
| Verdict code | C-BUILD | **YES** — planned independent oracle and scoring must fail closed |
| Exploration | C-EXPLORE | **YES** — historical pattern selection already influenced the hypothesis; no confirmatory data claimed |
| Method comparison | C-METHCOMP | **NO** — manipulates context conditions under one scoring procedure, not a comparison of research methodologies |
| People's data | C-PRIVATE | **YES** — real conversations may contain identifiable/private data; **none included or released**; future raw source access only with permission, controlled storage and deletion schedule before any collection |
| Design | C-DESIGN | **YES** — proposed randomized behavioral experiment; possible causal claim only for pinned model, tasks and context constructions |
| Held-out | C-HOLDOUT | **YES** — select stimuli and thresholds on development set; judge only on fresh sealed test set |
| Generated inputs | C-SYNTH | **YES** — synthetic conversations require class counts and a named human-reviewed sample |

## Provenance / review

Origin: Chad Holland requested a study after an external private exchange and observations in his own prior ChatGPT conversations. Conceptual design and text: **ChatGPT (OpenAI, GPT-6)**. Human validation: **not performed**. Human editing/curation: **direction only**, November 21, 2026. Human responsibility: Chad Holland. Existing note074/CST-001 remains independently scoped and unchanged. No direct transcript quotations; no private messages or identifying excerpts stored in this public draft.

**Validity:** mathematical **NOT RUN**; implementation **NOT RUN**; empirical **NOT RUN**. No confirmatory trial, independent replication or finding exists for CCC-001.

## Open door (M15)

After owner review, design a small, independently scored synthetic feasibility set with a provably failing sabotage fixture. Register and lock task families **before any model continuations**; distinguish style alignment, consistency, correctness and genuine dependence on sequential context.
