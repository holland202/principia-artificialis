# PA-LINEAGE-001 — Scientific Lineage Graph: initial software build registration

**State:** REGISTERED — NOT RUN at the time of this commit.
**Method:** [METHOD.md](../METHOD.md) at blob SHA `6e4247ced1f2eef8b3c9917624d17d46d5bb80aa` on main commit `05078579b674f8a93cc56de4eba3d5fa6511d159`.
**Scope:** Standalone, local, stdlib Python append-only event journal, reproducible graph export, and a read-only browser-based explorer of hypotheses, revisions, evidence references, tests and failures. Beginner-facing explanatory text. No user accounts, external ingestion, AI inference, global deployment or automatic scientific verification.
**Authors:** Direction and long-term concept: Chad Holland. Implementation, documentation and self-tests to be drafted by ChatGPT (OpenAI GPT-6), human review **direction only** at registration. Owner review not assumed.
**Status axes:** Mathematical NOT RUN; implementation NOT RUN; empirical NOT RUN. This is a build registration, not a scientific discovery.

## W1: falsifiable question

Can an operator use this exact prototype to append and explore a branching history of scientific hypotheses and outcomes **without allowing later contributions to overwrite old records or turn an experiment outcome into an unearned scientific truth claim**?

## Contract and case matrix (pre-execution)

- **P1 / benign:** Create an initial hypothetical idea, record a refuting experiment, then register a revised descendant. After reloading the journal, all three events still exist; the child's parent points to the original; exit 0.
- **P2 / forbidden or missing evidence:** Attempt to record `HELD` or `REFUTED` without a nonempty evidence reference, scope, and registered prediction; the operation raises a validation error and journal length does not change.
- **P3 / corruption:** Change one non-digest character of a committed journal record and read it back. The reader raises a `JournalError`, rather than accepting it as valid.
- **P4 / invalid relationship:** Attempt to attach a test to an unknown hypothesis or revise from an unknown parent. Both operations refuse and preserve the file.
- **P5 / read-only graph:** Export graph nodes/edges from a valid record and ensure the original has no automatic scientific promotion. Imported `HELD` / `REFUTED` predictions may be *displayed*, but hypothesis scientific status is `UNASSESSED` and cannot be supplied by the contributor.
- **P6 / sabotage:** A deliberately corrupted event digest used with `--sabotage` produces a nonzero process exit; the benign `verify` command exits 0.
- **P7 / no-code educational UI:** Browser can display source-qualified hypothesis lineage from a loaded JSON graph and create a local proposal export; this is checked by static source inspection, **not** claimed as browser-tested or accessibility-validated.
- Outcome recording: print `P1 ... P7` results; `VERDICT n of m as registered`; SHA-256 of canonical machine-readable results; save stdout and exit status in `results/PA-LINEAGE-001/`. A result is `HELD`, `REFUTED`, `IMPLEMENTATION_ERROR`, `NOT RUN`, etc per METHOD §4. No numeric performance or scientific efficacy claims.

## Controls, limits and independent rival

**Simplest rival:** a plain GitHub issue/discussion thread. Both can preserve history and link evidence; no superiority claim is registered, so no comparative performance test or efficacy claim.

**Anti-vacuity (M3):** clean journal accepted; altered content rejected, missing evidence rejected, non-existent parent rejected. Sabotage must exit 1 (not a printed claim of rejection).

**Stand-ins (M4):** deliberately constructed hypothetical scientific ideas and invented evidence-path strings. No real scientific experiment or external research corpus.

**Evidence ladder (C-EVID):** fresh = manually entered source reference with explicit label, NOT authenticated; stale = no freshness verification; unavailable = refuse evidence-based outcomes missing references; contradictory = retain parallel observations without choosing a winner; derived same-source = no independence inferred; replayed = duplicate IDs rejected, while semantic repeats remain possible. The prototype does not authenticate input data.

**C-BUILD:** errors/absent mandatory fields fail closed for writes; no inferred authority, no scientific-status promotion.

**M10 / C-INDEP:** Any run performed by the AI author under Chad's direction is **self-tested**, not independently replicated.

| Trigger | Answer yes if … | Control | Answer (yes / no + reason) |
|---|---|---|---|
| Feasibility | the design depends on how many inputs, units or records have some property (real data, logs, corpora, model outputs) | C-FEAS | no — fixed constructed cases, no corpus count claim |
| Noise | any arm can give different outputs for the same input (model sampling, nondeterministic hardware, network, timing) | C-NOISE | no — deterministic behavior conditioned on events; IDs and timestamps excluded from predictions |
| Statistics | a claim states a rate, probability, mean or difference estimated from samples | C-STAT | no — no population inference |
| Evidence | the question is whether a rule or system handles its evidence correctly (freshness, source, provenance of inputs) | C-EVID | yes — see ladder above |
| Independence | a claim says independent, replicated, reproduced or externally reviewed, or counts more than one implementation as confirmation | C-INDEP | yes — self-tested only; no claim of independent replication |
| External | the work quotes, cites or relies on material from outside the repository (a critique, a question, a message, a dataset, another system's figures) | C-EXT | no — constructed data and existing internal PA rules only |
| Device | a claim is about behaviour on a specific device or platform, or files move between machines | C-DEVICE | no — no S25 claim; execution platform explicitly named later |
| Verdict code | the artifact returns a verdict (a gate, guard, verifier, check or lint) | C-BUILD | yes — journal integrity and event validation checks |
| Exploration | anything run before registration produced outputs on the registered cases, or the claim came out of exploratory search | C-EXPLORE | no — ideation only; no PA-LINEAGE-001 code/cases run before registration |
| Method comparison | the study compares methods | C-METHCOMP | no — no comparative method claim |

## Design constraints / threats

- Journal uses a SHA-256 chain to detect local edits with an independently trusted head, **not** to authenticate authors or protect against wholesale rewriting/truncation by an attacker with filesystem access.
- One local writer; simultaneous writers and crash durability are not claimed. Network access, untrusted-code execution, external API publishing and remote multi-user auth are out of scope.
- Source references are **claims supplied by contributors**, not independently attested evidence. An experiment prediction outcome is different from claim/evidence status.
- Rendering is read-only with respect to the journal: exported proposals require review and explicit CLI admission. No browser network requests or token handling.
- Do not change METHOD.md, existing scientific claims, or the earlier PA file graph.
- Retain original failures. Corrections are new children and new tests, not edits.

## W15 next unrun door

Independently authored implementation of the event validator; concurrent-write fault testing; externally anchored journal heads; actual novice usability and accessibility studies; independent inspection of source provenance; federated contribution moderation.

*Freeze condition:* This file is committed alone on a separate feature branch **before any PA-LINEAGE-001 implementation execution**. Subsequent results are append-only records.