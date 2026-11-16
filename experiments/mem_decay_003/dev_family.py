"""ONE development scenario family ("facility operations") for instrument qualification only. Evaluation families
are to be authored separately (by Codex, per issue #150) and are disjoint by template family, not just by seed.
Written by Claude (Anthropic, Opus 5.5), 2026-11-16.
REV1 (2026-11-16, after Codex's review on PR #159): ids are opaque and assigned after shuffling, so no id carries the
record's kind (A4: the draft always gave the correction id m001); the conjunctive pair no longer has one premise
restated by the question; every task carries evidence rules for licensed_answer()."""
import random

ROOMS = ["Room A", "Room B", "Room C", "Room D", "Room E", "Room F"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def scenario(seed, n_filler=12):
    rng = random.Random(seed)
    old, new = rng.sample(ROOMS, 2)
    d1, d2 = rng.sample(DAYS, 2)
    recs, tasks = [], []

    def add(kind, text, age, uses):
        rid = f"tmp{len(recs)}"
        recs.append({"id": rid, "text": text, "age": age, "uses": uses, "kind": kind})
        return rid

    # superseded value plus a short correction; the original is long and salient
    o = add("original", f"The quarterly safety review is scheduled in {old}. Attendance is required for all "
                        f"shift leads, and the review must start on time at 9 a.m.", rng.randint(30, 60), rng.randint(3, 6))
    c = add("correction", f"Update: review moved to {new}.", rng.randint(1, 10), 0)
    tasks.append({"q": "Which room is the quarterly safety review in?", "answer": new, "stale": old,
                  "needs": [c], "type": "correction", "evidence": [[[c], new], [[o], old]]})
    # a singleton critical constraint
    k = add("critical", f"Loading dock gate must never be left open after 6 p.m.; the limit is strict.",
            rng.randint(40, 90), 1)
    tasks.append({"q": "Until what time may the loading dock gate be left open?", "answer": "6 p.m.", "stale": None,
                  "needs": [k], "type": "singleton",
                  "evidence": [[[k], "6 p.m."]]})
    # a conjunctive pair: neither record alone determines the answer, and the question restates neither
    p1 = add("conjunct", "The forklift inspection is held on the same day as the fire drill.", rng.randint(20, 50), 0)
    p2 = add("conjunct", f"The fire drill is on {d1}.", rng.randint(20, 50), 0)
    tasks.append({"q": "On which day is the forklift inspection held?", "answer": d1,
                  "stale": None, "needs": [p1, p2], "type": "conjunctive", "evidence": [[[p1, p2], d1]]})
    # redundant copies of one fact
    for _ in range(3):
        add("redundant", f"Coffee supplies are restocked every {d2}.", rng.randint(5, 30), rng.randint(0, 2))
    tasks.append({"q": "On which day are coffee supplies restocked?", "answer": d2, "stale": None,
                  "needs_any": [r["id"] for r in recs if r["kind"] == "redundant"], "needs": [], "type": "redundant",
                  "evidence": [[[r["id"]], d2] for r in recs if r["kind"] == "redundant"]})
    for i in range(n_filler):
        add("filler", f"Note {i}: the {rng.choice(['printer', 'kettle', 'radio', 'fan'])} in "
                      f"{rng.choice(ROOMS)} was checked.", rng.randint(1, 90), rng.randint(0, 4))
    rng.shuffle(recs)
    # opaque ids, drawn after the shuffle so neither id nor list position encodes the kind
    new_ids = {}
    while len(new_ids) < len(recs):
        cand = f"r{rng.getrandbits(24):06x}"
        if cand not in new_ids.values():
            new_ids[recs[len(new_ids)]["id"]] = cand
    for r in recs:
        r["id"] = new_ids[r["id"]]
    for t in tasks:
        t["needs"] = [new_ids[i] for i in t["needs"]]
        if "needs_any" in t:
            t["needs_any"] = [new_ids[i] for i in t["needs_any"]]
        t["evidence"] = [[[new_ids[i] for i in ids], v] for ids, v in t["evidence"]]
    return {"scenario_id": f"dev-fac-{seed}", "family": "facility_ops_dev", "records": recs, "tasks": tasks}
