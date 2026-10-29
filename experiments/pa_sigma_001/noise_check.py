#!/usr/bin/env python3
"""PA-SIGMA-001 same-input noise check (C-NOISE). Runs SigmaHQ's own runner functions on the UNMUTATED
rules three times and reports whether any rule's result differs between runs. Prints counts only.

Usage: python noise_check.py SIGMA_CHECKOUT EVTX_CHECKER JSON_CHECKER   (the `sigma` CLI must be on PATH)

The EVTX path is `run_evtx_batch` (one checker call for all 471 EVTX tests); the JSON path is
`run_json_checker` (sigma convert, then json_checker). Both are imported from
`tests/regression_tests_runner.py`, not copied.
"""
import collections
import contextlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from feasibility import RULE_PATHS, load_runner  # noqa: E402

RUNS = 3
TEMP_PATH_FIELDS = ("File", "RulePath")  # the runner stages files in a new temporary directory per call
UNORDERED_FIELDS = ("MatchStrings",)  # a list whose order the checker does not fix between runs


def _normalized(line):
    obj = json.loads(line)
    for key in TEMP_PATH_FIELDS:
        obj.pop(key, None)
    for key in UNORDERED_FIELDS:
        if isinstance(obj.get(key), list):
            obj[key] = sorted(json.dumps(x, sort_keys=True) for x in obj[key])
    return json.dumps(obj, sort_keys=True)


def _differing_fields(a, b):
    x, y = json.loads(a), json.loads(b)
    return {k for k in set(x) | set(y) if x.get(k) != y.get(k)}


def main(sigma, evtx_checker, json_checker):
    sigma, evtx_checker, json_checker = (os.path.abspath(p) for p in (sigma, evtx_checker, json_checker))
    runner = load_runner(sigma)
    os.chdir(sigma)
    rules, _, _ = runner.find_rules_with_tests(RULE_PATHS)
    evtx_items = [(r, i, t) for r in rules for i, t in enumerate(r["tests"]) if t.get("type") == "evtx"]
    json_items = [(r, i, t) for r in rules for i, t in enumerate(r["tests"]) if t.get("type") != "evtx"]
    counts, lines, json_out = [], [], []
    for k in range(RUNS):
        with contextlib.redirect_stdout(io.StringIO()):
            m = runner.run_evtx_batch(evtx_items, evtx_checker, "tests/thor.yml")
        if m is None:
            print(f"run {k + 1}: evtx batch FAILED")
            return 2
        counts.append({r["id"]: len(m.get(r["id"], [])) for r, _, _ in evtx_items})
        lines.append({rid: v for rid, v in m.items()})
        jo = {}
        for r, i, t in json_items:
            with contextlib.redirect_stdout(io.StringIO()):
                ok, out = runner.run_json_checker(t["type"], r["path"], r["id"], t, json_checker)
            jo[(r["id"], i)] = (ok, 0 if not out else out.count("\n    ") + 1)
        json_out.append(jo)
        print(f"run {k + 1}: evtx tests {len(counts[-1])}, match lines {sum(counts[-1].values())}, "
              f"tests with zero matches {sum(1 for v in counts[-1].values() if v == 0)}; "
              f"json tests {len(jo)}, passing {sum(1 for ok, _ in jo.values() if ok)}, "
              f"match lines {sum(n for _, n in jo.values())}")
    diff_counts = sum(1 for rid in counts[0] if len({c[rid] for c in counts}) > 1)
    rids = sorted(set().union(*lines))
    raw = sum(1 for rid in rids if len({tuple(sorted(l.get(rid, []))) for l in lines}) > 1)
    norm = sum(1 for rid in rids
               if len({tuple(sorted(_normalized(x) for x in l.get(rid, []))) for l in lines}) > 1)
    fields = set()
    for rid in rids:
        for a, b in zip(sorted(lines[0].get(rid, []), key=_normalized), sorted(lines[1].get(rid, []), key=_normalized)):
            fields |= _differing_fields(a, b)
    diff_json = sum(1 for key in json_out[0] if len({j[key] for j in json_out}) > 1)
    print(f"evtx tests whose match count differs across the {RUNS} runs: {diff_counts}")
    print(f"evtx tests whose match lines differ across the {RUNS} runs, as printed: {raw}")
    print(f"fields that differ between run 1 and run 2 in any match line: {sorted(fields)}")
    print(f"evtx tests whose match lines differ with {list(TEMP_PATH_FIELDS)} removed and "
          f"{list(UNORDERED_FIELDS)} sorted: {norm}")
    print(f"json tests whose (pass, match count) differs across the {RUNS} runs: {diff_json}")
    dist = collections.Counter(counts[0].values())
    print(f"evtx match count distribution (run 1): {dict(sorted(dist.items()))}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
