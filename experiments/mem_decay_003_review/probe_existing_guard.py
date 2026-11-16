#!/usr/bin/env python3
"""Insert the public ID shortcut into the original hidden-field test.

Codex / OpenAI GPT-6 Astra; self-tested; human review direction only;
editing pending; Chad Holland responsible. No model or held-out data.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mem_decay_003"))
import test_memdecay3 as T


def id_rule(view, budget, seed):
    return [r["id"] for r in view if r["id"] == "m001"][:budget]


if __name__ == "__main__":
    T.M.SELECTORS["review_id_only_shortcut"] = id_rule
    suite = unittest.TestSuite([T.Blindness("test_every_selector_ignores_hidden_fields")])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("ID-only shortcut included in original hidden-field guard:", result.wasSuccessful())
    raise SystemExit(0 if result.wasSuccessful() else 1)
