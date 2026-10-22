# Start Here

> **Inventory correction — 2026-10-16.** At repository revision
> [`05078579b674f8a93cc56de4eba3d5fa6511d159`](https://github.com/holland202/principia-artificialis/tree/05078579b674f8a93cc56de4eba3d5fa6511d159),
> 92 files match the existing index generator's discovery rules. The committed
> index lists 88; matching files 068–071 are absent. These are file-discovery
> counts, not counts of validated research findings; the matched set includes
> a handoff document. The matched set contains 22 duplicated note numbers.
> There are 27 reference-script files; this inventory did not execute them.
> Historical statistics below are preserved and are not a current census.
>
> Inventory basis: the complete Git tree at that revision, using
> `research_notes/note[0-9][0-9][0-9]_*.md`,
> `research_notes/[0-9][0-9][0-9]_*.md`, and
> `notes/[0-9][0-9][0-9]_*.md`, compared with the committed index links.
> `notes/note048_grok_contribution_manifesto.md` falls outside these patterns;
> inclusion policy and index regeneration remain separate review items.
>
> Correction provenance (W9 / M13): ChatGPT (OpenAI; model identifier not
> available in this session) assisted with inventory and drafting → human
> validation: not performed → human editing/curation: scope and wording direction
> by Chad Holland → human responsibility: Chad Holland. Human review level:
> direction only. This correction is not independent research validation.

This is **Principia-Artificialis**: an open research program on the
mathematics of artificial thought — information geometry, topology,
dynamical systems, and thermodynamics applied to AI inference. It is a
**notes program**, not a library and not a product. The primary artifact is
a numbered series of research notes, each with registered predictions and,
where possible, runnable reference code.

Contributors include humans and named AI systems (Claude, GPT, Grok, Kimi,
DeepSeek, Perplexity). AI contributions are credited by model name in each
note's header, deliberately.

## The method, in one paragraph

Claims are stated so they can be precisely wrong. Predictions are
registered and numbered (P1, P2, …) **before** running anything. Every
instrument carries an anti-vacuity control — it must be shown able to
return null, because a gate you have never seen fail is not evidence that
anything passed. When a registered claim fails, it is kept, marked
refuted, and explained; several notes are marked REFUTED on purpose.
Numbers in prose are pasted from code output, never paraphrased. Every
note ends with at least one prediction left unrun.

The canonical research method is [METHOD.md](METHOD.md), with
[WORKFLOW.md](WORKFLOW.md) and [CONTROLS.md](CONTROLS.md).
[NOTE_TEMPLATE.md](NOTE_TEMPLATE.md) is the contribution template.
*Superseded wording, preserved:* "The full spec is `NOTE_TEMPLATE.md`."
The status labels
(`Speculative` → `Draft` → `Draft, verified reference code` → `Verified`,
plus `REFUTED (kept)`) are honest by construction — a `Speculative` label
is a valid contribution, not an apology.

## Where to start reading

- **`NOTES_INDEX.md`** — the generated index of files matching its discovery rules.
  Historical count, preserved: 73 notes (previously described as "currently 73 notes").
  See the dated inventory correction above for the pinned comparison. Generation is
  not automatic freshness: matching-file changes require regeneration, and excluded
  files require separate review. The command is `python scripts/make_index.py`;
  it was not run for this correction.
  ⚡ marks numbers claimed by more than one note — collisions are
  displayed, not hidden. ⚠ marks a registered claim that failed and was
  kept. Those marks are assets, not defects.
- **`research_notes/note044_circularity_test.md`** — the methodology note:
  why a benchmark that validates itself carries no evidence.
- **`research_notes/note052_verification_that_cannot_fail.md`** — the
  method applied to this estate's own code, refutations included.
- **`WHITEPAPER.md`** and `whitepapers/` — longer syntheses.

## How to run things

```bash
make synthetic     # run all synthetic demos (scripts/run_all_notes.py)
make report        # show results/last_run_report.json
python scripts/make_index.py            # regenerate NOTES_INDEX.md
python sovereign_core/test_sovereign.py # governance suite (expect 33/33)
```

Reference code convention: `scripts/noteNNN_reference.py`,
dependency-light (NumPy-tier), printing every number that appears in the
matching note.

## Honest state of the repository

Two filename conventions are live (`NNN_*.md` and `noteNNN_*.md`); the
index matches both. Some files in `research_notes/` match neither and are
invisible to the index — a known, recorded defect. The note graph is
currently hub-and-spoke (the index links everything; few notes link each
other laterally); adding real cross-links is the highest-value structural
improvement available. If you find a verification script here that cannot
fail, that is note052's subject — file an issue.

*Vincit Omnia Veritas.*
