# PA Research Gateway — public website pilot

**Status:** public navigation and voluntary workflow pilot. This document does not amend PA's adopted research methodology, grant repository permissions, or freeze/authorize any experiment.
**Owner:** Chad Holland.

## What changed

- `index.html`: beginner-friendly PA homepage, mission, participation path, founder's novice background, substantial use of AI tools, transparent limitations, links to existing sources.
- `dashboard.html`: read-only public research issue navigation, existing submission forms, evidence checklist, research pathways, and links to contributor attribution.
- `file-graph.html`: byte-for-byte preservation of the previous interactive root file-graph homepage. Keep it accessible; do not discard original graphics or data.

This is a static website, not a paid app. It has no logins, server database, API keys, analytics trackers, payment handling, contributor rankings, or AI-powered auto-approvals.

## Existing sources of authority

Follow `JOIN_RESEARCH.md`, `METHOD.md`, `WORKFLOW.md`, `CONTROLS.md`, `REVIEW_PLAYBOOK.md` and `CONTRIBUTOR_RIGHTS.md`.

**Status update, 2026-10-22:** `RECRUITMENT_PROTOCOL.md` is **in effect as a pilot** (PR #83: recruitment reopened by owner direction). `CONTRIBUTOR_TRUST_PATH.md` is still a **draft proposal, not adopted**. Its procedures must not be represented as in force.

Independent researchers may choose their own questions and submit them without an invitation. No deadlines, membership fees, required work hours, or automatic access.

*(Superseded lines, kept verbatim: "`RECRUITMENT_PROTOCOL.md` and `CONTRIBUTOR_TRUST_PATH.md` are marked **draft, not adopted**. Their procedures must not be misrepresented as automatically in force." and "The pause affects **outbound recruitment**, not independent public submissions.")*

## Lightweight pilot plan

1. Week 1: Check site navigation, accessibility, mobile layout and existing contribution links.
2. Week 2: Work through one or two already-existing submissions using `REVIEW_PLAYBOOK.md`. Keep source review distinct from actual testing.
3. Week 3: Collect only *documented* usability problems and missing evidence fields. Draft changes separately for owner approval.
4. Week 4: Decide whether the pilot reduces the owner's workload before considering additional recruitment or automation.

These weeks are suggested checkpoints, not obligations placed on contributors. Contact with existing volunteers remains voluntary and at their pace. Do not publish contributors' private notes or imply their consent to new roles.

## Owner-only management is separate

The public dashboard intentionally does **not** expose an owner progress sheet, private messages, individual volunteer workloads or private check-ins. The owner may use a separately distributed **local/off-repository tracker** for private notes. No owner tracking file or completed records are stored in this public GitHub repository, and this website has no login or access control.

Existing contributor attributions are linked via [AUTHORS.md](../AUTHORS.md); credit does not imply approval of the associated hypotheses. Volunteers control their own workload and may opt out of additional assignments.

## Publication validation and fallback

Before release, confirm the preserved `file-graph.html` is unchanged from its earlier archived implementation and that local links point to existing paths. The dashboard uses a public, unauthenticated GitHub Issues API call and must degrade gracefully when offline or rate-limited. All issue titles are assigned with DOM `textContent` rather than rendered as HTML. Responsive layout uses a single column on smaller screens, including tablet-sized and in-app browser viewports. Existing artwork from `figures/principia_hero.png` is reused instead of introducing an unreviewed brand asset.

The repository's configured homepage URL does not prove that GitHub Pages is active or reachable. Publishing files to `main` also does not prove the site has deployed; deployment must be checked separately. If needed, restore the previous root homepage from Git history without rewriting history.

## Provenance

Substantially AI-assisted draft: ChatGPT (OpenAI, GPT-6), source-level review of PA's public docs; directed by Chad Holland. This implementation is not an independent scientific evaluation. Its website behavior requires deployment and browser verification.
