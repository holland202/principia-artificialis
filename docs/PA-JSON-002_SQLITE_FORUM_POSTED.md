# PA-JSON-002: SQLite forum report, as posted

**Status:** SUBMITTED, awaiting moderator approval (as of 2026-11-09 04:20 UTC). There is no maintainer response
yet.

| | |
|---|---|
| Thread | https://sqlite.org/forum/forumpost/4db7e4cd27a7ee1d583f080fe31ab8f9f66e96ab16c0aae8db4ecde414475e04 |
| Posted | 2026-11-09 04:18:04 UTC, by Chad Holland from his own SQLite forum account (holland202) |
| Draft it came from | [PA-JSON-002_SQLITE_FORUM_DRAFT.md](PA-JSON-002_SQLITE_FORUM_DRAFT.md) (ChatGPT), with three additions from Claude's review on PR #128 (note pa/claude/128-1) |
| Final text | below, verbatim, as also recorded in note pa/claude/128-2 on PR #128 |

Claude prepared the final text. It could not post it: the forum requires a human check, and Claude does not
complete those. Chad posted it himself, and the forum's own page confirms the post (artifact `4db7e4cd27`).

## Title

Long decimal numbers equal to 1 read as Inf or 0.0 (exponent cap in sqlite3AtoF)

## Body (Markdown, as posted)

~~~~markdown
SQLite 3.54.1 on Linux x86_64 (source id 2026-10-16 14:45:20 555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76), CLI built from the official amalgamation. The same output came from two separate builds (GCC 13.3 and 14.2).

These inputs are valid JSON numbers whose exact value is 1. Both json_extract() and CAST(... AS REAL) return Inf or 0.0:

```
.mode list
WITH input(label,v) AS (
  VALUES ('baseline','1e0'),
         ('integer_padding','1'||hex(zeroblob(50000))||'e-100000'),
         ('fraction_padding','0.'||hex(zeroblob(50000))||'1e100001')
)
SELECT label, length(v), json_valid(v), json_extract(v,'$'), CAST(v AS REAL)
FROM input;
```

```
baseline|3|1|1.0|1.0
integer_padding|100009|1|Inf|Inf
fraction_padding|100010|1|0.0|0.0
```

Expected: 1.0 in both value columns of every row.

The same thing can turn a value that rounds to 0.0 into an ordinary finite number. This 10,010-byte input is exactly 42e-90000, and Python's json.loads() returns 0.0 for it:

```
WITH input(v) AS (VALUES ('42'||hex(zeroblob(5000))||'e-100000'))
SELECT length(v), json_valid(v), json_extract(v,'$'), CAST(v AS REAL) FROM input;
```

```
10010|1|42.0|42.0
```

The apparent cause is this line in sqlite3AtoF() (src/util.c: line 960 at the 3.54.1 check-in, line 967 on current trunk, 2a4fb623):

```
exp = exp<10000 ? (exp*10 + v) : 10000;
```

An explicit exponent of 100000 or more becomes 10000. Each extra significand digit, though, still shifts the decimal exponent with no limit, so the two no longer cancel. The cap dates from check-in 4becc47eb4d48686 (2011-10-17, to avoid 32-bit overflow).

Is this intended? Or should a compensating exponent be preserved, for example by capping the combined exponent rather than the explicit one? We have not built or run trunk, and we make no claim about novelty or security impact.

Full records: https://github.com/holland202/principia-artificialis (PA-JSON-002, pull requests #123 and #125).

This was found and checked with AI assistance (ChatGPT and Claude) under my direction. I have not verified it by hand.

Chad Holland
~~~~

## Next (door)

- **When the moderator approves the post:** confirm that the thread is public.
- **If maintainers reply or change the code:** record the reply verbatim, with its author and date. Then re-run
  `experiments/pa_json_002/upstream/minimal.sql` and Claude's `check_c.py` cases on the fixed version. Under a fix,
  every D3 token should match its exact oracle, not the model.

Provenance (M13): report drafted by ChatGPT (OpenAI, GPT-6; Codex agent); final text and this record by Claude
(Anthropic, Opus 5.5); posted by Chad Holland → human validation: not performed → human responsibility: Chad
Holland. Review level: direction only. The post itself says that it was found with AI assistance and not verified
by hand.
