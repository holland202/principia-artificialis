#!/usr/bin/env python3
"""PA-SIGMA-004 harness: yamllint and the JSON-schema check against PA-SIGMA-001's 1,502 BROADENING mutants.

Registered in PREREG.md (commit 77ee154) before this file existed. Items, layout, staging and the two checks come
from feasibility.py (committed with the registration). This file runs one staged pass, applies the gates, scores
P1-P4, adds PA-SIGMA-003's arm-B result to give the combined count, and prints a DIGEST.

  python -B experiments/pa_sigma_004/run_pa_sigma_004.py --sigma SIGMA --tools VENV_BIN --schema SCHEMA_JSON
  ... --sabotage    stage every mutant's original rule bytes instead (expected: 3 of 4, exit 1)
  ... --selftest    check this harness's own logic on constructed inputs

Exit: 0 = outcome equals RECORDED (or RECORDED not pinned yet); 1 = it differs; 2 = a gate or pin failed.
"""
import argparse
import collections
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SIGMA_COMMIT = "05d1031f537e830b76da53bae2400c5814c89165"
SURV_IDENTITY = "b0c45e1108bb89987bac7fb7b75a7d5fa1863aba3b237d8469d4f382ac11bc6b"
RESULTS_003 = os.path.join(ROOT, "results", "pa_sigma_003", "results.json")
RECORDED = (("HELD", "HELD", "HELD", "HELD"),
            "6f598a26ae03548b91f6ac0becaee7aedad4fedc36e38f8b0d38373898ae7890")  # runs 1 and 2 (G7)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def feas():
    return _load("pa_sigma_004_feasibility", os.path.join(HERE, "feasibility.py"))


def score(items, flags):
    """items: built items; flags: {item id: {"YL": [...], "SCH": [...]}}. Returns (statuses, facts)."""
    A = [i for i in items if i["kind"] == "MUTANT" and i["arm"] == "A"]
    B4 = [i for i in items if i["kind"] == "MUTANT" and i["arm"] == "B4"]

    def hit(i, c):
        return bool(flags.get(i["id"], {}).get(c))
    b4_yl = {i["key"] for i in B4 if hit(i, "YL")}
    b4_sch = {i["key"] for i in B4 if hit(i, "SCH")}
    a_yl = {i["key"] for i in A if hit(i, "YL")}
    a_sch = {i["key"] for i in A if hit(i, "SCH")}
    statuses = (
        "HELD" if not b4_yl else "REFUTED",
        "HELD" if not b4_sch else "REFUTED",
        "HELD" if len(a_yl) == len(A) else "REFUTED",
        "HELD" if not a_sch else "REFUTED",
    )
    facts = {"B4": {"YL": len(b4_yl), "SCH": len(b4_sch)}, "A": {"YL": len(a_yl), "SCH": len(a_sch), "n": len(A)},
             "b4_flagged": sorted(b4_yl | b4_sch), "a_not_yl": sorted({i["key"] for i in A} - a_yl),
             "a_sch": sorted(a_sch)}
    return statuses, facts


def combined(items, flags, flagged_003, changed_003):
    """SURV keys passing all seven checks in house style: not flagged by PA-SIGMA-003's arm B, nor here in B4."""
    surv = {i["key"] for i in items if i["kind"] == "MUTANT" and i["arm"] == "A" and i["surv"]}
    f3 = {k for k in surv if (("B:" + k) if k in changed_003 else ("A:" + k)) in flagged_003}
    f4 = {i["key"] for i in items if i["kind"] == "MUTANT" and i["arm"] == "B4" and any(flags.get(i["id"], {}).values())}
    passing = surv - f3 - f4
    return {"surv": len(surv), "flagged_by_003_arm_b": len(f3 & surv), "flagged_here_b4": len(f4 & surv),
            "pass_all_seven": len(passing), "rules_keeping_one": len({k.split(":")[0] for k in passing}),
            "rules_with_surv": len({k.split(":")[0] for k in surv})}


def digest(statuses, flags, gates):
    canon = {"statuses": list(statuses), "gates": gates,
             "flags": {i: {c: sorted(r) for c, r in sorted(f.items()) if r} for i, f in sorted(flags.items())
                       if any(f.values())}}
    return hashlib.sha256(json.dumps(canon, sort_keys=True).encode()).hexdigest()


def git(sigma, *args):
    return subprocess.run(["git", "-C", sigma, *args], capture_output=True, text=True).stdout.strip()


