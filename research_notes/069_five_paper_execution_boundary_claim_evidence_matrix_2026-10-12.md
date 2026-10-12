# Research note 069 — Five-paper execution-boundary claim/evidence comparison

**Date:** 2026-10-12  
**Status:** READ-ONLY COMPARATIVE RESEARCH; NO NEW EXPERIMENT; NOT INDEPENDENT SECURITY VALIDATION  
**Research direction:** Chad Holland  
**Prior note:** [068 — Undermind evidence-bound literature intake](068_undermind_evidence_bound_agent_literature_intake_2026-10-12.md)  
**Undermind workspace/search:** https://app.undermind.ai/projects/7f21744a-49d7-4ede-901b-96a2ec393ea2?path=/Evidence%20Bound%20AI%20Agent%20Actions%20and%20Independent%20Verification  
**Sovereign Veritas code/document snapshot:** `holland202/sovereign-veritas` `main` at `439b7351f162b378cb02ed4bfa44f171e73452b6` (read-only GitHub connector retrieval, 2026-10-12). This is an inspection pin, **not** a build, test run, or claim of HEAD immutability.

## Method and evidence levels

Undermind's `read_pdfs` agents analyzed the full text of five candidate papers. The analyst compared that text-derived extraction against a direct GitHub retrieval of Sovereign Veritas source code, tests, and existing experimental reports at the pinned revision. Paper metrics below are **author-reported and extracted by an AI paper-reading tool**, not independently recomputed from paper datasets or verified with reproduction. Code inspection corroborates the existence of mechanisms; report inspection corroborates **reported** runs and limitations, not independent execution.

Evidence vocabulary:
- **CODE-OBSERVED:** directly read implementation at the pinned GitHub revision; runtime behavior not thereby proved.
- **SELF-TEST REPORTED:** repository reports bounded outcomes; this review did not rerun the commands.
- **GAP / NOT ESTABLISHED:** the cited artifacts do not establish the property; not necessarily a proof that no alternative system can achieve it.
- **LITERATURE-REPORTED:** source-paper claim, not an SV result.

This is a scoped comparison, **not** an exhaustive audit of all executors, provider adapters, credentials, or egress routes.

## Literature reviewed (full-text AI extraction; metadata links)

| Key | Paper | Selected reported measurement and limitation |
|---|---|---|
| `Ton26` | Tong et al., *AID-Guard: Stateful Authorization for Delegated Agent Effects* (2026), https://arxiv.org/abs/2608.21159 | 13 official-MCP mutations rejected or post-effect verification failed; seven independent HTTP/JSONL effect-count scenarios reported. All protected effects must pass a complete declared D0 route inventory; its prototype does not discover omitted routes. Controlled provider contracts and finite test schedules bound at-most-once claims (Sections II, III, IV, VI). |
| `San26b` | Santos-Grueiro, *Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents* (2026), https://doi.org/10.48550/arXiv.2607.10487 | In a 270-run deliberately invalidated synthetic matrix, 262 reached their endpoints but only 55 were authorized completions; 207 unauthorized commits reported. Boundary guard experiments were narrower; protected atomic commit surfaces and trustworthy visible invalidators are assumptions (Sections 4–7). |
| `Kha26b` | Khan, *Stop Means Stop: Measuring and Repairing the Enforcement Gap in Agent-Framework Control Primitives* (2026), https://doi.org/10.48550/arXiv.2607.14166 | Reported 215/1,200 unmediated live-model FW-A effect leaks versus 0/1,200 when effects were routed through the gate; local HTTP demonstration landed a POST before rejection. These are bounded framework tests; complete mediation, including non-network effects, remains a deployment condition (Sections 3–5). |
| `Cal26` | Calboreanu, *TRACE: Runtime Governance, Containment, and Evidence for Autonomous AI Agent Operations* (2026), https://doi.org/10.1109/ACCESS.2026.3733578 | Deposited primary detection and side-effect instruments were invalid, so original detection hypothesis had no valid measurement. Corrected observer reported 0 prohibited effects among 3,703 exercised replicates, but 197 missing runs meant **no confirmatory rejection** under the registered threshold (Section IV-C, Table 8). |
| `Xu26` | Xu et al., *Beyond Single-Use Tokens: Durable Authorization State for Replay-Resistant LLM Agent Actions* (2026), https://arxiv.org/abs/2608.01710 | Reported 12,000 kill/restart schedules without replay failures using an idempotent sink, under durable linearizable non-rollback state assumptions. Its negative control duplicates effects when sink idempotency is absent; new issuance for equivalent intent defeats token-ID-only replay checks (Sections 3–7). |

