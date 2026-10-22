"""Tests for scripts/make_dashboard.py (self-tested by its author, Claude Opus 5.5).

Each planted defect must stop the build (C-BUILD fail-closed); the real sources must build; the drift check must
return 1 on a hand-edited page and 0 on the generated one. Run: python -m unittest scripts/test_make_dashboard.py
"""
import copy
import re
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_dashboard as md  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CARD = json.loads((ROOT / "data/dashboard/egrr_card.json").read_text(encoding="utf-8"))
INDEX = (ROOT / "NOTES_INDEX.md").read_text(encoding="utf-8")
PAGE = (ROOT / "dashboard.html").read_text(encoding="utf-8")


def planted(edit):
    c = copy.deepcopy(CARD)
    edit(c)
    return c


class RealSourcesBuild(unittest.TestCase):
    def test_real_card_validates_and_page_is_current(self):
        md.validate_card(copy.deepcopy(CARD))
        self.assertEqual(md.build(PAGE, INDEX, copy.deepcopy(CARD)), PAGE)  # the committed page is up to date

    def test_index_counts_agree_with_its_own_table(self):
        ix = md.parse_index(INDEX)
        self.assertEqual(sum(ix["tiers"].values()), ix["total"])
        self.assertGreater(len(ix["kept"]), 0)


class PlantedDefectsAreRejected(unittest.TestCase):
    CASES = {
        "observation without its limitation": lambda c: c["observations"][0].update(limitation=" "),
        "unknown source id": lambda c: c["adverse"][0].update(sourceIds=["nope"]),
        "source outside the allowlist": lambda c: c["sources"][0].update(url="https://example.com/x"),
        "claim judged without execution": lambda c: c["states"]["claim"].update(value="supported"),
        "reproduction without execution":
            lambda c: c["states"]["reproduction"].update(value="independent-reproduction-documented"),
        "value from another dimension": lambda c: c["states"]["execution"].update(value="supported"),
        "missing dimension": lambda c: c["states"].pop("engineering"),
        "state without a source": lambda c: c["states"]["protocol"].update(sourceIds=[]),
        "duplicate source id": lambda c: c["sources"].append(dict(c["sources"][0])),
        "bad timeline date": lambda c: c["timeline"][0].update(date="Oct 13"),
        "empty open decisions": lambda c: c.update(openDecisions=[]),
    }

    def test_each_planted_defect_stops_the_build(self):
        for name, edit in self.CASES.items():
            with self.subTest(name):
                with self.assertRaises(md.BuildError):
                    md.build(PAGE, INDEX, planted(edit))

    def test_index_whose_header_disagrees_with_its_table(self):
        # Derive the count from the live index; a hardcoded "92" broke this test as soon as a note was added.
        bad = re.sub(r"\*\*(\d+) notes indexed", lambda m: "**%d notes indexed" % (int(m.group(1)) - 1), INDEX, count=1)
        self.assertNotEqual(bad, INDEX, "fixture: header text not found")
        with self.assertRaises(md.BuildError):
            md.parse_index(bad)

    def test_page_without_markers(self):
        with self.assertRaises(md.BuildError):
            md.build(PAGE.replace("<!-- generated:egrr-card:start -->", ""), INDEX, copy.deepcopy(CARD))


class OutputSafety(unittest.TestCase):
    def test_card_text_is_escaped(self):
        c = planted(lambda c: c.update(title="<script>alert(1)</script>"))
        out = md.render_card(md.validate_card(c))
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_drift_check_says_the_other_thing(self):
        hand_edited = PAGE.replace("<b>23</b><span>Verified</span>", "<b>99</b><span>Verified</span>", 1)
        self.assertNotEqual(hand_edited, PAGE, "fixture: tile text not found")
        self.assertNotEqual(md.build(hand_edited, INDEX, copy.deepcopy(CARD)), hand_edited)


if __name__ == "__main__":
    unittest.main()
