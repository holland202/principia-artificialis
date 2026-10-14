# Thermal Witness HMAC v2.2 — experimental trust boundary

This stacked experiment adds a **domain-separated HMAC-SHA256 witness attestation** to the checkpoint experiment in PR #42. The HMAC binds the witness identifier and canonical checkpoint; verification independently checks the MAC and the underlying evidence chain.

**Threat model:** the evidence writer can rewrite evidence but does not know or control the witness's secret. A separate operator must hold the secret and independently retain the attestation. The code cannot establish that separation. If the evidence writer possesses the key, both log and attestation can be forged. A symmetric MAC is **not** a publicly verifiable signature, nor a trusted timestamp, nor an external append-only witness. Do not commit keys or real observations.

## Reproduce synthetic controls
```sh
python -m unittest discover -s experiments -p 'test_thermal_witness_hmac_v22.py' -v
```
For a manual demonstration, generate a private random binary key (at least 32 bytes) outside the repository, then use:
```sh
python experiments/thermal_witness_hmac_v22.py attest evidence.jsonl --key-file /secure/witness.key --witness-id lab-witness --out witness.json
python experiments/thermal_witness_hmac_v22.py verify evidence.jsonl --key-file /secure/witness.key --witness-id lab-witness --attestation witness.json
```
The CLI does not create keys or contact an independent service. Protect witness key material and restrict filesystem permissions. The prototype does not enforce OS permissions or secure key custody.

## Controls and boundaries
Tests cover matching evidence, wrong key, wrong witness identity, tampered MAC, truncation, fully resealed replacement evidence, modified checkpoint, weak key length, and empty logs. A valid result means a MAC matches a supplied secret and an internally consistent chain matches the checkpoint. It **does not** establish sensor identity, measured truth, trusted time, single-use execution authorization, or actual witness independence.

**Next:** external asymmetric witness signatures with public verification, separate operator/key custody, witness replay and crash recovery, and an action-time interlock. Preserve all negative results and do not merge until CI passes.
