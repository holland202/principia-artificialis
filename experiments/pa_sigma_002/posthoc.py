#!/usr/bin/env python3
"""PA-SIGMA-002 post-hoc (written after run 1; EXPLORATORY, not registered).

1. The person-look sample (C-SYNTH): five CAUGHT and five uncaught catchable mutants, the first five of each by
   sha256, with the diff of each against its original rule. Identities go to results/pa_sigma_002/look_sample.json;
   the diffs (SigmaHQ rule text) go to the path given with --diffs, outside the repository.
2. Descriptive counts: how many rules have at least one CAUGHT mutant, and how the CAUGHT mutants spread over rules.

Usage: python experiments/pa_sigma_002/posthoc.py --sigma SIGMA --diffs /path/outside/repo.md
"""
import argparse
import collections
import difflib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pa_sigma_001"))
import feasibility as _f1  # noqa: E402,F401  (PA-SIGMA-001's)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


F2 = _load("pa_sigma_002_feasibility", os.path.join(HERE, "feasibility.py"))
H = _load("pa_sigma_002_harness", os.path.join(HERE, "run_pa_sigma_002.py"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma", required=True)
    ap.add_argument("--diffs", required=True)
    a = ap.parse_args()
    sigma = os.path.abspath(a.sigma)
    with open(os.path.join(ROOT, "results", "pa_sigma_002", "results.json")) as fh:
        res = json.load(fh)
    caught = set(res["results"]["caught_mutants"])
    muts = F2.broadening_set(sigma)
    fps = H.known_fp_rows(sigma)

    def bucket(m):
        if m["level"] == "low":
            return "level_low"
        if any(p == ".*" for p in fps.get(m["rule"], [])):
            return "known_fp_all"
        return "catchable"

    cat = [m for m in muts if bucket(m) == "catchable"]
    key = lambda m: f"{m['rule']}:{m['k']}:{m['sha']}"
    got = [m for m in cat if key(m) in caught]
    missed = [m for m in cat if key(m) not in caught]
    print(f"catchable {len(cat)}; caught {len(got)} (matches results.json: {len(got) == res['results']['caught']})")
    per_rule = collections.Counter(m["rule"] for m in got)
    rules_cat = {m["rule"] for m in cat}
    print(f"rules with at least one CAUGHT mutant: {len(per_rule)} of {len(rules_cat)}")
    print(f"CAUGHT mutants per such rule: {dict(sorted(collections.Counter(per_rule.values()).items()))}")
    top = per_rule.most_common(5)
    print(f"most CAUGHT mutants in one rule: {top}")
    sample = sorted(got, key=lambda m: m["sha"])[:5] + sorted(missed, key=lambda m: m["sha"])[:5]
    look = [{"rule": m["rule"], "k": m["k"], "op": m["op"], "sha256": m["sha"], "caught": key(m) in caught,
             "path": m["path"]} for m in sample]
    with open(os.path.join(ROOT, "results", "pa_sigma_002", "look_sample.json"), "w") as fh:
        json.dump(look, fh, indent=1)
    with open(a.diffs, "w") as fh:
        fh.write("# PA-SIGMA-002 look sample: five CAUGHT, five uncaught broadening mutants\n\n")
        for m, row in zip(sample, look):
            with open(os.path.join(sigma, m["path"]), encoding="utf-8") as rf:
                orig = H.M._dump(__import__("yaml").safe_load(rf.read()))
            d = difflib.unified_diff(orig.splitlines(), m["text"].splitlines(), "original (re-dumped)", "mutant", n=2,
                                     lineterm="")
            fh.write(f"## {'CAUGHT' if row['caught'] else 'not caught'}: {m['op']} on {m['path']} (rule {m['rule']}, "
                     f"mutant {m['k']})\n\n```diff\n" + "\n".join(d) + "\n```\n\n")
    print(f"look sample: {sum(r['caught'] for r in look)} CAUGHT + {sum(not r['caught'] for r in look)} not caught; "
          f"identities in results/pa_sigma_002/look_sample.json; diffs in {a.diffs}")


if __name__ == "__main__":
    main()
