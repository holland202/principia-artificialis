# SWAY door: machine-checked proofs as an evidence level

**Status:** DOOR, 2026-11-26. **Not adopted, and not a rule.** Under M18, a rule is adopted only after a real
failure shows it would have caught something the method as written did not. No such failure has been recorded in
this program, so this file only fixes what the rule would say and what would trigger it. METHOD.md, WORKFLOW.md and
CONTROLS.md are unchanged.

**Provenance (M13):** AI participation → human validation → human editing/curation → human responsibility.
- **AI participation:** Claude (Anthropic, Opus 5.5) drafted this from the owner's request to bring the Riemann
  Hypothesis work into SWAY.
- **Human validation:** direction only. Chad Holland agreed to the proposal in chat on 2026-11-26 and has not read
  this text.
- **Human editing/curation:** none.
- **Responsibility:** Chad Holland.

## Why this, and not the theorem

The Riemann Hypothesis is a statement about the zeros of one function. It gives SWAY no step, check or rule, and
citing it inside the method would add a name that never executes. What SWAY can use is how the 2026-11-20 proof was
established: a proof of about 17 million lines, checked by a proof assistant (Lean), not by human reading. SWAY's
vocabulary has no level for a claim whose proof a machine has checked. Its highest replication level is
*generalization*, which is about data and tasks, not about deduction.

## The rule, if a trigger is met

A new value, **FORMALLY VERIFIED**, in the vocabulary map (§4), for a mathematical claim:
1. It applies only when a proof assistant (Lean, Coq/Rocq, Isabelle, or similar) accepts a proof of the claim. The
   record names the tool, its version, the library versions and a commit or hash, and gives the command that
   re-checks it.
2. **It covers the formal statement only.** The record quotes the statement as written in the proof assistant. Any
   prose or note that restates it carries its own label (usually SELF-TESTED or VERIFIED FROM SOURCE) until someone
   other than the author has checked that the formal statement says what the prose says. The translation between
   the two is where errors hide.
3. **Assumptions are listed.** Every axiom, `sorry`, `admit` or unproved import is named. Any `sorry` or `admit`
   means the label does not apply.
4. It says nothing about running code, models or measurements. An empirical claim never carries this label, even
   when a formalized lemma stands behind it.
5. **The anti-vacuity control (M3):** a deliberately false variant of the statement must be *rejected* by the same
   tool and setup, recorded beside the accepted proof.

## Triggers that would justify adoption (M18)

Any one of these, recorded as an incident:
- A note in this program states a mathematical claim as proved, and the claim later turns out false or narrower
  than stated, in a way a formal statement would have exposed.
- A claim taken from outside material is presented as "formally proved" while its formal statement says something
  different from the prose. This is the translation gap in rule 2.
- The program itself produces a proof-assistant artifact, and the current vocabulary cannot label it honestly.

## Open questions (doors within the door)

- Q1: Is a separate *statement-match* review (rule 2) a replication level in its own right, or part of C-INDEP?
- Q2: Should a formally verified lemma used inside an empirical note change that note's label at all? Rule 4 says
  no, and that position is untested.
- Q3: Which Principia notes already state mathematical claims that a proof assistant could check cheaply? Candidates
  are the small identities in the reference scripts. That would be the first test of whether this level is worth
  having.