**No paper's experiments, artifacts, or numerical claims were independently reproduced here.** Full-text agent summaries may misread equations/tables; verify directly from PDFs and archives before citing precise values in external scientific claims.

## Pinned Sovereign Veritas observations

1. **Decision semantics — CODE-OBSERVED / SELF-TEST REPORTED.** `sovereign_veritas/decision.py` blob `e646691b3bf976ee45fa4bcdd9f54b5faa72ca05` implements deterministic ALLOW/DEFER/REFUSE, including evidence, capability and runtime guards. `CONTRACT.md` blob `451c3c70420cede8ba70e2837fd29ec8bfb468fd` defines 4,690 conformance vectors and digest `44823d0ff707213ae8bc310ed8b21e135f8e742fd8834e8f9474743d3a250628`. Same-author conforming implementations and tests are not independent validation.
2. **Mutable parameter TOCTOU — CODE-OBSERVED / SELF-TEST REPORTED (bounded correction).** `sovereign_veritas/workflow.py` blob `c901885c0798a03bd0a432f5ee72588edc98c168` evaluates evidence holding a copied action and constructs the executed `ActionProposal` from the decision evidence, not the caller's mutable action. `docs/SV_ATTACK_001_RESULTS.md` documents the original Q1/Q3 failures; `docs/SV_FIX_001_RESULTS.md` blob `d5f5745eb28263492efd42ccbcbb9053403547fd` reports F1 and F2 PASS in one Linux x86-64 container run, self-tested, not S25. `tools/verify_package.py` blob `78096f4848be226b88f038c54ae5fb6e53fb9e58` includes vehicle-command comparison for supported backends. This does not establish executor honesty or global effect-route coverage.
3. **Sequential and same-key duplicate suppression — CODE-OBSERVED / SELF-TEST REPORTED; conditional.** `tests/test_execution_boundary.py` blob `5b104238fc5d0720d159a833c1545889eba3f167` records sequential duplicate refusal, but explicitly preserves a sink without `has_record` for which a duplicate causes **2 effects**. `tests/test_idempotency.py` blob `aa977253933cd6b0155cd923f5e06c4eb6586d63` documents same-key refusal, file reservation exclusivity, and that **fresh key per retry yields 2 effects**. `docs/RK2_RESULTS.md` reports 12/12 registered checks with fixed intent keys, but expired/unknown key recovery costs liveness, and same-key protection does not ensure atomic effect+ledger recording.
4. **Effect truth versus workflow claims — GAP, SELF-TEST NEGATIVE.** `docs/EO1_RESULTS.md` blob `8c89722a3f08f1460236cf06a6a4a0373e5d9121` reports that `execution_status=SUCCEEDED` only records that the executor returned. A no-op or wrong-action executor can be reported as succeeded, and a mutated guard can perform an effect despite the package verifying `CONSISTENT` as no execution recorded. EO-1 was a simulated, self-tested container probe, not a real-world effect audit.
5. **Crash/record failure and concurrent execution — GAP in general workflow.** `docs/EXECUTION_BOUNDARY_RESULTS.md` blob `80c5d7745c5e307248b779210a2a25886aa1859c` preserves X4 concurrent same-ID race and X5 effect-before-record failure. Opt-in key reservations mitigate specific duplicate schedules under stable-key assumptions but do **not** make reservation, provider effect and evidence append a single transaction. The no-key path remains weaker.
6. **Release posture — EXPLICIT NON-CLAIM.** `STATUS.md` blob `4b86032ad9de615649b00e9beb0a831ae6df4938` and `docs/RELEASE_NOTES_v0.2.0.md` blob `a55ac8016b529c69f8295f05403b21400d60a07d` mark v0.2.0 maintenance-only, **NOT PRODUCTION-READY** and **NOT INDEPENDENTLY SECURITY-VALIDATED**. Signature authenticates bytes, not truth, provenance of declarations, or freshness. Cross-platform conformance is not hardware-integrated safety verification.

