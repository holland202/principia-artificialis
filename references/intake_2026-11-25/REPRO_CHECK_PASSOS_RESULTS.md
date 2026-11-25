# Results: "One Run Is Not Enough" (arXiv:2611.19359) reproduced from its own committed rows

Registration: [`REPRO_CHECK_PASSOS_REGISTRATION.md`](REPRO_CHECK_PASSOS_REGISTRATION.md), commit `f6f8261`, pushed before
anything was computed. Study repo: github.com/renorai/gemma4-memory-study at `2eea9c6` (Apache-2.0).
Run by Claude (Anthropic, Opus 5.5) in a Linux container, 2026-11-25. Human review: none. Self-tested.

## Deviation first

The registration said E1–E3 would be checked by running the authors' `results/analyze_rows.py`. This session's
safety controls refused to run code downloaded from the study repo. Instead, E1–E3 were recomputed by Claude's own
script, [`repro_check_passos.py`](repro_check_passos.py), which reads only `run_rows.jsonl` and imports nothing from
the study repo. Its pairing rule was read from the authors' script, so it is not independent of their choices.
The 95% interval was not recomputed; it is compared with the authors' committed `results/analysis.json` only.

## Output (verbatim, `repro_check_passos_output.txt`)

```
primary_48                         pairs 48  recap 29  none 25  diff +8.3 pts  discordant recap-only 5 none-only 1  exact McNemar p 0.2188
extension_50                       pairs 50  recap 18  none 23  diff -10.0 pts  discordant recap-only 1 none-only 6  exact McNemar p 0.1250
combined_98                        pairs 98  recap 47  none 48  diff -1.0 pts  discordant recap-only 6 none-only 7  exact McNemar p 1.0000
flip_none_run2_vs_run1_modal       pairs 16  flipped 3  (18.8%)
flip_none_run2_vs_run1_kaggle      pairs 32  flipped 6  (18.8%)
flip_none_run2_vs_run1_all         pairs 48  flipped 9  (18.8%)
```

| ID | Result |
|---|---|
| E1 | **Matches.** 47/98 vs 48/98, −1.0 points, p = 1.0. Interval: the authors' committed `analysis.json` gives Newcombe [−0.0834, +0.0633], i.e. the abstract's [−8.3, +6.3]; not recomputed here |
| E2 | **Matches.** 29 vs 25, p = 0.2188 (abstract: 0.22); 18 vs 23, p = 0.125 |
| E3 | **Matches.** 9 of 48 identical no-memory pairs flip (18.8%; abstract: 19%). It is measured on the 48 Modal and Kaggle tasks, not on all 98 |
| E4 | **Holds.** `PREREG.md` first committed `07d0a72` (2026-11-07 12:11 UTC); `run_rows.jsonl` first committed `8ca3806` (2026-11-09 07:53 UTC). The paper itself discloses that its 48-pair primary was a deviation, and the repo's commit `ab88cf0` removes "pre-registered" from that figure |
| E5 | **Matches.** Claude's own two-sided exact McNemar gives the same p for all three blocks |

Anti-vacuity: with one paired recap outcome flipped, the combined block reports recap 48, not 47
(`repro_check_passos_sabotage.txt`). The check can move.

## One observation (Claude's, not the paper's)

On the 48 primary tasks, the two arms disagree on 6 tasks (12.5%). Two identical no-memory runs on the same 48 tasks
disagree on 9 (18.8%). The treatment changed outcomes less often than rerunning the control did. That is what a null
looks like, and it is the paper's point: a single run per arm cannot separate a reminder effect from rerun noise.

## What this does not show

It does not check the rows against the raw traces (not committed), the task validity rule (129 → 105), the harness,
or the model. It is a second computation on the authors' data, not a replication.
