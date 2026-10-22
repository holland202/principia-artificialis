"""PA-LINEAGE-001: local, single-writer scientific lineage journal.

Claims and prediction outcomes here are *reported* by contributors, not verified
scientific facts. A SHA-256 chain detects ordinary edits, not a fully rewritten
history or a dishonest contributor. No external data is fetched or executed.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "pa.lineage/1"
GENESIS = "0" * 64
OUTCOMES = frozenset((
    "HELD", "REFUTED", "INSUFFICIENT_EVIDENCE", "VACUOUS", "NOT RUN",
    "COULD NOT RUN AS REGISTERED", "IMPLEMENTATION_ERROR", "UNRESOLVED",
))
KINDS = frozenset(("hypothesis", "result", "source"))
REVIEW = frozenset(("none", "direction only", "outcome review", "line-by-line"))
MAX_TEXT = 10000
MAX_FILE_BYTES = 8 * 1024 * 1024


class JournalError(ValueError):
    """Invalid journal, event, or unsupported operation."""


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _pairs(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise JournalError("duplicate JSON key: " + key)
        data[key] = value
    return data


def _text(d, name, required=True):
    s = d.get(name, "")
    if not isinstance(s, str) or len(s) > MAX_TEXT or (required and not s.strip()):
        raise JournalError("missing/invalid " + name)
    return s


def _who(data):
    _text(data, "contributor")
    if data.get("contributor_kind") not in ("human", "ai"):
        raise JournalError("contributor_kind must be human or ai")
    level = data.get("review_level")
    if data["contributor_kind"] == "ai":
        _text(data, "model")
        if not isinstance(level, str) or level not in REVIEW:  # audit L1: type before membership
            raise JournalError("AI contribution must declare review_level")
    elif data.get("model", ""):
        raise JournalError("human contributions cannot declare an AI model as themselves")
    elif level is not None and (not isinstance(level, str) or level not in REVIEW):  # audit L3
        raise JournalError("invalid review_level")


def _data(kind, d, prior):
    if not isinstance(kind, str) or kind not in KINDS or not isinstance(d, dict):  # audit L1
        raise JournalError("invalid kind/data")
    allowed = {
        "hypothesis": {"title", "claim", "parent_id", "reason", "contributor", "contributor_kind", "model", "review_level"},
        "result": {"hypothesis_id", "prediction", "observation", "outcome", "evidence_ref", "scope", "lesson", "next_question", "contributor", "contributor_kind", "model", "review_level"},
        "source": {"hypothesis_id", "reference", "description", "contributor", "contributor_kind", "model", "review_level"},
    }[kind]
    if set(d) - allowed:
        raise JournalError("unexpected data fields")
    _who(d)
    hypotheses = {e["id"] for e in prior if e["kind"] == "hypothesis"}
    if kind == "hypothesis":
        _text(d, "title")
        _text(d, "claim")
        parent = d.get("parent_id")
        if parent is not None:
            if not isinstance(parent, str) or parent not in hypotheses:
                raise JournalError("unknown parent hypothesis")
            _text(d, "reason")
    else:
        if not isinstance(d.get("hypothesis_id"), str) or d["hypothesis_id"] not in hypotheses:  # audit L1
            raise JournalError("unknown hypothesis")
        if kind == "source":
            _text(d, "reference")
            _text(d, "description", required=False)
        else:
            _text(d, "prediction")
            _text(d, "observation", required=False)
            _text(d, "lesson", required=False)
            _text(d, "next_question", required=False)
            if not isinstance(d.get("outcome"), str) or d["outcome"] not in OUTCOMES:  # audit L1
                raise JournalError("unknown prediction outcome")
            if d["outcome"] in ("HELD", "REFUTED"):
                _text(d, "scope")
                _text(d, "evidence_ref")
                _text(d, "observation")


def _check_events(events, require_nonempty=False):
    if not isinstance(events, list) or (require_nonempty and not events):
        raise JournalError("journal absent or empty")
    prev = GENESIS
    ids = set()
    for number, event in enumerate(events, 1):
        if not isinstance(event, dict) or set(event) != {
            "schema", "seq", "id", "created_utc", "kind", "data", "prev_hash", "hash"
        }:
            raise JournalError("bad event envelope")
        if event["schema"] != SCHEMA or type(event["seq"]) is not int or event["seq"] != number:
            raise JournalError("bad schema or sequence")
        if not isinstance(event["id"], str) or not event["id"].strip() or event["id"] in ids:
            raise JournalError("missing or duplicate event ID")
        ids.add(event["id"])
        try:
            dt = datetime.fromisoformat(event["created_utc"])
            if dt.tzinfo is None or dt.utcoffset().total_seconds() != 0:
                raise ValueError()
        except (TypeError, AttributeError, ValueError):
            raise JournalError("timestamp is not UTC")
        if event["prev_hash"] != prev:
            raise JournalError("broken journal hash chain")
        core = {k: v for k, v in event.items() if k != "hash"}
        try:
            expected = _digest(core)
        except (TypeError, ValueError) as exc:
            raise JournalError("noncanonical event") from exc
        if event["hash"] != expected:
            raise JournalError("event digest mismatch")
        _data(event["kind"], event["data"], events[:number-1])
        prev = expected
    return prev


def _read_unlocked(path):
    if not path.exists():
        raise JournalError("journal does not exist; run init first")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise JournalError("journal exceeds local prototype size limit")
    result = []
    with path.open("r", encoding="utf-8") as fp:
        for lineno, line in enumerate(fp, 1):
            if not line.endswith("\n"):
                raise JournalError("incomplete final journal line")
            try:
                obj = json.loads(line, object_pairs_hook=_pairs,
                                 parse_constant=lambda v: (_ for _ in ()).throw(JournalError("nonfinite JSON")))
            except (json.JSONDecodeError, UnicodeError) as exc:
                raise JournalError("invalid JSON line " + str(lineno)) from exc
            result.append(obj)
    _check_events(result)
    return result


@contextmanager
def _lock(path, exclusive):
    # POSIX local prototype only; this does not protect an adversarial filesystem.
    lockfile = path.with_suffix(path.suffix + ".lock")
    fd = os.open(lockfile, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        with os.fdopen(fd, "rb") as fp:
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
            yield
            fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
    except BaseException:
        raise


def init(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
    except FileExistsError as exc:
        raise JournalError("refusing to overwrite an existing journal") from exc


def read_events(path, require_nonempty=False):
    path = Path(path)
    with _lock(path, exclusive=False):
        events = _read_unlocked(path)
        _check_events(events, require_nonempty=require_nonempty)
        return events


def append(path, kind, data):
    """Append exactly one event, validating full existing chain under local lock."""
    path = Path(path)
    if not isinstance(data, dict):
        raise JournalError("data must be an object")
    with _lock(path, exclusive=True):
        prior = _read_unlocked(path)
        _data(kind, data, prior)
        event = {
            "schema": SCHEMA, "seq": len(prior) + 1,
            "id": uuid.uuid4().hex,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "kind": kind, "data": data,
            "prev_hash": prior[-1]["hash"] if prior else GENESIS,
        }
        event["hash"] = _digest(event)
        _check_events(prior + [event])
        encoded = (_canonical(event) + "\n").encode("utf-8")
        fd = os.open(path, os.O_WRONLY | os.O_APPEND)
        try:
            written = os.write(fd, encoded)
            if written != len(encoded):
                raise JournalError("partial journal write")
            os.fsync(fd)
        finally:
            os.close(fd)
    return event


def graph(events):
    """Read-only derivative; prediction outcomes never promote a scientific claim."""
    _check_events(events, require_nonempty=True)
    nodes, edges = [], []
    for e in events:
        d = e["data"]
        common = {"id": e["id"], "kind": e["kind"], "contributor": d["contributor"],
                  "contributor_kind": d["contributor_kind"], "model": d.get("model", ""),
                  "review_level": d.get("review_level", "none"), "created_utc": e["created_utc"]}
        if e["kind"] == "hypothesis":
            nodes.append({**common, "title": d["title"], "claim": d["claim"],
                          "scientific_status": "UNASSESSED", "reason": d.get("reason", "")})
            if d.get("parent_id"):
                edges.append({"from": e["id"], "to": d["parent_id"], "relation": "revises"})
        elif e["kind"] == "result":
            nodes.append({**common, "title": d["prediction"], "observation": d.get("observation", ""),
                          "outcome": d["outcome"], "evidence_ref": d.get("evidence_ref", ""),
                          "scope": d.get("scope", ""), "lesson": d.get("lesson", ""),
                          "next_question": d.get("next_question", "")})
            edges.append({"from": e["id"], "to": d["hypothesis_id"], "relation": "tests"})
        else:
            nodes.append({**common, "title": d["reference"], "description": d.get("description", "")})
            edges.append({"from": e["id"], "to": d["hypothesis_id"], "relation": "references"})
    return {"schema": "pa.lineage.graph/1", "source": "local journal (contributor-reported, unauthenticated)",
            "journal_head": events[-1]["hash"], "nodes": nodes, "edges": edges}
