# Research Note #062: Do the Notes' Numbers Appear in Their Own Code's Output?

**Status:** Draft, verified reference code (registered 2026-09-27, before the audit was run)
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

(Filled in after the run. Numbers below are pasted from `results/NUMBER_CHECK.md`.)

## Falsifiable next predictions

- **P4 (open)** Adding `check_numbers.py` to CI as a *warning* (not a gate) reduces new class-(c) drift
  to zero over the next ten notes. Unrun.
