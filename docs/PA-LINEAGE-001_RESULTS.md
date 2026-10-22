# PA-LINEAGE-001 — Initial software build results

**Research status:** Experimental software prototype. NOT independently validated. NOT a scientific discovery, source-authentication mechanism, or deployed multi-user system.
**Registered before execution:** [PA-LINEAGE-001_PREREG.md](PA-LINEAGE-001_PREREG.md), first committed alone at `aa567e5eb318a1f0a0ce8e9a1c6a5246f4177e0c`.
**Execution source:** [GitHub Actions run 38612373839](https://github.com/holland202/principia-artificialis/actions/runs/38612373839), job 116018726406, self-test at code commit `49a42500a4ba4df5a44397a7f92200e531732328`.
**Raw observed output:** [results/PA-LINEAGE-001/2026-10-14_ci_selftest.txt](../results/PA-LINEAGE-001/2026-10-14_ci_selftest.txt).
**Implementation and test author:** ChatGPT (OpenAI GPT-6), under Chad Holland's direction. **Human review:** direction only; no line-by-line human review asserted.
**Replication level:** self-tested. No independent implementation, independent reviewer or S25 run.

## Limits and failures first (M8)

- P7 browser behavior **NOT RUN**; static source inspection was present, not proof that the UI works on any browser. No accessibility or novice-learning measurements.
- CI tested the local event mechanics, not whether scientific claims in contributed evidence are true.
- SHA-256 record chaining provides consistency checks against ordinary line edits. It does **not** establish author identity, source authenticity, immutability against a fully controlled adversary, or detection of suffix truncation without an independently trusted head.
- Program assumes a cooperative single-writer POSIX filesystem. No durable multi-party synchronization, remote user identity, permissions or moderation.
- No external ingestion, outbound research publication, or live AI-agent execution; multi-source contributions are manually referenced, not fetched.
- Unit and acceptance tests were authored by the same AI as the software; no claim of independent adversarial validation.
- No correctness claim for Android/S25, Windows or browsers. Python used in CI was 3.11 on `ubuntu-latest`.
- Canonical PA notes, methodology files, original research conclusions and `main` remained unchanged.

## Raw observation (verbatim acceptance stdout)

```
P7_STATIC_SOURCE_CHECK: PRESENT (not browser execution)
P1 HELD
P2 HELD
P3 HELD
P4 HELD
P5 HELD
P6 HELD
P7 NOT RUN
VERDICT 6 of 7 as registered
DIGEST 209e78c4bb5385a44fb6bf8b3493df37b6786b14a8b63b313712812790af6d66
```

The same CI job reported `Ran 14 tests in 0.024s` followed by `OK`; its independent process gate checked that a clean journal returned 0, and an intentional digest sabotage returned exit 1. This confirms **only** the exact simulated cases and software version documented in the run. The local journal demo was fictional, with no empirical science.

| Registered prediction | Observation | Outcome |
|---|---|---|
| P1 Retain old and new hypotheses plus refutation | Graph preserved predecessor, experimental event and revision | HELD |
| P2 Missing evidence / scope / prediction cannot append | Three writes refused; journal bytes unchanged | HELD |
| P3 Altered record detected | Changed journal content refused | HELD |
| P4 Invalid relationship refused | Unknown revision parent and result subject refused | HELD |
| P5 No automatic scientific claim promotion | `UNASSESSED` retained, outcome not promoted | HELD |
| P6 Sabotage changes process exit | Clean accepted; altered digest detected with exit 1 | HELD |
| P7 Beginner explorer browser behavior | Static HTML artifacts inspected, **no browser run** | NOT RUN |

## Interpretation, validity and next doors

**Implementation:** The scoped constructed-input self-tests passed; that is not independent confirmation of completeness or security.
**Mathematical:** NOT RUN; no new theorem.
**Empirical:** NOT RUN; no real scientific experiment or novice study.
**Scientific claim evidence status:** INSUFFICIENT_EVIDENCE for broader usefulness or superiority.

The demo may be used for exploratory contributions but no `result` event can automatically certify its own scientific hypothesis. Its displayed `HELD` and `REFUTED` values are contributor-reported registered prediction outcomes, not a claim verdict.

Next unrun doors: open `explorer.html` in real browsers and check usability/accessibility; have an independent reviewer implement a second parser/verifier; validate external source authenticity; test crash/concurrent writers; anchor trusted heads; measure whether novices understand the distinction between a failed prediction and an unsupported theory; compare against ordinary issue-thread lineage under a preregistered protocol.

**No merge authorized by this record.** Main remains the source of truth; feature branch and PR are for human review.

*Vincit Omnia Veritas.*
