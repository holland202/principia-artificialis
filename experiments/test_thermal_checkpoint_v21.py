"""Adversarial controls for independently retained thermal checkpoints."""
import importlib.util
import sys
import unittest
from pathlib import Path

root = Path(__file__).parent
for name, file in (("thermal_evidence_v2", "thermal_evidence_v2.py"),
                   ("thermal_checkpoint_v21", "thermal_checkpoint_v21.py")):
    spec = importlib.util.spec_from_file_location(name, root / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

from thermal_evidence_v2 import Policy, make_record
from thermal_checkpoint_v21 import checkpoint, verify_against_checkpoint

class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.policy = Policy()
        a = make_record({"temp_c": 30, "observed_at_s": 100,
                         "source": "synthetic", "authenticity": "not_established"}, self.policy, 101)
        b = make_record({"temp_c": 31, "observed_at_s": 102,
                         "source": "synthetic", "authenticity": "not_established"}, self.policy, 103,
                        a["record_sha256"], 1)
        self.records = [a, b]
        self.cp = checkpoint(self.records)

    def test_positive(self):
        self.assertEqual(verify_against_checkpoint(self.records, self.cp),
                         (True, "CHECKPOINT_MATCH_UNAUTHENTICATED"))

    def test_truncation_detected(self):
        self.assertEqual(verify_against_checkpoint(self.records[:1], self.cp)[1],
                         "RECORD_COUNT_MISMATCH")

    def test_extension_detected(self):
        third = make_record(None, self.policy, 104, self.records[-1]["record_sha256"], 2)
        self.assertEqual(verify_against_checkpoint(self.records + [third], self.cp)[1],
                         "RECORD_COUNT_MISMATCH")

    def test_rewrite_detected_even_when_resealed(self):
        a = make_record({"temp_c": 20, "observed_at_s": 100,
                         "source": "synthetic", "authenticity": "not_established"}, self.policy, 101)
        b = make_record(None, self.policy, 103, a["record_sha256"], 1)
        self.assertEqual(verify_against_checkpoint([a, b], self.cp)[1], "HEAD_MISMATCH")

    def test_checkpoint_mutation_detected(self):
        cp = dict(self.cp)
        cp["record_count"] = 1
        self.assertEqual(verify_against_checkpoint(self.records, cp)[1], "CHECKPOINT_DIGEST")

    def test_empty_refused(self):
        with self.assertRaises(ValueError):
            checkpoint([])

    def test_boolean_count_refused(self):
        cp = dict(self.cp)
        cp["record_count"] = True
        self.assertEqual(verify_against_checkpoint(self.records, cp)[1], "CHECKPOINT_COUNT")

    def test_missing_checkpoint_field_refused(self):
        cp = dict(self.cp)
        del cp["last_record_sha256"]
        self.assertEqual(verify_against_checkpoint(self.records, cp)[1], "CHECKPOINT_SCHEMA")

if __name__ == "__main__":
    unittest.main()
