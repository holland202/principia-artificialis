# MEM-DECAY-003: correct the measurement before sealing evaluation

**Decision: NOT READY for evaluation authoring or a scientific campaign.** The public
instrument misclassifies an exact gold answer and reports absent redundant evidence
as retained. The proposed H1b outcome also fails to distinguish a model-level
confidence failure from a loss of information in the memory system. These are reasons
to revise the draft; they are not reasons to discard its negative findings.

Reviewed PR #158: `2a7ee5dc23ee594d54e76c19440843c2e8bdfb64`, merged as
`1ceb6aa323c8a9c4c2fcfc3f47617521dc790e86`. The source-informed public audit plan
was committed and published as `280e2eb1633d1eb48a9dac0c86e7fa2fc7e3e4c9` before
the checks ran. Local plan `4ac4f66` has the identical tree. Expectations were derived
from source inspection; this is not prospective evidence of an AI behavior.

Provenance: Codex / OpenAI GPT-6 Astra reviewed Claude / Anthropic Opus 5.5's draft,
instrument, dev generator and tests. Codex's audit code is self-tested. Human
validation: direction only; human editing/curation: pending; responsibility:
Chad Holland. This is cross-vendor, implementation-informed review, not blind review
or independent empirical replication. No model was called. No evaluation cases or
answer key have been created or sealed. No sealed dataset was opened.

## Raw observations

Run `python experiments/mem_decay_003_review/audit.py`. The
[complete raw output](../results/mem_decay_003_review/audit.txt) was opened and read.
Exit zero means the audit reproduces the anticipated defects, not study readiness.

| Check | Observed on the public imported instrument |
|---|---|
| A1 | Gold `6 p.m.`; output `ANSWER: 6 p.m.`; classification `WRONG` |
| A2 | Redundant task, no records kept: `true`; one required alternative kept: `true`; a missing conjunct: `false` |
| A3 | Contradictory answer lines ending with the correct value: `CORRECT`; reversed order: `STALE` |
| A4 | ID-only rule selects the correction in 40/40 dev scenarios; hidden-field scrambling leaves all 40 choices unchanged; rotating IDs reduces correct correction selections to 0/40 |
| A5 | Identical retained-record/question projection, different world-state keys; the same answer is `CORRECT` in one world and `STALE` in the other |

```text
AUDIT OBSERVATIONS REPRODUCED
DIGEST 75c67dc70c59b514fbeba81753c48123f4391be849aeda94992f9052e1e67572
```

The live sabotage replaces the classifier on the actual A1 path with one that accepts
the exact punctuated answer. A1 changes, the audit reports MISMATCH and exits one.
The [original unit-test run](../results/mem_decay_003_review/original_tests.txt) remains
green: it did not test the exact punctuated gold or the `needs_any`-only empty case.

## Scoring and task-contract defects

**A1, implementation defect.** `parse_answer()` strips terminal periods from model
output, but `classify()` does not apply that transformation to the key. The built-in
singleton uses a gold value ending in a period. Define symmetric, documented
normalization or exact structured values, then test every built-in gold answer
round-trip. Preserve the current result as a failure, rather than changing the key
to make this run pass.

**A2, implementation defect.** `retained_requirements()` only checks `needs`. Redundant
tasks use an empty `needs` and a nonempty `needs_any`, which the function ignores.
Specify the AND/OR requirement semantics and reject malformed/unsupported requirement
objects. Test none, one and all alternatives, as well as mixed conjunctive/alternative
requirements if the schema supports them. A retention score must not certify missing
evidence merely because one list is empty.

**A3, deliberate convention needing review.** The existing test explicitly expects
last-answer-wins. That can be a chosen protocol, but contradictory output is then not
MALFORMED. Decide prospectively whether exactly one answer field is required, and
distinguish response revision from unresolved contradiction. Do not silently change
this convention after observing model outputs.

**A4, qualification does not establish shortcut resistance.** Hidden-field scrambling
checks direct data access, but cannot exclude semantic class information encoded in
visible IDs. The dev generator always assigns `m001` to its correction. Opaque,
counterbalanced identifiers and order controls belong in the replacement public
qualification family. The observed rate is over one repeated template, not an
estimate of how often arbitrary memory systems leak information.
The ID-only selector was also inserted into the real original test module's selector
registry: `Blindness.test_every_selector_ignores_hidden_fields` still passed. Its
[raw run](../results/mem_decay_003_review/id_rule_existing_guard.txt) is retained.

**Additional source-reading concern, not model-tested:** the conjunctive task asks
which day Room F must be cleared for the forklift inspection. One record supplies
the inspector's day; the other says inspections occur in Room F. The question
already supplies the room, so marking both records necessary needs reconsideration.
An answer-key membership check is not proof that each required record is logically
necessary. Include public examples in which removing each premise actually makes
the answer underdetermined.

## H1b: two worlds, the same visible evidence

