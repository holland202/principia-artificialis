# PA-JSON-001 — Numeric conversion: stability versus fidelity

**Status: EXPLORATORY archival record. Self-tested. Novelty rejected for the SQLite defect.**

## Limits first

- The run predates its first Git commit. The original local plan and hash freeze
  are preserved unchanged; they do not satisfy METHOD.md M2 / WORKFLOW.md W2.
- SQLite upstream already corrected the exact formatter in May. This is not a
  new or demonstrated-current SQLite defect.
- The generated corpus has no recorded human look. C-SYNTH remains unmet.
- ChatGPT designed, executed, and interpreted the run and wrote both observers.
  A second implementation is a self-check, not independent replication.
- These are finite-corpus conformance observations, not a population failure
  rate, production reliability estimate, or comparison of research methods.

The readable record is [Note 077](../../research_notes/note077_numeric_conversion_stability.md).
The original [protocol](PROTOCOL.md), [local freeze](FREEZE.json),
[summary](results/summary.json), [raw observations](results/cases.jsonl.gz),
[observer check](results/verification.json), and [deviations](DEVIATIONS.md) are retained.

## Inspect without rerunning the subjects

From the repository root:

```bash
python3 scripts/note077_reference.py
```

This verifies the archive hashes and frozen source identities, then rechecks
saved output values with the JavaScript bit-pattern observer. It requires Python
and Node, uses no network, and does not run a new SQLite experiment.

The planted in-memory observation error must be refused with exit code 1:

```bash
python3 scripts/note077_reference.py --sabotage
```

## Re-execute the original conversion study

This is a new run on the reader's installed builds, not a command to reproduce
the old counts on arbitrary SQLite versions. Use a new output directory:

```bash
python3 experiments/pa_json_001/run.py --out pa-json-001-reproduction
```

`run.py` and `node_transform.mjs` are unchanged from the local freeze. `verify.mjs`
was extended after the original observer check to read the compressed archive and
plant a sabotage error; this is documented in DEVIATIONS.md.

## Files

- `results/cases.jsonl.gz`: every input bit pattern and both outputs for every
  conversion, including the deliberately lossy constant-output control. Gzip
  decompression gives the exact `cases_sha256` bytes in the summary.
- `results/corpus_profile.json`: post-hoc counts of input classes.
- `results/look_sample.json`: named cases for a future human look; not human reviewed.
- `results/verification.json`: original second-observer output, before archiving.
- `results/verification_archived.json`: the same observations checked with the
  archive-aware observer; no subject rerun.
- `SOURCE_PROVENANCE.json`: source identities and claim-by-claim checks.
- `MANIFEST.sha256`: file integrity only; it does not certify the observations' truth.

**Provenance:** ChatGPT (OpenAI, GPT-6; Codex agent) → human validation: not
performed → human editing/curation: direction by Chad Edward Holland → human
responsibility: Chad Edward Holland. Review level: direction only.
