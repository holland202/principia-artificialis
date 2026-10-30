#!/usr/bin/env python3
"""PA-SIGMA-004 items, house layout and feasibility counts (C-FEAS). Run before registration.

Door P6 of PA-SIGMA-003: SigmaHQ's two remaining automated rule checks, yamllint (job `yamllint` in
sigma-test.yml) and the JSON-schema check (workflow sigma-validation.yml), on the 1,502 broadening mutants.

Arms:
  A  each mutant exactly as PA-SIGMA-001 wrote it (PyYAML defaults: 2-space indentation);
  B4 each mutant in PA-SIGMA-003's house style (arm B), written in SigmaHQ's own layout (house_dump below).
     Comments are not kept.
Controls: IDENTITY (each original's bytes), ROUNDTRIP4 (each original in house layout), LAYOUT_BAD (10 originals
in PyYAML's default layout, the layout arm A has), SCHEMA_BAD (10 originals in house layout with level: bogus).

Without --run nothing is checked. With --run: G1 (yamllint over the whole unmutated checkout and the schema check
over every rule file, as the workflows run them) and one pass over the controls (282 IDENTITY, 282 ROUNDTRIP4,
10 LAYOUT_BAD, 10 SCHEMA_BAD). No mutant is checked here.

Usage (repository root, the venv PA-SIGMA-002/003 used):
  python experiments/pa_sigma_004/feasibility.py --sigma SIGMA [--run --tools VENV_BIN --schema SCHEMA_JSON]
"""
import argparse
import collections
import copy
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCHEMA_SHA256 = "eb95ddb1bc2503145a6e84511e38990f74fe9a843067065a23d3763457fb2d95"
STAGE_DIR = os.path.join("rules", "pa_sigma_004")
N_BAD = 10


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


F3 = _load("pa_sigma_003_feasibility", os.path.join(os.path.dirname(HERE), "pa_sigma_003", "feasibility.py"))
M = F3.M


def house_dump(rule):
    """SigmaHQ's layout: mappings indented by 4, list dashes 4 under their key with one space after the dash
    (ruamel.yaml, indent mapping=4, sequence=6, offset=4). PyYAML cannot write that layout: with indent=4 it puts
    three spaces after each dash, which yamllint's `hyphens` rule rejects (seen in the first ROUNDTRIP4 pre-check)."""
    from ruamel.yaml import YAML

    y = YAML(typ="rt")
    y.indent(mapping=4, sequence=6, offset=4)
    y.width = 10 ** 6
    buf = io.StringIO()
    y.dump(rule, buf)
    return buf.getvalue()


def build_items(sigma, sabotage=False):
    """dict(id, kind, arm, rule, rel, op, surv, key, text). Sabotage writes each mutant's original instead."""
    items3 = F3.build_items(sigma)
    originals = {}
    out = []
    for i in items3:
        if i["kind"] == "IDENTITY":
            originals[i["rule"]] = i["text"]
    rules = sorted({i["rule"]: i["rel"] for i in items3}.items())
    for rid, rel in rules:
        orig = yaml.safe_load(originals[rid])
        out.append({"id": f"IDENTITY:{rid}", "kind": "IDENTITY", "arm": "-", "rule": rid, "rel": rel,
                    "text": originals[rid]})
        out.append({"id": f"ROUNDTRIP4:{rid}", "kind": "ROUNDTRIP4", "arm": "-", "rule": rid, "rel": rel,
                    "text": house_dump(orig)})
    for rid, rel in rules[:N_BAD]:
        orig = yaml.safe_load(originals[rid])
        bad = copy.deepcopy(orig)
        bad["level"] = "bogus"
        out.append({"id": f"LAYOUT_BAD:{rid}", "kind": "LAYOUT_BAD", "arm": "-", "rule": rid, "rel": rel,
                    "text": M._dump(orig)})
        out.append({"id": f"SCHEMA_BAD:{rid}", "kind": "SCHEMA_BAD", "arm": "-", "rule": rid, "rel": rel,
                    "text": house_dump(bad)})
    b_text = {i["key"]: i["text"] for i in items3 if i["kind"] == "MUTANT" and i["arm"] == "B"}
    for i in items3:
        if i["kind"] != "MUTANT" or i["arm"] != "A":
            continue
        house = yaml.safe_load(b_text.get(i["key"], i["text"]))
        out.append({"id": "A:" + i["key"], "kind": "MUTANT", "arm": "A", "rule": i["rule"], "rel": i["rel"],
                    "op": i["op"], "surv": i["surv"], "key": i["key"],
                    "text": originals[i["rule"]] if sabotage else i["text"]})
        out.append({"id": "B4:" + i["key"], "kind": "MUTANT", "arm": "B4", "rule": i["rule"], "rel": i["rel"],
                    "op": i["op"], "surv": i["surv"], "key": i["key"],
                    "text": originals[i["rule"]] if sabotage else house_dump(house),
                    "house_equal_b": yaml.safe_load(house_dump(house)) == house})
    return out


# ------------------------------------------------------------------ staging and the two checks

def make_tree(sigma, parent):
    root = tempfile.mkdtemp(prefix="pa4-", dir=parent)
    for entry in sorted(os.listdir(sigma)):
        if entry != ".git":
            subprocess.run(["cp", "-al", os.path.join(sigma, entry), root], check=True)
    return root


