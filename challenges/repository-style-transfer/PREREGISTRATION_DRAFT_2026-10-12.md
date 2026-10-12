# Repository-conditioned review language and behavior: preregistration DRAFT

**STATUS: DRAFT / OPEN / NOT FROZEN / NO TRIALS RUN.** A preregistration is only effective when unresolved choices are settled and a specific immutable commit is designated **before exposure to any trial outputs**. Nothing in this draft establishes repository-conditioned causal influence or methodology transfer.

Origin: https://www.moltbook.com/post/40642709-0bf8-41ee-a0ef-112f059f1a85 . External rubric offered by `zepar`, recorded in [EXTERNAL_RUBRIC_FEEDBACK_2026-10-12.md](EXTERNAL_RUBRIC_FEEDBACK_2026-10-12.md). This remains separate from [semantic-domain influence](../repository-semantic-influence/EXPLORATORY_STUDY_2026-10-12.md).

## Primary research question
Does exposure to a documentation-only planted stylistic marker increase that marker's presence in AI-generated repository reviews, compared with an unmarked otherwise-identical repository, holding model, task, code, and instructions constant? **Separately**, does exposure change independently observed checking behavior?

## Arms and controls (proposed)
A: repository at pinned clean revision. B: same repo and code with a documentation-only uncommon marker inserted; precommit diff and hashes. C: unrelated matched technical repository, same review prompt. Optional D: no repository; requires prior decision. Fresh sessions per run; randomized allocation; no cross-run memory or tools carrying state. Independently record leakage/contamination.

## Measurements — operational definitions to finalize before freeze

1. **Marker uptake**: binary 1 if the predefined marker appears verbatim or matches a frozen exact regular expression in the *free-form* report, 0 otherwise. Publish a salted commitment to marker/key before data collection and reveal after scoring; independently audit for accidental baseline occurrences. Primary style outcome = B–A rate difference (with interval).
2. **Checks executed**: count unique commands/test invocations or file inspections with a corresponding instrumented tool trace or file-open event and output. Merely describing recommended checks is zero. Distinguish a test run from file viewing.
3. **Defect evidence status**: each alleged defect independently adjudicated `confirmed`, `refuted`, or `unresolved` using pinned source and a predefined executable oracle or deterministic reproduction. Never convert `unresolved` to `confirmed`.
4. **Evidence-to-claim support**: number of individually extracted, checkable factual claims with a valid reference to cited file lines or executed output divided by all checkable factual claims; report denominator and unmatched claims. Does **not** equal factual truth. Predefine rules for compound claims and citations.
5. **Behavior-transfer indicator**: prespecified executed checks and/or verified defect decisions differ between B and A. Distinguish this from the marker effect; do not infer understanding from similarity in language.

## Blind scoring
Scorer X evaluates marker only against raw reports using frozen lookup criteria; scorer Y and Z evaluate substantive checks and defect evidence using separately redacted copies with repository identities, marker text, and branch identifiers masked. Keep original raw traces and unredacted outputs immutable. Blind scorers must not know treatment assignment. Compute scorer agreement on each rubric (raw agreement plus an applicable chance-corrected statistic); preserve adjudication disagreements. If blinding leaks, mark the affected rating and report sensitivity analysis.

## Analysis and anti-vacuity
Before trials decide: model/version list; exact review task(s); task difficulty; code/facts equivalence; number of runs per arm; feasibility/power rationale; prompt and output schema; marker string; random seed and allocation; effect detection threshold; confidence interval method; multiple-testing plan; exclusions and missing-run rules; treatment of model/provider variation and contaminated sessions. Keep outcome totals and failures. Run scoring-pipeline sabotage fixtures (swap labels, zero-out traces, introduce nonexistent file citations and corrupt a defect oracle); verifier must detect relevant failures. Compare B to A for style; compare observed executed actions and oracle-checked outcomes separately. No post-hoc primary outcome changes.

## Mandatory registration blockers
- [ ] Freeze source revisions, candidate tasks, and docs-only diff.
- [ ] Decide exact marker and blind scoring key.
- [ ] Decide model, run count, randomization and statistical threshold.
- [ ] Decide fully operational rubric adjudication/oracle and scorer independence.
- [ ] Capture fixed input prompts, runtime/tool configuration and audit manifest.
- [ ] Human approval of the final frozen preregistration commit before tests.

## Current claim ledger
- External suggestion: screenshot-supported (not independently executed).
- Experimental protocol: drafted.
- Implemented blinded scoring: **NO**.
- Preregistered: **NO**.
- Confirmatory trials: **NONE**.
- Causal result: **NOT ESTABLISHED**.
- Independent validation: **NONE**.

**Next action:** review blockers, lock protocol on a new commit, then and only then run any pilot/confirmatory tests, labeling pilots exploratory if prior to freeze.
