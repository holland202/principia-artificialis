# Sandeep EGRR — Historical Research Archive Snapshot (2026-10-14)

**Record type:** Historical contributor-archive snapshot (PA WORKFLOW.md W9). **Status:** ARCHIVED AS SUBMITTED; **NOT** a registered experiment, confirmatory validation, or endorsement of the research hypothesis.

**Originating investigator:** [Sandeep / @sunny-kavixo](https://github.com/sunny-kavixo)  
**Archive decision and curation:** Chad Holland, with AI-assisted drafting/review (OpenAI ChatGPT GPT-6); no author or ownership transfer.  
**Recorded:** 2026-10-14 UTC. **Target:** Principia Artificialis's durable public Git history.

## Exact provenance and scope

- [Contributor qualification and Note #040 evidence record](../../NOTE040_INITIAL_REVIEW.md) (already on PA main; retained in place), with the unresolved historical `+0.7133` discrepancy.
- [PA research Issue #28](https://github.com/holland202/principia-artificialis/issues/28): Sandeep's original EGRR proposal, authorized for **protocol development only**.
- [PA PR #37](https://github.com/holland202/principia-artificialis/pull/37): original code, protocol versions, documented exploration, and mathematical feasibility review; **not merged by this archive**. Snapshot reference commit `e93035809897b10f6895168b51021f76e3fa79c3`.
- [Sandeep's fork draft PR #1](https://github.com/sunny-kavixo/principia-artificialis/pull/1): the one-document EGRR-DESC-001 study proposal; snapshot commit `b467f1ee7f1c2c2ea36abae0ac148a385abff17f`. **Draft / design-only.**
- `records/FORKS_PR37_SUBMITTED.md` is a **verbatim snapshot of the submitted branch's FORKS.md**, including F-003. It is not an amendment to PA's canonical root FORKS.md.

Every file listed in the manifest below is copied **without changing the submitted text** from the specified fork commit. Python source/test files have a `.py.txt` archive extension only to prevent automated test discovery or accidental integration into PA's live research tooling; restore the original `.py` filename only in a separately reviewed reproducibility environment. The source contents remain unchanged.

## Observations that are preserved without promotion

**Historical exploratory local synthetic case (Sandeep-reported, 2026-10-13):**
- Normal synthetic `W` 16×8, calibration `X` 64×16, seed 28, symmetric 3-bit quantizer, 8 corrections.
- Sandeep reported calibration MSEs: covariance-greedy **0.8220074902**, residual magnitude **0.8896527392**, input-RMS **0.9210985039**, random **0.9731676638**, and **111 EGR2 bytes** for each corrected arm.
- **The same calibration inputs were used for selection and evaluation.** This does **not** demonstrate held-out improvement or generalization.

**Separate structural tests (investigator-reported):**
- The later 64×32, K=128 matched-storage check reported **1,311 bytes** for each corrected arm; decoder/reconstruction checks are available as submitted source/test files.
- Sandeep reported **21 of 21 local structural and numerical tests passing** at commit `2885adbc03ee44ca5032dda06a686d7b8ffb5434`. Test logs/exits have **not been independently reproduced by PA in this archive**; reported test success is not a scientific result.
- Reported historical environment for the exploratory materials: Python **3.14.5**, NumPy **2.4.6**, macOS arm64.

**Negative / unresolved analysis kept intact:**
- The population P1 estimand is `E[1 - MSE_covariance / MSE_magnitude]`. A useful pre-data lower support bound or proven variance bound has **not** been established. The proposed fixed-sample 5% significance claim is **UNRESOLVED / NOT APPROVED**, as described in `records/egrr_issue28_statistical_feasibility.md`.
- Earlier numerical tolerances, initial protocol drafts, historical provenance gaps, and reviewer criticism stay on record. No unfavorable findings are removed or overwritten.
- The proposed EGRR-DESC-001 **100-seed descriptive study has NOT RUN**; no frozen registration, approval to generate its evaluation arrays, or execution has occurred. The seed choice remains subject to review. A descriptive study would not constitute a population-inference test or a real-LLM benchmark.

## What is NOT in this archive

Original **raw synthetic arrays, original run logs/stdout/stderr, full historical local workspace code, complete original run commands, independent test outputs, or a completed 100-seed dataset** have not been provided here. The historical source-file SHA-256 values recorded by Sandeep cannot by themselves establish which exact local source revision generated his older observations. This archive **does not pretend those missing bytes exist**. Published numerical summaries are transcriptions of his attributed observations, not independent remeasurements.

## Source snapshot SHA-256 manifest

SHA-256 values below refer to the **exact UTF-8 file contents** preserved at the indicated archive paths, separately checked against the original Git blob identities. All paths are relative to this directory. The original submitted paths are unchanged except for the archival directory prefix and `.txt` extension for Python files.

| Archived file | SHA-256 (exact contents) |
|---|---|
| `records/egrr_issue28_exploration_provenance.md` | `67f07ea799eaebde0dffcedbbb14ff574810e0831f86b4abd1bfa6639273dc55` |
| `records/egrr_issue28_statistical_feasibility.md` | `a642ed125832ee8cbc0c67c491d41185d940790ff1e244ea561f6fbffdef51a6` |
| `records/egrr_issue28_protocol_draft.md` | `94dc0ff93902319e431f63aa0a148cbf75b29904cefb0fd3bd0872734ee10eb8` |
| `records/EGRR-DESC-001_DRAFT.md` | `187c4bdc804bab7a065353176c1b1a1784d384dcd395368d765222e38506deda` |
| `records/FORKS_PR37_SUBMITTED.md` | `aaa32f536ced9a755aea8c1266f1b6c8962e88ad51c336cf04ac2889ac3c9c82` |
| `source/covariance_float16.py.txt` | `51389fda50ee09034806e6a4b12bb395de14de6ce8e29830ef12d64bbc8d5b6c` |
| `source/egrr.py.txt` | `a1057838af2384f37029189e74ad59ce1a9d6f5d84b62ece9ae22b482992cd29` |
| `source/packing.py.txt` | `c1fa507ab1ec4b7e493ed5e388bdf31a9bc8a235e8ca5aaaab082ddb36f44097` |
| `source/primary_scoring.py.txt` | `10adfc9b3b13e58389e513ceab7a5f416dc062a5db9962b7b96c90a587fa3717` |
| `source/storage.py.txt` | `1a20b6ec271ec4bb7d47e3d0f65a284559efc83ab2f0a1457e09dbd349b4f6f1` |
| `source/structural_gate.py.txt` | `91a6c871fd01616e9e8e6363de5207f4d9d35fccba09933377011fb59d90c440` |
| `source/test_covariance_safety.py.txt` | `fc6c95561fd6ae6e0362e4dd75822a188ac90831d1e3c4cc34a40431bf2eb4b4` |
| `source/test_matched_bytes.py.txt` | `122fec7a034308370ce09f2c9fd4642676d592a37d46c02cb7c670c249ef39e0` |
| `source/test_primary_scoring.py.txt` | `193b504379b8b0ca35daf5d98177e569cc46a47f4be2307ce0c264b1b407c3b8` |
| `source/test_reserved_code.py.txt` | `c17092a539e7bd5ad1c4b5b6504a21b3d10f1ff43a1c118d95f1f9e750185d7e` |
| `source/test_scoring_safety.py.txt` | `d8324827ca2e2581b092414c0c6ee3e886340c1bbb298dd320c697ae1dcce430` |

## Research governance and future updates

This is a **W9 documentation/evidence-preservation action**, not M2 registration, W4 experiment, scientific endorsement or permission to merge the source-development PR. Sandeep remains the originating investigator and retains authorship credit. The repository's [MIT license](../../../../LICENSE) remains applicable, without any invented assignment of rights. Any future raw data or revised results should be deposited in an **additive, separately attributed, dated supplement** with raw-file hashes and original execution logs; do not retroactively rewrite this snapshot.

**No new EGRR experiment was run, and no change to METHOD.md, WORKFLOW.md, CONTROLS.md, or the original population P1 claim was made for this archival action.**
