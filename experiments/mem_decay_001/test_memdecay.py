"""Spec-derived property tests for memdecay.py (no answer key). SELF-TESTED: author Claude Opus 5.5, 2026-11-13.

They check what each arm and the guard must do by definition, on seeded random inputs. They compute no
registered metric. Run: python -m unittest discover -s experiments/mem_decay_001 -p 'test_memdecay.py' -v
"""
import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memdecay as m  # noqa: E402

STORE, QUERIES = m.build("dev")
T = float(np.median(STORE["age"]))
RNG = np.random.default_rng(7)
PROBES = [m.unit(RNG.normal(size=m.D)) for _ in range(60)] + [q["qvec"] for q in QUERIES[::7]]


class Arms(unittest.TestCase):
    def test_a0_is_descending_cosine_over_everything(self):
        alive = m.candidates(STORE, "A0", T)
        for q in PROBES:
            top = m.topk(STORE, q, "A0", "G0", T, T, alive)
            sims = STORE["vec"] @ q
            self.assertEqual(len(top), m.K)
            self.assertEqual(len(set(top)), m.K)
            self.assertTrue(all(sims[a] >= sims[b] for a, b in zip(top, top[1:])))
            self.assertGreaterEqual(min(sims[top]), np.sort(sims)[-m.K])

    def test_a3_with_infinite_half_life_equals_a0(self):
        alive = m.candidates(STORE, "A0", T)
        for q in PROBES:
            self.assertEqual(m.topk(STORE, q, "A3", "G0", T, float("inf"), alive),
                             m.topk(STORE, q, "A0", "G0", T, T, alive))

    def test_a3_deletes_nothing_and_never_raises_a_score(self):
        self.assertTrue(m.candidates(STORE, "A3", T).all())
        factor = np.exp(-math.log(2) * STORE["age"] / T)
        self.assertTrue(((factor > 0) & (factor <= 1)).all())

    def test_deletion_arms_respect_their_rules(self):
        a1 = m.candidates(STORE, "A1", T)
        a4 = m.candidates(STORE, "A4", T)
        a2 = m.candidates(STORE, "A2", T)
        self.assertTrue((STORE["age"][a1] <= T).all())
        self.assertTrue(((STORE["age"][a4] <= T) | STORE["critical"][a4]).all())
        self.assertTrue(STORE["critical"][STORE["critical"]].all() and a4[STORE["critical"]].all())
        self.assertEqual(int(a2.sum()), len(a2) // 2)
        self.assertLessEqual(STORE["access"][a2].max(), STORE["access"][~a2].min())
        for arm, alive in (("A1", a1), ("A2", a2), ("A4", a4)):
            for q in PROBES:
                self.assertTrue(all(alive[i] for i in m.topk(STORE, q, arm, "G0", T, T, alive)))

    def test_guard_g1_returns_only_current_records(self):
        for arm in m.ARMS:
            alive = m.candidates(STORE, arm, T)
            for q in PROBES:
                top = m.topk(STORE, q, arm, "G1", T, T, alive)
                self.assertTrue(all(STORE["status"][i] == m.CURRENT for i in top))

    def test_g0_can_return_non_current_records(self):
        """Anti-vacuity for the guard test: without the guard, a revoked record does come back."""
        alive = m.candidates(STORE, "A0", T)
        q = next(qd for qd in QUERIES if qd["cat"] == "revoked")
        self.assertIn(q["revoked"], m.topk(STORE, q["qvec"], "A0", "G0", T, T, alive))


class Build(unittest.TestCase):
    def test_build_is_deterministic(self):
        s2, q2 = m.build("dev")
        self.assertEqual(m.canonical(STORE, QUERIES), m.canonical(s2, q2))

    def test_dev_and_test_differ(self):
        s3, q3 = m.build("test")
        self.assertNotEqual(m.canonical(STORE, QUERIES), m.canonical(s3, q3))

    def test_integrity_gate_passes_real_dev_and_catches_planted_defects(self):
        _, _, problems = m.integrity_gate(STORE, QUERIES, "dev")
        self.assertEqual(problems, [])
        _, _, p1 = m.integrity_gate(STORE, QUERIES[:-1], "dev")
        self.assertTrue(any("queries" in p for p in p1))
        young = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in STORE.items()}
        young["age"][np.flatnonzero(young["critical"])[0]] = 0.0
        _, _, p2 = m.integrity_gate(young, QUERIES, "dev")
        self.assertTrue(any("critical" in p for p in p2))

    def test_shuffled_ages_keep_the_same_multiset(self):
        s, _ = m.build("dev", shuffle_ages=True)
        self.assertTrue(np.array_equal(np.sort(s["age"]), np.sort(STORE["age"])))
        self.assertFalse(np.array_equal(s["age"], STORE["age"]))


class Stats(unittest.TestCase):
    def test_wilson_contains_the_estimate_and_stays_in_bounds(self):
        rng = np.random.default_rng(11)
        for _ in range(500):
            n = int(rng.integers(1, 400))
            k = int(rng.integers(0, n + 1))
            lo, hi = m.wilson(k, n)
            self.assertTrue(0 <= lo <= k / n <= hi <= 1)

    def test_wilson_ends_are_exact(self):
        """Added after mutant M8 survived the random test: every n from 1 to 400, at k = 0 and k = n."""
        for n in range(1, 401):
            self.assertEqual(m.wilson(0, n)[0], 0.0)
            self.assertEqual(m.wilson(n, n)[1], 1.0)


if __name__ == "__main__":
    unittest.main()
