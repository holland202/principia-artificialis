# External ML research evidence catalog — candidate intake (2026-10-21)

**Status: PROPOSED / REFERENCE ONLY.** This catalog records publicly available external material for review. It is not a PA scientific execution, replication, protocol registration, endorsement, or verification of authors' reported results. No external code, datasets, or papers are imported.

## Intake principles
- Prefer established mathematical theory, peer-reviewed primary publications, production-grade tools, independent replications and transparent negative results.
- Record exact source and version/date, claimed result, available artifacts, limitations, licensing and a falsifiable PA follow-up.
- Keep *external claim*, *externally reported test*, *PA independently reproduced*, and *PA registered/frozen* distinct.
- Check primary-source identity, publication status, artifact hashes, baseline parity, environment, statistical uncertainty, hardware and model configurations before promoting evidence.
- Public visibility does not establish redistribution rights.

## Candidate sources (not yet independently qualified)

| Candidate | Source | Evidence type | Potential PA use | Intake caveat |
|---|---|---|---|---|
| MLCommons MLPerf Inference v6.1 | https://mlcommons.org/2026/09/mlperf-inference-v6-1-results/ | Industry benchmark release | Reproducibility criteria, benchmark controls and workload definitions | Inspect official rules, submission artifacts, hardware comparability and permitted reuse |
| vLLM performance evaluation | https://github.com/vllm-project/perf-eval | Production-oriented open tooling | Continuous regression, accuracy and throughput baselines | Pin commit, inspect CI coverage, license and environment; do not infer scientific validation |
| IEEE inference efficiency study | https://doi.org/10.1109/TCC.2026.3674888 | Reported peer-reviewed study | Statistical design and efficiency comparison | Verify bibliographic metadata, peer-review status, dataset and analysis code before relying on quantitative claims |
| Winder.AI LLM inference benchmark | https://github.com/winderai/llm-inference-benchmark | Public benchmark repository | Cross-runtime replication protocol | Verify commits, scripts, raw logs, hardware/quantization parity, sampling and license |
| MLPerf Inference methodology | https://arxiv.org/abs/1911.02549 | Foundational preprint / methodology | Benchmark design, measurement definitions | Check final publication and current MLPerf rules; historical framework is not a current benchmark result |

## Proposed review gates
1. **Identity:** Resolve authoritative publication, author, publication date, version/commit and stable URLs.
2. **Rights:** Review paper, code, model and dataset licenses independently; link rather than copy unless licensed.
3. **Evidence:** Inspect methods, data availability, code, baselines, environment, negative controls, uncertainty and limitations.
4. **Fit:** Identify a concrete PA research question and possible falsification or independent reproduction.
5. **Decision:** Classify as reference / candidate for protocol design / qualified external evidence / independently reproduced. Only documented independent work may receive the last classification.

## Open questions
- Are the cited versions and publication metadata accurate and current?
- Which artifacts can be independently obtained and hashed?
- Which claims are appropriately controlled and statistically supported?
- Do existing PA records already cover any of these candidates?
- Which candidate warrants a separately approved, frozen protocol?

**No tests authorized or executed by this catalog. No changes to existing PA research status.**
