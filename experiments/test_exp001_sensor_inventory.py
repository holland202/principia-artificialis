"""Synthetic tests for Exp001 sensor inventory. No physical readings claimed."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory", Path(__file__).with_name("exp001_sensor_inventory.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class InventoryTests(unittest.TestCase):
    def test_no_sensor(self):
        with tempfile.TemporaryDirectory() as d:
            r = m.inspect(Path(d))
            self.assertEqual(r["zones"], [])
            self.assertFalse(r["sensor_identity_verified"])

    def test_candidate_unit_not_verified(self):
        with tempfile.TemporaryDirectory() as d:
            z = Path(d) / "thermal_zone0"
            z.mkdir()
            (z / "type").write_text("test-cpu")
            (z / "temp").write_text("42000")
            row = m.inspect(Path(d))["zones"][0]
            self.assertEqual(row["temp_c"], 42.0)
            self.assertEqual(row["status"], "candidate_millicelsius")
            self.assertEqual(row["scale"], "assumed_millicelsius_unverified")

    def test_unreadable_sensor(self):
        with tempfile.TemporaryDirectory() as d:
            z = Path(d) / "thermal_zone1"
            z.mkdir()
            (z / "type").write_text("unknown")
            row = m.inspect(Path(d))["zones"][0]
            self.assertEqual(row["status"], "unavailable")
            self.assertIsNone(row["temp_c"])

    def test_nonfinite(self):
        with tempfile.TemporaryDirectory() as d:
            z = Path(d) / "thermal_zone2"
            z.mkdir()
            (z / "type").write_text("unknown")
            (z / "temp").write_text("nan")
            row = m.inspect(Path(d))["zones"][0]
            self.assertEqual(row["status"], "nonfinite")
            self.assertIsNone(row["temp_c"])

    def test_observed_sentinel(self):\n        with tempfile.TemporaryDirectory() as d:\n            z = Path(d) / "thermal_zone61"\n            z.mkdir()\n            (z / "type").write_text("sdr0_pa")\n            (z / "temp").write_text("-273000")\n            row = m.inspect(Path(d))["zones"][0]\n            self.assertEqual(row["status"], "suspected_invalid_sentinel")\n            self.assertIsNone(row["temp_c"])\n\n    def test_out_of_range(self):
        with tempfile.TemporaryDirectory() as d:
            z = Path(d) / "thermal_zone3"
            z.mkdir()
            (z / "type").write_text("unknown")
            (z / "temp").write_text("1000000")
            self.assertEqual(m.inspect(Path(d))["zones"][0]["status"], "outside_candidate_range")

if __name__ == "__main__":
    unittest.main()
