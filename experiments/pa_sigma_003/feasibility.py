#!/usr/bin/env python3
"""PA-SIGMA-003 population, house-style normalisation, derived expectations and feasibility counts (C-FEAS).

Run before registration. Without --run it stages nothing. With --run it runs only the unmutated tree (G1) and one
round holding the 282 ROUNDTRIP controls (each rule loaded and dumped again with no change), to check that the
dump path alone trips no check. No mutant is staged here.

Population: PA-SIGMA-001's 1,502 BROADENING mutants, rebuilt with its own code (as in PA-SIGMA-002), and the
1,197 of them that PA-SIGMA-002 found pass both behavioural jobs (SURV).

Arm A stages each mutant as PA-SIGMA-001 wrote it. Arm B stages its house-style form: a field list left with one
value becomes that value, and a key carrying |all with one value left loses |all. Sigma gives both forms the same
meaning; gate G6 checks that a backend converts each pair to the same query.

Derived expectations mirror, line for line, the two checks read in SigmaHQ's sources that can see an edit's
shape: test_rules.py's test_selection_list_one_value (DERIVED_TR) and pySigma-validators-sigmahq's
SigmahqInvalidAllModifierValidator (DERIVED_SC). They are predictions about the real checks, not the checks.

Usage (repository root, SigmaHQ venv's Python, i.e. the one PA-SIGMA-002 ran with):
  python experiments/pa_sigma_003/feasibility.py --sigma SIGMA [--run --py3 PY311 --attack JSON --d3fend JSON]
"""
import argparse
import collections
import copy
import glob
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pa_sigma_001"))
import mutants as M  # noqa: E402  (PA-SIGMA-001's operators)
import feasibility as _f1  # noqa: E402,F401  (PA-SIGMA-001's; loaded so the import below cannot shadow it)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


F2 = _load("pa_sigma_002_feasibility", os.path.join(os.path.dirname(HERE), "pa_sigma_002", "feasibility.py"))
S = _load("pa_sigma_003_stage", os.path.join(HERE, "stage.py"))

RESULTS_002 = os.path.join(ROOT, "results", "pa_sigma_002", "results.json")
SET_IDENTITY = "4bb6343d864618f43b895e98a711c7599f29e895173adaec5ef7621d5d596ba0"
ATTACK_SHA256 = "81113ba98afa2928f3dcff62022539f7ce30c315c32e14422f11ff95ce534352"
N_CONTROL_RULES = 10
UNUSED = "PA-SIGMA-003-UNUSED-SELECTION"


def key(m):
    return f"{m['rule']}:{m['k']}:{m['sha']}"


def identity(keys):
    return hashlib.sha256("\n".join(sorted(keys)).encode()).hexdigest()


# ------------------------------------------------------------------ derived expectations (mirrors)

def derived_tr(rule):
    """Mirror of tests/test_rules.py test_selection_list_one_value (SigmaHQ 05d1031)."""
    det = rule.get("detection") or {}
    for name, values in det.items():
        if isinstance(values, list):
            if len(values) == 1 and not isinstance(values[0], str):
                return True
            if values and isinstance(values[0], dict):
                for d in values:
                    for v in d.values():
                        if isinstance(v, list) and len(v) == 1:
                            return True
        if isinstance(values, dict):
            for v in values.values():
                if isinstance(v, list) and len(v) == 1:
                    return True
    return False


def derived_sc(rule):
    """Mirror of SigmahqInvalidAllModifierValidator: a field key with |all and fewer than 2 values."""
    det = rule.get("detection") or {}
    for name, sel in det.items():
        if name in ("condition", "timeframe"):
            continue
        for m in (sel if isinstance(sel, list) else [sel]):
            if isinstance(m, dict):
                for k, v in m.items():
                    parts = str(k).split("|")
                    if parts[0] and "all" in [p.lower() for p in parts[1:]] and (not isinstance(v, list) or len(v) < 2):
                        return True
    return False


# ------------------------------------------------------------------ house style (arm B)

