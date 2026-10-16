"""Unit tests for scripts/check_numbers.py (note062 update, 2026-10-16, P8).

Every test builds a throwaway repository root (scripts/ + research_notes/) in a temp directory, so nothing in
the real repository is read, run or written. Stdlib only.

  python -m unittest discover -s scripts -p 'test_check_numbers.py' -v
"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_numbers as C  # noqa: E402


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "scripts"))
        os.makedirs(os.path.join(self.root, "research_notes"))
        self._root, C.ROOT = C.ROOT, self.root
        self._run = C.run_script

    def tearDown(self):
        C.ROOT = self._root
        C.run_script = self._run
        self.tmp.cleanup()

    def script(self, num, body):
        with open(os.path.join(self.root, "scripts", f"note{num}_reference.py"), "w") as fh:
            fh.write(body)

    def note(self, name, text):
        with open(os.path.join(self.root, "research_notes", name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def main(self, *args):
        """Run main(); return (exit code, stdout, report text)."""
        old, sys.argv = sys.argv, ["check_numbers.py", *args]
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                try:
                    C.main()
                    code = 0
                except SystemExit as e:
                    code = e.code
        finally:
            sys.argv = old
        path = os.path.join(self.root, "results", "NUMBER_CHECK.md")
        report = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        return code, out.getvalue(), report


class SelfTest(Fixture):
    def test_selftest_passes_on_the_real_checker(self):
        with redirect_stdout(io.StringIO()):
            self.assertTrue(C.self_test())

    def test_broken_selftest_exits_1_and_writes_no_report(self):
        self.script("990", "print('AUC 0.98421')\n")
        self.note("note990_x.md", "Uses note990_reference. AUC 0.984.\n")
        C.self_test, real = (lambda: False), C.self_test
        try:
            code, _, report = self.main()
        finally:
            C.self_test = real
        self.assertEqual(1, code)
        self.assertEqual("", report)


class Exit2(Fixture):
    def test_timeout_is_recorded_as_not_run_and_exits_2(self):
        self.script("991", "import time\ntime.sleep(5)\n")
        self.note("note991_x.md", "Uses note991_reference. Value 0.123.\n")
        C.run_script = lambda num: self._run(num, timeout=0.5)
        code, out, report = self.main()
        self.assertEqual(2, code)
        self.assertIn("NOT RUN", out)
        self.assertIn("not run: timed out", report)
        self.assertIn("**Not run:** 991", report)

    def test_clean_run_exits_0(self):
        self.script("992", "print('slope 1.6398')\n")
        self.note("note992_x.md", "Uses note992_reference. Slope 1.6398 here.\n")
        code, out, report = self.main()
        self.assertEqual(0, code)
        self.assertIn("TOTAL 1/1 found", out)

    def test_missing_results_directory_is_created(self):
        self.script("993", "print('x 0.500')\n")
        self.note("note993_x.md", "Uses note993_reference. x 0.500.\n")
        self.assertFalse(os.path.exists(os.path.join(self.root, "results")))
        code, _, report = self.main()
        self.assertEqual(0, code)
        self.assertIn("| 993 |", report)


class Pairing(Fixture):
    def test_note_that_does_not_name_its_script_is_paired_by_filename(self):
        self.script("994", "print('rate 0.0494')\n")
        self.note("note994_bound.md", "The rate was 0.0494 and 0.7411 by hand.\n")
        code, out, report = self.main()
        self.assertEqual(0, code)
        self.assertIn("note994_bound.md (paired by filename", report)
        self.assertIn("| 0 | 2 | 1 | 1 |", report)
        self.assertIn("line 1: `0.7411`", report)

    def test_shared_number_stays_unpaired(self):
        self.script("995", "print('v 0.111')\n")
        self.note("995_first.md", "v 0.111\n")
        self.note("note995_second.md", "v 0.111\n")
        code, _, report = self.main()
        self.assertEqual(0, code)
        self.assertIn("shared by several note files", report)
        self.assertNotIn("paired by filename", report)

    def test_a_note_that_names_its_script_wins_over_filename(self):
        self.script("996", "print('v 0.222')\n")
        self.note("996_old.md", "unrelated 0.999\n")
        self.note("note996_new.md", "Uses note996_reference. v 0.222.\n")
        code, _, report = self.main()
        self.assertEqual(0, code)
        self.assertIn("| 996 | note996_new.md | 0 |", report)


if __name__ == "__main__":
    unittest.main()
