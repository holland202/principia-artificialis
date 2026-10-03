# METHOD: how research and builds are done in this estate (SWAY, consolidated)

**Status:** ADOPTED 2026-10-03 by [Amendment 3](METHOD_SWAY_AMENDMENT_3.md), registered at `0c634a1`.
Chad Holland delegated the adoption; the human review level is direction only. It is **not
validated** as better than the texts it consolidates: P6 and P7 are open.

**This file is canonical.** Every rule is defined once, under its ID: here (M), in
[WORKFLOW.md](WORKFLOW.md) (W), or in [CONTROLS.md](CONTROLS.md) (C-).
- Any other text that states a rule (CLAUDE.md, NOTE_TEMPLATE.md, skills, READMEs) cites the ID, or
  carries a verbatim excerpt that [`scripts/method_lint.py`](scripts/method_lint.py) checks.
- Where another text disagrees, this one governs.
- [METHOD_SWAY.md](METHOD_SWAY.md) and its amendments are kept as the record of why each rule exists.
  [methodology/RULE_INVENTORY.md](methodology/RULE_INVENTORY.md) maps every item in them to its home.

**Scope:** every repository in the estate. A registration names the commit of this file it follows.

**Provenance:** AI participation → human validation → human editing/curation → human responsibility.
- **AI participation:** Claude (Anthropic, Opus 5.5) consolidated this text from METHOD_SWAY.md,
  Amendments 1–2, NOTE_TEMPLATE.md, CLAUDE.md and two skills. Suggestions from ChatGPT (OpenAI) were
  evaluated in Amendment 3.
- **Human review:** direction only.
- **Responsibility:** Chad Holland.

The method's authors are Chad Edward Holland, with Claude (Anthropic, Opus 5.5). *Vincit Omnia
Veritas.*

## Force

| Force | Meaning |
|---|---|
| **MUST** | Breaking it changes what may be claimed. Nothing is promoted, and the break is reported first, as a deviation |
| **SHOULD** | The default. Departing from it needs one written reason, wherever the work is recorded |
| **MAY** | An available technique. No reason is needed either way |

Every rule names its source: the incident or text that put it there.

## Rules at a glance

<!-- canonical:index -->
| ID | Force | Rule |
|---|---|---|
| M1 | MUST | Claims can be precisely wrong |
| M2 | MUST | Register before observing |
| M3 | MUST | Anti-vacuity: the instrument can say the other thing |
| M4 | MUST | Real code, named stand-ins |
| M5 | MUST | Exact, deterministic verdicts |
| M6 | MUST | Numbers come from code |
| M7 | MUST | Honest labels |
| M8 | MUST | Failures lead and are kept |
| M9 | MUST | Observation before interpretation |
| M10 | MUST | Nothing certifies itself |
| M11 | MUST | Confirmation is fresh |
| M12 | MUST | The record is append-only |
| M13 | MUST | AI provenance, with the review that happened |
| M14 | MUST | The simplest rival is an arm |
| M15 | MUST | Every line of inquiry ends with a door |
| M16 | MUST | Triggered controls are on unless answered |
| M17 | MUST | One definition per rule |
| M18 | MUST | Change control |
| W1 | MUST | Frame the question |
| W2 | MUST | Register |
| W3 | SHOULD | Design the smallest discriminating instrument |
| W4 | MUST | Build and run |
| W5 | SHOULD | Attack |
| W6 | MUST | Write the results |
| W7 | SHOULD | CI, commit and merge |
| W8 | MUST | Close a build (DONE) |
| W9 | MUST | Record edits |
| C-FEAS | MUST | Feasibility counts |
| C-NOISE | MUST | Measure same-input noise first |
| C-STAT | MUST | Error control that matches the stopping rule |
| C-EVID | MUST | Evidence ladder |
| C-INDEP | MUST | Independence and replication |
| C-EXT | MUST | Outside material |
| C-DEVICE | MUST | Device claims |
| C-BUILD | MUST | Fail-closed verdict code |
| C-EXPLORE | MUST | Exploration is disclosed |
| C-DISCOVER | MAY | The discovery loop |
| C-METHCOMP | MUST | Methodology comparison protocol |
<!-- /canonical:index -->

