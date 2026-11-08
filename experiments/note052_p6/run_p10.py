#!/usr/bin/env python3
"""note052 P10 driver (Amendment 3). Committed before any repository is drawn.

  python experiments/note052_p6/run_p10.py draw    OUT   draw the sample from GitHub search (writes OUT/sample.json)
  python experiments/note052_p6/run_p10.py fetch   OUT   clone each drawn repo and pin it to its last commit before 2022-12-01
  python experiments/note052_p6/run_p10.py scan    OUT   pinned linter on each eligible repo; strata sealed in strata.json
  python experiments/note052_p6/run_p10.py blind   OUT   shuffled hand-check sheet, repository names hidden
  python experiments/note052_p6/run_p10.py score   OUT   P10a/P10b verdicts after every finding has a verdict
  python experiments/note052_p6/run_p10.py control OUT   planted Type A file flagged, clean copy not

Uses run_p6.py's filtered_copy/parse/has_python/control. Standard library only (plus the gh CLI for search).
"""
import json, math, os, random, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_p6  # noqa: E402

LINTER_COMMIT = "b8bb09e0fc30cac3305dc2db99bbce1b8dd3ac9d"
LINTER_SHA256 = "a92963c69fa129db"
SEED = 1010
N_ELIGIBLE = 80
MAX_DRAWS = 400
PIN_BEFORE = "2022-12-01"
QUERY = "language:python stars:20..300 fork:false archived:false size:<100000 created:{a}..{b}"
CI_FILES = (".travis.yml", ".gitlab-ci.yml", "azure-pipelines.yml", "appveyor.yml", ".appveyor.yml")
CI_DIRS = (".circleci",)
MIN_PER_STRATUM = 10
HANDCHECK_CAP = 150


def linter():
    run_p6.LINTER_COMMIT, run_p6.LINTER_SHA256 = LINTER_COMMIT, LINTER_SHA256
    return run_p6.linter_path()


def months():
    out = []
    for y in range(2017, 2022):
        for m in range(1, 13):
            a = f"{y}-{m:02d}-01"
            b = f"{y + (m == 12)}-{(m % 12) + 1:02d}-01"
            out.append((a, b))
    return out


_CACHE = {}


def search(q, page):
    """Search with a cache and rate-limit retry (deviation 1: added after registration, before any draw ran;
    neither changes which repository a draw selects)."""
    if (q, page) in _CACHE:
        return _CACHE[(q, page)]
    import time
    for attempt in range(12):
        p = subprocess.run(["gh", "api", "-X", "GET", "search/repositories", "-f", f"q={q}", "-f", "per_page=100",
                            "-f", f"page={page}"], capture_output=True, text=True)
        if p.returncode == 0:
            _CACHE[(q, page)] = json.loads(p.stdout)
            return _CACHE[(q, page)]
        if "rate limit" in (p.stderr + p.stdout).lower() or "403" in p.stderr or "429" in p.stderr:
            time.sleep(65)
            continue
        raise RuntimeError(p.stderr.strip()[-200:])
    raise RuntimeError("search failed after retries")


def draw(out):
    """Draw candidates in a fixed random order: month window, then result page, then item."""
    os.makedirs(out, exist_ok=True)
    rng = random.Random(SEED)
    ms, seen, cands = months(), set(), []
    for i in range(MAX_DRAWS):
        a, b = rng.choice(ms)
        q = QUERY.format(a=a, b=b)
        total = search(q, 1)["total_count"]
        pages = max(1, min(10, math.ceil(min(total, 1000) / 100)))
        page = rng.randint(1, pages)
        items = search(q, page)["items"]
        if not items:
            continue
        it = items[rng.randrange(len(items))]
        if it["full_name"] in seen or it["owner"]["login"].lower() == "holland202":
            continue
        seen.add(it["full_name"])
        cands.append({"order": len(cands) + 1, "repo": it["full_name"], "created": it["created_at"],
                      "stars": it["stargazers_count"], "window": a, "page": page})
    json.dump({"query": QUERY, "seed": SEED, "candidates": cands}, open(f"{out}/sample.json", "w"), indent=1)
    print(f"{len(cands)} distinct candidates drawn in fixed order (eligibility decided by fetch)")


