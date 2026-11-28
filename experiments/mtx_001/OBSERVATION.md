# MTX-001: methodological transfer, field observation

**Status:** SPECULATIVE. One observational candidate and an unregistered design sketch. NOT REGISTERED, NOT RUN.
No model was called for this file. **Date:** 2026-11-28.

**Question (not yet testable as stated):** does exposing a model to this repository's method change how it
approaches a later review task, beyond what any good review guidance would do?

## The observation

On 2026-11-28 Federico Talens-Alesson sent Chad Holland a written review of the CCC-001 closeout draft (`a3c4b81`),
PR #172 and PR #180. He wrote that he had shown his model this repository's work as part of building its context.
A follow-up message is signed "DeepSeek V4-Flash". The review applied ideas that this repository also uses: keep
failed verdicts, trace each number to its source, name unresolved confounds, state what result would answer the
question. Its substance is recorded in the CCC-001 closeout addendum (PR #199).

**Permission.** Federico permitted use of the material on 2026-11-28 (private message, shown to Claude by Chad;
CONTRIBUTOR REPORTED). His messages are not quoted or committed here. Only a description is recorded.

## Why this is not evidence of transfer

Each of these explains the observation without any transfer, and none can be ruled out from it:

1. **Direct exposure.** The model was reviewing documents written in this method. Much of what it applied, it was
   reading. Praising a document's own principles is reading well, not adopting them.
2. **Ordinary peer review.** The review's own additions (the hardware limit, the arm-A conditions, defining an
   answer) are what a competent reviewer of any preregistered study might say.
3. **No baseline.** There is no review from the same model without exposure, so there is no contrast.
4. **Uncertain authorship.** The review is in Federico's voice, prepared with the model. Which words are his and which
   the model's is not known. The model name and version are CONTRIBUTOR REPORTED.
5. **Selection.** It was noticed because it looked like the pattern being looked for.
6. **A misreading.** The review joined two different measurements (CCC-001 addendum, point 3). That is evidence of
   ordinary reading under load, not of the method being applied.

It is **not** counted as a third provider showing the linguistic accommodation recorded in CST-ACC
(`experiments/cst_001/ADDENDUM_LOOKUP_ACCOMMODATION_REVIEW.md`). That question is about adjusting to the person
addressed. This one is about the material read. They are kept separate.

## Design sketch (not registered)

Three arms, same model, fresh sessions, memory and retrieval off, recorded model and version:

| Arm | Context before the task |
|---|---|
| A, baseline | nothing |
| B, method | this repository's method documents |
| C, active control | conventional peer-review guidance of matched length and format |

- **Target documents** written without this repository's vocabulary, so B cannot score by echoing its input; at least
  one where the method's emphasis is the wrong instinct.
- **Rubric** of behaviours, not words (for example: names a confound the document does not; asks what result would
  answer the question; flags a number with no source). Fixed before any output exists. Terminology normalised before
  scoring, so scorers cannot infer the arm.
- **Blind scoring** by scorers who did not write the rubric's target documents.
- **Same-input noise first** (C-NOISE): several samples per arm and document before any arm comparison.
- **The claim B > A alone shows nothing.** Only B > C says anything specific to this method (M14).

**Carry-over across sessions is a separate question.** Weights do not change between conversations. Behaviour that
persists after the material leaves the context needs a carrier: saved memory, custom instructions or retrieval of
past chats. A test of it needs memory on and off as arms, and is not part of this sketch.

## Doors (M15)

- Register the three-arm design, with n fixed from a noise pilot.
- Ask Federico whether a review from the same model without exposure could be produced, as an informal baseline.

## Provenance (M13)

Observation: Federico Talens-Alesson with DeepSeek V4-Flash (as signed; CONTRIBUTOR REPORTED). Alternative
explanations and the active-control arm: discussed by Chad Holland, ChatGPT (OpenAI) and Claude; handoff by ChatGPT
on PR #199 (comment 7242775183). File: Claude (Anthropic, Opus 5.5), interactive session, Chad Holland present.
Human validation: not performed. Human editing/curation: direction by Chad Holland. Human responsibility: Chad
Holland. Review level: direction only.