def stage_all(root, items):
    """Every item as its own file under rules/pa_sigma_004/. Returns {relative staged path: item id}."""
    d = os.path.join(root, STAGE_DIR)
    os.makedirs(d)
    names = {}
    for n, i in enumerate(items):
        rel = os.path.join(STAGE_DIR, f"item_{n:05d}.yml")
        with open(os.path.join(root, rel), "w", encoding="utf-8", newline="") as fh:
            fh.write(i["text"])
        names[rel] = i["id"]
    return names


def run_yamllint(tools, root, target):
    """yamllint as the action runs it (-f parsable -s), with the repository's .yamllint, from the root."""
    p = subprocess.run([os.path.join(tools, "yamllint"), "-f", "parsable", "-s", target], cwd=root,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def run_schema(tools, root, schema, files):
    """check-jsonschema as sigma-rules-validator runs it, on the given files."""
    p = subprocess.run([os.path.join(tools, "check-jsonschema"), "--schemafile", schema] + files, cwd=root,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def yamllint_flags(out):
    """{relative path: set of rule names} from yamllint's parsable lines: path:line:col: [level] msg (rule)."""
    flags = {}
    for line in out.splitlines():
        m = re.match(r"^(?:\./)?(.+?\.yml):\d+:\d+: \[(error|warning)\] .*?(?:\((\S+)\))?$", line)
        if m:
            flags.setdefault(m.group(1), set()).add(m.group(3) or m.group(2))
    return flags


def schema_flags(root, out):
    """{relative path: set of JSON paths} from check-jsonschema's error lines: '  <abs path>::$.x: msg'."""
    flags = {}
    for line in out.splitlines():
        m = re.match(r"^\s*(\S+?\.yml)::(\S*?):", line)
        if m:
            path = m.group(1)
            rel = os.path.relpath(path, root) if os.path.isabs(path) else path
            flags.setdefault(rel, set()).add(m.group(2) or "$")
    return flags


def schema_rule_files(root):
    """The files validate.py lists for SIGMA_RULES_PATH as sigma-validation.yml sets it."""
    out = []
    for d in ("rules", "rules-compliance", "rules-dfir", "rules-emerging-threats", "rules-placeholder",
              "rules-threat-hunting"):
        for base, _, files in os.walk(os.path.join(root, d)):
            out += [os.path.join(base, f) for f in files if f.endswith(".yml")]
    return sorted(out)


def versions(tools):
    code = ("import importlib.metadata as m, sys\nprint('yamllint', m.version('yamllint'), '| check-jsonschema',"
            " m.version('check-jsonschema'), '| jsonschema', m.version('jsonschema'), '| python', sys.version.split()[0])")
    return subprocess.run([os.path.join(tools, "python"), "-I", "-c", code], capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma", required=True)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--tools")
    ap.add_argument("--schema")
    a = ap.parse_args()
    sigma = os.path.abspath(a.sigma)
    items = build_items(sigma)
    kinds = collections.Counter(i["kind"] + ("/" + i["arm"] if i["arm"] != "-" else "") for i in items)
    print(f"0. items {len(items)} {dict(sorted(kinds.items()))}")
    b4 = [i for i in items if i["arm"] == "B4"]
    print(f"1. B4 texts that parse back to their house-style rule: {sum(i['house_equal_b'] for i in b4)} of {len(b4)}; "
          f"SURV {sum(1 for i in b4 if i['surv'])}; by operator {dict(sorted(collections.Counter(i['op'] for i in b4).items()))}")
    if not a.run:
        return 0
    with open(a.schema, "rb") as fh:
        sh = hashlib.sha256(fh.read()).hexdigest()
    print(f"2. tools: {versions(a.tools)} | schema sha256 {sh} (pinned: {sh == SCHEMA_SHA256})")
    work = os.path.join(os.path.expanduser("~"), "pa_sigma_004_work")
    os.makedirs(work, exist_ok=True)
    root = make_tree(sigma, work)
    try:
        t0 = time.time()
        code, out = run_yamllint(a.tools, root, ".")
        print(f"3. G1 yamllint over the unmutated checkout: exit {code}, files flagged {len(yamllint_flags(out))}, "
              f"{time.time() - t0:.0f}s")
        t0 = time.time()
        files = schema_rule_files(root)
        code, out = run_schema(a.tools, root, a.schema, files)
        print(f"4. G1 schema check over {len(files)} rule files: exit {code}, files flagged "
              f"{len(schema_flags(root, out))}, {time.time() - t0:.0f}s; last line: {out.strip().splitlines()[-1][:80]!r}")
        ctl = [i for i in items if i["kind"] in ("IDENTITY", "ROUNDTRIP4", "LAYOUT_BAD", "SCHEMA_BAD")]
        names = stage_all(root, ctl)
        code_y, out_y = run_yamllint(a.tools, root, STAGE_DIR)
        code_s, out_s = run_schema(a.tools, root, a.schema, sorted(names))
        fy, fs = yamllint_flags(out_y), schema_flags(root, out_s)
        for kind in ("IDENTITY", "ROUNDTRIP4", "LAYOUT_BAD", "SCHEMA_BAD"):
            ids = {n for n, i in names.items() if i.startswith(kind + ":")}
            print(f"5. {kind} control pre-check, {len(ids)} files: yamllint flagged {len(ids & set(fy))}, "
                  f"schema flagged {len(ids & set(fs))}")
        reasons = collections.Counter(r for n, rs in fy.items() for r in rs)
        print(f"   yamllint reasons on controls: {dict(reasons.most_common(8))}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
