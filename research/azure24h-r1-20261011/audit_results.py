#!/usr/bin/env python3
"""Read-only R1 JSONL auditor. Standard library only; no project code executes.

Usage:
    python3 audit_results.py /path/to/runs/unattended-20261011T215619Z

The script compares data-derived counts against both the run checkpoint and
the published transcript-derived summary.json. It does not validate probe
correctness, physical effects, SHA-256 origin, or statistical independence.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def empty_project():
    return {
        "executions": 0,
        "passed": 0,
        "outcome_pass": 0,
        "exit_code_zero": 0,
        "timeouts": 0,
        "seed_slots": 0,
        "checks_reported": 0,
        "nonempty_failure_lists": 0,
        "failure_field_absent": 0,
        "mock_only_true": 0,
        "mock_only_false": 0,
        "mock_only_absent": 0,
    }


def audit(run: Path) -> tuple[dict, list[str]]:
    errors = []
    stats = defaultdict(empty_project)
    round_projects = defaultdict(Counter)
    result_path = run / "results.jsonl"
    checkpoint_path = run / "checkpoint.json"
    published_path = Path(__file__).with_name("summary.json")
    if not all(p.is_file() for p in (result_path, checkpoint_path, published_path)):
        missing = [str(p) for p in (result_path, checkpoint_path, published_path) if not p.is_file()]
        raise FileNotFoundError("missing required input: " + ", ".join(missing))

    with checkpoint_path.open(encoding="utf-8") as f:
        checkpoint = json.load(f)
    with published_path.open(encoding="utf-8") as f:
        reference = json.load(f)

    invalid_lines = 0
    valid_lines = 0
    with result_path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
                if not isinstance(r, dict) or not isinstance(r.get("parsed"), dict):
                    raise ValueError("record or parsed payload is not an object")
                project = r["project"]
                round_number = r["round"]
                if not isinstance(project, str) or not isinstance(round_number, int):
                    raise ValueError("project/round has invalid type")
                seed_count = r["seed_count"]
                checks = r["parsed"]["checks"]
                if not isinstance(seed_count, int) or not isinstance(checks, int):
                    raise ValueError("seed_count/checks has invalid type")
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as e:
                invalid_lines += 1
                if len(errors) < 25:
                    errors.append(f"invalid JSONL record at line {line_number}: {e}")
                continue

            valid_lines += 1
            p = r["parsed"]
            s = stats[project]
            s["executions"] += 1
            s["passed"] += int(r.get("status") == "PASS")
            s["outcome_pass"] += int(p.get("outcome") == "PASS")
            s["exit_code_zero"] += int(r.get("exit_code") == 0)
            s["timeouts"] += int(bool(r.get("timeout")))
            s["seed_slots"] += seed_count
            s["checks_reported"] += checks
            if "failures" not in p:
                s["failure_field_absent"] += 1
            else:
                s["nonempty_failure_lists"] += int(bool(p["failures"]))
            if p.get("mock_only") is True:
                s["mock_only_true"] += 1
            elif p.get("mock_only") is False:
                s["mock_only_false"] += 1
            else:
                s["mock_only_absent"] += 1
            round_projects[round_number][project] += 1

    total = sum(s["executions"] for s in stats.values())
    passed = sum(s["passed"] for s in stats.values())
    timeouts = sum(s["timeouts"] for s in stats.values())
    rounds_four = sum(sum(projects.values()) == 4 for projects in round_projects.values())
    duplicate_project_rounds = sum(
        sum(n - 1 for n in projects.values() if n > 1)
        for projects in round_projects.values()
    )
    output = {
        "valid_records": valid_lines,
        "invalid_records": invalid_lines,
        "unique_rounds": len(round_projects),
        "rounds_with_four_records": rounds_four,
        "duplicate_project_round_occurrences": duplicate_project_rounds,
        "projects": dict(sorted(stats.items())),
    }

    campaign = reference["campaign"]
    comparisons = {
        "project_executions": total,
        "passed": passed,
        "nonzero_exit_codes": total - sum(s["exit_code_zero"] for s in stats.values()),
        "timeouts": timeouts,
        "invalid_jsonl_records": invalid_lines,
        "rounds_complete": len(round_projects),
        "seed_slots": sum(s["seed_slots"] for s in stats.values()),
        "internal_checks_reported": sum(s["checks_reported"] for s in stats.values()),
    }
    for field, actual in comparisons.items():
        if campaign[field] != actual:
            errors.append(f"summary mismatch {field}: published={campaign[field]!r} actual={actual!r}")
    if rounds_four != len(round_projects):
        errors.append("not every round has four records")
    if duplicate_project_rounds:
        errors.append(f"duplicate project-round records: {duplicate_project_rounds}")
    if set(round_projects) != set(range(campaign["rounds_complete"])):
        errors.append("round identifiers are not exactly 0..rounds_complete-1")

    expected_projects = {p["project"]: p for p in reference["projects"]}
    if set(expected_projects) != set(stats):
        errors.append(f"project names differ: published={sorted(expected_projects)} actual={sorted(stats)}")
    for name, actual in stats.items():
        expected = expected_projects.get(name, {})
        for field in ("executions", "passed", "exit_code_zero", "timeouts",
                      "seed_slots", "checks_reported", "nonempty_failure_lists",
                      "mock_only_true", "mock_only_false", "mock_only_absent"):
            if expected.get(field) != actual[field]:
                errors.append(f"{name}.{field}: published={expected.get(field)!r} actual={actual[field]!r}")
        if actual["outcome_pass"] != actual["executions"]:
            errors.append(f"{name}: some parsed outcomes are not PASS")
        if actual["failure_field_absent"]:
            errors.append(f"{name}: {actual['failure_field_absent']} records lack a failures field")

    for field, value in (
        ("rounds_complete", len(round_projects)),
        ("project_runs", total),
        ("passed", passed),
        ("blocked_or_error", total - passed),
        ("findings", campaign["findings_reported"]),
    ):
        if checkpoint.get(field) != value:
            errors.append(f"checkpoint mismatch {field}: checkpoint={checkpoint.get(field)!r} expected={value!r}")
    for field in ("started_utc", "deadline_utc", "finished_utc", "state"):
        key = "checkpoint_state" if field == "state" else field
        if checkpoint.get(field) != campaign.get(key):
            errors.append(f"checkpoint mismatch {field}: checkpoint={checkpoint.get(field)!r} published={campaign.get(key)!r}")
    if invalid_lines:
        errors.append(f"{invalid_lines} malformed records")
    if total == 0:
        errors.append("no records found")

    return output, errors


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        output, errors = audit(Path(sys.argv[1]))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"INPUT_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(output, sort_keys=True, indent=2))
    for error in errors:
        print("MISMATCH:", error, file=sys.stderr)
    print("ACCOUNTING_MATCH" if not errors else "ACCOUNTING_MISMATCH", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
