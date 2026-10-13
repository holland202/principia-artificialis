# Azure ARM64 R1 endurance campaign — 2026-10-11 to 2026-10-12

**Evidence class:** operator-provided terminal output, cross-checked against a reported JSONL scan and SHA-256 manifest verification.  
**Publication state:** preliminary, instrument qualification incomplete.  
**Scope:** four local experimental probes on Azure VM `lde-test-03` (Ubuntu 24.04.4, aarch64). This is **not** a production security certification or an independent reproduction.

## Observed execution result

| Field | Recorded value |
| --- | ---: |
| Campaign start (UTC) | 2026-10-11T21:56:19.356975+00:00 |
| Configured deadline (UTC) | 2026-10-12T21:08:00+00:00 |
| Recorded finish (UTC) | 2026-10-12T21:08:01.516151+00:00 |
| Elapsed wall time | about 23 h 11 min 42 s, **not 24 elapsed hours** |
| Final checkpoint state | `DEADLINE_REACHED` |
| Complete rounds | 23,408 |
| Executions | 93,632 |
| Execution `status=PASS` | 93,632 |
| `parsed.outcome=PASS` | 93,632 |
| Nonzero exit codes | 0 |
| Timeouts | 0 |
| Nonempty `parsed.failures` lists | 0 |
| Invalid JSONL records | 0 |
| Reported seed slots | 1,123,584 |
| Reported internal checks | 36,963,662 |
| Reported findings | 0 |
| SHA-256 manifest lines | 93,639 |
| `sha256sum --check --quiet artifact_hashes.sha256` | exit 0 (Azure) |

Every one of the 23,408 distinct round identifiers had four recorded project executions. The independently interrupted short run (`unattended-20261011T215443Z`, state `STOP_REQUESTED`, 9 project runs) is **not** counted in the above campaign.

## Per-project accounting

| Project | Executions | PASS | Seed slots | Internal checks | Timeouts | `mock_only` annotation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `evidence-ledger` | 23,408 | 23,408 | 280,896 | 21,090,608 | 0 | absent in records sampled/aggregated |
| `skn-v1-` | 23,408 | 23,408 | 280,896 | 5,337,024 | 0 | absent in records sampled/aggregated |
| `slc-v12-` | 23,408 | 23,408 | 280,896 | 9,131,550 | 0 | true for all 23,408 |
| `veritas-companion` | 23,408 | 23,408 | 280,896 | 1,404,480 | 0 | absent in records sampled/aggregated |
| **Total** | **93,632** | **93,632** | **1,123,584** | **36,963,662** | **0** | |

*Seed slots count uses the recorded `seed_count` totals. It does not establish unique, independent, or statistically representative seeds. An internal "check" is a harness-reported counter, not necessarily an independent property assertion.*

## Interpretation / claim boundary

**Supported by available records:** The harness recorded uninterrupted passing executions through the configured deadline; JSONL record counting and project/round accounting reconcile; SHA-256 verification on Azure found no content mismatches in the manifest entries; a compressed evidence archive was transferred to the S25 and matched the recorded archive SHA-256.

**Not established:** (1) independent authenticity of the original observations; (2) exact source revisions used at execution time; (3) independence of sampled seeds; (4) effectiveness against known-bad mutations; (5) physical-world or full platform integration; (6) external scientific reproduction. The `slc-v12-` results explicitly report mock-only execution. Missing `mock_only` fields in other records must **not** be interpreted as physical integration.

An all-pass endurance run supports stability **under tested inputs and the existing probe**. It cannot establish that the detector would reject an unknown exploit or a deliberately sabotaged implementation. Zero *reported* findings is not proof of absence of defects.

## Reanalysis

Run `python3 audit_results.py /path/to/extracted/runs/unattended-20261011T215619Z` to compute a fresh project rollup from the JSONL and compare the checkpoint counts. The checked-in `summary.json` is a transcript-derived transcription, not output directly obtained by this repository from Azure.

The original 21 MB archive is **not** included in this draft. It remains on the operator's S25; source trees and virtual environment state require separate preservation and attribution. See [PROVENANCE.md](PROVENANCE.md) for archive digests, incomplete source attribution, and publication safeguards.