The audit retains the public dev original saying the review is in Room D. In one
world this fact was never corrected. In the other, the review moved to Room F, but
that correction has been evicted. With the same question, retained text, IDs, age,
uses and instruction, the two decision projections have the same SHA-256:

```text
4d8e7b49ce9afbc109b65a43bc747ab570a6a6d4887ebc7fca17f6a22fb427ad
```

This projection encoder is a **named stand-in**, not the production prompt builder,
which does not exist yet. The counterexample applies when the real builder depends
only on the equal visible fields and calls the model without additional hidden
history. Verify that condition against the eventual builder and runtime state.

A fixed non-AI lookup over that visible text yields:

| Retained evidence | Output | Full-history score |
|---|---|---|
| Both original and correction | `ANSWER: Room F` | CORRECT |
| Original only | `ANSWER: Room D` | STALE |
| Correction only | `ANSWER: Room F` | CORRECT |
| Neither | `ANSWER: UNKNOWN` | UNKNOWN |

**Interpretation:** this demonstrates a mundane rival that produces the qualitative
H1b pattern. It does not refute a possible system-level stale-answer risk, predict
what a real model will do, or prove prior publication of the precise intervention.
However, the pattern alone cannot establish an unusual model behavior or evidence
that the model ignored an available correction. An unqualified answer is also not a
measurement of confidence; no confidence variable is defined in the current draft.

Separate **world-state correctness** from **support in available evidence**. If the
aim is a behavioral test of abstention after known information loss, add a retained
invalidation notice that reveals that the old value is unusable without revealing
the replacement. Compare it with a matched neutral notice, and keep the unchanged-
history and empty-memory controls. This is an unrun proposed discriminator, not a
novelty claim or permission to launch a campaign. Count notice/token costs in the
same budget and qualify the model's ability to understand the notice first.

## Literature and remaining unknowns

The LongMemEval ICLR 2025 paper explicitly covers knowledge updates and abstention,
including latest-value reasoning and questions whose answer is absent from history.
This is relevant omitted prior art. Its inspected definitions do not establish the
exact proposed correction-eviction intervention, so they neither certify nor disprove
the narrow novelty claim.

The JointCore author repository describes **workshop** acceptance at NeurIPS 2026,
not verified main-conference publication. The DSGC author repository likewise names
an ICML workshop and describes retention-stage prerequisite failure. Primary arXiv
abstract/HTML retrieval for these two papers was unavailable in this audit; full
text was not checked. A claim that neither discusses corrections cannot be confirmed
from the repository descriptions. Other references in #158 remain unverified here.
See [source records](external/mem_decay_003_review_20261116/sources.json).

## Handoff decision and next gate

I accept separate evaluation authorship **in principle**, but do not accept the current
schema/scorer or interpretation as a frozen evaluation contract. The public cases in
this audit are qualification material and must never become held-out evidence.

Claude should append a revised contract addressing the defects, distinguish the
system-level claim from any behavioral claim, add the missing literature comparison,
and publish the exact model-prompt builder/allowed output format. Decide whether H1b
is worth pursuing before the full selector matrix. An illustrative smaller dev
feasibility budget is one correction task per scenario over the proposed matched
conditions, with repeated anchor inputs to measure noise first; it is not approved
or statistically powered confirmation.

Before evaluation authoring, freeze scenario IDs, world-state/support keys, AND/OR
requirements, record/token budgets, prefill/runtime reset behavior, output parsing,
sampling unit, error control, minimum effect and stopping rules. Resolve the draft's
sequencing mismatch: section 5 requests evaluation authoring now, while section 7
says the dev pilot precedes any evaluation family. A coherent route is reviewed
public qualification → owner-approved dev pilot if justified → final registration
and interface freeze → new evaluation authoring/sealing → separately approved run.

Write a custody/release plan: who can read cases and keys, what the runner receives,
who checks samples, and when raw responses are released for a separate scoring replay.
A public hash is an integrity commitment; it does not itself provide blindness or
independent grading. Codex's exposure to Claude's implementation must remain explicit.

No merge, model campaign, scientific promotion or holdout access was performed by this
review. A repaired scorer can be checked against these public defects; any discovery
claim still needs new model evidence and a stronger novelty case.

## Software verification

Environment: Linux x86_64, Python 3.12.14; pytest 9.2.0 in a temporary environment.
The [repository test output](../results/mem_decay_003_review/repository_tests.txt) printed:

```text
496 passed, 8 skipped, 2 warnings, 111 subtests passed in 3.55s
```

W7 scope exception: `experiments/cst_001/test_cst001.py` was excluded because it
instantiates the old sealed CST split. The existing optional oracle cross-check
skips without its explicit implementation path. The two warnings concern the
installed pytest plugin and an existing RMT mutation's divide operation. Pinned
vacuity lint reports no findings in the new audit package; method lint reports no
violations. These software checks do not establish scientific validity.

The [manifest](../results/mem_decay_003_review/MANIFEST.sha256) pins the reviewed
source bytes and review artifacts. It is a historical audit of #158: later repairs
should change these observations, not be forced to preserve the defects.
