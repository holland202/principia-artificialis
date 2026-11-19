#!/usr/bin/env python3
"""Post-review audit, not a prospective experiment or model run.

Claude Opus 5.5 identified the naming and repetition shortcuts. Codex / OpenAI
GPT-6 Astra reproduced them and added a threshold counterexample. Human review:
direction only, Chad Holland. Expected audit outcomes are retrodictions.
Old public qualification/development cases only. No sealed split is instantiated.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re

import instrument

ROOT = Path(__file__).resolve().parents[2]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def qualification_shortcut(sabotage=False):
    correct = total = 0
    for case in instrument.qualification_cases():
        # Read rendered records, not the answer metadata or oracle graph.
        records = dict(re.findall(r"^([A-Z][0-9]{2}[A-Z]): uses ([A-Z][0-9]{2}[A-Z])$",
                                  case["prompt"], re.MULTILINE))
        selected = re.search(r"Selected reports: (\w+), (\w+)\.", case["prompt"]).groups()
        variable = next(node for node in selected if node.endswith("X"))
        shared = records[variable][-1] in "AB"
        if sabotage:
            shared = not shared
        guess = case["mapping"]["INSUFFICIENT" if shared else "CONFIRMED"]
        correct += guess == instrument.answer(case)
        total += 1
    return {"correct": correct, "total": total, "follows_links": False}


def old_repetition_shortcut():
    cases = load_module("public_cst_cases_review", "experiments/cst_001/cases.py")
    result = {}
    # This fixed allowlist intentionally has no test/confirmatory option.
    for split, per_cell in (("qual", 1), ("dev", 2), ("dev2", 2)):
        correct = total = 0
        for pair in cases.build(split, per_cell):
            for version in pair["versions"]:
                ids = re.findall(r"\b[A-Z]+-[0-9]{3}\b", version["prompt"])
                if len(ids) != 2:
                    raise ValueError("unexpected public observation-ID layout")
                repeated = max(Counter(ids).values()) > 1
                guess = "INSUFFICIENT" if repeated else "CONFIRMED"
                correct += guess == version["answer"]
                total += 1
        result[split] = {"correct": correct, "total": total}
    result["total"] = {k: sum(r[k] for r in result.values()) for k in ("correct", "total")}
    return result


def archive_marginals():
    scorer = load_module("public_cst_scorer_review", "experiments/cst_001/scorer.py")
    results = []
    for filename in ("dev_outputs_7b.jsonl", "dev2_hop2_7b.jsonl"):
        path = ROOT / "results/cst_001" / filename
        groups = defaultdict(dict)
        for row in map(json.loads, path.read_text().splitlines()):
            hop = int(re.search(r"-h([12])-", row["pair"]).group(1))
            key = (row["arm"], hop)
            case_key = (row["pair"], row["version"])
            if case_key in groups[key]:
                raise ValueError("duplicate archive key")
            if row["version"] not in ("SHARED", "INDEPENDENT"):
                raise ValueError("unknown truth class")
            gold = "INSUFFICIENT" if row["version"] == "SHARED" else "CONFIRMED"
            groups[key][case_key] = scorer.parse(row["output"]) == gold
        for (arm, hop), scored in sorted(groups.items()):
            if arm not in ("D", "E"):
                continue
            pairs = {pair for pair, _ in scored}
            if len(scored) != 2 * len(pairs):
                raise ValueError("incomplete pair")
            n = len(pairs)
            s = sum(scored[(p, "SHARED")] for p in pairs)
            i = sum(scored[(p, "INDEPENDENT")] for p in pairs)
            joint = sum(scored[(p, "SHARED")] and scored[(p, "INDEPENDENT")] for p in pairs)
            product = Fraction(s * i, n)
            results.append({"archive": filename, "arm": arm, "hop": hop, "pairs": n,
                            "shared_correct": s, "independent_correct": i, "pair_correct": joint,
                            "product_expected_count": str(product), "equals_product": joint == product,
                            "youden_j": str(Fraction(s + i, n) - 1),
                            "archive_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return results


def rates(positive, negative, offset):
    hit = Fraction(sum(x + offset >= 0 for x in positive), len(positive))
    false_alarm = Fraction(sum(x + offset >= 0 for x in negative), len(negative))
    concordant = sum(Fraction(1) if p > n else Fraction(1, 2) if p == n else Fraction(0)
                     for p in positive for n in negative)
    auc = concordant / (len(positive) * len(negative))
    return {"hit_rate": str(hit), "false_alarm_rate": str(false_alarm),
            "youden_j": str(hit - false_alarm), "auc": str(auc)}


def threshold_counterexample():
    data = {"shallow": ([1, 2, 3, 4], [-4, -3, -2, -1]),
            "deep": ([-3, -2, -1, 0], [-7, -6, -5, -4])}
    return {depth: {"offset_0": rates(p, n, 0), "offset_3": rates(p, n, 3)}
            for depth, (p, n) in data.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sabotage", action="store_true")
    args = parser.parse_args()
    shortcut = qualification_shortcut(args.sabotage)
    repetition = old_repetition_shortcut()
    threshold = threshold_counterexample()
    checks = {
        "reviewed_naming_failure_reproduced": shortcut == {
            "correct": 32, "total": 32, "follows_links": False},
        "reviewed_repetition_failure_reproduced": repetition == {
            "qual": {"correct": 64, "total": 64},
            "dev": {"correct": 128, "total": 128},
            "dev2": {"correct": 128, "total": 128},
            "total": {"correct": 320, "total": 320}},
        "j_crossover_with_fixed_discrimination": (
            threshold["shallow"]["offset_0"]["youden_j"] == "1" and
            threshold["shallow"]["offset_3"]["youden_j"] == "1/4" and
            threshold["deep"]["offset_0"]["youden_j"] == "1/4" and
            threshold["deep"]["offset_3"]["youden_j"] == "1" and
            all(t["auc"] == "1" for depth in threshold.values() for t in depth.values()))}
    payload = {"status": "POST-REVIEW AUDIT / RETRODICTIONS / NO MODEL INFERENCE",
               "qualification_shortcut": shortcut, "old_repetition_shortcut": repetition,
               "archive_marginals": archive_marginals(), "constructed_threshold_example": threshold,
               "checks": checks}
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("AUDIT CHECKS " + ("REPRODUCED" if all(checks.values()) else "MISMATCH"))
    print("DIGEST " + instrument.digest(payload))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
