"""Anti-vacuity and fail-closed checks for eval3.py / score3.py (REGISTRATION_003.md P5).
Claude (Anthropic, Opus 5.5), 2026-11-20. SELF-TESTED only."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
import engine as E
import eval3

HERE = Path(__file__).parent


class Oracle(torch.nn.Module):
    """Predicts the copy exactly: the token k+1 positions back. shift=1 makes it off by one."""
    def __init__(self, k, shift=0):
        super().__init__(); self.k, self.shift = k, shift
    def forward(self, x):
        # position t predicts x[t+1]; in the copy, x[t+1] = x[t-k] (k source tokens plus SEP back)
        return F.one_hot(torch.roll(x, self.k + self.shift, 1), E.VOCAB).float()


class Cases(unittest.TestCase):
    def test_families(self):
        rng = np.random.default_rng(0)
        for fam, cap in (("distinct", None), ("alpha32", 32), ("alpha8", 8)):
            x, m = eval3.case(rng, 63, fam)
            s = x[1:64]
            self.assertEqual(x[64], E.SEP); self.assertTrue((x[65:128] == s).all())
            self.assertFalse(m[:64].any()); self.assertTrue(m[64:127].all())
            if cap is None:
                self.assertEqual(len(set(s)), 63)
            else:
                self.assertLessEqual(len(set(s)), cap); self.assertLess(len(set(s)), 63)


class Scores(unittest.TestCase):
    def test_tf_oracle_and_offbyone(self):
        for fam in eval3.FAMS:
            self.assertEqual(eval3.tf_acc(Oracle(63), fam, 63, 1, n=32), 1.0)
            self.assertLess(eval3.tf_acc(Oracle(63, shift=1), fam, 63, 1, n=32), 0.5)

    def test_free_oracle_and_offbyone(self):
        self.assertEqual(eval3.free_whole(Oracle(63), "alpha8", 63, 2, n=16), 1.0)
        self.assertEqual(eval3.free_whole(Oracle(63, shift=1), "alpha8", 63, 2, n=16), 0.0)

    def test_untrained_below_005(self):
        torch.manual_seed(991)
        r = eval3.evaluate3(E.TinyEngine(E.CFG3))
        self.assertTrue(all(v < 0.05 for v in r.values()), r)


def fake(d, arm, cfg, seeds, b_wins):
    p = d / arm; p.mkdir(parents=True)
    for i, s in enumerate(seeds):
        sc = {f"{t}_L{L}": 0.99 for L in (128, 256, 512, 1024) for t in ("periodic_heldout", "recall", "copy")}
        base = 0.6 + 0.001 * i
        up = (arm == "B") == b_wins
        sc.update(tf_alpha8_k63=base + (0.2 if up else 0), tf_alpha8_k127=0.5 + 0.001 * i,
                  free_distinct_k127=base + (0.2 if up else 0))
        (p / f"seed{s}.json").write_text(json.dumps({"seed": s, "cfg": cfg, "scores": sc}))


def score(d):
    r = subprocess.run([sys.executable, str(HERE / "score3.py"), str(d)], capture_output=True, text=True, cwd=HERE)
    return r.returncode, r.stdout


class Scorer(unittest.TestCase):
    S = (11, 12, 13, 14, 15, 16)

    def test_both_verdicts_reachable(self):
        for b_wins, word in ((True, "HELD"), (False, "FAILED")):
            with tempfile.TemporaryDirectory() as t:
                d = Path(t); fake(d, "A", E.CFG2, self.S, b_wins); fake(d, "B", E.CFG3, self.S, b_wins)
                rc, out = score(d)
                self.assertEqual(rc, 0, out)
                for line in out.splitlines():
                    if line.startswith(("P1", "P2")):
                        self.assertIn(word, line)

    def test_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); fake(d, "A", E.CFG2, self.S, True)
            self.assertEqual(score(d)[0], 2)                          # arm B missing
            fake(d, "B", E.CFG2, self.S, True)
            self.assertEqual(score(d)[0], 2)                          # arm B has arm A's config
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); fake(d, "A", E.CFG2, self.S, True); fake(d, "B", E.CFG3, self.S[:5], True)
            self.assertEqual(score(d)[0], 2)                          # a seed missing


if __name__ == "__main__":
    unittest.main()
