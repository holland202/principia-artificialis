# PA-NS-001 Stage 2 provenance and reuse record

Status: development engineering evidence; no AI study or independent validation.
Chad Holland directed and authorized this work. ChatGPT (OpenAI GPT-6) inspected,
implemented, executed tests and drafted the analysis. Human review: direction only.
No attribution to another contributor or independent reviewer is implied.

## Public source boundary
- Repository `holland202/principia-artificialis`, ID 1302030647, visibility public
  confirmed before development.
- Initial branch `research/pa-ns-001-protocol-v0-2`:
  `8a3194f56f400a306778f7a837b51216c3b71220`.
- Compared main: `ae0afc07f8fae8b5f63657ed01b5fae988c777d6`.
- Pre-measurement engineering-plan commit:
  `4bdaa6535984716fa4816ad5d50c2c55a60e169f`.
- Original ns001.py and tests are preserved byte-for-byte in
  `evidence/stage2/baseline/original_ns001.py` and `original_test_ns001.py`, with
  SHA-256 in the baseline RUN.json. Original test_ns001.py remains unchanged.
- Original README and STAGE2_HANDOFF.md retain their historical statements;
  README receives an additive Stage 2 update, not replacement of its prior record.
- Inputs: those public PA files, canonical public method, public primary references
  below and synthetic analytic profiles authored in this branch. No private repository
  access, private-derived code, private artifact, credential or private architecture
  was used in this PA-NS-001 task. No cross-repository bridge exists in this package.

Every recorded command has stdout/stderr, exit code, Python/platform, source hashes
and timestamp. A RUN.json source_commit names the base commit; uncommitted code at
that run is identified by its source_sha256 map, not falsely claimed to have already
been committed. Later development commits preserve those bytes and raw failures.
Paths in exact command logs are local public-workspace paths, not external data.

## Primary technical inputs
| Source/version | Use and limits | Reuse/dependency disposition |
|---|---|---|
| [Python 3.12 floating-point tutorial](https://docs.python.org/3.12/tutorial/floatingpoint.html), page displayed 3.12.15, updated 2026-10-01 | binary64 representation, rational arithmetic; running interpreter is 3.12.14 | PSF License v2; examples Zero-Clause BSD; no documentation code copied |
| [NIST/SEMATECH confidence intervals §7.2.4.1](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm), retrieved 2026-10-20 | exact-binomial inversion and approximate worked example; not a sample-size endorsement | no reference code copied; original stdlib implementation tested against closed forms and published approximate roots |
| [statsmodels McNemar documentation](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html), displayed 0.15.0, retrieved 2026-10-20 | maintained alternative and definition of exact paired test; future analysis cross-check recommended | package not installed/added; no source copied or relicensed |
| [NASA/NPARC verification glossary](https://www.grc.nasa.gov/WWW/wind/valid/tutorial/glossary.html), updated 2021-02-10 | distinguish mathematical code verification from comparison to physical data | page contains attributed AIAA definitions; no wholesale copying |

Short verbatim excerpts, authors, URLs, displayed versions and exact UTF-8 hashes
are in `evidence/stage2/external_excerpts.json`. The excerpts are research inputs,
not endorsements. Source pages and prior theory are not claimed as PA inventions.
The NIST example's displayed upper endpoint .401029 is an approximation; direct
inversion gives about .4010281173. The test allows the example's display error and
also checks the defining binomial equations; this discrepancy is not hidden.

## Implementation and costs
No NumPy, SciPy, statsmodels, CFD framework, dataset, model download, paid service
or new Python dependency was introduced. Fraction is slower than a vectorized float
checker; exact rational arithmetic is feasible for this deliberately bounded
5–4097-sample analytic prototype, not evidence of general CFD scalability. Runtime
durations in RUN.json include the actual local process cost and are not benchmark
claims. A maintained statistics package remains an appropriate independent numerical
cross-check before freezing an actual AI-study analysis.

The new CI job uses the repository's existing official checkout/setup-python action
families, read-only contents permission and no persisted checkout credential. It runs
engineering scripts only on the specified development branch; no AI provider,
publication, Pages deployment, artifact upload, secret or private repository is used
by the new workflow. Existing repository workflows are separate and unchanged.

License: new owner-directed code follows this public repository's applicable code
terms. No external manuscript, private code, contributor snapshot or third-party
implementation is imported or relicensed. Attaching tests does not confer novelty,
patents, independent authorship or empirical truth.
