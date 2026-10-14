# Thermal Evidence v2.1 — checkpoint experiment

This stacked experiment extends [Thermal Evidence v2](THERMAL_EVIDENCE_V2.md) with a **separately retained checkpoint** containing the expected record count and terminal SHA-256 hash.

## Claim and limits
A verifier holding an independently retained checkpoint can reject a truncated log, appended log, or internally consistent rewrite that no longer matches that checkpoint. This is a *conditional integrity property*, not proof of sensor authenticity, external witnessing, trusted time, non-equivocation, or execution authorization. **The code does not upload or publish checkpoints**. Merely placing a checkpoint beside the log does not establish independence: an attacker able to rewrite both can reseal both.

## Reproduce
```sh
python -m unittest discover -s experiments -p 'test_thermal_checkpoint_v21.py' -v
python experiments/thermal_evidence_v2.py evaluate --temp-c 30 --observed-at-s 100 --now-s 101 --out evidence.jsonl
python experiments/thermal_checkpoint_v21.py checkpoint evidence.jsonl checkpoint.json
python experiments/thermal_checkpoint_v21.py verify evidence.jsonl checkpoint.json
```

The checkpoint output is **not authenticated**. For a real independent witness, use a separately controlled, access-restricted append-only store or signature-backed witness and explicitly document key custody, witness identity, checkpoint delivery, time source, rollback model, and failure recovery. The current implementation does not provide those guarantees.

## Falsification
Tests cover a matching record chain, truncation, extension, fully rewritten and resealed evidence, altered checkpoint count, missing fields, invalid boolean count and empty evidence. Both false positives and false negatives should be retained in subsequent reports. These are synthetic controls; no device sensor measurements or cross-substrate results are claimed.

## Integration boundary
This PR deliberately does **not** authorize or execute an action. A future executor must independently verify sensor identity and calibration, checkpoint provenance, freshness, capability scope, single-use reservation, and revalidation at the instant of execution. The verifier's success is insufficient to confer those permissions.

Legacy Exp #001 files and data remain untouched.
