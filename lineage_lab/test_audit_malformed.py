"""PA-LINEAGE-001 audit (2026-10-22): malformed field types must be refused as JournalError.

Self-tested by Claude (Anthropic, Opus 5.5); not independent validation.
Each case must raise JournalError on both the append path and the read path (crafted
journal with a valid hash chain), never TypeError or another unstructured exception.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from .core import GENESIS, JournalError, _canonical, _digest, append, init, read_events

BAD = ([], {}, 7, True, None)
HUMAN = {"contributor": "Test author (fictional)", "contributor_kind": "human"}
AI = {"contributor": "Test model (fictional)", "contributor_kind": "ai", "model": "fictional-model"}


def write_chain(path, events):
    """Write events with a freshly computed, valid hash chain (an attacker or bad tool could)."""
    prev, lines = GENESIS, []
    for n, e in enumerate(events, 1):
        e = {k: v for k, v in e.items() if k != "hash"}
        e.update(seq=n, prev_hash=prev)
        e["hash"] = _digest(e)
        prev = e["hash"]
        lines.append(_canonical(e) + "\n")
    path.write_text("".join(lines), encoding="utf-8")


def envelope(n, kind, data):
    return {"schema": "pa.lineage/1", "seq": n, "id": "audit-%d" % n,
            "created_utc": "2026-10-22T00:00:00+00:00", "kind": kind, "data": data}


class MalformedTypes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "journal.jsonl"
        init(self.path)
        self.h = append(self.path, "hypothesis", {**HUMAN, "title": "An idea", "claim": "A claim"})

    def cases(self):
        hid = self.h["id"]
        for bad in BAD:
            yield "kind", bad, {**HUMAN, "title": "t", "claim": "c"}
            yield "hypothesis_id", bad, ("result", {**HUMAN, "hypothesis_id": bad, "prediction": "p", "outcome": "NOT RUN"})
            yield "outcome", bad, ("result", {**HUMAN, "hypothesis_id": hid, "prediction": "p", "outcome": bad})
            yield "ai_review_level", bad, ("source", {**AI, "review_level": bad, "hypothesis_id": hid, "reference": "r"})
            if bad is not None:  # an absent/None human review_level is allowed
                yield "human_review_level", bad, ("hypothesis", {**HUMAN, "review_level": bad, "title": "t", "claim": "c"})

    def test_append_path_refuses_with_journal_error(self):
        before = self.path.read_bytes()
        for field, bad, spec in self.cases():
            kind, data = (bad, spec) if field == "kind" else spec
            with self.subTest(field=field, value=repr(bad)):
                with self.assertRaises(JournalError):
                    append(self.path, kind, data)
        self.assertEqual(self.path.read_bytes(), before)

    def test_read_path_refuses_with_journal_error(self):
        first = read_events(self.path)[0]
        for field, bad, spec in self.cases():
            kind, data = (bad, spec) if field == "kind" else spec
            with self.subTest(field=field, value=repr(bad)):
                write_chain(self.path, [first, envelope(2, kind, data)])
                with self.assertRaises(JournalError):
                    read_events(self.path)

    def test_cli_verify_on_crafted_journal_exits_2_without_traceback(self):
        first = read_events(self.path)[0]
        write_chain(self.path, [first, envelope(2, "result", {
            **HUMAN, "hypothesis_id": [], "prediction": "p", "outcome": "NOT RUN"})])
        r = subprocess.run([sys.executable, "-m", "lineage_lab", "verify", "--journal", str(self.path)],
                           capture_output=True, text=True, cwd=Path(__file__).resolve().parent.parent)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("GATE: FAIL", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