A C- control is a MUST only when its trigger (§3) fires.

## 1. Core rules

- **M1** · MUST · **Claims can be precisely wrong.** Every claim is stated so that an observation
  could refute it. If nothing could, it is not yet a claim: sharpen it until something could.
  *Source: NOTE_TEMPLATE.md "The claim"; CLAUDE.md method rule 1.*
- **M2** · MUST · **Register before observing.**
  - Predictions are numbered (P1, P2, …), each with exact pass criteria, inclusive or exclusive bounds
    and tolerances.
  - They are committed before any code that tests them runs, in a commit of their own when the result
    will be published or relied on.
  - A registration is never edited afterwards. Errors and changes are appended as dated deviations.
  - Constants and predictions are never retuned after the results are seen.

  *Source: NOTE_TEMPLATE.md; CLAUDE.md rule 2; SWAY elevator; prereg skill §2–§3.*
- **M3** · MUST · **Anti-vacuity: the instrument can say the other thing.**
  - Every instrument and every guard ships with its killer: a planted case or a `--sabotage` switch
    that must flip the verdict (exit nonzero), and a benign case that must pass.
  - The registration states the path by which each guard can fire under the system's actual policy.
    If there is none, the prediction is registered as untestable, not as a test.
  - A guard that only ever prints a value is a log line.

  *Source: NOTE_TEMPLATE.md; CLAUDE.md rule 3; SWAY build rule 4; Amendment 1 item 2 (veritas-companion
  C006b P1).*
- **M4** · MUST · **Real code, named stand-ins.**
  - A question about how a mechanism in the estate behaves is settled by running the repository's real
    code (imported, not copied or reconstructed), after reading the code and specification it touches.
    Explanation alone does not settle it.
  - Every stand-in (a model, a fake backend, constructed inputs, a simulated environment) is named in
    the claim it supports.

  *Source: Amendment 2 item 10 (an external analysis's figures about sovereign-veritas, wrong until
  checked); experiment-first step 2; prereg skill §1, §3.*
- **M5** · MUST · **Exact, deterministic verdicts.**
  - Thresholds on rational quantities are compared exactly (fractions or integers), and each bound
    says whether it is inclusive.
  - Verdicts are seeded or free of randomness.
  - Outputs compared across platforms are rounded, so no threshold sits on a knife edge.
  - A verdict that can be redrawn is not a verdict.

  *Source: Amendment 1 item 3 (C006b P3: `8/20 − 7/20 = 0.050000000000000044`); SWAY build rule 5;
  prereg skill §3.*
- **M6** · MUST · **Numbers come from code.**
  - Every number in prose is pasted from the output of code in the repository, never paraphrased or
    typed from memory.
  - Reading a file is not running it: run, paste, then claim.
  - A claim with no code that prints its numbers is labelled `Speculative`, with the experiment
    described so that someone else can build it.

  *Source: SWAY invariant 1; NOTE_TEMPLATE.md "Reference code"; CLAUDE.md rule 5 and house rules.*
