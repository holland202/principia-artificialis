# Owner decisions before the next scientific execution gate

2026-10-20; development branch only. No AI evaluation or spending authorized.

| Decision | Concrete proposal | Why approval/review is required |
|---|---|---|
| Gate B reviewer | Independent fluid-mechanics/numerical-analysis review of ORACLE_AND_FAULTS.md, fixtures and numerical policy | Same-author code separation does not satisfy independent review; no contact authorized |
| Research target | Start with controlled AI review of supplied profiles (A); defer AI-generated profiles (B) | A changes the original question's scope; it cannot be silently substituted |
| Precision contract | Review dimensionless engineering policy v1; 16-epsilon floor, 1e-6 sample-resolution cap, .01 momentum cap; exact-zero rule | These are preselected engineering proposals, not approved scientific criteria; 39/240 calibration cases remain unresolved |
| Confirmatory design | 400 invalid + 400 valid IID mixture units, one cached AI response per unit; B/V/profile-only arms | Replaces the illustrative 200-total target; requires sample/cost and IID-assumption approval |
| Meaningful effect | >=5 percentage-point FAR reduction lower confidence bound, <=2-point added false-rejection upper bound | Values reflect a proposed usefulness criterion, not established PA policy |
| Model and budgets | Freeze exact model/prompt/decoding/token ceilings and retry policy; explicitly approve any API spending | No external AI calls were made; no provider/credential/resource decision inferred |
| Method applicability | Resolve C-METHCOMP | Canonical control refers to a parked experiment-specific protocol; this is not authority to change it |
| Freeze and execution | Commit a separately approved preregistration and independent case/analysis manifests before fresh main cases | Current draft and observed engineering cases cannot be retrospectively confirmatory |
| Publication/integration | Separate review before main merge, scientific claims or release | Current authorization covers this development branch only |

Root FORKS.md entry appended for this engineering exploration (no other inquiry altered):

`2026-10-20 | PA-NS001-S2 | fixed-grid analytic verifier calibration, invalid-input diagnostics and constructed faults | plan 4bdaa6535984716fa4816ad5d50c2c55a60e169f; source hashes in evidence RUN.json | public Stage 2 engineering fixtures, no main study cases | Python 3.12.14 Linux container | 3 identical 240-case calibration digests, 114 construction checks; 39 unresolved rounded profiles | EXPLORATORY | engineering only; independent review pending`

The append-only disclosure is an engineering record, not a new scientific registration.
No other program's registration is changed. No decision above is marked approved
merely because the document exists.
