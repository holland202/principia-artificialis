# Evidence-Bound Thermal Decisions v2 — experimental prototype

**Question:** Can a thermal decision be independently replayed from explicitly admitted observations and policy, while refusing absent, stale, malformed or excessive readings?

## What is new
This is a separately versioned successor to Exp #001, not a rewrite of its history. The instrument returns **ALLOW / DEFER / REFUSE** with machine-readable reason codes, a deterministic policy digest, canonical JSON records, a SHA-256 record chain and a verifier that recomputes decisions rather than trusting recorded labels.

No live sensor is polled automatically. CLI-supplied observations carry `authenticity=not_established` and are not evidence of actual SoC temperature. The demonstration ceiling is not a validated hardware safety threshold.

## Reproduce (Python 3.11+, standard library)
```sh
python -m unittest discover -s experiments -p 'test_thermal_evidence_v2.py' -v
python experiments/thermal_evidence_v2.py evaluate --now-s 101 --temp-c 30 --observed-at-s 100 --out evidence.jsonl
python experiments/thermal_evidence_v2.py verify evidence.jsonl
python experiments/thermal_evidence_v2.py evaluate --now-s 101
```
The last command emits **DEFER / NO_OBSERVATION**. No sample is invented.

## Evidence contract
- `observation`: numeric `temp_c`, `observed_at_s`, source and declared authenticity, or `null`.
- `policy`: ceiling, freshness limit, physically plausible input bounds (demonstration values).
- `result`: deterministic decision and reason.
- `record_sha256`: SHA-256 over canonical JSON excluding that field.
- `prev_hash`: hash of prior record; `sequence` starts at zero.
- `policy_sha256`: hash of the policy. A standalone record is internally verifiable, not externally authenticated.

## Registered failure and limitation cases
The tests cover missing readings, stale/future timestamps, nonfinite/out-of-range inputs, boundary equality, mutation of evidence, resealed false decisions, reordered chains and invalid policies. They deliberately document that **truncating an unanchored log to a valid prefix still verifies**. Hash chains do not prove truth, sensor identity, hardware calibration, external time, non-rollback or authorization to execute.

**Scope of ALLOW:** the supplied observation satisfies the *demonstration policy*; it does not authorize a physical action. There is no sensor authentication, signing, independent witness, monotonic clock or atomic reservation/execution mechanism. This is not a production safety controller.

## Next falsification gates
1. Bind to a named, calibrated sensor with units and error budget, then compare independent measurements.
2. Add signed observation provenance and an external checkpoint for truncation detection.
3. Measure freshness under clock rollback, concurrent writers and interrupted writes.
4. Separate authorization from execution and revalidate immediately before action.
5. Cross-substrate reproduce byte-identical canonical records and report environment, exit codes and failures.

## Legacy preservation
The original `exp001_entropy_monitor.py`, accompanying diagrams and original measurements remain part of the public research record. Do not backfill or relabel historical values as verified. Synthetic fixtures are only tests, never observations.

Related guidance: NIST SP 800-53 (audit record integrity and provenance), NIST Research Data Framework, and GitHub Actions security guidance. These references motivate controls; they do not validate this implementation.
