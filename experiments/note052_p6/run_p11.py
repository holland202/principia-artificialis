#!/usr/bin/env python3
"""note052 P11 driver (Amendment 5). Committed with the registration, before any head was measured.

Within the same 80 repositories, from the P10 pin (last commit before 2022-12-01) to the default-branch head as
cloned for P10 on 2026-11-07: did adding CI go with adding checks?

  export VL_B=<vacuity_lint.py with sha256 beginning a6c8a65d6a9150f6>   # PR #32 head, = its merge into main
  python experiments/note052_p6/run_p11.py control P10RUN OUT   planted repositories: BA with +1, BB with 0
  python experiments/note052_p6/run_p11.py measure P10RUN OUT   CI and verification-shaped count at pin and head
  python experiments/note052_p6/run_p11.py score   P10RUN OUT   P11a-P11c verdicts and the secondary comparison

P10RUN holds P10's partial clones in repos/. Standard library only.
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_p6  # noqa: E402
import run_p10  # noqa: E402
import run_p13  # noqa: E402

P10 = os.path.join(HERE, "results_p10")
MIN_GROUP = 8          # P11a and the secondary comparison: fewer than this in either group is UNDERPOWERED
DORMANT_SHARE = 0.5    # P11b
MAX_REMOVED = 2        # P11c
ENV = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")


def git(src, *a, timeout=900):
    return subprocess.run(["git", "-C", src, *a], capture_output=True, text=True, env=ENV, timeout=timeout)


def measure_rev(lp, src, rev, work):
    """Check out rev in its own worktree, take CI from the full tree, scan the filtered copy. Nothing in src moves."""
    wt, flt = f"{work}/wt", f"{work}/filtered"
    for d in (wt, flt):
        shutil.rmtree(d, ignore_errors=True)
    git(src, "worktree", "prune")
    p = git(src, "-c", "advice.detachedHead=false", "worktree", "add", "-q", "--detach", wt, rev)
    if p.returncode != 0:
        return {"ok": False, "reason": "checkout failed: " + (p.stderr.strip().splitlines() or ["?"])[-1][:160]}
    try:
        ci = run_p10.ci_of(wt)
        run_p6.filtered_copy(wt, flt)
        try:
            r = run_p13.run(lp, flt)
        except AttributeError:  # no "verification-shaped" line: the linter did not report a count
            p = subprocess.run([sys.executable, lp, flt], capture_output=True, text=True, timeout=900)
            return {"ok": False, "reason": f"no count in linter output (exit {p.returncode}): "
                                           + (p.stdout.strip().splitlines() or [""])[0][:120]}
    finally:
        git(src, "worktree", "remove", "--force", wt)
        shutil.rmtree(flt, ignore_errors=True)
    return {"ok": True, "ci": ci, "shaped": r["verification_shaped"], "findings": len(r["findings"]),
            "exit": r["exit"]}


def measure_repo(lp, src, pin, head, work):
    after = git(src, "rev-list", "--count", f"{pin}..{head}")
    anc = git(src, "merge-base", "--is-ancestor", pin, head).returncode == 0
    rec = {"pin": pin, "head": head, "pin_is_ancestor": anc,
           "commits_after_pin": int(after.stdout.strip()) if after.returncode == 0 else None,
           "head_date": git(src, "log", "-1", "--format=%cI", head).stdout.strip()}
    rec["at_pin"], rec["at_head"] = measure_rev(lp, src, pin, f"{work}/pin"), measure_rev(lp, src, head, f"{work}/head")
    return rec


def control(p10run, out):
    lp = run_p13.linter("B")
    res = {}
    for name, add in (("BA", True), ("BB", False)):
        src = f"{out}/control/{name}"
        shutil.rmtree(src, ignore_errors=True)
        os.makedirs(src)
        env = dict(ENV, GIT_AUTHOR_DATE="2022-01-01T00:00:00Z", GIT_COMMITTER_DATE="2022-01-01T00:00:00Z")
        run = lambda *a, e=env: subprocess.run(["git", "-C", src, *a], capture_output=True, text=True, env=e)  # noqa
        run("init", "-q")
        run("config", "user.email", "control@example.invalid")
        run("config", "user.name", "control")
        open(f"{src}/app.py", "w").write("def add(a, b):\n    return a + b\n")
        run("add", "-A")
        run("commit", "-q", "-m", "pin")
        pin = run("rev-parse", "HEAD").stdout.strip()
        if add:
            os.makedirs(f"{src}/.github/workflows")
            os.makedirs(f"{src}/tests")
            open(f"{src}/.github/workflows/ci.yml", "w").write("on: push\n")
            open(f"{src}/tests/test_app.py", "w").write("from app import add\n\n\ndef test_add():\n    assert add(1, 2) == 3\n")
        else:
            open(f"{src}/README.md", "w").write("notes\n")
        e2 = dict(env, GIT_AUTHOR_DATE="2024-01-01T00:00:00Z", GIT_COMMITTER_DATE="2024-01-01T00:00:00Z")
        run("add", "-A", e=e2)
        run("commit", "-q", "-m", "later", e=e2)
        head = run("rev-parse", "HEAD").stdout.strip()
        r = measure_repo(lp, src, pin, head, f"{out}/control/work_{name}")
        res[name] = {"transition": r["at_pin"]["ci"]["primary"] + r["at_head"]["ci"]["primary"],
                     "delta": r["at_head"]["shaped"] - r["at_pin"]["shaped"]}
        print(f"control {name}: transition {res[name]['transition']}, delta {res[name]['delta']}")
    ok = res["BA"] == {"transition": "BA", "delta": 1} and res["BB"] == {"transition": "BB", "delta": 0}
    print(f"control: {'PASS' if ok else 'FAIL'}")
    json.dump(res, open(f"{out}/control.json", "w"), indent=1, sort_keys=True)
    return 0 if ok else 1


def measure(p10run, out):
    lp = run_p13.linter("B")
    scan, strata = json.load(open(f"{P10}/scan.json")), json.load(open(f"{P10}/strata.json"))
    res = {}
    for rec in json.load(open(f"{P10}/fetch_log.json")):
        if not rec.get("eligible"):
            continue
        repo, src = rec["repo"], f"{p10run}/repos/{rec['repo'].replace('/', '__')}"
        if git(src, "rev-parse", "HEAD").stdout.strip() != rec["pin"]:
            sys.exit(f"{repo}: P10 checkout is not at its pin; run discarded")
        head = git(src, "rev-parse", "refs/remotes/origin/HEAD").stdout.strip()
        if not head:
            res[repo] = {"excluded": "no origin/HEAD in the P10 clone"}
            continue
        r = measure_repo(lp, src, rec["pin"], head, f"{out}/work")
        # Fail closed: the pin, re-measured here, must agree with P10's own records.
        if r["at_pin"]["ok"] and (r["at_pin"]["ci"] != strata[repo]
                                  or r["at_pin"]["shaped"] != scan[repo]["verification_shaped"]):
            sys.exit(f"{repo}: pin re-measurement disagrees with P10 (ci or count); run discarded")
        res[repo] = r
        h = r["at_head"]
        print(f"{repo}: after {r['commits_after_pin']}, head {'ok' if h['ok'] else h['reason']}")
    json.dump(res, open(f"{out}/measure.json", "w"), indent=1, sort_keys=True)
    print(f"measured {len(res)}; excluded {sum(1 for v in res.values() if 'excluded' in v or not v['at_head']['ok'])}")


def score(p10run, out):
    res = json.load(open(f"{out}/measure.json"))
    ok = {r: v for r, v in res.items() if "excluded" not in v and v["at_pin"]["ok"] and v["at_head"]["ok"]
          and v["pin_is_ancestor"] and v["commits_after_pin"] is not None}
    excluded = sorted(set(res) - set(ok))
    for r, v in ok.items():
        v["transition"] = v["at_pin"]["ci"]["primary"] + v["at_head"]["ci"]["primary"]
        v["delta"] = v["at_head"]["shaped"] - v["at_pin"]["shaped"]
    by = {t: sorted(r for r, v in ok.items() if v["transition"] == t) for t in ("AA", "AB", "BA", "BB")}
    med = lambda v: (v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2) if v else None  # noqa

    def compare(lo_name, lo, hi_name, hi):
        dl, dh = sorted(ok[r]["delta"] for r in lo), sorted(ok[r]["delta"] for r in hi)
        row = {"groups": [lo_name, hi_name], "n": [len(dl), len(dh)], "median_delta": [med(dl), med(dh)],
               "share_delta_positive": [sum(d > 0 for d in dl) / len(dl) if dl else None,
                                        sum(d > 0 for d in dh) / len(dh) if dh else None]}
        if len(dl) < MIN_GROUP or len(dh) < MIN_GROUP:
            row["verdict"] = "UNDERPOWERED"
        else:
            row["U_low_lower"], row["perm_p"] = run_p10.mannwhitney_less(dl, dh)
            row["verdict"] = "CONFIRMED" if (row["perm_p"] < 0.05 and med(dh) > med(dl)) else "REFUTED"
        return row

    bb_active = [r for r in by["BB"] if ok[r]["commits_after_pin"] > 0]
    dormant = sum(1 for v in ok.values() if v["commits_after_pin"] == 0)
    p11a = compare("BB", by["BB"], "BA", by["BA"])
    secondary = compare("BB with commits after pin", bb_active, "BA", by["BA"])
    v = {"P11a": p11a["verdict"],
         "P11b": "HELD" if dormant / len(ok) >= DORMANT_SHARE else "REFUTED",
         "P11c": "HELD" if len(by["AB"]) <= MAX_REMOVED else "REFUTED"}
    o = {"verdicts": v, "n_measured": len(ok), "excluded": excluded,
         "transitions": {t: len(rs) for t, rs in by.items()}, "transition_repos": by,
         "dormant": dormant, "P11a": p11a, "secondary_BB_active_vs_BA": secondary,
         "median_delta_by_transition": {t: med(sorted(ok[r]["delta"] for r in rs)) for t, rs in by.items()},
         "per_repo": {r: {"transition": x["transition"], "delta": x["delta"], "commits_after_pin": x["commits_after_pin"],
                          "shaped": [x["at_pin"]["shaped"], x["at_head"]["shaped"]],
                          "findings_unchecked": [x["at_pin"]["findings"], x["at_head"]["findings"]]}
                      for r, x in sorted(ok.items())}}
    json.dump(o, open(f"{out}/score.json", "w"), indent=1, sort_keys=True)
    print(json.dumps({k: o[k] for k in ("verdicts", "n_measured", "excluded", "transitions", "dormant",
                                        "median_delta_by_transition", "P11a", "secondary_BB_active_vs_BA")},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    cmd, p10run, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    sys.exit({"control": control, "measure": measure, "score": score}[cmd](p10run, out) or 0)
