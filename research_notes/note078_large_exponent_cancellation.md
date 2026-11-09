# Note #078 — Equal decimal values can parse as infinity or zero in SQLite 3.54.1

**Status:** Draft — registered execution, self-tested; human look and independent review pending.
**Theme:** Software correctness / Numeric parsing / Representation invariance
**Author:** ChatGPT (OpenAI, GPT-6; Codex agent), at Chad Edward Holland's direction, November 7, 2026.
**Builds on:** [[note077_numeric_conversion_stability]] (the prior defect's novelty was rejected) and [[note044_circularity_test]] (observer limitations). The target is SQLite, with Python and JavaScript comparison arms.
**Method:** [METHOD.md](../METHOD.md), [WORKFLOW.md](../WORKFLOW.md), [CONTROLS.md](../CONTROLS.md) at `936ee25f708156ec005d3356735a270633837c63`.

## Limits first

- **Novelty is unresolved.** The exponent cap is old, visible source behavior. No confirmed prior report of these exact finite-value cancellation witnesses was found in the scoped searches. That does not establish a new bug discovery or world-first result.
- **Self-tested.** ChatGPT designed the source-derived prediction, exact oracle, corpus, C API wrapper and CLI reproducer. The source predictions were not blind. No independent person or separately authored observer has reproduced the result.
- **Human look not performed.** A named sample and full case-class counts are retained. C-SYNTH's person-look requirement remains pending; execution and green CI cannot promote the scientific claim.
- **Constructed inputs.** These spellings are long. No production prevalence, impact, security, performance or standards-violation conclusion is claimed. Empirical validity is NOT RUN.
- **Additional inspection is post-hoc.** The CLI reproducer, profile, named sample and handoff were written after the registered run. They preserve that run and do not add cases to it.

## The precisely refutable observation

For the pinned build and registered inputs, numeric conversion can depend on the
decimal spelling even when the exact rational value is unchanged. In particular,
the unit witnesses below denote exactly **1**, yet the two long spellings are
accepted as JSON and yield positive infinity and positive zero.

A separate observer returning **1** for those exact long inputs on the pinned
build, a failure of exact equivalence, or an identified API/oracle error would
refute the corresponding recorded observation. This is not an assertion about
all builds, all numbers, or what the SQLite project promises to support.

## Registration before execution

[PA-JSON-002_PREREG.md](../docs/PA-JSON-002_PREREG.md) was committed at
`5089867192d5d42d5c0ab9a3cd1f967cb596bb9f` before the test harness was written or
any candidate numeric input was executed. Source inspection, dependency building,
version inventory and input eligibility counts preceded the registration and are
disclosed there. The [receipt](../experiments/pa_json_002/REGISTRATION_RECEIPT.json)
records the public Git commit identity.

The tested release is **SQLite 3.54.1**, built from Git mirror commit
`57520227c95396ce39ba6ecaac8d475b78dd3964`. The generated amalgamation matched
the release's published SHA3. All calls used the real public C API through the
pinned shared library, not Python's older bundled SQLite.

## Raw observation before interpretation

Token construction notation below describes ASCII strings; the quotes and `+`
operators are not part of the tokens.

| Token construction | Exact value | SQLite JSON extraction | SQLite CAST AS REAL | Python / JavaScript |
|---|---:|---|---|---|
| `"1e0"` | 1 | 1 | 1 | 1 |
| `"1" + "0"*100000 + "e-100000"` | 1 | +infinity | +infinity | 1 |
| `"0." + "0"*100000 + "1e100001"` | 1 | +zero | +zero | 1 |

For the two transformed tokens, `json_valid` returned **1** and the SQL type was
`real`. The registered raw bit observations were:

| Case | Token bytes | Expected bits | SQLite JSON / CAST bits |
|---|---:|---|---|
| 12, integer padding | 100009 | `3ff0000000000000` | `7ff0000000000000` |
| 28, fraction padding | 100010 | `3ff0000000000000` | `0000000000000000` |

The algebra does not require approximate arithmetic: the first long value is
`10^100000 * 10^-100000`; the second is `10^-100001 * 10^100001`. Both equal **1**.

The complete corpus comprised **512** distinct transformed tokens representing
**16** distinct exact values. Every pair's rational equivalence was checked
before parsing. The raw output, retained verbatim in
[run.stdout.txt](../experiments/pa_json_002/results/run.stdout.txt), includes:

```text
P1: HELD
P2: HELD
P3: HELD
P4: HELD
P5: HELD
VERDICT 5 of 5 as registered
DIGEST c20ab3a00385be45ce58611401af3cbe816690db4051e3f805169d1aa9fd7ba2
```

| Route | Equivalent pairs | Pair disagreements | Baseline oracle mismatches | Transformed oracle mismatches | Errors |
|---|---:|---:|---:|---:|---:|
| SQLite JSON extraction | 512 | 166 | 0 | 166 | 0 |
| SQLite CAST AS REAL | 512 | 166 | 0 | 166 | 0 |
| Python float parsing | 512 | 0 | 0 | 0 | 0 |
| JavaScript JSON parsing | 512 | 0 | 0 | 0 | 0 |

These are complete counts for constructed cases, not population failure rates.
The post-hoc outcome classes were **346** preserved, **40** positive infinity,
**40** negative infinity, **43** positive zero and **43** negative zero. The
named [look sample](../experiments/pa_json_002/results/LOOK_SAMPLE.json) contains
**7** distinct cases, including the two unit witnesses, their negative
counterparts, and benign cases. A person has not inspected it.

## Predictions and instrument controls

| Prediction | Outcome | Observation |
|---|---|---|
| P1: an equivalent pair differs through JSON extraction | HELD | 166 differing pairs |
| P2: the named unit witnesses produce infinity and zero on both SQLite routes | HELD | Cases 12 and 28 match the registered exact bit patterns |
| P3: Python and JavaScript preserve the exact oracle value throughout | HELD | 0 errors or oracle mismatches in either arm |
| P4: instrument controls behave as registered | HELD | 10 exact-rounding calibration cases; 3 malformed JSON controls refused; benign small-padding cases preserved; planted unit-control error exits 1 |
| P5: all transformed inputs are accepted as numeric JSON | HELD | 512 valid, real-valued, successful extractions |

The oracle reads the complete decimal tokens as exact Fractions and computes
nearest binary64 values with integer division and ties-to-even. The target
results are observed as bits, not via SQLite's decimal printer. The small-padding
controls, deliberately different `1e0` / `2e0` values and malformed JSON cases
demonstrate that the instrument can distinguish outcomes. Its native sabotage
run printed `GATE: FAIL unit-control mismatch` and exited **1**. The gate checks
instrument consistency; it does not certify the research claim.

## Post-hoc convenience reproduction in SQLite's own shell

[minimal.sql](../experiments/pa_json_002/minimal.sql) constructs the same unit
witnesses using `hex(zeroblob(50000))`, which supplies the required zero digits.
It uses no persistent database. The [retained output](../experiments/pa_json_002/results/minimal_cli.stdout.txt)
from the same release's CLI was:

```text
label|bytes|valid_json|sql_type|parsed_value
baseline|3|1|real|1.0
integer_padding|100009|1|real|Inf
fraction_padding|100010|1|real|0.0
```

This reduces reliance on the ctypes wrapper as an explanation for the witness.
It is still a same-author post-hoc check, not independent reproduction.

## Interpretation and prior art

**Interpretation:** `sqlite3AtoF()` first accumulates a limited significand and
tracks a decimal-point offset. The explicit exponent is capped before being
combined with that offset. The long equivalent spellings require those two
large components to cancel. Clipping one component changes the combined scale,
consistent with the observed infinity/zero results. This explanation is grounded
in the [pinned source](https://github.com/sqlite/sqlite/blob/57520227c95396ce39ba6ecaac8d475b78dd3964/src/util.c#L878), not a new algorithm introduced by this note.

SQLite's [maintainer discussion](https://sqlite.org/forum/info/0b25ff2d9dbf6b8ae4c10993d6e804b031ea2a45dc6618b7e16d4fbd18ffb3ad?t=h)
already discloses significant-digit limitations and possible rounding differences
for long decimal inputs. The exponent cap also appears in historic source.
This record concerns exact finite-value cancellation and does not claim that
general floating-point parsing issues or that cap were previously unknown.
[SOURCES.json](../experiments/pa_json_002/SOURCES.json) retains the checked primary
sources and excerpts; later witness-specific searches are in POSTHOC.json.

The unit value **1** is exactly representable, so generic binary approximation of
a non-dyadic decimal is not an explanation for these particular witnesses. What
this means for supported input limits, intended API behavior and novelty still
requires outside review. No fix, upstream report or security claim is proposed.

## Validity and reproduction status

| Dimension | Status | Scope |
|---|---|---|
| Mathematical | PASS | Exact equivalence of the registered token constructions |
| Implementation | PASS, self-tested | Registered output from the pinned build and public API; no promotion while review is missing |
| Empirical | NOT RUN | Constructed cases, no production workload |
| Replication | self-tested | Same author wrote the observers and CLI convenience check |
| Human look | NOT PERFORMED | Named sample retained; C-SYNTH pending |
| Novelty | UNRESOLVED | No world-first, standards-violation or current-trunk execution claim |

The full answered trigger table remains in the immutable registration. No
registered prediction was edited after the run. Extra CLI/profile inspection
is disclosed as post-hoc. Other platforms, including Android / Termux, are
NOT VALIDATED for this study.

## Reference code and reviewer handoff

```bash
python3 scripts/note078_reference.py
```

[The archive guide](../experiments/pa_json_002/README.md) separates offline
inspection from a new target run. The complete compressed raw observations are
retained, and `RECORDED.json` pins the outcomes in a commit after the run commit.
CI re-runs are labelled re-runs, not independent replication.

[Claude's handoff](../docs/PA-JSON-002_CLAUDE_HANDOFF.md) asks for a separately built
dependency, independently written observer, wrapper/oracle review and prior-art
check. It has not been delivered via a direct Claude connection.

## Unrun door (M15)

A separately authored observer reproduces or refutes the unit witnesses on a
separately built pinned release and documents what the reviewer saw before
writing it. That remains unrun here. A separate current-trunk check is also
unrun and must not be inferred from the inspected release source.

---
*Provenance (M13): ChatGPT (OpenAI, GPT-6; Codex agent) inspected sources, designed,
built, ran and interpreted the experiment, and wrote this record → human
validation: not performed → human editing/curation: direction by Chad Edward
Holland → human responsibility: Chad Edward Holland. Review level: direction only.*
