# PA-AGCR-001 — Scion/Antique evidence intake and build translation

**Date:** 2026-10-13  
**Status:** READ-ONLY SOURCE SYNTHESIS / CANDIDATE ENGINEERING DESIGN — NOT IMPLEMENTED, NOT VALIDATED  
**Parent registration:** [PA-AGCR-001_PREREG.md](PA-AGCR-001_PREREG.md), first committed separately at `34b52dd085b35635499b93368be59d95c12e5260`.  
**External source record:** [anthropic_scion_2026-10-13_excerpt.md](external/anthropic_scion_2026-10-13_excerpt.md).  
**Internal code references read:** [Sovereign Veritas README](https://github.com/holland202/sovereign-veritas/blob/main/README.md), [STATUS](https://github.com/holland202/sovereign-veritas/blob/main/STATUS.md), [Gate contract](https://github.com/holland202/sovereign-veritas/blob/main/CONTRACT.md), [Gate decision source](https://github.com/holland202/sovereign-veritas/blob/main/sovereign_veritas/decision.py). These were **inspected** on 2026-10-13, not executed. Prior-to-run source revision pinning remains required.  
**Attribution:** Research direction: Chad Holland. Source author: Nick G. and Anthropic source-control team. Analysis/draft: ChatGPT (OpenAI, GPT-6). Human review: direction only; human responsibility remains Chad Holland. No affiliation with or endorsement by Anthropic.

## What the public source actually supports

All quantities below are **reported by Anthropic in its engineering article**, not results from PA scripts or independently audited performance measurements. They are workload context, **not performance targets for PA**.

| Publicly described feature / figure | Support level | Interpretation for PA |
|---|---|---|
| May 2026 ~2,500 merges/day; September >30,000/day | Anthropic-reported organizational workload | Human attention and authorization surface can become more constrained than code generation. We do not extrapolate a PA merge rate. |
| ~25 million CI checkouts/day; main history ~100 GB; compressed working copy >25 GB | Anthropic-reported scale | Repeated wholesale checkout is costly at extreme monorepo scale; not evidence Git is unsuitable for PA. |
| Scion's server-based changesets use parent-relative changed files, content-addressed data and a write-ahead log; derived ancestry/path indexes | Architecture described in primary source | Keep an immutable, digest-bound change identity; permit derived query data but never let an index certify authority. |
| Content-addressed server/cache tiers with reported >99% cache hit rates; regional caches and failure-domain boundaries | Architecture + Anthropic-reported internal measurement | A digest-checked, offline-capable local cache may improve lookup while keeping integrity separate from availability. |
| Reported 200x smaller infrastructure CPU/memory footprint, roughly two orders faster checkouts, and ~25% CI CPU capacity gain | Vendor-reported comparison under vendor workload | Do **not** cite as evidence for local adapter speed or claim equivalent benefits. |
| Scion prefers always-online clients, sparse/virtualized checkouts, server-hosted commits and few mutable refs | Architecture described in primary source | **Contrasts** with PA's desired sovereignty/offline operation; borrow ideas, not an online dependency. |
| Directory-level access control and complex semantic review/approval constraints via broader source-control and review tooling | High-level Anthropic description; no published security proof | Motivates a separate, deterministic policy boundary that does not trust an agent's "safe" summary. |
| Human reviewers increasingly focus on intent; adversarial AI review can over-engineer hypothetical problems | Anthropic-reported working practices | Prioritize human review of consequence, but require independent check of actual changed objects; do not equate intent approval with execution authority. |
| Post-merge/pre-deployment testing adopted in response to difficult serialized merge-queue scaling | High-level Anthropic description | Detection after landing is not a substitute for authorization at landing. Risk-sensitive revalidation is a distinct problem. |
| Specialized monitoring agents ("superfans") inspect telemetry; conventional alerts remain | Anthropic-described practice | Use advisory anomaly observers, independent of the gate's ability to authorize or create effects. |
| Seven engineers built Scion, Antique and related systems over five months | Anthropic-reported history | Illustration of AI-assisted development; not evidence that equivalent PA scope is feasible. |

**What cannot be inferred:** No public implementation of Antique's semantic rule evaluator, complete review UI, reviewer credential model, race control, adversarial bypass coverage, or guarantee that it prevents unauthorized merges is established by this article. The LinkedIn speculation about Claude `/review` and `/security-review` is opinion, not an Anthropic admission.

**References:** Anthropic, Nick G. and source-control team, [*Redesigning source control at Anthropic*](https://www.anthropic.com/engineering/redesigning-source-control), published 2026-10-13. Public-source capture limitations: [external record](external/anthropic_scion_2026-10-13_excerpt.md).

## Translation into our architecture: adopt, adapt, reject

| Source concept | Candidate component in PA experimental adapter | What must remain untrusted | Decision |
|---|---|---|---|
| Immutable changeset and content-addressed blobs | `ChangeIdentity`: repository, base revision, target head, candidate tree, actual diff digest; re-derive from Git object database | Agent-provided diff hash or prose | **ADAPT** for binding; verify recomputation |
| Server commit / compare-and-swap on mutable refs | `LandingController`: final compare current target SHA; require atomic protected ref effect or durable single-use reservation | Preflight ALLOW, non-atomic log-before/after heuristics | **ADAPT**; race proof pending |
| Semantic approval constraints | `ReviewPolicy` + `ApprovalAttestation`: authorized principal, sensitive paths, specific candidate, explicit policy version, expiry/nonce | AI risk labels, role strings written by the agent | **ADAPT**, conservative fail-closed |
| Sparse/virtualized working copy | `ObjectResolver`: lazy reads of exact Git objects with digest checks and complete protected-scope coverage | Missing sparse objects, unverified filesystem view | **CONDITIONAL**; unresolved objects mean DEFER |
| Derived ancestry/path-history indices | Read-only `ChangeContextIndex` for reviewer triage | Index freshness and assumptions about invisible history | **OPTIONAL**; never authority |
| Regional caches | Local-first immutable object cache, digest re-checks, bounded eviction | Cache freshness as a proxy for authorization | **ADAPT** only if useful; no always-online server |
| Human intent-oriented review | Human-facing `ConsequenceReview`: show actual sensitive-object delta, identity, signer, decision reasons, side-effect reachability | Summary-only review and model self-certification | **ADAPT**; review UX not a proof |
| Component "superfan" telemetry | Read-only `BoundaryObserver`: independent effect counts, unexpected ref moves, unreconciled decisions | Model-produced telemetry interpretation | **OPTIONAL**; observer cannot ALLOW |
| Post-merge and pre-deploy test gates | Separate detection/recovery stages, visibly not equivalent to pre-effect authorization | Claims that later CI negates an unauthorized commit effect | **ADAPT with explicit limitation** |
| Entire Scion/Antique system and server dependency | Replacement for Git or cloud-backed central authority | Vendor-specific workload assumptions | **REJECT for this phase** |

## Candidate minimal data / control contract (not implemented)

```text
UNTRUSTED AI PROPOSAL
  |
  v
Git-object reader -> candidate tree + actual changed-path digest
  |
  v
Protected-path/risk rule (trusted policy; fail-closed if coverage unknown)
  |
  v
Reviewer authority + approval attestation verification
  |
  v
Evidence-binding check (repo, target, head, tree, diff, policy, nonce)
  |
  v
Integration boundary: recheck head + single-use authorization
  |            |             |
  ALLOW        DEFER         REFUSE
  |
  v
Atomic protected ref write / observed synthetic effect
  |
  v
Append-only evidence record and *separate* effect observer
```

A valid record needs **two different claims**: (a) the decision matched the stated policy, and (b) an effect occurred or did not occur at the protected sink. A ledger row is not proof of (b). A valid signature may authenticate a signer but not a human's informed approval; signer authorization is a separate policy lookup. A valid hash may show byte equality but cannot establish the truthfulness of a source.

### Proposed typed objects

```text
ChangeIdentity:
  repo_id, target_ref, target_head_sha, base_commit_sha,
  candidate_tree_sha, changed_paths_digest, actual_diff_digest

ApprovalAttestation:
  approver_principal, credential_id, approval_nonce,
  approved_change_identity_digest, policy_digest, issued_at,
  expiry, signature, declared_review_scope

LandingAttempt:
  change_identity_digest, attestation_digest, current_head_sha,
  nonce_state, decision, reasons, observed_sink_effect_id
```

No wire format, serialization, expiry tolerance, identity-to-role mapping, nonce store semantics, or signature algorithm has been frozen. A correct implementation must not infer any of them from this outline. The integration protocol itself needs separate versioning and review, and it must defend against renames, file-mode changes, symlinks, submodules, delete/add equivalence, and policy-path bypasses if those features are in scope.

## What we already have, and what we do not

**Existing evidence (read-only inspection, not fresh run):**
- Sovereign Veritas has an experimental `ALLOW / DEFER / REFUSE` Gate, evidence-package mechanisms, and independent decision *replay* code. Its published `sv.gate/0` contract is tightly bounded. The release is **maintenance-only; not production-ready; not independently security-validated**.
- Historical limitations are explicit: consistent but untruthful evidence can verify; effects can diverge from logs; replay and concurrency need real effect-boundary checks; an approval of a mutable proposal may not bind the eventual effect. Some later candidate fixes have their own bounded results; their presence does not establish general integration safety.
- PA already has SWAY registration, anti-vacuity requirements, add-only correction rules, and source provenance rules. These can govern a new *experimental* adapter without altering the frozen SV kernel.

**Missing (must not imply it exists):**
1. A git-aware adapter that can evaluate actual protected changed objects.
2. Independently grounded reviewer identity and signature/credential verification at the authorization boundary.
3. A commit-time linearization strategy for nonce and ref effects; evidence of complete mediation.
4. A real independent effect observer (not a gate-generated success label).
5. Reproducible adversarial fixtures covering malformed, missing, stale, replayed, same-source, and conflicting evidence.
6. A verified local/offline fallback that fails closed when independent trust anchors are unavailable.

**Architectural separation:** Research and protocols go in PA. An adapter, if later authorized, should live in PA's experimental area or a separately approved experimental repo; **do not add features to maintenance-only Sovereign Veritas**. Private commercial projects are out of scope. No automatic cross-repository transfers are authorized. No remote systems, user accounts, or production branches are integration targets in PA-AGCR-001.

## Build sequence — proposed, not authorized execution

**Stage 0 — completed as documentation only:** preregistration at a frozen commit, source provenance record, and this architecture intake. No experiment has run.

**Stage 1 — next owner decision:** review P1–P9, choose trusted policy/approval fixtures and deterministic concurrent-effect model. Resolve the precise semantics of insufficient vs malicious approval and identity attestations. Freeze test cases and digest/canonicalization before implementation.

**Stage 2 — future isolated prototype:** instrument a throwaway local Git repo and synthetic commit sink; implement narrow adapter importing current real code where applicable; emit raw decision/effect observations and a planted mutant that proves the guard can fail. No GitHub merge API and no cloud executor.

**Stage 3 — independently inspected confirmation:** compare exact outputs against the precommitted cases; preserve failed and unreachable cases; test mutation bypasses; run cold clone and offline path; arrange outside evaluation. Follow [METHOD.md](../METHOD.md), not this document, for promotion thresholds.

**Stage 4 — optional exploratory extensions:** measure latency/scale at chosen workloads only after separate preregistration; study semantic false negatives with independently labeled diffs; investigate policy changes while queues are in flight; test compromised reviewer keys, rollback of nonce state, incomplete Git trees, branch force pushes, network partitions and cache poisoning.

**No production deployment, funding claim, commercial-product feature, or Anthropic equivalence is implied.** This intake is reusable engineering direction whose claims remain open until tested.

## External claims and novelty boundary

The transferable principles (content addressing, CAS, capability checks, identity-bound approval, semantic triage, independent observation) are established engineering ideas. The novelty question is **not** whether PA invented these ideas; it is whether the proposed assembled boundary actually holds its declared invariants against named counterexamples in a small reproducible experiment. Cite prior art and publish negative findings.

**Open door:** If P1–P9 hold in a synthetic sink, can the same invariant be demonstrated against an independently instrumented real Git hook/merge endpoint *without* bypass paths? This remains **NOT RUN**, requiring new preregistration and explicit authorization.
