# Claude's check of PA-JSON-002 — results

Registration: [REGISTRATION.md](REGISTRATION.md), committed and pushed at `106616d` before any token was run.
Container (Linux x86_64, Python 3.13.18, gcc 13.3.0). NOT VALIDATED on the S25. Not blind; a second AI, not an
independent human.

## Part A — 5 of 7 HELD; C3a and C3b REFUTED

### What went wrong, first

1. **C3a is REFUTED: my threshold was off by a factor of ten.** I predicted that failures would begin with a padding
   length between 9,000 and 10,999. Every padding length from 0 to 12,000 is exact, in both families and both
   routes. Failures begin between n = 99,784 and n = 100,000, the gap between two neighbouring points of my sparse
   grid. I took "near 10,000" from the n values in ChatGPT's protocol and did not check it against the source,
   which I had chosen not to read before running.
2. **C3b is REFUTED: there is no finite wrong band in these families.** I predicted a run of wrong but finite
   powers of ten above the threshold. Instead the results jump from exact (1.0) straight to +inf (F1) and +0
   (F2). Since there was no threshold in the dense range, the band test could not apply as registered. The sparse
   points show the jump directly.
3. **Both failures come from one misreading of the cap's form.** The source (read after the run; below) shows the
   explicit exponent does not saturate at its true size. Any exponent with six or more digits collapses to
   exactly 10,000.

### Results (`results_A/run.txt`)

```
"controls": K1 true, K2 true, K3 true, K4 true, K5 true
"observer_header": "#3.54.1\t2026-10-16 14:45:20 555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76"
"verdicts": {"C2": "HELD", "C3a": "REFUTED", "C3b": "REFUTED", "C3c": "HELD", "C3d": "HELD", "C3e": "HELD", "C3f": "HELD"}
"families": F1 threshold null, F2 threshold null      (no failure anywhere in n = 0-12,000)
"sparse_wrong_count": {"F1": 33, "F2": 33}, "sparse_total": 123
"tokens": 24320, "total_token_bytes": 162872047
"observations_sha256": "03a76adc1060cb2ec7aa67037f471194c43e808ab48294e0ad49c68eaa6541bc"
```

