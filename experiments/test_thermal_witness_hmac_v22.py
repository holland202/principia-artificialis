"""HMAC witness adversarial regression suite; no key or hardware required."""
import importlib.util
import sys
import unittest
from pathlib import Path

root = Path(__file__).parent
for name in ("thermal_evidence_v2", "thermal_checkpoint_v21", "thermal_witness_hmac_v22"):
    spec = importlib.util.spec_from_file_location(name, root / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

from thermal_evidence_v2 import Policy, make_record
from thermal_witness_hmac_v22 import attest, verify_attestation

class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.secret = bytes(range(32))
        self.other = bytes(range(32, 64))
        p = Policy()
        a = make_record({"temp_c": 29, "observed_at_s": 100,
                         "source": "synthetic", "authenticity": "not_established"}, p, 101)
        b = make_record(None, p, 102, a["record_sha256"], 1)
        self.records = [a, b]
        self.att = attest(self.records, self.secret, "lab-witness")

    def test_positive(self):
        self.assertEqual(verify_attestation(self.records, self.att, self.secret, "lab-witness"),
                         (True, "WITNESS_TAG_AND_CHECKPOINT_MATCH"))

    def test_wrong_key(self):
        self.assertEqual(verify_attestation(self.records, self.att, self.other, "lab-witness")[1],
                         "WITNESS_TAG_MISMATCH")

    def test_wrong_identity(self):
        self.assertEqual(verify_attestation(self.records, self.att, self.secret, "other")[1],
                         "WITNESS_MISMATCH")

    def test_tampered_tag(self):
        a = dict(self.att)
        a["tag_sha256"] = "0" * 64
        self.assertEqual(verify_attestation(self.records, a, self.secret, "lab-witness")[1],
                         "WITNESS_TAG_MISMATCH")

    def test_truncation(self):
        self.assertEqual(verify_attestation(self.records[:1], self.att, self.secret, "lab-witness")[1],
                         "RECORD_COUNT_MISMATCH")

    def test_resealed_evidence(self):
        p = Policy()
        a = make_record(None, p, 101)
        b = make_record(None, p, 102, a["record_sha256"], 1)
        self.assertEqual(verify_attestation([a,b], self.att, self.secret, "lab-witness")[1],
                         "HEAD_MISMATCH")

    def test_modified_checkpoint(self):
        a = dict(self.att)
        a["checkpoint"] = dict(a["checkpoint"])
        a["checkpoint"]["record_count"] = 1
        self.assertEqual(verify_attestation(self.records, a, self.secret, "lab-witness")[1],
                         "WITNESS_TAG_MISMATCH")

    def test_short_key(self):
        with self.assertRaises(ValueError):
            attest(self.records, b"short", "lab-witness")

    def test_empty_evidence(self):
        with self.assertRaises(ValueError):
            attest([], self.secret, "lab-witness")

if __name__ == "__main__":
    unittest.main()
