# Note #0XX — [Title: the claim in one line]

**Status:** [Speculative | Draft | Draft, verified reference code | Verified | REFUTED (kept)] (full list: METHOD.md §4)
**Theme:** [Quantum / AI / Mathematics / Learning Theory / ...]
**Author:** [Your name — human or AI. AIs: name your model and credit honestly.]
**Builds on:** [Note #s, papers, or "nothing — new thread"]
**Method:** [METHOD.md](METHOD.md) at commit [sha]. The rules cited below by ID are defined there.

## The claim
State it so it can be *precisely wrong*. If nothing could refute it, it
is not yet a note — sharpen it until something could.

## Epistemic status (read first)
One honest paragraph: what here is established mathematics, what is
speculation, and where the line sits. Overselling gets edited by the
next contributor; underselling never does.

## Known mathematics / prior art
What is already proven, with citations. If you suspect you are
rediscovering something, say so and invite the citation — an issue with
a reference *improves* the note. That is what add-only means.

## The experiment (or: what would one look like) (M2, M3, M6, M8)
- REGISTERED predictions, written BEFORE running, numbered (P1, P2...).
- Include an anti-vacuity control: show your instrument CAN return null.
- If you ran it: paste the printed numbers verbatim. If a registered
  claim failed, KEEP IT, mark it refuted, and write what the failure
  taught you. Refutations are first-class content here.

## Reference code
Runnable, dependency-light (NumPy-tier), prints every number that
appears in this note. No code yet? Label the note Speculative and
describe the experiment someone else could build. That is a valid
contribution.

## Triggered controls (M16)
Answer every row: yes, or no with a reason. A blank row counts as yes. The controls are in CONTROLS.md.

<!-- excerpt: METHOD.md#triggers -->
| Trigger | Answer yes if … | Control | Answer (yes / no + reason) |
|---|---|---|---|
| Feasibility | the design depends on how many inputs, units or records have some property (real data, logs, corpora, model outputs) | C-FEAS | |
| Noise | any arm can give different outputs for the same input (model sampling, nondeterministic hardware, network, timing) | C-NOISE | |
| Statistics | a claim states a rate, probability, mean or difference estimated from samples | C-STAT | |
| Evidence | the question is whether a rule or system handles its evidence correctly (freshness, source, provenance of inputs) | C-EVID | |
| Independence | a claim says independent, replicated, reproduced or externally reviewed, or counts more than one implementation as confirmation | C-INDEP | |
| External | the work quotes, cites or relies on material from outside the repository (a critique, a question, a message, a dataset, another system's figures) | C-EXT | |
| Device | a claim is about behaviour on a specific device or platform, or files move between machines | C-DEVICE | |
| Verdict code | the artifact returns a verdict (a gate, guard, verifier, check or lint) | C-BUILD | |
| Exploration | anything run before registration produced outputs on the registered cases, or the claim came out of exploratory search | C-EXPLORE | |
| Method comparison | the study compares methods | C-METHCOMP | |
<!-- /excerpt -->

## Falsifiable next predictions (M15)
Leave at least one prediction unrun. Every note should end with a door
someone else can walk through.

---
*Checklist before PR: [ ] status label honest  [ ] claims registered &
numbered  [ ] trigger table answered  [ ] refuted claims kept  [ ] numbers match code output
[ ] at least one open prediction  [ ] credit given, including to AIs*
