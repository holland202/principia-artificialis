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
                 None: "MALFORMED"}
        for text, want in cases.items():
            self.assertEqual(M.classify(self.T, text), want, text)

    def test_no_stale_value_means_never_stale(self):
        self.assertEqual(M.classify({"answer": "6 p.m.", "stale": None}, "ANSWER: 5 p.m."), "WRONG")

    def test_retained_requirements(self):
        self.assertTrue(M.retained_requirements({"needs": ["a", "b"]}, ["a", "b", "c"]))
        self.assertFalse(M.retained_requirements({"needs": ["a", "b"]}, ["a", "c"]))


REV1 = "REV1 (2026-11-16): tests added after Codex's review on PR #159; each failed on the merged draft (see RESULTS)"


class Rev1Contract(unittest.TestCase):
    """A3: exactly one ANSWER line; A1: symmetric normalisation."""

    def test_more_than_one_answer_line_is_malformed(self):
        T = {"answer": "Room C", "stale": "Room A"}
        for text in ("ANSWER: Room A\nANSWER: Room C", "ANSWER: Room C\nANSWER: Room A",
                     "ANSWER: Room C\nANSWER: Room C", "no answer here"):
            self.assertEqual(M.classify(T, text), "MALFORMED", text)

    def test_every_gold_value_round_trips(self):
        for sc in SCEN:
            for t in sc["tasks"]:
                for wrap in ("{}", "{}.", " {} ", '"{}"', "{}".upper()):
                    self.assertEqual(M.classify(t, "ANSWER: " + wrap.format(t["answer"])), "CORRECT", (t, wrap))
                if t.get("stale"):
                    self.assertEqual(M.classify(t, "ANSWER: " + t["stale"] + "."), "STALE")

    def test_exact_punctuated_gold(self):
        self.assertEqual(M.classify({"answer": "6 p.m.", "stale": None}, "ANSWER: 6 p.m."), "CORRECT")


class Rev1Retention(unittest.TestCase):
    """A2: AND over needs, OR over needs_any; no requirement is an error, never a pass."""

    def test_needs_any(self):
        t = {"needs": [], "needs_any": ["x", "y", "z"]}
        self.assertFalse(M.retained_requirements(t, []))
        self.assertFalse(M.retained_requirements(t, ["q"]))
        self.assertTrue(M.retained_requirements(t, ["y"]))
        self.assertTrue(M.retained_requirements(t, ["x", "y", "z"]))

    def test_mixed(self):
        t = {"needs": ["a"], "needs_any": ["x", "y"]}
        self.assertFalse(M.retained_requirements(t, ["a"]))
        self.assertFalse(M.retained_requirements(t, ["x"]))
        self.assertTrue(M.retained_requirements(t, ["a", "x"]))

    def test_malformed_requirements_raise(self):
        for t in ({"needs": []}, {"needs": [], "needs_any": []}, {"needs": "a"}, {"needs": [1]}):
            with self.assertRaises(ValueError):
                M.retained_requirements(t, ["a"])

    def test_dev_redundant_task_with_nothing_kept_is_not_retained(self):
        for sc in SCEN:
            red = [t for t in sc["tasks"] if t["type"] == "redundant"][0]
            self.assertFalse(M.retained_requirements(red, []))


def relabel(sc, seed):
    """Same records and tasks, ids replaced by a random permutation of fresh opaque ids."""
    import random
    s = copy.deepcopy(sc)
    rng = random.Random(seed)
    fresh = [f"z{rng.getrandbits(24):06x}" for _ in s["records"]]
    m = {r["id"]: f for r, f in zip(s["records"], rng.sample(fresh, len(fresh)))}
    for r in s["records"]:
        r["id"] = m[r["id"]]
    return s


def kept_texts(sc, ids):
    by = {r["id"]: r["text"] for r in sc["records"]}
    return sorted(by[i] for i in ids)