`--sabotage` (one flipped bit of `1e0`'s result) failed K1 and K4 and exited 1 (`results_A/sabotage.txt`).

| | prediction | result |
|---|---|---|
| C1 | my build is the pinned release | **HELD**: the zip and `sqlite3.c` hashes match sqlite.org's published values; the observer reports 3.54.1 and the pinned source ID |
| C2 | the two witnesses reproduce through my own observer | **HELD**: `7ff0000000000000` (+inf) and `0000000000000000` (+0) in both routes, `json_valid` 1, type `real`; `1e0` gives `3ff0000000000000` |
| C3a | threshold between 9,000 and 10,999 | **REFUTED**: none below 12,000; failures begin between 99,784 and 100,000 |
| C3b | finite wrong band above the threshold | **REFUTED**: exact, then +inf or +0 directly |
| C3c | JSON and CAST agree | **HELD**, on every long token |
| C3d | SQLite accepts every long token | **HELD**: `json_valid` 1, type `real` |
| C3e | long digits alone do not break it | **HELD**: `"1.0" + "0"*n + "e0"` is exact up to n = 131,072 |
| C3f | sign symmetry | **HELD** |

Every sparse point from n = 100,000 upward is wrong: +inf for F1, +0 for F2. No exact point appears after the first
wrong one. From where I stand, the handoff's central observation is reproduced by a separately written observer, on
a separately built copy of the same release, with a corpus generated separately.

Recorded but not scored: SQLite returns integers, not reals, for `9007199254740993` and `9007199254740995`, so the
observer marks them non-float. It returns the correctly rounded bits for `0.1` and the three subnormal-boundary
cases.

### The mechanism, from the source (read after Part A ran)

From `sqlite3AtoF()` in the verified `sqlite3.c`:

```c
      while( (v = (unsigned)z[0] - '0')<10 ){
        exp = exp<10000 ? (exp*10 + v) : 10000;
        z++;
      }
      d += esign*exp;
```

The exponent accumulator takes digits while it is below 10,000. An exponent of up to five digits (at most 99,999)
is read exactly. Any exponent of six or more digits (100,000 and above) becomes exactly 10,000.

Meanwhile, every integer digit after the 19th (`while( sqlite3Isdigit(z[0]) ){ z++; d++; }`) and every fraction
digit (`d--`) moves the decimal exponent `d` with no limit. The cap is harmless when the digits do not compensate:
10^±10000 already overflows or underflows. It breaks when they do compensate.
- F1 at n = 100,000: the significand stops at s = 10^19, and the 99,981 skipped zeros give d = 99,981 − 10,000.
  The result is 10^90000, which is +inf.
- F2 at n = 99,999: d = −100,000 + 10,000, so the result is +0.

The source also predicts a case my corpus did not contain: tokens whose true value overflows or underflows, read as
ordinary finite numbers. Part C registers and tests that before running it.

## Part C — 6 of 6 HELD (source-derived, registered at `7d406e1` before running)

These predictions came from reading the source after Part A, so they are not fresh confirmation. They are exact,
and any of them could have failed.

```
"controls": K1 true, K2 true, K3 true, K4 true
"verdicts": {"D1": "HELD", "D2_X1": "HELD", "D2_X2": "HELD", "D3": "HELD", "D4": "HELD", "D5": "HELD"}
"D3_checked": {"part_A_long_tokens": 24304, "part_C_long_tokens": 1072, "failures_A": [], "failures_C": []}
"X1_examples": {"0": "3ff0000000000000", "1": "4024000000000000", "308": "7fe1ccf385ebc8a0", "309": "7ff0000000000000"}
"X2_examples": {"1": "3fb999999999999a", "323": "0000000000000002", "324": "0000000000000000"}
"X3_bits": {"42:0": "4045000000000000", "-7:0": "c01c000000000000", "123456789:0": "419d6f3454000000"}
"max_len_X": 10339
```

| | prediction | result |
|---|---|---|
| D1 | exact threshold: integer padding exact up to n = 99,999 and +inf from 100,000; fraction padding exact up to 99,998 and +0 from 99,999 | **HELD** at every n from 99,900 to 100,100, and at 131,072 |
| D2 X1 | `"1"+"0"*(10000+k)+"e-100000"` should underflow to 0, but is read as 10^k (k ≤ 308), then +inf | **HELD**. For example k = 1 gives `4024000000000000`, which is 10.0 |
| D2 X2 | `"0."+"0"*(9999+j)+"1e100000"` should overflow to +inf, but is read as 10^−j (j ≤ 323), then +0 | **HELD**. For example j = 1 gives `3fb999999999999a`, which is 0.1 |
| D3 | a one-line model explains everything: replace any explicit exponent above 99,999 with 10,000, then round correctly | **HELD**: within 1 ULP on all 25,376 long tokens from Parts A and C |
| D4 | an arbitrary value hidden in a number whose exact value is ±0 | **HELD**: SQLite reads 42.0, −7.0, 123456789.0, and those values × 1000 |
| D5 | still valid JSON, type real, both routes identical | **HELD** |

The finite wrong values I wrongly expected in Part A do exist. They need a long token whose exact value is outside
the double range, not one whose value is 1.

## Part B — HELD: ChatGPT's harness reproduces its pinned digest on my build

ChatGPT's unmodified `run.py` (from PR #123, read only after Part A was committed) was run against a shared library
I compiled from the verified `sqlite3.c` (`gcc -O2 -shared -fPIC`; library SHA-256 in `results_B/library_sha256.txt`):

```
P1: HELD   P2: HELD   P3: HELD   P4: HELD   P5: HELD
VERDICT 5 of 5 as registered
DIGEST c20ab3a00385be45ce58611401af3cbe816690db4051e3f805169d1aa9fd7ba2
```

That is ChatGPT's pinned semantic digest, exactly, from a different build route and different compiler flags. It is
a re-run of their code, not an independent check; the independent parts are A and C.

## How other readers see the same tokens (post hoc; `results_C/interop_posthoc.txt`; decides nothing)

```
system SQLite (Python's sqlite3 module): 3.53.1; observer: 3.54.1
42 hidden in a zero (X3 42:0): 10010 characters
  Python json.loads 0.0   Node JSON.parse 0   system SQLite CAST 42.0 json_extract 42.0   SQLite 3.54.1 json_extract 42.0
10 hidden in a zero (X1 k=1): 10010 characters
  Python json.loads 0.0   Node JSON.parse 0   system SQLite CAST 10.0 json_extract 10.0   SQLite 3.54.1 json_extract 10.0
0.1 hidden in an overflow (X2 j=1): 10010 characters
  Python json.loads inf   Node JSON.parse Infinity   system SQLite CAST 0.1 json_extract 0.1   SQLite 3.54.1 json_extract 0.1
```

SQLite 3.53.1, the version installed in this container, behaves the same way. So this is not new in 3.54.1.

## Prior art (searched 2026-11-08; five web searches and nine pages opened)

- **The cap's origin.** SQLite check-in [4becc47eb4d48686](https://www.sqlite.org/src/info/4becc47eb4d48686)
  (2011-10-17, drh): "Avoid 32-bit integer overflow when evaluating the exponent of a floating point value during
  ascii to binary conversion". It changed `e = e*10 + (*z - '0')` to `e = e<10000 ? (e*10 + (*z - '0')) : 10000`. Its
  tests cover exponents like `2.5e+10000` and `2.5e2147483650`, whose values really do overflow or underflow.
- **Digits feeding the exponent** date from the 2009 rewrite,
  [f084f5a8ba850de6](https://www.sqlite.org/src/info/f084f5a8ba850de6). Its `nan.test` change uses 10,000 nines with
  `.0e-9000`, whose value really does overflow.
- **Known accuracy limits:** SQLite's own comment on `sqlite3AtoF()` (only about 19 significant digits count);
  [ExploringBinary, 2010](https://www.exploringbinary.com/incorrect-decimal-to-floating-point-conversion-in-sqlite/)
  (errors of up to 4 ULPs, from a since-improved algorithm); and [floatingpoint.html](https://sqlite.org/floatingpoint.html),
  which states no limit on literal length or exponent.
- **Not found:** a report of a compensating exponent, where padding digits offset a capped exponent, giving a wrong
  but accepted value. That does not establish novelty. I did not check other parsers or float-parsing test suites,
  where this general class may well be known.

## What this shows and does not show

- **Shown:**
  - From SQLite 3.54.1, built separately, read through my own observer: valid JSON numbers of at least 100,000
    padding digits, whose exact value is 1, are read as +inf or +0. This reproduces ChatGPT's observation.
  - About 10,000 characters is enough to make SQLite read a value whose exact value is 0 (or overflows) as a finite
    number of the writer's choosing, such as 42.0.
  - One rule explains every observation: explicit exponents above 99,999 become 10,000, while padding digits move
    the exponent with no limit.
- **A plausible consequence, not demonstrated:** a system that checks a JSON number with one parser and stores or
  computes with SQLite could act on a different value from the one it checked. That is the JSON-interoperability
  class of problem. Any input-length limit below about 10 KB per number prevents it.
- **Not shown:** that anyone uses inputs like this, any security impact, whether this counts as a defect or a
  numeric limit, or behaviour on other platforms or builds. As I recall it, RFC 8259 lets implementations limit the
  range and precision of numbers. I did not re-read it for this note, and returning a different finite value is not
  the usual reading of a limit.
- No upstream report has been made. Whether to make one is Chad's decision.

## Door (unrun)

- **P-up.** If this is reported upstream and SQLite changes the cap (for example, saturating the combined exponent
  `d` rather than the explicit one), D1–D4 become a regression test. At the fixed version, every D3 token should then
  match its exact oracle, not the model.

Provenance (M13): check designed, written, run and written up by Claude (Anthropic, Opus 5.5). The original study
and its harness are by ChatGPT (OpenAI, GPT-6; Codex agent). Human validation: not performed → human direction:
Chad Holland, 2026-11-08 → human responsibility: Chad Holland. Review level: direction only.
