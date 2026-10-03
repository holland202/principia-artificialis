# SWAY Amendment 2: experiment-first, and AI work that cannot vouch for itself

**Status:** Proposed 2026-10-03, not adopted until Chad Holland approves it. It is **not validated** as
better than SWAY plus Amendment 1; its prediction P6, below, is unrun. `METHOD_SWAY.md` before this
amendment: commit `322c6ae`, md5 `aae4d54fa2c92e6869085884b70c1960`.

**Provenance:** AI-assisted. Chad Holland supplied the experiment-first procedure. Claude (Anthropic,
Opus 5.5) mapped it against SWAY and Amendment 1 and drafted this text. Human review: line-by-line, by
Chad Holland, before adoption. Chad Holland is responsible for the adopted text.

## The adoption rule used (unchanged from Amendment 1)

An item is **ADOPTED** only if a real failure shows that it would have caught something the method as
written did not. Otherwise it stays a **DOOR**. Items the method already covers are mapped, not
re-adopted.

## What broke (failures lead)

| Incident | Where | What SWAY + Amendment 1 did not catch |
|---|---|---|
| Two Claude sessions ran the same challenge question within an hour. The later write-up first called them "designed independently by separate sessions" | sovereign-veritas: A/B branch `7fb1c48`/`8e31454`, V15 `eaacb55`, unmerged draft of PR #20 | Amendment 1 item 8 has replication levels, but nothing about whether two AI sessions count as independent |
| The independent reviewer of V14's bound did not finish. Its replacement was the same model attacking its own design | sovereign-veritas `docs/V14_CORRIDOR_RESULTS.md` | invariant 3 covers *systems* certifying themselves, not an AI's design agreeing with its own prediction |
| A proposal's text was credited to "the author" without evidence of who drafted it | sovereign-veritas V14 registration; corrected afterwards in `docs/V14_CORRIDOR_RESULTS.md` and `LINEAGE.md` (INDETERMINATE) | no rule says how to record who, or which model, produced an artifact, or how much human review it had |
| A cross-check accepted stale, replayed and derived-from-A evidence. Earlier tests had used only fresh and absent evidence | sovereign-veritas V12/V13 compared with the A/B experiment and V15 | no default case matrix for questions about evidence; the conditions that failed were not in the earlier designs |
| An outside AI's analysis stated figures about the repository that were stale or wrong (test counts, guard counts, "not implemented") | sovereign-veritas `docs/EXTERNAL_CRITIQUE_PERPLEXITY.md` | the explanation was taken in before the repository was checked; only checking it caught the errors |

## ADOPTED

10. **Behaviour questions are settled against the actual code, not by explanation.** When the
    question is how a mechanism in this estate behaves, it is settled by running the real repository
    code, or by reading the code and then running it. A reconstruction or a prose account is not
    enough. Every stand-in is named in the claim: a model, a fake backend, constructed inputs, a
    simulated environment. A result that rests on a stand-in has its empirical axis (Amendment 1
    item 6) recorded as `NOT RUN`.
11. **Default matrix for evidence questions.** When the question is whether a rule handles its
    evidence correctly, the registration covers, or states why it skips, each of:
    fresh → stale → unavailable → contradictory → derived from the same source → replayed.
    This is a default, not a requirement that every experiment use every row.
12. **AI work does not vouch for itself.** An AI system's design, code, interpretation or attack on
    its own work is not independent of that work.
    - When the same AI designed the test and predicted its result, the result is labelled
      **self-tested**.
    - An attack by the same AI is labelled as such, and it is weaker.
    - Two sessions of the same AI are not independent unless provenance shows it. Separate sessions
      alone show nothing.
    - This extends Amendment 1 item 8. Independent reproduction needs a different person, or a
      separately labelled reviewer that had not seen the build. Same-vendor models are labelled
      same-vendor.
13. **AI provenance is stated with the review level that actually happened.** Every artifact that AI
    materially helped produce states:
    - **the chain:** AI participation → human validation → human editing/curation → human
      responsibility;
    - **the model**, by name;
    - **one human review level:** line-by-line, outcome review, or direction only. The level is never
      rounded up.

    Human review of AI-assisted material is not validation of the underlying claim.

## Mapped, not re-adopted (already in SWAY or Amendment 1)

| Experiment-first step | Already covered by |
|---|---|
| Predict first; preregister if it will be relied on | Elevator: "written as a registered prediction before touching the sealed set" |
| Run and record raw output, commit, environment | invariant 1, invariant 6, build elevator (cold clone, md5) |
| Keep failures and refutations | invariant 2 |
| Anti-vacuity control, sabotage switch | Elevator; build rule 4; Amendment 1 item 2 (the guard must be reachable) |
| Simplest rival explanation | Amendment 1 item 5 (the simplest rival is a required arm) |
| "If a test cannot settle it, stop" | Amendment 1 item 2 (registered as untestable) and item 7 (`UNRESOLVED`) |
| Never upgrade a simulation into a real-world claim | Amendment 1 item 6 (three validity axes) and item 10 above |
| Results are appended, never rewritten | invariant 6; the repositories' append-only practice |

## Not adopted: the eight-word status list

The proposed list (observed / reproduced / supported / not supported / refuted / unknown / not tested /
simulation-only, "exactly one per claim") **conflicts** with vocabulary already in use:

- **"Reproduced"** already has a defined meaning in Amendment 1 item 8: the same specification,
  executed independently. Using it for "ran again" would blur re-run into reproduction, which is the
  error item 8 exists to prevent.
- **"Exactly one per claim"** contradicts Amendment 1 item 6, under which each claim carries three
  separate axes.
- **"Supported / not supported / refuted"** is a claim-verdict layer that already exists in code:
  `refutes_claim` in sovereign-veritas `sovereign_veritas/adapters/veritas_science.py`. There, NOT
  SUPPORTED is not REFUTED unless `refutes_claim` is true. SWAY's text does not yet state that
  distinction.

**Reconciliation instead of a new list:**
- the status ladder and `EXPLORATORY` for the note;
- Amendment 1 item 7's outcomes for each prediction;
- item 6's three axes for each claim, with `NOT RUN` on the empirical axis for model or
  constructed-input results;
- item 8's levels for replication;
- `SUPPORTED / NOT_SUPPORTED / REFUTED` for claim verdicts where an evidence adapter produces them.
  NOT_SUPPORTED is never reported as REFUTED.

## DOORS (proposed, not adopted: no incident yet)

| Proposal | Why it is a door |
|---|---|
| Output shape: "prediction, what happened, status, limits, next unrun test" | a reporting style; no result has gone wrong for lack of it |
| Preferring interactive artifacts (visualizations, manipulable models) as instruments | nothing has failed for want of one; kept for when a question needs one |

## Registered prediction about this amendment

- **P6, OPEN, unrun.** Over the next 5 registrations across the estate that involve an AI-designed
  test or a question about evidence, count two kinds of failure:
  - an AI-produced result described as independent without provenance showing it;
  - an evidence rule tested without stale, derived or replayed conditions and without a stated reason.

  Prediction: 0. One or more refutes the amendment for that purpose, and the refutation is kept.

Every note ends with a door. This one does too.
