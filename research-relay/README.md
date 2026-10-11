# Sovereign Research Relay (SRR-1)

**Status: PROPOSED / PILOT / NOT ADOPTED / NOT VALIDATED.**
**Initiated by:** Chad Holland. Drafted with ChatGPT (OpenAI), 2026-10-11.
**Execution authority:** none. **Claude:** hiatus, READ_ONLY. No automatic model invocation or tool execution.

SRR-1 is a minimal GitHub-based handoff and evidence-indexing protocol for Chad, ChatGPT, and Claude. It is not a new AI runtime, a product, a verified security boundary, or a replacement for Sovereign Veritas's actual authorization gate.

The canonical estate method remains [METHOD.md](../METHOD.md), [WORKFLOW.md](../WORKFLOW.md), and [CONTROLS.md](../CONTROLS.md). SRR-1 is a proposed *coordination convention* under those documents. Any discrepancy is resolved in favor of the canonical method; this proposal does not amend M/W/C rules.

## Start here

- [PROTOCOL.md](PROTOCOL.md): roles, approval states, handoffs, event identities, and fail-closed rules.
- [STATUS.md](STATUS.md): declared relay status and task inventory.
- [TASKS/SRR-001.md](TASKS/SRR-001.md): dormant, READ_ONLY example; not an assignment.
- [TEMPLATES](TEMPLATES/TASK.md): forms for task, handoff, and Chad decision records.
- [HANDOFFS](HANDOFFS/README.md) and [DECISIONS](DECISIONS/README.md): currently no active handoff or approval.
- [scripts/validate_relay.py](scripts/validate_relay.py): stdlib structural checker; it does not authenticate identity or evidence.
- [tests/test_validate_relay.py](tests/test_validate_relay.py): deterministic positive and negative checker examples.

The checker reads the embedded JSON metadata in TASKS/*.md and verifies basic coherence. Run manually from the repository root:

    python3 -m unittest discover -s research-relay/tests -v
    python3 research-relay/scripts/validate_relay.py research-relay

No GitHub Action, notification routing, Claude invocation, or automated permission grant is installed by this proposal. Creating a GitHub PR is not permission to start a research task. **No work should begin on SRR-001 until Chad issues a new explicit decision.**

## Boundaries

GitHub is the shared record, not a trusted execution authority. A green validator means the metadata is syntactically coherent; it does not prove a decision came from Chad, evidence is authentic, tests succeeded, a repository revision is current, or two models constitute independent verification.

Implementation phases are intentionally distinct: (1) manually inspected relay records; (2) optional deterministic CI only with Chad's approval; (3) optional authenticated orchestration, separately designed and approved. Only phase 1 is drafted here.
