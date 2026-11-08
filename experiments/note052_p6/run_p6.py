#!/usr/bin/env python3
"""note052 P6/P8 driver (Amendment 2). Written and committed before any pool repository is cloned.

  python experiments/note052_p6/run_p6.py clone   OUT     clone the 20-repository pool (shallow, default branch)
  python experiments/note052_p6/run_p6.py scan    OUT     run the pinned linter on each clone (exclusions applied)
  python experiments/note052_p6/run_p6.py blind   OUT     write findings for hand-checking with repository names hidden
  python experiments/note052_p6/run_p6.py score   OUT     join the hand-check file with strata and print P6/P8 verdicts
  python experiments/note052_p6/run_p6.py control OUT     anti-vacuity: a planted Type A file must be found, a clean copy not

Strata are written to OUT/strata.json during `scan` and are not read again until `score`.
"""
import hashlib, json, os, random, re, shutil, subprocess, sys

POOL = ["benoitc/gunicorn", "pallets/jinja", "psf/requests", "celery/celery", "pallets/click",
        "kennethreitz/records", "mitsuhiko/rye", "pyca/cryptography", "tqdm/tqdm", "python-attrs/attrs",
        "kennethreitz/maya", "kennethreitz/pipenv-old", "jsvine/pdfplumber", "mkorpela/pabot", "dbader/schedule",
        "jd/tenacity", "lepture/mistune", "bslatkin/effectivepython", "amoffat/sh", "gruns/furl"]
LINTER_COMMIT = "a468d2c7005f26a45a985a792fc12bfcf07dc81b"
LINTER_SHA256 = "7a5b8d100457128f"  # first 16 hex of vacuity_lint.py at that commit
ESTATE_DENSITY = 1.2
SEED = 52


def sh(*a, **k):
    return subprocess.run(a, capture_output=True, text=True, **k)


def linter_path():
    p = os.environ.get("VL_A468")
    if not p or not os.path.exists(p):
        sys.exit("set VL_A468 to vacuity_lint.py at commit " + LINTER_COMMIT)
    if hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] != LINTER_SHA256:
        sys.exit("linter hash mismatch: not the pinned instrument")
    st = sh(sys.executable, p, "--selftest")
    if "20/20 checks passed" not in st.stdout:
        sys.exit("linter selftest did not report 20/20; run discarded")
    return p


