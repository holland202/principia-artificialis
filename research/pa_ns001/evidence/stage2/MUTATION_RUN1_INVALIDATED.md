# First mutation run is not promotion evidence

2026-10-20, ChatGPT (OpenAI GPT-6), owner direction only.

The first mutation execution overlapped with creation of `test_study_design.py`.
Its child processes consequently ran different test counts (23 then 27), and the
new NIST example test initially treated an approximate published root too strictly.
That unrelated test failed in some mutated children. The full raw outputs are kept
in `mutations-run1/` and `mutations-data1/`; the reported 8/8 summary is **invalidated**
as a clean mutation comparison. It must not be used to establish guard coverage.

The statistical test was corrected to distinguish the approximate published example
from binomial-CDF inversion and to check the CDF at both numerical roots. The
mutation runner now requires a passing unmutated baseline and hashes every Python
source before/after the full run. The fresh `mutations-run2/` is the intended evidence.
No calibration thresholds, fixed case matrix or fault labels changed.
