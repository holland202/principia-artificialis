# PA-JSON-002 — Exact decimal equivalence across large exponent cancellation

**State:** REGISTERED when committed; no subject-input execution before this commit.
**Design:** deterministic conformance audit; existence and finite-corpus claims only.
**Owner-facing date:** November 7, 2026, America/Chicago.
**Method:** METHOD.md / WORKFLOW.md / CONTROLS.md at
`936ee25f708156ec005d3356735a270633837c63`.

## Question

Can SQLite 3.54.1 return different binary64 values for valid JSON numeric tokens
that denote exactly the same finite rational number, when a large significand
and a compensating decimal exponent cancel mathematically?

This follows the unrun door in Note 077. The question was narrowed by inspecting
the current release's parser, not by running candidate numbers. No claim of
world-first novelty, standards violation, or production impact is registered.

## Prior work, source inspection, and preparation

- SQLite's published release history identifies 3.54.1 as the latest release
  inspected for this registration. Source ID:
  `2026-10-16 14:45:20 555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76`.
- The GitHub mirror tag `version-3.54.1` resolves to
  `57520227c95396ce39ba6ecaac8d475b78dd3964`. Its generated amalgamation SHA3-256
  matches SQLite's published release digest:
  `e2b869d3003b33c942b7dd7063604fbc53553e1b66609570df39b9b7b558ee81`.
- `src/util.c`, `sqlite3AtoF()`, accumulates a significand and decimal exponent.
  Its exponent digit loop caps the accumulator after sufficiently large
  prefixes. This motivates P1/P2; it is not a measured result.
- SQLite maintainers already disclose limited significant-digit handling and
  occasional rounding differences on long decimal inputs. Historic source also
  contains the exponent cap. Neither mechanism is claimed as newly invented or
  newly discovered here. Searches for compensating exponents, exponent saturation,
  exponent clamping, and long significands found source and related rounding
  discussions, not a confirmed report of this exact finite-value cancellation
  case. That search does not establish novelty.
- Python's installed SQLite and Node's embedded SQLite are older than this
  target. The test must load the independently built, pinned 3.54.1 dependency
  through its actual public C API. The Python/JavaScript reference arms use their
  own numeric parsers, not their embedded SQLite bindings.
- Dependency generation/compilation and version inventory occurred before this
  registration. They executed no candidate numeric inputs. Input construction
  and feasibility counts are the only study code run before registration; the
  subject harness has not yet been written or run.

Primary source identities, retained excerpts, and build preparation are in
`experiments/pa_json_002/SOURCES.json` and `BUILD.json`.

## Frozen corpus and exact equivalence

Input generator: `experiments/pa_json_002/cases.py`. Feasibility code:
`experiments/pa_json_002/feasibility.py`. Counts are committed with this plan in
`FEASIBILITY.json`; no target parse outcomes are in that file.

Let m range over `(1, 125, 9007199254740993, 18014398509481983)`, q over `(0,-2)`,
and sign over `(1,-1)`. The canonical token is `sign + digits(m) + 'e' + q`.
Its exact value is `sign*m*10^q` and is finite and nonzero in binary64.

For each canonical token, construct both families for each n in:

```text
0, 1, 18, 19, 20, 9998, 9999, 10000, 10001, 10002,
99998, 99999, 100000, 100001, 100002, 131072
```

| Family | Transformed token, before sign prefix | Exact algebra |
|---|---|---|
| integer_padding | digits(m) + n zero characters + 'e' + (q-n) | m*10^n*10^(q-n) = m*10^q |
| fraction_padding | '0.' + n zeros + digits(m) + 'e' + (q+n+len(digits(m))) | m*10^(-n-len(digits(m)))*10^(q+n+len(digits(m))) = m*10^q |

The corpus has 512 cases, 512 distinct transformed tokens, 16 distinct baseline
values and 496 nonidentity spellings. Maximum token length is 131099 bytes;
total transformed token bytes are 21804598. All 512 pairs pass exact-rational
equivalence before any subject parsing. The ordered canonical JSONL input digest
is `9aa6c77939135ac22fcf74d9818f6d12691205f9325c2f3c56877dedc99a3076`.

