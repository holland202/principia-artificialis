# Numeric conversion: stability versus fidelity

Status: local prospective analysis plan, frozen before the systematic corpus run.
Owner-facing date: November 7, 2026 (America/Chicago).

## Question

For precisely specified JSON numeric conversions, how often does byte stability
after a second conversion coexist with a changed binary64 value after the first?
This is a measurement study, not a proposal for a new testing method or a claim
that floating-point rounding or lossy idempotent functions were previously unknown.

## Prior observations and scope

Exploration has already shown that this installed SQLite build maps
`[0.10000000000000002]` to `[0.1]` and
`[1.2345678901234567]` to `[1.23456789012346]` through
`json_array(json_extract(document, '$[0]'))`.
Maximum finite binary64 also produced a decimal exceeding the finite range.
These are explanatory examples, not held-out discoveries. The sample below has
not yet been generated or run. There is no external preregistration or blinding.

## Frozen corpus

Generate 16,384 distinct finite, nonzero IEEE 754 binary64 bit patterns. For
counter i = 0, 1, ... take the first 8 bytes of
SHA256(ASCII('numeric-stability-v1|' + decimal(i))) as big-endian bits.
Reject exponent 2047, signed zeros, and duplicate bits. Continue until the fixed
sample size is reached. Record every rejection. Use `[repr(x)]` as each input.
Do not infer production-workload prevalence from this deterministic corpus.
Signed-zero identity, NaNs, infinities as inputs, arbitrary precision integer
semantics, and exact-decimal (rather than binary64) preservation are out of scope.

## Conversions

Apply each function independently to the same original one-number JSON array:

1. Python: json.loads followed by json.dumps(separators=(',', ':'), allow_nan=False).
2. JavaScript: JSON.parse followed by JSON.stringify, in the installed Node runtime.
3. SQLite numeric: SELECT json_array(json_extract(?, '$[0]')).
4. SQLite token: SELECT json_array(? -> '$[0]').
5. SQLite cast: SELECT '[' || CAST(json_extract(?, '$[0]') AS TEXT) || ']'.
6. SQLite printf17: SELECT '[' || printf('%!.17g', json_extract(?, '$[0]')) || ']'.

Also run a deliberately lossy constant-output control T(s)='[0]'. It must be
stable and fail fidelity on every nonzero input. Report it separately from real
implementations. Token, cast, and printf routes are comparison conditions, not
unconditionally recommended repairs.

## Observers

Stability: compare first-output bytes with second-output bytes, T(s)==T(T(s)).
Fidelity: parse the single JSON numeric token to an exact Fraction using decimal
digits and integer arithmetic. Compute the exact midpoint interval surrounding
the original binary64 x from adjacent representable values. Check whether the
output is in that interval with round-to-nearest, ties-to-even endpoints. For
maximum finite values use the extrapolated next binade boundary 2^1024 to obtain
the overflow midpoint. Do not use any target JSON parser or float(token) to
decide fidelity. A nonnumeric output or malformed JSON fails numeric fidelity;
exceptions are counted separately and are not stable successes.

Calibrate the observer before running conversions: original repr must pass for
every sampled x, repr of the adjacent finite value away from zero must fail,
midpoints must follow even/odd low significand bit, and malformed/non-number
arrays must fail. These are oracle checks, not additional subject results.

## Outcomes and stopping

For each conversion report N, errors, first-output fidelity failures, stable
outputs, and joint stable-and-lossy outputs. Retain every original and both
outputs, rather than only selected examples. Run the complete fixed corpus once.
No stopping rule depends on results. If implementation or observer defects are
found, preserve the original run and explain any amendment and rerun.

## Interpretation limits

Same agent writes the harness, runs it, and interprets the result. This is not
independent replication. All implementation claims are restricted to the exact
recorded builds and options. Current SQLite upstream is newer than the installed
3.53.1 build; do not describe an observation as an unfixed upstream defect.
Search results cannot establish world-first novelty. A useful new measurement
must be distinguished from a known mathematical limitation or known bug.
