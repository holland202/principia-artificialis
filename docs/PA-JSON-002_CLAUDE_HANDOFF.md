# Claude handoff — PA-JSON-002

Chad asked ChatGPT to tell Claude what is being built and to request a separate check.
This is a copy-ready brief; it has not been sent through a direct Claude connection.

## What we are building

A reproducible software-correctness experiment and evidence package in
Principia Artificialis: **can mathematically equal JSON numeric spellings
produce different values in current SQLite?** This examines external software,
not a Sovereign repository's implementation.

- Repository: <https://github.com/holland202/principia-artificialis>
- Research branch: `chatgpt/pa-json-002-decimal-equivalence-20261107`
- Registration, committed before the harness and numeric run:
  `5089867192d5d42d5c0ab9a3cd1f967cb596bb9f`
- Harness and complete first-run observations:
  `c9c825460bef715c23b8633c0b2fc66ed74e353f`
- Separate outcome pin:
  `59f8d5c1ad78a19d76a405588fdf74a0eff476e1`
- Protocol: `docs/PA-JSON-002_PREREG.md`
- Code/data: `experiments/pa_json_002/`
- Readable account: `research_notes/note078_large_exponent_cancellation.md`

The prior PA-JSON-001 defect was already fixed upstream, and its novelty claim
was rejected. This new registered run targets SQLite **3.54.1**, built from the
official release source, whose amalgamation hash matches the published hash.

## What the first run recorded

Across **512** fixed exact-equivalent pairs, SQLite JSON extraction and CAST each
disagreed on **166** baseline/transformed pairs. Python's float parser and
JavaScript's JSON parser had **0** disagreements with the exact oracle. The
instrument recorded **5 of 5 as registered**. It is **self-tested**, not an
independent reproduction or a world-first novelty claim.

The strongest witnesses need no subtle rounding argument:

| Token construction | Exact rational value | SQLite JSON/Cast result | Python/JavaScript |
|---|---:|---|---:|
| `1e0` | 1 | 1 | 1 |
| `"1" + "0"*100000 + "e-100000"` | 1 | positive infinity | 1 |
| `"0." + "0"*100000 + "1e100001"` | 1 | positive zero | 1 |

SQLite reports both long tokens as valid JSON with SQL type `real`. The two
long-token observations are registered cases **12** and **28**. A post-hoc
convenience SQL reproducer also exhibits them in SQLite's own CLI. That CLI
check is by the same ChatGPT author and is not independent replication.

Pinned semantic digest:

```text
c20ab3a00385be45ce58611401af3cbe816690db4051e3f805169d1aa9fd7ba2
```

## What I am asking you to check

1. Rebuild the exact SQLite release independently and run `minimal.sql` first.
   For a stronger implementation check, write your own small C API observer
   from the protocol before reading `run.py`; copy double bits with `memcpy`.
   Check that baseline and transformed inputs are the same exact rational and
   that no API error, NULL coercion, or display formatting explains the result.
2. Review the oracle, generated corpus, C API wrapper, and controls. Try to
   refute the reported observations. Reusing our harness is a re-run; a new
   observer or separately generated corpus must be identified honestly.
3. Check prior art for **finite-value significand/exponent cancellation**, not
   merely general floating-point rounding or the well-known exponent cap.
   Challenge whether this is a correctness defect, a documented numeric limit,
   or another implementation choice. No standards-violation claim is made.
4. Return exact source/version/hash, commands, raw output, observed differences,
   and what you read before writing your checker. Preserve all negative results.

You already know our reported results from this handoff. Do not call the review
blind. A different AI family is not an independent human reviewer. Human sample
inspection remains NOT PERFORMED, and no scientific status promotion is claimed.
Do not edit the registration, replace original results, merge a PR, or post an
upstream report as part of this requested check.

## Commands — one at a time

Inspect the saved archive without any new subject run or network:

```bash
python3 scripts/note078_reference.py
```

Build the pinned source and CLI into a new directory (requires Git, C compiler,
make and Tcl; commands were tested on Linux):

```bash
python3 experiments/pa_json_002/build_sqlite.py --out pa-json-002-build --cli
```

Use SQLite's CLI on the two witnesses:

```bash
pa-json-002-build/sqlite3 < experiments/pa_json_002/minimal.sql
```

Re-run the complete original corpus on the new build:

```bash
python3 experiments/pa_json_002/run.py --sqlite-lib pa-json-002-build/libsqlite3-pa-json-002.so --out pa-json-002-reproduction
```

Target source Git commit: `57520227c95396ce39ba6ecaac8d475b78dd3964`.
Official amalgamation SHA3-256:

```text
e2b869d3003b33c942b7dd7063604fbc53553e1b66609570df39b9b7b558ee81
```

**Provenance:** ChatGPT (OpenAI, GPT-6; Codex agent) wrote this handoff at Chad
Edward Holland's direction. Human validation not performed; human curation is
direction only; human responsibility: Chad Edward Holland.
