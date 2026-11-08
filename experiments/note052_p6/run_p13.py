#!/usr/bin/env python3
"""note052 P13 driver (Amendment 4). Committed with the registration, before any rescan or census ran.

Does the decoding defect ChatGPT reported in vacuity_lint.py PR #32 change any P10 result?

  export VL_A=<vacuity_lint.py at b8bb09e>   # the instrument P10 used
  export VL_B=<vacuity_lint.py at db98e60>   # PR #32 head: tokenize.open, undecodable source -> UNPARSEABLE
  python experiments/note052_p6/run_p13.py control P10RUN OUT   K1-K3 planted files, both linters
  python experiments/note052_p6/run_p13.py census  P10RUN OUT   how each .py file decodes under A's and B's reads
  python experiments/note052_p6/run_p13.py rescan  P10RUN OUT   both linters on the 80 trees, rebuilt from the pins
  python experiments/note052_p6/run_p13.py score   P10RUN OUT   P13a-P13d verdicts

P10RUN holds P10's pinned checkouts in repos/. P10's records are read from results_p10/ next to this file.
Standard library only.
"""
import hashlib, json, os, re, shutil, subprocess, sys, tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_p6  # noqa: E402
import run_p10  # noqa: E402

P10 = os.path.join(HERE, "results_p10")
PINS = {"A": ("VL_A", "b8bb09e0fc30cac3305dc2db99bbce1b8dd3ac9d", "a92963c69fa129db"),
        "B": ("VL_B", "db98e60971452ba2ac1c8a6da3c6118cfc69f80a", "a6c8a65d6a9150f6")}
CENSUS_LIMIT = 0.01   # P13b
DIFF_LIMIT = 3        # P13c


def linter(which):
    var, commit, sha = PINS[which]
    p = os.environ.get(var)
    if not p or not os.path.exists(p):
        sys.exit(f"set {var} to vacuity_lint.py at commit {commit}")
    if hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] != sha:
        sys.exit(f"{var}: hash mismatch, not the pinned instrument")
    st = subprocess.run([sys.executable, p, "--selftest"], capture_output=True, text=True)
    m = re.search(r"(\d+)/(\d+) checks passed", st.stdout)
    if not m or m.group(1) != m.group(2) or (which == "A" and m.group(0) != "20/20 checks passed"):
        sys.exit(f"{var}: selftest did not pass; run discarded\n{st.stdout[-400:]}")
    print(f"linter {which}: {commit[:7]} sha256 {sha}, selftest {m.group(0)}")
    return p


def run(lp, d):
    p = subprocess.run([sys.executable, lp, d], capture_output=True, text=True, timeout=900)
    shaped, findings = run_p6.parse(p.stdout)
    for f in findings:
        f["path"] = os.path.relpath(f["path"], d)
    return {"exit": p.returncode, "verification_shaped": shaped, "findings": findings}


def control(p10run, out):
    la, lb = linter("A"), linter("B")
    body = "ok = True\nprint('PASS' if ok else 'FAIL')\n"   # the P10 control's planted file
    cases = {"K1": body.encode() + b"# \xff\n",              # undecodable byte on line 3
             "K2": body.encode(),
             "K3": b"\xef\xbb\xbf" + body.encode()}          # UTF-8 BOM
    res = {}
    for k, data in cases.items():
        d = f"{out}/control/{k}"
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        open(f"{d}/verify_output.py", "wb").write(data)
        res[k] = {w: sorted(f["category"] for f in run(lp, d)["findings"]) for w, lp in (("A", la), ("B", lb))}
        print(f"{k}: A {res[k]['A']}  B {res[k]['B']}")
    k1 = bool(res["K1"]["A"]) and "UNPARSEABLE" not in res["K1"]["A"] and res["K1"]["B"] == ["UNPARSEABLE"]
    k2 = bool(res["K2"]["A"]) and res["K2"]["A"] == res["K2"]["B"]
    k3 = res["K3"]["A"] == res["K3"]["B"]
    print(f"K1 (comparison can see a difference): {'PASS' if k1 else 'FAIL'}")
    print(f"K2 (B does not differ on clean input): {'PASS' if k2 else 'FAIL'}")
    print(f"K3 (prediction, not a control: BOM makes no difference): {'HELD' if k3 else 'REFUTED'}")
    json.dump(res, open(f"{out}/control.json", "w"), indent=1, sort_keys=True)
    return 0 if (k1 and k2) else 1


