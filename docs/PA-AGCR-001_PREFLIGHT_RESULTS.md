# PA-AGCR-001 — Method guidance preflight and contract-freeze blocker

**Run date:** 2026-10-13 (session date)  
**Status:** LIMITED DOCUMENT INSPECTION SELF-TESTED; AGCR-001 P1–P9 **NOT RUN**  
**Owner/direction:** Chad Holland. **Tester and drafter:** ChatGPT (OpenAI GPT-6). **Human review:** direction only.  
**No independent replication.** No changes to maintenance-only Sovereign Veritas; no real merge or external protected effect.

## Exact inspected GitHub blobs

| Source | Git blob SHA |
|---|---|
| PA `main/METHOD.md` | `6e4247ced1f2eef8b3c9917624d17d46d5bb80aa` |
| PA draft branch `METHOD.md` | `67026af98a4d1cdb7294f283cc11a2443b325998` |
| PA `main/WORKFLOW.md` | `b74b40203f5e4b2797a4c885edcf9c0bded3c418` |
| PA `main/CONTROLS.md` | `5d9661cec8044695e325375242aa677494a5c6b3` |

The files were fetched via the connected GitHub tool at those revisions. A local Python checker was prepared, but could not download the same inputs because the container could not resolve `raw.githubusercontent.com`; **the Python checker was not run on valid inputs** and is not claimed as confirming evidence. Instead a separate inline JavaScript inspector, executed against the GitHub connector responses, performed the bounded checks below. The inspector script is not committed as a portable executable, so a cold-clone independent re-run has **not** been performed.

## Read-only test: exact check and sabotage

For the baseline the inspector located the single section `## 2A. Engineering application guide — agent-generated changes (non-normative)` in the draft `METHOD.md`, removed that block *in memory*, compared the remaining text exactly to PA main, checked existing rule definitions, confirmed its nonbinding status, and verified historical reference and canonical marker presence.

The sabotage arm mutated the *fetched draft text in memory* by replacing the first `NOT A NEW RULE` string with `IS A NEW RULE`. The same inspector was then applied. No GitHub document was mutated in the sabotage arm.

### Actual observed check values

| Check | Baseline | Planted mutation |
|---|---|---|
| Single nonbinding guide section present | true | true |
| Remaining main METHOD text exactly identical | true | true |
| Existing canonical rule IDs retained | true | true |
| Guide does not declare a new MUST | true | **false** |
| M18 promotion boundary remains | true | true |
| No automatic external publishing/merge | true | true |
| Existing negative finding references present | true | true |
| Unrun/test limits explicitly stated | true | **false** |
| Canonical method markers retained | true | true |
| **All checks** | **9/9 — PASS** | **7/9 — FAIL** |

**Instrument diagnostic:** The planted textual mutation is detected by two assertions. This shows only that this particular read-only assertion set could reject that exact mutated document; it does **not** demonstrate broad method linting, code-security validation, or independence. No process exit code from a portable CLI is claimed.

## AGCR-001 integration experiment preflight: HALT / NOT RUN

The [existing preregistration](PA-AGCR-001_PREREG.md) explicitly leaves these owner decisions open:

1. **Approver identity and trusted credential source:** a Git hash or an agent-written string cannot establish that an authorized reviewer signed a particular change.
2. **Protected-path policy:** which paths demand stronger approval and what precisely counts as adequate authorization.
3. **Landing/effect linearization:** the actual atomic compare-and-update or durable nonce reservation that would support the P6 at-most-once claim.
4. **DEFER-versus-REFUSE reason precedence** and malformed-evidence behavior to be frozen before coding.

These are **material experimental inputs**, not clerical details. To avoid inventing them after preregistration, we did not construct fixtures, implement the proposed adapter, or execute P1–P9. They remain **NOT RUN**; the registered success/falsifier thresholds remain unchanged.

W2 also specifies a registration commit preceding implementation, with an owner-requested freeze merged before code exists. PR #32 remains a draft and is not a frozen merged authorization to start an implementation. If the owner authorizes a contract freeze, record the exact interface and test fixtures before implementation; do not reinterpret this documentary self-test as a confirmation run.

## Interpretation and next gate

- **SUPPORTED (limited):** The new guide is a nonbinding insertion that preserves the rest of the fetched PA main method; the deliberate deletion of a key disclaimer is detectable by a bounded source-text check.
- **NOT SUPPORTED:** Any claim that C-EFFECT is nonredundant, that the registered AGCR-001 adapter prevents unauthorized landings, that exactly-once integration holds, that GitHub enforces semantic review, or that the full methodology test suite passed.
- **UNRUN:** independent/cold-clone test, full method lint and CI, PA-AGCR-001 P1–P9, real protected sink verification, and any methodology-comparison protocol.

**Next decision:** Freeze trusted reviewer credentials, protected-path policy, atomic landing boundary and verdict precedence; then implement a separate synthetic-only adapter on an experimental branch, not in the maintenance-only Sovereign Veritas codebase. Preserve raw instrument outputs and negative findings per SWAY.

## Subsequent owner disposition (2026-10-13)

The preceding `Next decision` was a proposal at the time of this inspection, **not** an authorization. The owner subsequently directed that the proposed methodology addition be archived as not adopted/redundant, and that the separate AGCR-001 experiment be retained but parked. No adapter tests (P1–P9) have been run. `METHOD.md` has been restored exactly to `main` on the PR branch; historical measurements of the former draft insertion are retained without being treated as checks of current methodology.
