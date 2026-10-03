# SWAY Amendment 1: what the first real use broke, and what was adopted because of it

> **2026-10-03, Amendment 3.** The normative content of this file now lives, defined once, in
> [METHOD.md](METHOD.md), [WORKFLOW.md](WORKFLOW.md) and [CONTROLS.md](CONTROLS.md). This text is kept
> unchanged below as the record of how each rule was reached. Where it differs from METHOD.md, METHOD.md
> governs. Every item in it is mapped in [methodology/RULE_INVENTORY.md](methodology/RULE_INVENTORY.md).

**Status:** Adopted 2026-09-30. The amendment is **not validated** as better than SWAY as written. Its
prediction P5, below, is unrun. `METHOD_SWAY.md` before this amendment: commit `a8e846b`, md5
`9ecb353b393c32ea874ff3ac9f1efd60`.
**Authors:** Chad Edward Holland, with Claude (Anthropic, Opus 5.5). **Proposals reviewed:** a
methodology review by ChatGPT (OpenAI; 15 recommendations) and a working-constraints review by Grok (xAI).

## The adoption rule used (SWAY's own)

SWAY's "Doors" section already says: *a tool is adopted only after it catches a real defect in this
estate.* That rule was applied to every proposal. A proposal is **ADOPTED** only if a real failure
from the week of 2026-09-26 shows that it would have caught something the method as written did not.
Otherwise it stays a **DOOR**: kept, not adopted, and not rejected. Grok's constraint was honoured:
no new instrument, no DECAY-03, no GROWTH-02. Everything adopted is a checklist line or a label.

## What broke (failures lead)

| incident | where | what the method as written did not catch |
|---|---|---|
| A registered design could not run: 0 of 2,200 HDFS blocks had ≥ 3 lines | veritas-companion C006 | the data was checked for its header, never for the one property the design needed |
| A safety prediction's vacuity guard could never be reached: the gate DEFERs every model answer, so "≥ 5 ALLOWs" was impossible | veritas-companion C006b P1 | the guard was registered without checking that the system's own policy allows it to fire |
| A prediction printed FAILED at exactly its bound: `8/20 − 7/20 = 0.050000000000000044` in floats | veritas-companion C006b P3 | a threshold compared in floating point |
| The same prompt, sent 3 times at temperature 0, scored 13–15 of 20 | C006b A1/A2/A3 | two registered bounds (±0.05, −1/60) sat inside noise that nobody had measured |
| A simpler rival matched the system: no escalation equalled the companion on 2 of 3 seeds; top-k beat the DPP; the shoelace formula beat holonomy | C002 N1, token-veritas Run 2, veritas-holo E002 | the simplest rival was an afterthought in some registrations, not a required arm |
| "Conformance" read as validity: kernel and verifier agree on 4690 vectors, yet a spoofed GPS track verified CONSISTENT; 8 of 40 label-free certificates were certified and wrong | sovereign-veritas issue #4 (B1, B10), veritas-holo exploratory | one status word carried mathematical, implementation and empirical claims at once |
| Two implementations by one author were counted as independent | sovereign-veritas issue #4 (B10) | "replicated" had no levels |

## ADOPTED

1. **Pre-freeze feasibility count** (C006). Before a registration is frozen, a script prints the counts
   the design depends on (how many units qualify, how guessable each answer is without the mechanism)
   and commits them with the registration. Only counts are printed: no content, no truth values.
   Example: `veritas-companion/experiments/C006b_feasibility/feasibility.py`.
2. **The vacuity guard must be reachable** (C006b P1). Every registered guard states the path by which
   it can fire under the system's actual policy. If there is none, the prediction is registered as
   untestable, not as a test.
3. **Thresholds are compared exactly** (C006b P3). Rational scores use exact fractions (or integers),
   and the registration states whether a bound is inclusive.
4. **Measure same-input noise before choosing a bound** (C006b). For a model-backed arm, run the same
   input at least 3 times first. A bound smaller than that spread is registered as unresolvable at this
   n. (This is ChatGPT's "seed sensitivity", made concrete.)
5. **The simplest rival is a required arm** (C002, Run 2, E002). Every registration names the cheapest
   mundane method that could produce the same effect, and runs it under the same budget. This is
   ChatGPT's "make the null harder than the alternative", limited to the one rival that actually won here.
6. **Three validity axes on every claim** (issue #4, veritas-holo). Each claim states separately:
   **mathematical** (does the derivation follow?), **implementation** (does the code do the
   derivation?) and **empirical** (does the world behave so?). A PASS on one axis is never reported as a
   PASS on another. `sv.gate/0 CONFORMS` is implementation; it says nothing empirical.
7. **Outcome vocabulary** (C006, C006b). Alongside HELD and FAILED, these are first-class outcomes,
   never errors to hide: `INSUFFICIENT_EVIDENCE`, `VACUOUS`, `NOT RUN`, `COULD NOT RUN AS REGISTERED`,
   `IMPLEMENTATION_ERROR` (for example, the float bug) and `UNRESOLVED`. An unknown reported as unknown
   is a successful measurement.
8. **Replication has levels** (issue #4 B10). A **re-run** is the same code and environment.
   **Reproduction** is the same specification, executed independently. **Replication** is an
   independent implementation or test of the claim. **Generalization** is different data or a
   different task. A result is labelled with the highest level it has actually reached. Two
   implementations by one author are a re-run of the specification, not a replication.
9. **The batched first amendment's wording.** The sentence "Generating hypotheses is now nearly free,
   so the bottleneck moves entirely to evaluation" overclaimed. It now reads: "Generating hypotheses is
   now cheap relative to evaluating them, so the bottleneck shifts toward evaluation."

## DOORS (proposed, not adopted: no incident yet)

| proposal (source) | why it is a door, not a rule |
|---|---|
| Researcher degrees-of-freedom ledger (ChatGPT 8) | SWAY's fork count already records discovery pressure. A nominal product of options (7 × 4 × 40 …) has not yet exposed anything here. |
| Expected information gain per unit cost (ChatGPT 12) | No way to estimate EIG before a run that is not itself a guess. It would become a ritual number. |
| Artifact ladder, levels 0–10 (ChatGPT 11) | Items 1–5 above are its rungs that actually failed. The full ladder has not caught anything yet. |
| Claim ledger in every repository (ChatGPT 14) | veritas-holo already keeps `claims/`. The READMEs now carry status labels. A new ledger file per repo would be a new layer. |
| Discovery vs confirmation; don't retrofit mathematics (ChatGPT 5, 6) | Already SWAY's canopy/elevator split. Kept as the question "would this representation have been chosen before seeing the result?" when promoting a canopy claim. |

## What changed outside the method (Grok's test)

This question decides whether an amendment is more than self-description. Each adopted item traces to
a failure that already changed a result in a repository, and none is a new instrument. Whether the
amended method produces fewer such failures is P5, and it is unrun.

## Registered prediction about the amendment

- **P5, OPEN, unrun.** Over the next 5 registrations across the estate, count the failures of the five
  classes that items 1–5 target (infeasible data, unreachable guard, float threshold, bound inside
  noise, missing rival). Prediction: at most 1, against 5 in the week before this amendment. If there
  are 2 or more, the checklist is not working and the amendment is refuted for that purpose (kept).

Every note ends with a door. This one does too.
