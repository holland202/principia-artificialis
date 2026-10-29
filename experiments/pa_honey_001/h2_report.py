#!/usr/bin/env python3
"""PA-HONEY-001 scoring report: counts and timestamps only, no IP addresses or request content.

Usage (on the sensor, after the H2 window has closed):
  python3 -I h2_report.py /opt/pa-honey/classify.py /var/lib/pa-honey-http/http80.jsonl /var/lib/pa-honey/https443.jsonl

It imports the pinned classify.py (refusing to run if its sha256 is not the registered one) and uses its own
`summarize`, `signature` and `canary`; it re-implements no signature. For each log it prints how many
requests there are, how many carry no canary, the first non-canary request, the number of PHP_UPLOAD_PROGRESS
hits in total and before the H2 deadline, the first hit, and the canaries. Source IPs are counted, never
printed: per the registration, defanged IPs of signature hits are published only after owner review.

Exit codes: 0 = report printed; 2 = classify.py is not the registered file, or a log could not be read.
"""
import hashlib
import importlib.util
import json
import sys

CLASSIFY_SHA256 = "064ee830455a921a0f976c8132d4ae89a8d11b78ed219a453490467ed02f9788"  # PREREG / cloud-init.yaml
H2_END = "2026-10-29T16:00:00"   # H2: a non-canary hit before 2026-10-29T16:00Z
H1_END = "2026-10-22T12:58:20"   # H1: within 60 min of the first startup line, 2026-10-22T11:58:20Z


def load_classify(path):
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    if digest != CLASSIFY_SHA256:
        print(json.dumps({"error": "classify.py is not the registered file", "sha256": digest}))
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("pa_honey_classify", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def report(c, path):
    with open(path, "rb") as f:
        lines = [x for x in f.read().splitlines() if x.strip()]
    recs = [json.loads(x) for x in lines]
    s = c.summarize(lines)
    non_canary = sorted(r["t_utc"] for r in recs if c.canary(r) is None)
    hits = sorted(h["t_utc"] for h in s["php_upload_progress_hits"])
    return {
        "records": len(recs),
        "first_record_utc": min((r["t_utc"] for r in recs), default=None),
        "last_record_utc": max((r["t_utc"] for r in recs), default=None),
        "non_canary_requests": len(non_canary),
        "first_non_canary_utc": non_canary[0] if non_canary else None,
        "non_canary_before_h1_end": sum(1 for t in non_canary if t < H1_END),
        "distinct_src_ips_non_canary": s["distinct_src_ips"],
        "php_upload_progress_hits": len(hits),
        "hits_before_h2_end": sum(1 for t in hits if t < H2_END),
        "first_hit_utc": hits[0] if hits else None,
        "canaries": [{"t_utc": x["t_utc"], "signature": x["signature"]} for x in s["canaries"]],
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    c = load_classify(argv[0])
    out = {"h1_end_utc": H1_END + "Z", "h2_end_utc": H2_END + "Z", "logs": {}}
    for path in argv[1:]:
        try:
            out["logs"][path] = report(c, path)
        except OSError as exc:
            out["logs"][path] = {"error": f"could not read: {exc}"}
            print(json.dumps(out, sort_keys=True))
            return 2
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
