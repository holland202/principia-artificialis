# CCC-001 stage Q letter-by-position crossing results: abstention follows the letter, and third place suppresses it for every letter (run 2026-11-21)

**Status:** run as registered at `88614da` ([QORDER_PREREG.md](QORDER_PREREG.md)). Development-only (C-EXPLORE).
Self-tested. Linux container CPU; S25 NOT VALIDATED.
**VERDICT 4 of 4 as registered: P0, P1, P2, P3 HELD.** This is a diagnostic of one small model's answer format on
24 development items. It says nothing about conversations, about CCC-001's hypothesis or about any other model.
**Stage Q's verdict does not change** (M12): Qwen2.5-1.5B stays not qualified.

Raw output: [`qorder_run.txt`](../../results/ccc_001/qorder_run.txt),
[`qorder_run_sabotage.txt`](../../results/ccc_001/qorder_run_sabotage.txt),
[`qorder.json`](../../results/ccc_001/qorder.json) (every letter logit, float32, for all 1,728 passes),
[`qorder_prompts.txt`](../../results/ccc_001/qorder_prompts.txt) (all 36 option lines and 6 instructions, printed
and read before the run). Harness: [`qorder.py`](qorder.py), run at `d0761d7`, outcome pinned at `9053557`.

## What could have gone wrong, first

1. **Self-tested throughout.** Claude wrote the registration, the harness and this file, and ran it. ChatGPT
   proposed the crossing and P1 (`ccc-relay/chatgpt/006`) and attacked the registration (`ccc-relay/chatgpt/008`);
   nobody reviewed the code or the run.
2. **A sign gate is weak.** P1 and P2 only require > 0. The sizes are printed so the reader can judge them; the
   smallest A − C contrast is 0.241090 (all conditions) and 0.230296 (unseen only).
3. **The registered reading table does not fit the position result cleanly.** Its row "P1 and P2 hold, position
   contrasts > 0" reads "both letter and first place contribute". The registered contrast is first minus third.
   It is positive for every letter, but for A and C the middle place is equal to or above the first (A: 0.525442
   vs 0.432110; C: 0.179381 vs 0.167036). What the data show is that **third place** lowers abstention, not that
   first place raises it. That is a reading of reported, ungated numbers, after the run.
4. **Additions after registration, before the run:** the `SUPP` lines (minimum contrasts, per-item counts, a
   matched P2 check) were asked for in `ccc-relay/chatgpt/008`. They are not registered and never gated. ChatGPT's
   optional 0.05 secondary threshold was not adopted, so no line uses it.
5. **Post-hoc check, not registered (below):** exact ties in arm D were inspected after the run, to close QDIAG's
   defect 5.
6. **Environment differs from QDIAG's session:** transformers 5.24.0, torch 2.15.0+cpu, 2 threads, a freshly
   downloaded model file with the registered SHA-256 (`dd924a11…c6d3ee`, checked with `sha256sum`). P0 bounds the
   effect: 0.000001.

## Raw output (pasted from `qorder_run.txt`)

```
P0 HELD 6 seen conditions vs qdiag.json uncached arm D: max |p diff| 0.000001 (<= 0.01)
P1 HELD m(A,j) - m(C,j), all 36 conditions, j=1,2,3: 0.265074  0.346060  0.241090 (> 0 each)
P2 HELD m(A,j) - m(C,j), 30 unseen conditions, j=1,2,3: 0.261972  0.346060  0.230296 (> 0 each)
P3 HELD sabotaged readout: contrasts all exactly 0: True, ties 864 of 864 (= 864), P1 and P2 refuted under sabotage: True
REPORT cell means m(L,j), arm D, p(abstention letter), all conditions [unseen only in brackets]:
REPORT   letter A: j=1 0.432110 [0.429008 n=2]  j=2 0.525442 [0.525442 n=4]  j=3 0.252348 [0.252348 n=4]
REPORT   letter B: j=1 0.397879 [0.397879 n=4]  j=2 0.314816 [0.311599 n=2]  j=3 0.097985 [0.097985 n=4]
REPORT   letter C: j=1 0.167036 [0.167036 n=4]  j=2 0.179381 [0.179381 n=4]  j=3 0.011257 [0.022052 n=2]
REPORT position contrast m(A,1) - m(A,3) = 0.179762
REPORT position contrast m(B,1) - m(B,3) = 0.299895
REPORT position contrast m(C,1) - m(C,3) = 0.155779
REPORT arm D modal readings over 864: {'A': 407, 'B': 274, 'C': 148, 'tie': 35}
REPORT secondary arm E cell means m_E(L,j), and Q2 components per cell (gain mean G(E)-G(D), E>D count of 96):
REPORT   letter A: j=1 0.209555 gain +0.2399 E>D 68/96  j=2 0.318001 gain -0.1199 E>D 37/96  j=3 0.303675 gain -0.1351 E>D 31/96
REPORT   letter B: j=1 0.595461 gain +0.0649 E>D 55/96  j=2 0.235103 gain +0.0693 E>D 49/96  j=3 0.164680 gain +0.0513 E>D 41/96
REPORT   letter C: j=1 0.300174 gain +0.1071 E>D 61/96  j=2 0.166574 gain +0.0205 E>D 49/96  j=3 0.064831 gain +0.0579 E>D 58/96
SUPP minimum of the three A-C contrasts: all 0.241090, unseen 0.230296
SUPP j=1: items with per-item m(A,j) - m(C,j) > 0: 23 of 24
SUPP j=2: items with per-item m(A,j) - m(C,j) > 0: 23 of 24
SUPP j=3: items with per-item m(A,j) - m(C,j) > 0: 23 of 24
SUPP matched P2 check j=1: other two letters displayed in descending order on both sides (A side 2 conditions, C side 2): m(A) - m(C) = 0.143969, sign same vs P2
SUPP matched P2 check j=3: other two letters displayed in descending order on both sides (A side 2 conditions, C side 2): m(A) - m(C) = 0.310179, sign same vs P2
VERDICT 4 of 4 as registered
DIGEST c6dbb84ce2ba69769a859472ed49b5db69f1c388f9154ab32a37cf65c592f729
```

