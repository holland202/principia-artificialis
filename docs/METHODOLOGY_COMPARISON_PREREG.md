# Methodology comparison: earlier practice vs current workflow — registration (Stage 1 of 2)

**Status:** Registered 2026-10-03. Nothing is built or run. This file is not edited after its commit.
Errors are recorded as dated deviations in a separate file.

**Provenance:**
- **AI participation:** Chad Holland specified the study. Claude (Anthropic, Opus 5.5) reconstructed
  the earlier method from the repository and drafted this registration.
- **Human review level at commit:** direction only. Chad Holland set the task; the text has not had a
  line-by-line review.
- **Responsibility:** Chad Holland is responsible for the adopted design.
- **Not independent:** the drafter also wrote Condition B's two skills and the draft SWAY Amendment 2.
  This registration is therefore not an independent design. See "Design flaws" below.

## Observable question

For comparable research-and-development tasks, does applying the current methodology change defect
discovery, unsupported conclusions, reproducibility, or research cost, compared with applying the
historically reconstructed earlier methodology?

"Is the current methodology better?" is the interpretation under test, not the question.

## Hypotheses (competing, none selected)

- **H1, improvement:** B beats A on at least one primary outcome, by the decision rule below, without
  meeting the H2 cost condition.
- **H0, no meaningful difference:** every primary outcome falls within its equivalence margin.
- **H2, cost without benefit:** B's cost exceeds the cost threshold, and no primary outcome favours B.
- **H3, task-dependent:** the direction of the B−A difference reverses between task categories
  (reported as descriptive only; see the status rules).
- **Also possible:** A beats B ("earlier performed better"), or the evidence is insufficient to
  distinguish them. Both are registered outcomes, not failures of the study.

## Condition A: the earlier method, reconstructed from the record

**Period:** before SWAY's adoption at `a8e846b` (2026-09-22 16:57 −0500). The last commit before that
date is `4afb3a2`.

**Documented requirements.** Source: `NOTE_TEMPLATE.md` (md5 `def8d93cf496a21a32efe7cc047f27c4`) and
`CLAUDE.md` "The method (binding)" (md5 `465206e261de1c6e19218b7072b693da`), both at `4afb3a2`.

| # | Requirement | Source |
|---|---|---|
| A-D1 | State claims so they can be precisely wrong | NOTE_TEMPLATE; CLAUDE.md rule 1 |
| A-D2 | Register numbered predictions (P1, P2, …) before running | rule 2 |
| A-D3 | Include an anti-vacuity control: the instrument can return null | rule 3 |
| A-D4 | Keep refutations, marked, with what they taught | rule 4 |
| A-D5 | Numbers in prose match code output verbatim | rule 5 |
| A-D6 | Leave at least one prediction unrun | rule 6 |
| A-D7 | Failures lead the document | rule 7 |
| A-D8 | Honest status labels from a fixed ladder | CLAUDE.md status labels |
| A-D9 | Credit contributors, including AIs by model name | NOTE_TEMPLATE checklist |
| A-D10 | Reference code is dependency-light and prints every number in the note | NOTE_TEMPLATE |

**Observed practice** (in commits before `a8e846b`; practised, not written as a rule):

| # | Practice | Evidence |
|---|---|---|
| A-O1 | A sabotage run must exit nonzero | `6e7847c` (note059: "real rc=0, sabotage rc=1") |
| A-O2 | Device verification on the S25 | `6e7847c`, `2da31cb`, `0944afe` |
| A-O3 | Dated amendments that keep the earlier text | `5cc514d`, `27f6658`, `e9b4e68` |
| A-O4 | A prediction registered in a commit of its own, before the run | `0f8061c` ("committed unrun"), `e9b4e68` |
| A-O5 | A runtime harness that refuses to report when an instrument gate fails | `scripts/prereg.py`, `0944afe` |
| A-O6 | Confounds of the instrument found and fixed with a kept record | `5cc514d` (masked-crash confound) |
| A-O7 | Mutation scores reported with their denominator | `6e7847c`, `27f6658` |

