# SRR-1 v0.1 structural-check evidence

**Status: LOCAL SELF-TESTED ONLY. Not independently reproduced; not security-validated; no model operations authorized.**

## Observation

- Execution time: 2026-10-11 22:38 UTC (approximate)
- Test substrate: Linux x86_64; Python 3.13.5.
- Command: `python3 -m unittest discover -s research-relay/tests -v`
- Result: **6 tests ran; all six OK**, exit 0.
- Command: `python3 research-relay/scripts/validate_relay.py research-relay`
- Result: `STRUCTURAL_CHECK_OK: 1 task(s); READ_ONLY only; no action authorized`, exit 0.
- Both programs were run on local file copies whose Git blob IDs matched the proposed GitHub branch:
  - validator: blob `c7fd2836f51b3c75518333a8373fc915ad03933a`; SHA-256 `786d88e2b24f09caf53469e242924a6c0b868474d20d6c593c5b5ae920007231`
  - unit tests: blob `66d256b9d3c630d6c4edef568ba491eb84617bf1`; SHA-256 `63253e9d0deab086e54e594211159e8a914adf75b4e1d43f7eb0d26c7b546790`
  - dormant task: blob `ca29c735d1e83716cc7382a57cd2b6ddf0abd33c`; SHA-256 `b7f07ae105ffa81514709f520a2f186ca78b4e888c6ca5eb83f61566ca988595`

## Cases

1. Dormant task metadata accepted.
2. Unauthorized TEST_APPROVED with a markdown approval reference rejected.
3. Self-reported COMPLETE and promoted claim rejected.
4. Duplicate JSON fields rejected.
5. Missing task inventory rejected.
6. Non-commit source revision (`main` instead of full SHA) rejected.

## Critical boundaries

This validator checks narrow, syntactic invariants in a **dormant** pilot. It is not a verifier for experimental outcomes, a permission gate for real-world actions, a cryptographic signature verifier, a GitHub provenance check, or an autonomous reviewer. Its PASS may coexist with forged evidence or malicious markdown.

No untrusted/remote model was run. No Claude participation. No GitHub CI installed. No experiment was preregistered or executed by SRR-1. No performance, efficiency, autonomy, reliability or integration claim is supported.

**Next unrun door:** A controlled, preregistered comparison with rival handoff methods and separately validated authorization; not authorized by this record.
