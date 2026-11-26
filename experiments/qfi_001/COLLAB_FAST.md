# FAST-1: a faster way for Claude and ChatGPT to work on QFI-001

**Status:** in force on QFI-001 from 2026-11-25, on Chad Holland's direction (live chat, paraphrased: make the
Claude–ChatGPT exchange faster and more efficient). This is a pilot, and other lines keep their own rules until they
move over. FAST-1 changes **how the two AIs talk**. It changes no rule of [METHOD.md](../../METHOD.md). Author: Claude
(Anthropic, Opus 5.5). Human review: direction only. ChatGPT (OpenAI, Codex) may attack it like anything else.

## Why (measured on PR #181, 2026-11-24 19:10Z to 2026-11-25 23:20Z)

- **Volume.** 15 comments, 4,325 words. Every scheduled Claude run read all of them before deciding whether to act.
- **Latency set by the schedule.** When both sides were active, a reply took 0.30–0.58 h. When Claude's side waited for
  its twice-daily schedule, a reply took 3.0–6.9 h.
- **One defect per round.** ChatGPT's notes 006, 008, 010, 012 and 014 each found one edge case in the same function:
  an exact tie, a near-tie, a sub-threshold gap, a support mask, and unequal small eigenvalues. Each finding cost a
  round of reproduce, amend, code, rerun and note.

## The changes

1. **State lives in one place.** The top of PR #181's description holds a `State` block: the last note read, who is
   waiting on whom, and the open asks with their ids. Claude keeps it current. A run reads the block plus the comments
   newer than `last_note`, and reads the full thread only when the block is missing or contradicts the thread.
2. **Short note cards.** The header keeps `note / by / re / verdict`. Three lists replace most prose: `done:` (ask ids
   closed), `found:` (one line per finding, each with an evidence label and a case id) and `asks:` (id, owner,
   done-when). Prose is at most 150 words, output blocks are verbatim with at most 20 lines, and the note ends with
   `EN:`. Asks are numbered `A<note>.<n>` and findings `F<note>.<n>`.
3. **Findings are executable cases.** A public counterexample is posted as a case, not only as prose. That means a
   line of [`cases/public.jsonl`](cases/public.jsonl), or a fenced `json` block in the note in that line format.
   Anyone runs every case with one command: `python experiments/qfi_001/run_cases.py experiments/qfi_001/cases/public.jsonl`.
   Floats are written so that they round-trip exactly (Python `repr`). Cases are public, so blind material never goes
   here (custody unchanged).
4. **Batch the attack.** Before posting, run the attack you have to the end and report every finding in one note.
   Do not send one finding per round. A fuzzer or a second implementation (D1, below) is the default way to attack.
5. **Parallel tracks.** Every task in the description has an owner. A task that does not block another runs in
   parallel. Nobody waits for a turn.
6. **One round of prose per disagreement.** State the disagreement once, with a proposed test. The other side runs
   that test or proposes a better one. There is no third prose round: run the simplest discriminating test, and if it
   cannot be run, record CONTESTED.
7. **Silence on reversible items.** An ask about a reversible item, such as a wording change or a case added, counts
   as accepted 24 h after it was posted with no objection. Irreversible steps keep their own rules. That covers
   registration freezes, blind runs, merges and status changes to notes.
8. **Agreement costs a reaction, not a note.** A 👍 on a note means "read, no objection". It is not a reproduction.
   Reproductions that matter are recorded in committed results.
9. **Cadence.** Claude's scheduled check runs every 3 hours. It exits immediately when the `State` block shows nothing
   new and nothing is Claude's to do.

## D1: differential check (ChatGPT owns it)

**Two kinds of evidence.** Two implementations that agree on the same inputs show agreement, not correctness. Both
can share a wrong definition, as Amendment 4's mask defect shows. A state that one implementation writes and the other
reads back shows interoperability.

- **ChatGPT writes an independent implementation** of `qfi_split_ex(rho, drho) -> {F_Q, F_C, F_R, split_resolved}`.
  It should use a different route, for example by solving ρL + Lρ = 2∂ρ for the SLD and taking F_Q = tr(∂ρ L). Its
  independence is partial, because ChatGPT has read `qfi_ref.py`.
- **ChatGPT also owns the comparison:** the input generators (random states plus states fuzzed near ε, τ_tie and
  τ_flag), the tolerances and the harness. It registers them on a `chatgpt/qfi-001-*` branch before running anything.
- **The handoff is crossed both ways.** Cases written by one side's tooling are read by the other side's runner, and in
  Q3 the density matrices saved by Claude's pipeline are read by ChatGPT's code.
- **Disagreements** are reported as cases (item 3).
- **Timing:** D1 runs in parallel with Q3 and must finish before Q5 interprets any split.

## Unchanged

M2 (register before observing), M10 and author-is-never-tester, custody of blind material, evidence labels, AI
provenance with model names (M13), W9 records, never quoting Chad's prompts, and the delegation and merge authority
recorded in comments 7141782954 and 7142406923.

## Measured success (registered here, before FAST-1 runs)

Over the next 14 days on QFI-001 we will report, from the PR #181 timestamps:
- the median time from one AI's note to the other AI's next note, in both directions (corrected below);
- the share of those replies that take more than 3 h;
- the median words per note;
- the number of rounds per defect.

**Baseline, computed by code from the PR #181 timestamps:**
- **Reply time:** the median is 1.66 h across 9 replies in both directions. 4 of the 9 took more than 3 h.
- **Note length:** a median of 294.5 words over 14 notes.
- **Defects:** one defect per ChatGPT round.

**FAST-1 counts as faster only if all three hold:**
- the median reply time is below 1.66 h;
- fewer than 4 in 9 replies take more than 3 h;
- the median note is under 294.5 words.

Otherwise we say so and revert.

**Correction (W9), 2026-11-26, before any FAST-1 reply was counted.** The first version of this section, verbatim, read:
"**Baseline:** 0.30–6.9 h per reply, a median of 294.5 words over 14 notes (4,325 words in 15 comments), and one
defect per ChatGPT round. FAST-1 counts as faster only if the median reply time is under 3 h and the words per note
drop." Its first item, also superseded, was "the median time from a ChatGPT note to Claude's next note".

That 3 h test was vacuous (M3). The baseline already meets it: 1.66 h in both directions, and 1.80 h for ChatGPT
to Claude alone (0.30, 0.58, 3.01 and 6.92 h). The fault came from stating a range instead of computing the median.
Claude found it while building the dashboard. Chad Holland also declined the change to Claude's scheduled cadence
(item 9 does not run), so any gain has to come from the note format, the cases and the batching.
