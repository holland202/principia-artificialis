"""Tests for guard.py and the two scorers (no training). Each attack must make the scorer refuse (exit 2, no verdict);
the real result sets must still score exactly as before. SELF-TESTED."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1 = ROOT / "results" / "tiny_engine"
V2 = ROOT / "results" / "tiny_engine" / "002"


def score(script, d):
    p = subprocess.run([sys.executable, str(HERE / script), str(d)], capture_output=True, text=True, cwd=HERE)
    return p.returncode, p.stdout


def copy_set(src):
    d = Path(tempfile.mkdtemp())
    for f in src.glob("seed*.json"):
        shutil.copy(f, d / f.name)
    return d


class RealSets(unittest.TestCase):
    def test_v1_verdicts_unchanged(self):
        code, out = score("score.py", V1)
        self.assertEqual(code, 0)
        self.assertIn("Q1: HELD (6/6", out)
        self.assertIn("Q2: FAILED (1/6", out)
        self.assertIn("Q3: HELD (6/6", out)

    def test_v2_verdicts_unchanged(self):
        code, out = score("score2.py", V2)
        self.assertEqual(code, 0)
        for q in ("Q1", "Q2", "Q3", "Q4"):
            self.assertIn(f"{q}: HELD (6/6", out)


class Attacks(unittest.TestCase):
    def refused(self, script, d):
        code, out = score(script, d)
        self.assertEqual(code, 2, out)
        self.assertIn("INVALID RESULT SET", out)
        self.assertNotIn("HELD", out)
        self.assertNotIn("FAILED", out)

    def test_five_copies_of_one_seed(self):
        """Codex's counterexample, PR #163."""
        d = Path(tempfile.mkdtemp())
        for i in range(1, 6):
            shutil.copy(V2 / "seed1.json", d / f"seed{i}.json")
        self.refused("score2.py", d)

    def test_six_copies_with_seed_field_rewritten(self):
        d = Path(tempfile.mkdtemp())
        r = json.loads((V2 / "seed1.json").read_text())
        for i in range(1, 7):
            (d / f"seed{i}.json").write_text(json.dumps(dict(r, seed=i)))
        self.refused("score2.py", d)

    def test_missing_result(self):
        d = copy_set(V2)
        (d / "seed6.json").unlink()
        self.refused("score2.py", d)

    def test_extra_seed(self):
        d = copy_set(V2)
        shutil.copy(V2 / "seed1.json", d / "seed7.json")
        self.refused("score2.py", d)

    def test_wrong_config(self):
        d = copy_set(V2)
        r = json.loads((d / "seed3.json").read_text())
        r["cfg"]["steps"] = 100
        (d / "seed3.json").write_text(json.dumps(r))
        self.refused("score2.py", d)

    def test_v1_results_rejected_by_v2_scorer(self):
        self.refused("score2.py", V1)

    def test_bad_score_values(self):
        for bad in (None, "0.99", 1.5, -0.1, float("nan"), True):
            d = copy_set(V2)
            r = json.loads((d / "seed2.json").read_text())
            r["scores"]["copy_L256"] = bad
            (d / "seed2.json").write_text(json.dumps(r))
            with self.subTest(bad=bad):
                self.refused("score2.py", d)

    def test_seed_field_mismatch(self):
        d = copy_set(V2)
        r = json.loads((d / "seed4.json").read_text())
        r["seed"] = 9
        (d / "seed4.json").write_text(json.dumps(r))
        self.refused("score2.py", d)


if __name__ == "__main__":
    unittest.main()