def run(a):
    F4 = feas()
    sigma = os.path.abspath(a.sigma)
    print("PA-SIGMA-004 harness" + (" (SABOTAGE: every mutant staged as its original)" if a.sabotage else ""))
    with open(a.schema, "rb") as fh:
        sh = hashlib.sha256(fh.read()).hexdigest()
    print(f"environment: {platform.system()} {platform.machine()} | harness Python {platform.python_version()} | "
          f"checks: {F4.versions(a.tools)} | SigmaHQ {git(sigma, 'rev-parse', 'HEAD')[:7]} | schema {sh[:12]}")
    if not (git(sigma, "rev-parse", "HEAD") == SIGMA_COMMIT and not git(sigma, "status", "--porcelain")
            and sh == F4.SCHEMA_SHA256):
        print("PIN FAILURE: SigmaHQ commit, clean checkout or schema sha256")
        return 2
    items = F4.build_items(sigma)
    staged = F4.build_items(sigma, sabotage=True) if a.sabotage else items
    A = [i for i in items if i["kind"] == "MUTANT" and i["arm"] == "A"]
    g2 = (F4.F3.identity(i["key"] for i in A) == F4.F3.SET_IDENTITY
          and F4.F3.identity(i["key"] for i in A if i["surv"]) == SURV_IDENTITY)
    g6 = all(i["house_equal_b"] for i in items if i["arm"] == "B4")
    kinds = collections.Counter(i["kind"] + ("/" + i["arm"] if i["arm"] != "-" else "") for i in staged)
    print(f"items: {dict(sorted(kinds.items()))}")
    work = os.path.join(os.path.expanduser("~"), "pa_sigma_004_work")
    os.makedirs(work, exist_ok=True)
    root = F4.make_tree(sigma, work)
    try:
        g1y_code, g1y_out = F4.run_yamllint(a.tools, root, ".")
        files = F4.schema_rule_files(root)
        g1s_code, g1s_out = F4.run_schema(a.tools, root, a.schema, files)
        g1 = (g1y_code == 0 and not F4.yamllint_flags(g1y_out) and g1s_code == 0
              and "ok -- validation done" in g1s_out)
        names = F4.stage_all(root, staged)
        y_code, y_out = F4.run_yamllint(a.tools, root, F4.STAGE_DIR)
        s_code, s_out = F4.run_schema(a.tools, root, a.schema, sorted(names))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    fy, fs = F4.yamllint_flags(y_out), F4.schema_flags(root, s_out)
    g8 = (y_code in (0, 1) and s_code in (0, 1) and (y_code == 1) == bool(fy) and (s_code == 1) == bool(fs)
          and (s_code == 1 or "ok -- validation done" in s_out))
    unknown = (set(fy) | set(fs)) - set(names)
    flags = {i["id"]: {"YL": [], "SCH": []} for i in staged}
    for rel, iid in names.items():
        flags[iid]["YL"] = sorted(fy.get(rel, []))
        flags[iid]["SCH"] = sorted(fs.get(rel, []))
    by_kind = collections.defaultdict(list)
    for i in staged:
        by_kind[i["kind"]].append(i)

    def n(kind, check=None):
        return sum(1 for i in by_kind[kind] if any(flags[i["id"]][c] for c in ([check] if check else ("YL", "SCH"))))
    gates = {
        "G1": g1,
        "G2": g2,
        "G3": n("IDENTITY") == 0,
        "G4": n("ROUNDTRIP4") == 0,
        "G5": n("LAYOUT_BAD", "YL") >= 9 and n("SCHEMA_BAD", "SCH") >= 9,
        "G6": g6,
        "G8": g8 and not unknown,
        "G9": git(sigma, "rev-parse", "HEAD") == SIGMA_COMMIT and not git(sigma, "status", "--porcelain"),
    }
    print(f"G1 unmutated checkout: yamllint exit {g1y_code}; schema exit {g1s_code} over {len(files)} rule files")
    print(f"staged run: yamllint exit {y_code}, files flagged {len(fy)}; schema exit {s_code}, files flagged {len(fs)}"
          f"; flagged paths not staged here: {len(unknown)}")
    print(f"controls flagged (either check): IDENTITY {n('IDENTITY')} of {len(by_kind['IDENTITY'])}, ROUNDTRIP4 "
          f"{n('ROUNDTRIP4')} of {len(by_kind['ROUNDTRIP4'])}; LAYOUT_BAD by yamllint {n('LAYOUT_BAD', 'YL')} of 10; "
          f"SCHEMA_BAD by schema {n('SCHEMA_BAD', 'SCH')} of 10 (each needs >= 9)")
    for g, ok in gates.items():
        print(f"{g} {'PASS' if ok else 'FAIL'}")
    statuses, facts = score(items, flags)
    with open(RESULTS_003) as fh:
        flagged_003 = json.load(fh)["flagged"]
    changed_003 = {i["key"] for i in F4.F3.build_items(sigma) if i["kind"] == "MUTANT" and i["arm"] == "B"}
    comb = combined(items, flags, flagged_003, changed_003)
    yl_reasons = collections.Counter(r for i in A for r in flags[i["id"]]["YL"])
    print(f"P1 B4, yamllint flags {facts['B4']['YL']} of 1502; registered: none -> {statuses[0]}")
    print(f"P2 B4, schema flags {facts['B4']['SCH']} of 1502; registered: none -> {statuses[1]}")
    print(f"P3 arm A, yamllint flags {facts['A']['YL']} of {facts['A']['n']}; registered: every one -> {statuses[2]}")
    print(f"P4 arm A, schema flags {facts['A']['SCH']} of 1502; registered: none -> {statuses[3]}")
    print(f"yamllint rules on arm A: {dict(yl_reasons.most_common())}")
    print(f"combined (house style): of {comb['surv']} SURV, PA-SIGMA-003 arm B flags {comb['flagged_by_003_arm_b']}, "
          f"this study's B4 flags {comb['flagged_here_b4']}; pass all seven checks: {comb['pass_all_seven']} of 1502 "
          f"broadening mutants; rules keeping one: {comb['rules_keeping_one']} of {comb['rules_with_surv']}")
    dg = digest(statuses, flags, gates)
    print(f"VERDICT {statuses.count('HELD')} of 4 as registered")
    print(f"DIGEST {dg}")
    out_dir = os.path.join(ROOT, "results", "pa_sigma_004")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results_sabotage.json" if a.sabotage else "results.json"), "w") as fh:
        json.dump({"study": "PA-SIGMA-004", "sabotage": a.sabotage, "statuses": statuses, "digest": dg,
                   "gates": gates, "facts": facts, "combined": comb, "yamllint_rules_arm_a": dict(yl_reasons),
                   "flagged": {i: {c: r for c, r in f.items() if r} for i, f in sorted(flags.items())
                               if any(f.values()) and not i.startswith("A:")},
                   "arm_a_flag_counts": {"YL": facts["A"]["YL"], "SCH": facts["A"]["SCH"]}},
                  fh, indent=1, sort_keys=True)
    if not all(gates.values()):
        print("GATE FAILURE: no verdict")
        return 2
    if RECORDED is None:
        print("RECORDED: not pinned yet")
        return 0
    same = (tuple(statuses), dg) == (tuple(RECORDED[0]), RECORDED[1])
    print(f"RECORDED {'matches' if same else 'DIFFERS'}")
    return 0 if same else 1


