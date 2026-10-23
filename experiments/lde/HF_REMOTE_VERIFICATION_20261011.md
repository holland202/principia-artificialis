# Hugging Face pinned-revision verification — 2026-10-11

**Status: REMOTE_CONTENT_MATCH_REPORTED; SOURCE_AUTHENTICITY_NOT_ESTABLISHED.**

> **Superseded in part, 2026-10-22 (W9).** The Azure "exit 1" reading below is superseded by [AZURE_ORIGINAL_RECOVERY_20261011.md](AZURE_ORIGINAL_RECOVERY_20261011.md): on the original VM, `exit_code.txt = 1` came from a failed import (`ModuleNotFoundError: No module named 'lde'`), and the captured confirmatory run's `confirmatory_exit_code.txt` is `0`. The text below is kept as written on 2026-10-11.


Owner executed an S25 Termux `huggingface_hub` download-and-SHA-256 comparison against the published dataset revision and provided the terminal output.

- Dataset: `holland202/lde-cross-substrate-research`
- Revision: [`bae88da7caead2c8e82480458c65bd5b1faaf760`](https://huggingface.co/datasets/holland202/lde-cross-substrate-research/commit/bae88da7caead2c8e82480458c65bd5b1faaf760)
- Prefix: `releases/2026-10-11/lde-cross-substrate-evidence/`
- Expected files: **35**
- Listed remote files: **35**
- SHA-256 matches after remote download: **35**
- Missing / unexpected / mismatching: **0 / 0 / 0**
- Retrieval errors: **0**
- Terminal status: `PINNED REMOTE CONTENT VERIFIED`

**Scope:** Owner-run byte comparison between staged local copies and the pinned Hugging Face revision. The individual hashes and complete transcript have not been independently supplied to the PA repository; this file accurately records the reported check rather than claiming a separate reviewer reproduced it.

**Scientific status unchanged:** S25 confirmatory exit `0`; Azure confirmatory exit `1`; stdout hashes match. The Azure source machine originals and historical executed source revision have not been independently verified. No claim of successful end-to-end cross-substrate validation follows.

**Next:** review and publish Codeberg provenance update, pin its commit; compare original Azure disk records if available; optionally attach a sanitized detailed SHA-256 verification manifest to this PR.
