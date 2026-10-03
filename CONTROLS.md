# CONTROLS: what a triggered control requires

This file is canonical for the C- controls. A control is switched on by its row in METHOD.md's trigger
table (§3). The row is answered in every registration, and a blank row counts as yes (M16). Only the
controls whose triggers fire apply; the M rules always apply.

- **C-FEAS** · MUST · **Feasibility counts.**
  - Before the registration is committed, a script prints the counts the design depends on: how many
    units qualify, and how guessable each answer is without the mechanism.
  - The counts are committed with the registration.
  - It prints counts only: no content and no truth values.

  Example: veritas-companion `experiments/C006b_feasibility/feasibility.py`.
  *Source: Amendment 1 item 1 (C006: 0 of 2,200 HDFS blocks had ≥ 3 lines).*
- **C-NOISE** · MUST · **Measure same-input noise first.** Run the same input at least 3 times before
  choosing any bound. A bound smaller than the observed spread is registered as unresolvable at that n.
  *Source: Amendment 1 item 4 (C006b: one prompt, run 3 times at temperature 0, scored 13–15 of 20).*
- **C-STAT** · MUST · **Error control that matches the stopping rule.** A claim estimated from samples
  is decided by a test whose guarantee holds under the stopping rule actually used:
  - a registered fixed-horizon test (exact where possible) when the sample size and the analysis are
    fixed in advance and nobody looks early;
  - an anytime-valid e-process with E ≥ 20 (α = 0.05) when the data are inspected as they arrive, or
    stopping depends on them.

  Further requirements:
  - Report the e-value or the exact p-value, never just "significant".
  - Combine e-values only by a rule whose validity conditions are stated. Independent e-values may be
    multiplied. A different day, device or dataset does not by itself make a stream independent.
  - A deterministic claim (same input → same output) is not a sample and gets no e-value. Its
    promotion evidence is M2, M3, W4's pinned outcome and M11's fresh run.

  **Reference implementation:** `scripts/eprocess.py` (md5 `63cb70b866e1b95faa150316b12dd76a`), a
  betting e-process for H0: success rate ≤ p0. Its validity proof and sabotage control are in
  METHOD_SWAY.md. **The e-process is AVAILABLE — NOT USED SINCE ADOPTION**: 0 uses in the estate as of
  2026-10-03.
  *Source: SWAY "anytime-valid evidence"; Amendment 3 D3 (F3).*
- **C-EVID** · MUST · **Evidence ladder.** Cover each of these, or state why it is skipped: fresh →
  stale → unavailable → contradictory → derived from the same source → replayed.
  *Source: Amendment 2 item 11. sovereign-veritas V12 and V13 tested only fresh and absent evidence;
  the A/B experiment and V15 then found stale, derived and replayed evidence accepted.*