def _norm_map(m):
    """(new map, changed, ok). One value in a list -> the value; |all on one value -> dropped if no key clash."""
    out, changed, ok = {}, False, True
    items = list(m.items())
    for k, v in items:
        if isinstance(v, list) and len(v) == 1:
            v, changed = v[0], True
        parts = str(k).split("|")
        if parts[0] and "all" in [p.lower() for p in parts[1:]] and not isinstance(v, list):
            nk = "|".join([parts[0]] + [p for p in parts[1:] if p.lower() != "all"])
            if nk in m or nk in out:
                ok = False
            else:
                k, changed = nk, True
        out[k] = v
    return out, changed, ok


def normalize(rule):
    """(house-style copy, changed, ok). Keyword lists are left alone (test_rules.py accepts one string keyword)."""
    r = copy.deepcopy(rule)
    det = r.get("detection") or {}
    changed, ok = False, True
    for name in list(det):
        if name in ("condition", "timeframe"):
            continue
        sel = det[name]
        if isinstance(sel, dict):
            det[name], c, o = _norm_map(sel)
            changed, ok = changed or c, ok and o
        elif isinstance(sel, list) and sel and all(isinstance(x, dict) for x in sel):
            new = []
            for m in sel:
                nm, c, o = _norm_map(m)
                new.append(nm)
                changed, ok = changed or c, ok and o
            det[name] = new
    return r, changed, ok


# ------------------------------------------------------------------ population and items

def population(sigma):
    """Mutants (PA-SIGMA-001's broadening set), originals and controls per rule, and SURV keys."""
    muts = F2.broadening_set(sigma)
    rules = {}
    for m in muts:
        rules.setdefault(m["rule"], m["path"])
    originals, controls = {}, {}
    for rid, rel in sorted(rules.items()):
        with open(os.path.join(sigma, rel), "rb") as fh:
            text = fh.read().decode("utf-8")
        originals[rid] = text
        ctl, why = M.enumerate_mutants(text)
        assert not why, (rid, why)
        controls[rid] = {c["op"]: c["text"] for c in ctl if c["op"] in ("IDENTITY", "ROUNDTRIP")}
        assert controls[rid]["IDENTITY"] == text
    with open(RESULTS_002) as fh:
        caught = set(json.load(fh)["results"]["caught_mutants"])
    surv = {key(m) for m in muts if key(m) not in caught}
    return muts, rules, originals, controls, surv, caught


def _first_string_field(rule):
    det = rule["detection"]
    names = [k for k in det if k not in ("condition", "timeframe")]
    for n in names:
        sel = det[n]
        for m in (sel if isinstance(sel, list) else [sel]):
            if isinstance(m, dict):
                for k, v in m.items():
                    if isinstance(v, str):
                        return n, m, k
    return None


def positive_controls(rules, originals):
    """Ten rules (lowest ids with a scalar string field). DANGLING -> SC, ONE_VALUE -> TR, BAD_LOGSOURCE -> TL."""
    out = {}
    for rid in sorted(rules):
        if len(out) == N_CONTROL_RULES:
            break
        rule = yaml.safe_load(originals[rid])
        hit = _first_string_field(rule)
        if hit is None:
            continue
        name, _, field = hit
        d = copy.deepcopy(rule)
        d["detection"] = {**{k: v for k, v in d["detection"].items() if k != "condition"},
                          "pa_sigma_003_unused": {field.split("|")[0]: UNUSED},
                          "condition": d["detection"]["condition"]}
        o = copy.deepcopy(rule)
        sel = o["detection"][name]
        for m in (sel if isinstance(sel, list) else [sel]):
            if isinstance(m, dict) and field in m and isinstance(m[field], str):
                m[field] = [m[field]]
                break
        b = copy.deepcopy(rule)
        b["logsource"]["pa_sigma_003_attr"] = "x"
        out[rid] = {"DANGLING": M._dump(d), "ONE_VALUE": M._dump(o), "BAD_LOGSOURCE": M._dump(b)}
    return out


TARGET = {"DANGLING": "SC", "ONE_VALUE": "TR", "BAD_LOGSOURCE": "TL"}


