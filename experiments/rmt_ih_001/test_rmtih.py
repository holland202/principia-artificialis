"""Property tests for RMT-IH-001's timing rule and instruments (no training). SELF-TESTED."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze as A  # noqa: E402
import tinyih as T  # noqa: E402

STEPS = list(range(0, 2001, 20))


def step_series(at, lo, hi, n=len(STEPS), noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    x = np.array([lo if s < at else hi for s in STEPS[:n]], float)
    return x + rng.normal(0, noise, len(x))


class Timing(unittest.TestCase):
    def test_recovers_a_known_jump_up_and_down(self):
        for at in (200, 700, 1500):
            self.assertEqual(A.t_change(STEPS, step_series(at, 0, 4), 0.5, 1.0), at)
            self.assertEqual(A.t_change(STEPS, step_series(at, 0.53, 0.47), 0.25, 0.02), at)

    def test_flat_or_small_change_is_none(self):
        self.assertIsNone(A.t_change(STEPS, np.full(len(STEPS), 0.5), 0.25, 0.02))
        self.assertIsNone(A.t_change(STEPS, step_series(700, 0.53, 0.52), 0.25, 0.02))

    def test_a_blip_does_not_count(self):
        x = step_series(1500, 0.53, 0.45)
        x[10:12] = 0.40                       # two-checkpoint blip, shorter than PERSIST
        self.assertEqual(A.t_change(STEPS, x, 0.25, 0.02), 1500)

    def test_direction_matters(self):
        x = step_series(800, 0.53, 0.45)
        x[5:9] = 0.60                         # an excursion the wrong way never triggers
        self.assertEqual(A.t_change(STEPS, x, 0.25, 0.02), 800)

    def test_noisy_jump_found_near_truth(self):
        errs = [abs(A.t_change(STEPS, step_series(1000, 0.53, 0.45, noise=0.005, seed=s), 0.25, 0.02) - 1000)
                for s in range(50)]
        self.assertLessEqual(max(errs), 40)

    def test_before(self):
        self.assertTrue(A.before(100, 200))
        self.assertFalse(A.before(200, 200))
        self.assertFalse(A.before(None, 200))
        self.assertFalse(A.before(100, None))


class Verdicts(unittest.TestCase):
    def fake(self, edge_at, ih_at, top_at, srank_at, nor_drop):
        def rows(edge_at, ih_at, top_at, srank_at, icl_hi, drop):
            e = step_series(edge_at, 0.53, 0.53 - drop)
            i = step_series(ih_at, 0.0, icl_hi)
            t = step_series(top_at, 2.3, 3.0)
            r = step_series(srank_at, 30.0, 20.0)
            return [{"step": s, "edge_r": e[j], "icl": i[j], "top_norm": t[j], "stable_rank": r[j]}
                    for j, s in enumerate(STEPS)]
        runs = {}
        for seed in range(1, 7):
            runs[f"repeat/{seed}"] = rows(edge_at, ih_at, top_at, srank_at, 4.1, 0.06)
            runs[f"norepeat/{seed}"] = rows(edge_at, 3000, top_at, srank_at, 0.0, nor_drop)
        return runs

    def test_early_warning_world_passes(self):
        _, _, v = A.verdicts(self.fake(400, 800, 900, 900, 0.0))
        self.assertTrue(all(ok for ok, _ in v.values()), v)

    def test_rival_first_world_fails_p3_only(self):
        _, _, v = A.verdicts(self.fake(400, 800, 300, 900, 0.0))
        self.assertFalse(v["P3"][0])
        self.assertTrue(v["P2"][0])

    def test_edge_after_jump_fails_p2(self):
        _, _, v = A.verdicts(self.fake(1200, 800, 1300, 1300, 0.0))
        self.assertFalse(v["P2"][0])

    def test_generic_training_world_fails_p4(self):
        _, _, v = A.verdicts(self.fake(400, 800, 900, 900, 0.06))
        self.assertFalse(v["P4"][0])


class Instruments(unittest.TestCase):
    def test_qr_levels_equal_full_svd(self):
        import torch
        torch.manual_seed(3)
        m = T.TinyAttnOnly()
        at = m.attn[1]
        wq = at.q.weight.detach().double().numpy().T
        wk = at.k.weight.detach().double().numpy().T
        dh = T.CFG["d_model"] // T.CFG["n_heads"]
        full = np.sort(np.linalg.svd(wq[:, dh:] @ wk[:, dh:].T, compute_uv=False)[:dh])
        mine = np.sort(T.head_qk_levels(m)[3][2])
        self.assertLess(np.max(np.abs(full - mine)) / full.max(), 1e-12)

    def test_ratio_statistic_on_reference_spectra(self):
        """C1/C2: the statistic returns the GOE value on GOE spectra and the Poisson value on Poisson spectra."""
        rng = np.random.default_rng(0)
        goe, poi = [], []
        for _ in range(400):
            a = rng.normal(size=(128, 128))
            ev = np.linalg.eigvalsh((a + a.T) / 2)
            goe.extend(T.ratios(ev[32:96])[0])
            poi.extend(T.ratios(np.cumsum(rng.exponential(size=64)))[0])
        self.assertAlmostEqual(np.mean(goe), 0.5307, delta=0.01)
        self.assertAlmostEqual(np.mean(poi), 0.3863, delta=0.01)

    def test_data_arms(self):
        x = T.batch(np.random.default_rng(5), "repeat")
        y = T.batch(np.random.default_rng(5), "norepeat")
        s = T.CFG["seg"]
        self.assertTrue(bool((x[:, 1:s + 1] == x[:, s + 1:]).all()))
        self.assertLess(float((y[:, 1:s + 1] == y[:, s + 1:]).float().mean()), 0.05)


if __name__ == "__main__":
    unittest.main()