def trees(p10run, out):
    """Rebuild each filtered tree from its pinned checkout, refusing a checkout that moved or was modified."""
    for rec in json.load(open(f"{P10}/fetch_log.json")):
        if not rec.get("eligible"):
            continue
        name = rec["repo"].replace("/", "__")
        src, dst = f"{p10run}/repos/{name}", f"{out}/filtered/{name}"
        head = subprocess.run(["git", "-C", src, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", src, "status", "--porcelain"], capture_output=True, text=True).stdout
        if head != rec["pin"] or dirty.strip():
            sys.exit(f"{rec['repo']}: checkout is not the P10 pin, or is modified; run discarded")
        if not os.path.isdir(dst):
            run_p6.filtered_copy(src, dst)
        yield rec["repo"], dst


def decode_class(path):
    try:
        a = open(path, encoding="utf-8", errors="replace").read()   # how A reads
    except OSError:
        return "UNREADABLE"
    try:
        with tokenize.open(path) as fh:                              # how B reads
            b = fh.read()
    except (SyntaxError, UnicodeError, LookupError):
        return "UNDECODABLE"
    if a == b:
        return "SAME"
    if a.startswith("﻿") and a[1:] == b:
        return "BOM"
    return "DECLARED"


def census(p10run, out):
    counts, odd = {}, []
    for repo, d in trees(p10run, out):
        for root, _, files in os.walk(d):
            for f in sorted(files):
                p = os.path.join(root, f)
                if not f.endswith(".py") or not os.path.isfile(p):
                    continue
                c = decode_class(p)
                counts[c] = counts.get(c, 0) + 1
                if c != "SAME":
                    odd.append({"repo": repo, "path": os.path.relpath(p, d), "class": c})
    total = sum(counts.values())
    o = {"total_py": total, "counts": counts, "not_same": odd}
    json.dump(o, open(f"{out}/census.json", "w"), indent=1, sort_keys=True)
    print(f"census: {total} .py files; {json.dumps(counts, sort_keys=True)}; not SAME {len(odd)} "
          f"({100 * len(odd) / total:.3f}%)")


def rescan(p10run, out):
    la, lb = linter("A"), linter("B")
    ra, rb = {}, {}
    for repo, d in trees(p10run, out):
        ra[repo], rb[repo] = run(la, d), run(lb, d)
    json.dump(ra, open(f"{out}/rescan_A.json", "w"), indent=1)
    json.dump(rb, open(f"{out}/rescan_B.json", "w"), indent=1)
    print(f"rescanned {len(ra)}: A findings {sum(len(v['findings']) for v in ra.values())}, "
          f"B findings {sum(len(v['findings']) for v in rb.values())}")


def keys(res):
    return {(r, f["path"], f["category"]) for r, v in res.items() for f in v["findings"]}


def rows(res, strata, tp):
    """The P10 score, as run_p10.score computes it, from a scan and per-repository TP counts."""
    med = lambda v: (v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2) if v else None  # noqa
    out = {}
    for defn in ("primary", "gha_only"):
        grp = {s: [r for r in res if strata[r][defn] == s and res[r]["verification_shaped"] is not None] for s in "AB"}
        nA, nB = len(grp["A"]), len(grp["B"])
        tA, tB = sum(tp[r] > 0 for r in grp["A"]), sum(tp[r] > 0 for r in grp["B"])
        dA = sorted(res[r]["verification_shaped"] for r in grp["A"])
        dB = sorted(res[r]["verification_shaped"] for r in grp["B"])
        row = {"nA": nA, "nB": nB, "repos_with_TP_A": tA, "repos_with_TP_B": tB,
               "share_A": tA / nA if nA else None, "share_B": tB / nB if nB else None,
               "median_density_A": med(dA), "median_density_B": med(dB),
               "underpowered": nA < run_p10.MIN_PER_STRATUM or nB < run_p10.MIN_PER_STRATUM}
        if not row["underpowered"]:
            row["fisher_p_one_sided"] = run_p10.fisher_one_sided(tB, nB - tB, tA, nA - tA)
            row["U_B_lower"], row["perm_p_density"] = run_p10.mannwhitney_less(dB, dA)
            gap = row["share_B"] - row["share_A"]
            row["P10a"] = ("CONFIRMED" if gap >= 0.10 and row["fisher_p_one_sided"] < 0.05 else
                           "INCONCLUSIVE (gap held, not significant)" if gap >= 0.10 else "REFUTED")
            row["P10b"] = "CONFIRMED" if (row["perm_p_density"] < 0.05 and med(dB) < med(dA)) else "REFUTED"
        else:
            row["P10a"] = row["P10b"] = "UNDERPOWERED"
        out[defn] = row
    return out


def score(p10run, out):
    scan, strata = json.load(open(f"{P10}/scan.json")), json.load(open(f"{P10}/strata.json"))
    bk, sheet = json.load(open(f"{P10}/blind_key.json")), json.load(open(f"{P10}/handcheck.json"))
    p10 = json.load(open(f"{P10}/score.json"))["results"]
    ra, rb = json.load(open(f"{out}/rescan_A.json")), json.load(open(f"{out}/rescan_B.json"))
    cen = json.load(open(f"{out}/census.json"))
    verdict = {(k["repo"], k["path"], k["category"]): next(s["verdict"] for s in sheet if s["id"] == fid)
               for fid, k in bk["key"].items()}

    # Fidelity: this file's rows() must reproduce P10's committed score from P10's own inputs.
    tp10 = {r: 0 for r in scan}
    for (r, _, _), v in verdict.items():
        tp10[r] += v == "TP"
    if rows(scan, strata, tp10) != p10:
        sys.exit("rows() does not reproduce results_p10/score.json; score discarded")

    a_same = all(ra[r]["exit"] == scan[r]["exit"] and ra[r]["verification_shaped"] == scan[r]["verification_shaped"]
                 for r in scan) and keys(ra) == keys(scan)
    share = len(cen["not_same"]) / cen["total_py"]
    gone, new = sorted(keys(scan) - keys(rb)), sorted(keys(rb) - keys(scan))
    tp_gone = [k for k in gone if verdict.get(k) == "TP"]
    unchecked = [k for k in new if k[2] != "UNPARSEABLE"]

    def tp_counts(unchecked_as):
        t = {r: 0 for r in rb}
        for k in keys(rb):
            v = verdict.get(k) or ("FP" if k[2] == "UNPARSEABLE" else unchecked_as)
            t[k[0]] += v == "TP"
        return t
    bounds = {"unchecked_FP": rows(rb, strata, tp_counts("FP")), "unchecked_TP": rows(rb, strata, tp_counts("TP"))}
    keep = all(b[d]["P10a"] == p10[d]["P10a"] and b[d]["P10b"] == p10[d]["P10b"]
               for b in bounds.values() for d in ("primary", "gha_only"))
    shaped_changed = {r: [scan[r]["verification_shaped"], rb[r]["verification_shaped"]] for r in scan
                      if scan[r]["verification_shaped"] != rb[r]["verification_shaped"]}
    v = {"P13a": "HELD" if a_same else "REFUTED",
         "P13b": "HELD" if share < CENSUS_LIMIT else "REFUTED",
         "P13c": "HELD" if len(gone) + len(new) <= DIFF_LIMIT and not tp_gone else "REFUTED",
         "P13d": "HELD" if keep else "REFUTED"}
    o = {"verdicts": v, "census_not_same_share": share, "findings_gone": gone, "findings_new": new,
         "tp_gone": tp_gone, "new_unchecked_non_unparseable": unchecked, "shaped_changed": shaped_changed,
         "bounds": bounds}
    json.dump(o, open(f"{out}/score.json", "w"), indent=1, sort_keys=True)
    print(json.dumps({k: o[k] for k in ("verdicts", "census_not_same_share", "findings_gone", "findings_new",
                                        "tp_gone", "shaped_changed")}, indent=1, sort_keys=True))
    for name, b in bounds.items():
        for d in ("primary", "gha_only"):
            r = b[d]
            print(f"{name} {d}: TP repos B {r['repos_with_TP_B']}/{r['nB']}, A {r['repos_with_TP_A']}/{r['nA']}, "
                  f"Fisher p {r.get('fisher_p_one_sided', float('nan')):.3f}, medians {r['median_density_B']} vs "
                  f"{r['median_density_A']}, perm p {r.get('perm_p_density')}: P10a {r['P10a']}, P10b {r['P10b']}")


if __name__ == "__main__":
    cmd, p10run, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    sys.exit({"control": control, "census": census, "rescan": rescan, "score": score}[cmd](p10run, out) or 0)