def build_items(sigma, sabotage=False):
    """Every staged item: dict(id, kind, arm, rule, rel, op, surv, text). Sabotage stages each mutant's original."""
    muts, rules, originals, controls, surv, _ = population(sigma)
    items = []
    for rid, rel in sorted(rules.items()):
        for op in ("IDENTITY", "ROUNDTRIP"):
            items.append({"id": f"{op}:{rid}", "kind": op, "arm": "-", "rule": rid, "rel": rel, "op": op,
                          "surv": None, "text": controls[rid][op]})
    for rid, ctl in sorted(positive_controls(rules, originals).items()):
        for op, text in ctl.items():
            items.append({"id": f"{op}:{rid}", "kind": op, "arm": "-", "rule": rid, "rel": rules[rid], "op": op,
                          "surv": None, "text": text})
    for m in sorted(muts, key=key):
        rule = yaml.safe_load(m["text"])
        norm, changed, ok = normalize(rule)
        text_a = originals[m["rule"]] if sabotage else m["text"]
        items.append({"id": "A:" + key(m), "kind": "MUTANT", "arm": "A", "rule": m["rule"], "rel": m["path"],
                      "op": m["op"], "surv": key(m) in surv, "text": text_a, "key": key(m),
                      "derived_tr": derived_tr(rule), "derived_sc": derived_sc(rule)})
        if changed:
            text_b = originals[m["rule"]] if sabotage else M._dump(norm)
            items.append({"id": "B:" + key(m), "kind": "MUTANT", "arm": "B", "rule": m["rule"], "rel": m["path"],
                          "op": m["op"], "surv": key(m) in surv, "text": text_b, "key": key(m), "norm_ok": ok,
                          "raw_text": m["text"], "derived_tr": derived_tr(norm), "derived_sc": derived_sc(norm)})
    return items


def lucene(text):
    """One query string list from pySigma's Lucene backend, or None if the rule cannot be converted."""
    from sigma.backends.elasticsearch import LuceneBackend
    from sigma.collection import SigmaCollection
    try:
        return LuceneBackend().convert(SigmaCollection.from_yaml(text))
    except Exception:
        return None


def equivalent(raw_text, norm_text):
    """G6 for one arm-B pair: 'query' if the Lucene queries are equal, 'parse' if the backend cannot convert the
    rule but pySigma parses both to the same detection, else 'DIFFERENT'."""
    qa, qb = lucene(raw_text), lucene(norm_text)
    if qa is not None and qb is not None:
        return "query" if qa == qb else "DIFFERENT"
    from sigma.rule import SigmaRule
    da = SigmaRule.from_yaml(raw_text).to_dict()["detection"]
    db = SigmaRule.from_yaml(norm_text).to_dict()["detection"]
    return "parse" if da == db else "DIFFERENT"


