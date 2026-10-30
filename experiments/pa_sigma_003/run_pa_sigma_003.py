#!/usr/bin/env python3
"""PA-SIGMA-003 harness: SigmaHQ's three static rule checks against PA-SIGMA-001's 1,502 BROADENING mutants.

Registered in PREREG.md (commit 88eeaaf) before this file existed. Population, house-style forms, derived sets and
controls come from feasibility.py; rounds, the checks and attribution from stage.py (both committed with the
registration). This file runs the rounds, applies the gates, scores P1-P4 and prints a DIGEST.

  python -B experiments/pa_sigma_003/run_pa_sigma_003.py --sigma SIGMA --py3 PY311 --attack JSON --d3fend JSON
  ... --sabotage    stage every mutant's original rule instead (expected: 1 of 4, exit 1)
  ... --selftest    check this harness's own logic on constructed inputs (no SigmaHQ checkout needed)

Exit: 0 = outcome equals RECORDED (or RECORDED not pinned yet); 1 = it differs; 2 = a gate or pin failed.
Run with the venv PA-SIGMA-002 used (pySigma 1.5.1 + Elasticsearch backend, for G6); the checks themselves run in
the Python 3.11 venv given by --py3.
"""
import argparse
import collections
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SIGMA_COMMIT = "05d1031f537e830b76da53bae2400c5814c89165"
SURV_IDENTITY = "b0c45e1108bb89987bac7fb7b75a7d5fa1863aba3b237d8469d4f382ac11bc6b"
RECORDED = None  # pinned after run 1 and run 2: (statuses, digest)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def modules():
    f3 = _load("pa_sigma_003_feasibility", os.path.join(HERE, "feasibility.py"))
    return f3, f3.S


# ------------------------------------------------------------------ scoring (pure functions, selftested)

def cross_rule_only(check, reasons, cross):
    return bool(reasons) and set(reasons) <= cross[check]


def score(items, flags, checks=("SC", "TR", "TL")):
    """items: built items; flags: {item id: {check: [reasons]}}. Returns (statuses, facts)."""
    A = [i for i in items if i["kind"] == "MUTANT" and i["arm"] == "A"]
    B = {i["key"]: i for i in items if i["kind"] == "MUTANT" and i["arm"] == "B"}

    def flagged(i, c):
        return bool(flags.get(i["id"], {}).get(c))

    def arm_b_flag(a, c):
        b = B.get(a["key"])
        return flagged(b, c) if b is not None else flagged(a, c)

    def arm_b_derived(a, what):
        b = B.get(a["key"])
        return (b if b is not None else a)[what]

    a_tr = {a["key"] for a in A if flagged(a, "TR")}
    a_sc = {a["key"] for a in A if flagged(a, "SC")}
    a_tl = {a["key"] for a in A if flagged(a, "TL")}
    b_tr = {a["key"] for a in A if arm_b_flag(a, "TR")}
    b_sc = {a["key"] for a in A if arm_b_flag(a, "SC")}
    b_tl = {a["key"] for a in A if arm_b_flag(a, "TL")}
    d_tr = {a["key"] for a in A if a["derived_tr"]}
    d_sc = {a["key"] for a in A if a["derived_sc"]}
    d_b_sc = {a["key"] for a in A if arm_b_derived(a, "derived_sc")}
    statuses = (
        "HELD" if a_tr == d_tr else "REFUTED",
        "HELD" if a_sc == d_sc else "REFUTED",
        "HELD" if not a_tl and not b_tl else "REFUTED",
        "HELD" if not b_tr and b_sc == d_b_sc else "REFUTED",
    )
    surv = {a["key"] for a in A if a["surv"]}
    ops = {a["key"]: a["op"] for a in A}
    a_any, b_any = a_tr | a_sc | a_tl, b_tr | b_sc | b_tl
    facts = {
        "arm_a": {"TR": len(a_tr), "SC": len(a_sc), "TL": len(a_tl), "any": len(a_any),
                  "any_in_surv": len(a_any & surv)},
        "arm_b": {"TR": len(b_tr), "SC": len(b_sc), "TL": len(b_tl), "any": len(b_any),
                  "any_in_surv": len(b_any & surv)},
        "derived": {"TR": len(d_tr), "SC": len(d_sc), "arm_b_SC": len(d_b_sc)},
        "mismatch": {"P1_flagged_not_derived": sorted(a_tr - d_tr), "P1_derived_not_flagged": sorted(d_tr - a_tr),
                     "P2_flagged_not_derived": sorted(a_sc - d_sc), "P2_derived_not_flagged": sorted(d_sc - a_sc),
                     "P3_flagged": sorted(a_tl | b_tl), "P4_tr_flagged": sorted(b_tr),
                     "P4_sc_flagged_not_derived": sorted(b_sc - d_b_sc), "P4_sc_derived_not_flagged": sorted(d_b_sc - b_sc)},
        "surv": len(surv),
        "pass_everything_arm_a": len(surv - a_any),
        "pass_everything_arm_b": len(surv - b_any),
        "by_op_arm_a_any": dict(sorted(collections.Counter(ops[k] for k in a_any).items())),
        "by_op_arm_b_any": dict(sorted(collections.Counter(ops[k] for k in b_any).items())),
        "rules_with_a_surv_mutant_passing_everything_arm_b": len({k.split(":")[0] for k in surv - b_any}),
        "rules_with_a_surv_mutant": len({k.split(":")[0] for k in surv}),
    }
    return statuses, facts


