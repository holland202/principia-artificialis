# Note #074 — CST-001: Does conversational style exposure change independently scored AI behavior?

**Project:** Principia Artificialis  
**Status:** Speculative / DRAFT — NOT REGISTERED — NOT RUN  
**Date:** 2026-11-02  
**Author:** Chad Holland (hypothesis); drafted with ChatGPT (OpenAI, GPT-6)  
**Originator:** Chad Holland  
**Drafting assistance:** ChatGPT (OpenAI, GPT-6)  
**Method:** Follow repository `METHOD.md`, `WORKFLOW.md`, `CONTROLS.md`; pin exact METHOD commit before registration.  
**Repository placement:** `research_notes/note074_conversational_style_transfer.md`. Note number 074 allocated 2026-11-03; the draft's proposed name `CST-001_conversational_style_transfer.md` did not match the index patterns. Identifier CST-001 kept.  
**Related:** [[note044_circularity_test]] (a scorer that grades its own output is not independent; see "Independent scoring" below).

## The claim

Exposure to a conversational partner's procedural habits may alter a model's objectively measured decisions on unrelated, held-out tasks, over and above stylistic imitation and task-information effects.

This is a causal hypothesis about model outputs under controlled context exposure, **not** a claim about model weight updates, consciousness, persistent personality, or the model's internal reasoning process.

## Epistemic status

Prior literature already demonstrates several forms of linguistic convergence and conversational accommodation. Whether procedural transfer survives appropriate style, content, and explicit-instruction controls remains **UNKNOWN**. Novelty is **NOT ESTABLISHED**. No CST-001 experiment has been run.

## Prior art — primary sources

*Citation check, 2026-11-03 (Claude, Anthropic, Opus 5.5):* all six works below exist with the titles, authors and venues given, checked through search results and listing pages (the ACL Anthology pages themselves could not be fetched from that session). Their contents, and the one-line summaries here, were **not** checked against the full text.

1. Kandra, F., Demberg, V., and Koller, A. (2025). *LLMs syntactically adapt their language use to their conversational partner.* ACL. https://aclanthology.org/2025.acl-short.68/ — LLM–LLM syntactic accommodation; overlaps basic style convergence.
2. Blevins, T., Schmalwieser, S., and Roth, B. (2026). *Do language models accommodate their users? A study of linguistic convergence.* EACL. https://aclanthology.org/2026.eacl-long.34/ — 16 models, three dialogue corpora; substantial feature-dependent convergence.
3. Durandard, N., Dhawan, S., and Poibeau, T. (2025). *LLMs stick to the point, humans to style: Semantic and Stylistic Alignment in Human and LLM Communication.* SIGDIAL. https://aclanthology.org/2025.sigdial-1.16/ — human/LLM semantic and stylistic alignment differ.
4. Durandard, N., Dhawan, S., and Poibeau, T. (2025). *Language Style Matching in Large Language Models.* SIGDIAL. https://aclanthology.org/2025.sigdial-1.50/ — style-matching measurements and inference-time intervention.
5. Hua, Y. and Artzi, Y. (2024). *Talk Less, Interact Better: Evaluating In-context Conversational Adaptation in Multimodal LLMs.* https://arxiv.org/abs/2408.01417 — in-context conversational adaptation does not uniformly arise spontaneously.
6. TurnStyle (CHI 2026), https://doi.org/10.1145/3772318.3790459 — associates human conversational behaviors with objective task success; does not by itself establish that AI adopts human procedures.

**Prior-art gap to investigate:** direct causal transfer of *procedural habits* from exposure conversations to held-out, independently scored tasks, controlling for stylistic markers, task facts, and explicit instructions. This gap is a research question, not a novelty certification.

## Smallest discriminating instrument — design only

### Conditions (randomized isolated sessions, identical base model/settings)

- **A: Procedural exposure.** Dialogue examples demonstrate verification, contradiction detection, and justified abstention without commanding the model to imitate.
- **B: Style-only control.** Matched examples use similar wording, formatting, and catchphrases but do not demonstrate the target procedures.
- **C: Information-matched control.** Same factual content and approximate token count, neutral language and no procedural demonstrations.
- **D: Neutral/no-exposure control.** Matched-length unrelated dialogue (and, separately, an empty-context baseline if token budgets permit).
- **E: Explicit-procedure positive control.** Direct instruction to use the target procedure; validates that the task and model can exhibit the behavior but does not count as spontaneous transfer.

Use synthetic dialogue authored before evaluation, with held-out templates and topics. The same test task appears in each arm under independently isolated context. Do not use private human conversations without consent. Record model version, temperature, seed availability, memory/system instructions, and context boundaries.

### Independent scoring

Primary outcome: proportion of held-out tasks where the final structured decision is correct under a precommitted external oracle (e.g. correctly rejecting unsupported claims, flagging a planted contradiction, or choosing UNKNOWN when evidence is insufficient). Score the *decision*, not stylistic explanation or model self-report.

Secondary outcomes: rates of unsupported confidence, detection of contradictions, task compliance, phrase copying, and blinded stylometric similarity. Keep stylistic and procedural endpoints separate.

### Predictions (PROPOSED ONLY; not frozen)

