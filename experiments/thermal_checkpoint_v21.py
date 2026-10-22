#!/usr/bin/env python3
"""Thermal v2.1: independently supplied checkpoint validation.

A checkpoint is trustworthy only if retained outside the evidence writer's control.
This module never asserts external anchoring, identity, or signature authenticity.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from thermal_evidence_v2 import GENESIS, SCHEMA, canonical, digest, read_jsonl, verify_records

CHECKPOINT_SCHEMA = "pa.thermal-checkpoint/1"
CHECKPOINT_FIELDS = {"schema", "evidence_schema", "record_count", "last_record_sha256", "checkpoint_sha256"}


def checkpoint(records):
    ok, count, reason = verify_records(records)
    if not ok:
        raise ValueError("cannot checkpoint invalid evidence: " + reason)
    body = {
        "schema": CHECKPOINT_SCHEMA,
        "evidence_schema": SCHEMA,
        "record_count": count,
        "last_record_sha256": records[-1]["record_sha256"],
    }
    return {**body, "checkpoint_sha256": digest(body)}


def verify_against_checkpoint(records, expected):
    """Compare against a separately retained checkpoint; reject truncation/extension.

    Caller must establish the checkpoint's provenance via an independent channel.
    """
    if not isinstance(expected, dict) or set(expected) != CHECKPOINT_FIELDS:
        return False, "CHECKPOINT_SCHEMA"
    body = {k: v for k, v in expected.items() if k != "checkpoint_sha256"}
    if expected["schema"] != CHECKPOINT_SCHEMA or expected["evidence_schema"] != SCHEMA:
        return False, "CHECKPOINT_SCHEMA"
    if type(expected["record_count"]) is not int or expected["record_count"] <= 0:
        return False, "CHECKPOINT_COUNT"
    try:
        if digest(body) != expected["checkpoint_sha256"]:
            return False, "CHECKPOINT_DIGEST"
    except (TypeError, ValueError, OverflowError):
        return False, "CHECKPOINT_INVALID"
    ok, count, reason = verify_records(records)
    if not ok:
        return False, "EVIDENCE_" + reason
    if count != expected["record_count"]:
        return False, "RECORD_COUNT_MISMATCH"
    if records[-1]["record_sha256"] != expected["last_record_sha256"]:
        return False, "HEAD_MISMATCH"
    return True, "CHECKPOINT_MATCH_UNAUTHENTICATED"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    create = sub.add_parser("checkpoint")
    create.add_argument("evidence")
    create.add_argument("output")
    verify = sub.add_parser("verify")
    verify.add_argument("evidence")
    verify.add_argument("checkpoint")
    args = ap.parse_args(argv)
    try:
        rows = read_jsonl(args.evidence)
        if args.command == "checkpoint":
            cp = checkpoint(rows)
            # Exclusive create avoids overwriting previously retained checkpoints.
            with open(args.output, "x", encoding="utf-8") as f:
                f.write(canonical(cp) + "\n")
            print(canonical({"created": True, "checkpoint": cp, "warning": "Store checkpoint independently of evidence writer"}))
            return 0
        with open(args.checkpoint, encoding="utf-8") as f:
            cp = json.load(f)
        ok, reason = verify_against_checkpoint(rows, cp)
        print(canonical({"verified": ok, "reason": reason,
                         "scope": "checkpoint equality only; no authenticity without independent trust"}))
        return 0 if ok else 1
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(canonical({"verified": False, "reason": "INVALID_INPUT", "detail": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
