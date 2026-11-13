"""Tests for verify_identity_hashes.py (SELF-TESTED: written by its author, Claude Opus 5.5, 2026-11-13).

Run: python -m unittest discover -s experiments/qm_obs_001_audit -p 'test_verify_identity_hashes.py' -v
Each planted defect must give exit 1 (mismatch) or 2 (could not check), never 0.
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_identity_hashes as v  # noqa: E402

REAL = v.DEFAULT.read_text(encoding="utf-8")


def run(text=None, args=()):
    out = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(out):
        path = v.DEFAULT if text is None else Path(tmp) / "s.md"
        if text is not None:
            path.write_text(text, encoding="utf-8")
        rc = v.main([str(path), *args])
    return rc, out.getvalue()


class Verify(unittest.TestCase):
    def test_real_file_matches_ten_of_ten(self):
        rc, out = run()
        self.assertEqual(rc, 0)
        self.assertIn("RESULT 10/10 MATCH", out)
        self.assertEqual(out.count(" MATCH "), 10)

    def test_negative_control_holds_on_the_real_file(self):
        rc, out = run(args=("--negative-control",))
        self.assertEqual(rc, 0)
        self.assertIn("MISMATCH: S02", out)
        self.assertIn("NEGATIVE CONTROL HELD", out)

    def test_changed_identity_line_is_named(self):
        rc, out = run(REAL.replace("Kelvin J. McQueen | Consciousness", "Kelvin J. McQueen | Conscious", 1))
        self.assertEqual(rc, 1)
        self.assertIn("MISMATCH: S01", out)

    def test_changed_recorded_digest_is_named(self):
        rc, out = run(REAL.replace("b178268b21e3c603", "b178268b21e3c604", 1))
        self.assertEqual(rc, 1)
        self.assertIn("MISMATCH: S10", out)

    def test_trailing_space_counts(self):
        line = "David J. Chalmers; Kelvin J. McQueen | Consciousness and the Collapse of the Wave Function | 10.1093/oso/9780197501665.003.0002"
        self.assertIn(line + "\n```", REAL, "fixture: S01 line not found")
        rc, _ = run(REAL.replace(line + "\n```", line + " \n```", 1))
        self.assertEqual(rc, 1)

    def test_could_not_check_cases_exit_2(self):
        s10 = REAL.index("## S10")
        cases = {
            "missing file": None,
            "empty file": "",
            "no entries": "nothing here\n",
            "entry without digest": REAL.replace("**Identity SHA-256:** `b0e30095", "**Identity SHA:** `b0e30095", 1),
            "duplicate id": REAL.replace("## S03", "## S02", 1),
            "nine entries": REAL[:s10] + "\n",
        }
        for name, text in cases.items():
            with self.subTest(case=name):
                if text is None:
                    out = io.StringIO()
                    with contextlib.redirect_stdout(out):
                        rc = v.main(["/nonexistent/path/sources.md"])
                else:
                    rc, out = run(text)
                    out = io.StringIO(out)
                self.assertEqual(rc, 2)
                self.assertIn("COULD NOT CHECK", out.getvalue())

    def test_wrong_expected_count_is_not_a_match(self):
        rc, out = run(args=("--expect", "11"))
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
