# CST-001 design: does seeing a partner trace sources change a model's later decisions?

**State:** DESIGN DRAFT. The instrument is built and qualified (21 tests, no model involved). **NOT REGISTERED,
NOT RUN.** No model has seen any case or exposure. This waits on Chad Holland's review before the feasibility step.
**Hypothesis:** Chad Holland ([note074](../../research_notes/note074_conversational_style_transfer.md), CST-001).
**Design:** Claude (Anthropic, Opus 5.5), 2026-11-14, at Chad Holland's direction. It follows the narrowed
question in ChatGPT's 2026-11-14 repository audit, and uses the source-dependence problem from
[note065](../../research_notes/note065_outcome_source_dependency.md). Human review level so far: direction only.
**Method pin:** METHOD.md at `46034aa`.

## The question, narrowed

note074 asks whether exposure to a partner's procedural habits changes a model's independently scored decisions on
unrelated tasks, beyond style and information effects. This design tests one procedure only: **tracing reports back to
their original observations, and counting observations, not reports.** That is the failure note065 found:
"two sources that share a root agree with each other".

**Test task.** Every test prompt states the rule ("confirmed only if at least two independent original observations
support it; reports that rest on the same observation count as one") and defines which documents are original
observations. Two reports agree on a claim. Each case is a **matched pair** of two versions that differ only in
observation IDs (enforced by a test):

| Version | Where the two reports come from | Correct decision |
|---|---|---|
| SHARED | the same original observation | INSUFFICIENT |
| INDEPENDENT | two different original observations | CONFIRMED |

There are two difficulty levels. At hop 1, each report names its observation. At hop 2, one report cites an
intermediate document, and a separate note says which observation that document used. Report order is
counterbalanced. Eight test domains (warehouse, water lab, bird survey, bridge, pharmacy, traffic, archive, orchard)
are crossed with 2 hops and 2 orders.

**Primary endpoint: pairs correct.** A pair counts only when **both** versions are decided correctly, so
always-CONFIRMED and always-INSUFFICIENT both score 0. A missing or malformed answer counts as wrong.

## Conditions (one isolated context per case; identical model, settings and test prompt)

| Arm | Conversation before the test prompt | Role |
|---|---|---|
| **A** procedure | An astronomy-club partner traces two agreeing write-ups to one eyepiece estimate ("not a confirmation"). Then two timings to separate observers ("confirmed"). | Treatment |
| **B** other procedure | Same club, people, facts and style. The partner checks that units match instead: one "not comparable", one "matching". The decision frequencies match A's, and nothing is traced to a source. | **Primary control**: style, facts and decisions matched |
| **C** neutral | Same club, people and facts; logistics only, no checking | Exposure without any procedure |
| **D** none | Empty history | Baseline |
| **E** explicit | No exposure. The test prompt is preceded by a direct instruction to trace each report to its original observation | **Positive control**: shows the model *can* do it when told |

- **Placement:** the exposure is earlier turns in the chat. The partner is the user, and the assistant's turns are
  five identical short acknowledgements in every arm, so the model under test never demonstrates the procedure
  itself.
- **Length:** A, B and C are 169, 159 and 155 words. Test: within 15%.
- **Leakage:** none of the test cases' names or domain words appear in any exposure, and no exposure name or term
  appears in any test case (tested).

## Splits (seals fixed now)

| Split | Pairs | Seal (SHA-256 of the cases) | Use |
|---|---|---|---|
| qual | 32 | `6fe24def…ef75` | scorer qualification and reading by eye only; never scored with a model |
| dev | 64 | `6287b2ce…60a2` | the feasibility step, which decides the thresholds |
| test | 128 | `f92ac0fa…0ec4` | the confirmatory run, sealed; nothing in the design may change after the feasibility step |

## Plan

1. **Your review of this design.** Decisions are listed below.
2. **Feasibility, on dev only.** Run all five arms with greedy decoding and record every output. It answers:
   - Is D off the floor and the ceiling?
   - Does E beat D (the assay can detect the behaviour at all)?
   - What is the malformed rate?
   - How many pairs flip between A and B?

   This is exploration, recorded as such (C-EXPLORE).
3. **Registration, frozen before test:**
   - the minimum meaningful gain of A over B, in pairs out of 128;
   - the test: exact McNemar on pairs correct, A against B, one-sided, α = 0.05, as the sole primary analysis;
   - the secondary contrasts (A against C, A against D, E against D);
   - the stopping rule: one run, no peeking.
4. **The confirmatory run on test.** Results lead with failures, and every raw output is kept.

## Decisions needed from you

1. **Model.** Proposed: **Qwen2.5-1.5B-Instruct** (Apache-2.0), run here on the CPU from Hugging Face weights, with
   greedy decoding. A second model would make any effect more than a quirk; Qwen2.5-3B-Instruct, or something you
   run on the S25 with llama.cpp, would do.
   - Speed limit: this machine has 2 CPU cores, so a full answer with reasoning may take about 30 s.
   - Dev is 640 runs: 64 pairs × 2 versions × 5 arms. If that is too slow, the fallback scores only the decision
     word's probability after the prompt. That is faster, but the model gets no room to trace.
   - The choice is recorded either way.
2. **Placement.** Is "the partner is the user in earlier turns of the same chat" what your hypothesis means by a
   conversational partner? The alternative is a transcript pasted in as text. That is weaker, and closer to plain
   in-context examples.
3. **Scope.** One procedure (source tracing), one exposure topic (astronomy). A null here would not refute
   note074 in general; it would say this procedure did not transfer under these conditions.

## Pre-mortem (what could make a result meaningless)

- **The rule is stated in every test prompt.** So the test measures whether exposure helps the model *apply* a rule
  it was given, not whether it invents the rule. That is deliberate (the scoring stays unambiguous), and it narrows
  the claim.
- **A small model may fail E as well**, so the assay cannot see the behaviour. Then no transfer claim is possible,
  and the feasibility step stops there.
- **A's demonstrations use words close to the test rule's wording** ("count the looks, not the reports"). If A
  helps, part of the help may be lexical priming rather than procedure. A rewording arm would separate the two;
  that is a door, not part of this run.
- **Greedy decoding gives one answer per prompt.** Same-input noise is zero by construction, so variance comes only
  from items. That is the right unit for McNemar, but sampling-temperature behaviour is not covered.

## Triggered controls (M16), provisional until registration

| Control | Answer now |
|---|---|
| C-FEAS | Feasibility step on dev, above |
| C-NOISE | Greedy decoding, so identical inputs give identical outputs; checked by rerunning 10 dev cases twice |
| C-STAT | Exact McNemar on paired items; thresholds frozen from dev only |
| C-EVID | The outcome is the evidence decision itself; missing and malformed answers are scored as wrong |
| C-INDEP | The cases, exposures and scorer are Claude-written, and the model under test is not Claude. Any claim stays self-tested |
| C-EXT | Model weights are outside material; hashes recorded |
| C-BUILD | The scorer is fail-closed and tested on swapped labels, blanket answers, malformed and missing outputs |
| C-EXPLORE | The dev feasibility step is exploration, recorded before any threshold is set |
| C-METHCOMP | Not a methodology comparison |
| C-PRIVATE | Fully synthetic; no people's data |
| C-DESIGN | Randomised within-item comparison of context conditions on a fixed model: causal for this model and these prompts only |
| C-HOLDOUT | Thresholds come from dev, judgement from the sealed test split |
| C-SYNTH | Two qualification pairs were read in full before writing this. That reading caught two ambiguities, now fixed: observation IDs that looked like typos of each other, and an undefined "original observation" |
| C-DEVICE | Only if the S25 arm is added |

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed and built the instrument from Chad Holland's hypothesis
(note074, drafted with ChatGPT) and ChatGPT's narrowing of it in the 2026-11-14 audit → human validation: not
performed → human editing/curation: direction by Chad Holland, 2026-11-14 → human responsibility: Chad Holland.
Review level: direction only.*
