# Contributor Trust and Responsibility Path (proposal)

**Status: DRAFT — proposed governance policy; not effective until owner review and merge.**
**Scope:** Principia Artificialis participation and repository access. This document does not change scientific acceptance standards in [METHOD.md](METHOD.md), [WORKFLOW.md](WORKFLOW.md), or [CONTROLS.md](CONTROLS.md).

## Principles and separation of authority

Contributors may challenge any result irrespective of role or seniority. Trust is evidenced by accountable actions, reproducibility, honest disclosure, and response to criticism—not agreement with the owner, popularity, number of commits, or positive findings. Attribution belongs to the actual contributors; membership, authorship, and repository permission are different decisions. No role automatically grants co-authorship, ownership, compensation, or access.

Scientific claims remain subject to the canonical method: M2 registration, M3 anti-vacuity, M7 honest validity labels, M8 preservation of failures, M10 independent-evidence boundaries, M12 append-only history, M13 AI provenance, M16 triggered controls, and applicable W/C controls. Contributor evaluation must not silently amend those rules (M17–M18).

PA currently operates as a voluntary, unpaid independent research initiative. There are no guaranteed jobs, stipends, revenue shares, co-authorship, or future permissions. Future arrangements require separate explicit agreement. Individuals can withdraw without forfeiting credit for accepted contributions.

## Role ladder

| Stage | Role | Permissions | Evidence needed to advance |
|---|---|---|---|
| 0 | Visitor / applicant | Public issues, discussions, forked PRs | Understand conduct and provenance expectations; choose a scoped first task |
| 1 | Independent research contributor | Propose, reproduce, challenge, submit PRs | One substantive auditable contribution with pinned source, commands/output, results and negative findings; resolve feedback or document limits |
| 2 | Trusted research collaborator | Coordinating scoped research and optional mentoring, with no automatic write permission | At least two additional reviewed contributions on distinct questions or failure modes; one adversarial/negative-control result; a review of someone else's work; sustained disclosure and constructive response to corrections |
| 3 | Scoped repository writer (optional) | Limited technical write role as GitHub permits; still PR-only changes to protected branches | Demonstrated care with code/evidence, security hygiene, owner-approved scope, branch protection, and a probationary review period |
| 4 | Maintainer / research steward (optional) | Owner-delegated triage/maintenance responsibilities; no automatic scientific authority | Continued successful stewardship, documented conflict-of-interest handling, incident response, and periodic owner review |

These are **suggested minimum evidence thresholds**, not automatic promotions or score-based entitlements. High-quality negative findings count as positive contributor evidence. A serious integrity or security issue can block promotion regardless of count.

## Reviewable evidence for each contribution

Record in the issue or PR: (1) exact question and proposed falsifier; (2) scope and pinned source commit; (3) environment and dependencies; (4) executable commands, raw stdout/stderr and exit codes, or a justified limitation; (5) source and output hashes where relevant; (6) interpretation separately from observation; (7) failures, discrepancies, and unperformed checks; (8) AI model/version and actual assistance, plus human validation level; (9) review disposition and independent-verification status.

A research contribution can be **accepted as a useful, documented contribution** even while its hypothesis is refuted or scientific replication remains unresolved. Do not equate contributor recognition with validation of the research.

## Advancement process

1. Contributor requests review through a public issue, linking evidence rather than resubmitting it.
2. Owner or delegated reviewer performs a documented checklist review against the above criteria; missing data are marked open, not guessed.
3. Contributor gets a chance to respond to concrete concerns or record disagreement without retaliation.
4. Owner posts a short decision: current stage, evidence supporting it, limitations, approved responsibility scope, next attainable step, and review date if relevant.
5. Changes of role are recorded in a dated, append-only contribution or governance record. Scientific records are never rewritten as a result of promotion.
6. Any repository permission change occurs separately, through GitHub's access controls, only after explicit owner authorization. No issue comment, policy merge, or AI-generated decision itself grants access.

A denied or deferred advancement request should identify specific missing evidence, not an opaque judgment. Contributors can request a second review with new evidence.

## Safety and access boundaries

- Stage 0–2 contributors need **no direct repository write access**. Forks and PRs remain the preferred path.
- If Stage 3 is authorized, prefer the smallest supported permission scope, protected default branch, mandatory PR review, passing checks, no force-push or branch deletion, and no self-approval for one's own changes. GitHub permissions vary by repository/account plan; verify actual available controls before promising them.
- No sharing cloud credentials, SSH private keys, CI secrets, financial accounts, signing keys, security recovery codes, or unpublished private datasets. No production/cloud access is implied by GitHub roles.
- Security-sensitive changes (gate policy, verifier, workflow, permissions, release signing, data publication) require explicit owner review and independent evidence appropriate to the risk.
- For an incident: suspend the affected permission if necessary, preserve evidence, document the narrow reason, and provide a review/appeal path. Avoid public personal accusations without established facts.
- Mentorship/sponsorship is optional. Sponsors help orient and review referred contributors; they are accountable for their own representations and diligence, not every unforeseeable act of others. Sponsorship never confers scientific or merge authority over other contributors.

## Periodic stewardship and removal of access

Review any granted writer/maintainer permission at an agreed interval (suggested: every 90 days), when the scope changes, or after a relevant incident. Inactivity alone is not misconduct. Remove permissions when no longer needed, at the contributor's request, or after documented security/integrity concerns, without erasing attribution or completed contributions.

## Current example: Sandeep (@sunny-kavixo)

**Recorded stage: 1 — independent research contributor**, based on the documented Note #040 partial reproduction, raw-evidence submission and AI-provenance disclosure in [collaboration issue #26](https://github.com/holland202/principia-artificialis/issues/26). The historical +0.7133 discrepancy remains unresolved. His [EGRR proposal, issue #28](https://github.com/holland202/principia-artificialis/issues/28), is approved **for protocol development only**, not as a validated result, confirmatory-run authorization, or write-access decision.

**Suggested next milestones (not pre-approved results):**
1. Agree and freeze the EGRR protocol with competing controls, exact decision rules, resource accounting, source/model hashes, leakage prevention and AI-assistance provenance.
2. Submit a separate reproducible exploratory implementation/results package, keeping every deviation and failure.
3. Independently critique a different PA experiment or control, with at least one substantive attempt to falsify it.
4. Submit a second distinct substantive contribution and respond to reviewer questions with raw evidence.
5. Request a documented Stage 2 review. No automatic writer role or seniority over scientific conclusions follows.

## Open governance decisions

Before this policy is adopted, confirm: who may conduct advancement reviews; whether a second reviewer is required for Stage 3; the available GitHub branch-protection/permission controls; whether and how to publish a contributor register; and what review or appeal procedure is feasible in a small volunteer project.

**Policy status:** Proposal only. Adoption, if approved, is a governance change to be recorded by owner review. This policy cites existing scientific rules rather than redefining them.
