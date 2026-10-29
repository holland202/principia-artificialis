#!/usr/bin/env python3
"""PA-SIGMA-001 mutation operators for Sigma rules. Standard library plus PyYAML only.

A mutant is the rule with exactly one change to its `detection` section. Each operator's direction
(BROADENING: the rule can match more; NARROWING: it can match less) follows from Sigma's semantics
and from the polarity of the selection in the condition:
  - keys of a selection map are ANDed; values in a list are ORed, unless the key carries `|all`;
  - a selection reached through an odd number of `not` is NEGATIVE (an exclusion), else POSITIVE.

Operators (one mutant per site, sites in YAML order, at most CAP per rule per operator):
  DROP_VALUE   remove one value from a list of two or more scalar values
  DROP_FIELD   remove one key from a selection map with two or more keys
  NEVER_SEL    make one whole selection unable to match (add a key that cannot match)
Controls (one each per rule):
  IDENTITY     the original file, byte for byte
  ROUNDTRIP    the rule loaded and dumped again with no change (tests the YAML path itself)
  NEVER_FIRE   the condition ANDed with a selection that cannot match, so the rule never fires

Rules whose condition is a list, uses an aggregation (`|` or `count(`), or names one selection with
both polarities are reported as SKIPPED with the reason, never mutated.
"""
import copy
import hashlib
import re

import yaml

NEVER = "PA-SIGMA-001-NEVER-MATCH-7f3a"
CAP = 25
OPERATORS = ("DROP_VALUE", "DROP_FIELD", "NEVER_SEL")
CONTROLS = ("IDENTITY", "ROUNDTRIP", "NEVER_FIRE")

_TOKEN = re.compile(r"\s*(\(|\)|\band\b|\bor\b|\bnot\b|\b(?:1|all|any)\s+of\s+[^\s()]+|[^\s()]+)", re.I)


class Skip(Exception):
    pass


def _tokens(condition):
    pos, out = 0, []
    while pos < len(condition):
        m = _TOKEN.match(condition, pos)
        if not m or m.end() == pos:
            raise Skip(f"untokenizable condition at {pos}")
        tok = m.group(1)
        out.append(tok)
        pos = m.end()
        while pos < len(condition) and condition[pos].isspace():
            pos += 1
    return out


def _expand(pattern, names):
    if pattern.lower() == "them":
        return [n for n in names if not n.startswith("_")]
    rx = re.compile("^" + re.escape(pattern).replace(r"\*", ".*") + "$")
    hit = [n for n in names if rx.match(n)]
    if not hit:
        raise Skip(f"pattern {pattern!r} matches no selection")
    return hit


def polarity(condition, names):
    """Return {selection name: {+1, -1}} for every selection the condition reaches."""
    if not isinstance(condition, str):
        raise Skip("condition is a list")
    if "|" in condition or "count(" in condition.lower():
        raise Skip("aggregation in condition")
    toks = _tokens(condition)
    seen = {}
    i = 0

    def expr(sign):
        nonlocal i
        term(sign)
        while i < len(toks) and toks[i].lower() in ("and", "or"):
            i += 1
            term(sign)

    def term(sign):
        nonlocal i
        if i >= len(toks):
            raise Skip("condition ends early")
        t = toks[i]
        low = t.lower()
        if low == "not":
            i += 1
            term(-sign)
        elif t == "(":
            i += 1
            expr(sign)
            if i >= len(toks) or toks[i] != ")":
                raise Skip("unbalanced parentheses")
            i += 1
        elif re.match(r"^(1|all|any)\s+of\s+", low):
            for n in _expand(t.split()[-1], names):
                seen.setdefault(n, set()).add(sign)
            i += 1
        elif low in ("and", "or", ")"):
            raise Skip(f"unexpected {t!r}")
        else:
            if t not in names:
                raise Skip(f"unknown selection {t!r}")
            seen.setdefault(t, set()).add(sign)
            i += 1

    expr(+1)
    if i != len(toks):
        raise Skip("trailing tokens in condition")
    return seen


def _dump(rule):
    return yaml.safe_dump(rule, sort_keys=False, allow_unicode=True, width=10_000)


def _field_of(key):
    return key.split("|")[0]


def _has_all(key):
    return "all" in [m.lower() for m in key.split("|")[1:]]


def _never_key(sel_map, rule_fields):
    """A key not already in the map whose value NEVER cannot match."""
    for field in rule_fields:
        for cand in (field, f"{field}|contains", f"{field}|startswith", f"{field}|endswith"):
            if cand not in sel_map:
                return cand
    return None


