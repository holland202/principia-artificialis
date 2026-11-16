# CST-MECH-QUAL-001 qualification results

**Failure first:** PR #152's proposed positive-interaction gate admits a case in which
instructions improve both depths. It does not establish the crossover stated in the proposal.
The executable counterexample concerns the proposed instrument, not an observed AI behavior.

**Self-tested only.** Codex / OpenAI GPT-6 Astra designed, implemented and checked this package.
The review of ChatGPT's proposal is same-vendor. Both graph oracles share an author. Human
validation is direction only; human editing/curation and scientific review are pending.
Human responsibility: Chad Holland. No new model inference, independent reproduction,
confirmatory dataset access or merge occurred.

## Registration and scope

[Registration](CST_MECH_QUAL_001_PREREG.md) was committed locally as `e12100e` before any
implementation or execution. Its registration-only tree was subsequently published as
`fe724ebab9acf910843ab60862b0b6bf89c5633d`. Publication happened after the local run; a public
pre-execution timestamp is not claimed. The branch preserves registration, execution and
outcome-pinning commits separately. No scientific protocol was frozen.

This is deterministic qualification of public constructed fixtures and review of already public
development archives. It is not a learned-agent simulation or a model experiment.

## Raw outcome

The [normal output](../results/cst_mech_qual/qualification.txt) was opened and read, including
the constructed both-benefit counterexample, before this record was written.

```text
VERDICT 5 of 5 as registered
DIGEST 998986f84b23a83cd59a2b11ece89787433922816a2de2c7034464248fb892ba
```

The [sabotage output](../results/cst_mech_qual/sabotage.txt) was also opened and read.

```text
VERDICT 2 of 5 as registered
DIGEST 264e202a9319b05a32c326e24e4d8dd55ac368127e8d073c4195d026c18dd416
EXIT_CODE 1
```

| Prediction | Normal outcome | Meaning |
|---|---|---|
| Q1 | HELD | The proposed #152 gate accepts a constructed same-direction benefit. |
| Q2 | HELD | Proposed directional checks reject that case and other named rivals. Generic-arm equality defeats specificity. |
| Q3 | HELD | Fixture graph oracles agree, node renaming preserves labels, and unused cycles/dangling edges fail. |
| Q4 | HELD | Named archive corruption and parser cases fail closed; constant labels solve no pairs. |
| Q5 | HELD | Exact-tail boundary cases agree; changing the live oracle defeats the qualification gate. |

Oracle sabotage flips Q3/Q4/Q5, while Q1/Q2 remain true because their arithmetic fixtures are
independent of the graph oracle. This is the expected fault path. It is not a failed scientific
prediction and does not overwrite the normal result.

The normal fixture scores 48/48 pairs. Both constant-label fixtures score 0; oracle sabotage
scores 0. The fixed manifest has 8 blocks, 32 graph cases and 96 instruction-specific trials.
These are constructed checks, not 96 AI responses. Graph bodies have 117 characters; instruction
prefixes are not tokenizer matched. No claim of model-task equivalence follows from that count.

## Archive replay and validation

The [replay](../results/cst_mech_qual/archive_replay.txt) re-executes the original CST scorer
on public dev and dev2 only. It also checks duplicate keys and prints raw archive hashes. This
is not a new independent scorer or inference run. The [shortlist](DISCOVERY_SHORTLIST_2026-11-15.md)
contains the bounded interpretation. Existing result files and registrations are unchanged.

Local repository tests, with the CST test file excluded, report:

```text
478 passed, 7 skipped, 2 warnings, 111 subtests passed in 35.41s
```

See [raw test output](../results/cst_mech_qual/repository_tests.txt). The excluded file,
`experiments/cst_001/test_cst001.py`, calls `cases.build("test", ...)`. Running it would generate
the old sealed holdout, contrary to Chad's current restriction. This is the explicit W7 scope
exception. The skipped tests and warnings are retained; the complete unfiltered suite was not run.

Pinned `vacuity_lint` at `718d103bfdc1eea84d2a86a32853ae3472eb6675`, SHA-256
`028d48687615b998373279660e4022acfcaa1735ea682a3db83ef8bee940f0d9`, found no issues in the new
package. The [repository-wide output](../results/cst_mech_qual/repository_vacuity_lint.txt)
retains existing findings in `exp050_seasonal_capacity_harness.py`, `qm_obs_001_audit/check.py`,
`make_index.py`, and `note053_reference.py`. Those files are unchanged from the review base.
`method_lint.py` and its planted-defect self-test succeeded. A dedicated workflow checks the
bounded new package without generating the old holdout.

## Limits and pending work

| Axis | Status |
|---|---|
| Mathematical | Exact arithmetic checked on named fixtures. A statistical guarantee for a future clustered scientific design is not established. |
| Implementation | SELF-TESTED on the recorded Linux/Python environment. General parser/oracle correctness and independent verification remain open. |
| Empirical AI behavior | NOT RUN in this work. Archived development observations remain exploratory. |
| Novelty | NOT ESTABLISHED. Close primary-source prior art is recorded. |

Human inspection of the [named qualification sample](../results/cst_mech_qual/human_review_sample.json)
is pending. This prevents treating the generated cases as a scientifically qualified assay.
The manifest fingerprint binds prompts, not real model provenance. There is no inference runner,
short-format decoder, tokenizer match, sealed new dataset or approved campaign.

**Next unrun test:** Claude or another reviewer writes a graph oracle without reading these
implementations and checks the causal intervention. A statistical reviewer checks the crossover
and specificity estimands, uncertainty intervals and sampling unit. Only then prepare and freeze
real-model qualification and a fresh owner-approved confirmatory protocol.

## Review update, 2026-11-16

Claude found that the node-name suffixes reveal the answer without source tracing. Codex
reproduced the shortcut on every qualification case. The original Q1–Q5 outcomes are preserved,
but do not establish shortcut resistance. The cases are inadmissible as a scientific
source-tracing assay until separately revised and qualified. The [follow-up record](CST_MECH_REVIEW_2026-11-16.md)
also shows why replacing pair accuracy with Youden J alone does not remove the decision-bias
rival. No new model inference occurred.
