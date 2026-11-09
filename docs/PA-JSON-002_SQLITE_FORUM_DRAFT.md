# PA-JSON-002 — SQLite forum report draft

Prepared 2026-11-08 (America/Chicago; execution host 2026-11-09 UTC).
**Recommendation: report upstream. State: DRAFT — NOT POSTED.**

The two registered witnesses both denote exactly one, so the report can ask a
concrete numeric-correctness question without depending on underflow terminology
or a claim of novelty. Use the following short post after owner review.

---

**Proposed title:** SQLite 3.54.1 reads long decimal numbers equal to 1 as infinity or zero

On Linux x86_64, SQLite 3.54.1 accepts these JSON numbers but returns infinity or
zero through both `json_extract` and `CAST AS REAL`. Each input's exact rational
value is 1. The following runs in the SQLite CLI without a database file:

```sql
.mode list
.headers on
SELECT sqlite_version(), sqlite_source_id();
WITH input(label,v) AS (
  VALUES ('baseline','1e0'),
         ('integer_padding','1'||hex(zeroblob(50000))||'e-100000'),
         ('fraction_padding','0.'||hex(zeroblob(50000))||'1e100001')
)
SELECT label, length(v), json_valid(v),
       json_extract(v,'$'), CAST(v AS REAL)
FROM input;
```

Observed value rows:

```text
baseline|3|1|1.0|1.0
integer_padding|100009|1|Inf|Inf
fraction_padding|100010|1|0.0|0.0
```

Expected numeric results: 1.0 in both columns for every row. The integer padding
represents `10^100000 * 10^-100000`; the fraction padding represents
`10^-100001 * 10^100001`.

Source ID:
`2026-10-16 14:45:20 555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76`.
The CLI was built from the release source with GCC 14.2. A separately written
C observer using the official amalgamation reproduced the behavior in another
AI-assisted check.

The apparent mechanism is in
[`sqlite3AtoF()`](https://github.com/sqlite/sqlite/blob/57520227c95396ce39ba6ecaac8d475b78dd3964/src/util.c#L960):
`exp = exp<10000 ? (exp*10 + v) : 10000;`
An explicit exponent above 99,999 becomes 10,000 before it is combined with the
significand's decimal offset.

Is this intended numeric-conversion behavior, or should compensating decimal
exponents preserve the value here? Current trunk and other platforms have not
been tested. We have not established novelty or a security impact.

Reproducible records: [original study, PR #123](https://github.com/holland202/principia-artificialis/pull/123)
and [separate check, PR #125](https://github.com/holland202/principia-artificialis/pull/125).
Research directed by Chad Holland with ChatGPT and Claude assistance; human
validation has not been performed.

---

## Evidence and scope of this draft

- Checked against main at `7452707568cac76fa589673dca54b5f8bf5c2348`.
- [SQL as rerun](../experiments/pa_json_002/upstream/minimal.sql) and
  [complete output](../experiments/pa_json_002/upstream/minimal.stdout) are kept
  together. These are the registered unit-value cases with a convenience CLI
  observer, not a new campaign or a new registration.
- The draft avoids the separate check's incorrect phrase "exact value is 0".
  [The appended correction](../experiments/pa_json_002_claude/RESULTS.md#correction-2026-11-08-exact-rational-value-and-rounded-binary64-value)
  distinguishes a tiny nonzero rational from its rounded binary64 value.
- No SQLite forum post, upstream ticket, source patch or external message has
  been sent by ChatGPT. Main has not been changed by this draft.

Provenance (M13): ChatGPT (OpenAI, GPT-6; Codex agent) wrote the draft and reran
the CLI reproducer; Claude (Anthropic, Opus 5.5) supplied the separately recorded
observer check and causal analysis → human validation: not performed → human
editing/curation: direction only, Chad Holland → human responsibility: Chad Holland.

Door (unrun): after an upstream response or fix, record the response and test
the affected release with the frozen cases. Until then, upstream status is unreported.
