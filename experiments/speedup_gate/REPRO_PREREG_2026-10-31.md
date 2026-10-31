# Registration — reproducing speedup_gate (note072), 2026-10-31

**Registered:** before `scripts/speedup_gate.py` is run inside this repository.
**Author:** Claude (Anthropic, Opus 5.5), at Chad Holland's direction. Review level: direction only.

## What could have gone wrong, first (C-EXPLORE)

- **Not blind.** On 2026-10-31, before writing this file, Claude ran the recovered script once in a container while surveying Chad's Drive. That run gave P1 CONFIRMED and P2–P4 REFUTED, with `--sabotage` exiting 1.
- **The September registration was not committed when written.** [PREREG_2026-09-16_original.md](PREREG_2026-09-16_original.md) and the script are kept byte-for-byte as recovered from Drive. Both carry Drive dates of 2026-09-16. Its claim to have been "registered before `speedup_gate.py` was written or run" cannot be checked from git. It is the author's statement, nothing more.

## Predictions for the in-repository run (C-NOISE: at least 3 runs of identical code)

- **R1.** Every run exits 0, with A0 PASS and A1 PASS.
- **R2.** `--sabotage` exits 1 with "INSTRUMENT UNTRUSTWORTHY".
- **R3.** Every run gives the same verdict pattern as September: P1 CONFIRMED, and P2, P3 and P4 REFUTED.
- **R4.** The measured speedups differ from September's: n=1024 at 14.84x, n=4096 at 39.99x. No direction is predicted. The September record itself says the speedup is not a scalar.

## Left unrun

P5 (the same script on the S25) and P6–P8 from the September record.