def versions(py3):
    code = ("import importlib.metadata as m\nfor p in ('pysigma','sigma-cli','pysigma-validators-sigmahq','pyyaml',"
            "'colorama'):\n print(p, m.version(p))\nimport sys; print('python', sys.version.split()[0])")
    return subprocess.run([py3, "-I", "-c", code], capture_output=True, text=True).stdout.strip().replace("\n", " | ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma", required=True)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--py3")
    ap.add_argument("--attack")
    ap.add_argument("--d3fend")
    a = ap.parse_args()
    sigma = os.path.abspath(a.sigma)
    commit = subprocess.run(["git", "-C", sigma, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    print(f"SigmaHQ {commit}")
    muts, rules, originals, controls, surv, caught = population(sigma)
    print(f"0. broadening mutants rebuilt {len(muts)} in {len(rules)} rules; identity {identity(key(m) for m in muts)} "
          f"(registered {SET_IDENTITY[:8]}...: {identity(key(m) for m in muts) == SET_IDENTITY})")
    print(f"   PA-SIGMA-002 caught {len(caught)}; SURV (pass both behavioural jobs) {len(surv)}; "
          f"SURV identity {identity(surv)}")
    ops = collections.Counter(m["op"] for m in muts)
    sops = collections.Counter(m["op"] for m in muts if key(m) in surv)
    print(f"1. by operator: all {dict(sorted(ops.items()))}; SURV {dict(sorted(sops.items()))}")
    orig_tr = sum(derived_tr(yaml.safe_load(t)) for t in originals.values())
    orig_sc = sum(derived_sc(yaml.safe_load(t)) for t in originals.values())
    print(f"2. originals with a derived TR or SC flag (must be 0, since the unmutated checks pass): TR {orig_tr}, SC {orig_sc}")
    items = build_items(sigma)
    A = [i for i in items if i["arm"] == "A"]
    B = [i for i in items if i["arm"] == "B"]

    def tally(rows, f):
        c = collections.Counter(i["op"] for i in rows if f(i))
        return f"{sum(c.values()):4d} {dict(sorted(c.items()))}"
    for label, rows in (("all", A), ("SURV", [i for i in A if i["surv"]])):
        print(f"3. arm A {label:4s}: DERIVED_TR {tally(rows, lambda i: i['derived_tr'])}")
        print(f"            DERIVED_SC {tally(rows, lambda i: i['derived_sc'])}")
        print(f"            DERIVED_TR or SC {tally(rows, lambda i: i['derived_tr'] or i['derived_sc'])}")
    print(f"4. arm B: {len(B)} mutants change under house style ({sum(1 for i in B if i['surv'])} in SURV); "
          f"|all kept because dropping it would duplicate a key: {sum(1 for i in B if not i['norm_ok'])} "
          f"({sum(1 for i in B if not i['norm_ok'] and i['surv'])} in SURV); "
          f"arm B DERIVED_TR {sum(i['derived_tr'] for i in B)}, DERIVED_SC {sum(i['derived_sc'] for i in B)} "
          f"({sum(i['derived_sc'] for i in B if i['surv'])} in SURV)")
    eq = collections.Counter(equivalent(i["raw_text"], i["text"]) for i in B)
    print(f"5. arm B equivalence (G6): {dict(sorted(eq.items()))} "
          "(query: same Lucene query; parse: backend cannot convert, same pySigma detection)")
    per_rule = collections.Counter(i["rel"] for i in items)
    kinds = collections.Counter(i["kind"] for i in items)
    print(f"6. staged items {len(items)} {dict(sorted(kinds.items()))}; rounds needed {max(per_rule.values())} "
          f"(items per rule: min {min(per_rule.values())}, median {sorted(per_rule.values())[len(per_rule) // 2]})")
    d3 = 0
    for p in glob.glob(os.path.join(sigma, "rules*", "**", "*.yml"), recursive=True):
        with open(p, encoding="utf-8") as fh:
            d3 += any(line.strip().lower().startswith("- d3fend.") for line in fh)
    print(f"7. rule files under rules* with a d3fend tag: {d3}")
    if not a.run:
        return 0
    with open(a.attack, "rb") as fh:
        att = hashlib.sha256(fh.read()).hexdigest()
    print(f"8. tools: {versions(a.py3)} | ATT&CK file sha256 {att} (pinned: {att == ATTACK_SHA256})")
    tools = S.Tools(sigma, a.py3, a.attack, a.d3fend)
    work = os.path.join(os.path.expanduser("~"), "pa_sigma_003_rounds")
    os.makedirs(work, exist_ok=True)
    g1 = S.run_round(tools, work, {})
    print("9. G1 unmutated tree: " + "; ".join(f"{c} exit {g1[c]['code']} completed {g1[c]['completed']} {g1[c]['seconds']}s"
                                              for c in S.CHECKS))
    rt = S.run_round(tools, work, {rel: controls[rid]["ROUNDTRIP"] for rid, rel in rules.items()})
    print(f"10. ROUNDTRIP pre-check, {len(rules)} rules in one round: " + "; ".join(
        f"{c} exit {rt[c]['code']} completed {rt[c]['completed']} flagged {len(rt[c]['flags'])}" for c in S.CHECKS))
    for c in S.CHECKS:
        for rel, why in list(rt[c]["flags"].items())[:5]:
            print(f"    {c} {rel} {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
