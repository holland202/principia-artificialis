#!/usr/bin/env python3
"""PA-SIGMA-004 look sample (C-SYNTH), written after run 1. EXPLORATORY, not registered.

Names three B4 files, the first by mutant key for each operator, as the registration says. A person compares each
with its original rule file: is this how a contributor could plausibly have written the edit? Identities go to
results/pa_sigma_004/look_sample.json; the diffs (SigmaHQ rule text, original bytes vs B4) go to --diffs, outside
the repository.

Usage: python experiments/pa_sigma_004/posthoc.py --sigma SIGMA --diffs /path/outside/repo.md
"""
import argparse
import difflib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma", required=True)
    ap.add_argument("--diffs", required=True)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("pa_sigma_004_feasibility", os.path.join(HERE, "feasibility.py"))
    f4 = importlib.util.module_from_spec(spec)
    sys.modules["pa_sigma_004_feasibility"] = f4
    spec.loader.exec_module(f4)
    items = sorted((i for i in f4.build_items(os.path.abspath(a.sigma)) if i["arm"] == "B4"), key=lambda i: i["key"])
    pick = [next(i for i in items if i["op"] == op) for op in ("DROP_VALUE", "DROP_FIELD", "NEVER_SEL")]
    look = []
    with open(a.diffs, "w") as out:
        out.write("# PA-SIGMA-004 look sample: original rule file vs the B4 file (house style, SigmaHQ layout)\n\n")
        for i in pick:
            with open(os.path.join(a.sigma, i["rel"]), encoding="utf-8") as fh:
                orig = fh.read()
            look.append({"key": i["key"], "op": i["op"], "path": i["rel"], "surv": i["surv"]})
            out.write(f"## {i['op']} on {i['rel']}\n\nkey `{i['key']}`\n\n```diff\n")
            out.write("\n".join(difflib.unified_diff(orig.splitlines(), i["text"].splitlines(), "original", "B4",
                                                     n=1, lineterm="")) + "\n```\n\n")
    with open(os.path.join(ROOT, "results", "pa_sigma_004", "look_sample.json"), "w") as fh:
        json.dump(look, fh, indent=1)
    print(f"look sample: {[(r['op'], r['path']) for r in look]}; diffs in {a.diffs}")


if __name__ == "__main__":
    sys.exit(main())
