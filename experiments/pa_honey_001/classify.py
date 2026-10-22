#!/usr/bin/env python3
"""PA-HONEY-001 classifier: counts registered signatures in sensor JSONL logs. Standard library only.

Signatures (frozen at registration):
  PHP_UPLOAD_PROGRESS  a request whose body contains the multipart field name PHP_SESSION_UPLOAD_PROGRESS,
                       or whose body/request line contains a multipart filename beginning with "<?php".
  CANARY               the request carries header X-PA-Canary: <value>. Canary requests are the owner's own
                       planted probes (anti-vacuity control). They are reported separately and never counted
                       toward a prediction.

Exit codes: 0 = summary printed; 1 = --selftest/--sabotage detected a broken instrument or the canary was
missing when --expect-canary was given; 2 = input could not be read.
"""
import argparse
import base64
import json
import re
import sys
from collections import Counter

FIELD = re.compile(rb'name="?PHP_SESSION_UPLOAD_PROGRESS"?', re.I)
PHPNAME = re.compile(rb'filename="?\s*<\?php', re.I)


def signature(rec, disabled=False):
    if disabled:  # sabotage switch: the instrument with its signature removed
        return False
    body = base64.b64decode(rec.get("body_b64", ""))
    line = rec.get("request_line", "").encode("latin-1", "replace")
    return bool(FIELD.search(body) or PHPNAME.search(body) or PHPNAME.search(line))


def canary(rec):
    for k, v in rec.get("headers", []):
        if k.lower() == "x-pa-canary":
            return v
    return None


def summarize(lines, disabled=False):
    total, hits, canaries, ips, first = 0, [], [], set(), None
    for raw in lines:
        if not raw.strip():
            continue
        rec = json.loads(raw)
        total += 1
        first = first or rec["t_utc"]
        c = canary(rec)
        sig = signature(rec, disabled)
        if c is not None:
            canaries.append({"t_utc": rec["t_utc"], "canary": c, "signature": sig, "sensor": rec["sensor"]})
            continue
        ips.add(rec["src_ip"])
        if sig:
            hits.append({"t_utc": rec["t_utc"], "sensor": rec["sensor"], "src_ip": rec["src_ip"],
                         "request_line": rec["request_line"], "raw_sha256": rec["raw_sha256"]})
    return {"requests": total, "distinct_src_ips": len(ips), "first_request_utc": first,
            "php_upload_progress_hits": hits, "canaries": canaries}


SAMPLE_BODY = (b'--B\r\nContent-Disposition: form-data; name="PHP_SESSION_UPLOAD_PROGRESS"\r\n\r\nx\r\n'
               b'--B\r\nContent-Disposition: form-data; name="f"; filename="<?php echo 1;?>.txt"\r\n\r\nz\r\n--B--\r\n')


def _fixture(body, headers):
    return json.dumps({"t_utc": "2026-10-22T00:00:00.000+00:00", "sensor": "selftest", "src_ip": "192.0.2.1",
                       "request_line": "POST / HTTP/1.1", "headers": headers, "raw_sha256": "0" * 64,
                       "body_b64": base64.b64encode(body).decode()})


def selftest(disabled=False):
    lines = [_fixture(SAMPLE_BODY, [["Content-Type", "multipart/form-data; boundary=B"]]),
             _fixture(b"", [["User-Agent", "scanner"]]),
             _fixture(SAMPLE_BODY, [["X-PA-Canary", "selftest-nonce"]])]
    s = summarize(lines, disabled)
    ok = (len(s["php_upload_progress_hits"]) == 1 and len(s["canaries"]) == 1
          and s["canaries"][0]["signature"] is True and s["requests"] == 3)
    return ok, s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sabotage", action="store_true", help="run the selftest with the signature disabled")
    ap.add_argument("--expect-canary", help="exit 1 unless this canary value is present AND matched the signature")
    a = ap.parse_args(argv)
    if a.selftest or a.sabotage:
        ok, s = selftest(disabled=a.sabotage)
        print("SELFTEST", "PASS" if ok else "FAIL", json.dumps(s, sort_keys=True))
        return 0 if ok else 1
    lines = []
    try:
        for path in a.logs:
            with open(path, "rb") as fp:
                lines.extend(fp.read().splitlines())
    except OSError as exc:
        print("COULD NOT READ:", exc)
        return 2
    s = summarize(lines)
    print(json.dumps(s, indent=1, sort_keys=True))
    if a.expect_canary:
        found = [c for c in s["canaries"] if c["canary"] == a.expect_canary and c["signature"]]
        print("CANARY", "DETECTED" if found else "MISSING", a.expect_canary)
        return 0 if found else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
