# FORKS.md - SWAY fork ledger (append-only)

One line per exploratory move:

date | fork id | what was tried | code md5/commit | data id | env | observation | EXPLORATORY | abandoned/continued/promoted

Ledger opened 2026-09-22 at SWAY adoption. No forks yet.
2026-09-30 | F-001 | reviewed 15 ChatGPT + Grok method proposals against the week's real failures | METHOD_SWAY_AMENDMENT_1.md | incidents C006, C006b, C007, C002, issue #4 | container | 8 had a failure behind them, 5 did not | EXPLORATORY | promoted to Amendment 1 (8 adopted, 5 doors); P5 unrun
2026-10-03 | F-002 | methodology simplification audit and design review: duplicated rules, unused machinery, contradictions; a 10-rule core checked against the 12 recorded incidents | METHOD_SWAY_AMENDMENT_3.md (registered 0c634a1) | the 7 method texts (232 items) | container | 3 contradictions; 12 of 12 incidents covered by the core (self-tested); e-value machinery used 0 times (the audit had said 1: a false match) | EXPLORATORY | promoted to Amendment 3
2026-10-13 | F-003 | EGRR covariance-greedy residual selection versus magnitude, RMS and random on one synthetic calibration-only linear-layer case | source SHA-256 identities recorded in research_notes/egrr_issue28_exploration_provenance.md; exact historical code revision unverified | synthetic Gaussian W 16x8, calibration X 64x16, seed 28, symmetric 3-bit, K=8 | Python 3.14.5, NumPy 2.4.6, macOS arm64 | reported calibration MSE: covariance 0.8220074902, magnitude 0.8896527392, RMS 0.9210985039, random 0.9731676638; EGR2 111 bytes per method; selection and evaluation used same calibration data | EXPLORATORY | continued to Issue #28 protocol proposal; no held-out confirmation or novelty claim
