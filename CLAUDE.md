# CLAUDE.md — Principia-Artificialis

Persistent context for Claude Code and any other agent working in this repo.
Read this before touching anything.

**Motto:** Vincit Omnia Veritas. **Prime directive:** trust the files, not the
summary of the files — including not trusting this one. Verify before you act.

---

## What this repo is

An open research program on the mathematics of artificial thought: information
geometry, topology, dynamical systems, and thermodynamics applied to AI
inference. It is a **notes program**, not a library. The primary artifact is a
numbered series of research notes, each with registered predictions and, where
possible, runnable reference code.

Contributors include humans and named AI systems (Claude, ChatGPT, Grok, Kimi,
Perplexity). AI contributions are credited by model name in the note
header. This is deliberate — do not strip AI attribution.

**What it is not:** a product, a framework, or a proof. Notes carry honest
status labels and several are marked REFUTED and kept on purpose.

---

## The method (binding — this governs every edit)

The canonical method is [METHOD.md](METHOD.md), with [WORKFLOW.md](WORKFLOW.md) and
[CONTROLS.md](CONTROLS.md): SWAY, consolidated by Amendment 3 on 2026-10-03. Read METHOD.md before any
edit that registers, runs or claims something.

The table below is a verbatim excerpt of METHOD.md's index, and `python scripts/method_lint.py` checks
it. The definitions, their sources and the vocabulary map (status labels included) are in METHOD.md.
Where this file and METHOD.md disagree, METHOD.md governs. The seven rules this section used to list
are M1, M2, M3, M8, M6, M15 and M8 there.

<!-- excerpt: METHOD.md#index -->
| ID | Force | Rule |
|---|---|---|
| M1 | MUST | Claims can be precisely wrong |
| M2 | MUST | Register before observing |
| M3 | MUST | Anti-vacuity: the instrument can say the other thing |
| M4 | MUST | Real code, named stand-ins |
| M5 | MUST | Exact, deterministic verdicts |
| M6 | MUST | Numbers come from code |
| M7 | MUST | Honest labels |
| M8 | MUST | Failures lead and are kept |
| M9 | MUST | Observation before interpretation |
| M10 | MUST | Nothing certifies itself |
| M11 | MUST | Confirmation is fresh |
| M12 | MUST | The record is append-only |
| M13 | MUST | AI provenance, with the review that happened |
| M14 | MUST | The simplest rival is an arm |
| M15 | MUST | Every line of inquiry ends with a door |
| M16 | MUST | Triggered controls are on unless answered |
| M17 | MUST | One definition per rule |
| M18 | MUST | Change control |
| W1 | MUST | Frame the question |
| W2 | MUST | Register |
| W3 | SHOULD | Design the smallest discriminating instrument |
| W4 | MUST | Build and run |
| W5 | SHOULD | Attack |
| W6 | MUST | Write the results |
| W7 | SHOULD | CI, commit and merge |
| W8 | MUST | Close a build (DONE) |
| W9 | MUST | Record edits |
| C-FEAS | MUST | Feasibility counts |
| C-NOISE | MUST | Measure same-input noise first |
| C-STAT | MUST | Error control that matches the stopping rule |
| C-EVID | MUST | Evidence ladder |
| C-INDEP | MUST | Independence and replication |
| C-EXT | MUST | Outside material |
| C-DEVICE | MUST | Device claims |
| C-BUILD | MUST | Fail-closed verdict code |
| C-EXPLORE | MUST | Exploration is disclosed |
| C-DISCOVER | MAY | The discovery loop |
| C-METHCOMP | MUST | Methodology comparison protocol |
<!-- /excerpt -->

---

## Directory map

| Path | Contents | Notes |
|---|---|---|
| `research_notes/` | 78 `.md` files — the note series | **Canonical home for all notes** |
| `notes/` | 2 stray `.md` files | Colliding duplicates — see Known defects |
| `scripts/` | 29 files: `noteNNN_reference.py`, figure generators, `make_index.py` | One reference script per note |
| `whitepapers/` | 8 longer writeups | |
| `sovereign_core/` | Governance engine + `test_sovereign.py` | 33/33 deterministic on device |
| `experiments/`, `simulations/` | Experiment code | |
| `figures/` | 49 generated images | Regenerate via `scripts/generate_*.py` |
| `results/` | `last_run_report.json` | Written by `make synthetic` |
| `formal/`, `references/`, `discussions/`, `datasets/`, `data/` | Supporting material | |

Governing documents at root: `NOTE_TEMPLATE.md`, `NOTES_INDEX.md`,
`DISCUSSION_NORMS.md`, `DRIFT_LEDGER.md`, `ROADMAP.md`, `WHITEPAPER.md`,
`CONTRIBUTING.md`.

---

## Naming conventions

Two conventions are in use and both are live:

