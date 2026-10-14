#!/usr/bin/env python3
"""Evidence-bound thermal decisions v2: deterministic, standard-library-only prototype.

No hardware actions. No fabricated sensor data. No claim of hardware safety.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "pa.thermal-evidence/2"
GENESIS = "0" * 64

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)

def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class Policy:
    ceiling_c: float = 38.5
    max_age_s: float = 10.0
    min_c: float = -40.0
    max_c: float = 150.0

    def __post_init__(self):
        if not all(math.isfinite(x) for x in (self.ceiling_c, self.max_age_s, self.min_c, self.max_c)):
            raise ValueError("nonfinite policy")
        if self.max_age_s < 0 or self.min_c >= self.max_c or not self.min_c < self.ceiling_c < self.max_c:
            raise ValueError("invalid policy limits")

    def as_dict(self):
        return vars(self).copy()

def evaluate(observation, policy, now_s):
    """REFUSE: invalid or excessive temperature; DEFER: missing/stale evidence."""
    if not math.isfinite(now_s):
        raise ValueError("invalid evaluation clock")
    if observation is None:
        return {"decision": "DEFER", "reason": "NO_OBSERVATION"}
    if not isinstance(observation, dict):
        return {"decision": "REFUSE", "reason": "MALFORMED_OBSERVATION"}
    value = observation.get("temp_c")
    at = observation.get("observed_at_s")
    if type(value) not in (float, int) or type(at) not in (float, int):
        return {"decision": "REFUSE", "reason": "MALFORMED_OBSERVATION"}
    if not math.isfinite(value) or not math.isfinite(at):
        return {"decision": "REFUSE", "reason": "NONFINITE_OBSERVATION"}
    if value < policy.min_c or value > policy.max_c:
        return {"decision": "REFUSE", "reason": "OUT_OF_RANGE"}
    if at > now_s:
        return {"decision": "DEFER", "reason": "FUTURE_TIMESTAMP"}
    if now_s - at > policy.max_age_s:
        return {"decision": "DEFER", "reason": "STALE_OBSERVATION"}
    if value >= policy.ceiling_c:
        return {"decision": "REFUSE", "reason": "THERMAL_CEILING"}
    return {"decision": "ALLOW", "reason": "WITHIN_DEMO_LIMITS"}

def make_record(observation, policy, now_s, prev_hash=GENESIS, sequence=0):
    if type(sequence) is not int or sequence < 0:
        raise ValueError("invalid sequence")
    if not isinstance(prev_hash, str) or len(prev_hash) != 64 or any(c not in "0123456789abcdef" for c in prev_hash):
        raise ValueError("invalid previous hash")
    payload = {
        "schema": SCHEMA,
        "sequence": sequence,
        "prev_hash": prev_hash,
        "policy": policy.as_dict(),
        "policy_sha256": digest(policy.as_dict()),
        "observation": observation,
        "evaluated_at_s": now_s,
        "result": evaluate(observation, policy, now_s),
    }
    payload["record_sha256"] = digest(payload)
    return payload

def verify_records(records):
    """Check full record chain and independently recompute decisions; no signatures or anchoring."""
    prev = GENESIS
    for i, row in enumerate(records):
        if not isinstance(row, dict) or row.get("schema") != SCHEMA:
            return False, i, "SCHEMA"
        if row.get("sequence") != i or row.get("prev_hash") != prev:
            return False, i, "CHAIN"
        body = {k: v for k, v in row.items() if k != "record_sha256"}
        try:
            if digest(body) != row.get("record_sha256"):
                return False, i, "DIGEST"
            if digest(row["policy"]) != row["policy_sha256"]:
                return False, i, "POLICY_DIGEST"
            p = Policy(**row["policy"])
            if evaluate(row["observation"], p, row["evaluated_at_s"]) != row["result"]:
                return False, i, "DECISION"
        except (TypeError, ValueError, KeyError, OverflowError):
            return False, i, "INVALID"
        prev = row["record_sha256"]
    return True, len(records), "CHAIN_INTERNALLY_CONSISTENT"

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def cli(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    sample = sub.add_parser("evaluate", help="Evaluate explicit observation; no automatic sensor reads")
    sample.add_argument("--temp-c", type=float)
    sample.add_argument("--observed-at-s", type=float)
    sample.add_argument("--now-s", type=float, required=True)
    sample.add_argument("--ceiling-c", type=float, default=38.5)
    sample.add_argument("--max-age-s", type=float, default=10)
    sample.add_argument("--out", help="Append JSONL with hash chain; file must be new")
    verify = sub.add_parser("verify", help="Recompute and verify an entire JSONL chain")
    verify.add_argument("path")
    args = ap.parse_args(argv)
    if args.command == "verify":
        try:
            ok, index, reason = verify_records(read_jsonl(args.path))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(canonical({"verified": False, "reason": "UNREADABLE", "detail": str(exc)}))
            return 2
        print(canonical({"verified": ok, "records": index, "reason": reason,
                         "scope": "internal consistency only; no physical authenticity or rollback proof"}))
        return 0 if ok else 1
    try:
        policy = Policy(ceiling_c=args.ceiling_c, max_age_s=args.max_age_s)
        if (args.temp_c is None) != (args.observed_at_s is None):
            ap.error("supply both --temp-c and --observed-at-s, or neither")
        observation = None if args.temp_c is None else {
            "temp_c": args.temp_c, "observed_at_s": args.observed_at_s,
            "source": "cli_unverified", "authenticity": "not_established"}
        record = make_record(observation, policy, args.now_s)
        if args.out:
            # Exclusive create prevents silently extending or replacing an existing chain.
            with open(args.out, "x", encoding="utf-8") as f:
                f.write(canonical(record) + "\n")
        print(canonical(record))
        return 0
    except (ValueError, OSError) as exc:
        print(canonical({"error": str(exc)}), file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(cli())
