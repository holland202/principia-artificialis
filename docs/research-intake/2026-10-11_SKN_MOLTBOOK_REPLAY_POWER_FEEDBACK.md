# Research intake: Moltbook SKN-V1 replay, power resilience and experimental custody

**Status: EXPLORATORY QUESTION INTAKE ONLY — NOT A PREREGISTRATION, TEST, OR ACCEPTED CLAIM.**  
**Date:** 2026-10-11. **Research director:** Chad Holland. **Synthesized by:** ChatGPT (OpenAI).  
**Full source and dispositions:** [SKN-V1 draft PR #8](https://github.com/holland202/skn-v1-/pull/8), `docs/external/MOLTBOOK_SKN_FEEDBACK_SYNTHESIS_2026-10-11.md`. This source is a reviewable proposal and **has not been merged**.  
**Governing rules:** [METHOD.md](../../METHOD.md), [WORKFLOW.md](../../WORKFLOW.md), [CONTROLS.md](../../CONTROLS.md). This is a record edit under W9, not an amendment to M/W/C rules.

## Why this belongs in the research-question inventory

Outside Moltbook feedback on [SKN-V1's simulated swarm](https://github.com/holland202/skn-v1-) identified questions on replay-state loss after restart, absent key membership/revocation, physical power and thermal constraints, and control of experimental baselines. This is a good candidate for a falsifiable *research process* test: can observed criticism be transformed into a preregisterable, discriminating study **without** upgrading an outside comment into verified evidence or retroactively changing earlier results?

The documented K8 missing-store fail-open path was corrected, but K8 **4/5 as registered (K8e REFUTED)** must be preserved. K9's separate candidate freshness experiment is **5/6 as registered (P4 REFUTED)**, with a known strong loss of valid out-of-order records. Both are **author-side reported/self-tested**, not an independently established fix to restart persistence. The GitHub records and citations are in SKN draft PR #8.

The `@dynamo` claim that software simulation has zero kinetic security value is an **unsupported blanket claim**. Its more focused concern—power interruption, thermal throttling and bus jitter are not addressed by a simulation-only crypto/topology demonstration—is an appropriate **untested hardware-scope limitation**. No physical experiment is claimed.

## Proposed PA → VO → SKN → evidence feedback path (no action authorized)

1. **PA:** maintain the hypothesis and alternative explanations; identify anti-vacuity, simplest rival, feasibility, state boundaries, and specific outcome measures under the frozen methodology commit.
2. **VO:** if Chad authorizes a separate study, evaluate the **design's** capacity to discriminate a restart-related replay failure from a test-harness or persistence error. No VO precheck is claimed here.
3. **SKN-V1:** appropriate subject for a proposed software fault-injection experiment comparing volatile with persisted replay state (including missing, corrupt, stale, rollback and interrupted-write cases), with a legitimate-first-use acceptance control. Do not treat it as a simulated power-electronics test.
4. **External validation:** pin code and evidence and invite reproduction with disclosed environment. Separate an outside question, author-side run, independently reproduced result, and physical device validation.
5. **SV:** cross-project analogy only. Sovereign Veritas's real-world authorization/effect boundary is distinct; **no SV change or integrated protection is implied**.

## Unrun door

If Chad chooses to proceed, draft and commit a **new** W2-compliant preregistration to SKN-V1 for a narrowly scoped persistence fault-injection experiment with an explicit sabotage branch, then freeze it before writing or running new test code. The past K8/K9 criteria and negative results must not be repaired retroactively. A separate future real-hardware study would require instruments, platform feasibility and authorization.

No scripts executed, no new experimental data, no code/CI changes, no model-to-model task delegation. Claude remains unassigned on hiatus. This document captures a research lead, not an instruction to act.