def digest(statuses, flags, gates):
    canon = {"statuses": list(statuses), "gates": gates,
             "flags": {i: {c: sorted(r) for c, r in sorted(f.items()) if r} for i, f in sorted(flags.items())
                       if any(f.values())}}
    return hashlib.sha256(json.dumps(canon, sort_keys=True).encode()).hexdigest()


# ------------------------------------------------------------------ the run

def git(sigma, *args):
    return subprocess.run(["git", "-C", sigma, *args], capture_output=True, text=True).stdout.strip()


def run(a):
    f3, S = modules()
    sigma = os.path.abspath(a.sigma)
    print("PA-SIGMA-003 harness" + (" (SABOTAGE: every mutant staged as its original)" if a.sabotage else ""))
    with open(a.attack, "rb") as fh:
        att = hashlib.sha256(fh.read()).hexdigest()
    print(f"environment: {platform.system()} {platform.machine()} | harness Python {platform.python_version()} | "
          f"checks: {f3.versions(a.py3)} | SigmaHQ {git(sigma, 'rev-parse', 'HEAD')[:7]} | ATT&CK {att[:12]}")
    pins = (git(sigma, "rev-parse", "HEAD") == SIGMA_COMMIT and not git(sigma, "status", "--porcelain")
            and att == f3.ATTACK_SHA256)
    if not pins:
        print("PIN FAILURE: SigmaHQ commit, clean checkout or ATT&CK file sha256")
        return 2
    t0 = time.time()
    items = f3.build_items(sigma)
    staged_items = f3.build_items(sigma, sabotage=True) if a.sabotage else items
    A = [i for i in items if i["kind"] == "MUTANT" and i["arm"] == "A"]
    B = [i for i in items if i["kind"] == "MUTANT" and i["arm"] == "B"]
    g2 = (f3.identity(i["key"] for i in A) == f3.SET_IDENTITY and
          f3.identity(i["key"] for i in A if i["surv"]) == SURV_IDENTITY)
    eq = collections.Counter(f3.equivalent(i["raw_text"], i["text"]) for i in B)
    print(f"items: {dict(sorted(collections.Counter(i['kind'] + ('/' + i['arm'] if i['arm'] != '-' else '') for i in staged_items).items()))}; "
          f"G6 equivalence {dict(sorted(eq.items()))}; built in {time.time() - t0:.0f}s")
    tools = S.Tools(sigma, a.py3, a.attack, a.d3fend)
    work = os.path.join(os.path.expanduser("~"), "pa_sigma_003_rounds")
    os.makedirs(work, exist_ok=True)
    g1 = S.run_round(tools, work, {})
    by_rel = collections.OrderedDict()
    for i in staged_items:
        by_rel.setdefault(i["rel"], []).append(i)
    rounds = S.schedule(by_rel)
    print(f"rounds: {len(rounds)} (+ G1), {a.workers} at a time")
    results = []
    for start in range(0, len(rounds), a.workers):
        chunk = rounds[start:start + a.workers]
        res = S.run_rounds(tools, work, [{rel: it["text"] for rel, it in r.items()} for r in chunk], workers=a.workers)
        results.extend(res)
        for j, (r, rr) in enumerate(zip(chunk, res)):
            print(f"  round {start + j + 1:2d}/{len(rounds)} items {len(r):3d} | " + " | ".join(
                f"{c} exit {rr[c]['code']} {rr[c]['seconds']:5.1f}s flagged {len(rr[c]['flags']):3d}" for c in S.CHECKS),
                file=sys.stderr, flush=True)
    flags = {i["id"]: {c: [] for c in S.CHECKS} for i in staged_items}
    completed = all(g1[c]["completed"] for c in S.CHECKS)
    for r, rr in zip(rounds, results):
        for c in S.CHECKS:
            completed = completed and rr[c]["completed"]
            for rel, reasons in rr[c]["flags"].items():
                flags[r[rel]["id"]][c] = reasons
    solo = [i for i in staged_items if any(S.CROSS_RULE[c] and f3_cross(S, c, flags[i["id"]][c]) for c in S.CHECKS)]
    for i in solo:
        rr = S.run_round(tools, work, {i["rel"]: i["text"]})
        completed = completed and all(rr[c]["completed"] for c in S.CHECKS)
        for c in S.CHECKS:
            if f3_cross(S, c, flags[i["id"]][c]):
                flags[i["id"]][c] = rr[c]["flags"].get(i["rel"], [])
    print(f"solo re-runs for cross-rule-only flags: {len(solo)}")
    by_kind = collections.defaultdict(list)
    for i in staged_items:
        by_kind[i["kind"]].append(i)

    def n_flagged(kind, check=None):
        return sum(1 for i in by_kind[kind] if any(flags[i["id"]][c] for c in ([check] if check else S.CHECKS)))
    gates = {
        "G1": all(g1[c]["code"] == 0 for c in S.CHECKS),
        "G2": g2,
        "G3": n_flagged("IDENTITY") == 0,
        "G4": n_flagged("ROUNDTRIP") == 0,
        "G5": all(n_flagged(k, f3.TARGET[k]) >= 9 for k in ("DANGLING", "ONE_VALUE", "BAD_LOGSOURCE")),
        "G6": set(eq) <= {"query", "parse"} and sum(eq.values()) == len(B),
        "G8": completed,
        "G9": git(sigma, "rev-parse", "HEAD") == SIGMA_COMMIT and not git(sigma, "status", "--porcelain"),
    }
    print("G1 unmutated tree: " + "; ".join(f"{c} exit {g1[c]['code']}" for c in S.CHECKS))
    print(f"controls flagged (by any check): IDENTITY {n_flagged('IDENTITY')} of {len(by_kind['IDENTITY'])}, "
          f"ROUNDTRIP {n_flagged('ROUNDTRIP')} of {len(by_kind['ROUNDTRIP'])}; positive controls flagged by their "
          f"target: DANGLING/SC {n_flagged('DANGLING', 'SC')}, ONE_VALUE/TR {n_flagged('ONE_VALUE', 'TR')}, "
          f"BAD_LOGSOURCE/TL {n_flagged('BAD_LOGSOURCE', 'TL')} (each of 10, need >= 9)")
    for g, ok in gates.items():
        print(f"{g} {'PASS' if ok else 'FAIL'}")
    statuses, facts = score(items if not a.sabotage else _relabel(items, staged_items), flags)
    reasons = collections.Counter((c, r) for i in by_kind["MUTANT"] for c in S.CHECKS for r in flags[i["id"]][c])
    fa, fb, d = facts["arm_a"], facts["arm_b"], facts["derived"]
    print(f"P1 arm A, test_rules.py flags {fa['TR']}; derived {d['TR']}; registered: exactly the derived set -> {statuses[0]}")
    print(f"P2 arm A, sigma check flags {fa['SC']}; derived {d['SC']}; registered: exactly the derived set -> {statuses[1]}")
    print(f"P3 test_logsource.py flags arm A {fa['TL']}, arm B {fb['TL']}; registered: none -> {statuses[2]}")
    print(f"P4 arm B, test_rules.py flags {fb['TR']}, sigma check flags {fb['SC']} (derived {d['arm_b_SC']}); "
          f"registered: TR none, SC exactly the derived set -> {statuses[3]}")
    print(f"mismatches: { {k: len(v) for k, v in facts['mismatch'].items()} }")
    print(f"flag reasons on mutants: {dict(sorted((f'{c}:{r}', n) for (c, r), n in reasons.items()))}")
    print(f"flagged by any static check: arm A {fa['any']} of 1502 ({fa['any_in_surv']} of {facts['surv']} SURV), "
          f"by operator {facts['by_op_arm_a_any']}; arm B {fb['any']} ({fb['any_in_surv']} SURV), by operator "
          f"{facts['by_op_arm_b_any']}")
    print(f"SURV mutants passing every check run (regression, goodlog, SC, TR, TL): arm A {facts['pass_everything_arm_a']}, "
          f"arm B {facts['pass_everything_arm_b']} of {facts['surv']}; rules keeping one (arm B): "
          f"{facts['rules_with_a_surv_mutant_passing_everything_arm_b']} of {facts['rules_with_a_surv_mutant']}")
    n_held = statuses.count("HELD")
    dg = digest(statuses, flags, gates)
    print(f"VERDICT {n_held} of 4 as registered")
    print(f"DIGEST {dg}")
    out_dir = os.path.join(ROOT, "results", "pa_sigma_003")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results_sabotage.json" if a.sabotage else "results.json"), "w") as fh:
        json.dump({"study": "PA-SIGMA-003", "sabotage": a.sabotage, "statuses": statuses, "digest": dg,
                   "gates": gates, "facts": facts, "equivalence": dict(eq),
                   "flag_reasons": {f"{c}:{r}": n for (c, r), n in sorted(reasons.items())},
                   "flagged": {i: {c: r for c, r in f.items() if r} for i, f in sorted(flags.items()) if any(f.values())},
                   "rounds": [{"items": len(r), **{c: {"exit": rr[c]["code"], "seconds": rr[c]["seconds"],
                                                       "flagged": len(rr[c]["flags"])} for c in S.CHECKS}}
                              for r, rr in zip(rounds, results)],
                   "solo": [i["id"] for i in solo]}, fh, indent=1, sort_keys=True)
    if not all(gates.values()):
        print("GATE FAILURE: no verdict")
        return 2
    if RECORDED is None:
        print("RECORDED: not pinned yet")
        return 0
    same = (tuple(statuses), dg) == (tuple(RECORDED[0]), RECORDED[1])
    print(f"RECORDED {'matches' if same else 'DIFFERS'}")
    return 0 if same else 1


