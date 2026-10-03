# Method record: verbatim copies (manifest)

These files are **record**, not method. They are kept byte for byte so that what the method used to
say can be checked. The canonical method is [`METHOD.md`](../../METHOD.md), with
[`WORKFLOW.md`](../../WORKFLOW.md) and [`CONTROLS.md`](../../CONTROLS.md).
`scripts/method_lint.py` fails if any file below no longer matches its md5. A copy is never edited; a
correction is a new dated file.

| path | md5 | sha256 | what it is |
|---|---|---|---|
| `skills/experiment-first.SKILL.md` | `e5fa5a566fa9055f6293926c6db90dfc` | `1e580af26e19c1af85b318b391aa4e0e1a2f759d2891c47972a647068e07303c` | The experiment-first skill as synced on 2026-10-03, before Amendment 3. The md5 matches Condition B in the methodology-comparison Stage 1 (`aef769e`) |
| `skills/prereg-research-workflow.SKILL.md` | `0992bc29efb422d6eff751c972a0ef46` | `7da4aaf9d6d9af3f36f2ecc8b31e9faf309a6cd71e2202c649d6b81734d001a5` | The prereg-research-workflow skill as synced on 2026-10-03, before Amendment 3. The md5 matches Condition B in Stage 1 |
| `drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md` | `261ffe7597c093b0b6b92296b5fa1e11` | `3a5ac30ef7301cc17ce4243be5d0fdeaed85d4d9471e01853a5825f8f08c72fd` | The SWAY Amendment 2 draft of 2026-10-03, never adopted separately. Its items 10–13 were adopted through Amendment 3 (decision D11). **Its line "Human review: line-by-line, by Chad Holland, before adoption" describes a review that was planned and did not happen.** The review that happened was direction only |
| `external/2026-10-03_chad-holland_chatgpt_refactoring-plan.txt` | `9f9da2abe8bb60d20ff0d89e87587ed4` | `50928b984e791c9a16a45dace0d9149072c3c9a4e703cc7c1af560961206ef86` | The refactoring plan Chad Holland sent on 2026-10-03, exactly as received (no trailing newline). It holds his directions (Part A) and ChatGPT's suggestions C1–C10 (Part B; OpenAI, model version not recorded). ChatGPT's suggestions are evaluated, not adopted wholesale, in Amendment 3 decision D12. Preserving them implies no endorsement by ChatGPT or OpenAI |

**Provenance of this record:** Claude (Anthropic, Opus 5.5) copied the files on 2026-10-03 and checked
each md5 against its source: the synced skill files, the stashed draft, and the received attachment.
Human review: direction only. Responsibility: Chad Holland.
