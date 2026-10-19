# Note #040 — External reproduction intake and contributor qualification

**Recorded:** 2026-10-13  
**Investigator (preferred public attribution):** Putluru Sandeep (GitHub: [@sunny-kavixo](https://github.com/sunny-kavixo))  
**Discussion:** [Principia Artificialis #26](https://github.com/holland202/principia-artificialis/issues/26)  
**Evidence report:** [PA_Note040_Reproduction_Evidence.md](https://github.com/user-attachments/files/33395353/PA_Note040_Reproduction_Evidence.md)  
**Source revision investigated:** `9208fb95cb5c0a6d340fd5a46d8099734d4add45`

**Attribution clarification (2026-10-19, administrative only):** The investigator's preferred public credit is **Putluru Sandeep (GitHub: @sunny-kavixo)**. The original record used “Sandeep” and/or the GitHub handle. See [the dated attribution note](ATTRIBUTION_2026-10-19.md); the original numerical findings, limitations, provenance and review disposition are unchanged.

## Administrative decision

**Initial contribution qualification: COMPLETED WITH DOCUMENTED LIMITATIONS.** Sandeep may now propose original research in PA and submit focused pull requests for maintainer review. This status concerns contributor onboarding, **not independent validation** of Note #040's scientific claims. No direct repository write access is granted by this record.

## Investigator's reported experiment

The reported environment is MacBook Air M4, macOS 27.0.1, Python 3.14.5, NumPy 2.4.6, SciPy 1.18.0. Running `python3 scripts/check_numbers.py --only 040` reportedly exited 0, with anti-vacuity check PASS, 3 of 5 numerical tokens found, and historical values `+0.7133` and `+0.7203` marked NOT FOUND in current reference output. An exit code 0 means the audit completed, not that every number matched.

Reported recomputation using existing `n40.npz` arrays:
- Double argsort, quicksort / heapsort / mergesort / stable: `0.720279720` in NumPy 2.4.6.
- Tie-aware SciPy Spearman: `0.7817719990481259`.
- Historical `+0.7133`: not reproduced in this reported environment.

The investigator disclosed ChatGPT GPT-6 assistance in experimental planning, code review, command construction, interpretation, and report drafting; the listed commands were human-executed. The experiment did **not** independently rerun full model training.

## Follow-up numerical check (separate evidence)

A subsequent AI-assisted local calculation from the **12 R and KO array values transcribed in the report** yielded approximately `0.713286713` under NumPy 2.3.5 quicksort, and `0.720279720` under stable sorting. This suggests sensitivity to tied-rank ordering; it **does not prove** the original historical environment or establish that the local arrays are byte-identical to the investigator's file. Preserve this as a follow-up observation requiring its own pinned executable evidence, rather than a correction to the original reference note. Historical heapsort claims also require separate reconciliation.

## Open provenance and validity questions

1. Input file `n40.npz` creation provenance, SHA-256 and exact correspondence across environments not established.
2. Original raw terminal log files and individual pipeline exit codes not attached; report transcribes observations.
3. Full reference training run not reproduced independently.
4. Original historical NumPy environment and explanation of `+0.7133` not reconstructed.
5. No independent validation of the broader fault-tolerance prediction.

**Finding status:** PARTIAL NUMERICAL REPRODUCTION; HISTORICAL SORT BEHAVIOR UNDER INVESTIGATION; SCIENTIFIC VALIDATION NOT ESTABLISHED.

## Follow-on process

Future independent proposals by Sandeep start as proposals, not endorsed results. Require explicit scope, testable predictions, failure conditions, reproducibility, provenance, AI-assistance disclosure and appropriate licensing/attribution. Preserve negative findings. Review changes through issues/pull requests; no elevated repository permissions are necessary.