def f3_cross(S, check, reasons):
    return cross_rule_only(check, reasons, S.CROSS_RULE)


def _relabel(items, staged_items):
    """Under sabotage the staged texts are originals; scoring still uses the registered item identities."""
    ids = {i["id"] for i in staged_items}
    return [i for i in items if i["id"] in ids]


# ------------------------------------------------------------------ selftest

def selftest():
    f3, S = modules()
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))

    root = "/x/round-1"
    sc_out = ("issue=SigmahqInvalidAllModifierIssue severity=high description=d rule=/x/round-1/rules/windows/a.yml(id)\n"
              "issue=DuplicateTitleIssue severity=high rule=/x/round-1/rules/windows/b.yml(id)\n")
    h = S.attribute("SC", root, sc_out, ["rules/windows/a.yml", "rules/windows/b.yml", "rules/windows/a.ym"])
    ok("SC path attribution", h.get("rules/windows/a.yml") == {"SigmahqInvalidAllModifierIssue"})
    ok("SC cross-rule reason kept", h.get("rules/windows/b.yml") == {"DuplicateTitleIssue"})
    ok("SC no prefix match", "rules/windows/a.ym" not in h)
    tr_out = ("Rule rules/windows/p.yml has the selection (s/k) with a list of only 1 value in detection\n"
              "FAIL: test_selection_list_one_value (__main__.TestRules.test_selection_list_one_value)\n"
              "AssertionError: Lists differ: ['rules/windows/q.yml'] != []\n"
              "FAIL: test_duplicate_detections (__main__.TestRules.test_duplicate_detections)\n"
              "AssertionError: [('rules/x/r.yml', 'rules-threat-hunting/x/r.yml')] != []\nRan 11 tests in 1.0s\n")
    h = S.attribute("TR", root, tr_out, ["rules/windows/p.yml", "rules/windows/q.yml", "rules/x/r.yml",
                                         "rules-threat-hunting/x/r.yml"])
    ok("TR print-only path is not a flag", "rules/windows/p.yml" not in h)
    ok("TR block attribution", h.get("rules/windows/q.yml") == {"test_selection_list_one_value"})
    ok("TR rules/ vs rules-threat-hunting/ kept apart",
       h.get("rules/x/r.yml") == {"test_duplicate_detections"} and h.get("rules-threat-hunting/x/r.yml") == {"test_duplicate_detections"})
    tl_out = ("FAIL: test_invalid_logsource_attributes (__main__.TestRules.test_invalid_logsource_attributes)\n"
              "AssertionError: Lists differ: ['/x/round-1/rules/windows/t.yml'] != []\n"
              "FAIL: test_logsource_value (__main__.TestRules.test_logsource_value)\n"
              "AssertionError: Lists differ: ['/x/round-2/rules/windows/u.yml'] != []\nRan 3 tests in 1.0s\n")
    h = S.attribute("TL", root, tl_out, ["rules/windows/t.yml", "rules/windows/u.yml"])
    ok("TL absolute path under this round's root (D3)", h.get("rules/windows/t.yml") == {"test_invalid_logsource_attributes"})
    ok("TL absolute path under another root is not a flag", "rules/windows/u.yml" not in h)
    ok("completed TR", S.completed("TR", 1, tr_out) and not S.completed("TR", 2, tr_out)
       and not S.completed("TR", 0, "Ran 10 tests in 1s"))
    ok("completed SC", S.completed("SC", 0, "x\n=== Summary ===\n") and not S.completed("SC", 1, "Traceback"))
    ok("cross-rule only", cross_rule_only("SC", ["DuplicateTitleIssue"], S.CROSS_RULE)
       and not cross_rule_only("SC", ["DuplicateTitleIssue", "DanglingDetectionIssue"], S.CROSS_RULE)
       and not cross_rule_only("TL", [], S.CROSS_RULE))
    one = {"detection": {"sel": {"A|contains": ["x"]}, "condition": "sel"}}
    allone = {"detection": {"sel": {"A|contains|all": ["x"]}, "condition": "sel"}}
    clash = {"detection": {"sel": {"A|contains|all": ["x"], "A|contains": ["y", "z"]}, "condition": "sel"}}
    two = {"detection": {"sel": {"A|contains|all": ["x", "y"], "B": "v"}, "condition": "sel"}}
    kw = {"detection": {"keywords": ["only"], "condition": "keywords"}}
    ok("derived_tr", f3.derived_tr(one) and f3.derived_tr(allone) and not f3.derived_tr(two) and not f3.derived_tr(kw))
    ok("derived_sc", f3.derived_sc(allone) and not f3.derived_sc(one) and not f3.derived_sc(two))
    n1, c1, o1 = f3.normalize(one)
    n2, c2, o2 = f3.normalize(allone)
    n3, c3, o3 = f3.normalize(clash)
    ok("normalize one value", c1 and o1 and n1["detection"]["sel"] == {"A|contains": "x"})
    ok("normalize |all", c2 and o2 and n2["detection"]["sel"] == {"A|contains": "x"})
    ok("normalize clash keeps |all", c3 and not o3 and f3.derived_sc(n3) and not f3.derived_tr(n3))
    sch = S.schedule({"r1": ["a", "b", "c"], "r2": ["d"]})
    ok("schedule", sch == [{"r1": "a", "r2": "d"}, {"r1": "b"}, {"r1": "c"}])
    items = [{"kind": "MUTANT", "arm": "A", "id": "A:k1", "key": "k1", "op": "DROP_VALUE", "surv": True,
              "derived_tr": True, "derived_sc": False},
             {"kind": "MUTANT", "arm": "A", "id": "A:k2", "key": "k2", "op": "NEVER_SEL", "surv": True,
              "derived_tr": False, "derived_sc": False},
             {"kind": "MUTANT", "arm": "B", "id": "B:k1", "key": "k1", "op": "DROP_VALUE", "surv": True,
              "derived_tr": False, "derived_sc": False}]
    st, facts = score(items, {"A:k1": {"TR": ["t"], "SC": [], "TL": []}})
    ok("score all held", st == ("HELD", "HELD", "HELD", "HELD") and facts["pass_everything_arm_b"] == 2)
    st, _ = score(items, {})
    ok("score: missing flag refutes P1 only", st == ("REFUTED", "HELD", "HELD", "HELD"))
    st, _ = score(items, {"A:k1": {"TR": ["t"]}, "A:k2": {"SC": ["x"]}})
    ok("score: extra SC flag refutes P2 and P4", st == ("HELD", "REFUTED", "HELD", "REFUTED"))
    st, _ = score(items, {"A:k1": {"TR": ["t"]}, "B:k1": {"TR": ["t"]}})
    ok("score: arm-B TR flag refutes P4", st[3] == "REFUTED")
    d1 = digest(("HELD",), {"x": {"TR": ["t"], "SC": []}}, {"G1": True})
    d2 = digest(("HELD",), {"x": {"TR": ["t"]}, "y": {"SC": []}}, {"G1": True})
    ok("digest ignores empty flags", d1 == d2)
    for name, good in checks:
        print(f"{'PASS' if good else 'FAIL'} {name}")
    bad = sum(1 for _, g in checks if not g)
    print(f"selftest: {len(checks) - bad}/{len(checks)} passed")
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma")
    ap.add_argument("--py3")
    ap.add_argument("--attack")
    ap.add_argument("--d3fend")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
