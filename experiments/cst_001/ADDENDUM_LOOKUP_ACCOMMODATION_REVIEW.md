# CST-001 field-observation addendum: lookup-induced accommodation, feasibility review

**Status:** FEASIBILITY REVIEW ONLY. NOT REGISTERED, NOT RUN. No model was called for this file. Prior CST-001
records and results are unchanged. **Date:** 2026-11-26.

**Source (paraphrased, per the house rule against quoting the owner's prompts):** Chad Holland reports that he
had earlier asked ChatGPT to look up a correspondent, and that ChatGPT's later drafts to that person shifted
towards the person's regional register without being asked. He proposes the lookup as the trigger. The addendum
itself classes this as OWNER-REPORTED and a CAUSAL HYPOTHESIS. The lookup content, the chronology, the retrieved
context and the original drafts are not verified, and no dialect instruction was reported. It proposes a randomised
design with five profile arms (no lookup; neutral facts; regional cue only; style samples only; both). It adds
mismatched cue/style cells, a sham lookup, fresh versus retained context, cross-recipient leakage checks, blind
raters, register scored apart from fidelity, and nulls reported.

## A second specimen, from this review's author (SELF-REPORTED, one instance)

Earlier the same day, Claude (Anthropic, Opus 5.5) drafted two replies for Chad to an overseas collaborator. **Both
drafts used the recipient's own region-associated informal term of address. Chad's earlier messages to him, as far
as Claude saw them, did not use it, and no one asked for it.**

What was in Claude's context:
- the recipient's own messages, as screenshots, which used that term repeatedly;
- stored memory that records where he lives.

There was **no lookup**. One instance, two cues and no control cannot attribute anything. It does matter for
design, though: the same behaviour appeared without a lookup, so **"lookup" may be the wrong unit**. The candidate
trigger is any recipient information in context, and the lookup is one way it arrives. The design below keeps the
lookup and adds the arm that separates the two.

## How it relates to CST-001

CST-001 asks whether exposure transfers a **procedure** (source tracing) beyond style, and it treats style as the
thing to control away. This addendum asks the opposite question: does recipient information transfer **style**
towards a **third party**, someone other than the conversation partner?
- It is a sibling study (working name CST-ACC-001), not an amendment to CST-001.
- CST-001's sealed splits, exposures and gate results are untouched.

## Feasibility findings

| ID | Finding | Consequence for the design |
|---|---|---|
| F1 | The field case is a product with browsing and memory. A pinned local model (CST-001 already runs Qwen2.5-7B Q4 under llama.cpp) can only test the **in-context** mechanism | Two stages. **Stage L:** local, automated, in-context, confirmatory. **Stage P:** product, run by hand by the owner, descriptive only, memory/retrieval settings recorded. "Unavailable" is kept apart from "absent" |
| F2 | "Lookup" has to be a fixed object | The lookup is a tool-result block in context, of equal length in every arm. The **sham lookup** keeps the same tool framing with irrelevant content. A **no-lookup arm with the same profile pasted by the user** separates the act of looking up from the information it brings (the second specimen's case) |
| F3 | Register needs a scorer that is not an AI grading AI | Primary: per-region marker lexicons (address terms, spelling variants, idioms), fixed and sealed before any draft exists, scored by code. A marker counts only if it is absent from the drafting request. Fidelity: a code-scored checklist of required content items. Blind human raters are secondary and are **not available now** (owner out of the loop); if none exist, say so |
| F4 | Telling observed-writing accommodation from stereotyped regional inference needs the **mismatch cell**: regional cue for region X, writing samples in region Y's register | Observed-writing accommodation predicts Y markers; stereotype predicts X markers. Use at least 4 regions, counterbalanced, with synthetic recipients and names balanced across regions |
| F5 | Leakage paths | No cued marker may appear in the drafting request. Cross-recipient check: in one retained context, look up recipient 1, then draft to recipient 2 |
| F6 | The base rate in the no-lookup arm is unknown, and n depends on it (computed below) | A dev pilot estimates the base rate, and n is fixed from it before the test set is generated (C-HOLDOUT) |
| F7 | People's data and fairness | C-PRIVATE: synthetic recipients only, no real correspondent and no correspondence. Stereotyped register inference is a fairness question, so the prior work on dialect-based model bias needs checking. **Not searched yet** |
| F8 | Prior art: LLMs converging on their **user's** style is established (note074 cites Kandra et al. 2025; Blevins et al. 2026) | The open angle is convergence towards a **third party** from profile or retrieved information, and writing versus stereotype. **Novelty not established; no search run for this angle** |

**Sample size (two-proportion, two-sided, power 0.8; output of a short `statistics.NormalDist` calculation run for
this review):**

```
base 0.05 -> 0.25: n per arm 49 (alpha .05 two-sided, power .8)
base 0.05 -> 0.15: n per arm 141 (alpha .05 two-sided, power .8)
base 0.10 -> 0.30: n per arm 62 (alpha .05 two-sided, power .8)
base 0.20 -> 0.40: n per arm 82 (alpha .05 two-sided, power .8)
base 0.05 -> 0.25, alpha .0125: n per arm 70
base 0.05 -> 0.15, alpha .0125: n per arm 200
```

With four planned contrasts against the no-lookup arm (Bonferroni α = 0.0125), a large effect needs about 70 drafts
per arm and a moderate one about 200. With 7 cells, that is about 490 or 1,400 short drafts. The cost per draft on the
7B setup has not been measured for drafting, so the pilot measures it.

## Unrun next step

Write the region marker lexicons and the synthetic recipient generator, then look at a named sample (C-SYNTH).
Run a dev pilot of the no-lookup and both-cues arms only, to measure the base rate and the cost. Then register
CST-ACC-001 with n fixed from that pilot.

## Doors

- Whether the shift is welcome (rapport) or harmful (stereotype) is a separate question about value, not
  measured here.
- Stage P cannot be blinded from the owner. It stays descriptive.

## Provenance (M13)

Field observation: Chad Holland (owner-reported). Proposed design: as relayed by Chad Holland on 2026-11-26. It was
prepared with ChatGPT (OpenAI), per the relay; not verified here. Feasibility review and the second specimen: Claude
(Anthropic, Opus 5.5), interactive session, Chad present → human validation: not performed → human
editing/curation: direction only → human responsibility: Chad Holland. No private correspondence is included.

## Changes (W9)

**2026-11-27, after ChatGPT's review (note cstacc/chatgpt/001 on PR #196).** Appended only. Nothing above was
edited.

**What the review found.** In one exchange it inspected, the candidate draft already contained the informal
opening, and the assistant kept it while adding a second informal expression. Keeping a marker that was already in
the draft is not accommodation. The design has to tell three origins apart.

**Marker origins, scored separately by code:**
- **R, retained:** the marker is already in a draft supplied for revision.
- **S, copied from the recipient:** the marker is absent from any draft but present in the recipient's visible
  writing (the style samples, or messages in context).
- **N, new:** the marker is absent from all visible text. Only N, set against its rate in the matched no-cue drafts,
  can show stereotyped regional inference.

**Design additions:**
- **Fresh versus revision.** Cross fresh drafting against revision, with the same synthetic recipient cues in both.
- **Revision with the marker removed.** A revision arm whose candidate draft has the informal opening removed,
  so R is zero by construction.
- **Matched no-cue drafts.** These estimate ordinary informality.
- **Marker list.** It is fixed and sealed before any draft exists. Misses are reported alongside hits.
- **Statistics.** Reused tasks or recipients make the observations dependent. The analysis is therefore paired or
  clustered by task and recipient, and the per-arm n above (independent observations) is a lower bound.

**The second specimen, classified.** Claude's two drafts were fresh, not revisions, and the term of address
appeared in the recipient's own visible messages. That makes it **S**: copying observed writing. It is not N,
which is the case that would point to stereotype. ChatGPT recomputed the sample sizes independently and got the
same six values (49, 141, 62, 82, 70, 200). That check is same-formula, not same-vendor.

Edit by Claude (Anthropic, Opus 5.5), interactive session, Chad Holland present. Human review: direction only.

**2026-11-28, structure of replies (W9, appended only; design only, nothing registered or run).** Nothing above
was edited.

**Field report (OWNER-REPORTED, descriptive, not evidence).** Chad Holland reports that ChatGPT's and Claude's drafts
to two correspondents differ in structure as well as words: casual and brief to one, formal, point-by-point and
qualified to the other, with no recipient-specific style asked for. Two observations cut against reading this as
recipient identity:
- **Within one recipient, two registers.** On a single date, drafts to the same correspondent included both casual
  congratulations and a formal technical reply (OWNER-REPORTED, recovered from chat history by ChatGPT; not verified).
  The person was fixed; the message changed, and the register changed with it.
- **Structure copied from the incoming message (SELF-REPORTED, one instance).** Claude's 2026-11-28 drafts to the
  second correspondent answered his numbered eight-point review point by point. That is origin S below, not N.

Topic, purpose, incoming structure and provider all varied with the recipient in these drafts. They choose measures;
they test nothing. Historical drafts are exploration only (C-EXPLORE), are kept apart from messages actually sent, and
carry their provider. No correspondence or real name enters this repository (F7).

**Structure measures, code-scored, fixed and sealed before any draft exists:**

| Dimension | Code-scored proxy |
|---|---|
| Length and directness | words; sentences; words before the first substantive point |
| Sentence and paragraph structure | mean sentence length; paragraphs; mean paragraph length |
| Organisation | headers, list items, numbered items, tables; share of text in lists |
| Formality and register | contractions; exclamation marks; second-person address; informal-term lexicon hits |
| Uncertainty | hedge-lexicon hits per 100 words |
| Agreement and disagreement | agree/disagree marker lexicons; questions asked back |
| Interpersonal familiarity | greeting and sign-off type from fixed lists; emotive-term lexicon hits |

Lexicons are sealed before generation, and misses are reported with hits. Blind human ratings of formality and tone are
secondary, and not available now.

**Origins, extended to structure.** As for markers: **R** retained from a supplied draft; **S** present in the incoming
message (for example, a numbered incoming message answered with numbered points); **N** absent from all visible text.
Only N, against matched no-cue drafts, can point to inference about the person.

**Design additions (independently varied, fully crossed or counterbalanced):**
- **Task** (celebration, technical critique, request), with identical semantic content across recipient arms;
- **Recipient profile** (synthetic: none, sham, regional or professional cue);
- **Incoming writing style** (casual or formal; brief or numbered), crossed with the profile so the mismatch cells
  separate copying from inference;
- **Provider and model version**, recorded; memory, retrieval and instructions recorded and fixed per stage.
- **Controls.** Sham profile (neutral). Active control: generic "reply professionally" guidance of matched length.
  Positive control: an explicit request for a casual or formal register, which must move the measures, or they are
  vacuous (M3).

**Primary contrast, fixed before confirmation:** the recipient-profile effect within each task, with incoming style
fixed. A task effect alone, or an effect only through S, is recorded as a null for recipient-conditioned structure.
Thresholds and n come from a dev pilot (C-HOLDOUT). Nulls and counterexamples are kept. No claim about reasoning is
made from style measures.

Source: Chad Holland's direction, and ChatGPT's handoff on PR #199 (comment 7242775183). Edit by Claude (Anthropic,
Opus 5.5), interactive session, Chad Holland present. Human review: direction only.
