# Derivation check registered before running (2026-10-22, Claude Opus 5.5; scratch, not a PA experiment)
Claim D: for a GKSL generator whose collapse operators are all Hermitian and diagonal in one basis of an n-level
system, there is a dephasing model with at most n-1 diagonal operators giving the IDENTICAL superoperator
(so no preparation/measurement can tell them apart). Predicted residual <= 1e-12 for 200 random cases, n=4.
Control (must FAIL the equivalence): add one non-diagonal Hermitian operator; predicted residual > 1e-3 for all 200.