def ci_of(d):
    wf = os.path.join(d, ".github", "workflows")
    gha = os.path.isdir(wf) and any(f.endswith((".yml", ".yaml")) for f in os.listdir(wf))
    other = any(os.path.exists(os.path.join(d, f)) for f in CI_FILES) or \
        any(os.path.isdir(os.path.join(d, f)) for f in CI_DIRS)
    return {"primary": "A" if (gha or other) else "B", "gha_only": "A" if gha else "B"}


def fetch(out):
    s = json.load(open(f"{out}/sample.json"))
    os.makedirs(f"{out}/repos", exist_ok=True)
    log, eligible = [], 0
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")
    for c in s["candidates"]:
        if eligible >= N_ELIGIBLE:
            break
        r, d = c["repo"], f"{out}/repos/{c['repo'].replace('/', '__')}"
        rec = {"repo": r, "order": c["order"]}
        p = subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", f"https://github.com/{r}", d],
                           capture_output=True, text=True, env=env, timeout=600)
        if p.returncode != 0:
            rec.update(eligible=False, reason="clone failed")
        else:
            pin = subprocess.run(["git", "-C", d, "rev-list", "-1", f"--before={PIN_BEFORE}", "HEAD"],
                                 capture_output=True, text=True).stdout.strip()
            if not pin:
                rec.update(eligible=False, reason="no commit before " + PIN_BEFORE)
            else:
                co = subprocess.run(["git", "-C", d, "-c", "advice.detachedHead=false", "checkout", "-q", pin],
                                    capture_output=True, text=True, env=env, timeout=600)
                date = subprocess.run(["git", "-C", d, "log", "-1", "--format=%cI"], capture_output=True,
                                      text=True).stdout.strip()
                if co.returncode != 0:
                    rec.update(eligible=False, reason="checkout failed")
                elif not run_p6.has_python(d):
                    rec.update(eligible=False, reason="no Python file at pinned commit", pin=pin)
                else:
                    rec.update(eligible=True, pin=pin, pin_date=date)
                    eligible += 1
        log.append(rec)
    json.dump(log, open(f"{out}/fetch_log.json", "w"), indent=1)
    print(f"eligible {eligible} of {len(log)} candidates tried")


def scan(out):
    lp = linter()
    res, strata = {}, {}
    for rec in json.load(open(f"{out}/fetch_log.json")):
        if not rec.get("eligible"):
            continue
        r = rec["repo"]
        src, dst = f"{out}/repos/{r.replace('/', '__')}", f"{out}/filtered/{r.replace('/', '__')}"
        strata[r] = ci_of(src)
        shutil.rmtree(dst, ignore_errors=True)
        run_p6.filtered_copy(src, dst)
        p = subprocess.run([sys.executable, lp, dst], capture_output=True, text=True, timeout=900)
        try:
            shaped, findings = run_p6.parse(p.stdout)
        except AttributeError:
            shaped, findings = None, []
        for f in findings:
            f["path"] = os.path.relpath(f["path"], dst)
        res[r] = {"exit": p.returncode, "verification_shaped": shaped, "findings": findings}
    json.dump(res, open(f"{out}/scan.json", "w"), indent=1)
    json.dump(strata, open(f"{out}/strata.json", "w"), indent=1)  # sealed until score
    print(f"scanned {len(res)}; findings {sum(len(v['findings']) for v in res.values())}; "
          f"unparsed {sum(v['verification_shaped'] is None for v in res.values())}; strata sealed")


def blind(out):
    res = json.load(open(f"{out}/scan.json"))
    items = [(r, f) for r, v in res.items() for f in v["findings"]]
    rng = random.Random(SEED)
    rng.shuffle(items)
    sampled = len(items) > HANDCHECK_CAP
    items = items[:HANDCHECK_CAP]
    key, sheet = {}, []
    for i, (r, f) in enumerate(items, 1):
        fid = f"G{i:03d}"
        key[fid] = {"repo": r, **f}
        sheet.append({"id": fid, "category": f["category"],
                      "file": f"{out}/filtered/{r.replace('/', '__')}/{f['path']}", "verdict": None, "reason": None})
    json.dump({"sampled": sampled, "key": key}, open(f"{out}/blind_key.json", "w"), indent=1)
    json.dump(sheet, open(f"{out}/handcheck.json", "w"), indent=1)
    print(f"{len(sheet)} findings to hand-check{' (random sample of 150)' if sampled else ''}")


