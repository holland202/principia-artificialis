# SBH-002 Moltbook verification gap — appended status event

**Event type:** negative publication finding / workflow defect. **Date:** 2026-10-12 UTC. **Recorded by:** ChatGPT (OpenAI) from Chad Holland's Termux outputs, not an independent API audit.

## Observations provided by Chad

Creation request `POST /api/v1/posts` for `veritasgate` returned HTTP **201** and `success: true` with post ID `ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696`. The posting script inspected only the top-level `result.get("verification")` and printed **`Verification object: not returned`**.

A subsequent read-only diagnostic on the stored original JSON showed:
- `original.success = True`
- `original.post.id = ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696`
- `original.post.verification_status = pending`
- `original.post.created_at = 2026-10-12T01:17:03.933Z`
- `original.post.verification` was a **nonempty nested object**
- The current public `GET /api/v1/posts/<id>` returned HTTP **200**, `success:true`, the same ID and **`verification_status: pending`**.

Chad's browser screenshots independently show the direct page is readable and appears in a profile 'Hot This Month' list, but lacks a green post-level Verified label and is absent from the standard 'Posts (2)' list. **Page readability does not establish verified publication or feed distribution.** This event supersedes any interpretation that initial HTTP 201 implied a fully published/verified post.

## Technical root cause and scope

**Observed client parsing defect:** the initial script checked `result.verification` but ignored `result.post.verification`. The evidence establishes the verification object existed but was not surfaced to the operator or answered. The original script did not make a `POST /api/v1/verify` call.

Moltbook's published skill instructions describe `post.verification.verification_code`, `challenge_text`, and `expires_at`, normally allowing approximately five minutes for an answer. The old code is **likely expired**, but **the specific expires_at value has not yet been inspected and no verification attempt has been made**. Do not mark the old post `verified`, `rejected`, `expired`, or `deleted` without an observed state change. Its latest confirmed verification status is **PENDING**.

## Proposed recovery — not executed

1. Read `post.verification.expires_at` locally and compare to UTC time **without printing or committing the verification token**.
2. If time remains, inspect the challenge text privately and submit a single, properly formatted answer to the official `https://www.moltbook.com/api/v1/verify` endpoint. If expired, do not make an expired/guessed verification attempt.
3. If expired and Chad authorizes a new publication attempt, ensure the pending old post is accounted for and use the **same frozen source body**, a new post only once, with a fresh challenge read at `post.verification`. Confirm the new `verification_status == verified` through a separate GET before recording final publication.
4. Save sanitized HTTP status, post ID, submitted body SHA-256, status, and exact time. Preserve the original pending identifier as part of the negative publication history; do not erase/overwrite it.

**No credentials, challenges, private verification codes, or answer keys are recorded here.**

## Evidence and interpretation boundary

- Frozen public challenge body SHA-256 from Termux preflight: `8bbb8373b226093c4362e90d63845424f76d12a4f606dd64981787da83f6e5cf`.
- Earlier creation observation: [PUBLICATION_2026-10-11.md](PUBLICATION_2026-10-11.md) (**creation accepted only**).
- **Current verified state of the Moltbook challenge: NOT ESTABLISHED.** Most recent reported API state: `pending`.
- No participants have been evaluated, no confirmatory research outcome exists.

**Lesson:** HTTP acceptance is not publication, a nested verification challenge must be checked explicitly, and independent status checks are required. A client-side formatting/field-path error must remain in the historical record.

## Addendum — user-confirmed expiry check (later observation, 2026-10-12 UTC)

Chad ran a **read-only Termux inspection** of the original saved publication response. Reported output:

```text
Post ID: ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696
Status: pending
Challenge present: True
Expires at: 2026-10-12 01:22:03.953422+00
Expired: True
No network requests or changes made.
```

**New supported conclusion:** the **original challenge expiry time was in the past at the time of Chad's check**. No `/verify` request was made. `pending` above came from the saved original response, not from a fresh post-status GET. Therefore do not claim the server changed the post to a separate `expired` state. The earlier note's uncertainty about `expires_at` is superseded by this observed addendum, not silently deleted.

**Next intended action:** A replacement post, if explicitly initiated in Termux, must use the frozen challenge body, capture nested `post.verification`, answer within the fresh window and confirm the new post status by GET. Preserve this first failed event and honor platform post rate limits.
