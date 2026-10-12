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


## Addendum — second create attempt returned original identifier (operator report)

After the read-only expiry check confirmed the original challenge deadline was past, Chad ran the previously prepared one-shot `publish_v2.py` in Termux. His terminal output reported:

```text
Original post status: pending
Source SHA-256: 8bbb8373b226093c4362e90d63845424f76d12a4f606dd64981787da83f6e5cf
Agent: veritasgate
Target: m/general
Creating ONE replacement post.
CREATE HTTP: 201
NEW POST ID: ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696
Initial status: pending
FINAL GET HTTP: 200
FINAL POST STATUS: pending
POST URL: https://www.moltbook.com/post/ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696
NOT VERIFIED — investigate before retrying
```

The returned identifier is **identical to the first pending post**, so a distinct second post **has not been established**. The v2 program displayed no verification question, consistent with its `post.verification` branch not being entered, but the saved v2 raw response has **not yet been examined**. The cause (API deduplication, replay, intermediary caching, or another behavior) is **UNKNOWN**. No successful verification was observed.

A second execution of `publish_v2.py` printed `STOP: V2 already attempted. Inspect before retrying.`, confirming the local one-shot marker blocked the third attempted run before an API write.

**Follow-up:** compare original and v2 locally saved JSON responses, printing only field names, IDs, timestamps, verification presence/expiry and digest equality—never bearer keys or verification tokens. No new publication/deletion/verification request until this read-only investigation resolves duplication status and Moltbook limitations. Preserve this addendum as a reported negative result.


## Addendum — raw-response comparison confirms existing record returned

Chad performed another **read-only** Termux inspection comparing `publish_response.json`, `publish_response_v2.json`, and `post_status_v2.json`. The output showed:

| File | Response SHA-256 | Post ID | Created | Verification |
|---|---|---|---|---|
| `publish_response.json` | `41b1670e218a5cbded273245c6b605aa3d50d003357b6361ac2402cd3387b84a` | `ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696` | `2026-10-12T01:17:03.933Z` | pending; nested challenge present |
| `publish_response_v2.json` | `ff0a99ea909bf3cb676459fb85d9568e2766b40a940d4ce904bf0ea80152bb85` | same | same | pending; no nested challenge |
| `post_status_v2.json` | `14e7031b68a79be1233d6bc4f6f1dc3fcc013df921f33c2e01bd2a01d4370c98` | same | same | pending; no nested challenge |

**Important new observation:** `publish_response_v2.json` has a top-level `already_existed` field, absent in the original creation response. That strongly supports a **server-side existing-post/duplicate response** as the reason no fresh challenge appeared. The diagnostic printed only **field names**, not the value of `already_existed` or the server's `message` / `tip`: do not assert their values until retrieved. The response bytes differ, but ID and creation timestamp match exactly.

**Decision:** No third POST, no old expired verification attempt, no deletion, and no marker reset. Before any further write, inspect `already_existed`, `message`, and `tip` locally and check the agent account status. Duplicate-content rules may constrain a replacement; prepare a clearly marked **revised** public challenge with distinct content if a replacement is permitted, with a fresh verification performed in the same session. Keep original frozen draft and evidence in GitHub.

**No new post and no verified publication established.** Raw responses remain locally on Chad's device and have not been uploaded. Previous status `pending` remains the latest GET result.

## Addendum — platform duplicate text and spam label (2026-10-12)

Chad's read-only Termux diagnostic confirmed `publish_response_v2.json` contained `success:True` and `already_existed:True`, with Moltbook's message: **"You already posted this! Here is your existing post."** Both submissions returned the original post ID and creation time. An authenticated `GET /agents/status` showed HTTP 200, `status: claimed`, `success: True`, message: **"Your agent is claimed and fully active!"** This establishes an active claimed agent at that check, not permission to bypass post moderation.

Subsequently Chad provided a browser screenshot and reported the original challenge is **labeled spam**. This is **screenshot-reported moderation**, not yet a verified API moderation field or known reason for the classification. It must not be conflated with the expired math verification and content deduplication; the relative causality is **UNKNOWN**. The screenshot itself is not archived in this repository, and no SHA-256 for that image has been recorded here.

**Current handling: STOP / REVIEW REQUIRED.** No new post, alternate-account posting, reformatted replacement, duplicate retry, or deletion should occur pending platform clarification. `POST_REVISED.md` is a preserved **unpublished draft**, explicitly [on hold](REVISED_EDITION_2026-10-12.md). For review/appeal, refer to Moltbook's [official help page](https://moltbook.com/help) (`help@moltbook.com`) with original post URL and moderation screenshot. Do not send a private API key or unpublished challenge answers. Preserve failed attempts and historical statuses rather than retroactively calling them verified or published.

## Correction — previously claimed Round 2 spam label belonged to another post

**User clarification on 2026-10-12 UTC:** The browser screenshot's red **Spam** label is attached to "RED TEAM CHALLENGE — ROUND 1: BREAK THE GATE CONTRACT" and **not** to "Smooth Brain Challenge Round 2: AI Security Claims", which is separately shown under "Up next" without a visible spam label. The earlier "platform duplicate text and spam label" addendum mistakenly associated the screenshot with Round 2. That attribution is **RETRACTED**. Preserve the earlier addendum as an error record; its spam-based stop decision for SBH-002 has been **superseded**.

**Current accurate Round 2 claim:** Original post ID `ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696` was retrievable and last observed as API `verification_status: pending`; original verification deadline expired. Second identical submission returned `already_existed:true` and reused the original ID. No verified Round 2 publication or spam flag is established. A substantively revised [POST_REVISED.md](POST_REVISED.md) is prepared, **not submitted**. The different Round 1 spam label does not establish the reason for moderation or any account-wide sanction; the account separately reported `claimed` and fully active.
