"""Negative and positive controls for thermal_evidence_v2; stdlib unittest."""
import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("thermal_evidence_v2", Path(__file__).with_name("thermal_evidence_v2.py"))
m = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = m
spec.loader.exec_module(m)

class ThermalEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.p = m.Policy()
        self.obs = {"temp_c": 30.0, "observed_at_s": 100.0,
                    "source": "synthetic_test", "authenticity": "not_established"}

    def test_positive_control(self):
        self.assertEqual(m.evaluate(self.obs, self.p, 101)["decision"], "ALLOW")

    def test_missing_deferred(self):
        self.assertEqual(m.evaluate(None, self.p, 101)["reason"], "NO_OBSERVATION")

    def test_stale_and_future_deferred(self):
        self.assertEqual(m.evaluate(self.obs, self.p, 111)["reason"], "STALE_OBSERVATION")
        self.assertEqual(m.evaluate(self.obs, self.p, 99)["reason"], "FUTURE_TIMESTAMP")

    def test_ceiling_refused(self):
        self.obs["temp_c"] = 38.5
        self.assertEqual(m.evaluate(self.obs, self.p, 101)["reason"], "THERMAL_CEILING")

    def test_nonfinite_and_out_of_range_refused(self):
        for v in (float("nan"), float("inf"), -100.0, 999.0):
            with self.subTest(v=v):
                self.obs["temp_c"] = v
                self.assertEqual(m.evaluate(self.obs, self.p, 101)["decision"], "REFUSE")

    def test_missing_provenance_deferred(self):
        self.obs.pop("source")
        self.assertEqual(m.evaluate(self.obs, self.p, 101)["reason"], "PROVENANCE_UNDECLARED")

    def test_bad_evaluation_clock(self):
        for now in (float("nan"), True, "101"):
            with self.subTest(now=now):
                with self.assertRaises(ValueError):
                    m.evaluate(self.obs, self.p, now)

    def test_missing_type_refused(self):
        for v in ("30", True, None):
            with self.subTest(v=v):
                self.obs["temp_c"] = v
                self.assertEqual(m.evaluate(self.obs, self.p, 101)["decision"], "REFUSE")

    def test_detects_payload_mutation(self):
        record = m.make_record(self.obs, self.p, 101)
        self.assertTrue(m.verify_records([record])[0])
        record["observation"]["temp_c"] = 39
        self.assertEqual(m.verify_records([record])[2], "DIGEST")

    def test_detects_resealed_false_decision(self):
        record = m.make_record(self.obs, self.p, 101)
        record["result"] = {"decision": "ALLOW", "reason": "FAKE"}
        record["record_sha256"] = m.digest({k:v for k,v in record.items() if k != "record_sha256"})
        self.assertEqual(m.verify_records([record])[2], "DECISION")

    def test_rejects_resealed_extra_fields(self):
        record = m.make_record(self.obs, self.p, 101)
        record["unexpected"] = "injected"
        record["record_sha256"] = m.digest({k:v for k,v in record.items() if k != "record_sha256"})
        self.assertEqual(m.verify_records([record])[2], "RECORD_FIELDS")

    def test_rejects_boolean_sequence(self):
        record = m.make_record(self.obs, self.p, 101)
        record["sequence"] = False
        record["record_sha256"] = m.digest({k:v for k,v in record.items() if k != "record_sha256"})
        self.assertEqual(m.verify_records([record])[2], "CHAIN")

    def test_chain_reorder_and_truncation_limit(self):
        a = m.make_record(self.obs, self.p, 101)
        b = m.make_record(self.obs, self.p, 102, a["record_sha256"], 1)
        self.assertTrue(m.verify_records([a,b])[0])
        self.assertFalse(m.verify_records([b,a])[0])
        # An unanchored prefix still verifies: limitation deliberately preserved.
        self.assertTrue(m.verify_records([a])[0])

    def test_policy_rejects_invalid(self):
        with self.assertRaises(ValueError):
            m.Policy(ceiling_c=float("nan"))
        with self.assertRaises(ValueError):
            m.Policy(min_c=50, max_c=30)

if __name__ == "__main__":
    unittest.main()
