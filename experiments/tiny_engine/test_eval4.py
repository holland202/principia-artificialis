"""Checks for TINY-ENGINE-004: answer_layout, old configs unchanged, fail-closed scorer that can say both things.
Claude (Anthropic, Opus 5.5), 2026-11-20. SELF-TESTED only."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
import torch
import engine as E

HERE = Path(__file__).parent


class Layout(unittest.TestCase):
    def test_coupled_ids(self):
        x = torch.tensor([[0, 5, 6, 5, 128, 5, 6, 5, 9], [0, 5, 6, 7, 8, 9, 10, 11, 12]])
        after, pos = E.answer_layout(x)
        self.assertEqual(pos.tolist(), [[0, 1, 2, 3, 0, 1, 2, 3, 4], list(range(9))])
        self.assertEqual(after.int().tolist(), [[0, 0, 0, 0, 0, 1, 1, 1, 1], [0] * 9])

    def test_answer_token_shares_source_id(self):
        k = 40
        x = torch.tensor([[0] + list(range(1, k + 1)) + [128] + list(range(1, k + 1))])
        _, pos = E.answer_layout(x)
        for i in range(k):
            self.assertEqual(int(pos[0, 1 + i]), int(pos[0, k + 2 + i]))

    def test_coupling_changes_output_label_off_does_not_leak(self):
        torch.manual_seed(0); b = E.TinyEngine(E.CFG4B)
        torch.manual_seed(0); c = E.TinyEngine(E.CFG4C)
        x = torch.tensor([[0, 5, 6, 128, 5, 6]])
        self.assertFalse(torch.allclose(b(x), c(x)))          # coupling is actually applied
        y = torch.tensor([[0, 5, 6, 7, 8, 9]])               # no SEP: coupling must do nothing
        self.assertTrue(torch.allclose(b(y), c(y)))


def fake(d, arm, cfg, val):
    p = d / arm; p.mkdir(parents=True)
    for i, s in enumerate((21, 22, 23, 24, 25, 26)):
        sc = {f"{t}_L{L}": 0.99 for L in (128, 256, 512, 1024) for t in ("periodic_heldout", "recall", "copy")}
        sc.update(tf_alpha8_k127=val + 0.001 * i, free_alpha8_k63=val, tf_alpha8_k127_uncoupled=0.3 + 0.001 * i)
        (p / f"seed{s}.json").write_text(json.dumps({"seed": s, "cfg": cfg, "scores": sc}))


def score(d):
    r = subprocess.run([sys.executable, str(HERE / "score4.py"), str(d)], capture_output=True, text=True, cwd=HERE)
    return r.returncode, r.stdout


class Scorer(unittest.TestCase):
    def test_both_directions(self):
        for vals, want in (((0.5, 0.4, 0.99), "HELD"), ((0.5, 0.6, 0.55), "FAILED")):
            with tempfile.TemporaryDirectory() as t:
                d = Path(t)
                for arm, cfg, v in zip("ABC", (E.CFG3, E.CFG4B, E.CFG4C), vals):
                    fake(d, arm, cfg, v)
                rc, out = score(d)
                self.assertEqual(rc, 0, out)
                for line in out.splitlines():
                    if line.startswith(("P1", "P2", "P5")):
                        self.assertIn(want, line, line)

    def test_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); fake(d, "A", E.CFG3, .5); fake(d, "B", E.CFG4B, .4)
            self.assertEqual(score(d)[0], 2)                  # arm C missing
            fake(d, "C", E.CFG4B, .99)
            self.assertEqual(score(d)[0], 2)                  # arm C carries arm B's config


if __name__ == "__main__":
    unittest.main()
