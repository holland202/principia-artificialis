#!/usr/bin/env python3
"""CST-MECH-QUAL-001. Public qualification fixtures, never model-study evidence.

Author: Codex / OpenAI GPT-6 Astra, 2026-11-15, Chad Holland's direction.
Human review: direction only. Both graph algorithms are self-tested, not independent.
No inference backend or confirmatory split exists in this module.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from math import comb
from pathlib import Path
import re


NAMESPACE = "CST-MECH-QUAL-001"
ARMS = ("N", "T", "G")
VARIANTS = ("SHARED", "INDEPENDENT")
PREFIX = {
    "N": "Read the records below and return the requested decision.",
    "T": "Trace each selected report through any intermediate records to its original observation. Count distinct original observations, not reports.",
    "G": "Check the information carefully before deciding. Review the relevant details and make sure the answer follows the stated rule.",
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def text_digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def sign_tail(positive, negative):
    """Exact upper binomial tail conditional on nonzero signs. Ties omitted."""
    if any(type(x) is not int or x < 0 for x in (positive, negative)):
        raise ValueError("sign counts must be nonnegative integers")
    n = positive + negative
    return Fraction(sum(comb(n, k) for k in range(positive, n + 1)), 2 ** n)


def sign_summary(values):
    values = list(values)
    if not values or any(type(x) is not int or x not in (-2, -1, 0, 1, 2) for x in values):
        raise ValueError("nonempty integer differences required")
    positive = sum(x > 0 for x in values)
    negative = sum(x < 0 for x in values)
    return {"mean": str(Fraction(sum(values), len(values))), "positive": positive,
            "negative": negative, "ties": len(values) - positive - negative,
            "p": str(sign_tail(positive, negative))}


def contrasts(blocks):
    """Rows: N1,T1,N2,T2,G1,G2, all binary paired correctness.

    These are candidate gates for review, not a frozen scientific protocol.
    Sign-tail guarantees require independent sampling units and their sign nulls.
    """
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("nonempty block list required")
    if any(not isinstance(b, (tuple, list)) or len(b) != 6 or
           any(type(x) is not int or x not in (0, 1) for x in b) for b in blocks):
        raise ValueError("six binary integer scores required per block")
    shallow = [t1 - n1 for n1, t1, n2, t2, g1, g2 in blocks]
    deep = [t2 - n2 for n1, t1, n2, t2, g1, g2 in blocks]
    interaction = [b - a for a, b in zip(shallow, deep)]
    specificity = [(t2 - g2) - (t1 - g1) for n1, t1, n2, t2, g1, g2 in blocks]
    s, d, q, g = map(sign_summary, (shallow, deep, interaction, specificity))
    harm_p = sign_tail(s["negative"], s["positive"])
    benefit_p = Fraction(d["p"])
    directional = (Fraction(s["mean"]) <= -Fraction(1, 8) and
                   Fraction(d["mean"]) >= Fraction(1, 8) and
                   max(harm_p, benefit_p) <= Fraction(1, 20))
    return {"blocks": len(blocks), "shallow": s, "deep": d, "interaction": q,
            "pr152_gate": Fraction(q["mean"]) >= Fraction(1, 4) and Fraction(q["p"]) <= Fraction(1, 20),
            "directional_gate": directional, "directional_iut_p": str(max(harm_p, benefit_p)),
            "generic_contrast": g,
            "specificity_gate": directional and Fraction(g["mean"]) >= Fraction(1, 4) and
            Fraction(g["p"]) <= Fraction(1, 20)}


def roots_by_paths(nodes, reports):
    """Follow every node, so unused cyclic or dangling records also fail closed."""
    if not isinstance(nodes, dict) or not nodes or not isinstance(reports, list) or len(reports) != 2:
        raise ValueError("graph and two selected reports required")
    if len(set(reports)) != 2 or any(r not in nodes or nodes[r] is None for r in reports):
        raise ValueError("selected reports must be distinct nonterminal nodes")
    for node, parent in nodes.items():
        if not isinstance(node, str) or not node or (parent is not None and parent not in nodes):
            raise ValueError("invalid node or dangling edge")
    resolved = {}
    for start in nodes:
        seen, cur, depth = set(), start, 0
        while nodes[cur] is not None:
            if cur in seen:
                raise ValueError("cycle")
            seen.add(cur)
            cur = nodes[cur]
            depth += 1
        resolved[start] = (cur, depth)
    return [resolved[r][0] for r in reports], max(resolved[r][1] for r in reports)


def roots_by_propagation(nodes, reports):
    """Alternative algorithm, same author. Not an independent verifier."""
    if not isinstance(nodes, dict) or not nodes or len(reports) != 2 or len(set(reports)) != 2:
        raise ValueError("invalid graph")
    if any(r not in nodes or nodes[r] is None for r in reports):
        raise ValueError("invalid selected reports")
    labels = {key: key for key, parent in nodes.items() if parent is None}
    pending = set(nodes) - set(labels)
    while pending:
        ready = {key for key in pending if nodes[key] in labels}
        if not ready:
            raise ValueError("cycle or dangling edge")
        for key in ready:
            labels[key] = labels[nodes[key]]
        pending -= ready
    return [labels[r] for r in reports]


def qualification_cases():
    """Fixed public matrix only. No random seed or holdout parameter."""
    cases = []
    for i in range(8):
        ids = [f"{kind}{i:02d}{suffix}" for kind, suffix in
               (("O", "A"), ("O", "Z"), ("L", "B"), ("L", "Y"), ("R", "C"), ("R", "X"))]
        a, b, left, right, r1, r2 = ids
        reports = [r1, r2] if i % 2 == 0 else [r2, r1]
        mapping = {"CONFIRMED": "A", "INSUFFICIENT": "B"} if (i // 2) % 2 == 0 else {
            "CONFIRMED": "B", "INSUFFICIENT": "A"}
        for depth in (1, 2):
            for variant in VARIANTS:
                target = a if variant == "SHARED" else b
                nodes = {a: None, b: None, left: a, right: b, r1: a,
                         r2: target if depth == 1 else (left if variant == "SHARED" else right)}
                body = "\n".join(f"{key}: " + ("original observation" if parent is None else f"uses {parent}")
                                 for key, parent in nodes.items())
                prompt = (f"Qualification case {NAMESPACE}-{i:02d}.\n"
                          "Only the two selected final reports are eligible evidence. Both report the same claim. "
                          "Follow their 'uses' links to original observations. Other records contribute only when reachable. "
                          "The claim is CONFIRMED exactly when the selected reports reach two distinct original observations, "
                          "otherwise it is INSUFFICIENT.\n" + body +
                          f"\nSelected reports: {reports[0]}, {reports[1]}.\n"
                          f"Use {mapping['CONFIRMED']} for CONFIRMED and {mapping['INSUFFICIENT']} for INSUFFICIENT. "
                          "A rationale is permitted. End with exactly one line: DECISION: A or DECISION: B.")
                cases.append({"case_id": f"Q{i:02d}-h{depth}-{variant}", "block": f"Q{i:02d}",
                              "depth": depth, "variant": variant, "nodes": nodes, "reports": reports,
                              "mapping": mapping, "body": body, "prompt": prompt})
    return cases


def answer(case, sabotage=False):
    roots, depth = roots_by_paths(case["nodes"], case["reports"])
    if depth != case["depth"]:
        raise ValueError("depth metadata disagrees with graph")
    confirmed = len(set(roots)) == 2
    if sabotage:
        confirmed = not confirmed
    return case["mapping"]["CONFIRMED" if confirmed else "INSUFFICIENT"]


def manifest():
    trials = []
    for case in qualification_cases():
        for arm in ARMS:
            prompt = PREFIX[arm] + "\n\n" + case["prompt"]
            trials.append({"trial_id": case["case_id"] + "-" + arm, "case_id": case["case_id"],
                           "arm": arm, "prompt": prompt, "prompt_sha256": text_digest(prompt)})
    return {"schema": NAMESPACE, "split": "public_qualification", "trials": trials}


def parse_completion(text, finish_reason):
    if not isinstance(text, str) or finish_reason != "stop":
        return None
    lines = text.strip().splitlines()
    candidates = [line for line in lines if "DECISION" in line.upper()]
    if len(candidates) != 1 or not lines:
        return None
    match = re.fullmatch(r"DECISION: ([AB])", lines[-1])
    return match.group(1) if match and candidates[0] == lines[-1] else None


def checked_rows(rows, expected):
    if not isinstance(rows, list) or not rows:
        raise ValueError("empty archive")
    known = {r["trial_id"]: r for r in expected["trials"]}
    if not known or len(known) != len(expected["trials"]):
        raise ValueError("invalid manifest")
    got = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"trial_id", "prompt_sha256", "completion", "finish_reason"}:
            raise ValueError("invalid response schema")
        if any(not isinstance(row[k], str) for k in row):
            raise ValueError("response fields must be strings")
        key = row["trial_id"]
        if key not in known or key in got:
            raise ValueError("duplicate or unexpected trial")
        if row["prompt_sha256"] != known[key]["prompt_sha256"]:
            raise ValueError("wrong prompt hash")
        if row["finish_reason"] not in ("stop", "length", "error"):
            raise ValueError("unknown finish reason")
        got[key] = row
    if set(got) != set(known):
        raise ValueError("missing trials")
    return got


def unique_object(items):
    obj = {}
    for key, value in items:
        if key in obj:
            raise ValueError("duplicate JSON field")
        obj[key] = value
    return obj


def load_archive(path):
    rows = []
    with Path(path).open() as stream:
        for line in stream:
            if not line.strip():
                raise ValueError("blank archive row")
            rows.append(json.loads(line, object_pairs_hook=unique_object))
    checked_rows(rows, manifest())
    return rows


def score(rows, sabotage=False):
    plan = manifest()
    responses = checked_rows(rows, plan)
    cases = {c["case_id"]: c for c in qualification_cases()}
    grouped, malformed = {}, 0
    by_truth = {variant: [0, 0] for variant in VARIANTS}
    for trial in plan["trials"]:
        c, row = cases[trial["case_id"]], responses[trial["trial_id"]]
        decision = parse_completion(row["completion"], row["finish_reason"])
        malformed += decision is None
        ok = decision == answer(c, sabotage=sabotage)
        by_truth[c["variant"]][0] += ok
        by_truth[c["variant"]][1] += 1
        key = (c["block"], c["depth"], trial["arm"])
        grouped.setdefault(key, []).append(ok)
    if any(len(values) != 2 for values in grouped.values()):
        raise ValueError("incomplete pair")
    paired = {key: int(all(values)) for key, values in grouped.items()}
    table = [[paired[(block, depth, arm)] for depth, arm in
              ((1, "N"), (1, "T"), (2, "N"), (2, "T"), (1, "G"), (2, "G"))]
             for block in sorted({c["block"] for c in cases.values()})]
    return {"rows": len(responses), "malformed": malformed, "truth_accuracy": by_truth,
            "pair_correct": sum(paired.values()), "pairs": len(paired), "contrasts": contrasts(table)}


def fixture_rows():
    """Constructed from the fixture truth axis, deliberately not answer()."""
    cases = {c["case_id"]: c for c in qualification_cases()}
    rows = []
    for trial in manifest()["trials"]:
        c = cases[trial["case_id"]]
        gold = c["mapping"]["CONFIRMED" if c["variant"] == "INDEPENDENT" else "INSUFFICIENT"]
        rows.append({"trial_id": trial["trial_id"], "prompt_sha256": trial["prompt_sha256"],
                     "completion": "DECISION: " + gold, "finish_reason": "stop"})
    return rows


def gates():
    examples = {
        "both_benefit": [(0, 1, 0, 1, 0, 0)] * 16 + [(0, 0, 0, 1, 0, 0)] * 48,
        "deep_only": [(0, 0, 0, 1, 0, 0)] * 64,
        "no_effect": [(0, 0, 0, 0, 0, 0)] * 64,
        "crossover": [(1, 0, 0, 1, 1, 0)] * 64,
        "reverse": [(0, 1, 1, 0, 0, 1)] * 64,
        "generic_matches": [(1, 0, 0, 1, 0, 1)] * 64,
    }
    return {name: contrasts(rows) for name, rows in examples.items()}


def qualification(sabotage=False):
    from test_instrument import run_registered_checks
    outcomes, details = run_registered_checks(sabotage=sabotage)
    payload = {"scope": "CONSTRUCTED QUALIFICATION ONLY", "predictions": outcomes, "details": details}
    sha = digest(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    print(f"VERDICT {sum(outcomes.values())} of {len(outcomes)} as registered")
    print("DIGEST " + sha)
    # W4 pin is mandatory. A missing pin fails closed with a nonzero import error.
    from recorded import RECORDED
    if (outcomes, sha) != RECORDED:
        return 1
    return 0 if all(outcomes.values()) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("qualify", "manifest", "score"))
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--sabotage", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "qualify":
            return qualification(args.sabotage)
        if args.command == "manifest":
            print(json.dumps(manifest(), indent=2, sort_keys=True))
            return 0
        if args.archive is None:
            raise ValueError("--archive is required")
        print(json.dumps(score(load_archive(args.archive), args.sabotage), indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("UNVERIFIED: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
