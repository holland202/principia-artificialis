#!/usr/bin/env python3
"""Prototype independent-witness HMAC attestation for thermal checkpoints.

The witness must control the secret independently of the evidence writer.
HMAC is symmetric: any key holder can forge attestations; no public verification.
"""
import argparse
import hashlib
import hmac
import json
import os
import sys

from thermal_checkpoint_v21 import checkpoint, verify_against_checkpoint
from thermal_evidence_v2 import canonical, read_jsonl

SCHEMA = "pa.thermal-witness-hmac/1"
DOMAIN = b"PA-THERMAL-WITNESS-HMAC-V1\x00"
FIELDS = {"schema", "checkpoint", "witness_id", "tag_sha256"}


def _tag(secret, witness_id, cp):
    return hmac.new(secret, DOMAIN + canonical({"checkpoint": cp, "witness_id": witness_id}).encode(), hashlib.sha256).hexdigest()


def attest(records, secret, witness_id):
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("witness secret must contain at least 32 bytes")
    if not isinstance(witness_id, str) or not witness_id:
        raise ValueError("witness id required")
    cp = checkpoint(records)
    return {"schema": SCHEMA, "checkpoint": cp, "witness_id": witness_id,
            "tag_sha256": _tag(secret, witness_id, cp)}


def verify_attestation(records, attestation, secret, expected_witness_id):
    if not isinstance(secret, bytes) or len(secret) < 32:
        return False, "INVALID_WITNESS_KEY"
    if not isinstance(attestation, dict) or set(attestation) != FIELDS or attestation.get("schema") != SCHEMA:
        return False, "ATTESTATION_SCHEMA"
    if not isinstance(expected_witness_id, str) or not expected_witness_id:
        return False, "EXPECTED_WITNESS_REQUIRED"
    if attestation["witness_id"] != expected_witness_id:
        return False, "WITNESS_MISMATCH"
    tag = attestation["tag_sha256"]
    if not isinstance(tag, str) or len(tag) != 64:
        return False, "INVALID_TAG"
    try:
        expected = _tag(secret, expected_witness_id, attestation["checkpoint"])
        if not hmac.compare_digest(expected, tag):
            return False, "WITNESS_TAG_MISMATCH"
        ok, reason = verify_against_checkpoint(records, attestation["checkpoint"])
        return (ok, "WITNESS_TAG_AND_CHECKPOINT_MATCH" if ok else reason)
    except (TypeError, ValueError, OverflowError):
        return False, "INVALID_ATTESTATION"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("attest", "verify"):
        cmd = sub.add_parser(name)
        cmd.add_argument("evidence")
        cmd.add_argument("--key-file", required=True, help="binary key file controlled by witness, never committed")
        cmd.add_argument("--witness-id", required=True)
        if name == "attest":
            cmd.add_argument("--out", required=True)
        else:
            cmd.add_argument("--attestation", required=True)
    args = ap.parse_args(argv)
    try:
        # Reject symlink key paths to reduce accidental redirection.
        if os.path.islink(args.key_file):
            raise ValueError("symlink key file refused")
        with open(args.key_file, "rb") as f:
            secret = f.read(4097)
        if len(secret) > 4096:
            raise ValueError("key too large")
        records = read_jsonl(args.evidence)
        if args.command == "attest":
            att = attest(records, secret, args.witness_id)
            with open(args.out, "x", encoding="utf-8") as f:
                f.write(canonical(att) + "\n")
            print(canonical({"created": True, "witness_id": args.witness_id,
                             "warning": "HMAC shared-secret prototype; key custody not proven"}))
            return 0
        with open(args.attestation, encoding="utf-8") as f:
            att = json.load(f)
        ok, reason = verify_attestation(records, att, secret, args.witness_id)
        print(canonical({"verified": ok, "reason": reason,
                         "scope": "symmetric-key checkpoint integrity only; witness independence not established"}))
        return 0 if ok else 1
    except (OSError, ValueError, TypeError) as exc:
        print(canonical({"verified": False, "reason": "INPUT_ERROR", "detail": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
