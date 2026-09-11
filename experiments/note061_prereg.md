# note061 (E16) — Preregistration: does a table of contents carry retrieval signal, or is the gain the two-stage machinery?

Status: REGISTERED, NOT RUN
Written: 2026-09-11
Corpus: principia-artificialis at e9b4e68, `research_notes/*.md`
Instrument: `scripts/note061_reference.py` (this experiment's reference script)
Author: Chad Edward Holland

This document is written before the experiment is run. Git history is the
evidence of that order.

## Why this exists

Structure-aware retrieval systems report gains against retrievers that differ
from them in more than one way at once. A published comparison of this kind
scores a structure-aware system at 82.6% Recall@1 against a differentiable
search index at 76.9%, BM25 at 59.5% and a dense retriever at 68.7%. Every
one of those baselines is a different retriever, so the comparison cannot
separate two explanations:

  (a) the table of contents carries semantic signal that helps retrieval
  (b) the two-stage narrow-then-search procedure helps, and the contents of
      the table of contents are close to irrelevant

The arm that separates them is absent from that design and from every
structure-aware retrieval comparison this author has seen: **the same
pipeline with the structure destroyed and nothing else changed.**

E16 does not evaluate that system, reproduce its numbers, or test its claims.
It has not been read beyond its abstract. E16 asks the separating question on
a corpus this author owns.

## The corpus, and why it is honest to use it

`NOTES_INDEX.md` is a real table of contents over the note series: it is
machine-generated from the notes, it carries each note's title, status and
author, and it was built for navigation rather than for this experiment.
Ground truth is free — a query drawn from a note is known to belong to that
note — and no labelling by the author is involved at any point.

The corpus is small and single-author. That is a limitation, registered
below, not a discovered caveat.

## Arms — identical except where stated

  FLAT        fixed-length chunks, TF-IDF cosine, no structure used
  TOC         two stages: rank ToC entries, keep the top k notes, then rank
              chunks within only those notes
  TOC_SHUF    identical to TOC in every respect, except the ToC entry strings
              are permuted across notes with a fixed seed, so each entry
              describes a note it does not point to
  RANDOM      selects a note uniformly at random, seeded

TOC and TOC_SHUF share one code path and one value of k. The only difference
between them is whether the table of contents tells the truth.

## Query construction — fixed before execution

For each note, deterministically select the longest sentence in its body
that is at least 12 words long and lies outside a fenced code block. That
sentence becomes the query and is REMOVED from the indexed text of its own
note, so no arm can match it to itself verbatim.

A note yielding no eligible sentence is excluded and the exclusion is
counted and reported. Notes are not replaced.

## Outcome

Recall@1: the proportion of queries whose top-ranked note is the source note.
Reported as raw counts with Clopper-Pearson 95% intervals. Never as a rate
alone.

## Registered predictions

P0  ANTI-VACUITY GATE, evaluated first.
    P0a RANDOM's Recall@1 interval contains 1/N, where N is the number of
        eligible notes.
    P0b FLAT's Recall@1 interval lies entirely above RANDOM's point estimate.
    If either fails, the corpus or the instrument is broken, and P1-P3 are
    VOID rather than reported. A retrieval task where flat retrieval cannot
    beat chance measures nothing about structure.

P1  TOC's Recall@1 point estimate exceeds FLAT's.

P2  LOAD-BEARING. TOC's Recall@1 point estimate exceeds TOC_SHUF's.
    P2 CONFIRMED if TOC exceeds TOC_SHUF and their 95% intervals do not
      overlap.
    P2 REFUTED if TOC_SHUF equals or exceeds TOC.
    P2 INCONCLUSIVE if TOC exceeds TOC_SHUF but the intervals overlap, and
      it is reported as inconclusive rather than as weak support.

    If P1 is confirmed and P2 is refuted, the gain is the two-stage
    procedure, not the table of contents, and any claim of the form
    "structure helps retrieval" on this corpus is unsupported.

P3  TOC_SHUF's point estimate does not exceed FLAT's.
    A shuffled table of contents that still beats flat retrieval would mean
    the narrowing step helps even when it narrows to the wrong notes, which
    would be a stronger and stranger result than P2 failing.

No prediction registers a numeric target. The procedure is registered; the
numbers fall where they fall.

## Determinism

Every random draw in this experiment is seeded. The script prints its seed
and must produce byte-identical output across runs and across architectures
(x86_64 and aarch64). A run that differs between two executions is void.
This rule exists because a gate whose verdict is redrawn each run was found
in this estate on 2026-09-11.

## Anti-vacuity control on the instrument

`--sabotage` corrupts the ground-truth mapping and must drive the gate to
exit 1. An instrument that cannot report failure reports nothing.

## Known limitations, registered rather than discovered

1. One corpus, one author, ~80 documents. Nothing here generalizes to
   book-scale or multi-domain corpora without being run there.
2. TF-IDF, not a learned retriever. A finetuned system may depend on
   structure differently. This design tests whether the STRUCTURE carries
   signal for a retriever, not whether every retriever behaves this way.
3. Queries are extracted sentences, not questions a person would ask.
   Extracted-sentence retrieval is an easier task than question answering.
4. k for the narrowing stage is fixed in advance and not tuned. A different
   k could change the result, and tuning k after seeing results would be
   goalpost-moving.

## Left unrun

Whether the effect, if any, survives when queries are paraphrased rather
than extracted verbatim. That requires a paraphrase step this corpus does
not have and would introduce a model into the query pipeline.

---

## Amendment 1 — registered 2026-09-11, AFTER the first run, NOT YET RUN

The first run refuted P1 and exposed a design defect in the P2 control.

TOC_SHUF permutes which NOTE each table-of-contents entry points to. That
destroys two things at once: the entry's semantic content AND the pointer.
With the pointer broken, the candidate set contains the target only by
chance, so TOC_SHUF is near-trivially low by construction and its disjoint
interval is an artifact of the design rather than evidence about content.

P2 as originally registered is therefore NOT load-bearing. It is kept,
marked, and not read as support.

The control that would separate content from narrowing keeps every pointer
correct and replaces each entry's TEXT with an uninformative label, so the
two-stage machinery is intact and only the semantics are gone:

P5  TOC's Recall@1 exceeds TOC_BLANK's, where TOC_BLANK uses the same
    pointers and the same k but entry text carrying no topical information.
    If TOC_BLANK matches TOC, the narrowing helps and the words in the table
    of contents do not.

P5 is registered here and left unrun.

---

## Amendment 2 — registered 2026-09-11, BEFORE running P5 or P6

Writing Amendment 1 exposed a problem with Amendment 1.

TOC_BLANK breaks the table of contents' ability to rank the right note
highly. So does TOC_SHUF. Under HARD narrowing — keep top k, discard the
rest — any arm whose entries cannot rank the target collapses to roughly
k/N, whatever the reason. P5 is therefore near-trivial for the same
structural reason P2 was, and "content versus machinery" is ill-posed for
this design: under hard narrowing the machinery has no effect except
through the content.

P5 is run anyway and reported, because a registered prediction that turns
out uninformative is kept and marked, not deleted.

The measurement that is not degenerate is the one that varies the narrowing
width. At k = N the two-stage arm is exactly FLAT by construction. So the
table of contents' whole contribution is the shape of the curve between
k = 1 and k = N.

P6  Recall@1 for the TOC arm is not monotonically increasing in k.
    A strictly increasing curve would mean narrowing never helps and only
    ever discards the answer, making the table of contents purely harmful
    on this corpus.
P7  TOC's Recall@1 at its best k does not exceed FLAT's.
    This is P1 given every chance: if no k beats flat retrieval, the
    refutation of P1 is not an artifact of fixing k = 5 in advance.

P6 and P7 are registered here, before execution.
