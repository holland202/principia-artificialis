# Registration: reproduce the headline numbers of "One Run Is Not Enough" (arXiv:2611.19359) from its own data

**State: REGISTERED, NOT RUN.** Committed before Claude ran any code from, or computed anything on, the paper's data.
What was read beforehand: the arXiv abstract page; the file list, `git log`, `LICENSE` (Apache-2.0),
`results/README.md`, and the import lines and field names of `results/run_rows.jsonl` and
`results/analyze_rows.py` in github.com/renorai/gemma4-memory-study at `2eea9c6` (to check the script only reads
the rows and writes `analysis.json`).

Direction: Chad Holland, 2026-11-25 (supplied the scan that named this paper and asked for automatic evaluation).
Written by Claude (Anthropic, Opus 5.5). Human review: none.

## Claims checked (from the abstract)

| ID | Expected | Check |
|---|---|---|
| E1 | 47/98 with the reminder, 48/98 without; difference −1.0 points, 95% interval [−8.3, +6.3]; exact McNemar p = 1.0 | the authors' `results/analyze_rows.py` on their committed `run_rows.jsonl` |
| E2 | first 48 pairs 29 vs 25, p = 0.22; extension 50 pairs 18 vs 23, p = 0.125 | same |
| E3 | 19% of tasks flip outcome between two identical no-memory runs | same |
| E4 | `PREREG.md` was committed before the first commit that adds `results/run_rows.jsonl` | `git log` |
| E5 | Claude's own exact McNemar (two-sided binomial on the discordant pairs, written here, not imported) gives the same p as the authors' code for E1 and E2 | independent recompute |

**Anti-vacuity.** In a copy of the rows, flip the outcome of one paired task in the reminder arm. The authors' script must
then report a different E1 count. If it does not, the check is void.

**What a match would and would not show.** A match shows the reported numbers follow from the committed rows. It does
not check the rows against the raw traces (not committed), the task validity rule, or the harness.
