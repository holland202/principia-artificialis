# Note #080 — Compensating decimal exponents across 25 number parsers: is SQLite alone?

**Status:** Draft — predictions registered; nothing run.
**Theme:** Software correctness / Numeric parsing
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's direction (2026-11-08). Review level: direction
only.
**Builds on:** [[note078_large_exponent_cancellation]] (ChatGPT's PA-JSON-002: SQLite reads long numbers equal to 1
as infinity or zero), [[note077_numeric_conversion_stability]] (the series it extends).
**Method:** [METHOD.md](../METHOD.md). Driver: `experiments/note080_crossparse/run.py`.

## What went wrong, first

Nothing has been run yet. This section is filled in with the results.

## The question

SQLite's `sqlite3AtoF()` caps an explicit exponent of 100,000 or more at 10,000. Padding digits still move the
decimal exponent with no limit, so valid numbers equal to 1 come back as infinity or zero
(`experiments/pa_json_002_claude/RESULTS.md`). A one-line cap like that is a natural shortcut in any hand-written
number parser. Is this a SQLite quirk, or a pattern found in other widely used parsers?

**Known before registering (C-EXPLORE).**
- SQLite's results.
- Python's `json.loads` and Node's `JSON.parse` give 0.0 and Infinity on two of the tokens below (a post-hoc
  record from that check).
- My general background knowledge: Go's, Java's and glibc's decimal-to-double conversions are documented as
  correctly rounded, and serde_json's default float parser is not promised to be. These are not scored.
- Not known: how any other implementation handles these tokens. I have not read their parsing source for this
  question.

## Implementations (25 observers; versions recorded by each observer at run time)

| Language or engine | Observers |
|---|---|
| Python 3.13.18 | `json` (stdlib), simplejson 4.2.0, ujson 6.1.0, orjson 3.13.0, python-rapidjson 1.26, pysimdjson 7.0.2, msgspec 0.22.0, yyjson 4.0.6 |
| SQL engines | DuckDB 2.0.0 (`CAST AS DOUBLE`, and JSON then `DOUBLE`); system SQLite 3.53.1 (`CAST AS REAL`, `json_extract`); verified SQLite 3.54.1 (JSON, CAST) |
| JavaScript | Node 22.23.4: `JSON.parse`, `Number()` |
| C | glibc 2.39 `strtod` |
| Go 1.24.7 | `strconv.ParseFloat`, `encoding/json` |
| Rust 1.97.0 | `str::parse::<f64>`, serde_json 1.0.154 (default features) |
| Java 21.0.12.1 | `Double.parseDouble`, `BigDecimal.doubleValue` |
| PHP 8.3.6 | `json_decode` |
| Ruby 3.3.6 | `JSON.parse` (json 2.7.2), `Float()` |
| Perl 5.38.2 | JSON::PP 4.16 |

## Tokens (17; `run.py tokens()`)

- **Controls:** `1e0`, `0.1`, `1.5e10`.
- **Witnesses, each exactly 1:**
  - `"1" + "0"*n + "e-" + n`;
  - `"0." + "0"*n + "1e" + (n+1)`;
  - both for n = 330, 1000, 2000, 10000, 20000 and 100000, so caps at several sizes can be seen.
- **`x3_42`:** `"42" + "0"*10000 + "e-100000"`, exactly 42e-90000, which rounds to +0.
- **`x2_tenth`:** `"0." + "0"*10000 + "1e100000"`, exactly 1e89999, which rounds to +inf.

**Reference:** the correctly rounded binary64 value of each token's exact rational value.

**Classification:**
- **CORRECT:** the same bits, or an exact integer equal to the value.
- **ERROR:** the API signals failure (an exception, ERANGE, or an error return). This is an explicit refusal, which
  RFC 8259's allowance for implementation limits permits.
- **WRONG:** a different value returned without any error.

## Predictions

- **P1 (replication).** Both SQLite versions are WRONG on `int_pad_100000`, `frac_pad_100000`, `x3_42` and
  `x2_tenth` in both routes, and CORRECT on the controls.
- **P2 (known good).** CPython `json`, V8 `JSON.parse`, glibc `strtod`, Go `strconv.ParseFloat` and Java
  `Double.parseDouble` are never WRONG on any token.
- **P3 (the bet; my prior is about even).** At least one valid implementation other than SQLite returns WRONG on
  at least one witness.

**What either result would mean.**
- If P3 holds, the cap-without-compensation pattern (or another silent failure) exists beyond SQLite. Any report to
  those projects is Chad's decision.
- If it is refuted, SQLite is the outlier among 25 observers. That strengthens the SQLite report.

## Controls (all must pass, or the verdicts are not scorable)

- **K1–K3 (classifier):** a wrong bit is WRONG, an error is ERROR, and an exact integer is CORRECT.
- **K4 (coverage):** every observer answered every token.
- **K5:** CPython `json`, `JSON.parse` and `strtod` are exact on the controls.
- **Validity gate:** an observer that is not exact on all three controls is INVALID, listed, and excluded from P2
  and P3. That way, a harness or API mistake cannot pass for a parser's behaviour.
- **Sabotage:** `--sabotage` plants one wrong bit, and the run must exit 1.

## Pre-mortem

- **A binding's error can be my harness's fault.** The validity gate catches a broken call on simple input, but not
  one that only breaks on long input. Every ERROR result is reported with its exception class, for that reason.
- **Some bindings share code.** Some may delegate to the same conversion routine (CPython's, or a common C
  library). Where that is known it is said, and shared code is not counted as independent agreement.
- **Range errors count as ERROR.** Under this rule, strtod's and Go's correct overflow and underflow become ERROR,
  not CORRECT. That does not affect P2 or P3, which concern WRONG only.
- **Versions drift.** Each observer prints its versions, and they are recorded with the results.

## Triggered controls (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | Yes: implementations installed and observers built before registering; nothing run on a token |
| Noise | C-NOISE | No: parsing is deterministic; any repeat-run difference would be reported |
| Statistics | C-STAT | No: existence claims per implementation, no rates |
| Evidence | C-EVID | No |
| Independence | C-INDEP | Yes: shared conversion code is named, and agreement through shared code is not counted as independent |
| External | C-EXT | Yes: third-party libraries are observed as they are, with versions recorded |
| Device | C-DEVICE | Yes: Linux x86_64 container only; not the S25 |
| Verdict code | C-BUILD | Yes: the classifier has its own controls (K1–K3), and a sabotage run must fail |
| Exploration | C-EXPLORE | Yes: SQLite's and two parsers' results were known; stated above |
| Method comparison | C-METHCOMP | No |
| People's data | C-PRIVATE | No |
| Design | C-DESIGN | Yes: a conformance check of named versions on 17 tokens. It supports existence claims about those versions only |
| Held-out | C-HOLDOUT | No: the tokens are fixed now |
| Generated inputs | C-SYNTH | Yes: tokens are generated; each one's exact value is stated by its construction, and the reference is computed from the token itself |

## Falsifiable next predictions (M15)

- **P4 (unrun).** For any implementation found WRONG, its source contains an exponent bound that does not account
  for the digit offset, as SQLite's does. A WRONG result whose cause is different refutes P4 for that
  implementation.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed the study, wrote the observers and driver, and drafted this
registration → human validation: not performed → human editing/curation: direction by Chad Edward Holland,
2026-11-08 → human responsibility: Chad Edward Holland. Review level: direction only.*
