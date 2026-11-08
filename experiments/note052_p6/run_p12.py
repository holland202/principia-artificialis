#!/usr/bin/env python3
"""note052 P12 driver (Amendment 6). Committed with the registration, before the sample was drawn.

A second reviewer re-checks a random 30 of P10's 137 hand-checked findings, using P10's rules. This measures
agreement with Claude's verdicts (Cohen's kappa).

  python experiments/note052_p6/run_p12.py draw  OUT            sample + packet for the second reviewer (no verdicts)
  python experiments/note052_p6/run_p12.py score OUT RATINGS    agreement, kappa, disagreements; P12a/P12b verdicts

RATINGS is the reviewer's JSON: {"reviewer": "...", "declaration": {...}, "ratings": [{"id": "R01",
"verdict": "TP" or "FP", "reason": "..."}, ...]}. Standard library only.
"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P10 = os.path.join(HERE, "results_p10")
SEED = 1212
N = 30
AGREE_MIN = 27     # P12a: at least 27 of 30
KAPPA_MIN = 0.6    # P12b

RULES = """A finding is TP only if both hold:
1. the file is meant to be run as a check or test by its authors (its name, docstring, or how the project invokes
   it says so); and
2. reading the file and anything it imports from the same repository, no input makes the check report failure
   through a nonzero exit, a raised exception, or a pytest/unittest failure.

It is FP if the file is not a check (a library module, demo, benchmark, build or docs script), or if a fail path
exists that the linter does not see (for example unittest.main(), a fixture or helper that raises, or
sys.exit(main())). Each verdict carries a one-line reason.

How rule 2 was applied in P10 (results_p10/HANDCHECK_CLARIFICATION.md, committed before P10's strata were read):
- An exception counts as a fail path only if it is how the check reports that the thing it checks is wrong. An
  unrelated error (missing dependency, empty input, division by zero on no data) does not count.
- So an import-only test file counts as able to fail (the import is the check), while a script that compares
  results and only prints "failed" counts as unable to fail.
- UNPARSEABLE findings (files that do not parse under Python 3) are FP: no vacuity can be established from a file
  the tool cannot read."""


def draw(out):
    bk = json.load(open(f"{P10}/blind_key.json"))
    pins = {r["repo"]: r["pin"] for r in json.load(open(f"{P10}/fetch_log.json")) if r.get("eligible")}
    ids = sorted(bk["key"])
    rng = random.Random(SEED)
    chosen = rng.sample(ids, N)
    rng.shuffle(chosen)
    items, key = [], {}
    for i, g in enumerate(chosen, 1):
        k, rid = bk["key"][g], f"R{i:02d}"
        key[rid] = g
        items.append({"id": rid, "linter_category": k["category"], "repository": k["repo"], "path": k["path"],
                      "commit": pins[k["repo"]],
                      "url": f"https://github.com/{k['repo']}/blob/{pins[k['repo']]}/{k['path']}"})
    os.makedirs(out, exist_ok=True)
    json.dump({"seed": SEED, "n": N, "items": items}, open(f"{out}/packet.json", "w"), indent=1)
    json.dump(key, open(f"{out}/key.json", "w"), indent=1, sort_keys=True)
    lines = ["# P12 second-reviewer packet (note052 Amendment 6)", "",
             f"{N} findings drawn with seed {SEED} from the 137 that P10 hand-checked. The packet contains no "
             "verdicts.", "", "## Rules (P10's, unchanged)", "", "```", RULES, "```", "",
             "## Findings", "", "| id | linter category | file at the pinned commit |", "|---|---|---|"]
    lines += [f"| {x['id']} | {x['linter_category']} | [{x['repository']}/{x['path']}]({x['url']}) |" for x in items]
    open(f"{out}/PACKET.md", "w").write("\n".join(lines) + "\n")
    print(f"drew {N} of {len(ids)} with seed {SEED}: {', '.join(f'{r}={g}' for r, g in sorted(key.items()))}")


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pa, pb = sum(a == "TP" for a, _ in pairs) / n, sum(b == "TP" for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def score(out, ratings_path):
    key = json.load(open(f"{out}/key.json"))
    mine = {s["id"]: s for s in json.load(open(f"{P10}/handcheck.json"))}
    r = json.load(open(ratings_path))
    theirs = {x["id"]: x for x in r["ratings"]}
    if set(theirs) != set(key) or any(x["verdict"] not in ("TP", "FP") for x in theirs.values()):
        sys.exit("ratings must give TP or FP for exactly R01-R30")
    pairs = [(mine[key[i]]["verdict"], theirs[i]["verdict"]) for i in sorted(key)]
    agree = sum(a == b for a, b in pairs)
    k = kappa(pairs)
    table = {f"claude_{a}_reviewer_{b}": sum(p == (a, b) for p in pairs) for a in ("TP", "FP") for b in ("TP", "FP")}
    both_labels = len({a for a, _ in pairs}) == 2 and len({b for _, b in pairs}) == 2
    v = {"P12a": "HELD" if agree >= AGREE_MIN else "REFUTED",
         "P12b": ("UNDETERMINED (a reviewer used one label only)" if not both_labels else
                  "HELD" if k >= KAPPA_MIN else "REFUTED")}
    dis = [{"id": i, "g": key[i], "claude": mine[key[i]]["verdict"], "claude_reason": mine[key[i]]["reason"],
            "reviewer": theirs[i]["verdict"], "reviewer_reason": theirs[i].get("reason")}
           for i in sorted(key) if mine[key[i]]["verdict"] != theirs[i]["verdict"]]
    o = {"verdicts": v, "agreement": f"{agree}/{len(pairs)}", "kappa": k, "table": table, "disagreements": dis,
         "reviewer": r.get("reviewer"), "declaration": r.get("declaration")}
    json.dump(o, open(f"{out}/score.json", "w"), indent=1, sort_keys=True)
    print(json.dumps(o, indent=1, sort_keys=True))


if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    if cmd == "draw":
        draw(out)
    elif cmd == "score":
        score(out, sys.argv[3])
    else:
        sys.exit(__doc__)