The 36-condition table is in `qorder_run.txt`. The sabotage run's last lines are pasted in the next section.

## Predictions

| ID | Registered | Outcome |
|---|---|---|
| P0 | 6 seen conditions reproduce `qdiag.json` arm D within 0.01 | HELD, 0.000001 |
| P1 | m(A,j) − m(C,j) > 0 at j = 1, 2, 3 | HELD, 0.265074 / 0.346060 / 0.241090 |
| P2 | P1 on the 30 unseen conditions only | HELD, 0.261972 / 0.346060 / 0.230296 |
| P3 | sabotage: contrasts exactly 0, 864 ties, P1 and P2 refuted, exit 1 | HELD in-process; CLI `--sabotage` gives 1 of 4, exit 1 |

## Anti-vacuity: the `--sabotage` run

Same harness with `--sabotage` (every letter logit set to zero before the softmax), pasted from
`qorder_run_sabotage.txt`:

```
P0 REFUTED 6 seen conditions vs qdiag.json uncached arm D: max |p diff| 0.666662 (<= 0.01)
P1 REFUTED m(A,j) - m(C,j), all 36 conditions, j=1,2,3: 0.000000  0.000000  0.000000 (> 0 each)
P2 REFUTED m(A,j) - m(C,j), 30 unseen conditions, j=1,2,3: 0.000000  0.000000  0.000000 (> 0 each)
P3 HELD sabotaged readout: contrasts all exactly 0: True, ties 864 of 864 (= 864), P1 and P2 refuted under sabotage: True
REPORT arm D modal readings over 864: {'A': 0, 'B': 0, 'C': 0, 'tie': 864}
VERDICT 1 of 4 as registered
DIGEST c32e928024687f5e7d3fdba91242778e379874e4c998ec35f280dd7f15bb7abb
EXIT 1
```

Both runs were made before `RECORDED` was pinned, so each exit code comes from the unpinned rule (exit 0 only if
all four held and no sabotage). After pinning, the harness was not re-run (NOT RUN).

## Post-hoc check, not registered: exact ties and QDIAG defect 5

In arm D, 35 of 864 readings have two or three letters with exactly equal float32 logits (20 A–B, 10 A–C, 4 B–C,
1 A–B–C). Seven are in the six conditions QDIAG also ran: π4 item 12 (B–C), π3 items 3, 5 and 22 (A–B), π2 items 2
(A–C), 11 and 18 (A–B). QDIAG's `modal` gives a tie to the first letter. So QDIAG's P5 count for π2 ("3 of 24")
left out two items where the not-enough letter B tied for first, and π4's "10 of 24" includes one item where B tied
with C. P5 stays REFUTED either way (π1 alone gives 12 > 2). QDIAG_RESULTS item 5 said whether unsabotaged items
tie was NOT RUN; it is now checked here, with this harness's logits, which reproduce QDIAG's within 0.000001.

## What this shows and does not show

- **Shows (this model, these items, this wording):** the probability given to the abstention meaning depends on
  its letter, A > C at every display position, by 0.23 or more, on 23 of 24 items at each position, and on
  conditions QDIAG never showed us. B sits between A and C at every position; at position 1 it is close to A
  (0.397879 vs 0.432110).
- **Shows:** listing the abstention option third lowers its probability for every letter. QDIAG's "C was modal on
  0 of 24" sat in the worst corner of the table: m(C,3) = 0.011257.
- **Does not show:** why. Letter token identity and alphabetical rank are not separated (registered limit). It
  does not show that first place helps: the middle place does as well or better for two of three letters.
- **Secondary arm E** is reported, not gated. The instruction does not remove the pattern (m_E(B,1) 0.595461 vs
  m_E(B,3) 0.164680), and Q2's gain is positive in 7 of 9 cells and largest at (A,1).
- **For the instrument:** any later stage Q that keeps one fixed letter-and-order mapping measures this bias along
  with whatever it is meant to measure. Counterbalancing letters and positions is a proposal, NOT RUN, and a design
  decision that waits for the relay and for Chad.

## Open (M15)

- The registered door stands: the next stage Q (Qwen2.5-7B-Instruct, 4-bit, items written by someone other than
  Claude) reports abstention at the (A,1), (A,3), (C,1), (C,3) corners alongside S and G. NOT RUN.
- Letter identity versus alphabetical rank (for example X, Y, Z or 1, 2, 3 labels). NOT RUN.

## Provenance (M13)

Question origin for CCC-001: Federico Talens-Alesson, credited as the question's originator only; no endorsement
or validation by him is implied. Crossing design and P1 proposed by ChatGPT (OpenAI) in the relay; attack of the
registration by ChatGPT in `ccc-relay/chatgpt/008`. Harness, run and this file by Claude (Anthropic, Opus 5.5) in a
fresh scheduled session under Chad Holland's standing direction of 2026-11-21. Human validation: not performed.
Human editing/curation: direction only. Human responsibility: Chad Holland.
