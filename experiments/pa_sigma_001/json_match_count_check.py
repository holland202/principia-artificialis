#!/usr/bin/env python3
"""PA-SIGMA-001 post-hoc check (EXPLORATORY; prompted by run 1, not registered): can SigmaHQ's JSON
regression path fail when a rule does not match?

Usage: python json_match_count_check.py SIGMA_CHECKOUT JSON_CHECKER   (the `sigma` CLI must be on PATH)

For each of the three rules with a JSON test, it writes a copy of the rule whose condition is ANDed with a
selection that cannot match, and calls the runner's own `run_json_checker` on it. It also runs json_checker
directly on the literal expressions `true` and `false`, and shows which of its output lines the runner's
counting rule keeps: `ln.endswith("MATCH")` (tests/regression_tests_runner.py line 384).
Prints verdicts, counts and json_checker's raw output lines; no rule text and no event content.
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from feasibility import RULE_PATHS, load_runner  # noqa: E402

NEVER = "PA-SIGMA-001-NEVER-MATCH-7f3a"


def main(sigma, json_checker):
    sigma, json_checker = os.path.abspath(sigma), os.path.abspath(json_checker)
    runner = load_runner(sigma)
    os.chdir(sigma)
    rules, _, _ = runner.find_rules_with_tests(RULE_PATHS)
    json_tests = [(r, t) for r in rules for t in r["tests"] if t.get("type") != "evtx"]
    print(f"rules with a JSON test: {len({r['id'] for r, _ in json_tests})}; JSON tests: {len(json_tests)}")

    print("\njson_checker on literal expressions, and what the runner's counting rule keeps:")
    sample = json_tests[0][1]["path"]
    for expr in ("true", "false"):
        out = subprocess.run([json_checker, "--event", sample, "--expr", expr, "--test-type", "json"],
                             capture_output=True, text=True, check=True).stdout
        lines = out.splitlines()
        kept = [ln for ln in lines if ln.endswith("MATCH")]
        print(f"  expr {expr!r}: output {lines}; lines the runner counts as matches: {len(kept)}")

    print("\nthe runner's own run_json_checker on each rule, unchanged and with a never-matching condition:")
    with tempfile.TemporaryDirectory() as tmp:
        for r, t in json_tests:
            with open(r["path"], encoding="utf-8") as f:
                rule = yaml.safe_load(f)
            det = rule["detection"]
            names = [k for k in det if k not in ("condition", "timeframe")]
            field = None
            for n in names:
                sel = det[n]
                for m in (sel if isinstance(sel, list) else [sel]):
                    if isinstance(m, dict):
                        field = field or next((k.split("|")[0] for k, v in m.items() if isinstance(v, (str, list))), None)
            det["pa_never"] = {field: NEVER}
            det["condition"] = f"({det['condition']}) and pa_never"
            path = os.path.join(tmp, f"{r['id']}.yml")
            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(rule, f, sort_keys=False)
            for label, p in (("unchanged", r["path"]), ("never-matching", path)):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    ok, out = runner.run_json_checker(t["type"], p, r["id"], t, json_checker)
                n = 0 if not out else out.count("\n    ") + 1
                print(f"  {r['id']} {label:15s}: runner verdict {'PASS' if ok else 'FAIL'}, "
                      f"counted matches {n}, match_count {t.get('match_count')}, lines counted {out.split(chr(10)) if out else []}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
