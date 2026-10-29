#!/usr/bin/env python3
"""PA-SIGMA-002 harness: does SigmaHQ's goodlog job catch the 1,502 broadening mutants that PA-SIGMA-001
showed its regression tests cannot fail?

Registered in experiments/pa_sigma_002/PREREG.md before this file existed. The goodlog job is run as the
workflow runs it (.github/workflows/goodlog-tests.yml at 05d1031): evtx-sigma-checker v0.8.5 with
tests/thor.yml over each of seven evtx-baseline v0.8.5 baselines, rule paths rules/windows/,
rules-emerging-threats/ and rules-threat-hunting/, then .github/workflows/matchgrep.sh with
known-FPs.csv. The job fails when matchgrep.sh exits 3 (findings left after its filters).

Every mutant and control is staged as its own rule file under a fourth --rule-path, with a fresh id so
the checker cannot confuse it with its original. After each run the staged findings get their original
rule id back (one exact substring replacement per line) and go through the real matchgrep.sh, so the
known-FP rows keyed on the original id apply to them exactly as they would in SigmaHQ's CI. A staged
item is CAUGHT on a baseline when matchgrep.sh leaves at least one of its findings.

Usage (from anywhere; the SigmaHQ venv's Python is not needed, only PyYAML):
  python run_pa_sigma_002.py --sigma SIGMA --checker EVTX_SIGMA_CHECKER --baselines DIR [--sabotage]
  python run_pa_sigma_002.py --selftest --sigma SIGMA
Exit: 0 = outcome equals RECORDED (or, before pinning, gates pass); 1 = anything else; 2 = gate failure
or environment not as registered (no verdict).
"""
import argparse
import collections
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
# PA-SIGMA-001's modules first: both studies have a feasibility.py, and this study's imports the earlier one's.
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pa_sigma_001"))
import feasibility as _f1  # noqa: E402,F401  (PA-SIGMA-001's: RULE_PATHS, load_runner)
import mutants as M  # noqa: E402  (PA-SIGMA-001's mutation operators)


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_f2 = _load("pa_sigma_002_feasibility", os.path.join(HERE, "feasibility.py"))
GOODLOG_PATHS, broadening_set = _f2.GOODLOG_PATHS, _f2.broadening_set

PINNED_SIGMA = "05d1031f537e830b76da53bae2400c5814c89165"
PINNED_SHA256 = {
    "tests/thor.yml": "8e72d9223e2c3c1d2d647b08e10118a3a067975ce7eba37dc1623f9d79604120",
    ".github/workflows/matchgrep.sh": "23412b0261f9c3629d3a04ec228bc890617550000f55d27a485698bb55ddf373",
    ".github/workflows/known-FPs.csv": "10bfaf96db16ba61bc1857f012426d96666a921f57e08fced381f20538bbbce4",
}
PINNED_CHECKER = "d672e07a516f3f72eaae8244f99fa2c5b133885a4401eb05a272903857d767e2"
PINNED_MUTANTS_MD5 = "97b57d4f5fd5ebbbf4ff9a1b93bbcd0f"
PINNED_SET = "4bb6343d864618f43b895e98a711c7599f29e895173adaec5ef7621d5d596ba0"
# baseline directory -> (archive, archive sha256, raw findings of the UNMUTATED rules, from the G1 run)
BASELINES = {
    "win7-x86": ("win7-x86.tgz", "e755f3cd48f8a3dc8877c46622339cd44fa0929981fcfd79ada63c2bafb62b9f", None),
    "Logs_Client": ("win10-client.tgz", "d48f1b328d48db6c6dfaa9b6e232dbb454d93e833c6e1248efc0faf690b6808e", None),
    "Logs_Win11": ("win11-client.tgz", "6caab8391ac3cf7135e2fd5f545c7b116a2b445ec061f83d05873f8081ff0202", None),
    "Logs_Win11_2023": ("win11-client-2023.tgz", "739079e63fc8a81d0b20eff6ee76b2f104a0cf6df115802c9bca128417c1e117", None),
    "win2022-evtx": ("win2022-evtx.tgz", "29406757f9761b56372d40550c9bef4eb2bf82ec21ba15115910742b03c4aab2", None),
    "Win2022-AD": ("win2022-ad.tgz", "dde89557c8dd19756d1fb4797f566aaa94509847c2740968bf04b5bea0b34ec1", None),
    "win2022-0-20348-azure": ("win2022-0-20348-azure.tgz", "4b3337d857f8e03273f831ad25db75e02a5a8b26b5ec14bb63727459250a5a73", None),
}
NS = uuid.UUID("6f1d2a7e-3c55-4d0e-9a51-5a1900020000")  # namespace for staged-rule ids
RECORDED = None  # pinned after the first full run, in a separate commit: (statuses, digest)
IDS = ["P1", "P2", "P3", "P4"]


