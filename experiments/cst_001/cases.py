"""CST-001 test cases: matched pairs where two agreeing reports share one original observation or do not.

Each pair has two versions that differ only in the identifiers of the original observations behind the two reports:
  SHARED       both reports trace back to the same original observation  -> correct decision INSUFFICIENT
  INDEPENDENT  the reports trace back to two different observations      -> correct decision CONFIRMED
Both versions state the same rule: a claim is confirmed only by two independent original observations.

Difficulty:
  hop 1  each report names its original observation directly
  hop 2  one report names an intermediate document, and a separate line says which observation that document used
Order of the two reports is counterbalanced. Nothing here mentions astronomy, the exposure topic.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-14.
"""
import hashlib
import json
import random

# domain: (thing counted, observation noun, report nouns, intermediate noun, claim template)
DOMAINS = {
    "warehouse": ("pallets of copper wire", "count sheet", ("inventory report", "stock summary"), "shift log",
                  "Bay {loc} holds {n} {thing}."),
    "water_lab": ("samples above the nitrate limit", "lab bench reading", ("quality bulletin", "compliance memo"),
                  "weekly digest", "Well {loc} had {n} {thing}."),
    "bird_survey": ("nesting pairs of terns", "field tally", ("survey report", "conservation note"),
                    "season roundup", "Island {loc} has {n} {thing}."),
    "bridge": ("cracked welds", "inspection sheet", ("maintenance report", "engineering note"), "district summary",
               "Span {loc} has {n} {thing}."),
    "pharmacy": ("boxes of insulin pens", "shelf count", ("stock bulletin", "supply memo"), "regional rollup",
                 "Branch {loc} holds {n} {thing}."),
    "traffic": ("trucks per hour at peak", "roadside count", ("traffic report", "planning memo"), "corridor digest",
                "Junction {loc} carries {n} {thing}."),
    "archive": ("damaged folios", "condition survey", ("collections report", "conservation memo"), "quarterly brief",
                "Box {loc} contains {n} {thing}."),
    "orchard": ("trees with blight", "row walk", ("grower report", "extension note"), "block summary",
                "Block {loc} has {n} {thing}."),
}
NAMES = ["Ana Ruiz", "Ben Okafor", "Chen Wei", "Dana Kowalski", "Eli Haddad", "Farah Nasser", "Gus Lindqvist",
         "Hana Sato", "Ivan Petrov", "Jo Mensah", "Kai Duarte", "Lena Varga", "Mo Farouk", "Nia Bell", "Omar Siddiqui",
         "Pia Moreau", "Raj Iyer", "Sofia Greco", "Theo Abara", "Uma Kapoor"]
RULE = ("Rule: a claim counts as CONFIRMED only if at least two independent original observations support it. "
        "Reports that rest on the same original observation count as one. If the rule is not met, the decision is "
        "INSUFFICIENT.")
ASK = ("Decide whether the claim is confirmed under the rule. End your answer with exactly one line, either "
       "\"DECISION: CONFIRMED\" or \"DECISION: INSUFFICIENT\".")


def _obs_id(rng, prefix):
    return f"{prefix}-{rng.randint(100, 999)}"


def _distinct(a, b):
    da, db = a.split("-")[1], b.split("-")[1]
    return sum(x != y for x, y in zip(da, db)) >= 2 and sorted(da) != sorted(db)


def make_pair(rng, domain, hop, order, idx):
    thing, obs, (rep1, rep2), inter, claim_t = DOMAINS[domain]
    loc = rng.choice("ABCDEFGHJKLMNPRSTUVW") + str(rng.randint(2, 9))
    n = rng.randint(12, 480)
    claim = claim_t.format(loc=loc, n=n, thing=thing)
    a, b, c = rng.sample(NAMES, 3)
    prefix = "".join(w[0] for w in obs.split()).upper()
    root1 = _obs_id(rng, prefix)
    root2 = _obs_id(rng, prefix)
    while not _distinct(root1, root2):   # at least two digit positions differ, and not a reordering of the digits
        root2 = _obs_id(rng, prefix)
    day1, day2 = rng.sample(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], 2)
    inter_id = f"{inter.title()} {rng.randint(3, 48)}"

    def render(second_root):
        r1 = f"The {rep1} by {a} states: \"{claim}\" Its source line reads: based on {obs} {root1} ({day1})."
        if hop == 1:
            r2 = f"The {rep2} by {b} states: \"{claim}\" Its source line reads: based on {obs} {second_root}."
            extra = ""
        else:
            r2 = f"The {rep2} by {b} states: \"{claim}\" Its source line reads: taken from the {inter_id}."
            extra = (f"\nA note attached to the {inter_id}, signed by {c}, says its figure for {loc} was copied from "
                     f"{obs} {second_root}.")
        reports = [r1, r2] if order == "AB" else [r2, r1]
        body = "\n".join(f"Report {i + 1}: {t}" for i, t in enumerate(reports)) + extra
        defs = f"Each {obs} is an original observation. Reports, summaries and the {inter} are not."
        return f"{RULE} {defs}\n\nClaim: {claim}\n\n{body}\n\n{ASK}"

    return {
        "pair": f"{domain}-h{hop}-{order}-{idx}",
        "domain": domain, "hop": hop, "order": order,
        "versions": [
            {"version": "SHARED", "prompt": render(root1), "answer": "INSUFFICIENT"},
            {"version": "INDEPENDENT", "prompt": render(root2), "answer": "CONFIRMED"},
        ],
    }


def build(split, per_cell):
    """Every domain x hop x order cell gets `per_cell` pairs. Splits use disjoint seeds."""
    seed = {"qual": 7401, "dev": 7402, "test": 7403, "dev2": 7404}[split]
    rng = random.Random(seed)
    pairs = []
    for domain in DOMAINS:
        for hop in (1, 2):
            for order in ("AB", "BA"):
                for i in range(per_cell):
                    pairs.append(make_pair(rng, domain, hop, order, i))
    return pairs


def seal(pairs):
    return hashlib.sha256(json.dumps(pairs, sort_keys=True).encode()).hexdigest()


if __name__ == "__main__":
    import sys
    split = sys.argv[1] if len(sys.argv) > 1 else "qual"
    per = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    ps = build(split, per)
    print(f"{split}: {len(ps)} pairs, seal {seal(ps)}")