**UNKNOWN.** The record does not establish whether these applied. None of them is assumed absent,
and none is imposed on Condition A.

| # | Requirement | Why UNKNOWN |
|---|---|---|
| A-U1 | Whether registration *always* preceded the run in a separate commit | Many pre-SWAY notes commit predictions and results together (for example `6e7847c`). Git cannot show the order inside one commit. |
| A-U2 | Whether a simplest-rival arm was expected | not documented; not checked across all 221 pre-SWAY commits |
| A-U3 | Whether feasibility counts were taken before registration | not documented |
| A-U4 | How independence and replication levels were judged | not documented (B gets these from Amendment 1, item 8) |
| A-U5 | Whether AI provenance carried review levels | not documented |
| A-U6 | Whether evidence-condition matrices (stale, replayed, …) were standard | not documented |

**How the inferences are handled.** Statements about what the researchers "probably intended" are
excluded from Condition A's instructions.

**What Condition A executors receive:** A-D1 to A-D10 and A-O1, A-O3 to A-O7, verbatim from this table.
A-O2 is excluded from both conditions (see the limits). They also receive `scripts/prereg.py` at
`4afb3a2`.

**What they do not receive:** anything from `METHOD_SWAY*`, the Condition B skills, or the A-U rows.

**A finding for the design:** the documented A rules are **still in force** in B. `NOTE_TEMPLATE.md`
and `CLAUDE.md` have the same md5 at `4afb3a2` and at `main` `4c7518a`. So B is A plus additions, and
the comparison measures the effect of the additions.

## Condition B: the current method, frozen

These are frozen at registration:

- `METHOD_SWAY.md`, md5 `aae4d54fa2c92e6869085884b70c1960` (main `4c7518a`).
- `METHOD_SWAY_AMENDMENT_1.md`, md5 `a051e7da4c4564445d1174db0be59b07`.
- The `prereg-research-workflow` skill, md5 `0992bc29efb422d6eff751c972a0ef46`.
- The `experiment-first` skill, md5 `e5fa5a566fa9055f6293926c6db90dfc`.

Both skills are the synced copies at registration. Their full text is placed in
`docs/methodology_comparison/frozen/` in the Stage 2 commit, and that commit is checked against these
md5s.

- **Also in force for both:** A-D1 to A-D10, as above.
- **Excluded:** SWAY Amendment 2 (an unadopted draft, parked uncommitted) and any change made after
  this commit.
- **Defects found later:** a defect found in B during the study is recorded as a deviation; it is not
  fixed inside the study.

## Task population

**Categories,** with 2 tasks each, 18 in total:
1. implementation behaviour;
2. evidence verification;
3. adversarial testing;
4. deterministic algorithm behaviour;
5. provenance/lineage;
6. malformed/boundary handling;
7. repository-level engineering change;
8. evidence freshness;
9. protocol/contract behaviour.

**Inclusion criteria (fixed now):**
- a self-contained, stdlib-Python target;
- one stated research question;
- ground truth sealed by the task author before any execution;
- solvable inside the session budget below.

**Exclusion criteria (fixed now):**
- any target derived from this estate's known history (V11–V15, XB-1/2, PX, A/B, EL-007, note059 and
  similar), because the executors know it;
- anything needing the S25, the network or a GPU;
- tasks whose answer depends on taste rather than an observable failure.

**Mix (fixed now):**
- at least 4 of the 18 are **null tasks**: no defect, or a correct claim. These measure false
  positives and overhead.
- at least 4 are **"plain" tasks** that a single test settles, where B's extra steps are expected to
  add cost rather than findings.
- tasks are not chosen to favour B.

**Who builds the tasks:** a person other than the drafter of this registration. The default is Chad
Holland or an outside contributor. The drafter must not plant, see or score the ground truth.

