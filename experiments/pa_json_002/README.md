# PA-JSON-002 — Large exponent cancellation

**Status: registered execution, self-tested; novelty and human review pending.**

SQLite 3.54.1 returned different numeric values for 166 of the 512 registered
exact-equivalent pairs. Both SQLite routes accepted the inputs without errors.
Python and JavaScript preserved the oracle values on this corpus. The complete
observations and the original source are retained; this is not a population
failure rate or a claim about production impact.

- [Note 078](../../research_notes/note078_large_exponent_cancellation.md)
- [Committed registration](../../docs/PA-JSON-002_PREREG.md)
- [Claude handoff](../../docs/PA-JSON-002_CLAUDE_HANDOFF.md)
- [Original raw output](results/run.stdout.txt)
- [Complete observations](results/observations.jsonl.gz)
- [Named human-look sample](results/LOOK_SAMPLE.json), review NOT PERFORMED

## Inspect the stored observations offline

From the repository root:

```bash
python3 scripts/note078_reference.py
```

This checks identities, reconstructs every registered case and its exact value,
recomputes the saved observations' summary and digest, and requires the separately
pinned outcome. It does not execute SQLite again or access the network. A valid
hash shows integrity of this record, not independent truth.

The planted unit-control mismatch must exit 1:

```bash
python3 scripts/note078_reference.py --sabotage
```

## Build and reproduce

Requirements on the tested Linux environment: Python, Git, C compiler, make, Tcl,
and Node for the JavaScript reference arm. Other platforms, including Android /
Termux, have not been tested for this study.

Build the pinned public-domain SQLite release in a new directory:

```bash
python3 experiments/pa_json_002/build_sqlite.py --out pa-json-002-build --cli
```

The source commit and official amalgamation SHA3 must match before compilation.
Inspect the two unit witnesses using SQLite's own shell:

```bash
pa-json-002-build/sqlite3 < experiments/pa_json_002/minimal.sql
```

Re-run the full fixed corpus (requires a new output directory):

```bash
python3 experiments/pa_json_002/run.py --sqlite-lib pa-json-002-build/libsqlite3-pa-json-002.so --out pa-json-002-reproduction
```

The deterministic semantic digest must match RECORDED.json. Build/host metadata
is recorded separately; it does not enter that digest. CI re-runs this same
registered corpus and the native sabotage control. CI is a re-run, not
independent replication.

## History and limits

1. Registration: `5089867192d5d42d5c0ab9a3cd1f967cb596bb9f`.
2. Executed code and complete first-run data: `c9c825460bef715c23b8633c0b2fc66ed74e353f`.
3. Separate outcome pin: `59f8d5c1ad78a19d76a405588fdf74a0eff476e1`.

`minimal.sql`, the CLI output, profile, named sample, reviewer handoff, and
archive wrapper were added after the registered run and are labelled post-hoc
convenience/inspection artifacts. The registered run files and predictions are
unchanged. The source-derived hypothesis is not a blind prediction. Neither a
human sample look nor an independent reproduction has occurred. No upstream
report or SQLite patch has been submitted.

**Provenance:** ChatGPT (OpenAI, GPT-6; Codex agent) → human validation: not
performed → human curation: direction by Chad Edward Holland → human
responsibility: Chad Edward Holland. Review level: direction only.