class Rev1IdCues(unittest.TestCase):
    """A4: hidden-field scrambling cannot see a cue carried by the ids themselves; relabelling can."""

    def test_deterministic_selectors_ignore_id_labels(self):
        for name in M.SELECTORS:
            if name == "random":
                continue
            for sc in SCEN:
                for b in BUDGETS:
                    r = relabel(sc, 99)
                    self.assertEqual(kept_texts(sc, M.run_selector(name, sc, b)),
                                     kept_texts(r, M.run_selector(name, r, b)), (name, sc["scenario_id"], b))

    def test_relabelling_catches_an_id_only_rule(self):
        def id_rule(view, budget, seed=None):
            return sorted(r["id"] for r in view)[:budget]
        caught = any(kept_texts(sc, id_rule(M.selector_view(sc), 3)) !=
                     kept_texts(relabel(sc, 5), id_rule(M.selector_view(relabel(sc, 5)), 3)) for sc in SCEN)
        self.assertTrue(caught)

    def test_no_kind_sits_at_a_fixed_id_rank(self):
        for kind in ("original", "correction", "critical"):
            ranks = set()
            for sc in SCEN:
                order = sorted(r["id"] for r in sc["records"])
                ranks.add(order.index([r["id"] for r in sc["records"] if r["kind"] == kind][0]))
            self.assertGreaterEqual(len(ranks), 8, kind)

    def test_smallest_id_rule_rarely_finds_the_correction(self):
        hits = sum(min(r["id"] for r in sc["records"]) ==
                   [r["id"] for r in sc["records"] if r["kind"] == "correction"][0] for sc in SCEN)
        self.assertLessEqual(hits, 10)


class Rev1Evidence(unittest.TestCase):
    """A5: world-state score and evidence-relative score are separate."""

    def test_four_conditions_for_a_correction_task(self):
        for sc in SCEN:
            t = [x for x in sc["tasks"] if x["type"] == "correction"][0]
            (c,), new = t["evidence"][0]
            (o,), old = t["evidence"][1]
            self.assertEqual(M.licensed_answer(t, [c, o]), new)
            self.assertEqual(M.licensed_answer(t, [o]), old)
            self.assertEqual(M.licensed_answer(t, [c]), new)
            self.assertEqual(M.licensed_answer(t, []), "UNKNOWN")

    def test_a_lookup_rival_follows_the_evidence_and_is_stale_by_world_score(self):
        """The mundane rival Codex built: answer whatever the retained notes say. It FOLLOWS the evidence in every
        condition, and is STALE by the world score when only the original is kept."""
        sc = SCEN[0]
        t = [x for x in sc["tasks"] if x["type"] == "correction"][0]
        (c,), _ = t["evidence"][0]
        (o,), _ = t["evidence"][1]
        for kept, world in (([c, o], "CORRECT"), ([o], "STALE"), ([c], "CORRECT"), ([], "UNKNOWN")):
            out = "ANSWER: " + M.licensed_answer(t, kept)
            self.assertEqual(M.evidence_outcome(t, kept, out), "FOLLOWS_EVIDENCE")
            self.assertEqual(M.classify(t, out), world)

    def test_every_conjunct_is_needed_and_the_question_states_neither(self):
        for sc in SCEN:
            t = [x for x in sc["tasks"] if x["type"] == "conjunctive"][0]
            p1, p2 = t["needs"]
            self.assertEqual(M.licensed_answer(t, [p1, p2]), t["answer"])
            self.assertEqual(M.licensed_answer(t, [p1]), "UNKNOWN")
            self.assertEqual(M.licensed_answer(t, [p2]), "UNKNOWN")
            texts = {r["id"]: r["text"] for r in sc["records"]}
            self.assertNotIn(t["answer"], t["q"])
            for p in (p1, p2):
                self.assertNotIn(texts[p].rstrip("."), t["q"])

    def test_licensed_answers_match_keys_with_full_memory(self):
        for sc in SCEN:
            every = [r["id"] for r in sc["records"]]
            for t in sc["tasks"]:
                self.assertEqual(M.licensed_answer(t, every), t["answer"])


class Rev1Prompt(unittest.TestCase):
    def test_prompt_shows_text_only(self):
        sc = SCEN[3]
        kept = [r["id"] for r in sc["records"]][:6]
        p = M.build_prompt(sc["tasks"][0]["q"], sc, kept)
        for i in kept:
            self.assertNotIn(i, p)
        self.assertEqual(p.count("\n- "), 6)
        self.assertIn("ANSWER: UNKNOWN", p)
        self.assertIn("(none)", M.build_prompt("q?", sc, []))

    def test_prompt_depends_only_on_retained_text(self):
        """A5 as a property: two histories with equal retained text give byte-identical prompts."""
        sc = SCEN[0]
        t = [x for x in sc["tasks"] if x["type"] == "correction"][0]
        (o,), _ = t["evidence"][1]
        other = copy.deepcopy(sc)
        other["records"] = [r for r in other["records"] if r["kind"] != "correction"]
        self.assertEqual(M.build_prompt(t["q"], sc, [o]), M.build_prompt(t["q"], other, [o]))


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
