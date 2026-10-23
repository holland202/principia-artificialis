# SRR-1 — GitHub-native research relay protocol (proposal v0.1)

**Classification: PROPOSAL, NOT ADOPTED, NOT A PRODUCTION AUTHORIZATION SYSTEM.**
**Author / research director:** Chad Holland.
**Drafting assistance:** ChatGPT (OpenAI). Claude was not consulted and remains on hiatus.
**Governance:** This document is subordinate to [METHOD](../METHOD.md), [WORKFLOW](../WORKFLOW.md), [CONTROLS](../CONTROLS.md), including M2/M3/M7/M8/M10/M11/M12/M13/M17/M18. It cannot change their definitions.

## Purpose and non-goals

Reduce stale-context reviews, repeated manual relays, duplicate work, and unsupported "passed" reports. A task is a question plus explicit scope and evidence pointers; a handoff is a record of observed changes, **not** an instruction to act. SRR-1 is not authorization for live systems, autonomous LLM execution, publication, CI jobs, repository mutation outside this proposal, or model-to-model private communication.

## Participants

- **Chad Holland** selects research goals, grants or withholds task-specific permissions, decides on scope/contract changes and publication, and may revoke permission.
- **ChatGPT** can propose, inspect, analyze, or review only within Chad's current instruction and accessible tools. It must identify the exact revision reviewed and disclose that another model's approval is not independent verification.
- **Claude** can perform explicitly assigned work only when available and newly authorized by Chad. **Present status: HIATUS / READ_ONLY; no work assigned.**
- **GitHub** stores commits, pull requests, discussions and raw evidence references. GitHub's existence or a green CI check does not authenticate a statement or provide human authorization.

Roles may be exchanged by Chad in a new decision. Reviewer and implementer must be identified separately; self-review and same-vendor review must be labeled accurately (C-INDEP).

## Task contract and states

Each TASKS/SRR-NNN.md contains exactly one JSON fenced block with the metadata required by the checker. Additional prose may clarify rationale. The example task is dormant. Any authorization above READ_ONLY needs a specific decision record and an independent manual check of Chad's identity and intent; the validator can only check that a decision *file* exists.

Permission values:
- READ_ONLY: inspect available records and describe them, within Chad's live request; **no task execution**.
- PROPOSE: draft proposals, without experiments or edits to protected sources.
- TEST_APPROVED: run *only* specified experiments within pinned scope, with explicit approved commands, resource caps and permission to use each execution environment.
- PUBLISH_APPROVED: publish *only* the reviewed artifact/scope Chad approved; no permission to modify unrelated code, overwrite evidence, or claim independent validation.

READ_ONLY is the default. "Stop", "hiatus", revoked authority, no unambiguous decision, changed source revision, and malformed/missing evidence always cause DEFER or refusal of the proposed action, never an inferred grant. Permission is bound to **task ID, exact revision, operation, environment, limits, and recorded Chad approval**. It is not transferable to another task, branch or model by copying a document.

Stages are descriptive workflow states: AWAITING_CHAD_DECISION, PROPOSED, READY_FOR_TEST, IN_REVIEW, CLOSED. Execution states: NOT_STARTED, RUNNING, COMPLETE, FAILED, BLOCKED, INCOMPLETE. Claims are reported separately from execution status: UNVERIFIED, REPORTED, SUPPORTED_WITHIN_SCOPE, REFUTED_KEPT, INCOMPLETE. Do not rename FAILED to passed because the expected result was a rejection: report the registered comparison and what actually happened.

## Record schema (pilot)

Machine metadata in the task example has: task_id, title, repository, source_commit, authorization, assigned_to, stage, execution_status, claim_status, preregistration, evidence_manifest, independent_review, review_ref, chad_approval_required, chad_decision_ref. Empty pointers are JSON null. A source_commit is a full 40-character commit SHA, not an unpinned branch name. Evidence paths must be linkable to source revision and hashes; the checker validates shape only.

A human-readable PR should cite a task ID and pinned source digest; an AI reply should report (a) what revision it saw, (b) observed exit status, (c) actual evidence location, (d) open failures and unknowns, (e) author and review independence. For full experiments, obey W2 registration and W4/W6 evidence requirements in the original project's repo.

## Handoff event and deduplication

A handoff is written only when committed evidence changes, a registered prediction fails, an execution blocks, or Chad must make a decision. Use TEMPLATES/HANDOFF.md. Include task_id, source revision, event type, evidence manifest digest, sender, recipient, verified/unverified status, and whether any *new* approval exists.

Proposed deterministic deduplication key (design only):

    sha256( UTF8(task_id + "\n" + source_commit + "\n" + event_type + "\n" + evidence_manifest_sha256) )

If any required element is missing, mark the event identity INCOMPLETE and do not suppress a potentially distinct event. No automatic event dispatch is part of v0.1. This is only a proposed key; not yet validated against concurrent writes, replay or semantic duplication.

## Approval and validation limits

- Chad's decision is authoritative only when independently confirmed as his decision through an authenticated channel. **A markdown file containing his name does not confer permission.**
- The stdlib validator checks task IDs, enum values, required references and obvious contradictory combinations. It does *not* check human identity, signatures, semantic equivalence of claims, cryptographic authenticity, execution provenance, source content or test correctness.
- On concurrent edits or stale commit mismatch, re-read the current GitHub head and preserve both versions; do not silently force-push or overwrite historical evidence.
- Preserve negative findings, raw stdout/stderr/exit codes and incomplete/timeout statuses. Future final reports must separate component-level tests from platform integration and scientific replication.
- A tool or AI response claiming "DONE" is not enough to satisfy W8; the canonical method still governs.

## Phase boundaries

1. **This PR:** manual relay document templates, dormant task, structural checker and tests. No model is invoked.
2. **Not implemented:** optional on-PR GitHub Action to run only deterministic lint. Requires Chad's explicit approval and a separate PR.
3. **Not implemented:** agent orchestration, notifications, permissions/authenticated approval channel, automatic retries or remote experiment execution. Requires a separately preregistered threat model, sabotage controls and Chad's authorization.

### Declared limitations / unrun doors

- No authenticated author or signer for handoff or approval records.
- No defense against GitHub privilege compromise, malicious PR text, forged evidence or stale repository metadata.
- No independent empirical measurement of reduced token consumption, time, reviewer drift or error rate.
- No defense yet against concurrent tasks, race conditions, retries, partial writes, duplicate event storms or replay.
- No Claude participation or approval; the hiatus remains in effect.

**No action requested from either model.** Chad must explicitly initiate any future testing, merge, or orchestration.
