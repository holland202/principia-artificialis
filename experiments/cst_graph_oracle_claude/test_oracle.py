"""Tests for Claude's CST graph oracle: hand cases, invalid inputs, a second formulation on random graphs,
counterfactual pairs that defeat each shortcut, and mutants that must be killed."""
import os
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle as O  # noqa: E402


def case(nodes, reports, same_as=None):
    return {"nodes": nodes, "reports": reports, "same_as": same_as or []}


ORIG = {"o1": None, "o2": None}


class Hand(unittest.TestCase):
    def test_depth1(self):
        self.assertEqual(O.decide(case({**ORIG, "r1": "o1", "r2": "o1"}, ["r1", "r2"])), "INSUFFICIENT")
        self.assertEqual(O.decide(case({**ORIG, "r1": "o1", "r2": "o2"}, ["r1", "r2"])), "CONFIRMED")

    def test_depth2(self):
        g = {**ORIG, "m": "o1", "n": "o2", "r1": "o1"}
        self.assertEqual(O.decide(case({**g, "r2": "m"}, ["r1", "r2"])), "INSUFFICIENT")
        self.assertEqual(O.decide(case({**g, "r2": "n"}, ["r1", "r2"])), "CONFIRMED")

    def test_alias_sharing_without_repetition(self):
        g = {"cs903": None, "wed_sheet": None, "r1": "cs903", "r2": "wed_sheet"}
        self.assertEqual(O.decide(case(g, ["r1", "r2"])), "CONFIRMED")
        self.assertEqual(O.decide(case(g, ["r1", "r2"], [["cs903", "wed_sheet"]])), "INSUFFICIENT")

    def test_repetition_without_sharing(self):
        # o1 is used three times, but the two selected reports rest on different originals
        g = {**ORIG, "x": "o1", "y": "o1", "r1": "o1", "r2": "o2"}
        self.assertEqual(O.decide(case(g, ["r1", "r2"])), "CONFIRMED")

    def test_report_uses_other_report(self):
        g = {**ORIG, "r1": "o1", "r2": "r1"}
        self.assertEqual(O.decide(case(g, ["r1", "r2"])), "INSUFFICIENT")

    def test_alias_transitive(self):
        g = {"a": None, "b": None, "c": None, "r1": "a", "r2": "c"}
        self.assertEqual(O.decide(case(g, ["r1", "r2"], [["a", "b"], ["b", "c"]])), "INSUFFICIENT")


class Invalid(unittest.TestCase):
    def bad(self, c):
        with self.assertRaises(O.Invalid):
            O.decide(c)

    def test_invalid_inputs(self):
        self.bad(case({**ORIG, "r1": "o1"}, ["r1"]))                                   # one report
        self.bad(case({**ORIG, "r1": "o1"}, ["r1", "r1"]))                             # same report twice
        self.bad(case({**ORIG, "r1": "o1", "r2": "zz"}, ["r1", "r2"]))                 # dangling
        self.bad(case({**ORIG, "r1": "r2", "r2": "r1"}, ["r1", "r2"]))                 # cycle
        self.bad(case({**ORIG, "r1": "o1"}, ["r1", "o2"]))                             # report is an original
        self.bad(case({**ORIG, "r1": "o1", "r2": ["o1", "o2"]}, ["r1", "r2"]))         # multi-parent
        self.bad(case({**ORIG, "r1": "o1", "r2": "o2"}, ["r1", "r2"], [["o1", "r1"]]))  # alias to non-original
        self.bad(case({**ORIG, "r1": "o1", "r2": "o2", "u": "v", "v": "u"}, ["r1", "r2"]))  # unused cycle


def second_formulation(c):
    """Independent formulation: spread original classes DOWN the tree from originals, then compare reports."""
    nodes = c["nodes"]
    cls = {n: n for n, p in nodes.items() if p is None}
    changed = True
    while changed:                                   # merge alias classes by relabelling to the min label
        changed = False
        for a, b in c["same_as"]:
            lo = min(cls[a], cls[b])
            for k, v in list(cls.items()):
                if v in (cls[a], cls[b]) and v != lo:
                    cls[k] = lo
                    changed = True
    label = dict(cls)
    frontier = list(cls)
    while frontier:
        nxt = []
        for n, p in nodes.items():
            if p in frontier and n not in label:
                label[n] = label[p]
                nxt.append(n)
        frontier = nxt
    a, b = c["reports"]
    return "CONFIRMED" if label[a] != label[b] else "INSUFFICIENT"