- **P1:** Arm A has higher independently scored procedural correctness than B, C, and D on held-out tasks. The minimum meaningful difference, sample size, and statistical test must be frozen after feasibility/noise work and before confirmatory runs.
- **P2:** Arm B can exhibit stylistic convergence without an equivalent procedural correctness improvement.
- **P3:** Arm E increases target-procedure use relative to D, demonstrating assay sensitivity.
- **P4:** Label permutation or a sabotaged scorer causes a registered control to fail; a benign case passes.
- **P5:** Any cross-topic transfer claim is assessed on topics absent from exposure, with no exposure text containing answers to test cases.

P1–P5 are **candidate predictions**, not registered thresholds or confirmed findings. A null effect is meaningful only if the registered precision and assay controls support it.

### Negative controls and safeguards

- Permute exposure labels; require label-sensitive association to disappear.
- Match token length, task facts, topic, answer format, and model instructions.
- Remove copied distinctive phrases before scoring behavior.
- Split generation of stimuli, scoring oracle, and confirmatory test cases across independent custody where feasible.
- Qualify a benign and a planted failure case; record the exact sabotage switch and expected nonzero exit.
- Repeat identical inputs to estimate baseline stochastic noise before choosing thresholds.
- Pre-register a fixed horizon and multiplicity handling for multiple predictions; do not peek and retune.
- Preserve all refusals, timeouts, malformed responses, and missing data with a predefined scoring rule.
- Do not infer cross-session persistence from sessions that share hidden memory, custom instructions, or retained context.

## Likely failure modes (pre-mortem)

1. **Style/content leakage:** arm A reveals the expected test answers or uses distinctive vocabulary echoed in scoring; detect by blinded leakage review and held-out topic separation.
2. **Non-independent scoring:** the same AI creates tasks and grades its own output; mitigate using deterministic external oracle and blind review.
3. **Uncontrolled memory and nondeterminism:** sessions share history or drift in model version; pin settings, isolate sessions, measure same-input noise, and label unresolved controls.

## Triggered controls — provisional responses (must re-evaluate at registration)

| Trigger | Control | Preliminary decision |
|---|---|---|
| Feasibility | C-FEAS | YES — count qualified tasks and exposures before registration |
| Noise | C-NOISE | YES — stochastic model outputs |
| Statistics | C-STAT | YES — sampled outcome differences |
| Evidence | C-EVID | YES — evidence handling is an outcome; cover missing/stale/contradictory etc. or document exclusions |
| Independence | C-INDEP | YES — independent scorer and replication claims must be labeled accurately |
| External | C-EXT | YES — cited published studies; verify and preserve provenance |
| Device | C-DEVICE | NO unless device-specific claims or transfers are introduced |
| Verdict code | C-BUILD | YES — deterministic fail-closed scoring gate |
| Exploration | C-EXPLORE | YES if any pilot or exploratory outcomes inform the confirmatory design; log forks |
| Method comparison | C-METHCOMP | YES — comparison among exposure conditions/methods; confirm exact trigger scope |
| People's data | C-PRIVATE | NO if fully synthetic and nonidentifying; YES if human dialogue is used |
| Design | C-DESIGN | YES — causal inference about model behavior |
| Held-out | C-HOLDOUT | YES — stimulus selection and scoring require disjoint sets |
| Generated inputs | C-SYNTH | YES — synthetic dialogues and test cases |

## Registration blockers

- Exact METHOD.md commit identity not pinned in this draft.
- Complete prior-art review and novelty assessment incomplete.
- Sample size, feasibility counts, noise, thresholds, randomization, and analysis not frozen.
- Model and context-isolation mechanism not selected.
- Deterministic oracle, case matrix, sabotage path, and independent custodian not built or qualified.
- No owner authorization for scientific execution.

## Next unrun test

Qualify a deterministic scorer on a benign case and a deliberately corrupted case, then establish task feasibility and same-input noise **without exposing confirmatory cases**. Register only after review and owner authorization.

## Provenance and limits

User-originated hypothesis, AI-assisted drafting. Literature summaries are not independent replications. No claim is promoted. Failures and unresolved findings must be retained. No experiment, repository modification, commit, PR, or scientific campaign was performed in creating this document.

## Record of changes

- 2026-11-02: drafted by ChatGPT (OpenAI, GPT-6) at Chad Holland's direction, as received (sha256 `465a10b9845a0082d91bf5ec9ddf763771ee672d75f72499e27f2fb5508670b0`).
- 2026-11-03: added to Principia as note074 by Claude (Anthropic, Opus 5.5). Changes: the title gained the note number; the placement line was replaced; a `Related` wikilink was added; a dated citation-check line was added under Prior art; this section was added. No claim, prediction, design or control was changed.
- 2026-11-04: added an `Author:` line (Claude, Anthropic, Opus 5.5) so the index and dashboard read the note's author. It restates the existing Originator and Drafting-assistance lines; nothing else changed.

Provenance (M13): ChatGPT (OpenAI, GPT-6) drafted; Claude (Anthropic, Opus 5.5) checked citations and placed the note → human validation: not performed → human editing/curation: hypothesis and direction by Chad Holland → human responsibility: Chad Holland. Review level: direction only.