class Abort(Exception):
    pass


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def md5_file(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# ---------------------------------------------------------------- staging
def restamp(text, orig_id, new_id):
    """Replace the rule's top-level id line, exactly once; everything else stays byte for byte."""
    pat = re.compile(r"^id:\s*['\"]?" + re.escape(orig_id) + r"['\"]?\s*$", re.M)
    out, n = pat.subn(f"id: {new_id}", text, count=1)
    if n != 1:
        raise Abort(f"could not restamp id {orig_id}")
    return out


def match_all_control(text):
    """The rule with its detection replaced by one that matches every process-creation event with a path."""
    r = yaml.safe_load(text)
    r["detection"] = {"selection": {"Image|contains": "\\"}, "condition": "selection"}
    return M._dump(r)


def build_items(sigma, sabotage=False):
    """All staged items: the 1,502 broadening mutants plus IDENTITY, NEVER_FIRE and MATCH_ALL controls."""
    muts = broadening_set(sigma)
    ident = hashlib.sha256("\n".join(sorted(f"{m['rule']}:{m['k']}:{m['sha']}" for m in muts)).encode()).hexdigest()
    if ident != PINNED_SET:
        raise Abort(f"broadening set identity {ident} != registered {PINNED_SET}")
    fps = known_fp_rows(sigma)
    rules = {}
    for m in muts:
        rules.setdefault(m["rule"], m)
    items = []
    originals = {}
    for rid, m in sorted(rules.items()):
        with open(os.path.join(sigma, m["path"]), encoding="utf-8") as fh:
            originals[rid] = fh.read()
    for m in muts:
        text = originals[m["rule"]] if sabotage else m["text"]  # sabotage: the mutation step returns the original
        items.append({"kind": "MUTANT", "op": m["op"], "rule": m["rule"], "k": m["k"], "sha": m["sha"],
                      "level": m["level"], "path": m["path"], "text": text})
    for rid, text in sorted(originals.items()):
        muts_all, why = M.enumerate_mutants(text)
        items.append({"kind": "IDENTITY", "op": "IDENTITY", "rule": rid, "k": 0, "sha": muts_all[0]["sha256"],
                      "level": rules[rid]["level"], "path": rules[rid]["path"], "text": muts_all[0]["text"]})
        items.append({"kind": "NEVER_FIRE", "op": "NEVER_FIRE", "rule": rid, "k": 2, "sha": muts_all[2]["sha256"],
                      "level": rules[rid]["level"], "path": rules[rid]["path"], "text": muts_all[2]["text"]})
    picked = 0
    for rid, text in sorted(originals.items()):
        r = yaml.safe_load(text)
        ls = r.get("logsource") or {}
        if (ls.get("category") == "process_creation" and str(r.get("level", "")).lower() != "low"
                and rid not in fps):
            t = match_all_control(text)
            items.append({"kind": "MATCH_ALL", "op": "MATCH_ALL", "rule": rid, "k": -1,
                          "sha": hashlib.sha256(t.encode()).hexdigest(), "level": rules[rid]["level"],
                          "path": rules[rid]["path"], "text": t})
            picked += 1
            if picked == 10:
                break
    if picked != 10:
        raise Abort(f"only {picked} MATCH_ALL controls could be built")
    for i, it in enumerate(items):
        it["tag"] = f"pa2_{i:05d}"
        it["new_id"] = str(uuid.uuid5(NS, it["tag"] + it["sha"]))
    return items


def stage(items, d):
    os.makedirs(d)
    for it in items:
        with open(os.path.join(d, it["tag"] + ".yml"), "w", encoding="utf-8") as fh:
            fh.write(restamp(it["text"], it["rule"], it["new_id"]))


def known_fp_rows(sigma):
    rows = collections.defaultdict(list)
    with open(os.path.join(sigma, ".github/workflows/known-FPs.csv"), encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            parts = line.rstrip("\n").split(";", 2)
            if len(parts) == 3:
                rows[parts[0]].append(parts[2])
    return rows


def caught_two_stage(sigma, staged, by_tag, work):
    """Staged findings, original ids restored, through the real matchgrep.sh.

    matchgrep.sh decides each line on its own (level, then known-FP rows), and an item is CAUGHT if any of its
    lines survives. Stage 1 sends each item's first STAGE1 lines; stage 2 sends every remaining line of the items
    stage 1 did not catch. Same script, same per-line decision, same verdict as one call on all lines, on far
    less data. Returns (caught Counter, raw line count per tag, stage-2 line count)."""
    raw_by_tag = {tag: len(lines) for tag, lines in staged.items()}

    def restored(tag, lines):
        it = by_tag[tag]
        needle = f'"RuleId":"{it["new_id"]}"'
        for line in lines:
            if line.count(needle) != 1:
                raise Abort(f"{tag}: RuleId not found exactly once in a finding")
            yield line.replace(needle, f'"RuleId":"{it["rule"]}"', 1)

    rw = os.path.join(work, "staged.json")
    with open(rw, "w", encoding="utf-8") as fh:
        for tag, lines in staged.items():
            fh.writelines(restored(tag, lines[:STAGE1]))
    caught = matchgrep_tags(sigma, rw)
    rest = {tag: lines[STAGE1:] for tag, lines in staged.items() if tag not in caught and len(lines) > STAGE1}
    stage2_lines = sum(len(v) for v in rest.values())
    if rest:
        with open(rw, "w", encoding="utf-8") as fh:
            for tag, lines in rest.items():
                fh.writelines(restored(tag, lines))
        caught.update(matchgrep_tags(sigma, rw))
    return caught, raw_by_tag, stage2_lines


def matchgrep_tags(sigma, path):
    """Run the real matchgrep.sh; return the staged tags of the findings it leaves (exit 3), or none (exit 0)."""
    mg = subprocess.run(["bash", os.path.join(sigma, ".github/workflows/matchgrep.sh"), path,
                         os.path.join(sigma, ".github/workflows/known-FPs.csv")],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if mg.returncode not in (0, 3):
        raise Abort(f"matchgrep.sh exit {mg.returncode}: {mg.stderr.decode()[-300:]}")
    hit = collections.Counter()
    if mg.returncode == 3:
        for line in mg.stdout.decode("utf-8", errors="replace").splitlines():
            m = TAG_RE.search(line)
            if m:
                hit[m.group(1)] += 1
    return hit


# ---------------------------------------------------------------- one baseline
TAG_RE = re.compile(r'"RulePath":"[^"]*?(pa2_\d{5})\.yml"')
STAGE1 = 20  # lines per item in the first matchgrep.sh call


def run_baseline(sigma, checker, bdir, staged_dir, by_tag, work):
    out = os.path.join(work, "findings.json")
    t0 = time.time()
    with open(out, "w") as fh:
        p = subprocess.run([checker, "--log-source", "tests/thor.yml", "--evtx-path", bdir + "/",
                            "--rule-path", "rules/windows/", "--rule-path", "rules-emerging-threats/",
                            "--rule-path", "rules-threat-hunting/", "--rule-path", staged_dir + "/"],
                           cwd=sigma, stdout=fh, stderr=subprocess.PIPE)
    secs = time.time() - t0
    if p.returncode != 0:
        raise Abort(f"checker exit {p.returncode} on {bdir}: {p.stderr.decode()[-300:]}")
    orig_lines, staged = [], collections.defaultdict(list)
    with open(out, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = TAG_RE.search(line)
            if m:
                staged[m.group(1)].append(line)
            elif line.strip():
                orig_lines.append(line)
    # G1: the unmutated rules, as CI sees them
    og = os.path.join(work, "orig.json")
    with open(og, "w", encoding="utf-8") as fh:
        fh.writelines(orig_lines)
    g1 = subprocess.run(["bash", os.path.join(sigma, ".github/workflows/matchgrep.sh"), og,
                         os.path.join(sigma, ".github/workflows/known-FPs.csv")],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    caught, raw_by_tag, stage2_lines = caught_two_stage(sigma, staged, by_tag, work)
    return {"seconds": round(secs, 1), "orig_raw": len(orig_lines), "g1_exit": g1.returncode,
            "g1_out": g1.stdout.decode().strip()[:40], "staged_raw": raw_by_tag, "caught": dict(caught),
            "stage2_lines": stage2_lines, "staged_lines": sum(raw_by_tag.values())}


# ---------------------------------------------------------------- verdicts
def analyse(items, per_base):
    caught_any = collections.defaultdict(list)
    raw_any = collections.Counter()
    for b, r in per_base.items():
        for tag in r["caught"]:
            caught_any[tag].append(b)
        for tag, n in r["staged_raw"].items():
            raw_any[tag] += n
    by_kind = collections.defaultdict(list)
    for it in items:
        by_kind[it["kind"]].append(it)
    gates = {
        "G1": all(r["g1_exit"] == 0 and r["g1_out"].startswith("No matches found") for r in per_base.values()),
        "G1b": all(r["orig_raw"] == BASELINE_RAW[b] for b, r in per_base.items()),
        "G3": sum(1 for it in by_kind["IDENTITY"] if it["tag"] in caught_any) == 0,
        "G4": sum(1 for it in by_kind["MATCH_ALL"] if it["tag"] in caught_any) >= 9,
        "G5": sum(1 for it in by_kind["NEVER_FIRE"] if raw_any[it["tag"]] > 0) == 0,
    }
    muts = by_kind["MUTANT"]
    catchable = [m for m in muts if m["bucket"] == "catchable"]
    caught = [m for m in catchable if m["tag"] in caught_any]
    frac = len(caught) / len(catchable)
    by_op = {op: (sum(1 for m in catchable if m["op"] == op and m["tag"] in caught_any),
                  sum(1 for m in catchable if m["op"] == op)) for op in M.OPERATORS}
    f_ns = by_op["NEVER_SEL"][0] / by_op["NEVER_SEL"][1]
    f_dv = by_op["DROP_VALUE"][0] / by_op["DROP_VALUE"][1]
    # P4 is over the rules that have catchable mutants (276 in the registration), counting catchable mutants only
    rules = collections.defaultdict(list)
    for m in catchable:
        rules[m["rule"]].append(m)
    rules_with_escape = sum(1 for rid, ms in rules.items() if any(m["tag"] not in caught_any for m in ms))
    S = {
        "P1": "HELD" if frac < 0.5 else "REFUTED",
        "P2": "HELD" if frac >= 0.05 else "REFUTED",
        "P3": "HELD" if f_ns > f_dv else "REFUTED",
        "P4": "HELD" if rules_with_escape >= 138 else "REFUTED",  # registered: at least 138 of the 276 rules
    }
    per_baseline_caught = {b: sum(1 for m in catchable if b in caught_any.get(m["tag"], [])) for b in per_base}
    R = {
        "catchable": len(catchable), "caught": len(caught), "frac": round(frac, 4),
        "by_op": {op: list(v) for op, v in by_op.items()},
        "frac_never_sel": round(f_ns, 4), "frac_drop_value": round(f_dv, 4),
        "rules": len(rules), "rules_with_a_mutant_passing_both_jobs": rules_with_escape,
        "uncatchable": dict(collections.Counter(m["bucket"] for m in muts if m["bucket"] != "catchable")),
        "passing_both_jobs_total": sum(1 for m in muts if m["tag"] not in caught_any),
        "per_baseline_caught": per_baseline_caught,
        "controls": {k: sum(1 for it in by_kind[k] if it["tag"] in caught_any) for k in ("IDENTITY", "MATCH_ALL", "NEVER_FIRE")},
        "never_fire_raw": sum(raw_any[it["tag"]] for it in by_kind["NEVER_FIRE"]),
        "caught_mutants": sorted(f"{m['rule']}:{m['k']}:{m['sha']}" for m in caught),
    }
    return gates, S, R


BASELINE_RAW = {}  # filled from PREREG's G1 counts at run time (see load_g1_counts)


def load_g1_counts():
    """The raw findings of the unmutated rules per baseline, as committed with the registration."""
    path = os.path.join(HERE, "g1_unmutated_output.txt")
    counts = {}
    with open(path) as fh:
        for line in fh:
            m = re.match(r"^(\S+) checker_exit=0 \d+s raw_findings=(\d+) matchgrep_exit=0 No matches found\.", line)
            if m:
                counts[m.group(1)] = int(m.group(2))
    if set(counts) != set(BASELINES):
        raise Abort(f"G1 counts file covers {sorted(counts)}, not the seven baselines")
    return counts


# ---------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma", required=True)
    ap.add_argument("--checker")
    ap.add_argument("--baselines")
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--keep", help="directory to keep the raw findings in (not committed)")
    a = ap.parse_args(argv)
    sigma = os.path.abspath(a.sigma)
    if a.selftest:
        return selftest(sigma)
    try:
        return run(a, sigma)
    except Abort as e:
        print(f"ABORT (no verdict): {e}")
        return 2


def run(a, sigma):
    head = subprocess.run(["git", "-C", sigma, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    problems = []
    if head != PINNED_SIGMA:
        problems.append(f"SigmaHQ HEAD {head}")
    for rel, want in PINNED_SHA256.items():
        if sha256_file(os.path.join(sigma, rel)) != want:
            problems.append(rel)
    checker = os.path.abspath(a.checker)
    if sha256_file(checker) != PINNED_CHECKER:
        problems.append("evtx-sigma-checker")
    if md5_file(os.path.join(os.path.dirname(HERE), "pa_sigma_001", "mutants.py")) != PINNED_MUTANTS_MD5:
        problems.append("mutants.py")
    for bdir, (arch, sha, _) in BASELINES.items():
        ap_ = os.path.join(a.baselines, arch)
        if not os.path.exists(ap_) or sha256_file(ap_) != sha:
            problems.append(f"baseline archive {arch}")
        if not os.path.isdir(os.path.join(a.baselines, bdir)):
            problems.append(f"baseline directory {bdir} not extracted")
    if problems:
        raise Abort("environment is not the registered one: " + "; ".join(problems))
    BASELINE_RAW.update(load_g1_counts())

    print(f"PA-SIGMA-002 harness{'  *** SABOTAGE: every mutant staged as its original rule ***' if a.sabotage else ''}")
    print(f"environment: {platform.system()} {platform.machine()} | Python {platform.python_version()} | "
          f"PyYAML {yaml.__version__} | SigmaHQ {head[:7]} | checker {PINNED_CHECKER[:12]}")
    items = build_items(sigma, sabotage=a.sabotage)
    fps = known_fp_rows(sigma)
    for it in items:
        if it["kind"] == "MUTANT":
            it["bucket"] = ("out_of_scope" if not it["path"].startswith(GOODLOG_PATHS) else
                            "level_low" if it["level"] == "low" else
                            "known_fp_all" if any(p == ".*" for p in fps.get(it["rule"], [])) else "catchable")
    by_tag = {it["tag"]: it for it in items}
    kinds = collections.Counter(it["kind"] for it in items)
    print(f"staged items: {dict(kinds)}")
    work = tempfile.mkdtemp(prefix="pa_sigma_002_")
    staged_dir = os.path.join(work, "staged")
    stage(items, staged_dir)
    per_base = {}
    for bdir in BASELINES:
        r = run_baseline(sigma, checker, os.path.join(os.path.abspath(a.baselines), bdir), staged_dir, by_tag, work)
        per_base[bdir] = r
        print(f"  {bdir:22s} {r['seconds']:7.1f}s unmutated raw {r['orig_raw']:5d} (G1 run {BASELINE_RAW[bdir]:5d}) "
              f"G1 matchgrep exit {r['g1_exit']} | staged items with raw findings {len(r['staged_raw']):4d} | "
              f"caught {len(r['caught']):4d}")
        if a.keep:
            os.makedirs(a.keep, exist_ok=True)
            shutil.copy(os.path.join(work, "staged.json"), os.path.join(a.keep, f"staged_{bdir}.json"))
    gates, S, R = analyse(items, per_base)
    shutil.rmtree(work, ignore_errors=True)
    for g, ok in gates.items():
        print(f"{g} {'PASS' if ok else 'FAIL'}")
    print(f"controls caught on any baseline: {R['controls']} (IDENTITY must be 0, MATCH_ALL >= 9 of 10); "
          f"NEVER_FIRE raw findings {R['never_fire_raw']} (must be 0)")
    print(f"P1 catchable mutants caught by the goodlog job: {R['caught']} of {R['catchable']} ({R['frac']:.2%}); "
          f"registered < 50% -> {S['P1']}")
    print(f"P2 same fraction >= 5% -> {S['P2']}")
    print(f"P3 NEVER_SEL caught {R['frac_never_sel']:.2%} vs DROP_VALUE {R['frac_drop_value']:.2%} (by operator "
          f"{R['by_op']}); registered NEVER_SEL > DROP_VALUE -> {S['P3']}")
    print(f"P4 rules with at least one broadening mutant passing both jobs: {R['rules_with_a_mutant_passing_both_jobs']} "
          f"of {R['rules']} rules with catchable mutants; registered >= 138 of 276 -> {S['P4']}")
    print(f"broadening mutants passing both jobs: {R['passing_both_jobs_total']} of 1502 "
          f"(uncatchable by construction: {R['uncatchable']})")
    print(f"caught per baseline: {R['per_baseline_caught']}")
    if not all(gates.values()):
        print(f"GATE FAILURE {[g for g, ok in gates.items() if not ok]}: no verdict")
        return 2
    held = tuple(S[i] for i in IDS)
    canon = json.dumps({"statuses": dict(zip(IDS, held)), "results": R}, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canon.encode()).hexdigest()
    print(f"VERDICT {sum(s == 'HELD' for s in held)} of {len(IDS)} as registered")
    print(f"DIGEST {digest}")
    res_dir = os.path.join(os.path.dirname(os.path.dirname(HERE)), "results", "pa_sigma_002")
    os.makedirs(res_dir, exist_ok=True)
    name = "results_sabotage.json" if a.sabotage else "results.json"
    with open(os.path.join(res_dir, name), "w") as fh:
        json.dump({"study": "PA-SIGMA-002", "statuses": dict(zip(IDS, held)), "results": R, "gates": gates,
                   "per_baseline": {b: {k: v for k, v in r.items() if k not in ("staged_raw", "caught")}
                                    for b, r in per_base.items()},
                   "digest": digest}, fh, indent=1, sort_keys=True)
    if RECORDED is None:
        print("RECORDED: not pinned yet")
        return 0 if not a.sabotage else 1
    match = (held, digest) == RECORDED
    print(f"RECORDED: {'reproduced' if match else 'NOT reproduced'}")
    return 0 if match else 1


# ---------------------------------------------------------------- selftest
def selftest(sigma):
    """Checks the staging and attribution path on synthetic findings, using the real matchgrep.sh."""
    ok = True
    def check(name, cond):
        nonlocal ok
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        ok &= bool(cond)
    t = "title: X\nid: 11111111-2222-3333-4444-555555555555\nlevel: high\n"
    s = restamp(t, "11111111-2222-3333-4444-555555555555", "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    check("restamp changes the id line only", s == t.replace("11111111-2222-3333-4444-555555555555",
                                                            "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"))
    try:
        restamp(t, "99999999-2222-3333-4444-555555555555", "x")
        check("restamp refuses a rule without that id", False)
    except Abort:
        check("restamp refuses a rule without that id", True)
    fps = known_fp_rows(sigma)
    all_fp = next(r for r, pats in sorted(fps.items()) if ".*" in pats)
    line = ('{"RulePath":"/tmp/x/staged/pa2_00007.yml","RuleTitle":"T","RuleId":"%s","RuleLevel":"%s",'
            '"MatchStrings":[],"Event":"Image: C:\\\\Windows\\\\x.exe"}\n')
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "s.json")
        with open(f, "w") as fh:
            fh.write(line % (all_fp, "high"))                       # filtered: known FP ".*"
            fh.write((line % ("00000000-0000-0000-0000-000000000001", "low")).replace("00007", "00008"))  # filtered: low
            fh.write((line % ("00000000-0000-0000-0000-000000000002", "high")).replace("00007", "00009"))  # survives
        mg = subprocess.run(["bash", os.path.join(sigma, ".github/workflows/matchgrep.sh"), f,
                             os.path.join(sigma, ".github/workflows/known-FPs.csv")],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        tags = [m.group(1) for m in map(TAG_RE.search, mg.stdout.decode().splitlines()) if m]
        check("real matchgrep.sh drops a known-FP '.*' finding and a low-level finding, keeps the other",
              mg.returncode == 3 and tags == ["pa2_00009"])
        # two-stage filtering gives the same verdicts as one matchgrep.sh call on every line
        narrow = next(r for r, pats in sorted(fps.items()) if "target\\.exe" in pats and ".*" not in pats)
        kept = "00000000-0000-0000-0000-000000000002"
        def staged_line(tag, event):
            return ('{"RulePath":"/tmp/x/staged/%s.yml","RuleTitle":"T","RuleId":"nid-%s","RuleLevel":"high",'
                    '"MatchStrings":[],"Event":"%s"}\n' % (tag, tag, event))
        staged = {"pa2_00001": [staged_line("pa2_00001", "Image: a.exe")] * 26,                 # rule with '.*' row
                  "pa2_00002": [staged_line("pa2_00002", "Image: a.exe")] * 3,                  # rule with no row
                  "pa2_00003": [staged_line("pa2_00003", "Image: C:\\\\x\\\\target.exe")] * 20
                               + [staged_line("pa2_00003", "Image: other.exe")]}                 # narrow row
        by = {"pa2_00001": {"new_id": "nid-pa2_00001", "rule": all_fp},
              "pa2_00002": {"new_id": "nid-pa2_00002", "rule": kept},
              "pa2_00003": {"new_id": "nid-pa2_00003", "rule": narrow}}
        two, _, s2 = caught_two_stage(sigma, staged, by, d)
        one_file = os.path.join(d, "one.json")
        with open(one_file, "w") as fh:
            for tag, ls in staged.items():
                fh.writelines(l.replace('"RuleId":"nid-%s"' % tag, '"RuleId":"%s"' % by[tag]["rule"]) for l in ls)
        one = matchgrep_tags(sigma, one_file)
        check("two-stage matchgrep gives the same caught items as one call (stage 2 catches a late survivor)",
              set(two) == set(one) == {"pa2_00002", "pa2_00003"} and s2 == 7)
        with open(f, "w") as fh:
            fh.write("")
        mg = subprocess.run(["bash", os.path.join(sigma, ".github/workflows/matchgrep.sh"), f,
                             os.path.join(sigma, ".github/workflows/known-FPs.csv")],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        check("an empty findings file passes matchgrep.sh (why G1b also checks the raw count)",
              mg.returncode == 0 and b"No matches found" in mg.stdout)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
