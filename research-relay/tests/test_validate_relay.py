"""SRR-1 checker tests; stdlib only and no network or GitHub mutations."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_relay", HERE / "scripts" / "validate_relay.py")
relay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(relay)

VALID = {
    "task_id": "SRR-001",
    "title": "Dormant task",
    "repository": "holland202/principia-artificialis",
    "source_commit": None,
    "authorization": "READ_ONLY",
    "assigned_to": None,
    "stage": "AWAITING_CHAD_DECISION",
    "execution_status": "NOT_STARTED",
    "claim_status": "UNVERIFIED",
    "preregistration": None,
    "evidence_manifest": None,
    "independent_review": "NOT_STARTED",
    "review_ref": None,
    "chad_approval_required": True,
    "chad_decision_ref": None,
}


class ValidatorTests(unittest.TestCase):
    def write_task(self, root, data):
        tasks = root / "TASKS"
        tasks.mkdir()
        target = tasks / "SRR-001.md"
        target.write_text("# test\n\n~~~json\n" + json.dumps(data) + "\n~~~\n", encoding="utf-8")
        return target

    def test_dormant_task_valid(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            self.write_task(root, dict(VALID))
            self.assertEqual([], relay.validate(root))

    def test_unsupported_permission_fails_closed(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            data = dict(VALID, authorization="TEST_APPROVED", chad_decision_ref="DECISIONS/SRR-001.md")
            self.write_task(root, data)
            errors = relay.validate(root)
            self.assertTrue(any("non-READ_ONLY" in e for e in errors))

    def test_self_reported_success_not_promoted(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            data = dict(VALID, execution_status="COMPLETE", claim_status="SUPPORTED_WITHIN_SCOPE")
            self.write_task(root, data)
            self.assertTrue(any("claim promoted" in e for e in relay.validate(root)))

    def test_duplicate_json_key_refused(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            target = self.write_task(root, dict(VALID))
            text = target.read_text(encoding="utf-8")
            target.write_text(text.replace('"task_id": "SRR-001"', '"task_id": "SRR-001", "task_id": "SRR-001"'), encoding="utf-8")
            self.assertTrue(any("duplicate JSON" in e for e in relay.validate(root)))

    def test_missing_record_is_not_success(self):
        with tempfile.TemporaryDirectory() as dirname:
            self.assertTrue(relay.validate(Path(dirname)))

    def test_bad_commit_sha_rejected(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            self.write_task(root, dict(VALID, source_commit="main"))
            self.assertTrue(any("source_commit" in e for e in relay.validate(root)))


if __name__ == "__main__":
    unittest.main()
