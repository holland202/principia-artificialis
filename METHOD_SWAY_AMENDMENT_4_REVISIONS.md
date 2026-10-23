# SWAY Amendment 4: revisions before adoption (append-only)

The registration (`METHOD_SWAY_AMENDMENT_4.md`, `3400469`) is not edited. Changes made to the build before the
owner merges are recorded here, newest last.

## R1 and R2 (2026-10-22)

**Source:** a preliminary audit by ChatGPT (OpenAI; model version not recorded), relayed by Chad Holland on
2026-10-22. It has not yet been posted as a GitHub note. Claude (Anthropic, Opus 5.5) checked both points
against the text and made the changes. Human review level: direction only.

- **R1: C-HOLDOUT was too broad.** As written, its trigger ("anything is selected, tuned, trained or
  thresholded on data") could fire on studies where nothing chosen from the data is judged by it. The trigger now
  asks whether **the same evidence could be used both to choose something and to judge the claim**. A generator or
  harness change counts as choosing. C-HOLDOUT now says it does not apply to verification that chooses nothing
  from the evidence it judges.
  - *First use, the same day:* applied to DIFF-001 (sovereign-veritas), the revised rule showed that the
    registered long run would have re-judged smoke cases 0–2,999, which had shaped generator amendment A1. That
    run's amendment A5 now starts at case 3,010, before any output exists. This is an incident caught by the rule,
    as M18 asks for.
- **R2: C-DESIGN needed a boundary for deterministic tests.** A deterministic test supports existence and
  conformance claims on the inputs tested, never a rate, a reliability figure or a population claim. That
  sentence was added to C-DESIGN.

**Checks after R1–R2:** `method_lint.py` and its `--coverage`, `--selftest` and `--sabotage` modes, results in
the commit and the PR.
