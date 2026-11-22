"""CCC-001 relay extractor checks X1-X3. Registration: RELAY_CHECKPOINTS_PREREG.md (98798ba), frozen at 7d80c0e.

Usage:
  python3 experiments/ccc_001/relay_extract_check.py [--sabotage] [--export results/ccc_001/relay_thread_2026-11-22.json]

Prints one HELD/REFUTED line per registered prediction X1-X3, `VERDICT n of 3 as registered` and a `DIGEST`.
`SUPP` lines are fixtures asked for in relay turn 012 or added by Claude after registration; never gated.
`--sabotage` turns off every fail-closed check in the extractor, so X2 must be REFUTED and the exit must be 1.
No model, tokenizer or network is used. Exit 0 only on the outcome pinned in RECORDED after the run.
"""
import argparse
import copy
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import relay_extract as rx  # noqa: E402

RECORDED = ((True, True, True), "3662f8ca4d4b6e85e2861d1f5a4a0db38086f197ff43a8a2ecf56fcd39b4978e")  # pinned after the run at d35a40a
DEFAULT_EXPORT = os.path.join(os.path.dirname(__file__), "..", "..", "results", "ccc_001",
                              "relay_thread_2026-11-22.json")


def run(comments, k, checks, snapshot=None):
    """Exit code the CLI would give: 0 written, 2 MISSING, 3 defect."""
    try:
        p = rx.extract(comments, k, snapshot, checks=checks)
    except rx.Missing:
        return 2, None
    except rx.Defect as e:
        return 3, str(e)
    return 0, p


def turn(cs, n):
    return next(c for c in cs if c["body"].split("\n")[1:2] == [f"note: ccc-relay/{'claude' if n % 2 else 'chatgpt'}/{n:03d}"])


def synthetic(k):
    """k well-formed turns with distinct bodies, for the shuffle checks at checkpoints not yet reached."""
    cs = []
    for n in range(1, k + 1):
        who = "claude" if n % 2 else "chatgpt"
        body = f"```yaml\nnote: ccc-relay/{who}/{n:03d}\nby: x; session: s; human review: none\nre: \"r\"\n```\n\nsynthetic turn {n}"
        t = f"2026-01-01T00:{n // 60:02d}:{n % 60:02d}Z"
        cs.append({"id": 1000 + n, "body": body, "created_at": t, "updated_at": t, "user": {"login": rx.RELAY_ACCOUNT}})
    return cs


