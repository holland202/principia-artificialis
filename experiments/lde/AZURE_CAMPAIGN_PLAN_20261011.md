# Azure parallel research campaign — planned, NOT DEPLOYED (2026-10-11)

**Status:** campaign staged for review; no additional resources created. **No scientific claims upgraded.**

## Recovery blocker
- Original `lde-test-02` VM accessed; 15 historical LDE files copied from VM to S25.
- Original-to-staged release comparison: **14 MATCH, 1 MISMATCH, 0 ABSENT**. The differing `03_substrates/s25/environment.txt` must be preserved on both sides and investigated, not silently replaced.
- Azure checkout has untracked `evidence/05_exploratory/` and `experiments/exploratory/`; inventory and secure-copy them before deallocating VM or launching new work.
- Source hashes, preregistered command sequence, and scientific result still need independent review.

## Five independent prospective studies
1. **LDE scaling:** 10k–100k seeds, independent RNG, argmax/argmin/random policies, selection regret and generalization.
2. **Sovereign Veritas:** stale/forged evidence, TOCTOU, replay, interruption, malformed signatures; false ALLOW, DEFER, REFUSE outcomes and mutation-detection rate.
3. **Distributed verifier:** Byzantine witnesses, network partitions, duplicate deliveries, rollback; separate safety/liveness measures.
4. **Compact-model discovery:** hidden rule discovery with local quantized models, oracle-contamination checks and scripted baselines.
5. **GPU pilot:** optional and separately priced/approved short experiment; no GPU quota/availability implied.

Each program needs an immutable preregistration (question, one primary metric, baseline, random-seed protocol, anti-vacuity, threshold, failure criteria, runtime budget), frozen source hashes, environment, explicit process exit, UTC timestamps, complete logs, output manifests, and negative findings. Exploratory data cannot be retroactively reclassified as confirmatory.

## Cost and orchestration gates
- Historical $200 initial Azure credit is **not** the current available balance. Verify credit remaining, credit expiration, resource quotas, region SKU pricing and storage/network charges in the subscription before requesting spend.
- A Cost Management budget/alert is not a hard spending cap. Implement and test a separate automated deallocation mechanism before concurrent provisioning; storage continues to cost after deallocation.
- Use one job per isolated worker/output directory; CPU jobs should be staggered or run on separate appropriately sized VMs to avoid burst-credit interference. GPU only after quota approval and cost gate.
- Preserve original VM for forensic recovery only; do not contaminate old evidence with new workloads.
- End-of-wave steps: hash, secure copy, independently compare, update evidence index with pinned remote commits, then deallocate workers.

## Suggested pacing (not approved expenditure)
Days 1–2: recover and audit originals; verify Azure subscription/credit/quota; freeze protocols.
Days 3–5: CPU pilot for each study, baseline and mutation smoke tests.
Days 6–18: parallel staged batches within confirmed budget, automatic stop if results invalid or costs exceed approved caps.
Days 19–22: GPU pilot only if authorized and available; otherwise extend adversarial tests.
Days 23–25: cross-machine verification, archive, publication, shutdown.

**Audit note:** File-level evidence is presently more important than consuming expiring credit. No cloud resources or scheduled tasks are created by this plan.