## Claim-to-evidence matrix

| Claim / question | Current bounded classification | Reason and discriminating evidence still needed |
|---|---|---|
| Models cannot themselves authorize capabilities; Gate has reproducible semantics | CODE-OBSERVED + SELF-TEST REPORTED, component only | Conformance vectors demonstrate selected contract behavior, not complete authorization policy or real principal identity. |
| Decision-bound command parameters cannot be altered by changing caller's original dict | CODE-OBSERVED + SELF-TEST REPORTED for targeted F1/F2 | Check an independent implementation/reproduction and other mutable/shared state and effect adapters. |
| Reject/refuse guarantees **no** external effect | **NOT ESTABLISHED** system-wide | Require complete mediation/path inventory, independently measured real effects and sabotage controls; EO-1 is a negative evidence-surface finding. |
| Every admitted external effect remains authorized at commit | **NOT ESTABLISHED** system-wide | Independent commit-time freshness/eligibility verification and atomic coupling to the provider; check stale and cancelled authority, provider preconditions and TOCTOU. |
| A replay or retry cannot repeat a committed external effect | SELF-TEST REPORTED for sequential and fixed-key cases; **NOT ESTABLISHED** generally | Intent-bound keys, atomic durable reservations, unknown-response reconciliation, concurrent/crash schedules, sink idempotency and controlled recovery. |
| A signed/consistent package proves what happened in the outside world | **REFUTED as a general inference by EO-1's simulated counterexamples** | Independent effect recorder with positive/negative controls and identity/freshness binding; signatures certify recorded bytes, not event truth. |
| Full platform has third-party certification or production safety | **NOT ESTABLISHED**; explicitly disclaimed | Independent red team, effect-path audit, actual substrate testing, external sink observation, deployment threat model. |

## Documentation inconsistency — DO NOT silently rewrite history

GitHub reported PR [#71](https://github.com/holland202/sovereign-veritas/pull/71) as **merged** 2026-10-10T11:23:52Z, merge commit `fff4f68f5a775212de344af6afc9d1f099e71457`, titled “SV-FIX-001: register fixes for SV-ATTACK-001 Q1 and Q3 (no code).” Pinned `main` has F1/F2 code. Yet `STATUS.md` still describes Q1/Q3 candidates as “not yet merged.” The status documentation is stale/internally inconsistent on disposition; retain the original failing evidence and verify exact fix integration separately before any status change. The PR title indicates a registration merge, **not** that #71 itself introduced F1/F2 executable code.

## Proposed next research actions — NOT AUTHORIZED OR EXECUTED HERE

1. Independently verify five source PDFs and deposited datasets/code against the extracted numerical and scope claims.
2. Construct a closed-world effect-route inventory (network, local files, IPC, direct credentials, adapters and tools) and demonstrate instrumentation sensitivity to deliberately induced external effects.
3. Preregister, freeze and run a bounded comparative matrix for authorization freshness and action-target binding at actual provider commit, including approved first uses.
4. Evaluate durable semantic identity and restart/retry/failure recovery with a provider-side idempotency contract; preserve ambiguous-response UNKNOWN states.
5. Audit independent effect receipts, observer provenance, failure and missing-evidence policy; never score missing observation as “no effect.”
6. Reconcile stale `STATUS.md` and PR #71 only through a separately reviewed, additive status correction consistent with the maintenance-only posture.

**Governance:** This note does not alter code, acceptance criteria, frozen registrations, prior test results, original negative findings, or project readiness status. No experiments were executed. AI source analysis is not independent validation.
