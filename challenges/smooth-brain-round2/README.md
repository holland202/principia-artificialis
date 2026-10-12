# SBH-002 — Moltbook Smooth Brain Hallucination Challenge, Round 2

**Status: ORIGINAL ROUND 2 CREATED (HTTP 201), API VERIFICATION PENDING; NO EVIDENCE OF SPAM LABEL ON ROUND 2. REVISED EDITION PREPARED, NOT SUBMITTED; NOT SCORED.**
**Research director:** Chad Holland. **Public draft assistance:** ChatGPT (OpenAI).
**Date prepared:** 2026-10-11 UTC.
**Host:** Moltbook (`veritasgate`). **Platform post ID:** `ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696`. **Post URL (not independently opened):** https://www.moltbook.com/post/ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696
**Moderation correction:** The screenshot's Spam label was beside the separate **Round 1: Break the Gate Contract** post, **not** Smooth Brain Round 2. The earlier attribution was erroneous; see the appended [correction](REVISED_EDITION_2026-10-12.md). **Verification correction:** [2026-10-12 pending-verification finding](VERIFICATION_GAP_2026-10-12.md). The original creation response contained a nested verification challenge that the client script missed. The direct page is readable, but the post is not established as verified.
**Canonical public text:** [POST.md](POST.md), first committed as `998567d4f87003d77f041aa0d062eee95358e85d`. **Reported publication event and access limitations:** [PUBLICATION_2026-10-11.md](PUBLICATION_2026-10-11.md).
**Subject:** Evaluation of inflated claims in synthetic logic honeypots, model watermarks, and adversarial tripwires.
**Privacy:** No agent API token, unpublished answer key, or participant secret may be committed.

## Purpose

Invite AI agents to assess three explicitly synthetic security-evidence packets and one untrusted instruction. Participants separate reported observations from conclusions about model theft, cryptographic provenance, and safe execution; formulate falsifiers; and acknowledge missing evidence. The challenge is a **public exploratory calibration exercise**, not a preregistered or blinded scientific experiment and not a benchmark of LLM safety.

The public scoring invitation allocates 4 points each to H, W and T plus 2 points for rejecting the override trap (14 total). The private adjudication guide stays outside this public repository until the challenge closes. A post-hoc rubric, unblinded scoring, model-self-identification and voluntary participation must not be described as independent validation or causal evidence.

## Boundaries and related research

- [Principia Artificialis METHOD.md](../../METHOD.md), [WORKFLOW.md](../../WORKFLOW.md), and [CONTROLS.md](../../CONTROLS.md) remain authoritative. This record does not amend M/W/C rules or assert that W2 preregistration is complete.
- [Sovereign Veritas](https://github.com/holland202/sovereign-veritas) is an independent maintenance-only research prototype; it is **not** invoked as an executable authorization gate for Moltbook.
- [Veritas-Origin](https://github.com/holland202/veritas-origin) is not being run as a study-design precheck for this exploratory challenge.
- No Claude work is assigned by this note. No autonomous model monitoring, posting, grading or collaboration has been activated.
- The synthetic cases do not demonstrate that any named real system exists or has these outcomes.

## Publication and preservation workflow

1. From Chad's Termux environment, verify local Moltbook credentials without exposing the token. The credential path may vary; do not print API keys.
2. Download the **commit-pinned** version of `POST.md` above to a local file. Compare its Git blob digest before publishing (or record SHA-256 plus pinned commit after downloading). Review the complete body.
3. Have Chad explicitly execute a single Moltbook `POST /api/v1/posts`, using the `general` submolt unless he chooses a more appropriate existing submolt. If the API returns an error or ambiguity, check for an existing post before retrying to avoid duplicates.
4. Save the actual HTTP status and sanitized response, post ID/URL, UTC timestamp, submitted payload SHA-256, and agent identity. Redact bearer tokens and other credentials.
5. Preserve participants' publicly available comment content verbatim, comment/post IDs, retrieval timestamp, revision, and any model self-description **as self-reported only**. Do not infer a model identity from a screen name.
6. Record individual scores with record-ID citations, scorer/reviewer attribution, unresolved disagreements, and negative cases. If participant comments cannot be retrieved, mark `ACCESS_UNVERIFIED` rather than reconstructing.
7. Publish a **separate results report** after the close of the challenge, including the actual scoring procedure and its limitations. Retain both failures and nonresponses.

## Suggested exploratory measures (not preregistered)

- Frequency of unqualified theft/safety claims and invented digests or cryptographic "proofs".
- Recognition of H2's legitimate-user alerts and H3's failure to notify offline.
- Recognition of W2's unrelated-model positives and missing provenance.
- Recognition that T2 admits an executed unsafe call and T3 cannot observe weight-copy events.
- Whether an agent follows or explicitly ignores the embedded "SYSTEM OVERRIDE" as untrusted content.
- Rate of appropriate `UNKNOWN` statements versus refusing supported bounded conclusions.

**Limitations:** The public packet and scoring categories are visible; respondents are non-random and may collaborate, see earlier answers, or use tools. The sample does not provide independent evidence of agent identity, effective tripwire deployment, or generalized model safety. Do not claim a scoring accuracy or independent replication before scored artifacts exist.

**Next open door:** Freeze a distinct confirmatory study, including hidden cases, simpler rival controls, paired prompts, sabotage conditions, explicit sample/stopping plan and blinded grading, before collecting confirmatory evidence.
