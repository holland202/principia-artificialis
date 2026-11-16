"""Qualification tests for the MEM-DECAY-003 instrument (no model involved)."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dev_family as D  # noqa: E402
import memdecay3 as M  # noqa: E402

SCEN = [D.scenario(s) for s in range(40)]
BUDGETS = (3, 6, 10)


def scramble_hidden(sc):
    """Same visible fields; every hidden field changed or removed."""
    s = copy.deepcopy(sc)
    for r in s["records"]:
        r["kind"] = "filler"
    s["tasks"] = [{"q": "x", "answer": "y", "stale": None, "needs": [], "type": "none"}]
    return s


class Blindness(unittest.TestCase):
    def test_view_has_only_visible_fields(self):
        for sc in SCEN:
            for r in M.selector_view(sc):
                self.assertEqual(set(r), set(M.VISIBLE))

    def test_every_selector_ignores_hidden_fields(self):
        for name in M.SELECTORS:
            for sc in SCEN:
                for b in BUDGETS:
                    self.assertEqual(M.run_selector(name, sc, b, 7), M.run_selector(name, scramble_hidden(sc), b, 7),
                                     (name, sc["scenario_id"], b))

    def test_invariance_check_catches_a_leaky_selector(self):
        def leaky(view, budget, seed):        # tries to read 'kind' through the raw scenario it closes over
            raise AssertionError("unreachable")
        # a selector given the raw scenario instead of the view would see 'kind'; show the check detects that
        def leaky_on_raw(sc, b):
            return [r["id"] for r in sc["records"] if r["kind"] in ("correction", "critical")][:b]
        caught = any(leaky_on_raw(sc, 6) != leaky_on_raw(scramble_hidden(sc), 6) for sc in SCEN)
        self.assertTrue(caught)
        with self.assertRaises(KeyError):      # and the view itself has no 'kind' to read
            M.selector_view(SCEN[0])[0]["kind"]


class Budget(unittest.TestCase):
    def test_budget_and_ids(self):
        for name in M.SELECTORS:
            for sc in SCEN:
                for b in BUDGETS:
                    kept = M.run_selector(name, sc, b, 3)
                    self.assertLessEqual(len(kept), b)
                    self.assertEqual(len(kept), len(set(kept)))
                    self.assertTrue(set(kept) <= {r["id"] for r in sc["records"]})

    def test_check_rejects_bad_output(self):
        view = M.selector_view(SCEN[0])
        with self.assertRaises(ValueError):
            M._check(view, 2, [view[0]["id"]] * 2)
        with self.assertRaises(ValueError):
            M._check(view, 2, ["nope"])
        with self.assertRaises(ValueError):
            M._check(view, 1, [view[0]["id"], view[1]["id"]])

    def test_deterministic(self):
        for name in M.SELECTORS:
            self.assertEqual(M.run_selector(name, SCEN[5], 6, 11), M.run_selector(name, SCEN[5], 6, 11))


class Decisions(unittest.TestCase):
    T = {"answer": "Room C", "stale": "Room A"}

    def test_classify(self):
        cases = {"ANSWER: Room C": "CORRECT", "answer: room c.": "CORRECT", "ANSWER: Room A": "STALE",
                 "ANSWER: UNKNOWN": "UNKNOWN", "ANSWER: Room B": "WRONG", "Room C": "MALFORMED",
                 "ANSWER: Room A\nANSWER: Room C": "CORRECT", None: "MALFORMED"}
        for text, want in cases.items():
            self.assertEqual(M.classify(self.T, text), want, text)

    def test_no_stale_value_means_never_stale(self):
        self.assertEqual(M.classify({"answer": "6 p.m.", "stale": None}, "ANSWER: 5 p.m."), "WRONG")

    def test_retained_requirements(self):
        self.assertTrue(M.retained_requirements({"needs": ["a", "b"]}, ["a", "b", "c"]))
        self.assertFalse(M.retained_requirements({"needs": ["a", "b"]}, ["a", "c"]))


class Scenarios(unittest.TestCase):
    def test_answer_key_is_consistent_with_records(self):
        for sc in SCEN:
            ids = {r["id"]: r for r in sc["records"]}
            for t in sc["tasks"]:
                for n in t["needs"]:
                    self.assertIn(n, ids)
                if t["type"] == "correction":
                    corr = ids[t["needs"][0]]
                    self.assertIn(t["answer"], corr["text"])
                    orig = [r for r in sc["records"] if r["kind"] == "original"][0]
                    self.assertIn(t["stale"], orig["text"])
                    self.assertNotEqual(t["answer"], t["stale"])


if __name__ == "__main__":
    unittest.main()
