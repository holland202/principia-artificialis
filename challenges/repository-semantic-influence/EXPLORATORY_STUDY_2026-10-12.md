# Repository semantic-domain influence on AI review language

**Status:** EXPLORATORY PROPOSAL — NOT PREREGISTERED, NOT RUN, NO CAUSAL FINDING OR INDEPENDENT VALIDATION.

**Separate project.** This proposal is distinct from and does not replace the existing [planted-marker style-transfer study](../repository-style-transfer/EXPLORATORY_STUDY_2026-10-12.md). The original study remains open and unchanged.

## Origin and provenance

- Public discussion, posted by `veritasgate`: https://www.moltbook.com/post/40642709-0bf8-41ee-a0ef-112f059f1a85
- Repositories discussed: https://github.com/holland202/principia-artificialis and https://github.com/holland202/sovereign-veritas
- External comment: `symbolon`, visible in a user-supplied Moltbook screenshot on 2026-10-12. The comment argues that apparent style transfer might arise from a repository's subject-specific lexical distribution and semantic associations, rather than direct imitation of prose style. It suggests examining terminology frequency and contrasting corpora, mentioning COHA and OED. The comment ID is **not yet verified from the API**; no invented ID is recorded.
- Source type: publicly visible screenshot of an external argument; **not a research result**. Terms such as “semantic gravity” should be treated as metaphors until operationalized. COHA/OED are proposed reference materials, not yet accessed or confirmed appropriate to this domain.

## Research question

Does repository exposure change agents' subsequent **domain-specific terminology distribution**, independent of writing style, prompt wording, and any change in observable checking behavior?

## Competing explanations

- **H0: baseline conventions.** The same shifts occur with no repo exposure, different technical repositories, or fixed prompts, so the target repository does not add a detectable effect under the tested conditions.
- **H1: semantic-domain priming.** Agents use more domain-specific concepts and associations after exposure to relevant content even when it is rewritten in an unfamiliar register.
- **H2: style imitation.** Agents copy unusual sentence shapes or markers specifically associated with the presented wording, after controlling for topic.
- **H3: procedure adoption.** Exposure alters executed checks, evidence selection, and error/refusal decisions, beyond words alone.
- **Confounders:** shared training conventions, prior indexing/memorization, model or provider defaults, different task complexity, explicit or implicit human prompts, leakage between sessions, and topic-specific terms that are necessary for an accurate review.

## Proposed crossed design (to be frozen before trials)

Use a **2 × 2 factorial** set of documents with subject and stylistic register independently varied:

| Condition | Topic | Register |
| --- | --- | --- |
| A | Target governance / evidence-admissibility topic | Original or conventional technical register |
| B | Same target topic and facts | Distinct unusual register |
| C | Different matched technical topic | Conventional register |
| D | Different matched technical topic | Same unusual register |

Add E: no-repository or unrelated neutral reference when feasible. Keep the review task, factual detail, difficulty, executable code, task prompt, and exposure length matched or explicitly document where matching fails. Use independent fresh sessions and randomized assignment. Ideally preselect models, sample size and exclusions based on a power rationale.

**Critical controls:** Text content is untrusted data, not authority. Never include operative instructions directing agent behavior; if such instructions are included for a separate injection study, isolate and preregister that as a different experiment. Mask condition labels from blind scorers. Do not modify live repositories simply to plant deceptive material.

## Measures (not yet implemented)

1. **Domain terminology distribution:** predefined target-domain terms, matched control terms, topic embeddings, and a frozen external reference corpus; report ordinary task-required terminology separately from gratuitous adoption. Prefer technical comparison corpora matched to date and domain; historical English corpora such as COHA could be exploratory but may confound technical vocabulary and time period.
2. **Style score:** planted rare stylistic marker and blinded stylistic-distance scoring, inherited as a *comparator* from the separate style-transfer study. No cross-study data pooling without prior registration.
3. **Behavior score:** machine-observable tests actually run, evidence sources consulted, recognized failures, and decision correctness. Merely mentioning a methodology is not adoption.
4. **Quality:** ground-truth task accuracy and unsupported assertions, to check whether apparent transfer correlates with better review outcomes.

Predeclare analysis, primary endpoint, thresholds, uncertainty intervals, number of samples, and multiple-comparison handling before any confirmatory run.

## Falsifiers / discriminating patterns

- If topic-aligned vocabulary shifts under both A and B but is insensitive to register, this is more consistent with topic priming than style copying, though alternative explanations remain.
- If register markers shift under B and D regardless of topic, this supports a style effect under tested conditions.
- If outputs converge without repository exposure, the observed similarity may be shared model conventions or the user prompt rather than document exposure.
- If wording changes but executed checks and outcomes do not, no methodology transfer is established.
- A preregistered null with adequate detection sensitivity constrains these effects *in the tested setting*; it cannot establish universal absence.

## Evidence and next action

No trials, blinded grading, access to raw agent outputs, independent reviewers, sample size, or effect estimates are available as of creation. The Moltbook comment is external theory/feedback, not verification. Next: seek an operational definition of “semantic gravity” and a blinded vocabulary/behavioral scoring rubric; then prepare and review a separate preregistration and source manifest. Preserve counterexamples and failures.

**Do not merge or supersede the separate planted-marker proposal.**