def selftest():
    F4 = feas()
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))
    y = ("rules/pa_sigma_004/item_00001.yml:15:3: [error] wrong indentation: expected 4 but found 2 (indentation)\n"
         "./rules/pa_sigma_004/item_00002.yml:1:1: [warning] truthy value should be one of [false, true] (truthy)\n"
         "rules/pa_sigma_004/item_00003.yml:2:1: [error] syntax error: mapping values are not allowed here\n")
    fy = F4.yamllint_flags(y)
    ok("yamllint rule name", fy.get("rules/pa_sigma_004/item_00001.yml") == {"indentation"})
    ok("yamllint ./ prefix and warnings", fy.get("rules/pa_sigma_004/item_00002.yml") == {"truthy"})
    ok("yamllint line without a rule", "rules/pa_sigma_004/item_00003.yml" in fy)
    s = ("Schema validation errors were encountered.\n"
         "  rules/pa_sigma_004/item_00004.yml::$.level: 'bogus' is not valid under any of the given schemas\n"
         "  /r/x/rules/pa_sigma_004/item_00005.yml::$: 'title' is a required property\n"
         "  Underlying errors caused this.\n")
    fs = F4.schema_flags("/r/x", s)
    ok("schema relative path", fs.get("rules/pa_sigma_004/item_00004.yml") == {"$.level"})
    ok("schema absolute path made relative", fs.get("rules/pa_sigma_004/item_00005.yml") == {"$"})
    ok("schema prose lines ignored", len(fs) == 2)
    items = [{"kind": "MUTANT", "arm": "A", "id": "A:k1", "key": "k1", "surv": True},
             {"kind": "MUTANT", "arm": "A", "id": "A:k2", "key": "k2", "surv": True},
             {"kind": "MUTANT", "arm": "B4", "id": "B4:k1", "key": "k1", "surv": True},
             {"kind": "MUTANT", "arm": "B4", "id": "B4:k2", "key": "k2", "surv": True}]
    st, _ = score(items, {"A:k1": {"YL": ["indentation"]}, "A:k2": {"YL": ["indentation"]}})
    ok("score all held", st == ("HELD", "HELD", "HELD", "HELD"))
    st, _ = score(items, {"A:k1": {"YL": ["indentation"]}})
    ok("score: one arm-A pass refutes P3 only", st == ("HELD", "HELD", "REFUTED", "HELD"))
    st, _ = score(items, {"A:k1": {"YL": ["x"]}, "A:k2": {"YL": ["x"]}, "B4:k2": {"SCH": ["$"]}})
    ok("score: a B4 schema flag refutes P2", st == ("HELD", "REFUTED", "HELD", "HELD"))
    c = combined(items, {"B4:k2": {"YL": ["x"]}}, {"B:k1": {"SC": ["x"]}}, {"k1"})
    ok("combined count", c["pass_all_seven"] == 0 and c["flagged_by_003_arm_b"] == 1 and c["flagged_here_b4"] == 1)
    c = combined(items, {}, {"A:k1": {"TR": ["x"]}}, {"k1"})
    ok("combined uses arm B when the mutant changed", c["pass_all_seven"] == 2)
    for name, good in checks:
        print(f"{'PASS' if good else 'FAIL'} {name}")
    bad = sum(1 for _, g in checks if not g)
    print(f"selftest: {len(checks) - bad}/{len(checks)} passed")
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma")
    ap.add_argument("--tools")
    ap.add_argument("--schema")
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    return selftest() if a.selftest else run(a)


if __name__ == "__main__":
    sys.exit(main())
