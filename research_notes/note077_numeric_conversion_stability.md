# Note #077 — A stable JSON conversion can change the original numeric value

**Status:** Draft — EXPLORATORY archival record; no PA confirmation or novelty promotion.
**Theme:** Software correctness / Serialization / Test oracles
**Author:** ChatGPT (OpenAI, GPT-6; Codex agent), at Chad Edward Holland's direction, November 7, 2026.
**Builds on:** [[note073_repair_verification_intake]] and [[note044_circularity_test]] for the distinction between what a checker observes and what its user might infer. The software examined here is Python, JavaScript, and SQLite, not a Sovereign project.
**Method:** [METHOD.md](../METHOD.md), [WORKFLOW.md](../WORKFLOW.md), and [CONTROLS.md](../CONTROLS.md), read at `cc4f2a9b8f4c0d915ede89a1041770ac0e8a8d88`. The deviations below prevent promotion under that method.

## What went wrong, first

- **Novelty rejected for the defect.** SQLite had already changed this exact JSON formatter from `%!0.15g` to `%!0.17g` in [upstream commit 5b98467](https://github.com/sqlite/sqlite/commit/5b98467d28aa1ceff5602b54a0cd7c0d3f1c8fb0), dated May 29, 2026. Our run exercised an older installed build. It does not establish a new or still-unfixed SQLite bug.
- **The local plan was not committed before execution.** [PROTOCOL.md](../experiments/pa_json_001/PROTOCOL.md) and [FREEZE.json](../experiments/pa_json_001/FREEZE.json) were written locally before the systematic run, after initial exploration. They are preserved unchanged, but do not satisfy M2 / W2. No prediction is retrospectively scored as registered.
- **The same agent made and checked the result.** The exact-rational observer and JavaScript bit-pattern observer agreed, but both were written by ChatGPT. Replication level: **self-tested**; no independent review.
- **Human look not performed.** Generated-input classes and a named [look sample](../experiments/pa_json_001/results/look_sample.json) are available; C-SYNTH remains unmet. These observations remain EXPLORATORY and are not cited as a promoted finding.

Full [deviations](../experiments/pa_json_001/DEVIATIONS.md) remain part of the evidence.

## The question and precisely refutable observation

For a conversion T of a JSON document, compare the properties:

\[
T(T(s)) = T(s)
\]

and preservation of the binary64 value represented by the original input.

The archived, self-tested observation is that the specified SQLite numeric path
produced byte-stable outputs for every input in the fixed corpus while changing
the binary64 value for the subset recorded below. A raw row with inconsistent
flags, an incorrect exact-value interval, or a disagreement in the recomputed
counts refutes the corresponding recorded observation. This is a conformance
audit of these inputs and builds, not an estimate of software failure rates.

## Observation before interpretation

Installed subjects: Python **3.12.14**, Node **24.22.1**, SQLite **3.53.1**.
SQLite source identity:

```text
2026-05-05 10:34:17 c88b22011a54b4f6fbd149e9f8e4de77658ce58143a1af0e3785e4e6475127e9
```

Each route received the same **16384** distinct finite, nonzero binary64 inputs
as one-number JSON arrays. Full versions, compile options, and generator details
are in [summary.json](../experiments/pa_json_001/results/summary.json).

| Conversion | Inputs | First output changes binary64 value | Second output equals first | Both stable and changed |
|---|---:|---:|---:|---:|
| Python `json.loads` → `json.dumps` | 16384 | 0 | 16384 | 0 |
| JavaScript `JSON.parse` → `JSON.stringify` | 16384 | 0 | 16384 | 0 |
| SQLite `json_array(json_extract(s,'$[0]'))` | 16384 | 15384 | 16384 | 15384 |
| SQLite `json_array(s -> '$[0]')` | 16384 | 0 | 16384 | 0 |
| SQLite extraction → `CAST(... AS TEXT)` → array delimiters | 16384 | 0 | 16384 | 0 |
| SQLite extraction → `printf('%!.17g',...)` → array delimiters | 16384 | 0 | 16384 | 0 |
| Deliberately lossy control: always return `[0]` | 16384 | 16384 | 16384 | 16384 |

All routes recorded **0** execution errors. The last row is a planted control,
not a production implementation. The numbers above are printed by
[the reference script](../scripts/note077_reference.py) after checking the saved archive.

One raw observation (case **0**, input bits `1dd0489ce846ab8c`):

```text
input:                  [4.418287677518092e-165]
sqlite_numeric first:   [4.41828767751809e-165]
sqlite_numeric second:  [4.41828767751809e-165]
stable: true
fidelity_loss: true
sqlite_cast first:      [4.4182876775180923e-165]
sqlite_cast second:     [4.4182876775180923e-165]
stable: true
fidelity_loss: false
```

The cast output illustrates why bytes alone are not the fidelity oracle: a
different decimal spelling can still round to the original binary64 value.

## Instrument and generated inputs

The first observer parses decimal digits to exact integer fractions and checks
the exact midpoint interval for the original binary64 value, including tie
parity. It does not parse target numeric output with `float()` to decide fidelity.
The second observer reparses the saved output in JavaScript and compares its
binary64 bits. It recorded **0** disagreements with the exact observer. This is
a second implementation by the same author, not independent replication.

The observer's calibration accepted **16384** original representations, rejected
**16384** adjacent finite values, exercised **16** midpoint endpoints and **8**
malformed or nonnumeric cases. The planted zero-output conversion demonstrates
that a stable result can fail the fidelity observation on every nonzero input.
The archive checker also has a sabotage path that flips a stored observation
flag in memory; it must exit nonzero without altering the archive.

The [post-hoc profile](../experiments/pa_json_001/results/corpus_profile.json)
reports **8144** positive and **8240** negative values, **16377** normal and **7**
subnormal values, **7751** integer-valued and **8633** noninteger-valued binary64
values, and **2046** distinct exponent fields. The generator made **16391** draws
and rejected **7** nonfinite patterns. There are **16384** distinct bit patterns;
the SQLite numeric route's outcome classes contain **15384** changed and **1000**
preserved values. The named sample has **7** distinct cases covering these
outcome classes and selected input classes. A person has not reviewed it.

These counts describe the constructed corpus only. They do not describe the
distribution of JSON values in actual applications. Zero, signed-zero identity,
NaN inputs, infinity inputs, arbitrary-precision integer semantics and
exact-decimal semantics were excluded by the local plan.

## Known mathematics and checked prior art

**Established mathematics, not new:** the constant conversion T(s) = `[0]` is
idempotent and fails to preserve every nonzero input. Therefore idempotence does
not imply fidelity. A correct stability test can pass a lossy conversion; that
does not make the stability test an incorrect test of its stated property.

| Primary source | Checked observation | Consequence for this record |
|---|---|---|
| [SQLite upstream formatter correction](https://github.com/sqlite/sqlite/commit/5b98467d28aa1ceff5602b54a0cd7c0d3f1c8fb0) | Inspected the source diff changing `%!0.15g` to `%!0.17g` and the regression test added with it | Reject a new-defect claim; do not extrapolate this old build's result to current SQLite |
| [SQLite floating-point documentation](https://sqlite.org/floatingpoint.html) | It explains why decimal rendering precision can affect binary64 round trips | Rounding-induced loss is established prior knowledge |
| Möller et al., [Cross-Language Differential Testing of JSON Parsers](https://www.mlsec.tu-berlin.de/docs/2024b-asiaccs.pdf), ASIA CCS, 2024 | The paper already studies semantic discrepancies among JSON parsers | Cross-runtime comparison is not a new method proposed here |

Exact retained excerpts, source identities, and claim checks are in
[SOURCE_PROVENANCE.json](../experiments/pa_json_001/SOURCE_PROVENANCE.json).
Source attribution is not outside validation of our measurements.

**Interpretation:** the recorded contrast is consistent with the older JSON
constructor's fixed decimal precision, while the other tested routes retain the
input's binary64 meaning. This is not a proof that the alternate routes preserve
every JSON value, an application-independent repair recommendation, or evidence
that SQLite's current implementation has this defect.

## Validity and claim limits (M7)

| Axis | Status | Scope |
|---|---|---|
| Mathematical | PASS | The elementary distinction between idempotence and fidelity; established mathematics, no new theorem |
| Implementation | NOT RUN as PA registered confirmation | Exploratory raw outputs and self-checks are retained; the registration and human-look gaps prevent promotion |
| Empirical | NOT RUN | Generated numeric inputs; no production workload or field experiment |
| Independent review | NOT RUN | Same agent authored both observers |
| Novelty | New-defect claim rejected | The upstream correction predates the study; no world-first claim for the measurements or principle |

## Reference code and raw evidence

[Archive instructions](../experiments/pa_json_001/README.md) separate inspection
of saved observations from re-execution on different installed builds.

```bash
python3 scripts/note077_reference.py
```

This command inspects the archive; it does not run the subjects again. The
original observations are retained as [gzip-compressed JSONL](../experiments/pa_json_001/results/cases.jsonl.gz).
Their uncompressed SHA-256 is:

```text
772f60a8dd12d893a308b0e55e988726eaf62ff35b24ac5d45502ebb86ff5dda
```

## Triggered controls (retrospective disclosure, M16)

This table records applicability; it does not retroactively register the run.

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | Yes: eligibility and distinct-input counts matter; counts retained, no separate precommit feasibility record |
| Noise | C-NOISE | No: fixed built-in numeric conversions; no timing, model sampling, or concurrency claim |
| Statistics | C-STAT | No: finite-corpus counts only, no estimated rate or population hypothesis |
| Evidence | C-EVID | No: the subject is numeric conversion, not freshness, source, or provenance handling |
| Independence | C-INDEP | Yes: both observers are self-tested; no reproduction or replication claimed |
| External | C-EXT | Yes: primary-source checks and retained excerpts; no outside endorsement |
| Device | C-DEVICE | Yes: exact host/build identities retained; other platforms, Android/Termux included, NOT VALIDATED |
| Verdict code | C-BUILD | Yes: archive checker refuses missing/corrupt evidence and a planted observation inconsistency; integrity is not truth |
| Exploration | C-EXPLORE | Yes: exploratory probe, systematic local run, and post-hoc audit logged in FORKS.md; no promotion |
| Method comparison | C-METHCOMP | No: no claim of superiority between research methods; only fixed conversion outputs and the logical distinction between properties |
| People's data | C-PRIVATE | No: synthetic numbers and public-source attribution only; no private dataset or message imported |
| Design | C-DESIGN | Yes: deterministic conformance audit; strongest admissible claims concern these inputs and builds |
| Held-out | C-HOLDOUT | No for the finite-corpus record: no selection, threshold fitting, or model training on these cases; the question was shaped by earlier probes and is labelled exploratory |
| Generated inputs | C-SYNTH | Yes: classes and named sample retained; required human look remains NOT PERFORMED |

## Falsifiable next prediction — unrun door (M15)

**P-NEXT, proposed, not registered or run:** On a pinned current SQLite release,
at least one pair of valid JSON numeric tokens that are exactly equal as rational
numbers, constructed by redistributing trailing zeros between a significand and
its decimal exponent, parses to different binary64 values. A future bounded test
must specify its full token grammar and corpus in a separate committed
registration before execution. No difference across that frozen corpus refutes
the bounded candidate. Current-release execution, fresh confirmation, prior-art
review for this narrower candidate, and a human look are still required.

---
*Provenance (M13): ChatGPT (OpenAI, GPT-6; Codex agent) designed the probe, wrote
and ran the code, checked sources, and drafted the record → human validation:
not performed → human editing/curation: direction by Chad Edward Holland → human
responsibility: Chad Edward Holland. Human review level: direction only.*
