# LDE cross-substrate evidence index — intake 2026-10-11

**Status: INTAKE / NOT INDEPENDENTLY VERIFIED.** This is a claim and source-location index based on a Termux audit transcript supplied by the experiment owner. It is not a copy of the primary data, an independent rerun, or a certification of the Azure VM's current disk contents. Do not treat this index as a normative amendment to PA's methodology.

> **Superseded in part, 2026-10-22 (W9).** The Azure "exit 1" reading below is superseded by [AZURE_ORIGINAL_RECOVERY_20261011.md](AZURE_ORIGINAL_RECOVERY_20261011.md): on the original VM, `exit_code.txt = 1` came from a failed import (`ModuleNotFoundError: No module named 'lde'`), and the captured confirmatory run's `confirmatory_exit_code.txt` is `0`. The text below is kept as written on 2026-10-11.


## Authoritative locations and roles

- **Source / frozen experiment code:** [Codeberg local-discovery-engine](https://codeberg.org/badatchess/local-discovery-engine). Record exact commit hashes for each execution, not only a branch name.
- **Research data / archived run records:** [Hugging Face lde-cross-substrate-research](https://huggingface.co/datasets/holland202/lde-cross-substrate-research). Dataset revision and complete file-level hash match remain to be checked.
- **Research method / cross-project review:** this PA repository, with this index in `experiments/lde/`. No raw machine-home export should be committed without inspection.
- **Original Azure VM files:** `lde-test-02` (Ubuntu x86_64), **not directly inspected for this intake**; local copies of Azure-named evidence exist on an S25 Termux host.

## Recorded intake observations (owner-provided terminal output)

Collection directory: `~/LDE_AUDIT_20261011T191812Z/` on an Android aarch64 Termux installation.

| Observation | Value | Verification |
| --- | --- | --- |
| File instances inventoried / hashed | 738 | Owner's local audit report; manifest not independently inspected |
| Distinct SHA-256 values | 467 | Owner's local deduplication script |
| Repeated-content instances | 271 | 738 minus 467; does not imply dispensability |
| Duplicate-hash groups | 109 | Owner's local deduplication script |
| Reported read/hash errors | 0 | Script-reported; scan scope limited to eight directories |
| Local engine Git HEAD at time of audit | `f979705293849de48e4b40aa8988c046fa5871da` | Does **not** establish historical Azure executed revision |

Eight scanned directories: `local-discovery-engine` (316), `lde-cross-substrate-evidence` (35), `lde-hf-audit` (60), `hf-azure-audit-20261008` (172), `lde-hf-roundtrip` (8), `lde-course-publish-20261008` (117), `lde-hyp001-batch` (3), `lde-cross-substrate-evidence-hf-check` (27).

### LDE-2G confirmatory output

| Property | S25 ARM64 | Azure-named local record |
| --- | --- | --- |
| Cases | 60 | 60 |
| Selected maximal | 49 | 49 |
| Selection rate | 0.816667 (reported) | 0.816667 (reported) |
| Mean selected discrimination | 3.8 | 3.8 |
| Mean maximum discrimination | 4.0 | 4.0 |
| Stdout size | 4,364 bytes | 4,364 bytes |
| Stdout SHA-256 | `966108ecadf6ce114c6e31846e2bae4c8033260a54b41b47abf5715c5d04934b` | same |
| Exit state | `exit_code: 0` in `result_summary.json`; standalone `exit_code.txt` missing | standalone `exit_code.txt` is `1` |
| stderr | Reported empty | Reported empty |

The Azure-named summary records `non_maximal: 11`, `primary_hypothesis_supported: false`, and seed range 0–59. These records are consistent with non-maximal seed IDs 7, 8, 9, 17, 20, 28, 30, 34, 44, 54, 59 from prior experiment notes, but this intake has **not** independently enumerated all 60 trial rows.

**Critical limitation:** Matching stdout bytes are not evidence of successful end-to-end cross-substrate reproduction. The historical Azure execution was recorded with exit code 1; previous investigation associated that failure with unavailable `pytest`. Preserve the failure; do not silently replace it with a later success. The S25 standalone exit-code evidence is missing in this selected archive, despite `exit_code: 0` appearing in its summary.

## Provenance and publication gates

1. Preserve original artifacts on each host, including failed and partial runs. Recompute hashes from source bytes before making any authenticity claim.
2. Collect read-only inventory and original experiment outputs from Azure's persistent disk when accessible; preserve host metadata, timestamps, exact command, shell exit status, stderr, source revision and environment.
3. Reconcile local S25 copies with original Azure and the Hugging Face dataset at a **pinned revision**. Mark each artifact as MATCH / MISMATCH / ABSENT / ACCESS_UNVERIFIED.
4. Review each proposed public file for credentials, tokens, SSH keys, private endpoints, and other sensitive data. Publish only reviewed files. Record any redaction as a new derivative with its own hash; never alter an original silently.
5. Add full manifests with paths, file hashes, source commit IDs, dataset revision, date of retrieval, and access status. Keep claim status separate from test output.
6. Do not infer independent validation from hash equality, process success, summary JSON, or internal consistency alone.

**Open status:** ORIGINAL_AZURE_ACCESS_UNVERIFIED; HF_DATASET_REVISION_UNVERIFIED; HISTORICAL_EXECUTED_SOURCE_REVISION_UNVERIFIED; CROSS_SUBSTRATE_VALIDATION_NOT_ESTABLISHED.

This index is suitable for review before primary source files are uploaded. It deliberately contains no credentials or machine configuration dumps.