**Recorded per task:** category, lines of target code, number of planted defects, null or not, and the
author's estimate of difficulty (1–3), all recorded before execution.

## Design

- **Executors:** fresh Claude sessions (model pinned at Stage 2). Each session gets **one** task, under
  **one** condition, with its condition's frozen method text, and nothing about the other condition.
- **Matching:** every task runs under both conditions, with **2 replicate sessions per condition**, so
  4 sessions per task and 72 in total. The replicates measure same-input noise (Amendment 1, item 4).
- **Equal budget per session:** the same wall-clock cap (Stage 2 fixes it, default 90 minutes), the
  same tool access and the same task text.
- **Ordering:** the 72 sessions run in a random order from a seed committed in Stage 2. No session
  sees another session's output.
- **Preserved per session:** every artifact, the full transcript, the commit, the commands, wall time
  and token count.

## Evaluation

- **Extraction.** A separate extraction pass turns each session's artifacts into a fixed form: claims,
  each claim's stated status, evidence pointers and reproduction commands. Method-specific vocabulary
  is mapped to neutral fields, and the extraction rules are fixed in Stage 2. This is partial blinding.
  Full blinding is not claimed.
- **Evaluator.** The evaluator is the task author, or another person who executed nothing and did not
  draft this file. The evaluator scores the extracted forms against the sealed ground truth.
- **Model-only evaluation.** If the evaluation is done by a model, it is reported as **same-vendor,
  not independent**.
- **Anti-vacuity of the evaluation itself.** Before scoring, the evaluator scores two calibration
  forms per task, prepared by the task author: one containing the planted defect, one omitting it.
  The instrument must record "discovered" for the first and "missed" for the second. If it fails on
  any task, that task is excluded and the exclusion is reported.
- **Detection floor.** If every session under both conditions misses a planted defect, that task's
  defect is flagged as a possible instrument or task defect. It is reported, not counted for either
  condition.

## Primary outcomes (definitions fixed now)

1. **Genuine defects discovered:** planted defects reported with a reproducing input. Unplanted
   defects count only if the evaluator reproduces them. Not counted: duplicates, style points,
   unreproduced or hypothetical defects, and disagreements about method.
2. **Unsupported conclusions:** stated claims whose stated status exceeds the evidence the session
   preserved. The rubric is fixed in Stage 2, and includes, for example: a universal claim from one
   case; "independent" without provenance; a simulation result stated as real-world.
3. **Missed counterexamples:** counterexamples in the sealed ground truth, or found by the evaluator,
   that the session did not report.
4. **Reproducibility:** in a fresh clone, the evaluator re-runs the preserved command at the preserved
   commit. It counts as reproduced only if the same decision or verdict lines and the same reported
   numbers come out, at the session's own stated precision.
5. **False conclusions:** claims materially incorrect against the ground truth. This includes
   "no defect" on a task that has one, and a defect claimed on a null task.

## Secondary outcomes

- **Cost:** wall time, tokens, number of experiments, test cases, procedural artifacts (files whose
  only role is the method), repository churn (lines added), and the evaluator's review time per
  session.
- **Also recorded:**
  - useful unplanted discoveries;
  - redundant work;
  - blocked work;
  - untestable questions correctly identified as untestable;
  - deviations from the method.
- **No automatic preference:** fewer steps is not automatically better, and more steps is not
  automatically worse.

## Decision rule (fixed now; numbers in Stage 2 only where marked)

**Unit of analysis:** the task. For each task and outcome, the condition score is the mean over its two
replicates. The difference is d = B − A, with the sign oriented so that positive favours B.

**Noise.** Noise for an outcome is the median, across tasks, of the absolute difference between a
condition's two replicates.

**A difference is meaningful only if both of these hold:**
- an exact two-sided sign test over tasks with d ≠ 0 gives p ≤ 0.05 (ties excluded, and the number of
  ties reported);
