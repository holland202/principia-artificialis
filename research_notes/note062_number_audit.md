# Research Note #062: Do the Notes' Numbers Appear in Their Own Code's Output?

**Status:** Draft, verified reference code; P2 refuted and kept — registered 2026-09-27, before the audit was run
**Theme:** Method / reproducibility
**Author:** Claude (Anthropic), for Chad Edward Holland
**Builds on:** the binding rule in NOTE_TEMPLATE.md ("numbers match code output"), [[note044_circularity_test]] (an instrument must be able to fail), [[note058_kv_vacuity]] (a check that lies about why it failed)
**Reference code:** `scripts/check_numbers.py` (writes `results/NUMBER_CHECK.md`)

## The claim

The program's first rule is that every number in a note's prose is printed by that note's reference
script. Nothing has ever checked the rule mechanically. This note builds the check and runs it once
over every note with a reference script. The claim that could be precisely wrong: **the rule already
holds, to within a few percent of the measured numbers.**

## Instrument

For each `scripts/noteNNN_reference.py`, the note that names it is paired with the script's output,
run with CI's arguments. A *measurement-like* number is a decimal or exponent literal with at least 3
significant digits. It is FOUND if the output prints it, or prints the same value to more decimal
places. Everything else is NOT FOUND and listed with its line, as a lead for a human reader.

## Registered predictions (written before the first full run)

- **P1 (anti-vacuity)** The self-test passes. A note that quotes its output shows 0 not found, and the
  same note with one digit changed (1.6398 → 1.6498) is flagged, and only that number.
- **P2** Across all notes with reference scripts, at least 90 % of measured numbers are FOUND.
- **P3** Every NOT FOUND number is classified by hand as (a) a parameter or a number quoted from
  elsewhere, (b) a derived value computed in prose from printed ones, or (c) drift: a number the code
  no longer prints. P3 predicts at least one (c), because a program with 20+ scripts edited over two
  months will have drifted somewhere.

## Results

**What broke first: the instrument.** Run 1 printed `TOTAL 125/195 found`. Reading the not-found list by
hand showed that the checker missed every negative number in prose. The notes write minus as U+2212
("−3.082") and the scripts print "-3.082". After the fix, run 2 printed:

```
self-test: honest note 0 not found; planted wrong number flagged: ['1.6498'] -> PASS
TOTAL 129/195 found; report: results/NUMBER_CHECK.md
```

- **P1 held.** The self-test passes and flags exactly the planted number.
- **P2 REFUTED (kept).** 129 of 195 measured numbers (66 %) appear in their script's output, against
  the registered ≥ 90 %.
- **P3 held.** Every one of the 66 NOT FOUND numbers was read by hand in context:

| class | count | what it is | notes |
|---|---|---|---|
| (a) quoted from elsewhere | 47 | pre-fix values kept as history, device-only runs (thermal, timings), another run size, a control corpus, and two instrument false positives (an arXiv id, a Python version) | 040, 048, 052, 053, 054, 055, 056, 059, 060, 061 |
| (b) derived in prose | 9 | computed from printed numbers: 2.15× = 1 + 1.1513, 12.0 % = 3/25, CI widths, a difference of two printed gains | 052, 054, 055, 059, 060 |
| (c) drift | 10 | numbers the code does not print | 043 |

**What P2's failure teaches.** The rule "every number in the prose is printed by the code" conflicts
with the program's other rule, "refutations and history stay on the page". Most not-found numbers are
honest history: pre-fix outputs kept so a reader can see what broke. The literal rule cannot hold for
them. A rule that can hold: *every number the note currently claims is printed by the code; every
historical or external number is marked as such where it appears.* The checker cannot tell the two
kinds apart yet. That is the next instrument.

**What P3's (c) found: note043's pasted output was not produced by its code.** The note shows
F = -8.7883 / 3.6652 and AUC 0.9950. Both the code pasted in the note and `scripts/note043_reference.py`
print F = -1.0232 / -0.6320 and AUC 1.0000, deterministically. The pasted block's line structure also
differs from anything the code prints. Its AUC is vacuous besides: every "hallucinated" trajectory
is identical. note043 now leads with a correction, and its status no longer says "verified reference
code". The original text is kept.

**A second, smaller drift, found on the way:** `scripts/note055_reference.py` printed "v1 already passed
its analogue (rho=+0.117)", but note054's tie fix changed that value to +0.1480, as note055's own prose
says. The printed line now gives both.

After these corrections, the committed report reads `TOTAL 145/216 found`. The total grew because the
note043 correction pastes the true output, and quotes the wrong numbers once more so a reader can
compare.

Not covered: notes 038, 041 and 050. The checker found no unique note naming their script (number
collisions, see the index's ⚡).

## Falsifiable next predictions

- **P4 (open)** Adding `check_numbers.py` to CI as a *warning* (not a gate) reduces new class-(c) drift
  to zero over the next ten notes. Unrun.