- **M7** · MUST · **Honest labels.**
  - Each claim states its mathematical, implementation and empirical validity separately. A pass on
    one axis is never reported on another.
  - A model, simulation or constructed-input result is `NOT RUN` on the empirical axis.
  - Results state the environment they ran in. Every other environment, including the S25, is
    `NOT VALIDATED` there.
  - `EXPLORATORY` output is never cited as a finding.
  - A promoted note starts at `Draft`, never higher, and no label is raised beyond its evidence.

  *Source: Amendment 1 item 6 (sovereign-veritas issue #4 B1/B10); SWAY invariant 5 and elevator;
  prereg skill §7; Amendment 3 D4.*
- **M8** · MUST · **Failures lead and are kept.**
  - A registered prediction that did not hold stays in the record, marked, with what it taught.
  - Nothing is deleted or reworded to make a claim look better, and a refuted note is never deleted.
  - Results documents open with what went wrong.

  *Source: SWAY invariant 2; NOTE_TEMPLATE.md; CLAUDE.md rules 4 and 7 and house rules.*
- **M9** · MUST · **Observation before interpretation.**
  - Results give the raw observation before any explanation.
  - Explanations cite the code or specification lines they rest on, and are marked as interpretation.
  - A prediction that held is not evidence that the system is valid.

  *Source: experiment-first steps 6–7; prereg skill §4.*
- **M10** · MUST · **Nothing certifies itself.**
  - A verdict above `UNVERIFIED` needs an input the system under test cannot write. A hash-valid
    manifest written by the system proves integrity, not truth.
  - An AI's design, code, interpretation or attack on its own work is **self-tested**, and is labelled
    so.
  - Two sessions of the same AI are not independent unless provenance shows it.
  - Independence needs a different person, or a separately labelled reviewer that has not seen the
    build. A model from the same vendor is labelled same-vendor.

  *Source: SWAY invariant 3 and build rule 3; Amendment 2 item 12 (the A/B and V15 sessions; the V14
  reviewer replaced by the same model).*
- **M11** · MUST · **Confirmation is fresh.** Evidence that confirms a claim is produced after the
  claim is registered, and was not used to shape it:
  - for data, a split sealed (and hashed) before exploration;
  - for code and devices, a fresh run after registration.

  *Source: SWAY invariant 4 and elevator.*
- **M12** · MUST · **The record is append-only.**
  - Results, corrections and provenance are appended and dated.
  - History, timestamps, tags and registrations are never rewritten.
  - Merges keep the order in which registration came before the run: merge commits, never squash.
  - Earlier or duplicate work is preserved and referenced, by an archive tag if needed, not hidden.

  *Source: SWAY invariant 6; prereg skill §3, §5, §6; experiment-first step 10; the A/B archive.*
- **M13** · MUST · **AI provenance, with the review that happened.** Every artifact that AI materially
  helped produce:
  - states the chain AI participation → human validation → human editing/curation → human
    responsibility;
  - names the model;
  - states the one human review level that actually happened (line-by-line, outcome review or
    direction only), never rounded up.

  Human review of AI-assisted material is not validation of its claims. Credit goes to specific,
  identifiable contributions, AI contributors included, by model name.
  *Source: Amendment 2 item 13 (the "Dependent Evidence" drafter misattribution); NOTE_TEMPLATE.md and
  CLAUDE.md credit rules; prereg skill §6.*
- **M14** · MUST · **The simplest rival is an arm.**
  - Every registration names the cheapest mundane explanation or method that could produce the same
    result, and runs it under the same budget.
  - A registration that claims no effect writes "no rival: no effect claimed".
  - A named rival that cannot be run is a recorded deviation, and the claim is weaker for it.

  *Source: Amendment 1 item 5 (C002 N1, token-veritas Run 2, veritas-holo E002); prereg skill §1.*
- **M15** · MUST · **Every line of inquiry ends with a door.** A research note or experiment ends with
  at least one named, unrun test. Builds close instead (W8).
  *Source: NOTE_TEMPLATE.md; CLAUDE.md rule 6; SWAY "Research is different".*
- **M16** · MUST · **Triggered controls are on unless answered.**
  - Every registration carries the trigger table (§3), with each row answered "yes", or "no" with a
    reason.
  - A blank row counts as yes.
  - A missed trigger found later is recorded as a deviation.

  *Source: Amendment 3 D7; the evidence ladder's "cover each row or state why".*
- **M17** · MUST · **One definition per rule.** Each normative rule is defined once, under its ID, in
  METHOD.md, WORKFLOW.md or CONTROLS.md. Other texts cite the ID, or carry a verbatim excerpt checked by
  `scripts/method_lint.py`. *Source: Amendment 3 D9 (F4).*
- **M18** · MUST · **Change control.**
  - A rule is adopted only after a real failure shows it would have caught something the method as
    written did not. Otherwise it is a door.
  - Weakening a MUST, or retiring any rule, needs the same kind of recorded reason (an incident, a
    contradiction or a superseding rule), in a dated amendment.
  - Predictions about the method are scored when their window closes, and the scoring is appended to
    that amendment's results.

  *Source: the adoption rule of Amendments 1 and 2; Amendment 3 D5 and D6 (Amendment 1's P5 expired
  unscored).*

## 2. The loop

Question → register → build → run → attack → record → review → close. The steps are defined in
WORKFLOW.md W1–W8. Record edits take the short path, W9.

## 3. Triggered controls

Copy this table into every registration and fill in the last column (M16). The controls are defined
in CONTROLS.md.

<!-- canonical:triggers -->
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
<!-- /canonical:triggers -->

## 4. Vocabulary map

Each dimension answers a different question. A label from one dimension is never used for another.

<!-- canonical:vocabulary -->
| Dimension | Question it answers | Values | Used for |
|---|---|---|---|
| Prediction outcome | Did the registered prediction hold? | `HELD` · `REFUTED` · `INSUFFICIENT_EVIDENCE` · `VACUOUS` · `NOT RUN` · `COULD NOT RUN AS REGISTERED` · `IMPLEMENTATION_ERROR` · `UNRESOLVED` | each prediction (P1, P2, …), summarized as `VERDICT n of m as registered`. An unknown reported as unknown is a successful measurement |
| Claim / evidence status | What does the evidence support? | `SUPPORTED` · `NOT_SUPPORTED` · `REFUTED` · `INSUFFICIENT_EVIDENCE` | a claim assessed against evidence (sovereign-veritas `epistemic.py`, `ebll/evaluator.py`). `NOT_SUPPORTED` and `INSUFFICIENT_EVIDENCE` are never reported as `REFUTED` |
| Validity axis | What kind of validity has been shown? | mathematical · implementation · empirical, each `PASS`, `FAIL` or `NOT RUN` | every claim (M7). Conformance (for example `sv.gate/0 CONFORMS`) is implementation only |
| Replication level | How independently has it been reproduced, and by whom? | self-tested · re-run · reproduction · replication · generalization | a result (C-INDEP). A re-run uses the same code and environment; a reproduction, the same specification executed independently; a replication, an independent implementation or test; a generalization, different data or a different task. The label is the highest level actually reached, with who reached it |
| Note status | How far has this note got? | `EXPLORATORY` · `Speculative` · `Draft` · `Draft, verified reference code` · `Architecture Self-Tested` · `Architecture Verified` · `Verified` · `REFUTED (kept)` | Principia notes and equivalent write-ups. `Verified` means the reference code prints the claimed numbers; it is not independent validation |
| Lineage | Is an influence claim shown? | `SUPPORTED` · `NOT SUPPORTED` · `INDETERMINATE` | rows in `LINEAGE.md` (C-EXT) |
| Review level | How much human review did AI-assisted work get? | line-by-line · outcome review · direction only | every AI-assisted artifact (M13) |
| Instrument gate | Does the instrument itself work? | `GATE: PASS` or `GATE: FAIL`; sabotage exits 1 | instruments, harnesses and lints (M3). This is not a prediction outcome |
| Study state | Where is a registered study? | `REGISTERED` · `RUN` · `PARKED` · `UNRUN` | registrations and studies. `PARKED`: the design is stopped, not frozen. `UNRUN`: the study cannot run as designed |
| Repository summary | A cross-repository summary | `IMPLEMENTED` · `EXPERIMENTAL` · `VERIFIED` · `REPRODUCED` · `REFUTED` · `UNRESOLVED` · `NOT TESTED` | `PROVENANCE.md` files only. It is a summary layer and never replaces the dimensions above |
<!-- /canonical:vocabulary -->

**Older words, and how to read them in records written before 2026-10-03** (Amendment 3, D1 and D2):

<!-- aliases -->
- `FAILED`, as the outcome of a registered prediction, reads as `REFUTED`. Instrument and runner
  outputs such as `GATE: FAIL` or pytest's `FAILED` belong to the instrument-gate dimension.
- The experiment-first skill's eight-word list (retired) maps as follows:
  - "observed" is any recorded prediction outcome other than `NOT RUN`;
  - "reproduced" is the replication level *reproduction*, and only that;
  - "supported", "not supported" and "refuted" are claim statuses;
  - "unknown" is `INSUFFICIENT_EVIDENCE` or `UNRESOLVED`;
  - "not tested" is `NOT RUN`;
  - "simulation-only" is the empirical axis `NOT RUN`, with the stand-in named (M4).
<!-- /aliases -->
