# Fresh-clone verification of the engineering checkpoint

2026-10-20. Software only; same ChatGPT author, independent scientific review NOT performed.

Tested public GitHub commit: `76f112400e15ed237cd595ea66fb6781298cf136`.
Implementation/evidence commit: `c36ba33ecbc7dde1160a82dc2e613d41367340e0`.
Pre-execution plan: `4bdaa6535984716fa4816ad5d50c2c55a60e169f`.
Main remained outside this work; no merge or findings release occurred.

A fresh GitHub clone (no local reference/cache) and new no-package Python 3.12.14
venv reproduced the complete engineering gate, exit 0. The clone was clean before
testing; 331 scoped files matched the development checkpoint byte-for-byte with
MD5 and SHA-256 recorded in `evidence/stage2/cold-clone-transfer.json`.
Exact clone command, output and status: `evidence/stage2/clone-transport/`.
Exact verification command, outputs, interpreter/platform, source hashes and status:
`evidence/stage2/cold-clone-run1/` and `cold-clone-data1/`.

Observed afresh: 32 tests in normal/-O/-OO; three identical 240-case calibration
digests; 114/114 construction labels; always-accept/always-reject controls exit 1;
eight selected source mutants produce actual assertion failures after a passing
baseline, with no child errors and unchanged source hashes. Calibration remains
201 accepted / 39 UNRESOLVABLE, with no change to the preselected policy.

GitHub engineering CI also passed its three jobs (Python 3.11, 3.12, 3.13), including
the complete gate and whole-gate sabotage expecting exit exactly 1:
[run 39448477831](https://github.com/holland202/principia-artificialis/actions/runs/39448477831).
Snapshot and job-step metadata: `evidence/stage2/ci-checkpoint-76f1124.json`.
The separate pre-existing verify-all-notes workflow was still running when that
snapshot was taken; its status must not be represented as passed by this report.

## Frozen engineering identity
The bounded software/calibration build meets Gate A for these files at the tested
commit. This is **not** closure of the research hypothesis or independent validation.

| File | MD5 at tested commit |
|---|---|
| ns001.py | 55480877c0f0408dfd666555393ab2d4 |
| analytic_oracle.py | 78d3cbdceaa9abe6f7ae0f63a80cfa0f |
| test_ns001.py | ff528b9fb505647e9153bf17a7516d2e |
| test_stage2.py | d4816085f6c53ba8003eef23e5aae6df |
| test_package.py | d33c5d5da28f8a6123d17bb88e85844b |
| test_study_design.py | c1acdab095af19cd0684dcc6c68dfbd7 |
| engineering_gate.py | 6acc35717d4a4a53fa77461f8351e3fa |
| RECORDED.json | 46280f017cab51f4f7347e10f3ca07d4 |

The accompanying MANIFEST.json inventories the final review package with byte sizes,
SHA-256 and MD5. It deliberately excludes itself and the package-audit output folder
to avoid recursive hashes; package-audit RUN.json records the manifest's source hash.
The trusted Git commit and source-provenance review are required in addition to
this consistency check. A self-consistent rewritten package is not authenticated.

From the repository root:

```sh
python research/pa_ns001/verify_package.py --root . --manifest research/pa_ns001/MANIFEST.json
```

Ready for **Gate B independent oracle/fault review**. Gate C remains blocked on the
research-target, precision/domain, model, budget, methodological applicability and
freeze decisions in OWNER_DECISIONS.md. No AI study execution is authorized here.