def clone(out):
    os.makedirs(f"{out}/repos", exist_ok=True)
    log = {}
    for r in POOL:
        dest = f"{out}/repos/{r.replace('/', '__')}"
        p = sh("git", "clone", "-q", "--depth", "1", f"https://github.com/{r}", dest,
               env=dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0"))
        if p.returncode != 0:
            log[r] = {"available": False, "reason": (p.stderr.strip().splitlines() or ["?"])[-1][:200]}
            continue
        head = sh("git", "-C", dest, "log", "-1", "--format=%H %cI").stdout.split()
        log[r] = {"available": True, "head": head[0], "head_date": head[1]}
    json.dump(log, open(f"{out}/clone_log.json", "w"), indent=1)
    print(json.dumps(log, indent=1))


def has_python(d):
    return any(f.endswith(".py") for _, _, fs in os.walk(d) for f in fs)


def filtered_copy(src, dst):
    def ignore(dirpath, names):
        return {n for n in names if n in (".git", "examples") or n == "conftest.py"}
    shutil.copytree(src, dst, ignore=ignore, symlinks=True)


def parse(text):
    shaped = int(re.search(r"verification-shaped\s*:\s*(\d+)", text).group(1))
    findings, cat = [], None
    for line in text.splitlines():
        m = re.match(r"^([A-Z_]+)\s+\((\d+)\)\s*$", line)
        if m:
            cat = m.group(1)
            continue
        m = re.match(r"^  (/\S.*)$", line)
        if m and cat:
            findings.append({"category": cat, "path": m.group(1).strip()})
    return shaped, findings


def scan(out):
    lp = linter_path()
    log = json.load(open(f"{out}/clone_log.json"))
    res, strata = {}, {}
    for r, info in log.items():
        if not info["available"]:
            continue
        src = f"{out}/repos/{r.replace('/', '__')}"
        if not has_python(src):
            info.update(available=False, reason="no Python file")
            continue
        wf = os.path.join(src, ".github", "workflows")
        strata[r] = "A" if os.path.isdir(wf) and any(f.endswith((".yml", ".yaml")) for f in os.listdir(wf)) else "B"
        dst = f"{out}/filtered/{r.replace('/', '__')}"
        if os.path.exists(dst):
            shutil.rmtree(dst)
        filtered_copy(src, dst)
        p = sh(sys.executable, lp, dst)
        open(f"{out}/filtered/{r.replace('/', '__')}.lint.txt", "w").write(p.stdout + p.stderr)
        shaped, findings = parse(p.stdout)
        for f in findings:
            f["path"] = os.path.relpath(f["path"], dst)
        res[r] = {"exit": p.returncode, "verification_shaped": shaped, "findings": findings}
    json.dump(log, open(f"{out}/clone_log.json", "w"), indent=1)
    json.dump(res, open(f"{out}/scan.json", "w"), indent=1)
    json.dump(strata, open(f"{out}/strata.json", "w"), indent=1)  # sealed until `score`
    print(f"scanned {len(res)} repositories; findings {sum(len(v['findings']) for v in res.values())}; "
          f"strata written to strata.json (not printed)")


def blind(out):
    res = json.load(open(f"{out}/scan.json"))
    items = [(r, f) for r, v in res.items() for f in v["findings"]]
    random.Random(SEED).shuffle(items)
    key, sheet = {}, []
    for i, (r, f) in enumerate(items, 1):
        fid = f"F{i:03d}"
        key[fid] = {"repo": r, **f}
        sheet.append({"id": fid, "category": f["category"], "file": f"{out}/filtered/{r.replace('/', '__')}/{f['path']}",
                      "verdict": None, "reason": None})
    json.dump(key, open(f"{out}/blind_key.json", "w"), indent=1)
    json.dump(sheet, open(f"{out}/handcheck.json", "w"), indent=1)
    print(f"{len(sheet)} findings to hand-check in handcheck.json")


def score(out):
    res, strata = json.load(open(f"{out}/scan.json")), json.load(open(f"{out}/strata.json"))
    key = json.load(open(f"{out}/blind_key.json"))
    sheet = {s["id"]: s for s in json.load(open(f"{out}/handcheck.json"))}
    if any(s["verdict"] not in ("TP", "FP") for s in sheet.values()):
        sys.exit("hand-check incomplete: every finding needs TP or FP before any rate is computed")
    tp = {r: 0 for r in res}
    for fid, k in key.items():
        tp[k["repo"]] += sheet[fid]["verdict"] == "TP"
    agg = {}
    for s in "AB":
        rs = [r for r in res if strata[r] == s]
        shaped = sum(res[r]["verification_shaped"] for r in rs)
        t = sum(tp[r] for r in rs)
        agg[s] = {"repos": len(rs), "shaped": shaped, "tp": t, "findings": sum(len(res[r]["findings"]) for r in rs),
                  "rate": (t / shaped) if shaped else None, "density": (shaped / len(rs)) if rs else None}
    under = agg["A"]["repos"] < 3 or agg["B"]["repos"] < 3
    rA, rB = agg["A"]["rate"], agg["B"]["rate"]
    p6 = None if under or rA is None or rB is None else (rB - rA) >= 0.05
    dA, dB = agg["A"]["density"], agg["B"]["density"]
    p8 = None if under or dA is None or dB is None else (ESTATE_DENSITY < dB < dA)
    per = {r: {"stratum": strata[r], "shaped": res[r]["verification_shaped"], "findings": len(res[r]["findings"]),
               "tp": tp[r]} for r in res}
    out_j = {"per_repo": per, "strata": agg, "underpowered": under,
             "P6": "UNDERPOWERED" if p6 is None else ("CONFIRMED" if p6 else "REFUTED"),
             "P8": "UNDERPOWERED" if p8 is None else ("CONFIRMED" if p8 else "REFUTED")}
    json.dump(out_j, open(f"{out}/score.json", "w"), indent=1, sort_keys=True)
    print(json.dumps(out_j, indent=1, sort_keys=True))


def control(out):
    lp = linter_path()
    d = f"{out}/control"
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(f"{d}/clean")
    os.makedirs(f"{d}/planted")
    open(f"{d}/clean/check_ok.py", "w").write("x = 1\nassert x == 1\n")
    open(f"{d}/planted/check_ok.py", "w").write("x = 1\nassert x == 1\n")
    open(f"{d}/planted/verify_output.py", "w").write("ok = True\nprint('PASS' if ok else 'FAIL')\n")
    c, p = sh(sys.executable, lp, f"{d}/clean"), sh(sys.executable, lp, f"{d}/planted")
    _, fc = parse(c.stdout)
    _, fp = parse(p.stdout)
    ok = not fc and any(f["path"].endswith("verify_output.py") for f in fp)
    print(f"control: clean findings {len(fc)}, planted findings {[f['category'] for f in fp]} -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    sys.exit({"clone": clone, "scan": scan, "blind": blind, "score": score, "control": control}[cmd](out) or 0)
