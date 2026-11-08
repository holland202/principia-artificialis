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
