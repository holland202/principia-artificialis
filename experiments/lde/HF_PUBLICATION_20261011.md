# LDE historical evidence publication — 2026-10-11

**State: REPORTED UPLOAD; REMOTE CONTENT MATCH NOT YET VERIFIED.**

> **Superseded in part, 2026-10-22 (W9).** The Azure "exit 1" reading below is superseded by [AZURE_ORIGINAL_RECOVERY_20261011.md](AZURE_ORIGINAL_RECOVERY_20261011.md): on the original VM, `exit_code.txt = 1` came from a failed import (`ModuleNotFoundError: No module named 'lde'`), and the captured confirmatory run's `confirmatory_exit_code.txt` is `0`. The text below is kept as written on 2026-10-11.


The experiment owner executed `huggingface_hub.HfApi.upload_folder` from S25 Termux and supplied the returned commit URL:

- Dataset: https://huggingface.co/datasets/holland202/lde-cross-substrate-research
- Commit: [`bae88da7caead2c8e82480458c65bd5b1faaf760`](https://huggingface.co/datasets/holland202/lde-cross-substrate-research/commit/bae88da7caead2c8e82480458c65bd5b1faaf760)
- Remote prefix: `releases/2026-10-11/lde-cross-substrate-evidence/`
- Local staged source: `LDE_PUBLICATION_20261011T193055Z/huggingface/lde-cross-substrate-evidence/`
- Files selected: 35
- Commit message: `evidence: publish LDE-2G historical cross-substrate records; Azure exit=1`

The preceding local preflight reported no staging hash mismatches or recognized credential patterns. This does not constitute exhaustive privacy review or remote byte-for-byte verification. The original Azure VM remains uninspected in this publication phase.

**Evidence limits:** The locally recorded S25 exit code is `0` (`confirmatory_exit_code.txt`), while Azure records include exit code `1`, notwithstanding identical 4,364-byte stdout SHA-256 `966108ecadf6ce114c6e31846e2bae4c8033260a54b41b47abf5715c5d04934b`. Successful cross-substrate validation remains **NOT ESTABLISHED**. The dataset publication is not a scientific endorsement.

## Verification still required

1. List all files at the pinned Hugging Face commit and compare counts, relative paths, sizes and SHA-256 against the local staging manifest.
2. Confirm the historical experiment provenance against the original Azure VM disk, or mark unavailable.
3. Review the newly public paths for unintended disclosures; handle any discovery as a separate security incident without rewriting local original evidence.
4. Publish Codeberg provenance updates only after reviewing the untracked `azure_environment.txt`; existing `LDE2F_PREREG.md` and `LDE2G_PREREG.md` are already tracked.
5. Keep `LDE-HYP-001-evidence.tar.gz` out of this particular release pending separate decision.
