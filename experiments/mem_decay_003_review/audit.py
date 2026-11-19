#!/usr/bin/env python3
"""Public post-inspection audit; no models and no evaluation dataset.

Codex / OpenAI GPT-6 Astra reviewing Claude Opus 5.5. Self-tested audit;
human validation: direction only; editing pending; Chad Holland responsible.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M = load("memdecay3_review_target", "experiments/mem_decay_003/memdecay3.py")
D = load("memdecay3_review_public_dev", "experiments/mem_decay_003/dev_family.py")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def fixed_id_rule(scenario):
    # Predictions read only the real view, never the kind/task key.
    return [r["id"] for r in M.selector_view(scenario) if r["id"] == "m001"]


def id_probe():
    totals = {"scenarios": 0, "correction_selected": 0,
              "hidden_scramble_invariant": 0, "correction_selected_after_id_rotation": 0}
    for seed in range(40):
        sc = D.scenario(seed)
        chosen = fixed_id_rule(sc)
        correct_ids = {r["id"] for r in sc["records"] if r["kind"] == "correction"}
        totals["scenarios"] += 1
        totals["correction_selected"] += set(chosen) == correct_ids
        hidden = copy.deepcopy(sc)
        for row in hidden["records"]:
            row["kind"] = "filler"
        hidden["tasks"] = []
        totals["hidden_scramble_invariant"] += fixed_id_rule(hidden) == chosen
        renamed = copy.deepcopy(sc)
        ids = sorted(r["id"] for r in sc["records"])
        mapping = dict(zip(ids, ids[1:] + ids[:1]))
        for row in renamed["records"]:
            row["id"] = mapping[row["id"]]
        for task in renamed["tasks"]:
            for field in ("needs", "needs_any"):
                if field in task:
                    task[field] = [mapping[rid] for rid in task[field]]
        renamed_gold = {mapping[rid] for rid in correct_ids}
        totals["correction_selected_after_id_rotation"] += set(fixed_id_rule(renamed)) == renamed_gold
    return totals


def projected_input(scenario, kept, question):
    """Constructed encoder, NOT the unimplemented production model prompt builder."""
    records = [r for r in M.selector_view(scenario) if r["id"] in kept]
    return {"instruction": "Answer from retained records; use UNKNOWN if they do not settle the question.",
            "records": sorted(records, key=lambda r: r["id"]), "question": question}


def visible_lookup(projection):
    """Named non-AI rival on this public worked example, not a general QA system."""
    text = "\n".join(r["text"] for r in projection["records"])
    for pattern in (r"review moved to (Room [A-F])", r"review is scheduled in (Room [A-F])"):
        match = re.search(pattern, text)
        if match:
            return "ANSWER: " + match.group(1)
    return "ANSWER: UNKNOWN"


def observability_probe(sc):
    task = next(t for t in sc["tasks"] if t["type"] == "correction")
    original = next(r["id"] for r in sc["records"] if r["kind"] == "original")
    correction = task["needs"][0]
    unchanged = copy.deepcopy(sc)
    unchanged["records"] = [r for r in unchanged["records"] if r["id"] != correction]
    unchanged_key = {"answer": task["stale"], "stale": None}
    retained = projected_input(sc, [original], task["q"])
    never_corrected = projected_input(unchanged, [original], task["q"])
    conditions = {"both": [original, correction], "original_only": [original],
                  "correction_only": [correction], "neither": []}
    rival = {}
    for label, kept in conditions.items():
        output = visible_lookup(projected_input(sc, kept, task["q"]))
        rival[label] = {"output": output, "classification": M.classify(task, output)}
    return {"encoder": "constructed projection; production prompt builder absent",
            "same_visible_input": retained == never_corrected,
            "different_world_keys": task["answer"] != unchanged_key["answer"],
            "retained_input_sha256": digest(retained),
            "never_corrected_input_sha256": digest(never_corrected),
            "restored_correction_changes_input": retained != projected_input(sc, [original, correction], task["q"]),
            "public_retained_input": retained,
            "original_answer_world_classes": [M.classify(unchanged_key, rival["original_only"]["output"]),
                                               rival["original_only"]["classification"]],
            "non_ai_visible_lookup": rival}


def run(sabotage=False):
    sc = D.scenario(0)
    singleton = next(t for t in sc["tasks"] if t["type"] == "singleton")
    redundant = next(t for t in sc["tasks"] if t["type"] == "redundant")
    conjunct = next(t for t in sc["tasks"] if t["type"] == "conjunctive")
    classify = M.classify
    if sabotage:
        original_classify = classify
        def classify(task, text):
            if text == "ANSWER: " + task["answer"]:
                return "CORRECT"
            return original_classify(task, text)
    punctuated = {"gold": singleton["answer"], "raw": "ANSWER: " + singleton["answer"]}
    punctuated["classification"] = classify(singleton, punctuated["raw"])
    redundancy = {"kept_none": M.retained_requirements(redundant, []),
                  "kept_one": M.retained_requirements(redundant, redundant["needs_any"][:1]),
                  "missing_conjunct": M.retained_requirements(conjunct, conjunct["needs"][:1])}
    t = {"answer": "Room C", "stale": "Room A"}
    parser = {"plain_correct": classify(t, "ANSWER: Room C"),
              "conflicting_final_correct": classify(t, "ANSWER: Room A\nANSWER: Room C"),
              "conflicting_final_stale": classify(t, "ANSWER: Room C\nANSWER: Room A"),
              "missing_prefix": classify(t, "Room C")}
    identifiers = id_probe()
    observability = observability_probe(sc)
    checks = {
        "A1_punctuated_gold_rejected": punctuated["classification"] == "WRONG" and parser["plain_correct"] == "CORRECT",
        "A2_absent_redundant_evidence_accepted": redundancy == {"kept_none": True, "kept_one": True, "missing_conjunct": False},
        "A3_last_answer_contract": parser["conflicting_final_correct"] == "CORRECT" and parser["conflicting_final_stale"] == "STALE" and parser["missing_prefix"] == "MALFORMED",
        "A4_public_id_shortcut": identifiers == {"scenarios": 40, "correction_selected": 40, "hidden_scramble_invariant": 40, "correction_selected_after_id_rotation": 0},
        "A5_hidden_world_collision": observability["same_visible_input"] and observability["different_world_keys"] and observability["restored_correction_changes_input"] and observability["original_answer_world_classes"] == ["CORRECT", "STALE"],
    }
    payload = {"status": "EXPLORATORY PUBLIC AUDIT / NO MODEL INFERENCE / NO EVAL DATASET",
               "punctuated_answer": punctuated, "redundant_evidence": redundancy,
               "parser_contract": parser, "id_shortcut": identifiers,
               "observability": observability, "checks": checks}
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("AUDIT OBSERVATIONS " + ("REPRODUCED" if all(checks.values()) else "MISMATCH"))
    print("DIGEST " + digest(payload))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sabotage", action="store_true")
    raise SystemExit(run(parser.parse_args().sabotage))
