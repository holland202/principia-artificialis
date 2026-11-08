# Claude's check of PA-JSON-002 — registration

**State:** REGISTERED when committed. No token has been run through my observer before this commit.
**Requested by:** ChatGPT's handoff on PR #123 (`docs/PA-JSON-002_CLAUDE_HANDOFF.md`), at Chad Holland's direction.
**Date:** 2026-11-08 (America/Chicago). **Design:** deterministic conformance check; existence claims only.

This attempts the protocol's unrun door: a separately written implementation, from the token grammar and the public
SQLite API, run against a separately built SQLite 3.54.1. It is not blind, and a second AI is not an independent
human reviewer.

## What I read before writing any code

- Read: the handoff, the PR #123 description, and the protocol `docs/PA-JSON-002_PREREG.md`.
- Not read: `run.py`, `cases.py`, any results file, Note 078, and SQLite's `sqlite3AtoF()` source. I read the
  source only after my runs.
- Known from the handoff:
  - the reported counts: 166 of 512 pairs differ through each SQLite route;
  - the two unit witnesses become +infinity and +0 while `json_valid` is 1;
  - the protocol's padding list probes n = 9998–10002, which suggests a limit near 10,000.

## Build (done before this registration; hash checks and compilation only)

- Official `sqlite-amalgamation-3540100.zip` from sqlite.org. Its SHA3-256, `92281c86…8e30`, matches
  `download.html`. The extracted `sqlite3.c` has SHA3-256 `e2b869d3…ee81`, which matches the SHA3-256 that
  `releaselog/3_54_1.html` publishes for `sqlite3.c`.
- That is a different route from ChatGPT's, which generated `sqlite3.c` from the Git tag.
- `observer.c` (mine) is compiled together with that `sqlite3.c`: `gcc -O2`, gcc 13.3.0, default SQLite options.
  No other SQLite library can be loaded.
- At run time the observer must report version `3.54.1` and source ID
  `2026-10-16 14:45:20 555e07ef…6ca76`. Otherwise the run is COULD NOT RUN AS REGISTERED.

## Instrument

- `observer.c`: three prepared statements, each with the token bound once as TEXT:
  - `json_valid(?1)`;
  - `typeof(json_extract(?1,'$'))` and `json_extract(?1,'$')`, only if valid;
  - `typeof(CAST(?1 AS REAL))` and `CAST(?1 AS REAL)`.
  Doubles are read with `sqlite3_column_double` and copied with `memcpy`. Step return codes are kept, and a
  non-float result is marked rather than coerced.
- `check.py`: my generator, two oracles and the verdicts.
  - Exact oracle: the token as an exact Fraction, then CPython's correctly rounded int/int division.
  - Second oracle: `float(token)`.
  - Neither uses SQLite.

## My corpus (`check.py corpus()`; not ChatGPT's)

| family | token | exact value | n |
|---|---|---|---|
| F1 | `"1" + "0"*n + "e-" + n` | 1 | every n in 0–12,000, plus sparse n to 131,072 |
| F2 | `"0." + "0"*n + "1e" + (n+1)` | 1 | same |
| R1 (rival) | `"1.0" + "0"*n + "e0"` | 1 | 33 values, 0–131,072 |
| NEG_F1, NEG_F2 | the same with a leading `-` | −1 | 12 values |
| witnesses | the handoff's two 100,000-zero tokens | 1 | — |

## Predictions

| ID | Prediction | HELD if |
|---|---|---|
| C1 | My build is the pinned release | both hashes match (already shown above) and the observer reports the pinned version and source ID |
| C2 | The two witnesses reproduce through my observer | both routes give `7ff0000000000000` for the integer-padding witness and `0000000000000000` for the fraction-padding witness, with `json_valid` 1 and both types `real`; `1e0` gives `3ff0000000000000` |
| C3a | A sharp threshold | For F1, and separately F2, there is an N in 9,000–10,999 such that every dense n ≤ N is exact in both routes and every dense n > N is wrong |
| C3b | A finite wrong band above the threshold | F1, for 1 ≤ n − N ≤ 308: the JSON result is within 1 ULP of 10^(n−N), finite and wrong; for n − N ≥ 309: +inf. F2, for 1 ≤ n − N ≤ 323: within 1 ULP of 10^−(n−N); for n − N ≥ 324: +0 |
| C3c | The routes agree | JSON and CAST bits are identical for every long token |
| C3d | SQLite accepts every long token | `json_valid` 1 and JSON type `real` for all of them |
| C3e | Long digits alone do not break it | every R1 token is exact in both routes, up to 131,072 trailing zeros |
| C3f | Sign symmetry | each negative token gives the positive result with only the sign bit flipped |

C3a–C3b are my mechanism hypothesis: the explicit exponent saturates near 10,000, while each padding digit still
moves the decimal exponent. C3e is the rival: if long significands alone caused the failure, R1 would fail too. The
band predictions are relative to the observed N, not to a number fixed now.

## Instrument controls (all must pass, or the verdicts are not scorable)

- K1: `1e0` and `2e0` are distinguished, and both are exact.
- K2: the two oracles agree on every token.
- K3: `1e`, `-` and `01` get `json_valid` 0.
- K4: `0.5`, `1.5e10`, `-3.25e-5`, `1e308` and `1e-300` are exact in both routes.
- K5: the exact oracle gives the known bits for 2^53+1, 2^53+3, `0.1`, and three cases at the subnormal boundary.
  SQLite's results on those are recorded but not scored.
- Sabotage: `--sabotage` flips one observed bit of `1e0` in memory; the run must exit 1.

## Part B (after Part A): a re-run of ChatGPT's harness on my build

- **PB.** ChatGPT's `run.py`, given a shared library compiled from my verified `sqlite3.c`, reproduces its pinned
  semantic digest `c20ab3a0…7ba2`.
- This is a re-run of their code, not an independent check. I read `run.py` only after Part A is committed.

## Pre-mortem

- My generator could build a token that is not the value I think it is. Both oracles compute the value from the
  string itself, and K2 checks that they agree.
- SQLite could round easy values badly too. K4 would then fail, and a broken arithmetic path would be reported
  instead of a threshold.
- The threshold may not be sharp, for example if behaviour depends on the significand's digit count. C3a and C3b
  are refuted and recorded as such.
- Knowing the reported results biases me toward confirming them. The registered criteria are exact, and
  disagreements are published.

## Limits and rules

- No edit to ChatGPT's registration or results, no merge, and no upstream report.
- After the runs I read `sqlite3AtoF()` and search for prior reports. That reading is labelled as after the fact.
- Container only (Linux x86_64, Python 3.13.18). Not run on the S25.

Provenance (M13): registration, observer and driver by Claude (Anthropic, Opus 5.5) → human validation: not
performed → human direction: Chad Holland, 2026-11-08 → human responsibility: Chad Holland. Review level:
direction only.
