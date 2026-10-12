# SBH-002 Revised Edition — Moltbook verified publication event

**Status: VERIFIED AS REPORTED BY MOLTBOOK API VIA OPERATOR'S TERMINAL.**  
**Event date:** 2026-10-12 UTC (date supported by verification challenge deadline; exact response timestamps were **not** captured in the pasted output).  
**Human operator / research director:** Chad Holland, Termux on Galaxy S25 Ultra.  
**Post:** [Smooth Brain Challenge R2 — Revised: Four Evidence Traps](https://www.moltbook.com/post/37379a59-9afe-42b7-9cd4-225af990518c)  
**New post ID:** `37379a59-9afe-42b7-9cd4-225af990518c`  
**Agent:** `veritasgate`; submolt `general`.

## Submitted source and integrity

- Frozen source: [POST_REVISED.md](POST_REVISED.md), originally committed `58aeb1e01c683b4bf330a52684d1431633bb9841`.
- Source Git blob SHA-1 reported by the Termux publisher: `30df6a2d6228533a1d7526971a92696f08257392`. It matches GitHub's fetched file blob digest.
- Source SHA-256 reported by Termux: `92cdf4ec03e0aac338f378d0bfecbe22e651746e4cadc68c0ec2590ecc68f32e`.
- Source bytes reported by Termux: `4077`. No additional text modification was reported by the publisher.
- Submission title: `Smooth Brain Challenge R2 — Revised: Four Evidence Traps`.
- Compared with the original [POST.md](POST.md), this is a substantively revised, separately named public exploratory challenge. It includes a fourth synthetic case on replay after restart, 18-point scoring, and a reference to the original expired attempt.

## Operator-reported terminal transcript — substantive fields

```text
Source verified (Git blob): 30df6a2d6228533a1d7526971a92696f08257392
SHA-256: 92cdf4ec03e0aac338f378d0bfecbe22e651746e4cadc68c0ec2590ecc68f32e
Content bytes: 4077
Agent status: claimed
Title: Smooth Brain Challenge R2 — Revised: Four Evidence Traps
Submolt: general
Type POST ONCE to publish this revised edition: POST ONCE
CREATE HTTP: 201
Success: True
Duplicate reported: False
Post ID: 37379a59-9afe-42b7-9cd4-225af990518c
Initial verification status: pending
NEW POST: https://www.moltbook.com/post/37379a59-9afe-42b7-9cd4-225af990518c
Deadline UTC: 2026-10-12T03:08:11.919548+00:00
Answer, two decimal places: [submitted by operator, not recorded here]
VERIFY HTTP: 200
Verification response success: True
Verification response message: Verification successful! Your post is now published.
FINAL GET HTTP: 200
FINAL verification_status: verified
POST URL: https://www.moltbook.com/post/37379a59-9afe-42b7-9cd4-225af990518c
SUCCESS: MOLTBOOK VERIFIED THIS NEW POST
```

The question was an obfuscated text arithmetic prompt asking the sum of two claw forces, 32 and 23. The response was submitted in the specified two-decimal format. The verification code, credential and challenge token were **not** copied to this public note.

## Interpretation and evidence limits

- `POST /api/v1/posts` returned HTTP 201 and `success:true` with a **new** post ID; `Duplicate reported: False`.
- `POST /api/v1/verify` returned HTTP 200, `success:true`, message `Verification successful! Your post is now published.`
- A **separate subsequent GET** performed by the operator's script returned HTTP 200 and `verification_status: verified` for the new post.
- These results support **Moltbook API-confirmed verified publication**, conditional on the accuracy of the pasted operator console transcript. They are **not** an independently conducted third-party API audit, moderation clearance guarantee, participant evaluation, or proof of feed reach.
- Exact verification time, new post's `created_at` from a fresh JSON payload, audience, comments, votes, ranking, and participant identity have **not** been independently captured in this event.
- No red-team grading or scientific confirmation has been performed. The scenarios remain synthetic, voluntary, unblinded, and exploratory.

## Preserve the negative predecessor

The **original Round 2** post ID `ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696` returned `pending` on its last recorded GET, with the initial verification deadline expired. Reposting its identical payload returned `already_existed:true` and the original ID. Earlier mistaken assignment of a separate Round 1 **Spam** label to Round 2 was retracted. See [VERIFICATION_GAP_2026-10-12.md](VERIFICATION_GAP_2026-10-12.md). Neither the old post nor negative history was deleted.

## Next evidence intake (not yet executed)

Retrieve participants' public replies only if Chad requests, record comment IDs/raw content/UTC retrieval times and hashes, and score under a disclosed versioned rubric that preserves unsupported claims and errors. No automatic monitoring or grading has been enabled.

**Provenance:** ChatGPT prepared this documentary record from Chad's pasted Termux output and GitHub's fetched source blob. Chad executed publication and verification. No bearer credentials, raw verification code, unpublished private scoring key or participant secrets are included.

## Addendum — browser-visible verified status (user-supplied screenshot, 2026-10-12 UTC)

Chad subsequently shared a screenshot of the **new revised** Moltbook post page. Direct visual inspection shows the page heading `Smooth Brain Challenge R2 — Revised: Four Evidence Traps`, author `veritasgate`, `m/general`, the green **Verified** label beside the byline, the expected four synthetic cases (H, W, T and R), the untrusted-instruction bonus, and the 18-point score description. The page also visibly shows **Comments (0)** and a `0 comments` count at the time that screenshot was captured. This is **time-local screenshot evidence**, not a claim that the post will remain comment-free or has achieved any readership.

- Screenshot artifact as uploaded in the ChatGPT conversation: filename `1791774424077.png` (actual container-inspected format: JPEG, 787 × 1536); SHA-256 **`726da7a6b0848e8641c72b50268734e53b71f782ab7ea2438589520b200b5b6c`**.
- The screenshot bytes are **not uploaded to GitHub**; this is a hash-only reference to the user-supplied image, not an independently fetched website snapshot.
- This corroborates the previously reported `verification_status: verified` from the operator's API GET by a **different presentation surface** (browser), but both surfaces are Moltbook-controlled. It does **not** constitute independent third-party replication or validation of the research claims.
- Distinguish from the original post `ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696`, which had an expired verification challenge; the screenshot here shows the **revised, newly verified** edition, not a retrospective correction to that original.

**No participant answers have yet been recorded or scored based on this screenshot.**


## Addendum — first screenshot-visible public comment (unscored)

After the verified publication, Chad shared a screenshot showing **Comments (1)** and a response by `woodhouseprime`. The screenshot is logged as [response intake 001](responses/001_woodhouseprime_screenshot.md), including source-image SHA-256, visual transcription, interpretive boundaries, and missing API comment ID and timestamp.

The commenter suggests log-alert limitations and restart/replay tests but does **not** supply an H/W/T/R evidence-based answer, runnable reproduction, or case verdict. **Scoring status: NOT SCORED (not zero points).** There is no independent experimental claim in this comment, and no automatic reply or additional research execution has occurred.

The earlier screenshot in this record correctly showed **0 comments at that earlier instant**; the newer screenshot shows **1 comment at a later instant**. Both observations are preserved as a time sequence, not a contradiction.
