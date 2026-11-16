"""MEM-DECAY-003 instrument: scenario schema, the task-blind selector view, equal-budget selectors, and the decision
scorer. No model is called here. PROTOCOL_DRAFT.md has the design.

A scenario: {"scenario_id", "family", "records": [{"id", "text", "age", "uses", "kind"}], "tasks": [...]}.
A record's "kind" (original, correction, critical, conjunct, redundant, filler) and every task field are HIDDEN from
selectors: they see only id, text, age and uses. selector_view() builds that view, and tests check that
selectors cannot see the hidden fields.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-16. SELF-TESTED.
"""
import hashlib
import random
import re

VISIBLE = ("id", "text", "age", "uses")


class Leak(RuntimeError):
    pass


def selector_view(scenario):
    """The only thing a selector may see: per-record id, text, age and uses. No kind, no tasks, no labels."""
    return tuple({k: r[k] for k in VISIBLE} for r in scenario["records"])


def _check(view, budget, chosen):
    ids = [r["id"] for r in view]
    if len(set(chosen)) != len(chosen) or not set(chosen) <= set(ids):
        raise ValueError("selector returned unknown or duplicate ids")
    if len(chosen) > budget:
        raise ValueError(f"selector exceeded budget {budget}: {len(chosen)}")
    return list(chosen)


# ---------------------------------------------------------------- equal-budget selectors (task-blind)
def sel_random(view, budget, seed):
    rng = random.Random(seed)
    return _check(view, budget, rng.sample([r["id"] for r in view], min(budget, len(view))))


def sel_recency(view, budget, seed=None):
    order = sorted(view, key=lambda r: (r["age"], r["id"]))
    return _check(view, budget, [r["id"] for r in order[:budget]])


def sel_uses(view, budget, seed=None):
    order = sorted(view, key=lambda r: (-r["uses"], r["age"], r["id"]))
    return _check(view, budget, [r["id"] for r in order[:budget]])


SALIENT = re.compile(r"\b(must|never|always|deadline|required|critical|do not|allerg\w*|safety|limit)\b", re.I)


def content_score(text):
    """A simple salience rule: hard-constraint words, numbers and length. It sees text only."""
    return 2 * len(SALIENT.findall(text)) + 0.5 * len(re.findall(r"\d", text)) + len(text) / 80


def sel_content(view, budget, seed=None):
    order = sorted(view, key=lambda r: (-content_score(r["text"]), r["age"], r["id"]))
    return _check(view, budget, [r["id"] for r in order[:budget]])


CORRECTION = re.compile(r"\b(update|correction|changed|moved|now|instead|no longer|replaces|cancel\w*)\b", re.I)


def sel_supersession_aware(view, budget, seed=None):
    """The 'fix' arm: reserve budget for records that read like corrections, then fill by content salience."""
    corr = sorted([r for r in view if CORRECTION.search(r["text"])], key=lambda r: (r["age"], r["id"]))
    rest = sorted([r for r in view if not CORRECTION.search(r["text"])],
                  key=lambda r: (-content_score(r["text"]), r["age"], r["id"]))
    return _check(view, budget, [r["id"] for r in (corr + rest)[:budget]])


SELECTORS = {"random": sel_random, "recency": sel_recency, "uses": sel_uses, "content": sel_content,
             "supersession_aware": sel_supersession_aware}


def run_selector(name, scenario, budget, seed=0):
    """Selectors get the view only; a selector that tries to read hidden fields raises KeyError there."""
    return SELECTORS[name](selector_view(scenario), budget, seed)


# ---------------------------------------------------------------- decisions
ANSWER = re.compile(r"^\s*ANSWER\s*:\s*(.+?)\s*$", re.I | re.M)


def parse_answer(text):
    m = ANSWER.findall(text or "")
    return m[-1].strip().rstrip(".") if m else None


def classify(task, raw_output):
    """CORRECT, STALE (gave the superseded value), UNKNOWN (abstained), WRONG (another value) or MALFORMED.

    task: {"answer": str, "stale": str or None}; matching is case-insensitive on the whole value."""
    a = parse_answer(raw_output)
    if a is None:
        return "MALFORMED"
    norm = lambda s: re.sub(r"\s+", " ", s.strip().lower())
    if norm(a) == norm(task["answer"]):
        return "CORRECT"
    if norm(a) == "unknown":
        return "UNKNOWN"
    if task.get("stale") and norm(a) == norm(task["stale"]):
        return "STALE"
    return "WRONG"


def retained_requirements(task, kept):
    """Retrieval-side outcome, separate from the decision: are all records the task needs kept?"""
    return set(task["needs"]) <= set(kept)


def seal(obj):
    import json
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()
