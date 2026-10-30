# Codeberg LDE S25 provenance publication — 2026-10-11

**Status: REMOTE_BRANCH_SHA_CONFIRMED_BY_OWNER_TERMINAL; ORIGINAL_AZURE_RECORDS_UNVERIFIED.**

- Canonical source: https://codeberg.org/badatchess/local-discovery-engine
- Published branch: `research/lde-provenance-20261011`
- Remote head SHA reported by `git ls-remote`: `910d230e7449f11dd2ad8bb13fdfa7847bf01e68`
- Commit subject: `evidence: preserve correctly attributed S25 environment snapshot`
- Added source file: `evidence/substrates/s25/environment_20261007.txt`
- File SHA-256: `b65131cccabc5fc15e97e4b4d75d7edd64d8c4d7cc3b1359aacef956950c1a11`
- Direct comparison: https://codeberg.org/badatchess/local-discovery-engine/compare/main...research/lde-provenance-20261011

The source file copied unchanged from locally untracked `azure_environment.txt` actually describes Android 16 / Termux, aarch64, Qualcomm Oryon, Python 3.14.6, and a local LDE checkout at `f979705293849de48e4b40aa8988c046fa5871da`; its original name is misleading. The untracked original was left unchanged. This branch push did not update Codeberg `main` or establish a merged pull request.

The Hugging Face historical evidence commit is `bae88da7caead2c8e82480458c65bd5b1faaf760`, with owner-reported 35/35 pinned remote hash matches. S25 exit=0 and Azure exit=1 remain recorded; neither result independently authenticates the original Azure disk contents. Cross-substrate end-to-end validation **NOT ESTABLISHED**.