def fisher_one_sided(a, b, c, d):
    """P(X >= a) for the hypergeometric with row sums a+b, c+d and column sum a+c (stratum B row first)."""
    n1, n2, k = a + b, c + d, a + c
    tot = math.comb(n1 + n2, k)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / tot


def mannwhitney_less(x, y, iters=20000, seed=SEED):
    """One-sided permutation test that x (no CI) tends to be lower than y (CI), on medians-free U statistic."""
    def u(a, b):
        return sum((ai < bi) + 0.5 * (ai == bi) for ai in a for bi in b)
    obs, pool, rng, hits = u(x, y), x + y, random.Random(seed), 0
    for _ in range(iters):
        rng.shuffle(pool)
        hits += u(pool[:len(x)], pool[len(x):]) >= obs
    return obs, hits / iters


def score(out):
    res, strata = json.load(open(f"{out}/scan.json")), json.load(open(f"{out}/strata.json"))
    bk = json.load(open(f"{out}/blind_key.json"))
    sheet = {s["id"]: s for s in json.load(open(f"{out}/handcheck.json"))}
    if any(s["verdict"] not in ("TP", "FP") for s in sheet.values()):
        sys.exit("hand-check incomplete")
    tp = {r: 0 for r in res}
    for fid, k in bk["key"].items():
        tp[k["repo"]] += sheet[fid]["verdict"] == "TP"
    rows = {}
    for defn in ("primary", "gha_only"):
        grp = {s: [r for r in res if strata[r][defn] == s and res[r]["verification_shaped"] is not None] for s in "AB"}
        nA, nB = len(grp["A"]), len(grp["B"])
        tA, tB = sum(tp[r] > 0 for r in grp["A"]), sum(tp[r] > 0 for r in grp["B"])
        pA, pB = (tA / nA if nA else None), (tB / nB if nB else None)
        dA = sorted(res[r]["verification_shaped"] for r in grp["A"])
        dB = sorted(res[r]["verification_shaped"] for r in grp["B"])
        med = lambda v: (v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2) if v else None  # noqa
        under = nA < MIN_PER_STRATUM or nB < MIN_PER_STRATUM
        row = {"nA": nA, "nB": nB, "repos_with_TP_A": tA, "repos_with_TP_B": tB, "share_A": pA, "share_B": pB,
               "median_density_A": med(dA), "median_density_B": med(dB), "underpowered": under}
        if not under:
            row["fisher_p_one_sided"] = fisher_one_sided(tB, nB - tB, tA, nA - tA)
            row["U_B_lower"], row["perm_p_density"] = mannwhitney_less(dB, dA)
            gap = pB - pA
            if gap >= 0.10 and row["fisher_p_one_sided"] < 0.05:
                row["P10a"] = "CONFIRMED"
            elif gap >= 0.10:
                row["P10a"] = "INCONCLUSIVE (gap held, not significant)"
            else:
                row["P10a"] = "REFUTED"
            row["P10b"] = "CONFIRMED" if (row["perm_p_density"] < 0.05 and med(dB) < med(dA)) else "REFUTED"
        else:
            row["P10a"] = row["P10b"] = "UNDERPOWERED"
        rows[defn] = row
    per = {r: {"strata": strata[r], "shaped": res[r]["verification_shaped"], "findings": len(res[r]["findings"]),
               "tp": tp[r]} for r in res}
    o = {"decision_definition": "primary", "results": rows, "handcheck_sampled": bk["sampled"], "per_repo": per}
    json.dump(o, open(f"{out}/score.json", "w"), indent=1, sort_keys=True)
    print(json.dumps(rows, indent=1, sort_keys=True))


def control(out):
    linter()
    return run_p6.control(out)


if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    sys.exit({"draw": draw, "fetch": fetch, "scan": scan, "blind": blind, "score": score,
              "control": control}[cmd](out) or 0)