Case identities and order are frozen by the generator and digest. No sampling,
search for a minimal counterexample, early stopping, or post-run corpus expansion
is part of this registered run. Any later exploration is separately labelled.

## Subject routes and observers

1. SQLite JSON route: bind the token as UTF-8 TEXT to a reusable statement that
   obtains `json_valid(?1)`, `typeof(json_extract(?1,'$'))`, and
   `json_extract(?1,'$')`. Read the numeric result using `sqlite3_column_double`;
   record its raw binary64 bits, not a decimal rendering.
2. SQLite CAST route: bind the identical token to `CAST(?1 AS REAL)` and read
   the result's binary64 bits through the public API.
3. Python reference: `float(token)`, with raw binary64 bits recorded.
4. JavaScript reference: `JSON.parse(token)` in the installed Node runtime,
   with `Buffer.writeDoubleBE` used only to observe its numeric bits.

Run each baseline and transformed token through each route. For SQLite record
validity, type, API return codes and errors as well as numeric bits. Do not
silently coerce rejected or NULL results into successful zero measurements.

The exact observer normalizes the complete decimal token to a Fraction, without
truncating the coefficient or clipping its exponent. Compute expected binary64
bits using integer division, exact remainder comparison, and ties-to-even.
It does not use target parsers or `float(token)` as the oracle. Both observers
and harness are written by ChatGPT; agreement is self-testing, not independence.

## Registered predictions

All comparisons are exact; no tolerances or estimated rates.

| ID | Prediction | HELD criterion | REFUTED criterion |
|---|---|---|---|
| P1 | At least one equivalent pair differs through SQLite's JSON route | At least 1 valid, numeric pair has unequal baseline/transformed binary64 bits | 0 such disagreements in the complete corpus |
| P2 | Source-derived unit examples exhibit catastrophic cancellation failure | For m=1,q=0,sign=+1,n=100000: baseline is `3ff0000000000000`; integer_padding is `7ff0000000000000` (+infinity); fraction_padding is `0000000000000000` (+zero); both SQLite routes agree on those bits, JSON validity is 1 and JSON type is real | Any specified observation differs |
| P3 | The two conventional parser arms preserve the exact values on this corpus | 0 errors and 0 baseline or transformed mismatches against the exact binary64 oracle in each arm | At least 1 error or mismatch in either arm |
| P4 | The instrument distinguishes errors and has benign passing cases | Oracle calibration succeeds; all n=0 and n=1 SQLite cases agree with their exact oracle; SQLite distinguishes `1e0` from `2e0`; JSON rejects all three malformed controls; sabotage is refused with exit 1 | Any named control fails |
| P5 | SQLite accepts the corpus as JSON numbers | All 512 transformed tokens have json_valid=1, numeric SQL type real, and successful JSON extraction | At least 1 rejection, nonnumeric type, or API failure |

Missing evidence or a target/build mismatch is `COULD NOT RUN AS REGISTERED` or
`IMPLEMENTATION_ERROR`, not a refutation caused by silently omitted cases.
P4 is an instrument prediction; it is not evidence for P1's scientific meaning.

## Controls, rivals, and pre-mortem

**Simplest rival:** the spellings actually represent different numbers, the
result was changed by decimal output formatting, or the effect is ordinary
rounding of a long nonzero coefficient. Check each pair with exact rational
arithmetic, observe the returned bits directly, and include the unit examples
whose only nonzero significand digit is 1. Run Python and JavaScript on precisely
the same strings and retain the small-padding SQLite controls.

**Anti-vacuity:** the benign identity/small-padding cases must have no mismatch;
the non-equivalent `1e0` / `2e0` controls must differ. Oracle calibration includes
exact dyadic values and the even/odd midpoint cases around 2^53.
Malformed JSON controls are `1e`, `-`, and `01`; JSON validation must return 0
and extraction must error. CAST's permissive malformed-prefix semantics are not
scored as JSON validity. A `--sabotage` mode flips the observed unit-control bits
in memory; the instrument must detect it and exit exactly 1 without modifying
raw evidence. Missing/empty/malformed records must fail closed.

