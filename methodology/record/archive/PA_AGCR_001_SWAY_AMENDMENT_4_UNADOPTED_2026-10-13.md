# Archival status (owner decision — 2026-10-13)

**ARCHIVED / NOT ADOPTED.** Historical candidate SWAY Amendment 4, retained as a theoretical proposal and redundancy review, **not** as binding methodology, a completed simulation, or a failed experimental test.

**Reason for archival:** Existing PA rules M3, M4, M7, M10, M17, M18, C-EVID and C-BUILD substantially address the proposed methodological concerns. The documentary redundancy audit did **not** demonstrate a nonredundant rule or satisfy M18's incident threshold. The candidate C-EFFECT control was therefore **not adopted**. The separate PA-AGCR-001 synthetic Git-integration experiment and its P1–P9 cases were **registered but not run**; no falsification outcome is claimed. The research design remains available for future owner-approved work.

**Preservation:** Historical proposal is reproduced below with its dated narrative (including earlier branch-only guide status); that narrative is **historical**, not current. Canonical `METHOD.md`, `WORKFLOW.md` and `CONTROLS.md` remain unchanged. Original file existed at root of PR #32 and is relocated here for archival, with internal relative links adjusted only. Historical commits remain in Git.

---

# SWAY Amendment 4 — Authorization, Consequence, and Effect Verification (PROPOSAL)

