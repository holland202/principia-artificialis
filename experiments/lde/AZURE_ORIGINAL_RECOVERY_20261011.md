# Original Azure LDE forensic recovery — 2026-10-11

**Status: OWNER-OBSERVED VM ORIGINALS; HF ORIGINAL-COMPARISON PENDING; SCIENTIFIC VALIDATION NOT ESTABLISHED.**

The owner connected by SSH to Azure VM `lde-test-02` (Ubuntu 24.04.4 x86_64, Python 3.12.3), inspected `/home/azureuser/lde-cross-substrate-evidence`, and supplied read-only terminal outputs. This note supersedes the earlier *interpretation* that `exit_code.txt=1` was the final confirmatory process exit. It does not delete or rewrite prior reports.

## Distinct executions

- `04_confirmatory/azure/exit_code.txt`: `1`, timestamp 2026-10-07 16:11:01 UTC.
- `04_confirmatory/azure/failed_attempt_status.txt`: `INVALID ATTEMPT — direct script invocation failed before experiment execution. Failure: ModuleNotFoundError: No module named 'lde'` (timestamp 16:12:15 UTC).
- `04_confirmatory/azure/confirmatory_exit_code.txt`: `0`, timestamp 16:12:18 UTC.
- `04_confirmatory/azure/confirmatory_stderr.txt`: 0 bytes.
- `04_confirmatory/azure/confirmatory_stdout.txt`: 4,364 bytes; SHA-256 `966108ecadf6ce114c6e31846e2bae4c8033260a54b41b47abf5715c5d04934b`.
- `04_confirmatory/azure/result_summary.json`: 7,786 bytes, mtime 16:14:05 UTC.
- The initial stdout file is empty and stderr is 259 bytes; both are preserved.

**Inference, not direct attestation:** Timestamps and filenames are consistent with an initial import failure followed by a successful captured command. The exact subsequent invocation and historical runtime inputs still require inspection. An exit code of zero does not establish that the preregistered hypothesis was supported.

## Source provenance

- Historical source revision in `02_source/commit.txt`: `f979705293849de48e4b40aa8988c046fa5871da`.
- Current Azure checkout: `81c6578f5c2dbff62c6ef8905d211f68798694de` (`Record LDE-2G Azure cross-substrate execution`, timestamp 2026-10-07 21:50:02 UTC).
- Historical source hashes recorded in `02_source/source_hashes.txt` for eight protocol/script/module/test files. Exact correspondence to the frozen historical commit has **not** been independently rechecked.
- Current Azure worktree additionally has untracked `evidence/05_exploratory/` and `experiments/exploratory/` directories. Preserve these before any cleanup.

## Fifteen original files on Azure

Original directory contains 15 files: `01_preregistration/LDE2G_PREREG.md`; `02_source/{commit.txt,source_hashes.txt}`; `03_substrates/s25/environment.txt`; and `04_confirmatory/azure/{artifact_hashes.txt,command.txt,confirmatory_exit_code.txt,confirmatory_stderr.txt,confirmatory_stdout.txt,environment.txt,exit_code.txt,failed_attempt_status.txt,result_summary.json,stderr.txt,stdout.txt}`.

## Cross-host and publication state

- On S25, confirmatory exit file records `0` and captured stdout SHA-256 equals Azure's.
- Hugging Face: [published release `bae88da7caead2c8e82480458c65bd5b1faaf760`](https://huggingface.co/datasets/holland202/lde-cross-substrate-research/commit/bae88da7caead2c8e82480458c65bd5b1faaf760) (owner-reported pinned 35/35 matches against **S25 staged** artifacts, not yet verified against Azure disk originals).
- Codeberg: branch `research/lde-provenance-20261011`, remote commit `910d230e7449f11dd2ad8bb13fdfa7847bf01e68`, contains correctly attributed S25 environment snapshot; not merged into main.

## Required checks before closure

1. Export and verify original Azure files plus untracked exploratory files without modifying their historical bytes.
2. Compare all 15 Azure originals to corresponding files at the pinned Hugging Face release; record MATCH, MISMATCH, ABSENT, with full per-file SHA-256.
3. Confirm frozen source hashes at historical revision and distinguish current checkout from executed source.
4. Preserve the failed import attempt and the successful confirmatory exit separately; do not infer hypothesis success.
5. Publish any genuinely missing original evidence at new, uniquely versioned dataset paths after scanning, then pin resulting revisions here.
6. Deallocate the Azure VM once originals are safely copied and verified.

**Claim status: ORIGINAL_VM_ACCESSED; TWO_RECORDED_EXIT_STATUSES; CROSS_SUBSTRATE_SCIENTIFIC_VALIDATION_NOT_ESTABLISHED.**
