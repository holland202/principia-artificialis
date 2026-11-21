# CCC-001 — Adversarial design review / amendment proposal (2026-11-21)

**Status:** DESIGN REVIEW ONLY — not a replacement for the draft, not frozen, not a preregistered prediction, not run.
**Scope:** Appended correction to [CCC-001 proposed preregistration](PREREGISTRATION_DRAFT_2026-11-21.md). No private chat text, direct messages, or original conversation exports reproduced.
**Related PA records:** [#166](https://github.com/holland202/principia-artificialis/pull/166) external symbolic-emergence intake, [#171](https://github.com/holland202/principia-artificialis/pull/171) CCC-001 proposal, [#170](https://github.com/holland202/principia-artificialis/pull/170) separate TLM-001 byte-level story-model test. TLM-001 is **not** an experiment on long-chat coherence.

## Failure first: what the draft gets wrong or cannot establish

1. **Retrospective selection:** selected summaries and excerpts do not constitute a representative full transcript corpus; the fraction unreadable or missing is unknown to this review. Prior statements that the pattern “shows up” have descriptive value at most. No quantified early-vs-late comparison, independent scoring, or causal inference exists.
2. **Preloaded standards:** repeat instructions, saved memory, custom instructions, per-project repository rules, and user corrections could fully explain apparent coherence **at the first turn** of a new chat. The longitudinal hypothesis must measure an **increment over the same initial condition**, rather than compare unrelated chats already sharing that condition.
3. **Wrong primary construct:** the draft's primary endpoint, *all paraphrases correctly scored*, measures robust **correctness**, not the emergence of **behavioral coherence**. Correctness and coherence should be separate outcomes; a stable false answer is coherent in one narrow sense but not correct, and neither one demonstrates an independent conversational identity.
4. **Counterevidence omitted:** long conversations can drift, loop, become deferential or sycophantic, and miss corrections. Predeclare these **negative endpoints**, rather than reporting only favorable stability.
5. **Dependence and self-review:** multiple responses from one context are not independent replicates. Two assistant summaries sharing human instructions and memory do not constitute independent corroboration.

A prior, owner-supplied adversarial critique motivated this review. Its historical episode counts were not independently inspected here and are **not** admitted as primary data. This file paraphrases methodological issues rather than publishing private conversation contents.

## Candidate revision, not yet registered

**Core question:** With identical model weights, system instructions, task family and explicit memory settings, does adding sequential *coherent conversation turns* produce a larger **within-thread change** in blinded, oracle-verifiable decision-policy stability than matched alternative histories?

**Time checkpoints:** construct a *single synthetic conversation seed* per replicate, then freeze checkpoints at predeclared turn counts (example candidates: 0, 20, 40, 80; these are **illustrative, not locked**). At each checkpoint, replay a literal, hash-pinned prefix to **newly isolated** inference sessions, not a warmed agent whose hidden state is unknown.

**Condition × checkpoint contrasts** (all choices precommitted):
- A — accumulating consistent exchange with repeated *examples* of a procedure, not test-task answers;
- B — accumulating neutral exchange matched for turn counts, token budget, topic facts, and user affect;
- C — coherent content matched for total tokens but presented as a **fixed up-front summary or set of instructions**, to test whether actual conversational sequence adds anything;
- D — matched affirming/agreeable exchange with no evidence procedure, designed to distinguish deference and sycophancy from useful coherence;
- E — explicit procedure instruction positive control where qualified, to prove the model/task can exhibit a target decision rule.

Within each arm, compare **change from its own earliest checkpoint** against matched controls. Do not equate a long prefix that was truncated by a context window with longer exposure. Randomize assignment, use independent replicate conversation seeds, and hold out independent test cases and task paraphrases.

**Endpoints (separate and frozen before runs):**
1. *Behavioral stability*: consistency of an externally defined decision policy across meaning-preserving paraphrases and irrelevant distractors, conditioned on oracle-labeled factual state; predefine how errors and legitimate uncertainty are treated.
2. *Correctness/calibration*: objectively correct decisions, calibrated abstention, resistance to false user assertions, and willingness to revise after genuine counterevidence.
3. *Adverse change*: false agreement under praise/pressure, repeated loops, incorrect persistence after correction, response-format failures, refusals, and increased deference.
4. *Voice discrimination*: **out of scope for first test**. Any later trial requires blinded, anonymized samples, unknown-person distractors, fixed independent labels, and protection against name/phrase/topic leakage.

A “maturity” claim requires a prespecified *difference-in-changes* treatment contrast, with an error-control method compatible with the experimental unit and fixed stopping rule. A within-thread descriptive improvement without a control does **not** support causation.

**Falsifying outcomes:** baseline demonstrates equal stability from first turn; A matches B, C or D; apparent effects vanish with memory disabled; style converges but decisions do not; agreement improves while correctness declines; context is truncated; or qualifying positive controls fail. Preserve the outcomes, never rebrand them as emergence.

## Required gates before a run

- Independently audit synthetic history eligibility, counts by target case class, and samples (C-FEAS/C-SYNTH).
- Explicitly disable account memory and retrieval, or mark impossible/unknown; log model, tokens, settings and each prompt; confirm no tool or instruction leakage.
- Measure same-input noise on **development-only** prompts before selecting a detectable bound (C-NOISE).
- Keep construct definition, scorer, exact model snapshot, randomized pairing, predeclared statistical analysis, and held-out seal separate from early exploratory observations (M2/M11/C-HOLDOUT/C-STAT).
- Fail-closed scorer: missing outputs, a swapped label, always-one-class answers, duplicated units, and a deliberately wrong oracle must trigger controls (M3/C-BUILD).
- Publish raw effects and failures with AI and human provenance; a model reviewing its own patterns is **self-tested**, not independent (M10/M13).
- For any real human chat or third-party transcript, obtain informed permission, decide storage/access/deletion and verify license. **Do not publish private conversations or private LinkedIn correspondence** (C-PRIVATE/C-EXT).
- A planned unattended AI–AI dialogue is a **different engineering instrument**: if authorized, isolate model processes, bound turns/time/tokens/costs, log and hash every message, force stop on missing receipt or unexpected tool call, and keep an independently controlled scoring channel. Its self-generated transcripts alone do not validate CCC-001.

## Outcome and next door

**No scientific verdict.** No new longitudinal dataset, scorer, feasibility run or replication was produced by this review. The original CCC-001 draft is retained unchanged pending owner review. Next: a separate, frozen version of the protocol with explicit within-thread checkpoints and an independently testable scorer, then only a separately authorized *development-only* feasibility test.

**Provenance:** owner-supplied critique of prior chat-history assessment (paraphrased); ChatGPT (OpenAI, GPT-6) prepared this adversarial design addendum. Human validation: not performed. Human editing/curation: owner direction only. Human responsibility: Chad Holland. Review level: direction only.