- **C-INDEP** · MUST · **Independence and replication.**
  - Label the highest replication level actually reached, and who reached it (vocabulary: replication
    level).
  - Two implementations by one author are a re-run of the specification, not a replication.
  - Separate sessions of one AI show nothing about independence.
  - A reviewer from the same vendor is labelled same-vendor.

  *Source: Amendment 1 item 8 (sovereign-veritas issue #4 B10); Amendment 2 item 12; M10.*
- **C-EXT** · MUST · **Outside material.**
  - Outside text is kept verbatim, in `docs/external/` or the repository's record, with its author
    named and the sha256 of the exact text received.
  - Its factual claims are checked one by one, and disagreements are written separately from it.
  - A quote is never reconstructed from memory. A private message is paraphrased, and labelled as a
    paraphrase, unless quoting is confirmed.
  - An outside question is credited as a question, with no implied endorsement or validation.
  - Influence claims go in `LINEAGE.md` with their evidence and a lineage status. Unknown authorship
    stays `INDETERMINATE`.

  *Source: prereg skill §6 (the Perplexity record; Amos Tipton's question; the "Dependent Evidence"
  drafter).*
- **C-DEVICE** · MUST · **Device claims.**
  - A claim about a device or platform needs a run on it, with the output pasted verbatim.
  - File identity is checked by md5 after every transfer between machines.
  - On the S25 under Termux, `/tmp` is not writable (use `$HOME`), and `set +H` comes before pasting
    text that contains `!`.

  *Source: SWAY build elevator; CLAUDE.md environment note; Amendment 3 D4.*
- **C-BUILD** · MUST · **Fail-closed verdict code.**
  - **Missing means deny.** Absent, empty, None or malformed input returns DENY or UNVERIFIED, never a
    skip. Validation runs eagerly: a check inside a generator does not run until the first iteration,
    and never runs on empty input.
  - **Vetoes never vote.** A veto is a separate fail-closed condition, never a value inside an
    aggregate. When it fires, the verdict is DENY or UNVERIFIED, whatever the other signals say.
  - M3, M5 and M10 apply to all verdict code.

  *Source: SWAY build rules 1–2 (`eprocess.py`'s generator guard; FIX-6, where 69.2 °C CRITICAL was
  outvoted to ALLOW).*
- **C-EXPLORE** · MUST · **Exploration is disclosed.**
  - Exploratory moves that feed a claim are logged, one line each, in the repository's append-only
    `FORKS.md`: date, fork id, what was tried, code identity, data identity, environment, observation,
    `EXPLORATORY`, and the outcome.
  - A promoted claim states how many forks preceded it. That is provenance, not a statistical
    correction.
  - If outputs on the registered cases were seen before registration, the prediction is a
    retrodiction and is labelled so. Confirmation then comes from fresh evidence (M11).

  **Ledger use since adoption:** 2 entries (F-001 and F-002), both for method amendments, none for a
  research claim. *Source: SWAY "Damper"; invariants 4 and 5.*
- **C-DISCOVER** · MAY · **The discovery loop.**
  - **What exploration allows:** anything except stating a result as true and touching sealed data.
    Peek freely; change the metric or the question; import mathematics from any field; generate
    hypotheses in bulk with several models, credited by name; run crude, fast experiments; follow
    anomalies.
  - **The loop:**
    1. Sprout 10–50 candidates, at least 20% of them from a deliberately foreign domain.
    2. Have a critic name the cheapest experiment that could kill each one, and run the cheapest first.
    3. Evolve the survivors that can be scored as programs, FunSearch-style, after first giving the
       evaluator its own anti-vacuity control.
    4. Crystallize a survivor into a registered claim (M2).

  **AVAILABLE — NOT USED SINCE ADOPTION:** no recorded use between 2026-09-22 and 2026-10-03. SWAY's
  P1–P4, which concern this loop, stay open, and cannot be measured until it is used.
  *Source: SWAY "Canopy" and "The AI discovery loop".*
- **C-METHCOMP** · MUST · **Methodology comparison protocol.**
  - A study that compares methods follows its own registered protocol:
    `docs/METHODOLOGY_COMPARISON_PREREG.md` (Stage 1, `aef769e`, on branch
    `methodology-comparison-registration`) and its Stage 2 specification, which is parked at revision 4.
  - It is specific to that experiment and never becomes general procedure.
  - **Status: UNRUN — independent task construction and scoring not available.**

  *Source: Stage 1; Amendment 3 D13.*

## Doors (not adopted)

These are kept as doors and are not rules. Each becomes one only through M18.
- METHOD_SWAY.md "Doors": property-based testing, mutation testing, coverage-guided fuzzing, symbolic
  contract checking, signed provenance, hash-pinned dependencies.
- Amendment 1 "DOORS": a degrees-of-freedom ledger, expected information gain, an artifact ladder, a
  claim ledger per repository, and the discovery-versus-confirmation question.
- The Amendment 2 draft's "DOORS": a fixed output shape, and interactive artifacts as instruments.
- Amendment 3 D12: a high-consequence trigger, and a fuller methodology lint.
