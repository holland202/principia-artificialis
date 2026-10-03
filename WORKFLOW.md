# WORKFLOW: how a piece of research or a build is run

This file is canonical for the W rules. It uses the M rules in [METHOD.md](METHOD.md) and the controls
in [CONTROLS.md](CONTROLS.md), and does not restate them. The force words have the meaning METHOD.md
gives them.

There are two paths:
- **Claims about behaviour or measurements**, in experiments and builds: W1–W8.
- **Record edits**, in documentation, attribution, lineage and corrections: W9 only.

- **W1** · MUST · **Frame the question.**
  - State it in one line, observable, and separate from the interpretation it might support.
  - Read the code and specification it touches before deciding whether running something can settle
    it.
  - If nothing can, register it as untestable (outcome `NOT RUN` or `UNRESOLVED`, with the reason) and
    stop.

  *Source: experiment-first step 1; prereg skill §1; Amendment 1 items 2 and 7.*
- **W2** · MUST · **Register.** The registration is `docs/<ID>_PREREG.md`, or in Principia a note made
  from NOTE_TEMPLATE.md. It holds:
  - the question, the scope and the constants;
  - the case matrix, with derived expected values;
  - numbered predictions (M2, M5);
  - the simplest rival (M14);
  - the anti-vacuity control, and how it fires (M3);
  - the stand-ins (M4);
  - the answered trigger table (M16), and the controls it switches on;
  - the limits;
  - provenance and credit (M13);
  - the next unrun test (M15);
  - the commit of METHOD.md it follows.

  It is committed alone, with a subject such as "<ID> REGISTRATION: … (nothing built or run)". When
  Chad Holland asks for a freeze, it is merged before any code exists.
  *Source: prereg skill §2; NOTE_TEMPLATE.md.*
- **W3** · SHOULD · **Design the smallest discriminating instrument.** Isolate the question on the real
  code path, change one condition at a time, and include boundary and adversarial cases.
  *Source: experiment-first steps 2–3.*
- **W4** · MUST · **Build and run.**
  - The harness imports the real functions.
  - It prints one outcome per prediction (vocabulary: prediction outcome), a
    `VERDICT n of m as registered` line, and a `DIGEST`: the sha256 of the canonical, rounded results.
  - It has the sabotage switch of M3.
  - It is committed exactly as run, together with its raw output (`results/<id>/`).
  - A published deterministic outcome is then pinned, as `RECORDED = (outcomes, digest)`, in a
    separate commit, so that the harness exits 0 only on the recorded outcome.

  *Source: prereg skill §3; experiment-first step 5.*
- **W5** · SHOULD · **Attack.** After the run, try counterexamples, malformed inputs and boundary cases,
  and ask which assumption would have to break for the conclusion to be wrong. An attack by the author
  is labelled self-tested (M10). *Source: experiment-first step 8.*
- **W6** · MUST · **Write the results.** `docs/<ID>_RESULTS.md`, or the note, opens with what could have
  gone wrong (M8):
  - self-testing;
  - model-derived results versus real ones;
  - registration errors;
  - deviations;
  - reviews that did not happen.

  Then it gives:
  - the raw output, pasted;
  - the prediction table, with refutations kept;
  - observation before interpretation (M9);
  - what the result shows and does not show, by validity axis (M7);
  - candidate fixes, marked as proposals. Contract and format changes are Chad Holland's decision;
  - what stays open (M15).

  The summary says "n of m as registered", never "passed", and says so when the predictions were
  predictions of failure. *Source: prereg skill §4; experiment-first steps 6 and 10.*
- **W7** · SHOULD · **CI, commit and merge.**
  - CI reproduces the recorded outcome, across the OS and Python matrix when the result should not
    depend on the platform.
  - CI runs the sabotage switch, expecting exit 1, and exercises challenger or protocol paths.
  - Before pushing, the full test suite and the pinned `vacuity_lint` are run.
  - Commits stage files by name, never with `-A`.
  - Merges use a merge commit (M12).

  *Source: prereg skill §5; SWAY build elevator.*
- **W8** · MUST · **Close a build (DONE).** A build is DONE when it works for a written scope:
  - a one- or two-sentence scope statement;
  - its gate proven both ways (M3);
  - a cold clone of the pushed commit reproduces the gate result without untracked local state;
  - no known defect inside the scope, with the limits outside it listed;
  - its frozen identity (commit SHA and file md5) recorded next to the word DONE.

  Doors are listed separately and never block DONE. Reopening needs one written reason:
  - a defect inside the scope;
  - a deliberate scope change, which is a new build (the old DONE stays true for the old scope);
  - a dependency or platform change that breaks the gate.

  "It could be better" is a door, not a reason to reopen. Research does not close: a claim is settled
  (promoted or refuted), and the inquiry ends with a door (M15).
  *Source: SWAY "When a build is DONE" and build elevator.*
- **W9** · MUST · **Record edits.**
  - Edits to documentation, attribution, lineage and corrections are not experiments, and need no
    registration.
  - They are append-only (M12) and carry provenance (M13).
  - They follow C-EXT when they touch outside material.
  - They are shown as a diff before commit whenever the owner asks.

  *Source: Amendment 3 D8.*

**Repository-specific additions** live with the repository, not here. Examples: Principia's
note-numbering and `NOTES_INDEX.md` rules in CLAUDE.md, and sovereign-veritas's challenge protocol in
its `CHALLENGE.md`. Where one of them restates a rule, it cites the ID.
