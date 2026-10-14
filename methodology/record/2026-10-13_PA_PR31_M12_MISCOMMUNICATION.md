# PA PR #31 — M12 merge-method deviation and communication clarification

**Date recorded:** 2026-10-13  
**Record status:** Documentation-only correction (W9); no methodology amendment or experimental result  
**Incident:** [PA PR #31](https://github.com/holland202/principia-artificialis/pull/31), Moltbook correspondence index, merged as squash commit `2f3ada9e6cd5fbc63525114d9d50d106edff3b54`.

## Observation

PA's adopted [METHOD.md](../../METHOD.md) M12 and [WORKFLOW.md](../../WORKFLOW.md) W7 require **merge commits**, preserving the ordered research-document history. PR #31 was instead squash-merged via the GitHub connector by ChatGPT, which is a deviation from the repository method. The published content and historical Git objects are left as they exist; no history rewrite, false merge reconstruction, or replacement chronology is attempted.

## Classification and responsibility

**Owner's requested label: miscommunication on my part.** Chad Holland characterized the merge-method misunderstanding as a miscommunication on his part. This wording records the owner's own characterization, **not** a technical finding that the user caused GitHub's choice of merge strategy.

**Operational action:** ChatGPT selected `squash` rather than checking and following the existing M12 merge-commit requirement. This selection was the immediate procedural cause of the deviation, regardless of communication ambiguity.

## Disposition

- **Deviation recorded; not repaired retroactively.** The squash merge remains in GitHub history as performed.
- **No new rule is needed.** M12 and W7 already specify the required behavior.
- For future PA research merges, consult M12/W7 and use the required **merge commit** rather than squash or rebase.
- Nothing in this record changes PA's adopted canonical methodology or reports the Moltbook correspondence as independently validated research.

**Prepared by:** ChatGPT (OpenAI GPT-6) from GitHub PR state and the owner's requested classification.  
**Human review level:** Direction only; no line-by-line review claimed.  
**Human responsibility:** Chad Holland.
