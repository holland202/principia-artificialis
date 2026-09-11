# Research Note #061: Does a Table of Contents Carry Retrieval Signal, or Is the Gain the Narrowing?

**Status:** Draft, verified reference code ⚠ refutations kept
**Author:** Chad Edward Holland, with Claude (Anthropic)
**Reference code:** `scripts/note061_reference.py`
**Preregistration:** `experiments/note061_prereg.md` — written and committed before execution
**Corpus:** PINNED at commit `e9b4e68`, materialized via `git archive`, 83 files
**Corpus manifest SHA-256:** `6665a4ace2962321...`

## What broke

Three defects, all found by running the instrument rather than reading it.
Two of them were in the instrument.

1. **The experiment measured a corpus its own publication changed.** The
   script globbed `research_notes/`, and this note lands in
   `research_notes/`. Staging it took the corpus from 83 notes to 84 and
   every count moved: flat 37/82 to 38/83, shuffled 3/82 to 5/83. Caught by
   the device reproduction gate, not by reading the code. The corpus is now
   pinned to a commit and read through `git archive`, never from the working
   tree, so the result reproduces from any clone made at any later date. An
   integrity check refuses to run if the note or query count differs from
   the registered one, with `--corpus-mutation` as its control.

2. **A verdict decided by sort tie-breaking, differing by architecture.**
   TOC_BLANK's index entries score exactly 0.0 against every query -- one
   distinct value across all 83 rows -- so which notes entered its candidate
   set was settled entirely by how `np.argsort` broke a total tie. NumPy
   dispatches architecture-specific sort kernels, so byte-identical logic
   scored TOC_BLANK at 1/82 in an x86_64 container and 4/82 on the S25
   (aarch64), on the same NumPy 2.4.4. Found by the device reproduction gate,
   which is the only instrument that could have found it. Same defect class as
   [[note054_kx_allocation]]'s `spearman()` tie handling, which was also found
   only by running on a second architecture. Fixed with an explicit stable
   sort, which preserves input order on ties by specification everywhere.

3. **The confidence intervals were inverted.** Clopper-Pearson was solved
   with the wrong target and the wrong monotonicity direction. The first run
   printed `[100.00%, 0.30%]` — a lower bound above its upper bound — and the
   inverted interval made the anti-vacuity gate P0a fail spuriously. Had the
   ordering not been absurd on its face, this note would have reported "the
   corpus is broken" about a corpus that was fine. Fixed, with a self-test
   asserting a textbook case and the ordering invariant at every k.

4. **The load-bearing control was not load-bearing.** P2 compared the real
   table of contents against a shuffled one. Shuffling permutes which *note*
   each entry points at, so it destroys the entry's content and its pointer
   together. With the pointer broken the candidate set contains the target
   only by chance, so the shuffled arm is near-trivially low by construction
   and its disjoint interval is an artifact of the design. Amendment 1
   proposed a content-only control; writing it revealed that under hard
   narrowing that control is degenerate for the same reason. Amendment 2
   registered the measurement that is not degenerate: vary k.

5. **The verdict block reached a conclusion the evidence did not support.**
   It printed "the table of contents carries signal" whenever P2 was
   confirmed, without consulting P1, and printed exactly that while P1 stood
   refuted. Same defect class this repository builds tools to detect,
   in the code written to detect it.

## Why

Structure-aware retrieval systems are compared against retrievers that differ
from them in more than one way at once. The arm that separates "the structure
carries semantic signal" from "narrowing before searching helps, and the
contents of the structure barely matter" is absent from the comparisons this
author has seen. This note runs that arm on a corpus it owns.

## Result

| arm | Recall@1 | 95% CI |
|---|---|---|
| RANDOM | 1/82, 1.22% | [0.03%, 6.61%] |
| FLAT | 37/82, 45.12% | [34.10%, 56.51%] |
| TOC, k=5 | 36/82, 43.90% | [32.96%, 55.30%] |
| TOC_SHUF | 3/82, 3.66% | [0.76%, 10.32%] |
| TOC_BLANK | 1/82, 1.22% | [0.03%, 6.61%] |

Narrowing width sweep, TOC arm:

| k | 1 | 2 | 5 | 10 | 20 | 40 | 83 |
|---|---|---|---|---|---|---|---|
| hits/82 | **45** | 35 | 36 | 35 | 35 | 36 | 37 |

- **P0** PASS both parts. Random sits on chance; flat beats it.
- **P1 REFUTED (kept).** At the registered k=5 the ToC arm scored 43.90%
  against flat's 45.12%. One query worse.
- **P2 CONFIRMED but VOID as evidence.** See defect 2.
- **P3 CONFIRMED**, trivially, for the same reason.
- **P5 CONFIRMED but VOID as evidence.** Amendment 1's control is degenerate.
- **P6 CONFIRMED.** The curve is not monotonic in k.
- **P7 REFUTED (kept).** At k=1 the ToC arm scored 45/82, above flat's 37/82.

At k=N the two-stage arm is flat retrieval by construction, and the sweep
lands on 37/82 there, which is exactly flat's score. That equality is not a
prediction; it is the arithmetic identity working, and it is the only thing
in this table that was guaranteed in advance.

## Reading

The registered refutation of P1 was an artifact of a narrowing width fixed in
advance and fixed badly. At k=5 the table of contents hurts. At k=1 it helps.
Both statements come from the same run.

**This is a lead, not a result.** k=1 is the best of seven widths tried, and
its interval overlaps flat's. Best-of-seven selection inflates any apparent
gain. Reporting 54.88% as the performance of ToC retrieval would be selecting
a winner after the fact, which is the thing this note's own method forbids.

What survives: on this corpus, whether a table of contents helps or hurts
retrieval depends entirely on how aggressively it narrows, and a single
pre-chosen k can put the answer on either side of the baseline. A comparison
that fixes k once and reports one number is not measuring the structure. It
is measuring the k.

## Anti-vacuity controls

- `--corpus-mutation` adds one phantom note; the integrity check refuses and
  exits 1. Verified.
- `--sabotage` shifts ground truth by one; P0b fails and the script exits 1. Verified.
- Determinism: two consecutive runs byte-identical. Every draw seeded.
- RANDOM arm present in every run as the chance floor.
- `_selftest_ci()` asserts the interval code against a known case and the
  ordering invariant before any measurement runs.

## Limitations, registered rather than discovered

One corpus, one author, ~80 documents. TF-IDF, not a learned retriever.
Queries are extracted sentences, which is an easier task than question
answering. None of this transfers to book-scale or multi-domain corpora
without being run there.

## Left unrun

**P4:** whether any of this survives paraphrased rather than verbatim
queries. Every arm here matches wording that appeared in the target note. A
paraphrase step would test retrieval rather than string overlap, and would
plausibly move flat retrieval more than the ToC arm.

## Related

Method ancestry: [[note052_verification_that_cannot_fail]] for the anti-vacuity
control discipline and [[note058_kv_vacuity]] for a prior case of a control
that could not fail, and the context-blind arm in quasar-v2's F19, which is
where the "delete the mechanism, keep the budget" control used here comes
from.