def shuffled_ok(p, k):
    perm = rx.shuffle_perm(k)
    by = {t["nnn"]: t for t in p["turns"]}
    new = [by[n] for n in perm]
    same_multiset = sorted(t["rendered"] for t in new) == sorted(t["rendered"] for t in p["turns"])
    alternates = all(t["speaker"] == ("claude" if i % 2 == 0 else "chatgpt") for i, t in enumerate(new))
    return same_multiset, alternates, perm != list(range(1, k + 1)), perm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--export", default=DEFAULT_EXPORT)
    a = ap.parse_args()
    checks = not a.sabotage
    raw = open(a.export, "rb").read()
    live = rx.load(raw)
    print("export sha256", rx.sha(raw), "comments", len(live))

    # X1 -- live thread: unreached checkpoint is MISSING (nonzero), reached one is written (exit 0).
    c16, _ = run(live, 16, checks)
    c08, p08 = run(live, 8, checks)
    h08 = rx.sha(rx.dumps(p08)) if p08 else None
    x1 = c16 == 2 and c08 == 0
    print("X1", "HELD" if x1 else "REFUTED", f"live k=016 exit {c16} (want 2 MISSING); live k=008 exit {c08} "
          f"(want 0), {len(p08['turns']) if p08 else 0} turns, prefix sha256 {h08}")

    # X2 -- registered fixtures, each must be rejected (nonzero).
    snap08 = run(live, 8, True)[1]
    fx = {}
    d = copy.deepcopy(live)
    dup = copy.deepcopy(turn(d, 4))
    dup["id"] += 10**9
    dup["created_at"] = dup["updated_at"] = "2026-11-21T17:30:00Z"
    d.append(dup)
    fx["duplicate_004"] = run(d, 8, checks)
    d = [c for c in copy.deepcopy(live) if c["id"] != turn(live, 5)["id"]]
    fx["gap_005"] = run(d, 8, checks)
    d = copy.deepcopy(live)
    t = turn(d, 6)
    t["body"] = t["body"].replace("ccc-relay/chatgpt/006", "ccc-relay/claude/006", 1)
    fx["swapped_speaker_006"] = run(d, 8, checks)
    d = copy.deepcopy(live)
    t = turn(d, 3)
    t["body"] += "\nedited"
    t["updated_at"] = "2026-11-22T03:00:00Z"
    fx["edited_after_snapshot_003"] = run(d, 8, checks, snapshot=snap08)
    for name, (code, msg) in fx.items():
        print(f"  fixture {name}: exit {code}" + (f" ({msg})" if code == 3 else ""))
    x2 = all(code != 0 for code, _ in fx.values())
    print("X2", "HELD" if x2 else "REFUTED", f"{sum(code != 0 for code, _ in fx.values())} of {len(fx)} fixtures rejected")

    # SUPP -- not registered, never gated.
    sx = {}
    d = copy.deepcopy(live)
    t = turn(d, 7)
    t["body"] += "\nedited"
    t["updated_at"] = "2026-11-22T03:00:00Z"
    sx["edited_no_snapshot_007"] = run(d, 8, checks)
    d = copy.deepcopy(live)
    turn(d, 2)["user"]["login"] = "someone-else"
    sx["wrong_account_002"] = run(d, 8, checks)
    d = copy.deepcopy(live)
    t = turn(d, 4)
    t["body"] = t["body"].replace("\nre: ", "\nreply: ", 1)
    sx["malformed_header_004"] = run(d, 8, checks)
    d = copy.deepcopy(live)
    turn(d, 3)["created_at"] = "2026-11-21T15:00:00Z"
    sx["order_vs_time_003"] = run(d, 8, checks)
    d = copy.deepcopy(live)
    t = turn(d, 3)
    t["updated_at"] = "2026-11-22T03:00:00Z"
    sx["touched_same_bytes_with_snapshot_003"] = run(d, 8, checks, snapshot=snap08)
    for name, (code, msg) in sx.items():
        print(f"SUPP fixture {name}: exit {code}" + (f" ({msg})" if code == 3 else ""))

    # X3 -- shuffle keeps text multiset and alternation; not identity for k >= 016.
    rows, perms = [], {}
    if p08:
        m, alt, _, perms[8] = shuffled_ok(p08, 8)
        rows.append(m and alt)
        print(f"  live k=008 shuffle: multiset {m}, alternation {alt}, perm {perms[8]}")
    else:
        rows.append(False)
    for k in (16, 24, 32, 40):
        code, p = run(synthetic(k), k, checks)
        m, alt, nonid, perms[k] = shuffled_ok(p, k)
        rows.append(code == 0 and m and alt and nonid)
        print(f"  synthetic k={k:03d} shuffle: exit {code}, multiset {m}, alternation {alt}, not identity {nonid}, "
              f"perm {perms[k]}")
    x3 = all(rows)
    print("X3", "HELD" if x3 else "REFUTED", f"{sum(rows)} of {len(rows)} shuffle rows hold")

    held = (x1, x2, x3)
    canon = {"x1": [c16, c08, h08], "x2": {k: v[0] for k, v in fx.items()},
             "supp": {k: v[0] for k, v in sx.items()}, "perms": {str(k): v for k, v in perms.items()}}
    dg = hashlib.sha256(json.dumps(canon, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(f"VERDICT {sum(held)} of 3 as registered")
    print("DIGEST", dg)
    ok = (held, dg) == RECORDED if RECORDED is not None else (all(held) and not a.sabotage)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
