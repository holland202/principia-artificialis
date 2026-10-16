#!/usr/bin/env python3
"""SRR-1 offline structural checker. Does not authorize actions or authenticate Chad.

Run: python3 research-relay/scripts/validate_relay.py research-relay
Requires Python 3.9+ standard library only.
"""
import json
import re
import sys
from pathlib import Path

REQUIRED = {
    "task_id", "title", "repository", "source_commit", "authorization",
    "assigned_to", "stage", "execution_status", "claim_status",
    "preregistration", "evidence_manifest", "independent_review", "review_ref",
    "chad_approval_required", "chad_decision_ref",
}
AUTH = {"READ_ONLY", "PROPOSE", "TEST_APPROVED", "PUBLISH_APPROVED"}
STAGE = {"AWAITING_CHAD_DECISION", "PROPOSED", "READY_FOR_TEST", "IN_REVIEW", "CLOSED"}
EXECUTION = {"NOT_STARTED", "RUNNING", "COMPLETE", "FAILED", "BLOCKED", "INCOMPLETE"}
CLAIM = {"UNVERIFIED", "REPORTED", "SUPPORTED_WITHIN_SCOPE", "REFUTED_KEPT", "INCOMPLETE"}
REVIEW = {"NOT_STARTED", "SELF_REVIEWED", "SAME_VENDOR_REVIEW", "INDEPENDENTLY_REPRODUCED"}
CODE_BLOCK = re.compile(r"(?ms)^~~~json[ \t]*\n(.*?)\n~~~[ \t]*$")
SHA40 = re.compile(r"[0-9a-f]{40}")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
TASK_ID = re.compile(r"SRR-[0-9]{3}")


class DuplicateField(ValueError):
    pass


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateField("duplicate JSON field: " + key)
        result[key] = value
    return result


def check_task(path: Path, root: Path):
    errors = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return ["unable to read task: " + str(exc)]
    blocks = CODE_BLOCK.findall(text)
    if len(blocks) != 1:
        return ["expected exactly one fenced ~~~json task metadata block"]
    try:
        obj = json.loads(blocks[0], object_pairs_hook=no_duplicates)
    except (ValueError, json.JSONDecodeError) as exc:
        return ["invalid JSON metadata: " + str(exc)]
    if not isinstance(obj, dict):
        return ["task metadata must be an object"]
    if set(obj) != REQUIRED:
        errors.append("field mismatch: missing=%s extra=%s" %
                      (sorted(REQUIRED - set(obj)), sorted(set(obj) - REQUIRED)))

    def val(name):
        return obj.get(name)

    task_id = val("task_id")
    if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
        errors.append("invalid task_id")
    elif path.name != task_id + ".md":
        errors.append("task_id does not match filename")
    if not isinstance(val("title"), str) or not val("title").strip():
        errors.append("missing title")
    if not isinstance(val("repository"), str) or not REPO.fullmatch(val("repository")):
        errors.append("invalid owner/repo")
    sha = val("source_commit")
    if sha is not None and (not isinstance(sha, str) or not SHA40.fullmatch(sha)):
        errors.append("source_commit must be null or lowercase full 40-character SHA")
    for name, allowed in (("authorization", AUTH), ("stage", STAGE),
                          ("execution_status", EXECUTION), ("claim_status", CLAIM),
                          ("independent_review", REVIEW)):
        value = val(name)
        if not isinstance(value, str) or value not in allowed:
            errors.append("invalid " + name)
    if val("assigned_to") is not None and val("assigned_to") not in ("ChatGPT", "Claude", "Chad"):
        errors.append("invalid assigned_to")
    if val("chad_approval_required") is not True:
        errors.append("chad_approval_required must be true")
    for name in ("preregistration", "evidence_manifest", "review_ref", "chad_decision_ref"):
        value = val(name)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(name + " must be null or nonblank string")

    # Pilot limitation: non-READ_ONLY is ALWAYS blocked until a separately reviewed
    # authenticated approval scheme is implemented. A markdown approval is not enough.
    if val("authorization") != "READ_ONLY":
        errors.append("non-READ_ONLY permission unsupported in pilot v0.1")
    if val("assigned_to") is not None:
        errors.append("active assignment unsupported in pilot v0.1")
    if val("chad_decision_ref") is not None:
        errors.append("approval reference unsupported in pilot v0.1")
    if val("execution_status") != "NOT_STARTED":
        errors.append("execution claimed in dormant pilot task")
    if val("stage") != "AWAITING_CHAD_DECISION":
        errors.append("active workflow stage unsupported in pilot v0.1")
    if val("claim_status") != "UNVERIFIED":
        errors.append("claim promoted in dormant pilot task")
    if val("independent_review") != "NOT_STARTED":
        errors.append("independent review claimed in dormant pilot task")
    if val("review_ref") is not None:
        errors.append("review reference on dormant pilot task")
    if val("preregistration") is not None or val("evidence_manifest") is not None:
        errors.append("evidence/preregistration reference on dormant pilot task")

    return errors


def validate(root: Path):
    tasks = sorted((root / "TASKS").glob("SRR-*.md"))
    errors = []
    if not tasks:
        return ["no task records found"]
    seen = set()
    for path in tasks:
        name = path.name
        if name in seen:
            errors.append("duplicate task filename: " + name)
        seen.add(name)
        for item in check_task(path, root):
            errors.append(str(path.relative_to(root)) + ": " + item)
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print("Usage: validate_relay.py [path-to-research-relay]", file=sys.stderr)
        return 2
    root = Path(args[0]) if args else Path(__file__).resolve().parents[1]
    errors = validate(root)
    for problem in errors:
        print("INVALID: " + problem)
    if errors:
        print("STRUCTURAL_CHECK_FAILED: %d issue(s)" % len(errors))
        return 1
    print("STRUCTURAL_CHECK_OK: %d task(s); READ_ONLY only; no action authorized" %
          len(list((root / "TASKS").glob("SRR-*.md"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