- `NNN_short_title.md` — 45 files (earlier series)
- `noteNNN_short_title.md` — 24 files (later series)

`scripts/make_index.py` matches both patterns and indexes **69 notes**. There
are **78 `.md` files in `research_notes/`**, so roughly 9 files match neither
pattern and are invisible to the index. Before adding a note, match one of the
two patterns exactly or it will not appear in `NOTES_INDEX.md`.

Reference code convention: `scripts/noteNNN_reference.py`, dependency-light
(NumPy-tier), printing every number that appears in the note.

---

## Known defects — read before you "fix" anything

These are recorded, not hidden. Do not paper over them.

1. **Number collisions are real and intentional to display.** `NOTES_INDEX.md`
   reports 20 numbers claimed by multiple notes, marked ⚡. Collisions are
   *shown*, not resolved by silent renumbering. Example: `#041` is claimed by
   both `041_retrocausal_self_consistency.md` and
   `note041_persistent_homology.md`.

2. **`notes/` duplicates numbers already used in `research_notes/`.**
   - `notes/028_thought_tensor_category_morphism.md` vs
     `research_notes/028_categorical_quantum_gravity_thought.md`
   - `notes/note048_grok_contribution_manifesto.md` vs
     `research_notes/note048_the_governor_is_the_dynamics.md`
   Different titles, same numbers. `notes/` is a stray directory. Consolidating
   it into `research_notes/` is a real cleanup task — but it changes note
   numbering, so **ask before doing it**.

3. **`START_HERE.md` is wrong.** It is an SECP deployment guide that tells the
   reader "All files are in `/mnt/user-data/outputs/`" — an AI sandbox path that
   exists on no reader's machine. It does not introduce the notes program at
   all. The file named START_HERE is currently the worst entry point in the
   repo. Rewriting it is high value.

4. **The graph is a star, not a network.** Across 78 notes there are **4
   `[[wikilinks]]` total**; 76 notes have zero outgoing links. `NOTES_INDEX.md`
   links out to everything, so the topology is one hub with 78 spokes and
   almost no lateral edges. Opening this vault in Obsidian today produces a
   scatter plus an orphan ring. Adding real cross-links is the single highest-
   value structural improvement available, and the 20 ⚡ collisions are the
   obvious first candidates — notes that collide on a number are usually
   topically adjacent.

---

## House rules for agents

- **Ask before restructuring.** Renumbering, merging directories, or bulk
  renaming changes the note series identity. Propose, don't perform.
- **Never edit a note to make a claim look better (M8).** If a registered prediction
  failed, the failure stays and gets explained.
- **Never delete a refuted note (M8).** `⚠` in the index marks kept failures. That
  mark is an asset.
- **Do not hand-edit `NOTES_INDEX.md`.** It is auto-generated. Edit notes, then
  re-run `python scripts/make_index.py`.
- **Preserve `[[wikilinks]]` and existing markdown links** on any edit.
- **Credit contributors, including AIs, by model name (M13).**
- **Do not present a reading of a file as a verified fact (M6).** Run it, paste the
  output, then claim it.
- **Do not add a claim to a note without the code that prints its numbers (M6).**
  If there is no code yet, label the note `Speculative` and describe the
  experiment someone else could build. That is a valid contribution.
- **One command at a time** when handing commands to the operator; this repo is
  driven from Termux on an Android device.

---

## Commands

```bash
make synthetic              # run all synthetic demos via scripts/run_all_notes.py
make real                   # synthetic, then attempt real model eval (needs GPU/transformers)
make report                 # cat results/last_run_report.json
make clean                  # remove report + __pycache__
python scripts/make_index.py    # regenerate NOTES_INDEX.md after editing notes
python sovereign_core/test_sovereign.py   # governance suite (expect 33/33)
```

Environment note (see CONTROLS.md C-DEVICE): this repo is developed on a Samsung Galaxy S25 Ultra under
Termux (aarch64, Python 3.14). `set +H` before pasting anything containing `!`
or markdown image syntax. `/tmp` is not writable — use `$HOME`.

---

## Adding a note — checklist

Copy `NOTE_TEMPLATE.md`. Then, before opening a PR:

- [ ] filename matches `NNN_*.md` or `noteNNN_*.md` exactly
- [ ] status label is honest (M7)
- [ ] claims registered and numbered (P1, P2, …) (M2)
- [ ] trigger table answered, every row (M16)
- [ ] anti-vacuity control present — the instrument can return null (M3)
- [ ] any refuted claim kept and marked (M8)
- [ ] every number in the prose matches `scripts/noteNNN_reference.py` output (M6)
- [ ] at least one open prediction left unrun (M15)
- [ ] at least one outgoing `[[wikilink]]` to a related note (no orphans)
- [ ] credit given, including to AI contributors (M13)
- [ ] `python scripts/make_index.py` re-run and the note appears