def random_case(rng):
    k = rng.randint(1, 4)
    origs = [f"o{i}" for i in range(k)]
    nodes = {o: None for o in origs}
    for i in range(rng.randint(2, 9)):
        nodes[f"n{i}"] = rng.choice(list(nodes))
    nonorig = [n for n, p in nodes.items() if p is not None]
    same_as = [rng.sample(origs, 2) for _ in range(rng.randint(0, 2))] if k >= 2 else []
    return case(nodes, rng.sample(nonorig, 2), same_as)


class Property(unittest.TestCase):
    def test_agrees_with_second_formulation_on_2000_random_graphs(self):
        rng = random.Random(20261116)
        both = {"CONFIRMED": 0, "INSUFFICIENT": 0}
        for _ in range(2000):
            c = random_case(rng)
            got = O.decide(c)
            self.assertEqual(got, second_formulation(c), c)
            both[got] += 1
        self.assertTrue(both["CONFIRMED"] > 200 and both["INSUFFICIENT"] > 200, both)   # both outcomes covered


class Shortcuts(unittest.TestCase):
    """For each shortcut: two cases the rule answers the SAME way whose correct answers DIFFER."""
    PAIRS = {
        "last_letter": (case({"oA": None, "oB": None, "mB": "oA", "r1": "oA", "r2": "mB"}, ["r1", "r2"]),
                        case({"oA": None, "oB": None, "mB": "oB", "r1": "oA", "r2": "mB"}, ["r1", "r2"])),
        "repeat_count": (case({**ORIG, "x": "o1", "r1": "o1", "r2": "o1"}, ["r1", "r2"]),
                         case({**ORIG, "x": "o1", "y": "o1", "r1": "o1", "r2": "o2"}, ["r1", "r2"])),
        "id_repeat_in_text": (case({"cs903": None, "wed": None, "r1": "cs903", "r2": "wed"}, ["r1", "r2"],
                                   [["cs903", "wed"]]),
                              case({"cs903": None, "wed": None, "r1": "cs903", "r2": "wed"}, ["r1", "r2"])),
        "report_parent_equal": (case({**ORIG, "m": "o1", "r1": "o1", "r2": "m"}, ["r1", "r2"]),
                                case({**ORIG, "m": "o2", "r1": "o1", "r2": "m"}, ["r1", "r2"])),
    }

    def test_every_shortcut_is_defeated_by_a_counterfactual_pair(self):
        self.assertEqual(set(self.PAIRS), set(O.SHORTCUTS))
        for name, (c1, c2) in self.PAIRS.items():
            rule = O.SHORTCUTS[name]
            self.assertEqual(rule(c1), rule(c2), name)
            self.assertNotEqual(O.decide(c1), O.decide(c2), name)


class Mutants(unittest.TestCase):
    """Each mutant of decide() must fail at least one hand test."""
    def run_hand(self):
        failures = 0
        for t in ("test_depth1", "test_depth2", "test_alias_sharing_without_repetition",
                  "test_repetition_without_sharing", "test_report_uses_other_report", "test_alias_transitive"):
            try:
                getattr(Hand(t), t)()
            except Exception:          # a wrong answer or a crash both kill the mutant
                failures += 1
        return failures

    def test_mutants_killed(self):
        orig_classes, orig_root = O._classes, O._root
        mutants = {
            "ignore_same_as": lambda: setattr(O, "_classes", lambda nodes, same_as: (lambda x: x)),
            "one_hop_only": lambda: setattr(O, "_root", lambda nodes, s: s if nodes[s] is None else nodes[s]),
        }
        for name, apply in mutants.items():
            apply()
            try:
                self.assertGreater(self.run_hand(), 0, f"mutant {name} survived")
            finally:
                O._classes, O._root = orig_classes, orig_root


@unittest.skipUnless(os.environ.get("CODEX_INSTRUMENT"), "set CODEX_INSTRUMENT to instrument.py to cross-check")
class CrossCheck(unittest.TestCase):
    def test_agrees_with_codex_oracle_on_its_qualification_cases(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("instrument", os.environ["CODEX_INSTRUMENT"])
        ins = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ins)
        for c in ins.qualification_cases():
            mine = O.decide({"nodes": c["nodes"], "reports": c["reports"]})
            self.assertEqual(c["mapping"][mine], ins.answer(c), c["case_id"])


if __name__ == "__main__":
    unittest.main()