**Status:** PROPOSED / NOT ADOPTED / NO NEW EXPERIMENT RUN  
**Prepared:** 2026-10-13, for owner review in PA draft [PR #32](https://github.com/holland202/principia-artificialis/pull/32)  
**Scope:** Evaluation of changes to Principia Artificialis research practice; no changes to canonical [METHOD.md](../../../METHOD.md), [WORKFLOW.md](../../../WORKFLOW.md), [CONTROLS.md](../../../CONTROLS.md), or [NOTE_TEMPLATE.md](../../../NOTE_TEMPLATE.md).  
**Source of inspiration:** Anthropic's public article [*Redesigning source control at Anthropic*](https://www.anthropic.com/engineering/redesigning-source-control) (2026-10-13). The source is attributed, not treated as an independent safety or performance validation. Source intake and its limits are documented in [PA-AGCR-001_DESIGN_INTAKE.md](../../../docs/PA-AGCR-001_DESIGN_INTAKE.md) and [the external-source record](../../../docs/external/anthropic_scion_2026-10-13_excerpt.md).  
**Internal evidence inspected:** Sovereign Veritas reports linked below; those report bounded self-tests, not independent validation.  
**Provenance:** Chad Holland directed this line of inquiry. ChatGPT (OpenAI, GPT-6) drafted the proposal and performed the source-comparison review. Human review level: **direction only** at drafting. Human editorial/line-by-line validation: **not yet asserted**. Human responsibility: Chad Holland. No Anthropic affiliation or endorsement is asserted.

> **Governance boundary:** This is a candidate amendment for discussion. Under M18, a proposed rule is **not** adopted merely because it sounds prudent, appears in another company's workflow, or could have detected an implementation defect. A demonstrated methodological failure *not already caught by SWAY as written* is the adoption prerequisite. None has been established by this review.

## 1. Question

Does PA's existing methodology need a new triggered control for claims about effects that AI agents execute, or do M3, M4, M7, M10, C-EVID, C-BUILD, and W4 already require enough scrutiny when correctly applied?

The target is the **method**, not a new gate implementation, a generic best-practices checklist, or a claim that Anthropic's source-control architecture can be transplanted. The registered PA-AGCR-001 integration-boundary experiment remains separate and **NOT RUN**.

## 2. Primary evidence (known before this proposal)

| Existing bounded finding | What the record reports | What the method question is **not** answered by |
|---|---|---|
| [SV-ATTACK-001](https://github.com/holland202/sovereign-veritas/blob/main/docs/SV_ATTACK_001_RESULTS.md) | A deterministic pre-execution mutation led to the executor receiving parameters different from those authorized (Q1), and the relevant verifier accepted the package (Q3). | It does **not** establish that SWAY lacked a rule; SWAY's own registered attack instrument discovered the failure. Later [SV-FIX-001](https://github.com/holland202/sovereign-veritas/blob/main/docs/SV_FIX_001_RESULTS.md) reports narrowly scoped candidate fixes; those do not establish a general repair. |
| [EO-1](https://github.com/holland202/sovereign-veritas/blob/main/docs/EO1_RESULTS.md) | A recorded success/non-execution status diverged from an independent marker-file effect observation in constructed tests. | It does **not** prove a production side effect, nor that M10 already failed as a *method*; the existing instrument explicitly detected the gap. |
| [XB-1](https://github.com/holland202/sovereign-veritas/blob/main/docs/EXECUTION_BOUNDARY_RESULTS.md) | Controlled duplicate-ID, concurrent-attempt and write-failure scenarios produced effects that a post-execution ledger did not faithfully constrain or record. | It does **not** establish a universal exactly-once mechanism or a population risk rate. |
| [PA-AGCR-001 registration](../../../docs/PA-AGCR-001_PREREG.md) | A new synthetic Git landing-boundary question has nine prospective falsifiers, including replay, stale authorization, race and sabotage. | These are **predictions, not outcomes**. No authorization or methodology improvement has been empirically established from them. |

**Interpretation:** The *implementation and evidence-surface gaps* are real within the recorded synthetic scopes. The narrower assertion that a **new methodology rule** would catch something the current method cannot remains **UNRESOLVED**. No additional rule may be called ADOPTED from these reports alone.

## 3. Overlap audit: avoid duplicating canonical rules

| Existing source of authority | Already covers | Open issue worth inspecting |
|---|---|---|
| M3 (anti-vacuity) | Plant a failing case that flips the verdict | Did a previous effect observation test lack a reachable failure path despite being marked as a valid instrument? |
| M4 (real code, stand-ins named) | Run the actual mechanism; label mocks | Were external-effect conclusions promoted from only a modeled sink? |
| M7 (honest status labels) | Separate mathematical, implementation and empirical claims | Did a recorded gate decision get presented as proof a real action happened? |
| M10 (nothing certifies itself) | Independent input needed for a verdict above UNVERIFIED | Does it explicitly cover an executor-controlled *effect receipt*, not just the decision evidence? |
| M13 (AI provenance) | Who authored, reviewed, and accepted an artifact | No evidence that another general approval checklist is needed; don't add a duplicate. |
| C-EVID | Fresh, stale, unavailable, contradictory, same-source-derived, replayed evidence | Are decision evidence and side-effect evidence separately assessed when the study claims an effect? |
| C-BUILD | Fail-closed verdicts, hard vetoes | Does a gate verdict's scope match the actual action parameters at the final boundary? |
| W4/W5/W7 | Real harness, sabotage, attack, CI and merge | Can post-merge CI be mistakenly described as pre-merge authorization? |
| M17/M18 | One definition per rule; empirical incident before rule adoption | Avoid rewording M10 as a new rule without finding a genuinely missing requirement. |

This audit is a **documentary comparison**, not a registered methodology-comparison experiment. No superiority verdict is given.

## 4. Candidate amendment decisions (none active)

### A4-D1 — Effect-correspondence control: **CANDIDATE, NOT ADOPTED**

**Proposed name:** C-EFFECT — Execution/effect claim correspondence.

**Candidate trigger:** An experiment, evaluation, or published finding asserts that an authorization mechanism controlled or caused an external, simulated, or repository-changing effect; or asserts at-most-once, exactly-once, or no unauthorized effects.

**Proposed normative text — NOT BINDING:**

> The registered effect claim identifies (a) the immutable action and authorization it applies to, (b) the precise effect boundary and all relevant bypass paths, (c) an observation of the actual effect independent of the mechanism's own success field, and (d) how mutation, replay, races, stale evidence and a failure of the recording path affect the claim. A decision log or returning executor is not by itself proof of an effect. Incomplete observation cannot certify absence of an effect; a partial boundary inventory cannot certify complete mediation. The instrument includes a legitimate positive effect, a blocked effect, and a planted bypass that changes the measured outcome.

**Scope qualification:** This proposed control specifies **what evidence a research claim must have**. It does not impose particular locking, signature, attestation, or network infrastructure on all systems. For effects that cannot be independently observed, report the limitation and narrow the claim. Its trigger is evidence about protected effects, not every note, PR, or external source.

**Possible alternatives:** Expand the interpretation of M10 and C-EVID in a non-normative example; create a repository-specific PA-AGCR-001 testing checklist; or adopt no change. If any suffices, M17/M18 favor **no new rule**.

**Required M18 evidence:** Find at least one dated research claim previously promoted in compliance with the then-current method, yet wrongly equating a verified decision/record with a verified effect, **and** demonstrate that the proposed control would have blocked that specific promotion while current rules, correctly interpreted, would not. Neither a mere implementation bug nor a late discovery that was already caught by M3/M10 is sufficient.

### A4-D2 — Authorization at the integration boundary: **EXPERIMENT-SPECIFIC, NOT A GENERAL METHOD RULE**

For PA-AGCR-001 only, investigate approvals bound to exact Git objects, trusted policy, approver identity and target head, with stale/replayed authorization refused or deferred and final validation at the effect boundary. The candidate comparator is a naive preflight-only check.

This is a **system behavior specification** requiring its own preregistered tests and controller design; it is not evidence that a new SWAY methodological MUST is missing. Do not silently change the maintenance-only Sovereign Veritas release or claim an atomic commit protocol exists.

### A4-D3 — Consequence-sensitive human review: **DOOR / NOT ADOPTED**

A reviewer may prioritize changes that modify permission checks, evidence boundaries, executable effects, security policy, deployment or protected content over cosmetic changes. But the actual Git diff, changed object set and effective authorization must be assessed independently of the proposing agent's summary; AI-authored risk labels are advisory.

**Reason to defer:** PA already records the *actual* human review level under M13. The current materials show no demonstrated method failure caused by the absence of a globally required consequence-tier rule. Amendments should not create bureaucratic thresholds from unverified third-party practice. If pursued, register missed high-impact edits *and* unnecessarily escalated benign edits to measure costs as well as detection.

### A4-D4 — Distinguish detection from authorization: **INTERPRETIVE CLARIFICATION CANDIDATE**

Post-merge CI, audits, dashboards and observer alerts can detect a failure or support remediation; they are not retroactive permission for an effect already committed. This follows from existing W7/M7 distinctions. Prefer a worked example in a research appendix unless an M18-qualified incident proves a normative gap.

### A4-D5 — External engineering/IP boundary: **ALREADY COVERED; NO NEW RULE**

Use C-EXT and M13. Cite the third-party article accurately; separate vendor-reported measurements from PA results; independently express and test general techniques. Do not copy private code, confidential artifacts, extended expressive text, trademarks as product affiliation, or third-party source files into PA without a separate rights/license assessment. This proposal contains no copied Anthropic implementation. General ideas being reusable does **not** settle patent, license, contract or commercial-distribution questions; evaluate those separately if a product is planned.

## 5. Study needed before M18 adoption

**Current study state: PARKED / NOT REGISTERED FOR CONFIRMATORY COMPARISON.**

A prospective study comparing present SWAY against a proposed SWAY+C-EFFECT treatment is a **methodology comparison**. The canonical C-METHCOMP control refers to a specific comparison protocol parked at Stage 2, with independent task construction and scoring not available. **Do not run an informal A/B and report it as confirmation.** A new or unparked registered method-comparison plan, with independently constructed tasks, a sealed scoring function, matched budgets and its own anti-vacuity controls, requires the applicable authorization/change process.

**Preliminary gap audit that does not make comparative efficacy claims:**
1. Assemble a date-pinned list of candidate incidents and the method revision then applicable.
2. Identify the *exact* claim that was promoted and the independent observations available at the time; do not reconstruct success from a later narrative.
3. Mark each case: caught under current rule, missed despite correct application, rule ambiguously worded, or information insufficient. Do not relabel the historical outcome.
4. If no case satisfies A4-D1's M18 prerequisite, retain the candidate as a **door**, not a rule.
5. If a case qualifies, propose a *separate frozen* amendment naming only the missing obligation, with its effect on the index, trigger table, templates, lint and migration inventory. Owner must approve before adoption.

**Anti-vacuity proposal, not executed:** An evaluation must include an ALLOW with independently observed authorized effect; a DENY/DEFER with zero effect; a DENY/DEFER with a hidden actual effect while records remain clean; and a wrong-action effect after a correctly recorded ALLOW. If a proposed control cannot distinguish the third and fourth from the positives, it is not a useful candidate. Observability limitations must be explicitly recorded.

**Potential falsifiers of the need for Amendment 4:** An audit finds that all credible failures were already caught by an existing rule when correctly followed; a proposed C-EFFECT rule adds no distinct mandatory evidence; an instrument's apparent detection comes entirely from untrusted self-reported logs; or a method comparison lacks independent tasks/scoring. Such results retain the original rule set unchanged.

## 6. Trigger assessment for this proposal (M16)

| Trigger | Answer | Reason |
|---|---|---|
| C-FEAS | No, for this written proposal | No eligible-population count or corpus-dependent claim; later task construction must reassess. |
| C-NOISE | No, for this written proposal | No stochastic instrument runs. A later trial using AI evaluators must activate baseline noise controls. |
| C-STAT | No, for this written proposal | No rates, confidence bounds, means, or superiority claims. |
| C-EVID | Yes | Source freshness, dependency and misleading evidence surfaces are central; this document cites existing registered case records and marks missing validations. |
| C-INDEP | No, for new claims | No replication asserted. Earlier source reports retain their own self-test attribution. |
| C-EXT | Yes | Outside public Anthropic source is attributed and provenance-limited; its text is not replicated here. |
| C-DEVICE | No | No device-specific experiment or portability claim. |
| C-BUILD | No, for this document | The proposal itself is not verdict-producing software; a later adapter activates C-BUILD. |
| C-EXPLORE | Yes, disclosed | The design was motivated by existing historical SV tests and the public article. This is NOT a fresh confirmatory method result. If prior exploratory forks of a future registered claim are identified, record them under the canonical process. |
| C-METHCOMP | **Yes for any proposed head-to-head method evaluation; PARKED** | No method comparison is run by this documentary review. Existing canonical comparison prerequisites remain unsatisfied. |

## 7. Adoption and release gates

**Present answer:** No Amendment 4 rule is adopted, and no canonical file is changed. This document is a reviewable proposal and does not alter the already registered P1–P9 outcomes for PA-AGCR-001.

Before a future adoption action:
- Verify an M18-qualifying methodological failure rather than merely an implementation failure.
- Resolve overlap with M10, C-EVID and C-BUILD; default to clarifying their application or using a project-local control rather than adding duplicate normative machinery.
- Freeze and perform a valid comparison only if the question genuinely claims methodology improvement; obey C-METHCOMP.
- Propose an append-only dated amendment, an exact canonical diff and explicit migration/compatibility notes; do not change historical registrations.
- Update only canonical definitions in METHOD.md / WORKFLOW.md / CONTROLS.md as applicable, with checked references in NOTE_TEMPLATE.md / CLAUDE.md / method_lint, after human acceptance and testing.
- Keep published negative findings. Review applicability to local-first, offline deployments without implying that central always-online architecture has been adopted.
- No automatic posting or merging. Owner decides if and when to adopt.

**Remaining door (M15):** Is there a credible, documented instance of a research finding that was wrongly promoted *despite compliant execution of current M3, M7, M10 and C-EVID*, and for which a clearly non-redundant C-EFFECT trigger would have prevented the erroneous claim?

---

*Provenance: this is a newly written, independently phrased PA analysis. Anthropic's public article is cited as a source of engineering inspiration, not incorporated as copied methodology text or code. SV historical reports are linked with their original limitations. This amendment remains PROPOSED and unrun.*

## Appendix — subsequent documentation-only core integration (2026-10-13)

After this initial proposal, Chad Holland directed incorporation of the useful engineering practices into the core methodology. On draft PR #32, commit `35c6aefb41cd8d77dd9acde54e2cd1c54fd9ac73` inserted **§2A Engineering application guide — agent-generated changes (non-normative)** into `METHOD.md`. The section records candidate practice for inspecting actual diffs, binding approval to exact revisions and authorized scope, rechecking at effect time, distinguishing recorded decisions from observed effects, consequence-oriented review, adverse cases and locally inspectable boundaries.

**Change-status reconciliation:** The earlier sentence in §7 that "no canonical file is changed" described the state at original drafting. `METHOD.md` now has a proposed **documentation-only edit on the unmerged PR branch**, while `main` and its binding normative M/W/C rules remain unchanged. This appendix is an add-only correction; it does not reword or retroactively adopt A4-D1/C-EFFECT. The method-lint and full test suite have **not been run** in this session; document-only verification is not test conformance.
