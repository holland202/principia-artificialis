"""Claude's CST source-graph oracle and shortcut negative controls. Semantics: SEMANTICS.md. Stdlib only.

Not blind: the author had read Codex's oracle (instrument.py at d52981a) before writing this. See SEMANTICS.md.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-16.
"""
import re


class Invalid(ValueError):
    """The case is malformed; it has no correct decision."""


def _root(nodes, start):
    seen, cur = [], start
    while True:
        if cur not in nodes:
            raise Invalid(f"dangling reference {cur!r}")
        if cur in seen:
            raise Invalid(f"cycle through {cur!r}")
        seen.append(cur)
        parent = nodes[cur]
        if parent is None:
            return cur
        if not isinstance(parent, str):
            raise Invalid(f"node {cur!r}: parent must be a node ID or null (multi-parent not allowed in v1)")
        cur = parent


def _classes(nodes, same_as):
    """Union-find over originals joined by same_as."""
    rep = {n: n for n, p in nodes.items() if p is None}

    def find(x):
        while rep[x] != x:
            rep[x] = rep[rep[x]]
            x = rep[x]
        return x
    for pair in same_as or []:
        if len(pair) != 2 or any(x not in rep for x in pair):
            raise Invalid(f"same_as must join two existing originals: {pair!r}")
        a, b = find(pair[0]), find(pair[1])
        rep[a] = b
    return find


def decide(case):
    """Return 'CONFIRMED' or 'INSUFFICIENT'; raise Invalid for a malformed case."""
    nodes, reports = case.get("nodes"), case.get("reports")
    if not isinstance(nodes, dict) or not nodes:
        raise Invalid("nodes must be a non-empty map")
    if not isinstance(reports, (list, tuple)) or len(reports) != 2 or reports[0] == reports[1]:
        raise Invalid("exactly two distinct reports required")
    for r in reports:
        if r not in nodes:
            raise Invalid(f"report {r!r} is not a node")
        if nodes[r] is None:
            raise Invalid(f"report {r!r} is an original observation, not a report")
    for n in nodes:                      # validate the whole graph, so unused bad records fail closed too
        _root(nodes, n)
    find = _classes(nodes, case.get("same_as"))
    a, b = (find(_root(nodes, r)) for r in reports)
    return "CONFIRMED" if a != b else "INSUFFICIENT"


# ---------------------------------------------------------------- shortcut rules (negative controls)
def last_letter(case):
    """note 004: read only the last letter of what the variable report uses."""
    var = case["reports"][-1]
    return "INSUFFICIENT" if str(case["nodes"][var])[-1:] in "AB" else "CONFIRMED"


def repeat_count(case):
    uses = [p for p in case["nodes"].values() if p is not None]
    return "INSUFFICIENT" if any(uses.count(u) >= 3 for u in set(uses)) else "CONFIRMED"


def id_repeat_in_text(case):
    text = case.get("prompt") or " ".join(f"{k} {v}" for k, v in case["nodes"].items())
    ids = [i for i in re.findall(r"\b[A-Za-z0-9]+(?:-\d+)?\b", text) if case["nodes"].get(i, 0) is None]
    return "INSUFFICIENT" if len(ids) != len(set(ids)) else "CONFIRMED"


def report_parent_equal(case):
    a, b = case["reports"]
    return "INSUFFICIENT" if case["nodes"][a] == case["nodes"][b] else "CONFIRMED"


SHORTCUTS = {"last_letter": last_letter, "repeat_count": repeat_count,
             "id_repeat_in_text": id_repeat_in_text, "report_parent_equal": report_parent_equal}