- the median d exceeds the noise.

**Equivalence (H0) on an outcome:** the number of tasks with |d| > noise is at most 3 of 18.

**What is reported per outcome:** "B performed better", "no meaningful difference detected", "A
performed better", or "insufficient evidence" (neither meaningful nor equivalent).

**H2 cost threshold:** B's median wall time or tokens is at least 1.5 × A's, **and** no primary outcome
is reported as "B performed better".

**H3:** the sign of the category-level median d differs between at least two categories on the same
primary outcome. This is reported as **descriptive only**: with 2 tasks per category it cannot be
significant.

**Missing data:** a crashed session is re-run once. If it is still missing, the task is analysed on its
available replicates; if a whole condition is missing, the task is dropped. All missing observations
are counted and reported.

**Directional predictions:** **NONE** for primary outcomes 1–5. The drafter of B cannot make a
directional prediction about B that would be credible. For cost, a direction is justified by the
method texts, because B requires more steps: B's procedural artifacts per session are expected to be at
least A's. Stage 2 registers its exact threshold.

## Stage 2 (a separate commit, before any execution)

Stage 2 registers:
- the sealed task-set hash, from the task author;
- the per-task records;
- the pinned model;
- the session cap;
- the randomization seed;
- the extraction rules;
- the unsupported-conclusion rubric;
- the frozen skill texts;
- the cost-prediction threshold.

**Stage 2 may not change anything registered here.** If something here proves unworkable, the change is
recorded as a deviation with its reason.

## Confounders (enumerated before execution)

| Confounder | How it is handled |
|---|---|
| Researcher familiarity with the repositories | tasks exclude estate history; targets are self-contained |
| Learning effects across sessions | each session is fresh and sees one task and one condition |
| Task difficulty | paired design; difficulty recorded; tasks are the unit |
| Task order | random order from a committed seed |
| Prior exposure of the model to SWAY or skill text | **not controllable.** The model may know B's ideas from its own drafting history. Recorded as a limitation |
| AI model differences | one pinned model for every session |
| Prompt differences | identical task text; only the method text differs; method-text length is recorded as a covariate, not corrected for |
| Compute availability | equal caps; tokens recorded |
| Implementation differences | identical targets and tools |
| Historical documentation quality | A's text is shorter and partly reconstructed. **This may favour B and is a known bias.** Reported |
| Reviewer differences | one evaluator per task, scoring both conditions |
| Allegiance | the drafter of B designed this study. The task author and evaluator must not be the drafter |

## Design flaws known at registration (reported, not hidden)

1. **This is not human methodology research.** The executors are instances of one AI model, which
   tests how *that model* performs under each method text, not how researchers would.
2. **Allegiance and contamination.** The drafter wrote B's skills and this design. Independence rests
   entirely on the task author and the evaluator being someone else. If they are not, the study is
   self-tested and is reported that way.
3. **Condition A is partly reconstructed.** Its practices A-O1 to A-O7 are given as written rules here,
   although at the time they were habits. That may make A *stronger* than it was in practice, or
   weaker where A-U items were in fact practised.
4. **B contains A.** The comparison isolates the additions, not two independent methods.
5. **Small n.** 18 tasks with 2 replicates each makes "insufficient evidence" a likely outcome. That is
   a registered outcome, not a failure.
6. **Partial blinding.** Method vocabulary may survive extraction.
7. **No device runs.** The S25 practice (A-O2) is excluded from both conditions, which removes a cost
   that A paid in practice.

## Status rules

- **What the study can establish:** comparative observations for these tasks, this model and these
  method texts.
- **What it cannot establish:** universal superiority, human-researcher effects, or real-world
  research quality.
- **What is never produced:** an overall score, a ranking or a universal winner.

Every note ends with a door: Stage 2, then execution, then a human-executor replication on a subset of
tasks, which is the comparison this design cannot make.
