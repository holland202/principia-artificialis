---
name: "prereg-research-workflow"
description: "Chad's research-and-development workflow for his repos (sovereign-veritas, principia-artificialis, evidence-ledger etc.): prereg-first experiments, pinned outcomes, sabotage controls, failures-first results, provenance and attribution rules."
---

# Research and development workflow

This is how experiments and changes are run in Chad Holland's repositories. It sits inside SWAY (`principia-artificialis/METHOD_SWAY.md` and its amendments). The investigation step follows the `experiment-first` skill. Read the repo's `CLAUDE.md`, and any SWAY amendments, before starting.

## 1. Frame

- **The question.** State the observable question in one line. Read the relevant code and spec first ("what the code can express"), then decide whether running something can settle it. If nothing can, register it as untestable.
- **The design.** Map the question onto the real code path. Name every stand-in: model, fake backend, constructed inputs.
- **The simplest rival.** Name it, and run it as an arm.
- **Feasibility counts.** Print the counts the design depends on and commit them with the registration.
- **For evidence questions,** cover fresh → stale → unavailable → contradictory → derived from the same source → replayed, or say why a row is skipped.

## 2. Register first, in its own commit

- Write `docs/<ID>_PREREG.md` (or a Principia note). Include:
  - the scope;
  - the constants;
  - the case matrix;
  - derived expected values;
  - numbered predictions with exact pass criteria and tolerances;
  - the anti-vacuity control and how it can fire;
  - the limits;
  - provenance and credit;
  - the unrun next step.
- Commit it alone ("<ID> REGISTRATION: … (nothing built or run)"). When Chad asks for a freeze, merge it before any code exists.
- **A registration is never edited after this.** Errors found later are recorded in the results.

## 3. Build and run

- Import the real functions; don't copy them. The harness prints one HELD or REFUTED line per prediction, a `VERDICT n of m as registered` line, and a `DIGEST` (sha256 of canonical, rounded results).
- Add a `--sabotage` switch that disables the mechanism under test. The outcome must then differ (exit 1).
- Keep runs deterministic across platforms: seeded RNGs and rounded outputs, with no knife-edge thresholds.
- Commit the harness exactly as run, together with the raw output (`results/<id>/run.txt` and `results.json`). Then pin `RECORDED = (held tuple, digest)` in a separate step, so the harness exits 0 only on the recorded outcome.
- Never retune constants or predictions after seeing results. Disclose any change made after registration as a deviation.

## 4. Results document: failures lead

`docs/<ID>_RESULTS.md` opens with "What could have gone wrong, first":
- self-testing;
- model-derived versus real;
- registration errors;
- deviations;
- reviews that did not happen.

Then it gives:
- the raw output, pasted, not paraphrased;
- a prediction table with refutations kept;
- what the result shows and does not show, separating mathematical, implementation and empirical claims;
- candidate fixes, marked as proposals. Contract and format changes are Chad's decision.
- what is still open.

"8 of 8 as registered" is not "passed". Say so when the predictions were predictions of failure.

## 5. CI and merge

- Add CI steps:
  - the harness reproduces the recorded outcome (on the full OS and Python matrix when the result should be platform-independent);
  - `--sabotage` must exit 1;
  - challenger or protocol paths are exercised.
- Run the full test suite and `vacuity_lint` (pinned) before pushing.
- Merge with a merge commit, never squash, so the registration-before-run order stays in history.
- When Chad says "show me the diff first", don't commit. If a hook demands a commit, stash the work and say so.

## 6. Provenance, credit, external input

- **AI provenance:** AI participation → human validation → human editing/curation → human responsibility. Name the model, and state only the review level that happened: line-by-line, outcome review, or direction only.
- **Self-validation:** Claude's own design, code or attack is never independent validation. Label it self-tested. Two Claude sessions are not independent unless provenance shows it.
- **Credit only for specific, identifiable contributions.** External questions are credited as questions, with an explicit statement that this implies no endorsement or validation.
- **External critiques and quotes:**
  - Keep them verbatim in `docs/external/`, with the author named and the sha256 of the exact text received.
  - Check their factual claims row by row.
  - Record disagreements separately from their text.
  - Never reconstruct a quote from memory or paraphrase. A private message is paraphrased, not quoted, unless quoting is confirmed.
- **Influence claims** go in `docs/LINEAGE.md` as SUPPORTED, NOT SUPPORTED or INDETERMINATE, with evidence. Unknown authorship stays INDETERMINATE.
- **Corrections are appended and dated.** History, timestamps and tags are never rewritten. Duplicate or earlier work is preserved and referenced, by an archive tag if needed, not hidden.

## 7. Environment and handoff

- **The proxy:** in Claude's sandbox it blocks GraphQL, tag pushes and some API writes. Use REST for PRs. Hand tag pushes and anything that must run on the S25 to Chad as Termux commands, one at a time.
- **Labels:** results not run on the device are marked NOT VALIDATED on the S25. Model results are never described as real-vehicle or real-world results.
- **Reporting:** report what was done, with commit hashes, CI status, the digest and what remains open. No recap of steps.