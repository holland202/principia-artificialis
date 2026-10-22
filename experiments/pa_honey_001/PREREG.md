# PA-HONEY-001: does a new, unadvertised server get probed for a freshly announced PHP flaw?

**State:** REGISTERED, NOT RUN. Committed before any sensor exists and before the scheduled public disclosure of CVE-2026-109618 / CVE-2026-109619 (reported as 2026-10-22 18:00 CEST = **16:00 UTC**).
**Authors:** Direction: Chad Holland (2026-10-22). Design, sensor and classifier: Claude (Anthropic, Opus 5.5). Human review level: direction only. Everything run under this registration is **self-tested** (M10).
**Method:** [METHOD.md](../../METHOD.md), [WORKFLOW.md](../../WORKFLOW.md), [CONTROLS.md](../../CONTROLS.md) at `main`.

## W1: question

A security vendor (Previdian, public LinkedIn post, 2026-10-21) reports that its honeypots saw probes for this PHP flaw, using the `PHP_SESSION_UPLOAD_PROGRESS` upload trick, starting at 13:05 UTC on 21 October, before its announced disclosure. That is **external, vendor-reported material (C-EXT)**, used here only as motivation.

**The question:** within a fixed window, do two brand-new, never-advertised cloud servers (no DNS name, no links, no prior content) receive any request carrying that probe's signature?

## Instrument (W3)

- [`sensor.py`](sensor.py): low-interaction, standard library only. It logs every HTTP(S) request (request line, headers, up to 64 KiB of body, SHA-256 of the raw bytes) and always returns the same static page. It runs nothing a client sends, reflects nothing back, and makes no outbound connections.
- [`classify.py`](classify.py): counts the frozen signature **PHP_UPLOAD_PROGRESS**: a body containing the multipart field `PHP_SESSION_UPLOAD_PROGRESS`, or a multipart filename beginning `<?php`. Requests carrying header `X-PA-Canary` are the owner's own planted probes; they are reported separately and **never counted** toward a prediction.
- **Sensors:** two new Azure VMs in separate regions (West US 2 and Central US), ports 80 and 443 (self-signed TLS), from [`cloud-init.yaml`](cloud-init.yaml). That file downloads the two scripts at a pinned commit and refuses to start if their SHA-256 hashes differ.

## Predictions (registered before observing; M1, M2)

| ID | Prediction | Credence before running | Precisely wrong if |
|---|---|---|---|
| **H1** | Each sensor logs at least one non-canary request within **60 minutes** of its first startup line | high (about 0.9) | either sensor has no non-canary request in that window |
| **H2** | Across both sensors, at least one non-canary request matches **PHP_UPLOAD_PROGRESS** before **2026-10-29T16:00Z** (7 days after the announcement) | genuinely uncertain (about 0.5) | zero matching requests by then, **with the canary control passing** |
| H3 (door, unrun) | The same signature appears on a sensor whose IP had **no** prior traffic history | not tested here | — |

H2's credence is stated in advance so that either outcome is informative. A "no" is a valid result: the vendor's observations came from a large sensor network, and two sensors are a small sample.

## Controls (M3) and the simplest rival (M14)

- **C1, canary (anti-vacuity).** After deployment, the owner sends one request per sensor from Termux, with the vendor's published probe shape (benign body `<?php echo 1;?>`) plus header `X-PA-Canary: <nonce>`. `classify.py --expect-canary <nonce>` must exit 0 for each sensor. **If C1 fails, the instrument is INVALID and H2 cannot be scored "no".**
- **C2, sabotage.** `classify.py --sabotage` (signature removed) must exit 1, and `--selftest` must exit 0. Both run before deployment and again on the final logs.
- **Simplest rival (M14):** any hit is just broad, indiscriminate scanning, not interest in this flaw. For every hit, the analysis reports how many other requests the same source IP sent, and to which paths. No intent is inferred.

## Stopping rule and data handling

- Collection ends at **2026-11-05T12:00Z** (before the Azure credit expires on 2026-11-06), or earlier if the credit drops below $10. Logs are then copied off, and the resource group is deleted by the owner.
- **Raw logs stay private.** They are not committed to this public repository. Published results are counts from `classify.py`, plus defanged source IPs for signature hits only, after owner review.
- Sensors never connect back to, scan or contact any source. All requests are recorded passively.

## Trigger table (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | yes: n = 2 sensors and short windows; only existence claims are registered, no rates |
| Noise | C-NOISE | partly: arrivals are stochastic, so no rate or comparison claims. Classification of a fixed log is deterministic |
| Statistics | C-STAT | no rate, mean or difference is claimed; H1 and H2 are existence predictions with fixed windows |
| Evidence | C-EVID | yes: first-party logs with a per-request raw SHA-256; the vendor post is external, unverified context |
| Independence | C-INDEP | yes: self-tested; this does not replicate or validate the vendor's claims |
| External | C-EXT | yes: Previdian post and Hacker News post (2026-10-21), cited as motivation only |
| Device | C-DEVICE | yes: Azure x86 VMs, Ubuntu 24.04; no S25 claim |
| Verdict code | C-BUILD | yes: `classify.py` fails closed (missing canary → exit 1; unreadable log → exit 2) |
| Exploration | C-EXPLORE | no: the sensor ran only on loopback for self-tests before this commit; no internet traffic observed |
| Method comparison | C-METHCOMP | no |

## Pre-registration self-test (loopback only, before any deployment)

Run 2026-10-22 ~11:48Z on Python 3.13, loopback only:
- HTTP and TLS requests, an unknown method (`PROPFIND`), HEAD, a 200 KB body (kept 64 KiB, `body_truncated: true`), and a slow client holding a connection while another request was served (200).
- A probe with the published multipart shape was counted as a hit. The canary was `DETECTED`.
- A canary with an empty body was reported but did **not** match the signature. This shows the instrument can return "no".
- `--selftest` PASS, `--sabotage` FAIL (exit 1).

*Vincit Omnia Veritas.*
