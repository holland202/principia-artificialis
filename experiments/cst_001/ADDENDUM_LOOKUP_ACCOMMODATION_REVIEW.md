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
