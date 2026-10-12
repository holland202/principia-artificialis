# SBH-002 revised-edition publication plan — 2026-10-12

**Status: PREPARED / NOT SUBMITTED / NOT VERIFIED.** Human operator: Chad Holland. Text drafted with ChatGPT.  
**Frozen revised prompt:** [POST_REVISED.md](POST_REVISED.md), first committed as `58aeb1e01c683b4bf330a52684d1431633bb9841`.
**Versioning:** This is a **substantively revised edition**, not a silent second posting of identical content. Changes: a fourth synthetic replay-after-restart case (R1–R4), altered task set and **18-point** scoring, revised framing, and a transparent link to the original pending edition. The first [POST.md](POST.md) stays unchanged.
**Original publication and failures:** [PUBLICATION_2026-10-11.md](PUBLICATION_2026-10-11.md) and [VERIFICATION_GAP_2026-10-12.md](VERIFICATION_GAP_2026-10-12.md), original ID `ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696`, pending after an expired verification challenge; second attempt `already_existed:true`, same ID and creation time.
**Moltbook identity observation:** Chad's `GET /agents/status` gave `HTTP 200`, `status:claimed`, and `message: Your agent is claimed and fully active!`. This is not a guarantee of posting eligibility or bypass of moderation.

## Controlled write protocol (planned)

1. Inspect the commit-pinned revised prompt and verify its Git blob SHA against GitHub *before* sending it. No arbitrary late edits, changed data, or silent re-scoring.
2. Enforce a conservative 30-minute cooldown from both the original post creation and the last attempted submission. Ensure local single-use guard is absent for the new revision.
3. Read account status (no secrets printed); POST once to `/api/v1/posts` as `veritasgate` in `m/general`. Mark the attempt on disk **before** network writes to survive ambiguous failures.
4. Preserve raw JSON response privately; if `already_existed:true`, old ID is reused, a 429 occurs, or post ID is absent, **halt** (do not retry blindly).
5. If the new record is `pending`, extract nested `post.verification`; display the puzzle without printing its code. Chad enters a verified two-decimal answer within `expires_at`; submit at most one answer to `/api/v1/verify`. If no challenge is returned or time expires, halt; do not invent a verification or circumvent moderation.
6. GET the new post by ID, preserve sanitized response, and report exactly its observed status. Do not equate HTTP 201 with public verified publication.
7. Add a subsequent factual GitHub status record including new post ID, answer success/failure, HTTP status, UTC timestamp, published prompt hashes, and any unexpected failures. Do not commit tokens, credential files, unredacted verification codes, answer keys, or user secrets.

## Limitations

Moltbook has a content-duplicate response distinct from its post cooldown. A genuinely revised edition may still be rejected or held pending, and no API behavior is guaranteed. No automated external posting, monitoring, or scoring is claimed by this document. This is exploratory public engagement, not a controlled multi-model evaluation, independently graded benchmark, or production security assessment.
