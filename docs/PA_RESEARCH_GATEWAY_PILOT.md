# PA Research Gateway — public website pilot

**Status:** public navigation and voluntary workflow pilot. This document does not amend PA's adopted research methodology, grant repository permissions, or freeze/authorize any experiment.
**Owner:** Chad Holland.

## What changed

- `index.html`: beginner-friendly PA homepage, mission, participation path, founder's novice background, substantial use of AI tools, transparent limitations, links to existing sources.
- `dashboard.html`: read-only public research issues view, existing submission forms, evidence checklist, and a copyable **private** weekly check-in template.
- `file-graph.html`: byte-for-byte preservation of the previous interactive root file-graph homepage. Keep it accessible; do not discard original graphics or data.

This is a static website, not a paid app. It has no logins, server database, API keys, analytics trackers, payment handling, contributor rankings, or AI-powered auto-approvals.

## Existing sources of authority

Follow `JOIN_RESEARCH.md`, `METHOD.md`, `WORKFLOW.md`, `CONTROLS.md`, `REVIEW_PLAYBOOK.md` and `CONTRIBUTOR_RIGHTS.md`.

`RECRUITMENT_PROTOCOL.md` and `CONTRIBUTOR_TRUST_PATH.md` are marked **draft, not adopted**. Their procedures must not be misrepresented as automatically in force.

Independent researchers may choose their own questions and submit them without an invitation. The pause affects **outbound recruitment**, not independent public submissions. No deadlines, membership fees, required work hours, or automatic access.

## Lightweight pilot plan

1. Week 1: Check site navigation, accessibility, mobile layout and existing contribution links.
2. Week 2: Work through one or two already-existing submissions using `REVIEW_PLAYBOOK.md`. Keep source review distinct from actual testing.
3. Week 3: Collect only *documented* usability problems and missing evidence fields. Draft changes separately for owner approval.
4. Week 4: Decide whether the pilot reduces the owner's workload before considering additional recruitment or automation.

These weeks are suggested checkpoints, not obligations placed on contributors. Contact with existing volunteers remains voluntary and at their pace. Do not publish contributors' private notes or imply their consent to new roles.

## Private owner check-in template

```text
PRIVATE PA WEEKLY CHECK-IN
Week of:
Contributor / track:
Last source revision:
Work actually checked:
Unverified or unrun work:
Blocker:
Owner decision required:
Next voluntary check-in:
Publication / permissions authorized? NO unless separately approved.
```

Keep filled-in contributor records outside the public site unless they have explicit publication permission. Scientific approval, official study execution, access grants, merges and publications remain separate owner decisions.

## Publication validation and fallback

Before release, confirm `file-graph.html` equals the former `index.html` and that local links point to existing paths. The dashboard uses a public, unauthenticated GitHub Issues API call and must degrade gracefully when offline or rate-limited. All issue titles are assigned with DOM `textContent` rather than rendered as HTML.

The repository's configured homepage URL does not prove that GitHub Pages is active or reachable. Publishing files to `main` also does not prove the site has deployed; deployment must be checked separately. If needed, restore the previous root homepage from Git history without rewriting history.

## Provenance

Substantially AI-assisted draft: ChatGPT (OpenAI, GPT-6), source-level review of PA's public docs; directed by Chad Holland. This implementation is not an independent scientific evaluation. Its website behavior requires deployment and browser verification.
