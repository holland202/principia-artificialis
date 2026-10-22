# Research note 068 — Evidence-bound AI agent literature intake

**Date:** 2026-10-12 (UTC date)  
**Status:** EXPLORATORY LITERATURE INTAKE; NO FULL-TEXT VALIDATION OR EXPERIMENTAL CONFIRMATION  
**Source:** Undermind deep search, `Evidence Bound AI Agent Actions and Independent Verification`, completed 2026-10-12 (service reported 13:02 UTC).  
**Workspace/search:** https://app.undermind.ai/projects/7f21744a-49d7-4ede-901b-96a2ec393ea2?path=/Evidence%20Bound%20AI%20Agent%20Actions%20and%20Independent%20Verification  
**Method:** Connected Undermind `inspect_deep_searches` result (summary and first 15 of 221 ranked relevant papers) and `get_paper_info` metadata for five selected papers. Findings below are *attributed to the literature-search tool's abstract/metadata synthesis*, not independently checked against full text. An available PDF does **not** mean its contents were read. This is not a systematic review or preregistered experiment.

## Intake observations

- Undermind reported the search **completed**, with **221 ranked relevant papers**. The first 15 displayed papers showed PDFs available. This count is a service result, not an independent database census; relevance ranking is not a quality grade.
- The synthesized research themes were: (1) separating agent proposals from effect-boundary authorization; (2) checking authority freshness, durable lifecycle state and replay resistance across restarts; (3) observing actual effects independently rather than equating alerts with prevention; (4) recognizing that signatures/hash chains support record integrity, not event truth or complete capture; and (5) limiting reproducibility/mutation-test conclusions to the declared instrument and tested scope.
- **No result from this search establishes that sovereign-veritas, SKN-V1, LDE, or another local system satisfies any of these claims.** Similarity of architecture is not implementation validation.

## Selected references for follow-up (metadata only)

| Undermind cite key | Publication | DOI or source | Proposed comparison axis |
|---|---|---|---|
| `Ton26` | *AID-Guard: Stateful Authorization for Delegated Agent Effects* (2026), Yingzhe Tong, Le-Yu Dai, Song-Hui Guo | https://arxiv.org/abs/2608.21159 (no DOI returned) | Statefulness, repeated effects, retry and crash contracts |
| `San26b` | *Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents* (2026), Igor Santos-Grueiro | https://doi.org/10.48550/arXiv.2607.10487 | Authorization freshness at effect commit |
| `Kha26b` | *Stop Means Stop: Measuring and Repairing the Enforcement Gap in Agent-Framework Control Primitives* (2026), Sajjad Khan | https://doi.org/10.48550/arXiv.2607.14166 | Stop/deny enforcement versus merely detecting attempts |
| `Cal26` | *TRACE: Runtime Governance, Containment, and Evidence for Autonomous AI Agent Operations* (2026), Elias Calboreanu | https://doi.org/10.1109/ACCESS.2026.3733578 | Instrument validity, containment, evidence limitations |
| `Xu26` | *Beyond Single-Use Tokens: Durable Authorization State for Replay-Resistant LLM Agent Actions* (2026), Jingheng Xu et al. | https://arxiv.org/abs/2608.01710 (no DOI returned) | Durable replay-state and restart tests |

Metadata, citation counts, apparent publication venues, and conclusions require bibliographic/full-text verification before external reliance. Papers are **reading candidates**, not endorsements. None were independently reproduced.

## Candidate claim-to-evidence checks (PROPOSED ONLY)

1. **Execution mediation:** Inventory every external effect route, including bypasses/direct credentials. Test fail-closed authorization at the actual effect boundary using independently collected side-effect telemetry.
2. **Freshness and replay:** Distinguish signature authenticity, authorization expiry, nonce/history persistence, duplicate external effects, and success for genuinely fresh authorized requests. Specify restart, missing/corrupt/rolled-back state, crash windows and concurrent retries.
3. **Detection versus prevention:** Separate timestamps for trigger, alert, policy decision, tool dispatch and external effect. An alert alone does not demonstrate a blocked effect.
4. **Instrument validity:** Include sabotage/mutation and negative controls that show the measurement can detect a real effect or violation. Equal hashes or a passing exit code cannot establish the truth of the underlying scientific claim.
5. **Provenance:** Pin GitHub commit and blob SHAs, dataset revisions, artifact SHA-256s, platform/runtime, commands, exit codes, and independent read-back of claimed outputs.

These checks are *design suggestions*, not approved changes to any frozen contract, preregistration, rubric, or acceptance criterion.

## Explicit limitations and next actions

- **Verified now:** Undermind search status and service-reported metadata and synthesis were retrieved through its authenticated connector; the PA repository was inspected separately through GitHub. 
- **Not verified:** Full-text methods or quantitative results, peer-review status across all papers, inclusion/exclusion completeness, independent replay of experiments, or application to Sovereign Veritas's code paths.
- **Not performed:** New experiments, scoring, grading, model benchmarking, execution-boundary audit, or code changes.
- **Follow-up:** Read the five PDFs, transcribe their actual measured outcomes and limitations with pinpoint citations, and independently reconcile each candidate claim to pinned repository artifacts before updating any component-level or integrated-platform validation status.

**Governance:** Additive external-literature research intake only. Preserve previous negative findings and source freezes. AI-generated synthesis is not independent validation. No assertion of deployment-level safety is authorized by this record.
