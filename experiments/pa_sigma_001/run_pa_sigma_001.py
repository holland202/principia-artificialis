#!/usr/bin/env python3
"""PA-SIGMA-001 harness: does SigmaHQ's regression-test job fail when a tested rule is weakened or broken?

Registered in PREREG.md (commit 1b0b9c4) before this file existed. Every verdict is SigmaHQ's own: this
file imports `tests/regression_tests_runner.py` from the SigmaHQ checkout and calls its `run_tests`,
which calls the runner's `run_evtx_batch` and `run_json_checker`. Thin wrappers ("taps") record the
match counts those functions return and check that the bytes they are handed are the mutant's bytes;
they call the real functions unchanged.

Usage (the `sigma` CLI, sigma-cli 3.1.x, must be on PATH):
  python run_pa_sigma_001.py SIGMA_CHECKOUT EVTX_CHECKER JSON_CHECKER [--out DIR] [--look-diffs FILE]
  python run_pa_sigma_001.py SIGMA_CHECKOUT EVTX_CHECKER JSON_CHECKER --sabotage
  python run_pa_sigma_001.py SIGMA_CHECKOUT EVTX_CHECKER JSON_CHECKER --selftest

Exit codes:
  0  a complete run whose outcome equals RECORDED (or RECORDED is not pinned yet); --selftest passed
  1  a gate failed, a mutant is UNRESOLVED, or the outcome differs from RECORDED (--sabotage must give 1)
  2  aborted, fail closed: no outcome is recorded
"""
import argparse
import collections
import contextlib
import copy
import difflib
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mutants as M  # noqa: E402
from feasibility import RULE_PATHS, load_runner, sample_events  # noqa: E402

# ---- registered constants (PREREG.md) -------------------------------------------------------------
PINNED_SIGMA = "05d1031f537e830b76da53bae2400c5814c89165"
PINNED_SHA256 = {
    "tests/regression_tests_runner.py": "d1b88d4b465ce3b227b26a8f76bdd59249e1c79c8f7fc018618f053e0080a438",
    "tests/thor.yml": "8e72d9223e2c3c1d2d647b08e10118a3a067975ce7eba37dc1623f9d79604120",
}
PINNED_EVTX_CHECKER = "d672e07a516f3f72eaae8244f99fa2c5b133885a4401eb05a272903857d767e2"
PINNED_JSON_CHECKER = "abd279e669a04f63db2bb505efc94e36be79d740aec5221b3547b53551966368"
PINNED_MUTANTS_MD5 = "97b57d4f5fd5ebbbf4ff9a1b93bbcd0f"
THOR = "tests/thor.yml"
MAX_EXCLUDED_RULES = 23          # G2: more than 5% of 471 rules excluded -> P1-P4 COULD NOT RUN AS REGISTERED
MAX_INVALID = 275                # G3: more than 5% of 5,509 operator mutants INVALID -> same
PASSES = 2                       # G4: the full census is run twice and must agree
PREDICTIONS = ("P1", "P2", "P3", "P4")
# Pinned after the first published run, in a separate commit (W4): (prediction outcomes, DIGEST).
# Run outputs: results/pa_sigma_001/run1.txt and run2.txt (commit 5a26f40), harness md5 d05d24ae2490baf38c96483c2c5f6ff4.
RECORDED = (("HELD", "HELD", "HELD", "HELD"), "765032efccf9cb7e6c9f7a6c41195980a9dfe78ef075b8bbbc40e107cbef929d")

PRECHECK_RX = re.compile(r"could not add rules from (\S+?\.yml): ")
# Lines the runner prints only on paths that are not a plain pass or a plain "match count too low".
ERROR_MARKERS = (
    "Error compiling rule", "Timeout", "Error running json_checker", "sigma produced an empty expr query",
    "evtx-sigma-checker exited with code", "Aborting further EVTX tests", "Unknown test type",
    "--json-checker is required", "Skipping non-JSON line", "EVTX filename collision",
)
NARROW, BROAD = "NARROWING", "BROADENING"


