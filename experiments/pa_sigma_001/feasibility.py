#!/usr/bin/env python3
"""PA-SIGMA-001 feasibility counts (C-FEAS). Prints counts only: no rule content, no mutant outcome.

Usage: python feasibility.py SIGMA_CHECKOUT EVTX_CHECKER JSON_CHECKER

SIGMA_CHECKOUT is a clone of SigmaHQ/sigma. Rule discovery is SigmaHQ's own
`tests/regression_tests_runner.py find_rules_with_tests`, imported, over the three rule paths its CI
uses. Mutant sites come from `mutants.py` in this directory. Sample sizes are read with python-evtx
(EVTX) or by counting non-empty lines (JSON). Nothing here runs a rule against a sample.
"""
import collections
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mutants as M  # noqa: E402

RULE_PATHS = ["rules", "rules-emerging-threats", "rules-threat-hunting"]


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_runner(sigma):
    spec = importlib.util.spec_from_file_location("sigma_runner", os.path.join(sigma, "tests", "regression_tests_runner.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sample_events(path, kind):
    if kind == "evtx":
        import Evtx.Evtx as evtx
        with evtx.Evtx(path) as log:
            return sum(1 for _ in log.records())
    with open(path, "rb") as f:
        return sum(1 for line in f if line.strip())


def main(sigma, evtx_checker, json_checker):
    sigma = os.path.abspath(sigma)
    head = subprocess.run(["git", "-C", sigma, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    print(f"SigmaHQ/sigma HEAD {head}")
    print(f"evtx-sigma-checker sha256 {sha256(evtx_checker)}")
    print(f"json_checker sha256 {sha256(json_checker)}")
    runner = load_runner(sigma)
    cwd = os.getcwd()
    os.chdir(sigma)
    try:
        rules, missing_files, missing_paths = runner.find_rules_with_tests(RULE_PATHS)
        tests = [(r, t) for r in rules for t in r["tests"]]
        print(f"rules with regression tests (runner discovery): {len(rules)}")
        print(f"tests: {len(tests)} by type {dict(collections.Counter(t.get('type') for _, t in tests))}")
        combos = collections.Counter(tuple(sorted(t.get("type") for t in r["tests"])) for r in rules)
        print(f"rules by test types: {dict(sorted(combos.items()))}")
        crlf = bom = 0
        for r in rules:
            with open(r["path"], "rb") as f:
                raw = f.read()
            crlf += b"\r" in raw
            bom += raw.startswith(b"\xef\xbb\xbf")
        print(f"rule files containing a carriage return: {crlf}; starting with a UTF-8 BOM: {bom}")
        print(f"test/stable rules without regression_tests_path (runner's own count): {len(missing_paths)}")
        mc = collections.Counter(t.get("match_count") for _, t in tests)
        print(f"match_count values: {dict(sorted(mc.items(), key=lambda kv: str(kv[0])))}")
        ev_eq, ev_more, ev_missing, sizes = 0, 0, 0, []
        for r, t in tests:
            p = t.get("path")
            if not p or not os.path.exists(p):
                ev_missing += 1
                continue
            n = sample_events(p, t.get("type"))
            sizes.append(n)
            expected = t.get("match_count") or 1
            if n <= expected:
                ev_eq += 1
            else:
                ev_more += 1
        sizes.sort()
        print(f"sample events per test: n={len(sizes)} min={sizes[0]} median={sizes[len(sizes) // 2]} max={sizes[-1]}")
        print(f"tests whose sample holds no more events than the expected match count: {ev_eq}")
        print(f"tests whose sample holds more events than the expected match count: {ev_more}")
        print(f"tests with no sample file found: {ev_missing}")
        per = collections.Counter()
        rules_with = collections.Counter()
        skipped = collections.Counter()
        cap_hits = collections.Counter()
        per_rule_total = []
        for r in rules:
            with open(r["path"], encoding="utf-8") as f:
                text = f.read()
            ms, why = M.enumerate_mutants(text)
            if why:
                skipped[why.split(":")[0]] += 1
                continue
            kinds = collections.Counter((m["op"], m["direction"]) for m in ms)
            for k, v in kinds.items():
                per[k] += v
                rules_with[k] += 1
            for op in M.OPERATORS:
                if sum(v for (o, _), v in kinds.items() if o == op) >= M.CAP:
                    cap_hits[op] += 1
            per_rule_total.append(len(ms))
        print(f"rules mutated: {len(per_rule_total)}; skipped: {sum(skipped.values())} {dict(skipped)}")
        for (op, d) in sorted(per):
            print(f"  {op:10s} {d:10s} mutants {per[(op, d)]:5d}  rules {rules_with[(op, d)]:4d}")
        print(f"rules reaching the per-operator cap of {M.CAP}: {dict(cap_hits)}")
        per_rule_total.sort()
        print(f"mutants per rule incl. controls: max {per_rule_total[-1]} (rounds needed), "
              f"total {sum(per_rule_total)}")
        json_rules = [r for r in rules if any(t.get("type") != "evtx" for t in r["tests"])]
        n_json = 0
        for r in json_rules:
            with open(r["path"], encoding="utf-8") as f:
                n_json += len(M.enumerate_mutants(f.read())[0])
        print(f"mutants incl. controls of the {len(json_rules)} rules that also have a json test: {n_json}")
    finally:
        os.chdir(cwd)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
