# Stage 2 — External evidence qualification: MLPerf and vLLM perf-eval

Date: 2026-10-21. **DESK REVIEW ONLY — NOT PA INDEPENDENT REPRODUCTION.** No experiments, benchmark executions, scientific registration or status promotion.

## MLPerf Inference (MLCommons)
Primary sources:
- https://github.com/mlcommons/inference
- https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc
- https://github.com/mlcommons/policies/blob/master/submission_rules.adoc
- https://github.com/mlcommons/inference/blob/master/Submission_Guidelines.md

**Source-confirmed design features:** Reference implementations and workload descriptions; benchmark rules explicitly require replicability, restrict nondeterminism, prohibit benchmark-specific detection and input-dependent optimizations, and specify shared benchmark implementations. Rules also distinguish performance, quality and hardware/software configuration.

**Qualification:** Strong external *methodological reference*, not a PA-reproduced result. MLPerf submission review is not interchangeable with journal peer review. Individual result claims need exact round, division, scenario, submission, configuration, code and dataset identities.

**Outstanding:** Pin exact policy/repository commits, confirm licensing for every reused component and dataset, select one appropriately sized reference case, document measurement boundaries and tolerances. No execution authorized.

## vLLM perf-eval
Primary source: https://github.com/vllm-project/perf-eval

**Source-confirmed design features:** YAML recipes bind model and hardware to evaluation tasks; Buildkite discovers workload recipes. Documented modules include model serving, lm-eval accuracy, vllm bench throughput/latency, aiperf profiling, and BFCL function-calling evaluations. README identifies CPU-only pipeline regression tests and GPU-dependent end-to-end runs.

**Qualification:** Useful *production engineering evaluation framework*, not proof of independently validated scientific results. Nightly tracking and tests do not themselves prove cross-hardware performance comparability or statistical significance.

**Outstanding:** Pin repository and vLLM commits, workload recipe and container digest; inspect dataset/version licensing, environment, repetitions, variance, accuracy targets, warmup and latency definitions; distinguish CI smoke tests from executed GPU evaluations. No execution authorized.

## Comparative assessment

| Dimension | MLPerf | vLLM perf-eval |
|---|---|---|
| Primary role | Standardized benchmark and submission methodology | Continuous production-oriented evaluation workflows |
| Controls visible in primary documentation | Replicability, reference equivalence, scenario and quality constraints | Recipe-based model/hardware/task configuration, pipeline regression tests |
| Main risk of overclaiming | Treating benchmark participation as universal performance or peer-reviewed scientific proof | Treating operational regression results as controlled cross-system scientific comparisons |
| Proposed PA use | Research measurement and benchmark governance template | Engineering evaluation harness design reference |

## Decision and proposed next gate
- **MLPerf:** retain as established external methodological reference.
- **vLLM perf-eval:** retain as production tooling reference.
- **Both:** external evidence only; no PA independently reproduced results.
- Before a future protocol: record immutable source IDs, license review, hardware/model comparability, baseline selection, falsification criteria, negative controls, statistical plan and owner approval.
- Other three entries in the Stage 1 catalog remain unqualified and should not be silently promoted.

## Provenance and limitations
This is a documentation-only synthesis of publicly readable upstream documentation as of 2026-10-21. No upstream source checkout, full code audit, commit-hash verification, license audit, CI execution, GPU run, scientific replication or independent result verification was performed. Source content may change; a subsequent reviewer must pin revisions. No private repositories accessed.
