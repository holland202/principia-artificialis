#!/usr/bin/env python3
"""PA-SIGMA-002 feasibility counts (C-FEAS), run before registration. Nothing here runs a mutant.

Rebuilds PA-SIGMA-001's mutant set with its own code (mutants.py, same SigmaHQ commit), keeps the
BROADENING mutants, checks they are exactly the 1,502 that PA-SIGMA-001 recorded (rule, index and
sha256), and counts what limits SigmaHQ's goodlog job before any mutant meets it:
  - scope: the goodlog job loads only rules/windows/, rules-emerging-threats/ and rules-threat-hunting/;
  - level: matchgrep.sh drops every finding of a rule whose level is "low";
  - known FPs: matchgrep.sh drops findings matching a known-FPs.csv row for the rule's id; a row whose
    pattern is ".*" drops all of them.

Usage (from the repository root, with the SigmaHQ venv's Python):
  python experiments/pa_sigma_002/feasibility.py --sigma /path/to/sigma
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
P1 = os.path.join(os.path.dirname(HERE), "pa_sigma_001")
sys.path.insert(0, P1)
import mutants as M  # noqa: E402
from feasibility import RULE_PATHS, load_runner  # noqa: E402

GOODLOG_PATHS = ("rules/windows/", "rules-emerging-threats/", "rules-threat-hunting/")
RESULTS_001 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "results", "pa_sigma_001", "results.json")


def broadening_set(sigma):
    runner = load_runner(sigma)
    cwd = os.getcwd()
    os.chdir(sigma)
    try:
        rules, _, _ = runner.find_rules_with_tests(RULE_PATHS)
    finally:
        os.chdir(cwd)
    out = []
    for r in sorted(rules, key=lambda r: r["id"]):
        path = os.path.relpath(os.path.join(sigma, r["path"]) if not os.path.isabs(r["path"]) else r["path"], sigma)
        with open(os.path.join(sigma, path), "rb") as fh:
            raw = fh.read()
        muts, why = M.enumerate_mutants(raw.decode("utf-8"))
        assert not why, (r["id"], why)
        rule = yaml.safe_load(raw)
        for k, m in enumerate(muts):
            if m["direction"] == "BROADENING":
                out.append({"rule": r["id"], "k": k, "op": m["op"], "sha": m["sha256"], "path": path,
                            "level": str(rule.get("level", "")).lower(), "text": m["text"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma", required=True)
    a = ap.parse_args()
    sigma = os.path.abspath(a.sigma)

    muts = broadening_set(sigma)
    with open(RESULTS_001) as fh:
        rec = json.load(fh)["mutants"]
    want = {(m["rule"], m["k"], m["sha"]) for m in rec if m["dir"] == "BROADENING"}
    got = {(m["rule"], m["k"], m["sha"]) for m in muts}
    print(f"0. broadening mutants rebuilt {len(got)}; PA-SIGMA-001 recorded {len(want)}; identical sets: {got == want}")

    fps = collections.defaultdict(list)
    with open(os.path.join(sigma, ".github/workflows/known-FPs.csv"), newline="") as fh:
        rd = csv.reader(fh, delimiter=";")
        next(rd)
        for row in rd:
            if row:
                fps[row[0].strip()].append(row[2] if len(row) > 2 else "")

    def bucket(m):
        if not m["path"].startswith(GOODLOG_PATHS):
            return "out_of_scope"
        if m["level"] == "low":
            return "level_low"
        if any(p == ".*" for p in fps.get(m["rule"], [])):
            return "known_fp_all"
        return "catchable"

    by = collections.Counter((bucket(m), m["op"]) for m in muts)
    rules_by = collections.defaultdict(set)
    for m in muts:
        rules_by[bucket(m)].add(m["rule"])
    print("1. broadening mutants by what limits the goodlog job (bucket x operator):")
    for b in ("out_of_scope", "level_low", "known_fp_all", "catchable"):
        row = {op: by[(b, op)] for op in M.OPERATORS}
        print(f"   {b:13s} total {sum(row.values()):5d} in {len(rules_by[b]):3d} rules | {row}")
    partial = sorted({m["rule"] for m in muts if bucket(m) == "catchable" and fps.get(m["rule"])})
    print(f"2. catchable mutants whose rule has a known-FP row with a narrower pattern: "
          f"{sum(1 for m in muts if m['rule'] in partial and bucket(m) == 'catchable')} mutants in {len(partial)} rules")
    products = collections.Counter()
    for m in muts:
        if bucket(m) == "catchable":
            ls = (yaml.safe_load(m["text"]).get("logsource") or {})
            products[str(ls.get("product", "-"))] += 1
    print(f"3. catchable mutants by logsource product: {dict(products.most_common())}")
    h = hashlib.sha256("\n".join(sorted(f"{r}:{k}:{s}" for r, k, s in got)).encode()).hexdigest()
    print(f"4. identity of the broadening set (sha256 of sorted rule:k:sha lines): {h}")


if __name__ == "__main__":
    main()
