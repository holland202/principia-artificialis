"""PA-LINEAGE-001: authored self-tests; NOT independent scientific validation."""
import json
import tempfile
import unittest
from pathlib import Path

from .core import JournalError, _check_events, append, graph, init, read_events


def who():
    return {"contributor": "Test author (fictional)", "contributor_kind": "human",
            "model": "", "review_level": "none"}


def hypothesis(parent=None, reason=""):
    return {**who(), "title": "An idea", "claim": "An observable prediction",
            "parent_id": parent, "reason": reason}


def result(hid, **changes):
    data = {**who(), "hypothesis_id": hid, "prediction": "P1: A will exceed B",
            "observation": "Toy result B was larger", "outcome": "REFUTED",
            "evidence_ref": "synthetic:fixture-output", "scope": "fictional toy data",
            "lesson": "A can fail", "next_question": "When might A hold?"}
    data.update(changes)
    return data


class LineageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "journal.jsonl"
        init(self.path)

    def new_hypothesis(self):
        return append(self.path, "hypothesis", hypothesis())

    def test_lineage_and_failure_retained(self):
        a = self.new_hypothesis()
        b = append(self.path, "result", result(a["id"]))
        c = append(self.path, "hypothesis", hypothesis(a["id"], "Counterexample"))
        events = read_events(self.path, require_nonempty=True)
        self.assertEqual([e["id"] for e in events], [a["id"], b["id"], c["id"]])
        self.assertEqual(events[1]["data"]["outcome"], "REFUTED")
        g = graph(events)
        self.assertEqual([e["relation"] for e in g["edges"]], ["tests", "revises"])
        self.assertEqual(g["nodes"][0]["scientific_status"], "UNASSESSED")

    def test_bad_result_cannot_append(self):
        a = self.new_hypothesis()
        before = self.path.read_bytes()
        for field in ["evidence_ref", "scope", "prediction", "observation"]:
            with self.subTest(field=field):
                d = result(a["id"], **{field: ""})
                with self.assertRaises(JournalError):
                    append(self.path, "result", d)
                self.assertEqual(self.path.read_bytes(), before)

    def test_unknown_parent_and_result_subject(self):
        before = self.path.read_bytes()
        with self.assertRaises(JournalError):
            append(self.path, "hypothesis", hypothesis("not-a-real-parent", ""))
        with self.assertRaises(JournalError):
            append(self.path, "result", result("not-a-real-parent"))
        self.assertEqual(self.path.read_bytes(), before)

    def test_tamper_detected(self):
        self.new_hypothesis()
        original = self.path.read_text()
        self.path.write_text(original.replace("An idea", "A broken idea"))
        with self.assertRaises(JournalError):
            read_events(self.path)

    def test_authored_status_cannot_promote(self):
        with self.assertRaises(JournalError):
            append(self.path, "hypothesis", {**hypothesis(), "scientific_status": "SUPPORTED"})
        a = self.new_hypothesis()
        self.assertEqual(graph(read_events(self.path))["nodes"][0]["scientific_status"], "UNASSESSED")
        append(self.path, "result", result(a["id"], outcome="HELD"))
        self.assertEqual(graph(read_events(self.path))["nodes"][0]["scientific_status"], "UNASSESSED")

    def test_noncannonical_json_duplicate_key_rejected(self):
        a = self.new_hypothesis()
        raw = self.path.read_text()
        raw = raw.replace('"schema":"pa.lineage/1"', '"schema":"pa.lineage/1","schema":"pa.lineage/1"')
        self.assertNotEqual(raw, self.path.read_text())
        self.path.write_text(raw)
        with self.assertRaises(JournalError):
            read_events(self.path)

    def test_duplicate_id_rejected(self):
        a = self.new_hypothesis()
        events = read_events(self.path)
        events.append(dict(events[0], seq=2))
        with self.assertRaises(JournalError):
            _check_events(events)

    def test_missing_file_fails_closed(self):
        self.assertRaises(JournalError, read_events, self.path.with_name("unknown.jsonl"))

    def test_empty_verify_fails_closed(self):
        with self.assertRaises(JournalError):
            read_events(self.path, require_nonempty=True)

    def test_ai_attribution_required(self):
        with self.assertRaises(JournalError):
            append(self.path, "hypothesis", {**hypothesis(), "contributor_kind": "ai", "model": ""})
        a = append(self.path, "hypothesis", {**hypothesis(), "contributor_kind": "ai", "model": "TestModel", "review_level": "none"})
        self.assertEqual(a["data"]["model"], "TestModel")
        node = graph(read_events(self.path))["nodes"][0]
        self.assertEqual((node["model"], node["review_level"]), ("TestModel", "none"))

    def test_unknown_outcome_rejected(self):
        a = self.new_hypothesis()
        with self.assertRaises(JournalError):
            append(self.path, "result", result(a["id"], outcome="SCIENTIFICALLY_PROVEN"))

    def test_source_does_not_upgrade_evidence(self):
        a = self.new_hypothesis()
        append(self.path, "source", {**who(), "hypothesis_id": a["id"], "reference": "https://example.org/example",
                                     "description": "Submitted but unauthenticated"})
        out = graph(read_events(self.path))
        self.assertEqual(out["nodes"][0]["scientific_status"], "UNASSESSED")
        self.assertEqual(out["edges"][0]["relation"], "references")

    def test_missing_final_newline_rejected(self):
        self.new_hypothesis()
        self.path.write_bytes(self.path.read_bytes().rstrip(b"\n"))
        with self.assertRaises(JournalError):
            read_events(self.path)

    def test_no_overwrite(self):
        self.new_hypothesis()
        with self.assertRaises(JournalError):
            init(self.path)


if __name__ == "__main__":
    unittest.main()
