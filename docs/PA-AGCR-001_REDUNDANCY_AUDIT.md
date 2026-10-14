# PA-AGCR-001 — Redundancy gate and test disposition (2026-10-13)

**Status:** DOCUMENTARY AUDIT + STRUCTURAL CHECKS; NOT A METHODOLOGY COMPARISON; NO EXECUTION-BOUNDARY EXPERIMENT RUN.  
**Owner:** Chad Holland. **AI-assisted analysis:** ChatGPT (OpenAI GPT-6). **Human review:** direction only; line-by-line review not claimed.  
**Scope:** The nonbinding agent-change application guide added to `METHOD.md` on the draft PR branch and the candidate Amendment 4 controls.  
**Sources checked:** `METHOD.md` on `main`, GitHub blob `6e4247ced1f2eef8b3c9917624d17d46d5bb80aa`; guide-bearing `METHOD.md`, blob `67026af98a4d1cdb7294f283cc11a2443b325998`; canonical `WORKFLOW.md` blob `b74b40203f5e4b2797a4c885edcf9c0bded3c418`; canonical `CONTROLS.md` blob `5d9661cec8044695e325375242aa677494a5c6b3`.

## A. Redundancy gate — document inspection, not causal efficacy test

| Proposed practice | Current coverage | Distinctness assessment | Disposition |
|---|---|---|---|
| Inspect actual diffs; distrust agent summary | M4 real code; M10 independent evidence; M7 accurate scope | Concrete workflow example, not a distinct general research rule | **KEEP as guidance**, no new mandatory rule |
| Bind approval to immutable code/parameters and policy | C-EVID source/freshness; C-BUILD vetoes; M10 authentication independence | **Distinct target-system feature** (an adapter contract), but not evidence of a missing methodology rule | **TEST in PA-AGCR-001**; do not add universal MUST |
| Revalidate target and authority immediately before effect | C-EVID stale/replay; C-BUILD fail-closed; W5 adversarial analysis | Timing/atomicity specification for a protected effect, not a general new research method | **TEST in PA-AGCR-001**; no proof yet |
| Independently observe actual side effect | M10 cannot self-certify; M7 validity axis; M4 stand-ins | Likely overlap; could be missing explicit trigger, but M18 evidence of a compliant method miss not established | **C-EFFECT remains proposed**; no adoption |
| Consequence-sensitive review | M13 reports review that happened; W3/W5 focus case design | Candidate reviewer prioritization, not universal research criterion | **OPTIONAL guidance**; avoid invented tiers |
| Separate post-merge detection from pre-merge authorization | M7 what was shown; W7 CI and merge | Clarifies interpretation, not a new rule | **KEEP example**, no new rule |
| Content-addressed identities and local/offline objects | M11 fresh confirmation; M12 record; W8 pinned build identity | Specific engineering representation, not an epistemic method | **OPTIONAL implementation choice**, no method rule |
| New universal high-consequence trigger | Amendment 3 D12 deliberately left it as a door | Requires its own qualifying incident | **DO NOT ADOPT** |

The table does not claim that SWAY without these design practices has equivalent performance or efficacy. This is a **scope/wording/overlap review**, not an independent review or head-to-head assessment.

## B. Structural test observed (read-only GitHub-source check)

A deterministic JavaScript inspection fetched `METHOD.md` on `main` and on the draft PR branch, and fetched current `WORKFLOW.md` and `CONTROLS.md`. It located section `## 2A. Engineering application guide — agent-generated changes (non-normative)` and removed that section from the proposed file in memory, then compared the rest byte-for-byte with the fetched `main` file. It additionally performed explicit string and cardinality assertions.

**Raw check outcomes, as returned by the read-only inspector:**

```text
single nonbinding section                                PASS
main METHOD preserved byte-for-byte outside guide         PASS
canonical W and C references still present                PASS
no new normative rule IDs                                 PASS
M18 adoption boundary explicitly retained                 PASS
no automated publishing or merging implied                PASS
three existing negative finding references                PASS
risks and untested status stated                           PASS
existing canonical indexed controls intact                PASS
TOTAL: 9 / 9 structural checks PASS
```

**Scope of this check:** only the fetched file identities, the one inserted section, and the declared textual assertions. This is not `scripts/method_lint.py`, not the full repository test suite, not CI, not a live Git hook, and not an execution-effect instrument. The isolated JavaScript inspection has **not** been committed as a portable test executable; independent cold-clone reproduction is **NOT RUN**. No numerical scientific finding is promoted from these checks.

## C. Next tests, deliberately separated by kind

**C1 — Existing-method completeness audit (UNRUN):** Trace each specific past research claim that was promoted (if any) despite claiming effect evidence from only a decision log. Compare the method revision applicable at that time. Determine whether M10/C-EVID already explicitly disallowed that promotion. Do not infer that a found implementation bug proves a method rule is missing.

**C2 — New engineering-contract experiment (REGISTERED, NOT RUN):** PA-AGCR-001 P1–P9 cover benign landing, protected unauthorized change, replay, action mutation, stale target, concurrent attempts, misleading description, evidence ladder, and a bypass mutant. Before execution, freeze missing credential policy, atomicity mechanism, and fixture generator according to the registration; unresolved preconditions must result in NOT RUN/UNRESOLVED, not a retrofitted pass.

**C3 — Candidate C-EFFECT distinctness (PARKED):** Test whether adding the control catches a methodological lapse the current binding rules did not, without merely restating M10. A true head-to-head methodology comparison triggers C-METHCOMP, whose prerequisites are currently unavailable. Do not silently run one under another name or report it as confirmatory.

**C4 — Whole-repository tool checks (NOT RUN):** `scripts/method_lint.py`, linked vacuity lint, complete test suite and full CI, plus current draft branch merge compatibility and external review. No passing claim before genuine tool output.

## D. Promotion decision

**Documentation integration is appropriate, but does not adopt new MUST rules.** The current guide may be kept in a draft PR as a teaching/application aid. With no M18-qualifying methodological gap demonstrated, proposed C-EFFECT remains a door; exact-change binding/revalidation remain engineering tests. A passing structural check cannot establish their security properties. Keep the draft unmerged until full checks and owner review.

**References:** [Canonical method](../METHOD.md); [Amendment 4](../methodology/record/archive/PA_AGCR_001_SWAY_AMENDMENT_4_UNADOPTED_2026-10-13.md); [AGCR protocol](PA-AGCR-001_PREREG.md); [SV-ATTACK-001](https://github.com/holland202/sovereign-veritas/blob/main/docs/SV_ATTACK_001_RESULTS.md); [EO-1](https://github.com/holland202/sovereign-veritas/blob/main/docs/EO1_RESULTS.md); [XB-1](https://github.com/holland202/sovereign-veritas/blob/main/docs/EXECUTION_BOUNDARY_RESULTS.md).


## Archival disposition — 2026-10-13 (owner direction)

The proposed `METHOD.md` §2A application guide was **withdrawn from PR #32** to keep the adopted method unchanged. Its historical limited document-inspection results above remain as recorded and are not presented as current canonical method content. [The complete unadopted Amendment 4 proposal](../methodology/record/archive/PA_AGCR_001_SWAY_AMENDMENT_4_UNADOPTED_2026-10-13.md) is archived, not implemented or experimentally refuted. Redundancy is a **documentary assessment**; AGCR-001 P1–P9 are still **NOT RUN**. Preserve the preregistration and source intake without promoting findings.