Pre-mortem:

- Wrong SQLite library loaded: libversion/source ID and build provenance gate
  before any target query; mismatch makes the run unscorable.
- Formatting hides infinity, zero, or a one-ULP difference: record raw double
  bits and SQL type; keep text renderings separate if added.
- Oracle or wrapper confuses sign, exponent offset, or a failed API read:
  exact Fraction equivalence, pinned input digest, midpoint controls, explicit
  SQLite return/type checks, and the independent-language reference arm expose it.

## Execution, recording, and stopping

Execute the full fixed corpus once after this registration has a Git commit
identity. Record every input and both outputs for each route. Compression is
allowed; the uncompressed SHA-256 must be retained. No stopping based on results.
Record each P outcome and `VERDICT n of 5 as registered`, then a digest of
canonical outcome/count/observation records. Environment/build metadata is
retained separately so it does not masquerade as a deterministic semantic result.

Commit the harness exactly as run with its raw output. Pin the recorded outcomes
and digest in a later separate commit. Any harness defects are disclosed with
the failed attempt preserved; this registration is never rewritten to match
the result. A fresh clone must verify stored evidence without rerunning subjects;
a separate command may reproduce the pinned target build and execute the study.

## Limits, validity axes, and review

Stand-in: constructed numeric strings, not a production workload. No benchmark
failure-rate, performance, exploitability, or security conclusion follows.
No SQLite source modification or upstream report is authorized by this record.

Mathematical validity concerns exact decimal equivalence. Implementation validity
concerns these public API calls on the named release/build only. Empirical
validity is NOT RUN: no field data or application workload. Replication level is
self-tested; no independent reviewer or person has inspected the generated
sample. C-SYNTH remains pending, so execution alone cannot promote a claim.

## Triggered controls (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | Yes: generator eligibility and counts committed with this registration; no target outcomes |
| Noise | C-NOISE | No: fixed C/standard-library numeric parsing; no timing, sampling or concurrency claim |
| Statistics | C-STAT | No: deterministic existence/conformance predicates on a fixed corpus, no population estimate |
| Evidence | C-EVID | No: numeric parsing is the subject, not freshness/provenance policy |
| Independence | C-INDEP | Yes: self-tested only; two languages by one author are not replication |
| External | C-EXT | Yes: sources/excerpts/hashes and source-specific checks retained in SOURCES.json |
| Device | C-DEVICE | Yes: target release/build and host recorded; all other platforms NOT VALIDATED |
| Verdict code | C-BUILD | Yes: missing evidence/API failures cannot pass; named benign and sabotage controls |
| Exploration | C-EXPLORE | Yes: prior PA-JSON-001 work and pre-run source inspection are disclosed; no outputs on this corpus were seen before this registration |
| Method comparison | C-METHCOMP | No: fixed parser conformance, not a comparison of research methodologies |
| People's data | C-PRIVATE | No: synthetic numbers and public source attribution; no private input or message publication |
| Design | C-DESIGN | Yes: deterministic conformance audit; existence claims only |
| Held-out | C-HOLDOUT | No: no selected model, fitted threshold or tuned generator from these parse outcomes; source-derived predictions disclosed |
| Generated inputs | C-SYNTH | Yes: full class counts and named cases retained; person-look NOT PERFORMED, promotion pending |

## Unrun door (M15)

A separately authored implementation, starting from this token grammar and
public SQLite API specification, reproduces a surviving counterexample on a
separately built current SQLite library. This remains unrun even after the
author's registered run and CI re-run.

## Provenance (M13)

ChatGPT (OpenAI, GPT-6; Codex agent) inspected sources, designed the corpus and
protocol, and performed feasibility counts → human validation: not performed →
human editing/curation: direction by Chad Edward Holland → human responsibility:
Chad Edward Holland. Human review level: direction only. User authorization:
continue the general-software research and record it in Principia Artificialis.
