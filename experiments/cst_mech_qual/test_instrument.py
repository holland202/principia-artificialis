"""Registered checks for public fixtures. No model data or holdout access.

Codex / OpenAI GPT-6 Astra, 2026-11-15. Self-tested, direction-only human review.
"""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

import instrument as subject


def rejects(call):
    try:
        call()
    except (ValueError, TypeError, KeyError):
        return True
    return False


def run_registered_checks(sabotage=False):
    examples = subject.gates()
    both = examples["both_benefit"]
    q1 = (both["pr152_gate"] and not both["directional_gate"] and
          both["shallow"]["mean"] == "1/4" and both["deep"]["mean"] == "1" and
          both["interaction"]["mean"] == "3/4" and
          Fraction(both["interaction"]["p"]) == Fraction(1, 2 ** 48))
    q2 = (examples["crossover"]["directional_gate"] and examples["crossover"]["specificity_gate"] and
          all(not examples[name]["directional_gate"] for name in
              ("both_benefit", "deep_only", "no_effect", "reverse")) and
          examples["generic_matches"]["directional_gate"] and
          not examples["generic_matches"]["specificity_gate"])

    cases = subject.qualification_cases()
    graph_checks, body_lengths = [], {}
    for c in cases:
        roots, depth = subject.roots_by_paths(c["nodes"], c["reports"])
        other = subject.roots_by_propagation(c["nodes"], c["reports"])
        literal = "CONFIRMED" if c["variant"] == "INDEPENDENT" else "INSUFFICIENT"
        graph_checks.append(roots == other and depth == c["depth"] and
                            subject.answer(c, sabotage) == c["mapping"][literal])
        body_lengths.setdefault(c["block"], set()).add(len(c["body"]))
        rename = {node: "RENAMED_" + str(i) for i, node in enumerate(reversed(c["nodes"]))}
        renamed = {rename[k]: None if p is None else rename[p] for k, p in c["nodes"].items()}
        rroots, _ = subject.roots_by_paths(renamed, [rename[r] for r in c["reports"]])
        graph_checks.append(len(set(rroots)) == len(set(roots)))
        for bad in ({**c["nodes"], "unused": "missing"}, {**c["nodes"], "unused": "unused"}):
            for oracle in (subject.roots_by_paths, subject.roots_by_propagation):
                graph_checks.append(rejects(lambda o=oracle, b=bad: o(b, c["reports"])))
    q3 = bool(graph_checks) and all(graph_checks) and all(len(v) == 1 for v in body_lengths.values())

    plan, rows = subject.manifest(), subject.fixture_rows()
    corruption = [[], rows[:-1], rows + [deepcopy(rows[0])]]
    for field, value in (("trial_id", "unknown"), ("prompt_sha256", "0" * 64),
                         ("completion", None), ("finish_reason", "UNKNOWN")):
        bad = deepcopy(rows)
        bad[0][field] = value
        corruption.append(bad)
    extra_field = deepcopy(rows)
    extra_field[0]["unexpected"] = "field"
    corruption.append(extra_field)
    archive_checks = [rejects(lambda bad=bad: subject.checked_rows(bad, plan)) for bad in corruption]
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "constructed.jsonl"
        p.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        archive_checks.append(subject.load_archive(p) == rows)
        p.write_text('{"trial_id":"one","trial_id":"two"}\n')
        archive_checks.append(rejects(lambda: subject.load_archive(p)))
        p.write_text("\n")
        archive_checks.append(rejects(lambda: subject.load_archive(p)))
    malformed = ["", "DECISION: C", "DECISION: A\nDECISION: B", "DECISION: A\nDECISION: A",
                 "DECISION: A\nmore text", "DECISION: A or B", "decision: A", "**DECISION: A**"]
    parser_checks = [subject.parse_completion(text, "stop") is None for text in malformed]
    parser_checks += [subject.parse_completion("DECISION: A", "length") is None,
                      subject.parse_completion("Explanation.\nDECISION: B", "stop") == "B"]
    benign = subject.score(rows, sabotage)
    negative_scores = {}
    for label in ("A", "B"):
        constant = [{**row, "completion": "DECISION: " + label} for row in rows]
        negative_scores[label] = subject.score(constant)["pair_correct"]
    swapped = deepcopy(rows)
    swapped[0]["completion"] = "DECISION: " + ("B" if rows[0]["completion"].endswith("A") else "A")
    truncated = deepcopy(rows)
    truncated[0]["finish_reason"] = "length"
    q4 = (all(archive_checks + parser_checks) and benign["pair_correct"] == benign["pairs"] and
          all(value == 0 for value in negative_scores.values()) and
          subject.score(swapped)["pair_correct"] == benign["pairs"] - 1 and
          subject.score(truncated)["pair_correct"] == benign["pairs"] - 1 and
          subject.score(truncated)["malformed"] == 1)
    tails = (subject.sign_tail(0, 0), subject.sign_tail(0, 4), subject.sign_tail(4, 0),
             subject.sign_tail(5, 0), subject.sign_tail(1, 1))
    q5 = (tails == (Fraction(1), Fraction(1), Fraction(1, 16), Fraction(1, 32), Fraction(3, 4)) and
          subject.sign_summary([1, 0, 0])["p"] == "1/2" and
          all(rejects(lambda x=x: subject.sign_tail(x, 0)) for x in (-1, 1.0, True)) and
          rejects(lambda: subject.contrasts([])) and rejects(lambda: subject.contrasts([[2] * 6])) and
          benign["pair_correct"] == benign["pairs"] and
          subject.score(rows, sabotage=True)["pair_correct"] == 0)
    details = {"gate_fixtures": examples, "qualification_cases": len(cases),
               "qualification_blocks": len(body_lengths), "qualification_trials": len(rows),
               "manifest_sha256": subject.digest(plan), "fixture_responses_sha256": subject.digest(rows),
               "benign_pairs_correct": benign["pair_correct"], "benign_pairs": benign["pairs"],
               "constant_label_pairs_correct": negative_scores,
               "oracle_sabotage_pairs_correct": subject.score(rows, True)["pair_correct"],
               "graph_check_count": len(graph_checks), "archive_check_count": len(archive_checks),
               "parser_check_count": len(parser_checks), "matched_graph_character_lengths": {
                   block: sorted(lengths) for block, lengths in body_lengths.items()},
               "budget_counts_not_runtime_estimates": {
                   "cst_screen_responses": 16 * 2 * 2 * 3,
                   "cst_noise_responses": 2 * 3 * 3,
                   "cst_fresh_long_format_responses": 64 * 2 * 2 * 3,
                   "cst_optional_short_format_responses": 64 * 2 * 2 * 2,
                   "redundancy_screen_trained_models": 3 * 4 * 2,
                   "context_screen_generated_programs": 16 * 2 * 2 * 2}}
    return {"Q1": bool(q1), "Q2": bool(q2), "Q3": bool(q3), "Q4": bool(q4), "Q5": bool(q5)}, details


class RegisteredChecks(unittest.TestCase):
    def test_registered_checks(self):
        outcomes, _ = run_registered_checks()
        self.assertEqual(outcomes, dict.fromkeys(("Q1", "Q2", "Q3", "Q4", "Q5"), True))

    def test_sabotage_on_live_path(self):
        outcomes, _ = run_registered_checks(sabotage=True)
        self.assertFalse(outcomes["Q3"])
        self.assertFalse(outcomes["Q4"])
        self.assertFalse(outcomes["Q5"])


if __name__ == "__main__":
    unittest.main()
