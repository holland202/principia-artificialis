# SBH-002 publication event — Moltbook Round 2

**Record status:** API acceptance reported from Chad Holland's S25 Ultra Termux output, 2026-10-11. **Public readability:** ACCESS_UNVERIFIED. **Scoring:** NOT STARTED. This record is not a confirmatory research result.

## Source evidence — human-supplied terminal transcript

- Operator: Chad Holland, Termux on Samsung Galaxy S25 Ultra.
- Agent credential name (no key disclosed): `veritasgate`.
- API request: single `POST https://www.moltbook.com/api/v1/posts` executed by operator.
- Target submolt: `general`.
- Submitted title: `Smooth Brain Challenge Round 2: AI Security Claims`.
- API HTTP status reported: **201**.
- JSON `success` reported: **true**.
- Post ID reported: `ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696`.
- Post URL constructed from that ID: https://www.moltbook.com/post/ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696
- Verification object returned by the script: **not returned**. This is not proof that there are no platform-side verification requirements.
- Local response file: `/data/data/com.termux/files/home/moltbook-challenges/sbh-002/publish_response.json` (not uploaded or inspected; secrets should be redacted before any upload).
- Canonical challenge text: [POST.md](POST.md), first committed at `998567d4f87003d77f041aa0d062eee95358e85d`.
- Preflight-verified Git blob SHA-1: `5fea1c91f3b72f53f43497179532147a4e382b37`.
- Preflight and submission-script expected source SHA-256: `8bbb8373b226093c4362e90d63845424f76d12a4f606dd64981787da83f6e5cf`.
- Preflight output: `CHALLENGE VERIFIED`, `Bytes: 3850`, `Credentials: FOUND`, `Agent: veritasgate`, `Publication: NOT ATTEMPTED`. Later operator submission output: `HTTP: 201`, `Success reported: True`, `Post ID: ef4e2bad-dfd2-49fd-a7a8-bdb0cf860696`, `Verification object: not returned`.
- Publication request JSON payload digest: **NOT AVAILABLE** from terminal excerpt. Script wrote it into a local `publish_attempt.json`, but that artifact has not been inspected; do not infer the digest.
- UTC publication timestamp: **NOT AVAILABLE** in the returned excerpt. Date known only as 2026-10-11 from this conversation's current date.
- Raw response body, independent public GET, comment counts, comment text, participant identities: **NOT RETRIEVED**.

## Interpretation and limitations

HTTP 201 and `success:true` support the conclusion that the API **accepted creation of a post** with the returned identifier. They do **not** alone prove public visibility, indexing, comment availability or that any challenge evaluation succeeded.

A public GET from this research environment could not be completed. Public readability remains `ACCESS_UNVERIFIED` until the operator or a second observer checks the permalink or public API and records the response.

No automated monitoring, scoring or model invocation was enabled. No token or private answer key has been committed. The source challenge remains exploratory and openly visible; it is not a blinded or preregistered benchmark.

## Next evidence request

Record a separately observed public GET or accessible screenshot, UTC time, permitted response fields (post ID, title, author, submolt), and any comments as exact copies. Save raw local evidence with digest and avoid leaking authentication or private keys. Preserve unexpected results rather than rewriting this event.
