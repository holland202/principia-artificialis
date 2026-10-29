#!/usr/bin/env python3
"""PA-SIGMA-001 post-hoc analysis (EXPLORATORY, written after run 1 was seen; not registered).

Usage: python posthoc.py RESULTS_JSON SIGMA_CHECKOUT

Reads the committed results.json and, for rule structure only, the SigmaHQ checkout at the pinned commit.
Prints counts, rule IDs and condition shapes; never rule text beyond the condition's operator skeleton and
never event content. Every question here was asked after looking at run 1, so nothing it prints is a
registered prediction (C-EXPLORE, PA-SIGMA-001-X5 in FORKS.md).
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from feasibility import RULE_PATHS, load_runner, sample_events  # noqa: E402

import yaml  # noqa: E402

NARROW, BROAD = "NARROWING", "BROADENING"


def skeleton(cond):
    """The condition with selection names replaced by S, so its shape can be counted without rule text."""
    if not isinstance(cond, str):
        return "<list>"
    out = re.sub(r"\b(1|all|any)\s+of\s+[^\s()]+", lambda m: f"{m.group(1)}-of-X", cond)
    out = re.sub(r"\b(?!and\b|or\b|not\b|1-of-X\b|all-of-X\b|any-of-X\b)[A-Za-z_][A-Za-z0-9_*]*", "S", out)
    return re.sub(r"\s+", " ", out).strip()


def positive_or(cond):
    """Heuristic: True if the condition has an alternative between positive terms, that is an 'or' in a
    group that is not negated, or a '1 of'/'any of' that is not negated. Post hoc and approximate: it does not
    check that both sides of an 'or' are positive."""
    if not isinstance(cond, str):
        return False
    toks = re.findall(r"\(|\)|\b(?:1|any|all)\s+of\s+[^\s()]+|\band\b|\bor\b|\bnot\b|[^\s()]+", cond, re.I)
    neg = [False]          # negation of the enclosing group
    pending = False        # a 'not' waiting for its term
    for t in toks:
        lt = t.lower()
        if lt == "not":
            pending = not pending
        elif t == "(":
            neg.append(neg[-1] ^ pending)
            pending = False
        elif t == ")":
            neg.pop()
        elif lt == "or":
            if not neg[-1]:
                return True
        elif lt == "and":
            pass
        else:  # a term: a selection name or an 'N of X'
            if re.match(r"^(1|any)\s+of\s+", lt) and not (neg[-1] ^ pending):
                return True
            pending = False
    return False


def main(results_json, sigma):
    with open(results_json, encoding="utf-8") as f:
        res = json.load(f)
    muts = res["mutants"]
    runner = load_runner(sigma)
    os.chdir(sigma)
    rules, _, _ = runner.find_rules_with_tests(RULE_PATHS)
    rinfo = {r["id"]: r for r in rules}
    cond = {}
    for r in rules:
        with open(r["path"], encoding="utf-8") as f:
            det = yaml.safe_load(f)["detection"]
        cond[r["id"]] = det["condition"]

    by_rule = collections.defaultdict(dict)
    for m in muts:
        by_rule[m["rule"]][m["k"]] = m
    ident = {rid: ms[0] for rid, ms in by_rule.items()}

    print("Q0 headline fractions from the registered run (scored operator mutants; all 471 rules included)")
    ops = [m for m in muts if m["op"] in ("DROP_VALUE", "DROP_FIELD", "NEVER_SEL")]
    for label, sel in (("all BROADENING", lambda m: m["dir"] == BROAD),
                       ("all NARROWING", lambda m: m["dir"] == NARROW),
                       ("DROP_VALUE NARROWING", lambda m: m["op"] == "DROP_VALUE" and m["dir"] == NARROW),
                       ("DROP_FIELD NARROWING (an exclusion broadened)", lambda m: m["op"] == "DROP_FIELD" and m["dir"] == NARROW),
                       ("NEVER_SEL NARROWING (a positive selection disabled)", lambda m: m["op"] == "NEVER_SEL" and m["dir"] == NARROW),
                       ("NEVER_SEL BROADENING (an exclusion switched off)", lambda m: m["op"] == "NEVER_SEL" and m["dir"] == BROAD)):
        ms = [m for m in ops if sel(m)]
        s = sum(m["out"] == "SURVIVED" for m in ms)
        print(f"  {label}: SURVIVED {s} of {len(ms)} ({100 * s / len(ms):.1f}%)")
    nar_rules = collections.defaultdict(list)
    for m in ops:
        if m["dir"] == NARROW:
            nar_rules[m["rule"]].append(m["out"])
    w = sum("SURVIVED" in v for v in nar_rules.values())
    print(f"  rules with a surviving NARROWING mutant: {w} of {len(nar_rules)} ({100 * w / len(nar_rules):.1f}%)")

    print("\nQ1 D2 exceptions: tests where IDENTITY's count differs from the sample's events")
    for rid in sorted(by_rule):
        for t, n in zip(rinfo[rid]["tests"], ident[rid]["counts"]):
            ev = sample_events(t["path"], t.get("type"))
            exp = t.get("match_count")
            if n != ev:
                print(f"  {rid} {t['type']}: IDENTITY count {n}, sample events {ev}, match_count {exp}")

    print("\nQ1b the same with JSON samples counted as documents, not lines (feasibility.py counted non-empty "
          "lines for every non-EVTX sample; a 'json' sample is one JSON document)")
    def events(t):
        if t.get("type") == "json":
            with open(t["path"], encoding="utf-8") as f:
                doc = json.load(f)
            return len(doc) if isinstance(doc, list) else 1
        return sample_events(t["path"], t.get("type"))
    n_le = n_le_all = n_all = 0
    more = []
    for rid in sorted(by_rule):
        for t, n in zip(rinfo[rid]["tests"], ident[rid]["counts"]):
            ev = events(t)
            exp = t.get("match_count") or 1
            n_all += n == ev
            if ev <= exp:
                n_le += 1
                n_le_all += n == ev
            else:
                more.append(rid)
    print(f"  tests whose sample holds no more events than the expected count: {n_le}; more: {len(more)}")
    print(f"  IDENTITY's count equals the sample's events: {n_all} of 474; among the {n_le}: {n_le_all}")

    print("\nQ2 NARROWING survivors whose match count changed (the drop stayed at or above match_count)")
    for m in muts:
        if m["dir"] == NARROW and m["out"] == "SURVIVED" and m.get("changed"):
            print(f"  {m['rule']} {m['op']} {m['site']}: counts {m['counts']}, IDENTITY {ident[m['rule']]['counts']}, "
                  f"match_count {m['expect']}")

    print("\nQ3 NARROWING survivors carrying the runner's over-match warning, by rule")
    ow = collections.Counter(m["rule"] for m in muts if m["dir"] == NARROW and m["out"] == "SURVIVED" and m["over"])
    for rid, n in sorted(ow.items()):
        print(f"  {rid}: {n} (IDENTITY counts {ident[rid]['counts']}, match_count {ident[rid]['expect']}, "
              f"IDENTITY over-match {ident[rid]['over']})")

    print("\nQ4 rules in which no NARROWING mutant is KILLED")
    for rid in sorted(by_rule):
        nar = [m for m in by_rule[rid].values() if m["dir"] == NARROW]
        if nar and not any(m["out"] == "KILLED" for m in nar):
            ops = collections.Counter(m["op"] for m in nar)
            print(f"  {rid}: {len(nar)} narrowing mutants {dict(ops)}; IDENTITY counts {ident[rid]['counts']} "
                  f"match_count {ident[rid]['expect']}; condition shape: {skeleton(cond[rid])}")

    print("\nQ5 NEVER_SEL NARROWING outcome by whether the condition lets two positive selections stand in for "
          "each other ('or' outside a negation, or '1 of'/'any of')")
    hand = {"selection": False, "selection and not filter": False, "selection and not 1 of filter_*": False,
            "1 of selection_*": True, "all of selection_*": False, "a or b": True, "a and not (f1 or f2)": False,
            "selection and not 1 of filter_* and 1 of sel_*": True,
            "all of selection_* and not 1 of filter_main_*": False, "(a or b) and not c": True,
            "not (a or b)": False, "x and (y or z)": True}
    ok = sum(positive_or(c_) == want for c_, want in hand.items())
    print(f"  heuristic checked on hand-written conditions: {ok} of {len(hand)} as expected")
    tab = collections.Counter()
    rules_tab = collections.defaultdict(set)
    for m in muts:
        if m["op"] == "NEVER_SEL" and m["dir"] == NARROW:
            shape = "positive OR" if positive_or(cond[m["rule"]]) else "no positive OR"
            tab[(shape, m["out"])] += 1
            rules_tab[(shape, m["out"])].add(m["rule"])
    for shape in ("positive OR", "no positive OR"):
        k, s = tab[(shape, "KILLED")], tab[(shape, "SURVIVED")]
        print(f"  {shape:15s}: KILLED {k:4d} SURVIVED {s:4d} (rules with a survivor {len(rules_tab[(shape, 'SURVIVED')])})")

    print("\nQ6 the 10 tests whose sample holds more events than match_count: BROADENING mutants of those rules")
    more = []
    for rid in sorted(by_rule):
        for t in rinfo[rid]["tests"]:
            ev = sample_events(t["path"], t.get("type"))
            if ev > (t.get("match_count") or 1):
                more.append((rid, ev, t.get("match_count")))
    for rid, ev, exp in more:
        b = [m for m in by_rule[rid].values() if m["dir"] == BROAD]
        ch = sum(1 for m in b if m.get("changed"))
        print(f"  {rid}: sample events {ev}, match_count {exp}, IDENTITY {ident[rid]['counts']}; "
              f"BROADENING mutants {len(b)}, count changed {ch}")
    print("  the same with JSON samples counted as documents (Q1b): EVTX tests only")
    tot_b = tot_ch = n_t = 0
    for rid in sorted(by_rule):
        for t in rinfo[rid]["tests"]:
            if t.get("type") != "evtx":
                continue
            ev = sample_events(t["path"], "evtx")
            if ev > (t.get("match_count") or 1):
                n_t += 1
                b = [m for m in by_rule[rid].values() if m["dir"] == BROAD]
                tot_b += len(b)
                tot_ch += sum(1 for m in b if m.get("changed"))
    print(f"  tests {n_t}; BROADENING mutants of their rules {tot_b}; count changed {tot_ch}")

    print("\nQ7 the three rules with EVTX and JSON tests: mutants whose two tests disagree (one passes, one fails)")
    for rid in sorted(by_rule):
        tests = rinfo[rid]["tests"]
        if len(tests) < 2:
            continue
        dis = 0
        for m in by_rule[rid].values():
            if m["out"] in ("KILLED", "SURVIVED"):
                ok = [(c >= x) if x is not None else (c > 0) for c, x in zip(m["counts"], m["expect"])]
                dis += len(set(ok)) > 1
        print(f"  {rid}: {len(by_rule[rid])} mutants incl. controls; tests disagree on {dis}")

    print("\nQ7b JSON tests across every mutant of those three rules (controls included): how often the JSON test "
          "passed by the runner's rule, and how often its EVTX test failed at the same time")
    j_pass = j_total = evtx_fail_json_pass = 0
    for rid in sorted(by_rule):
        tests = rinfo[rid]["tests"]
        if len(tests) < 2:
            continue
        ji = [i for i, t in enumerate(tests) if t.get("type") != "evtx"][0]
        ei = [i for i, t in enumerate(tests) if t.get("type") == "evtx"][0]
        for m in by_rule[rid].values():
            if m["out"] not in ("KILLED", "SURVIVED"):
                continue
            c, x = m["counts"], m["expect"]
            jp = (c[ji] >= x[ji]) if x[ji] is not None else (c[ji] > 0)
            ep = (c[ei] >= x[ei]) if x[ei] is not None else (c[ei] > 0)
            j_total += 1
            j_pass += jp
            evtx_fail_json_pass += (not ep) and jp
    print(f"  JSON test passed for {j_pass} of {j_total} mutants; EVTX failed while JSON passed: {evtx_fail_json_pass}")

    print("\nQ8 KILLED fraction by operator and direction, per rule (rules with at least one such mutant)")
    for op in ("DROP_VALUE", "DROP_FIELD", "NEVER_SEL"):
        fr = []
        for rid in sorted(by_rule):
            ms = [m for m in by_rule[rid].values() if m["op"] == op and m["dir"] == NARROW]
            if ms:
                fr.append(sum(m["out"] == "KILLED" for m in ms) / len(ms))
        if fr:
            fr.sort()
            print(f"  {op:10s} NARROWING: rules {len(fr)}, median kill fraction {fr[len(fr) // 2]:.3f}, "
                  f"all killed {sum(x == 1 for x in fr)}, none killed {sum(x == 0 for x in fr)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
