# R1 provenance and preservation boundary

**Status:** operator-observed evidence, internal integrity verified, independent provenance and verifier qualification pending.

## Execution identity

- Platform: Azure-hosted Ubuntu 24.04.4 LTS, `aarch64`.
- Run label: `unattended-20261011T215619Z`.
- Start: `2026-10-11T21:56:19.356975+00:00`.
- Configured cutoff: `2026-10-12T21:08:00+00:00`.
- Finish: `2026-10-12T21:08:01.516151+00:00`; checkpoint state `DEADLINE_REACHED`.
- The configured window lasted **23 h 11 min 42 s**, not precisely 24 elapsed hours.
- Distinct earlier short run: `unattended-20261011T215443Z`, `STOP_REQUESTED`, 9 recorded executions; **excluded** from R1 totals.

## Locally captured digests

| Artifact | SHA-256 |
| --- | --- |
| Azure archive, `azure24h-R1-20261011T215619Z.tar.gz` | `3bf2ba76ae947c5dd11ecc52060590f30357dd41b5a9ada24dc09ce12bc565de` |
| Campaign instrument, `probe.py` | `832d6ac64f2cdd33288bced12dadbfead0006d462c8b0386192506a7ef015a4d` |
| Campaign controller, `campaign.sh` | `c4df4e04fba2b4106602afe760da37b4468247c8bc39ae969bc9ff7b7fbb1768` |
| Private full-workspace preservation archive | `621b3dc7fcea9ca74ff3f4937f0158ce70f5097acd55ccfa5052059b43f13b47` |

The on-VM manifest (`artifact_hashes.sha256`) contained **93,639 lines**; from its run directory, `sha256sum --check --quiet artifact_hashes.sha256` exited **0**. The transfer of the 21 MB compressed archive from Azure to Termux completed; Termux `sha256sum -c` printed `OK` for the digest above, and `tar -tzf` succeeded. This verifies present-day consistency with those stored digests, **not** independently established authorship, temporal authenticity, or external attestation.

## Private workspace preservation and offline recheck

A later full-workspace capture retained the campaign files, Git repositories, experimental worktrees, virtual environments, and dependency records **privately**. The operator transferred that archive to an S25 device and ran a separate read-only offline preservation audit.

The operator-provided audit output reported **108,192 regular files** matching their archive contents, **25,185 directories** checked, and **48 links** checked. It also reported all **93,639** R1 manifest hashes matching, **93,632 valid JSONL records**, **23,408 complete rounds**, and the same per-project totals published here. The audit's final status was `LOCAL_PRESERVATION_CONSISTENCY_VERIFIED`.

This was a **same-custodian local audit**, not third-party attestation or independent execution of the underlying scientific experiment. Current Git HEADs, dirty-tree status at execution, worktree-to-probe bindings, and exact dependency revisions **at execution time remain unverified**.

## Publication exclusions / limitations

The original 21 MB archive, private 257 MB workspace archive, full raw `results.jsonl`, virtual environments, cloud credentials, SSH keys, and source snapshots are **not** included in these PRs. Private materials require a separate sensitive-data screening and provenance review before any release. The published summary was transcribed from operator-provided output, then checked for accounting consistency by the operator's offline audit; GitHub does not host the raw records.

`slc-v12-` recorded `mock_only: true` on all 23,408 execution records. Other projects' `mock_only` values were **absent**; absence is not evidence of real-world integration. No directly demonstrated adversarial fault-detection controls or independent reproduction are claimed.

## Verification procedure for a future reviewer

1. Obtain the original archive from its custodian by an authenticated delivery channel, check its published SHA-256, and inspect it for sensitive material before redistribution.
2. Extract into a new, isolated directory; do not overwrite the preserved original.
3. From the extracted `runs/unattended-20261011T215619Z` directory, run `sha256sum --check artifact_hashes.sha256` to verify all listed items. This tests consistency, not identity.
4. Run `python3 audit_results.py <extracted-run-directory>` to independently reaggregate the JSONL and compare its checkpoint to this published summary.
5. Independently acquire pinned source revisions and environments; inspect the actual `probe.py` assertions and run discriminatory known-bad controls before making a security claim.
6. Preserve unexpected results, corruption, failure cases, and contradictory artifacts, not just passing totals.

**Verification state:** operator-run offline preservation and record accounting match; execution-time source provenance, adversarial sensitivity, independent reproduction, and physical effects **remain open**.
