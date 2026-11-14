"""CST-001 scorer: deterministic, fail-closed. A pair counts as correct only if BOTH versions are decided correctly.

Input: the case pairs (cases.build) and a mapping {(pair_id, version): raw model output text}.
A response's decision is the LAST line of the form "DECISION: CONFIRMED" or "DECISION: INSUFFICIENT" (case and
surrounding whitespace ignored). No such line, or a missing response, is MALFORMED and counts as wrong.
Blanket acceptance (always CONFIRMED) and blanket abstention (always INSUFFICIENT) both score 0 pairs.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-14.
"""
import re

DECISION = re.compile(r"^\s*\**\s*DECISION\s*:\s*\**\s*(CONFIRMED|INSUFFICIENT)\s*\**\s*\.?\s*$", re.I)


def parse(text):
    if not isinstance(text, str):
        return "MALFORMED"
    found = [m.group(1).upper() for line in text.splitlines() for m in [DECISION.match(line)] if m]
    return found[-1] if found else "MALFORMED"


def score(pairs, outputs):
    """Return per-pair records and totals. Never raises on bad outputs; missing data is counted, not dropped."""
    rows = []
    for p in pairs:
        decided = {}
        for v in p["versions"]:
            key = (p["pair"], v["version"])
            decided[v["version"]] = parse(outputs.get(key))
        ok = {v["version"]: decided[v["version"]] == v["answer"] for v in p["versions"]}
        rows.append({"pair": p["pair"], "hop": p["hop"], "order": p["order"], "domain": p["domain"],
                     "shared": decided["SHARED"], "independent": decided["INDEPENDENT"],
                     "pair_correct": all(ok.values())})
    n = len(rows)
    tot = {
        "pairs": n,
        "pair_correct": sum(r["pair_correct"] for r in rows),
        "shared_correct": sum(r["shared"] == "INSUFFICIENT" for r in rows),
        "independent_correct": sum(r["independent"] == "CONFIRMED" for r in rows),
        "malformed": sum((r["shared"] == "MALFORMED") + (r["independent"] == "MALFORMED") for r in rows),
    }
    return rows, tot
