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


# REV1: deterministic selectors break ties by text before id, so relabelling the opaque ids cannot change which
# records (by content) are kept; the id-relabelling test checks that (Codex review A4).
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
    order = sorted(view, key=lambda r: (r["age"], r["text"], r["id"]))
    return _check(view, budget, [r["id"] for r in order[:budget]])


def sel_uses(view, budget, seed=None):
    order = sorted(view, key=lambda r: (-r["uses"], r["age"], r["text"], r["id"]))
    return _check(view, budget, [r["id"] for r in order[:budget]])


SALIENT = re.compile(r"\b(must|never|always|deadline|required|critical|do not|allerg\w*|safety|limit)\b", re.I)


def content_score(text):
    """A simple salience rule: hard-constraint words, numbers and length. It sees text only."""
    return 2 * len(SALIENT.findall(text)) + 0.5 * len(re.findall(r"\d", text)) + len(text) / 80


def sel_content(view, budget, seed=None):
    order = sorted(view, key=lambda r: (-content_score(r["text"]), r["age"], r["text"], r["id"]))
    return _check(view, budget, [r["id"] for r in order[:budget]])


CORRECTION = re.compile(r"\b(update|correction|changed|moved|now|instead|no longer|replaces|cancel\w*)\b", re.I)


def sel_supersession_aware(view, budget, seed=None):
    """The 'fix' arm: reserve budget for records that read like corrections, then fill by content salience."""
    corr = sorted([r for r in view if CORRECTION.search(r["text"])], key=lambda r: (r["age"], r["text"], r["id"]))
    rest = sorted([r for r in view if not CORRECTION.search(r["text"])],
                  key=lambda r: (-content_score(r["text"]), r["age"], r["text"], r["id"]))
    return _check(view, budget, [r["id"] for r in (corr + rest)[:budget]])


SELECTORS = {"random": sel_random, "recency": sel_recency, "uses": sel_uses, "content": sel_content,
             "supersession_aware": sel_supersession_aware}


def run_selector(name, scenario, budget, seed=0):
    """Selectors get the view only; a selector that tries to read hidden fields raises KeyError there."""
    return SELECTORS[name](selector_view(scenario), budget, seed)


# ---------------------------------------------------------------- decisions
# Output contract (REV1, 2026-11-16, fixed before any model output exists): the reply must contain EXACTLY ONE line
# "ANSWER: <value>". Zero lines, or two or more (even if they agree), is MALFORMED. This replaces the draft's
# last-line-wins convention (Codex review A3).
ANSWER = re.compile(r"^\s*ANSWER\s*:\s*(.+?)\s*$", re.I | re.M)


def parse_answer(text):
    m = ANSWER.findall(text or "")
    return m[0] if len(m) == 1 else None


def norm_value(s):
    """Symmetric normalisation, applied to model output AND key alike (Codex review A1): trim, drop surrounding
    quotes/backticks, lower-case, collapse whitespace, drop trailing periods."""
    s = s.strip().strip("\"'`").strip()
    s = re.sub(r"\s+", " ", s.lower())
    return s.rstrip(".").rstrip()


def classify(task, raw_output):
    """World-state outcome: CORRECT, STALE (gave the superseded value), UNKNOWN (abstained), WRONG or MALFORMED.

    This scores against the full history. It does NOT say whether the answer was supported by the records the
    model actually saw; evidence_outcome() does that (Codex review A5)."""
    a = parse_answer(raw_output)
    if a is None:
        return "MALFORMED"
    a = norm_value(a)
    if a == norm_value(task["answer"]):
        return "CORRECT"
    if a == "unknown":
        return "UNKNOWN"
    if task.get("stale") and a == norm_value(task["stale"]):
        return "STALE"
    return "WRONG"


def _ids(task, key):
    v = task.get(key, [])
    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
        raise ValueError(f"task field {key!r} must be a list of record ids")
    return v


def retained_requirements(task, kept):
    """Retention outcome, separate from the decision. Semantics (Codex review A2): every id in "needs" (AND) is
    kept, and, if "needs_any" is non-empty, at least one of its ids (OR) is kept. A task with neither is
    malformed and raises: an empty requirement must never certify missing evidence."""
    needs, any_ = _ids(task, "needs"), _ids(task, "needs_any")
    if not needs and not any_:
        raise ValueError("task has no evidence requirement")
    kept = set(kept)
    return set(needs) <= kept and (not any_ or bool(kept & set(any_)))


def licensed_answer(task, kept):
    """What the RETAINED records license, by the task's evidence rules: a list of [ids, value] in precedence order.
    The first rule whose ids are all kept gives the value; if none applies, "UNKNOWN". Example: a correction task
    has [[correction], new], [[original], old]; with only the original kept the licensed answer is the old value."""
    rules = task.get("evidence")
    if not rules:
        raise ValueError("task has no evidence rules")
    kept = set(kept)
    for ids, value in rules:
        if set(ids) <= kept:
            return value
    return "UNKNOWN"


def evidence_outcome(task, kept, raw_output):
    """Evidence-relative outcome: FOLLOWS_EVIDENCE, DEPARTS_FROM_EVIDENCE or MALFORMED. With only a superseded
    record kept, giving the old value FOLLOWS the evidence: that is information loss in the store, not a model
    failure."""
    a = parse_answer(raw_output)
    if a is None:
        return "MALFORMED"
    return "FOLLOWS_EVIDENCE" if norm_value(a) == norm_value(licensed_answer(task, kept)) else "DEPARTS_FROM_EVIDENCE"


# ---------------------------------------------------------------- the exact prompt (published before any run)
PROMPT_HEAD = ("You are given notes from a memory store. Answer the question using only these notes. "
               "If the notes do not determine the answer, answer UNKNOWN.")
PROMPT_TAIL = "Reply with exactly one line, either \"ANSWER: <value>\" or \"ANSWER: UNKNOWN\"."


def build_prompt(question, scenario, kept):
    """Kept records' TEXT only, ordered by id. Ids are opaque, so the order carries no kind information; ids,
    age and uses are not shown to the model."""
    by_id = {r["id"]: r for r in scenario["records"]}
    notes = "\n".join(f"- {by_id[i]['text']}" for i in sorted(kept))
    return f"{PROMPT_HEAD}\n\nNotes:\n{notes or '(none)'}\n\nQuestion: {question}\n{PROMPT_TAIL}"


def seal(obj):
    import json
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()
