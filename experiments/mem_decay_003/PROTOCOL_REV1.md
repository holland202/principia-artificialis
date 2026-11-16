# MEM-DECAY-003 protocol, revision 1: what Codex's review broke, what is fixed, and what is left

**State:** DRAFT REVISION. **NOT REGISTERED, NOT RUN.** No model has been called. Owner approval is still needed
before any campaign. This file revises [PROTOCOL_DRAFT.md](PROTOCOL_DRAFT.md), which stays as written.
**Authors:** Direction: Chad Holland (2026-11-16). Review that prompted this revision: Codex (OpenAI), draft PR #159 at
`96c00d1`. Revision: Claude (Anthropic, Opus 5.5). Human review level: direction only. Self-tested.

## 1. Failures first

Codex reviewed the merged draft (PR #158, merged as `1ceb6aa`). Claude reran each finding against its own code before
fixing it. All four implementation defects reproduced:

| # | Defect in the draft | Reproduced by Claude |
|---|---|---|
| A1 | The exact gold answer `ANSWER: 6 p.m.` scored WRONG: output lost its final period, the key kept it | yes, singleton task in every dev scenario |
| A2 | `retained_requirements()` ignored `needs_any`, so a redundant task with **nothing** kept counted as retained | yes |
| A3 | Several ANSWER lines were allowed and the last one won, so a self-contradicting reply could score CORRECT | yes, a deliberate convention that was never justified |
| A4 | The dev family always gave the correction the id `m001`. An id-only rule found it 40/40, and the scrambling test could not see this | yes, 40/40 |
| — | The conjunctive question named Room F, so one of its two "required" records was already given by the question | yes, by reading |

**Also wrong in the draft:**

- **A5, the bigger one (accepted).** H1b as written cannot separate a model failure from plain information loss. A
  history that was never corrected and a history whose correction was evicted can leave the model the same notes. The
  same answer is then CORRECT in one and STALE in the other. A non-AI lookup reproduces the whole STALE pattern.
  The draft also said "confidently wrong" but measured no confidence.
- **Prior work was under-searched.** The draft called *Beyond Marginal Influence* (JointCoreBench) a NeurIPS 2026 paper;
  its authors describe a NeurIPS 2026 **workshop** paper. The draft also missed four closely related works:
  - LongMemEval (ICLR 2025): knowledge-update and abstention questions;
  - STALE (arXiv 2605.06527): memories invalidated by later observations;
  - *Two Levers for Undermined Facts in Agent Memory* (NeurIPS 2026 PALM workshop): on MEME's Absence items, readers
    answer about 1.5% correctly when a stored value's grounds lapsed with no replacement, and a three-sentence
    system prompt raises that to 0.923 (abstract level);
  - a deterministic supersession ledger (arXiv 2606.26511).
- **Unsaved script.** The draft's qualification table came from an inline script that was never committed, so it
  cannot be rerun. It is kept as it was. [`qualify.py`](qualify.py) now produces the table.

## 2. What changed in the code (`memdecay3.py`, `dev_family.py`)

- **Output contract, fixed before any model output exists:** exactly one line `ANSWER: <value>`. None, or two or
  more (even if they agree), is MALFORMED.
- **Normalisation is applied to the answer and the key alike:** trim, drop surrounding quotes, lower-case, collapse
  spaces, drop trailing periods. Every gold answer in the dev family must round-trip in five forms.
- **Retention:** every `needs` id is kept (AND), and at least one `needs_any` id if that list is not empty (OR). A
  task with no requirement raises an error instead of passing.
- **Opaque ids**, drawn after shuffling. Selector ties break on text before id. A new test relabels every id and
  requires the same records, by content, to be kept; an id-only rule fails it.
- **A real conjunctive pair:** "the inspection is held on the same day as the fire drill" + "the fire drill is on
  {day}". The question names neither, and each premise alone licenses UNKNOWN.
- **Two scores, kept apart (A5):**
  - `classify()` scores against the full history (CORRECT / STALE / UNKNOWN / WRONG / MALFORMED);
  - `licensed_answer()` and `evidence_outcome()` score against what the retained notes license.
  With only the original kept, the old value FOLLOWS the evidence: the store lost information, and the model did
  not fail.
- **The exact prompt is published:** `build_prompt()` shows the retained notes' text only, with no ids, ages or
  use counts. A test checks the A5 property: equal retained text gives a byte-identical prompt.

**Checks, Claude-run:**

- **The new tests:** 17 tests (27 in total). Run against the merged draft, they gave 9 failures and 6 errors. They
  all pass on this revision ([`results/mem_decay_003/tests_rev1.txt`](../../results/mem_decay_003/tests_rev1.txt)).
- **Codex's audit:** run unchanged against this revision, it reports `AUDIT OBSERVATIONS MISMATCH`. That is the
  intended result: A1–A4 no longer reproduce, and A5 still does, by design.

## 3. H1b is withdrawn as a claim about model behaviour

There are two reasons:

- **It can't be identified:** with equal retained text, a model that gives the old value is following its evidence.
  Nothing in the draft's design could show more than that.
- **The behavioural version is already studied:** the version that *would* be identifiable is whether a model
  abstains when a retained note says the old value no longer holds. That is close to MEME's Absence items and *Two
  Levers*, so Codex's proposed invalidation-notice control would be a near-replication. **It is not planned.**

## 4. What is left: a smaller question about the store, needing almost no model

**Question (to kill, not to claim):** at the same memory budget, do realistic task-blind selectors leave the store
licensing a superseded value more often than random selection does?

- **Measure:** `stale_licensed`, the share of correction tasks where the retained set licenses the old value
  (original kept, correction lost). It is computed from the retained set alone, so **the deterministic selectors
  need no model calls at all.**
- **Arms:** random, recency, uses, content, supersession-aware, and an LLM-judge selector. The judge is the only one
  that needs a model: the same 7B rates each record 1–5, one record at a time, without the task.
- **Kill:** on externally written evaluation families, recency, uses and the LLM judge each show `stale_licensed` no
  higher than random at the same budget. Exact thresholds are frozen before evaluation.
- **Novelty:** unestablished. The supersession-ledger paper fixes staleness at write time. I found no paper on
  budgeted eviction of corrections, but that is an absence in a short search, not evidence of novelty.
- **Dev-only qualification:** [`qualification_rev1.txt`](../../results/mem_decay_003/qualification_rev1.txt). The
  content rule licenses the stale value in 40/40 and the uses rule in 39/40 at budget 6, and random in 6/40. This is
  **still by construction**, because I wrote the corrections short and without constraint words. It shows the
  instrument registers the difference, and nothing more.

**Pilot, replacing the draft's 672 decision calls:** LLM-judge scoring on 12 dev scenarios × 20 records = **240
short calls**, roughly 20–40 minutes here. The draft's decision-model pilot is dropped. An optional later bridge
check would confirm on a small sample that the model's answers follow `licensed_answer()`. It is not needed for the
question in section 4.

## 5. Custody and order (Codex asked for both)

**A hash is a commitment, not blindness.** Codex has read the instrument, so the evaluation cases it writes are
implementation-informed. Under the coordination rules that is allowed: the test author may see the code, but the
code author must not see the cases before the run. Proposed order:

1. Codex reviews this revision.
2. Chad decides whether MEM-DECAY-003 continues in this smaller form, or closes as a withdrawn lead.
3. If it continues, Claude freezes the harness at a named commit. Any later code change voids the evaluation run.
4. Codex writes the evaluation families against the frozen schema and posts only their SHA-256. Records are written
   by Codex, ids are opaque, order is counterbalanced, and the challenge variations from the draft's section 5 are
   included.
5. The deterministic arms need no model, so Codex can run them itself and publish outputs and cases together. For
   the LLM-judge arm, either Codex runs it, or the cases go to whoever runs the frozen harness, at run time and not
   before. Chad picks.

## 6. Open choices

1. Continue in the smaller form, or close MEM-DECAY-003 as withdrawn? **Claude's recommendation:** continue. It is
   cheap (no decision model; 240 judge calls), and a null is informative. But this is not a new lead in any strong
   sense.
2. Who runs the LLM-judge arm on the evaluation families (section 5, step 5)?
3. Does the bridge check (do model answers follow `licensed_answer()`?) belong in this study, or in a separate one?

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) revised its own draft after review by Codex (OpenAI) → human
validation: not performed → human editing/curation: direction by Chad Holland, 2026-11-16 → human responsibility:
Chad Holland. Review level: direction only. Claude's tests of its own fixes are self-tests.*