class Abort(Exception):
    """Fail closed (C-BUILD): the run stops with exit 2 and records no outcome."""


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def md5_file(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


# ---- taps around the runner's own functions -------------------------------------------------------
class Taps:
    """Record what the runner's functions return; refuse bytes the harness did not stage."""

    def __init__(self, runner):
        self.real_batch = runner.run_evtx_batch
        self.real_json = runner.run_json_checker
        runner.run_evtx_batch = self._batch
        runner.run_json_checker = self._json
        self.lock = threading.Lock()
        self.expected = None
        self.evtx, self.json_out, self.batch_calls = None, {}, 0

    def begin(self, expected):
        self.expected, self.evtx, self.json_out, self.batch_calls = dict(expected), None, {}, 0

    def end(self):
        self.expected = None

    def _check(self, path):
        exp = None if self.expected is None else self.expected.get(path)
        if exp is None:
            raise Abort(f"the runner was handed a file the harness did not stage: {path}")
        if sha256_file(path) != exp:
            raise Abort(f"staged bytes differ from the mutant's bytes: {path}")

    def _batch(self, items, evtx_checker_path, thor_config):
        for rule_info, _, _ in items:
            self._check(rule_info["path"])
        self.batch_calls += 1
        matches = self.real_batch(items, evtx_checker_path, thor_config)
        self.evtx = matches
        return matches

    def _json(self, test_type, rule_path, rule_id, test_data, json_checker_path):
        self._check(rule_path)
        ok, out = self.real_json(test_type, rule_path, rule_id, test_data, json_checker_path)
        n = 0 if not out else out.count("\n    ") + 1  # the runner joins match lines with "\n    "
        with self.lock:
            self.json_out[(rule_id, test_data["path"])] = (ok, n)
        return ok, out


class CompileCache:
    """Memoize the runner's real `compile_rule_to_expr` by file content, so the validity pre-check and
    `run_tests` share one `sigma convert` per mutant. Cleared between passes so passes stay independent."""

    def __init__(self, runner):
        self.real = runner.compile_rule_to_expr
        runner.compile_rule_to_expr = self
        self.lock = threading.Lock()
        self.cache = {}

    def clear(self):
        with self.lock:
            self.cache = {}

    def __call__(self, rule_path, pipelines, filters):
        with open(rule_path, "rb") as f:
            key = (sha256_bytes(f.read()), tuple(pipelines), tuple(filters))
        with self.lock:
            hit = self.cache.get(key)
        if hit is None:
            try:
                hit = ("ok", self.real(rule_path, pipelines, filters))
            except subprocess.CalledProcessError as e:
                hit = ("err", e)
            with self.lock:
                self.cache[key] = hit
        if hit[0] == "err":
            raise hit[1]
        return hit[1]


# ---- setup -----------------------------------------------------------------------------------------
class Ctx:
    pass


def setup(sigma, evtx_checker, json_checker, check_pins=True):
    ctx = Ctx()
    ctx.sigma = os.path.abspath(sigma)
    ctx.evtx_checker = os.path.abspath(evtx_checker)
    ctx.json_checker = os.path.abspath(json_checker)
    if shutil.which("sigma") is None:
        raise Abort("the `sigma` CLI is not on PATH")
    head = subprocess.run(["git", "-C", ctx.sigma, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    ctx.meta = {
        "sigma_head": head,
        "runner_sha256": sha256_file(os.path.join(ctx.sigma, "tests/regression_tests_runner.py")),
        "thor_sha256": sha256_file(os.path.join(ctx.sigma, THOR)),
        "evtx_checker_sha256": sha256_file(ctx.evtx_checker),
        "json_checker_sha256": sha256_file(ctx.json_checker),
        "mutants_md5": md5_file(os.path.join(HERE, "mutants.py")),
        "harness_md5": md5_file(os.path.abspath(__file__)),
        "python": platform.python_version(),
        "platform": f"{platform.system()} {platform.machine()}",
        "packages": _package_versions(),
    }
    if check_pins:
        problems = []
        if head != PINNED_SIGMA:
            problems.append(f"SigmaHQ HEAD {head} != {PINNED_SIGMA}")
        for rel, want in PINNED_SHA256.items():
            if sha256_file(os.path.join(ctx.sigma, rel)) != want:
                problems.append(f"{rel} sha256 differs from the registration")
        if ctx.meta["evtx_checker_sha256"] != PINNED_EVTX_CHECKER:
            problems.append("evtx-sigma-checker sha256 differs from the registration")
        if ctx.meta["json_checker_sha256"] != PINNED_JSON_CHECKER:
            problems.append("json_checker sha256 differs from the registration")
        if ctx.meta["mutants_md5"] != PINNED_MUTANTS_MD5:
            problems.append("mutants.py md5 differs from the registration")
        if problems:
            raise Abort("environment is not the registered one: " + "; ".join(problems))
    ctx.runner = load_runner(ctx.sigma)
    os.chdir(ctx.sigma)
    ctx.taps = Taps(ctx.runner)
    ctx.compile = CompileCache(ctx.runner)
    ctx.ns = argparse.Namespace(evtx_checker=ctx.evtx_checker, thor_config=THOR, verbose=False,
                                json_checker=ctx.json_checker, workers=None)
    ctx.work = tempfile.mkdtemp(prefix="pa_sigma_001_")
    ctx.empty_dir = os.path.join(ctx.work, "empty_samples")
    ctx.invalid_dir = os.path.join(ctx.work, "invalid")
    os.makedirs(ctx.empty_dir)
    os.makedirs(ctx.invalid_dir)
    return ctx


def _package_versions():
    out = {}
    try:
        from importlib.metadata import version
        for name in ("pySigma", "sigma-cli", "pySigma-backend-golangexpr", "PyYAML", "python-evtx"):
            try:
                out[name] = version(name)
            except Exception:  # noqa: BLE001 - reported, not fatal
                out[name] = "not installed"
    except Exception:  # noqa: BLE001
        pass
    return out


# ---- the plan: every rule's mutants, controls first ------------------------------------------------
def build_plan(ctx, sabotage=False, only=None):
    rules, _, _ = ctx.runner.find_rules_with_tests(RULE_PATHS)
    rules = sorted(rules, key=lambda r: r["id"])
    if only is not None:
        rules = [r for r in rules if r["id"] in only]
    plan = []
    for r in rules:
        with open(r["path"], "rb") as f:
            raw = f.read()
        muts, why = M.enumerate_mutants(raw.decode("utf-8"))
        if why:
            raise Abort(f"rule {r['id']} was skipped by mutants.py ({why}); the registration counted 0 skipped")
        if [m["op"] for m in muts[:3]] != ["IDENTITY", "ROUNDTRIP", "NEVER_FIRE"]:
            raise Abort(f"rule {r['id']}: controls are not the first three mutants")
        if muts[0]["text"].encode("utf-8") != raw:
            raise Abort(f"rule {r['id']}: IDENTITY is not byte-identical to the rule file")
        for k, m in enumerate(muts):
            m["k"] = k
        if sabotage:  # the mutation step silently returns the original rule (pre-mortem failure 1)
            ident = muts[0]
            muts = [dict(m, text=ident["text"], sha256=ident["sha256"]) for m in muts]
        plan.append({"rule": r, "mutants": muts})
    return plan


# ---- one round: the k-th mutant of every rule that has one -----------------------------------------
def precheck(ctx, rdir, staged):
    """Same checker, same arguments, empty sample directory. Returns {path: reason} for files it rejects."""
    invalid = {}
    by_real = {os.path.realpath(p): p for _, _, p in staged}
    while True:
        r = subprocess.run([ctx.evtx_checker, "--log-source", THOR, "--evtx-path", ctx.empty_dir,
                            "--rule-level", "informational", "--rule-path", rdir],
                           capture_output=True, text=True, timeout=600)
        if r.returncode == 0:
            if r.stdout.strip():
                raise Abort("the pre-check printed matches with no samples present")
            return invalid
        mm = PRECHECK_RX.search(r.stderr)
        if not mm:
            raise Abort(f"checker failed and named no rule file: {r.stderr.strip()[:300]!r}")
        p = by_real.get(os.path.realpath(mm.group(1)))
        if p is None or p in invalid:
            raise Abort(f"checker named a file that is not a staged mutant: {mm.group(1)}")
        line = r.stderr[mm.end():].splitlines()[0] if r.stderr[mm.end():] else ""
        invalid[p] = "checker: " + re.sub(r"of rule .*?: ", "of rule <title>: ", line)[:200]
        shutil.move(p, os.path.join(ctx.invalid_dir, f"{os.path.basename(rdir)}_{os.path.basename(p)}"))


def run_round(ctx, k, batch, recs):
    rdir = tempfile.mkdtemp(prefix=f"round{k:03d}_", dir=ctx.work)
    staged, expected = [], {}
    for e, m in batch:
        path = os.path.join(rdir, f"{e['rule']['id']}.yml")
        data = m["text"].encode("utf-8")
        if sha256_bytes(data) != m["sha256"]:
            raise Abort(f"mutant {e['rule']['id']}#{m['k']} does not hash to its recorded sha256")
        with open(path, "wb") as f:
            f.write(data)
        expected[path] = m["sha256"]
        staged.append((e, m, path))
    invalid = precheck(ctx, rdir, staged)
    for e, m, path in staged:
        if path in invalid:
            continue
        for t in e["rule"]["tests"]:
            if t.get("type") == "evtx":
                continue
            try:
                ctx.compile(path, t.get("pipelines", []), t.get("filters", []))
            except subprocess.CalledProcessError as err:
                invalid[path] = f"sigma convert exited {err.returncode}"
                break
    valid = [(e, m, p) for e, m, p in staged if p not in invalid]
    infos = [dict(e["rule"], path=p) for e, m, p in valid]
    ctx.taps.begin(expected)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            total, passed, failures = ctx.runner.run_tests(ctx.ns, infos)
    finally:
        ctx.taps.end()
    printed = buf.getvalue()
    for marker in ERROR_MARKERS:
        if marker in printed:
            raise Abort(f"round {k}: the runner printed {marker!r}")
    if any(f.get("batch_failed") for f in failures):
        raise Abort(f"round {k}: the runner reports a failed batch")
    n_tests = sum(len(i["tests"]) for i in infos)
    if total != n_tests or passed + len(failures) != total:
        raise Abort(f"round {k}: {total} tests reported, {n_tests} expected, {passed} passed, {len(failures)} failed")
    n_evtx = sum(1 for i in infos for t in i["tests"] if t.get("type") == "evtx")
    if ctx.taps.batch_calls != (1 if n_evtx else 0):
        raise Abort(f"round {k}: {ctx.taps.batch_calls} checker batches for {n_evtx} EVTX tests")
    failed = collections.Counter(f["rule_id"] for f in failures)
    evtx = ctx.taps.evtx or {}
    warned = set(re.findall(r"Warning: (\S+): Got \d+ matches but only \d+ expected", printed))
    for e, m, p in valid:
        rid = e["rule"]["id"]
        counts, expect = [], []
        for t in e["rule"]["tests"]:
            expect.append(t.get("match_count"))
            if t.get("type") == "evtx":
                counts.append(len(evtx.get(rid, [])))
            else:
                key = (rid, t["path"])
                if key not in ctx.taps.json_out:
                    raise Abort(f"round {k}: json test of {rid} was not observed")
                counts.append(ctx.taps.json_out[key][1])
        outcome = "KILLED" if failed[rid] else "SURVIVED"
        # Consistency check only (the verdict above is the runner's): its pass rule applied to the counts.
        rule_pass = all((c >= x) if x is not None else (c > 0) for c, x in zip(counts, expect))
        if rule_pass != (outcome == "SURVIVED"):
            raise Abort(f"round {k}: runner verdict for {rid} disagrees with its pass rule on counts {counts}")
        over = any(x is not None and c > x for c, x in zip(counts, expect))
        if over != (rid in warned):
            raise Abort(f"round {k}: over-match warning for {rid} does not match its counts")
        recs[(rid, m["k"])] = _rec(e, m, outcome, counts, expect, over)
    for e, m, p in staged:
        if p in invalid:
            recs[(e["rule"]["id"], m["k"])] = _rec(e, m, "INVALID", None, [t.get("match_count") for t in e["rule"]["tests"]],
                                                   False, invalid[p])
    shutil.rmtree(rdir)


def _rec(e, m, outcome, counts, expect, over, reason=None):
    r = {"rule": e["rule"]["id"], "k": m["k"], "op": m["op"], "dir": m["direction"], "site": m["site"],
         "sha": m["sha256"], "out": outcome, "counts": counts, "expect": expect, "over": over}
    if reason:
        r["reason"] = reason
    return r


def census(ctx, plan):
    ctx.compile.clear()
    recs = {}
    nrounds = max(len(e["mutants"]) for e in plan)
    for k in range(nrounds):
        batch = [(e, e["mutants"][k]) for e in plan if k < len(e["mutants"])]
        run_round(ctx, k, batch, recs)
    expected = sum(len(e["mutants"]) for e in plan)
    if len(recs) != expected:
        raise Abort(f"census recorded {len(recs)} mutants, plan has {expected}")
    return recs


# ---- analysis and scoring --------------------------------------------------------------------------
def analyse(plan, passes, events_per_test):
    a, b = passes[0], passes[-1]
    unresolved = sorted(key for key in a if (a[key]["out"], a[key]["counts"]) != (b[key]["out"], b[key]["counts"]))
    final = {key: dict(a[key]) for key in a}
    for key in unresolved:
        final[key]["out"] = "UNRESOLVED"
    by_rule = collections.defaultdict(list)
    for r in final.values():
        by_rule[r["rule"]].append(r)
    for rid in by_rule:
        by_rule[rid].sort(key=lambda r: r["k"])
    ctrl = {rid: {r["op"]: r for r in rs if r["op"] in M.CONTROLS} for rid, rs in by_rule.items()}
    g1_fail = sorted(rid for rid, c in ctrl.items() if c["IDENTITY"]["out"] != "SURVIVED")
    excluded = sorted(rid for rid, c in ctrl.items()
                      if c["IDENTITY"]["out"] != "SURVIVED" or c["ROUNDTRIP"]["out"] != "SURVIVED"
                      or c["NEVER_FIRE"]["out"] != "KILLED")
    included = set(by_rule) - set(excluded)
    ops = [r for r in final.values() if r["op"] in M.OPERATORS]
    invalid_ops = sorted((r["rule"], r["k"]) for r in ops if r["out"] == "INVALID")

    # CHANGED and monotonicity (G5) against IDENTITY's counts
    g5 = []
    for r in ops:
        ident = ctrl[r["rule"]]["IDENTITY"]
        if r["out"] in ("INVALID", "UNRESOLVED") or ident["out"] != "SURVIVED":
            r["changed"] = None
            continue
        r["changed"] = r["counts"] != ident["counts"]
        lower = any(c < i for c, i in zip(r["counts"], ident["counts"]))
        higher = any(c > i for c, i in zip(r["counts"], ident["counts"]))
        if (r["dir"] == BROAD and lower) or (r["dir"] == NARROW and higher):
            g5.append((r["rule"], r["k"]))
    g5 = sorted(g5)

    scored = [r for r in ops if r["rule"] in included and r["out"] in ("KILLED", "SURVIVED")]
    verdicts, detail = score(scored, g1_fail, excluded, invalid_ops)
    sens = score([r for r in scored if (r["rule"], r["k"]) not in set(g5)], g1_fail, excluded, invalid_ops)[0] if g5 else None

    # D2: tests where IDENTITY matches every sample event
    d2_all = d2_464 = n_464 = 0
    for rid, c in ctrl.items():
        for t, n in zip([e for e in plan if e["rule"]["id"] == rid][0]["rule"]["tests"], c["IDENTITY"]["counts"] or []):
            ev = events_per_test[(rid, t["path"])]
            exp = t.get("match_count") or 1
            d2_all += n == ev
            if ev <= exp:
                n_464 += 1
                d2_464 += n == ev

    return {"final": final, "unresolved": unresolved, "g1_fail": g1_fail, "excluded": excluded,
            "invalid_ops": invalid_ops, "g5": g5, "verdicts": verdicts, "detail": detail, "sens": sens,
            "included": included, "scored": scored, "d2": (d2_all, d2_464, n_464), "by_rule": by_rule, "ctrl": ctrl}


def score(scored, g1_fail, excluded, invalid_ops):
    """Registered scoring of P1-P4 (PREREG.md). Exact integer comparisons."""
    detail = {}
    if g1_fail:
        return ("IMPLEMENTATION_ERROR",) * 4, {"why": f"G1 failed for {len(g1_fail)} rule(s)"}
    if len(excluded) > MAX_EXCLUDED_RULES or len(invalid_ops) > MAX_INVALID:
        return ("COULD NOT RUN AS REGISTERED",) * 4, {
            "why": f"G2 excluded {len(excluded)} (max {MAX_EXCLUDED_RULES}); G3 INVALID {len(invalid_ops)} (max {MAX_INVALID})"}
    broad = [r for r in scored if r["dir"] == BROAD]
    p1_killed = sum(r["out"] == "KILLED" for r in broad)
    detail["P1"] = f"BROADENING mutants KILLED: {p1_killed} of {len(broad)}"
    p1 = "HELD" if p1_killed == 0 else "REFUTED"

    dv = [r for r in scored if r["op"] == "DROP_VALUE" and r["dir"] == NARROW]
    dv_s = sum(r["out"] == "SURVIVED" for r in dv)
    detail["P2"] = f"DROP_VALUE NARROWING SURVIVED: {dv_s} of {len(dv)}"
    p2 = "INSUFFICIENT_EVIDENCE" if not dv else ("HELD" if dv_s * 2 > len(dv) else "REFUTED")

    narrow_rules = collections.defaultdict(list)
    for r in scored:
        if r["dir"] == NARROW:
            narrow_rules[r["rule"]].append(r["out"])
    with_surv = sum(1 for outs in narrow_rules.values() if "SURVIVED" in outs)
    detail["P3"] = f"rules with a surviving NARROWING mutant: {with_surv} of {len(narrow_rules)}"
    p3 = "INSUFFICIENT_EVIDENCE" if not narrow_rules else ("HELD" if with_surv * 2 > len(narrow_rules) else "REFUTED")

    ns = [r for r in scored if r["op"] == "NEVER_SEL" and r["dir"] == NARROW]
    ns_s = sum(r["out"] == "SURVIVED" for r in ns)
    detail["P4"] = f"NEVER_SEL NARROWING SURVIVED: {ns_s} of {len(ns)}"
    p4 = "INSUFFICIENT_EVIDENCE" if not ns else ("HELD" if ns_s * 10 >= len(ns) else "REFUTED")
    return (p1, p2, p3, p4), detail


def digest_of(an):
    rows = sorted([r["rule"], r["k"], r["op"], r["dir"], r["sha"], r["out"], r["counts"]] for r in an["final"].values())
    canon = {"mutants": rows, "unresolved": [list(k) for k in an["unresolved"]], "g1_fail": an["g1_fail"],
             "excluded": an["excluded"], "invalid_ops": [list(k) for k in an["invalid_ops"]],
             "g5": [list(k) for k in an["g5"]], "verdicts": list(an["verdicts"])}
    return sha256_bytes(json.dumps(canon, sort_keys=True, separators=(",", ":")).encode())


def look_sample(an):
    cells = collections.OrderedDict([((BROAD, "SURVIVED"), []), ((NARROW, "SURVIVED"), []), ((NARROW, "KILLED"), []),
                                     ((BROAD, "KILLED"), []), (("any", "INVALID"), [])])
    for r in an["final"].values():
        if r["op"] not in M.OPERATORS:
            continue
        key = ("any", "INVALID") if r["out"] == "INVALID" else (r["dir"], r["out"])
        if key in cells:
            cells[key].append(r)
    out = []
    for (d, o), rs in cells.items():
        for r in sorted(rs, key=lambda r: r["sha"])[:2]:
            out.append({"cell": f"{d}/{o}", "rule": r["rule"], "k": r["k"], "op": r["op"], "dir": r["dir"],
                        "site": r["site"], "sha": r["sha"], "out": r["out"], "counts": r["counts"], "expect": r["expect"]})
    return out


# ---- reporting -------------------------------------------------------------------------------------
def report(an, plan, meta, passes_seconds):
    final, P = an["final"], print
    P("=" * 78)
    P("PA-SIGMA-001: SigmaHQ regression-test job against one-point mutants (self-tested)")
    P("=" * 78)
    for k, v in meta.items():
        P(f"{k}: {v}")
    P(f"passes: {len(passes_seconds)} ({', '.join(f'{s:.0f} s' for s in passes_seconds)})")
    P("")
    P("FAILURES AND EXCLUSIONS FIRST")
    P(f"  G4 UNRESOLVED (outcome or counts differ between passes): {len(an['unresolved'])} {an['unresolved'][:20]}")
    P(f"  G1 IDENTITY not SURVIVED: {len(an['g1_fail'])} {an['g1_fail'][:20]}")
    P(f"  G2 rules excluded (IDENTITY/ROUNDTRIP not SURVIVED or NEVER_FIRE not KILLED): {len(an['excluded'])} "
      f"(max {MAX_EXCLUDED_RULES}) {an['excluded'][:20]}")
    for rid in an["excluded"][:20]:
        c = an["ctrl"][rid]
        P(f"      {rid}: IDENTITY {c['IDENTITY']['out']}, ROUNDTRIP {c['ROUNDTRIP']['out']}, NEVER_FIRE {c['NEVER_FIRE']['out']}")
    P(f"  G3 INVALID operator mutants: {len(an['invalid_ops'])} (max {MAX_INVALID})")
    reasons = collections.Counter(final[k].get("reason", "?") for k in an["invalid_ops"])
    for reason, n in reasons.most_common(10):
        P(f"      {n:5d}  {reason}")
    inv_ctrl = sorted((r["rule"], r["op"]) for r in final.values() if r["op"] in M.CONTROLS and r["out"] == "INVALID")
    P(f"  INVALID controls: {len(inv_ctrl)} {inv_ctrl[:10]}")
    P(f"  G5 direction-label violations (count moved against the label): {len(an['g5'])} {an['g5'][:20]}")
    P("")
    P("OUTCOMES BY OPERATOR AND DIRECTION (all rules; INVALID and UNRESOLVED shown)")
    tab = collections.Counter((r["op"], r["dir"], r["out"]) for r in final.values())
    for op in M.CONTROLS + M.OPERATORS:
        for d in ("CONTROL", BROAD, NARROW):
            row = {o: tab[(op, d, o)] for o in ("KILLED", "SURVIVED", "INVALID", "UNRESOLVED")}
            if sum(row.values()):
                P(f"  {op:10s} {d:10s} KILLED {row['KILLED']:5d}  SURVIVED {row['SURVIVED']:5d}  "
                  f"INVALID {row['INVALID']:4d}  UNRESOLVED {row['UNRESOLVED']:3d}")
    distinct = len({r["sha"] for r in final.values() if r["op"] in M.OPERATORS})
    n_ops = sum(1 for r in final.values() if r["op"] in M.OPERATORS)
    P(f"  operator mutants {n_ops}; distinct texts (sha256) {distinct}; included rules {len(an['included'])}")
    P("")
    P("SURVIVORS: CAN THE SAMPLE SEE THEM? (scored mutants of included rules)")
    for d in (BROAD, NARROW):
        surv = [r for r in an["scored"] if r["dir"] == d and r["out"] == "SURVIVED"]
        ch = sum(1 for r in surv if r["changed"])
        ov = sum(1 for r in surv if r["over"])
        P(f"  {d:10s} SURVIVED {len(surv):5d}: match count CHANGED {ch:5d}, unchanged {len(surv) - ch:5d}; "
          f"over-match warning {ov}")
    ns_b = [r for r in an["scored"] if r["op"] == "NEVER_SEL" and r["dir"] == BROAD]
    ns_b_rules = {r["rule"] for r in ns_b}
    ns_b_surv_rules = {r["rule"] for r in ns_b if r["out"] == "SURVIVED"}
    P(f"  NEVER_SEL BROADENING (an exclusion switched off): SURVIVED {sum(r['out'] == 'SURVIVED' for r in ns_b)} "
      f"of {len(ns_b)}; rules with such a survivor {len(ns_b_surv_rules)} of {len(ns_b_rules)}")
    d2_all, d2_464, n_464 = an["d2"]
    P(f"  D2: tests where IDENTITY matches every sample event: {d2_all} of 474; among the {n_464} tests whose sample "
      f"holds no more events than expected: {d2_464}")
    fr = []
    for rid in sorted(an["included"]):
        rs = [r for r in an["scored"] if r["rule"] == rid and r["dir"] == NARROW]
        if rs:
            fr.append(sum(r["out"] == "KILLED" for r in rs) / len(rs))
    fr.sort()
    if fr:
        q = lambda p: fr[min(len(fr) - 1, int(p * len(fr)))]  # noqa: E731
        P(f"  per-rule NARROWING kill fraction over {len(fr)} rules: min {fr[0]:.3f} q25 {q(.25):.3f} "
          f"median {q(.5):.3f} q75 {q(.75):.3f} max {fr[-1]:.3f}; rules with every narrowing mutant KILLED "
          f"{sum(1 for x in fr if x == 1.0)}; with none KILLED {sum(1 for x in fr if x == 0.0)}")
    P("")
    P("PREDICTIONS (registered in PREREG.md)")
    for pid, v in zip(PREDICTIONS, an["verdicts"]):
        P(f"  {pid}: {v}  ({an['detail'].get(pid, an['detail'].get('why', ''))})")
    if an["sens"] is not None:
        P(f"  sensitivity, G5 violators excluded (disclosed, not the registered scoring): P1-P4 {an['sens']}")
    held = sum(v == "HELD" for v in an["verdicts"])
    P(f"VERDICT {held} of {len(PREDICTIONS)} as registered")


def run_main(args):
    ctx = setup(args.sigma, args.evtx_checker, args.json_checker)
    plan = build_plan(ctx, sabotage=args.sabotage)
    events = {}
    for e in plan:
        for t in e["rule"]["tests"]:
            events[(e["rule"]["id"], t["path"])] = sample_events(t["path"], t.get("type"))
    meta = dict(ctx.meta, sabotage=args.sabotage, rules=len(plan), mutants=sum(len(e["mutants"]) for e in plan))
    passes, secs = [], []
    for i in range(PASSES):
        t0 = time.time()
        passes.append(census(ctx, plan))
        secs.append(time.time() - t0)
    an = analyse(plan, passes, events)
    digest = digest_of(an)
    report(an, plan, meta, secs)
    print(f"DIGEST {digest}")
    outcome = (tuple(an["verdicts"]), digest)
    if args.out and not args.sabotage:
        os.makedirs(args.out, exist_ok=True)
        _write_results(args.out, an, meta, digest)
    if args.look_diffs and not args.sabotage:
        _write_look_diffs(args.look_diffs, an, plan)
    gate_fail = bool(an["g1_fail"]) or len(an["excluded"]) > MAX_EXCLUDED_RULES or len(an["invalid_ops"]) > MAX_INVALID
    if gate_fail:
        print("GATE: FAIL")
        return 1
    print("GATE: PASS")
    if an["unresolved"]:
        print(f"UNRESOLVED mutants present ({len(an['unresolved'])}): the outcome cannot be pinned")
        return 1
    if RECORDED is None:
        print("RECORDED: not pinned yet")
        return 0
    if outcome != RECORDED:
        print(f"RECORDED differs: recorded {RECORDED}, this run {outcome}")
        return 1
    print("RECORDED: reproduced")
    return 0


def _write_results(out, an, meta, digest):
    mutants = sorted(an["final"].values(), key=lambda r: (r["rule"], r["k"]))
    head = {"study": "PA-SIGMA-001", "meta": meta, "digest": digest,
            "verdicts": dict(zip(PREDICTIONS, an["verdicts"])), "detail": an["detail"],
            "gates": {"G1_identity_not_survived": an["g1_fail"], "G2_excluded_rules": an["excluded"],
                      "G3_invalid_operator_mutants": [list(k) for k in an["invalid_ops"]],
                      "G4_unresolved": [list(k) for k in an["unresolved"]],
                      "G5_direction_violations": [list(k) for k in an["g5"]]},
            "d2": dict(zip(("identity_matches_every_event_all_tests", "same_among_tests_with_events_le_expected",
                            "tests_with_events_le_expected"), an["d2"]))}
    lines = [json.dumps(r, sort_keys=True, separators=(",", ":")) for r in mutants]
    with open(os.path.join(out, "results.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(head, sort_keys=True, indent=1)[:-2] + ',\n "mutants": [\n' + ",\n".join(lines) + "\n ]\n}\n")
    with open(os.path.join(out, "look_sample.json"), "w", encoding="utf-8") as f:
        json.dump(look_sample(an), f, sort_keys=True, indent=1)
        f.write("\n")
    for name in ("results.json", "look_sample.json"):
        print(f"wrote {name} sha256 {sha256_file(os.path.join(out, name))}")


def _write_look_diffs(path, an, plan):
    """Diffs of the look sample against ROUNDTRIP, for a person to read. Not committed (rule text)."""
    texts = {(e["rule"]["id"], m["k"]): m["text"] for e in plan for m in e["mutants"]}
    titles = {e["rule"]["id"]: e["rule"]["path"] for e in plan}
    chunks = []
    for s in look_sample(an):
        base = texts[(s["rule"], 1)]
        diff = difflib.unified_diff(base.splitlines(), texts[(s["rule"], s["k"])].splitlines(),
                                    "ROUNDTRIP", f"{s['op']} {s['site']}", lineterm="", n=2)
        chunks.append(f"### {s['cell']}: {s['rule']} ({titles[s['rule']]}) {s['op']} {s['dir']} at {s['site']} -> "
                      f"{s['out']}, counts {s['counts']}, expected {s['expect']}\n```diff\n" + "\n".join(diff) + "\n```\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# PA-SIGMA-001 look sample (SigmaHQ rules, Detection Rule License 1.1; not committed)\n\n" + "\n".join(chunks))
    print(f"wrote look-sample diffs to {path}")


# ---- self-test (M3, C-BUILD) -----------------------------------------------------------------------
TOY = """title: toy
id: 00000000-0000-0000-0000-000000000001
logsource:
    product: windows
    category: process_creation
detection:
    selection:
        Image|endswith:
            - '\\\\a.exe'
            - '\\\\b.exe'
        CommandLine|contains|all:
            - 'x'
            - 'y'
    sel2:
        - Image|endswith: '\\\\c.exe'
        - OriginalFileName:
            - 'c.exe'
            - 'd.exe'
    filter:
        ParentImage|endswith:
            - '\\\\p.exe'
            - '\\\\q.exe'
        User|contains|all:
            - 'u'
            - 'v'
    keywords:
        - 'k1'
        - 'k2'
    condition: selection and sel2 and not filter and keywords
level: high
"""


def selftest(args):
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    print("[1] polarity of selections in conditions")
    P_ = M.polarity
    check("plain selection is positive", P_("selection", ["selection"]) == {"selection": {1}})
    check("'and not' makes an exclusion", P_("selection and not filter", ["selection", "filter"]) == {"selection": {1}, "filter": {-1}})
    check("nested not flips twice", P_("not (a or not b)", ["a", "b"]) == {"a": {-1}, "b": {1}})
    check("1 of pattern, both polarities split", P_("1 of selection_* and not 1 of filter_*", ["selection_a", "selection_b", "filter_x"])
          == {"selection_a": {1}, "selection_b": {1}, "filter_x": {-1}})
    check("'them' skips names starting with _", P_("all of them", ["a", "_b"]) == {"a": {1}})
    for cond, names, why in (("a | count() > 5", ["a"], "aggregation"), (["a", "b"], ["a", "b"], "list"),
                             ("unknown", ["a"], "unknown selection"), ("(a", ["a"], "unbalanced"),
                             ("1 of nomatch_*", ["a"], "matches no selection"), ("a and", ["a"], "ends early")):
        try:
            P_(cond, names)
            check(f"skip: {why}", False)
        except M.Skip as e:
            check(f"skip: {why} ({e})", why.split()[0] in str(e) or why in str(e))
    muts, why = M.enumerate_mutants(TOY.replace("condition: selection and sel2 and not filter and keywords",
                                                "condition: selection and not selection"))
    check("a selection with both polarities is skipped", muts == [] and "both polarities" in (why or ""))

    print("[2] directions on a hand-written rule")
    muts, why = M.enumerate_mutants(TOY)
    check("toy rule is not skipped", why is None)
    d = {(m["op"], m["site"]): m["direction"] for m in muts}
    want = {
        ("DROP_VALUE", "selection/0/Image|endswith[0]"): NARROW,
        ("DROP_VALUE", "selection/0/CommandLine|contains|all[1]"): BROAD,
        ("DROP_VALUE", "sel2/1/OriginalFileName[0]"): NARROW,
        ("DROP_VALUE", "filter/0/ParentImage|endswith[1]"): BROAD,
        ("DROP_VALUE", "filter/0/User|contains|all[0]"): NARROW,
        ("DROP_VALUE", "keywords[1]"): NARROW,
        ("DROP_FIELD", "selection/0/Image|endswith"): BROAD,
        ("DROP_FIELD", "filter/0/User|contains|all"): NARROW,
        ("NEVER_SEL", "selection"): NARROW,
        ("NEVER_SEL", "sel2"): NARROW,
        ("NEVER_SEL", "filter"): BROAD,
        ("NEVER_SEL", "keywords"): NARROW,
    }
    for key, direction in want.items():
        check(f"{key[0]} {key[1]} is {direction}", d.get(key) == direction)
    check("controls come first", [m["op"] for m in muts[:3]] == ["IDENTITY", "ROUNDTRIP", "NEVER_FIRE"])
    check("IDENTITY is the input text", muts[0]["text"] == TOY)
    import yaml
    nf = yaml.safe_load(muts[2]["text"])["detection"]
    check("NEVER_FIRE ANDs a never-matching selection", nf["condition"].endswith(") and pa_sigma_001_never")
          and list(nf["pa_sigma_001_never"].values()) == [M.NEVER])
    ns = yaml.safe_load([m for m in muts if m["op"] == "NEVER_SEL" and m["site"] == "sel2"][0]["text"])["detection"]["sel2"]
    check("NEVER_SEL on a list of maps puts the never value in every map", all(M.NEVER in m.values() for m in ns))
    nk = yaml.safe_load([m for m in muts if m["op"] == "NEVER_SEL" and m["site"] == "keywords"][0]["text"])["detection"]["keywords"]
    check("NEVER_SEL on a keyword list leaves only the never value", nk == [M.NEVER])
    dv = yaml.safe_load([m for m in muts if m["site"] == "selection/0/Image|endswith[0]"][0]["text"])["detection"]["selection"]
    check("DROP_VALUE removes exactly that value", dv["Image|endswith"] == ["\\\\b.exe"] and dv["CommandLine|contains|all"] == ["x", "y"])
    long_rule = TOY.replace("        Image|endswith:\n            - '\\\\a.exe'\n            - '\\\\b.exe'\n",
                            "        Image|endswith:\n" + "".join(f"            - 'v{i}'\n" for i in range(30)))
    lm, _ = M.enumerate_mutants(long_rule)
    check("cap: at most 25 DROP_VALUE mutants per rule", sum(m["op"] == "DROP_VALUE" for m in lm) == M.CAP)
    dup_rule = TOY.replace("            - '\\\\b.exe'\n        CommandLine", "            - '\\\\a.exe'\n        CommandLine")
    dm, _ = M.enumerate_mutants(dup_rule)
    check("identical mutant texts are kept once", sum(m["site"].startswith("selection/0/Image|endswith[") for m in dm) == 1)

    print("[3] scoring boundaries and gates (registered thresholds)")
    def mk(op, d, out, rule="r"):
        return {"op": op, "dir": d, "out": out, "rule": rule}
    base = [mk("DROP_VALUE", NARROW, "SURVIVED"), mk("DROP_VALUE", NARROW, "KILLED")]
    v, _ = score(base + [mk("NEVER_SEL", NARROW, "KILLED")], [], [], [])
    check("P2 at exactly half is REFUTED", v[1] == "REFUTED")
    v, _ = score([mk("NEVER_SEL", NARROW, "SURVIVED")] + [mk("NEVER_SEL", NARROW, "KILLED")] * 9, [], [], [])
    check("P4 at exactly 10% is HELD", v[3] == "HELD")
    v, _ = score([mk("NEVER_SEL", NARROW, "SURVIVED")] + [mk("NEVER_SEL", NARROW, "KILLED")] * 10, [], [], [])
    check("P4 below 10% is REFUTED", v[3] == "REFUTED")
    v, _ = score([mk("DROP_FIELD", BROAD, "KILLED")], [], [], [])
    check("P1 with one BROADENING KILLED is REFUTED", v[0] == "REFUTED")
    v, _ = score([mk("NEVER_SEL", NARROW, "KILLED", "a"), mk("NEVER_SEL", NARROW, "SURVIVED", "b")], [], [], [])
    check("P3 at exactly half of rules is REFUTED", v[2] == "REFUTED")
    v, _ = score(base, [], ["x"] * (MAX_EXCLUDED_RULES + 1), [])
    check("G2: 24 excluded rules -> COULD NOT RUN AS REGISTERED", v == ("COULD NOT RUN AS REGISTERED",) * 4)
    v, _ = score(base, [], ["x"] * MAX_EXCLUDED_RULES, [])
    check("G2: 23 excluded rules still scores", v[1] in ("HELD", "REFUTED"))
    v, _ = score(base, [], [], [("x", 1)] * (MAX_INVALID + 1))
    check("G3: 276 INVALID -> COULD NOT RUN AS REGISTERED", v == ("COULD NOT RUN AS REGISTERED",) * 4)
    v, _ = score(base, ["r"], [], [])
    check("G1 failure -> IMPLEMENTATION_ERROR", v == ("IMPLEMENTATION_ERROR",) * 4)
    mm = PRECHECK_RX.search("could not add rules from /w/round001_x/abc-1.yml: syntax error in condition element of rule T: x")
    check("pre-check message parsed to the file", bool(mm) and mm.group(1) == "/w/round001_x/abc-1.yml")

    print("[4] the real runner, checker and json path on three rules (needs the registered environment)")
    try:
        ctx = setup(args.sigma, args.evtx_checker, args.json_checker)
        rules, _, _ = ctx.runner.find_rules_with_tests(RULE_PATHS)
        ids = sorted(r["id"] for r in rules)
        pick = {ids[0], ids[1], "7dbbcac2-57a0-45ac-b306-ff30a8bd2981"}
        plan = build_plan(ctx, only=pick)
        check("three rules planned, one with a json test", len(plan) == 3 and any(len(e["rule"]["tests"]) == 2 for e in plan))
        # keep the controls and two operator mutants per rule, to stay fast
        for e in plan:
            e["mutants"] = e["mutants"][:5]
        recs = census(ctx, plan)
        for e in plan:
            rid = e["rule"]["id"]
            check(f"{rid[:8]} IDENTITY SURVIVED", recs[(rid, 0)]["out"] == "SURVIVED")
            check(f"{rid[:8]} ROUNDTRIP SURVIVED", recs[(rid, 1)]["out"] == "SURVIVED")
            check(f"{rid[:8]} NEVER_FIRE KILLED", recs[(rid, 2)]["out"] == "KILLED")
        # an invalid mutant is set INVALID by the pre-check, and its round goes on
        e0 = copy.deepcopy(plan[0])
        bad = re.sub(r"(\n[ \t]+condition:[ \t]*)", r"\1pa_undefined_selection and ", e0["mutants"][0]["text"], count=1)
        check("the broken copy differs from the rule", bad != e0["mutants"][0]["text"])
        e0["mutants"] = [dict(e0["mutants"][0], k=0, text=bad, sha256=sha256_bytes(bad.encode()))]
        recs2 = census(ctx, [e0])
        check("a broken rule is INVALID, not KILLED", recs2[(e0["rule"]["id"], 0)]["out"] == "INVALID")
        # staged bytes that differ from the mutant abort the run
        ctx.taps.begin({})
        try:
            ctx.taps._check(os.path.join(ctx.sigma, plan[0]["rule"]["path"]))
            check("unstaged file aborts", False)
        except Abort:
            check("a file the harness did not stage aborts", True)
        finally:
            ctx.taps.end()
        p = os.path.join(ctx.work, "probe.yml")
        with open(p, "w") as f:
            f.write("x")
        ctx.taps.begin({p: "0" * 64})
        try:
            ctx.taps._check(p)
            check("changed bytes abort", False)
        except Abort:
            check("staged bytes that differ from the mutant abort", True)
        finally:
            ctx.taps.end()
        # sabotage: the pipeline runs the original while believing it runs the mutants
        sab = build_plan(ctx, sabotage=True, only=pick)
        for e in sab:
            e["mutants"] = e["mutants"][:3]
        recs3 = census(ctx, sab)
        check("under sabotage NEVER_FIRE SURVIVES (so G2 would fail)",
              all(recs3[(e["rule"]["id"], 2)]["out"] == "SURVIVED" for e in sab))
        shutil.rmtree(ctx.work, ignore_errors=True)
    except Abort as e:
        check(f"real-runner checks could not run: {e}", False)
    print(f"SELFTEST: {'PASS' if not fails else 'FAIL'} ({len(fails)} failure(s))")
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sigma")
    ap.add_argument("evtx_checker")
    ap.add_argument("json_checker")
    ap.add_argument("--out", help="directory for results.json and look_sample.json")
    ap.add_argument("--look-diffs", help="file for the look sample's diffs (rule text; keep it out of the repository)")
    ap.add_argument("--sabotage", action="store_true", help="run the original rule in place of every mutant; must exit 1")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.selftest:
            return selftest(args)
        return run_main(args)
    except (Abort, subprocess.TimeoutExpired) as e:
        print(f"ABORT (fail closed, no outcome): {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
