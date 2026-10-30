#!/usr/bin/env python3
"""PA-SIGMA-003 look sample (C-SYNTH), written after run 1. EXPLORATORY, not registered.

Names three arm-A FLAGGED, three arm-B FLAGGED and three unflagged SURV mutants, as the registration says. The
registration fixed the counts, not the rule for choosing; this one was set before anyone looked at a diff:
  - arm A FLAGGED: the first three by mutant key, one per rule;
  - arm B FLAGGED: the first by key for each reason a house-style edit was flagged (|all kept, User field,
    duplicate detection), so each mechanism is seen once;
  - SURV, not flagged in either arm: the first by key for each operator (DROP_VALUE, DROP_FIELD, NEVER_SEL).
Identities go to results/pa_sigma_003/look_sample.json. The diffs (SigmaHQ rule text, original vs arm A vs arm B)
go to the path given with --diffs, outside the repository, for Chad to look at.

Usage: python experiments/pa_sigma_003/posthoc.py --sigma SIGMA --diffs /path/outside/repo.md
"""
import argparse
import difflib
import importlib.util
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma", required=True)
    ap.add_argument("--diffs", required=True)
    a = ap.parse_args()
    f3 = _load("pa_sigma_003_feasibility", os.path.join(HERE, "feasibility.py"))
    with open(os.path.join(ROOT, "results", "pa_sigma_003", "results.json")) as fh:
        res = json.load(fh)
    flagged = res["flagged"]
    items = f3.build_items(os.path.abspath(a.sigma))
    A = sorted((i for i in items if i["kind"] == "MUTANT" and i["arm"] == "A"), key=lambda i: i["key"])
    B = {i["key"]: i for i in items if i["kind"] == "MUTANT" and i["arm"] == "B"}
    def arm_b_flags(i):
        b = B.get(i["key"])
        return flagged.get(b["id"], {}) if b else flagged.get(i["id"], {})

    pick, rules_seen = [], set()
    for i in A:
        if i["id"] in flagged and i["rule"] not in rules_seen and len(rules_seen) < 3:
            rules_seen.add(i["rule"])
            pick.append(("arm A FLAGGED", i))
    for reason in ("SigmahqInvalidAllModifierIssue", "SigmahqFieldUserIssue", "test_duplicate_detections"):
        hit = next((i for i in A if any(reason in r for r in arm_b_flags(i).values())), None)
        if hit:
            pick.append((f"arm B FLAGGED ({reason})", hit))
    for op in ("DROP_VALUE", "DROP_FIELD", "NEVER_SEL"):
        hit = next((i for i in A if i["op"] == op and i["surv"] and i["id"] not in flagged and not arm_b_flags(i)), None)
        if hit:
            pick.append(("SURV, not flagged in either arm", hit))
    look = []
    with open(a.diffs, "w") as out:
        out.write("# PA-SIGMA-003 look sample\n\nOriginal rule (re-dumped so layout does not show as change) vs arm A "
                  "vs arm B. Reasons are the checks' own issue or test names.\n\n")
        for label, i in pick:
            with open(os.path.join(a.sigma, i["rel"]), encoding="utf-8") as fh:
                orig = f3.M._dump(yaml.safe_load(fh.read()))
            b = B.get(i["key"])
            row = {"label": label, "key": i["key"], "op": i["op"], "path": i["rel"],
                   "arm_a_flags": flagged.get(i["id"], {}), "arm_b_flags": flagged.get(b["id"], {}) if b else "same text as arm A"}
            look.append(row)
            out.write(f"## {label}: {i['op']} on {i['rel']}\n\nkey `{i['key']}`; arm A flags {row['arm_a_flags']}; "
                      f"arm B flags {row['arm_b_flags']}\n\n```diff\n")
            out.write("\n".join(difflib.unified_diff(orig.splitlines(), i["text"].splitlines(), "original", "arm A",
                                                     n=2, lineterm="")) + "\n")
            if b:
                out.write("\n".join(difflib.unified_diff(i["text"].splitlines(), b["text"].splitlines(), "arm A",
                                                         "arm B", n=1, lineterm="")) + "\n")
            out.write("```\n\n")
    with open(os.path.join(ROOT, "results", "pa_sigma_003", "look_sample.json"), "w") as fh:
        json.dump(look, fh, indent=1)
    print(f"look sample: {[(r['label'], r['key'][:13]) for r in look]}; diffs in {a.diffs}")


if __name__ == "__main__":
    sys.exit(main())
