# EGRR Issue #28 — Pre-registration exploration provenance

Status: EXPLORATORY. Not confirmatory, frozen or independently replicated.
Related protocol: `egrr_issue28_protocol_draft.md`.

## Historical local record

- Recorded UTC: 2026-10-13T20:01:22.041028+00:00.
- Synthetic Gaussian weight matrix: 16 x 8.
- Calibration inputs: 64 x 16.
- Seed: 28.
- Quantization: symmetric 3-bit.
- Corrections: K=8.
- Representation: EGR2 with float16 corrections and CRC32.
- Reported serialized size: 111 bytes per corrected method.
- Calibration output MSE, magnitude: 0.8896527392.
- Calibration output MSE, RMS sensitivity: 0.9210985039.
- Calibration output MSE, random: 0.9731676638.
- Calibration output MSE, covariance greedy: 0.8220074902.

**Limitation:** Selection and evaluation used the same calibration
inputs. These are historical, locally reported exploratory numbers,
not held-out results or an independent reproduction.

## Source identity (SHA-256, verified locally 2026-10-14)

| File | SHA-256 |
|---|---|
| egrr.py | 982efcb7418a78de787fc3b643936a2ec942c183ac4f43450917f45c2e5e8c46 |
| packing.py | c1fa507ab1ec4b7e493ed5e388bdf31a9bc8a235e8ca5aaaab082ddb36f44097 |
| storage.py | 48b61a4fadf1f729c262dd7ac10ec0a5a4332944e3509b3d9d4deb651572fd18 |
| covariance_candidate.py | c41e96d122ba5d5029a97462618af1bf2a2fec261e5f66b91401733afa5d840d |
| covariance_float16.py | 8e53fe60543b21b34ba741584b4ea3a294588115a0541aabe15d12a2f564c3c9 |
| test_egrr.py | 3bf51a779267c5a10fd7c2ea28720b8af953b1eca88712d080544528d422e16e |
| test_packing.py | 1cc99cc36684ec3bf9a800cbd47b8a0ed484a793ef9c330320c3af8179328fda |
| test_storage.py | ba21efdcb24d4519fd3513c4e3034a41bc9c9022018250379885c13863839aa4 |
| test_serialized_quality.py | d4fce483781b46d75b88108bfda139c6514f068587e1ca7111bdc844cc8ccf23 |
| test_covariance_float16.py | b480494e16182d6f0228fef5684d0f7c833a756dd8b7e91efeaee9f007bfbb94 |

## Recorded environment

- Python: 3.14.5
- NumPy: 2.4.6
- Platform: macOS-27.0.1-arm64-arm-64bit-Mach-O
- Architecture: arm64

An earlier eight-file manifest reported 18 structural tests
passing. Later local tests and the four-arm 1311-byte round-trip
check are separate observations, not part of that historical run.

## Known provenance limitations

- The historical source files currently reside in a local
  non-Git workspace and are not included in this protocol PR.
- File hashes alone do not establish the exact source revision
  used when each historical observation was produced.
- Historical stdout, full generator draw order and original
  execution command have not yet been independently verified.
- This record does not claim a complete C-EXPLORE FORKS.md
  ledger or enumerate every preceding exploratory fork.
- Any missing exploration must be disclosed before registration.
- No confirmatory held-out experiment has been authorized.

## AI and human provenance

- AI assistance: OpenAI ChatGPT GPT-6, planning and drafting.
- Human investigator: Sandeep (`sunny-kavixo`).
- Human validation: independent scientific validation not established.
- Maintainer review: direction-level technical review with
  changes requested; not a protocol freeze or validation.
- Responsibility for execution and scientific claims remains
  with the investigator and reviewing project governance.

## Next unrun test

Once a complete protocol is jointly approved and separately
registered, conduct its fixed-horizon held-out comparison.
Do not run it before authorization.