def _string_fields(detection, names):
    """Fields of the rule's selections whose values are strings, in YAML order."""
    out = []
    for n in names:
        sel = detection[n]
        maps = sel if isinstance(sel, list) else [sel]
        for m in maps:
            if isinstance(m, dict):
                for k, v in m.items():
                    vals = v if isinstance(v, list) else [v]
                    if vals and all(isinstance(x, str) for x in vals) and _field_of(k) not in out:
                        out.append(_field_of(k))
    return out


def _never_selection(sel, fields):
    """A copy of one selection that cannot match, or None if no safe construction exists."""
    if isinstance(sel, dict):
        key = _never_key(sel, fields)
        if key is None:
            return None
        new = dict(sel)
        new[key] = NEVER
        return new
    if isinstance(sel, list) and sel and all(isinstance(x, dict) for x in sel):
        out = []
        for m in sel:
            key = _never_key(m, fields)
            if key is None:
                return None
            nm = dict(m)
            nm[key] = NEVER
            out.append(nm)
        return out
    if isinstance(sel, list) and sel and all(isinstance(x, (str, int)) for x in sel):
        return [NEVER]  # a keyword list that cannot match
    return None


def enumerate_mutants(text):
    """Return (mutants, skipped_reason). Each mutant: dict(op, direction, site, text)."""
    rule = yaml.safe_load(text)
    det = rule.get("detection") if isinstance(rule, dict) else None
    if not isinstance(det, dict) or "condition" not in det:
        return [], "no detection/condition"
    names = [k for k in det if k != "condition" and k != "timeframe"]
    try:
        pol = polarity(det["condition"], names)
    except Skip as e:
        return [], str(e)
    mixed = [n for n, s in pol.items() if len(s) > 1]
    if mixed:
        return [], f"selection with both polarities: {mixed[0]}"
    fields = _string_fields(det, names)
    out = [{"op": "IDENTITY", "direction": "CONTROL", "site": "-", "text": text},
           {"op": "ROUNDTRIP", "direction": "CONTROL", "site": "-", "text": _dump(rule)}]
    nf = copy.deepcopy(rule)
    nf["detection"]["pa_sigma_001_never"] = {fields[0]: NEVER} if fields else [NEVER]
    nf["detection"]["condition"] = f"({det['condition']}) and pa_sigma_001_never"
    out.append({"op": "NEVER_FIRE", "direction": "CONTROL", "site": "-", "text": _dump(nf)})
    counts = {op: 0 for op in OPERATORS}

    def add(op, direction, site, new_rule):
        if counts[op] >= CAP:
            return
        counts[op] += 1
        out.append({"op": op, "direction": direction, "site": site, "text": _dump(new_rule)})

    for n in names:
        if n not in pol:
            continue
        sign = +1 if pol[n] == {+1} else -1
        sel = det[n]
        maps = sel if isinstance(sel, list) and all(isinstance(x, dict) for x in sel) else (
            [sel] if isinstance(sel, dict) else None)
        # DROP_VALUE on keyword lists
        if isinstance(sel, list) and len(sel) >= 2 and all(isinstance(x, (str, int)) for x in sel):
            for j in range(len(sel)):
                r = copy.deepcopy(rule)
                del r["detection"][n][j]
                add("DROP_VALUE", "NARROWING" if sign > 0 else "BROADENING", f"{n}[{j}]", r)
        if maps is not None:
            for mi, m in enumerate(maps):
                for k, v in m.items():
                    if isinstance(v, list) and len(v) >= 2 and all(isinstance(x, (str, int, float)) for x in v):
                        narrowing = (sign > 0) != _has_all(k)
                        for j in range(len(v)):
                            r = copy.deepcopy(rule)
                            target = r["detection"][n] if isinstance(r["detection"][n], dict) else r["detection"][n][mi]
                            del target[k][j]
                            add("DROP_VALUE", "NARROWING" if narrowing else "BROADENING", f"{n}/{mi}/{k}[{j}]", r)
                if len(m) >= 2:
                    for k in list(m):
                        r = copy.deepcopy(rule)
                        target = r["detection"][n] if isinstance(r["detection"][n], dict) else r["detection"][n][mi]
                        del target[k]
                        add("DROP_FIELD", "BROADENING" if sign > 0 else "NARROWING", f"{n}/{mi}/{k}", r)
        never_sel = _never_selection(sel, fields)
        if never_sel is not None:
            r = copy.deepcopy(rule)
            r["detection"][n] = never_sel
            add("NEVER_SEL", "NARROWING" if sign > 0 else "BROADENING", n, r)
    seen, unique = set(), []
    for m in out:
        h = hashlib.sha256(m["text"].encode()).hexdigest()
        if m["op"] not in CONTROLS and h in seen:
            continue
        seen.add(h)
        m["sha256"] = h
        unique.append(m)
    return unique, None
