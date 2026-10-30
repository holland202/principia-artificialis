#!/usr/bin/env python3
"""PA-SIGMA-003 staging and the three checks. Shared by feasibility.py and the harness. Standard library only.

A round is a hard-linked copy of the SigmaHQ checkout in which at most one file per rule is replaced (unlink,
then write, so the checkout itself is never written through a hard link). Each check runs from the round's root
the way SigmaHQ's sigma-test.yml workflow runs it:

  SC  sigma check --fail-on-error --fail-on-issues --validation-config tests/sigma_cli_conf.yml rules*
      (job sigma-check), through sigma_offline.py (stand-in S1: MITRE data from local files)
  TR  python tests/test_rules.py        (job test-sigma-legacy), through unittest_full.py (deviation D2)
  TL  python tests/test_logsource.py    (job test-sigma-logsource), through unittest_full.py (deviation D2)

Attribution. A staged file is FLAGGED by a check when the check exits non-zero and the file's path occurs:
  SC: on an output line (sigma-cli prints each issue and error with the rule's absolute path);
  TR, TL: inside a FAIL or ERROR block (the assertion message lists the faulty files; maxDiff is off).
A flag whose only reasons are cross-rule checks (another rule's id, title, file name or detection) can come from
two staged files colliding with each other, so the harness re-runs such an item alone and keeps that result.
"""
import concurrent.futures
import glob
import os
import re
import shutil
import subprocess
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKS = ("SC", "TR", "TL")
CROSS_RULE = {
    "SC": {"IdentifierCollisionIssue", "DuplicateTitleIssue", "DuplicateFilenameIssue"},
    "TR": {"test_duplicate_detections"},
    "TL": set(),
}
EXPECTED_TESTS = {"TR": 11, "TL": 3}
_BLOCK = re.compile(r"^(FAIL|ERROR): (\w+)", re.M)
_ISSUE = re.compile(r"issue=(\w+)")


class Tools:
    def __init__(self, sigma, py3, attack, d3fend):
        self.sigma = os.path.abspath(sigma)
        self.py3 = py3
        self.attack = os.path.abspath(attack)
        self.d3fend = os.path.abspath(d3fend)
        self.offline = os.path.join(HERE, "sigma_offline.py")
        self.unittest_full = os.path.join(HERE, "unittest_full.py")

    def commands(self, root):
        rules = sorted(os.path.basename(d) for d in glob.glob(os.path.join(root, "rules*")))
        return {
            "SC": [self.py3, "-I", self.offline, self.attack, self.d3fend, "check", "--fail-on-error",
                   "--fail-on-issues", "--validation-config", "tests/sigma_cli_conf.yml"] + rules,
            "TR": [self.py3, "-I", self.unittest_full, "tests/test_rules.py"],
            "TL": [self.py3, "-I", self.unittest_full, "tests/test_logsource.py"],
        }


def make_tree(sigma, parent):
    root = tempfile.mkdtemp(prefix="round-", dir=parent)
    for entry in sorted(os.listdir(sigma)):
        if entry == ".git":
            continue
        subprocess.run(["cp", "-al", os.path.join(sigma, entry), root], check=True)
    return root


def stage(root, rel, text):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        raise RuntimeError(f"staging target is not a file in the checkout: {rel}")
    os.unlink(path)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def completed(check, code, out):
    """The check ran to its end: a known exit code and its closing lines (gate G8)."""
    if code not in (0, 1):
        return False
    if check == "SC":
        return "=== Summary ===" in out
    m = re.search(r"^Ran (\d+) tests? in ", out, re.M)
    return bool(m) and int(m.group(1)) == EXPECTED_TESTS[check]


def attribute(check, root, out, rels):
    """{rel: set of reasons} for the staged paths this check's output names."""
    hits = {}
    if check == "SC":
        lines = out.splitlines()
        for rel in rels:
            absolute = os.path.join(root, rel)
            pat = re.compile(re.escape(absolute) + r"(?![\w.-])")
            for line in lines:
                if pat.search(line):
                    m = _ISSUE.search(line)
                    hits.setdefault(rel, set()).add(m.group(1) if m else "error-line")
        return hits
    blocks = []
    marks = list(_BLOCK.finditer(out))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(out)
        blocks.append((m.group(2), out[m.start():end]))
    for rel in rels:
        pat = re.compile(r"(?<![\w./-])" + re.escape(rel) + r"(?![\w.-])")
        for name, text in blocks:
            if pat.search(text):
                hits.setdefault(rel, set()).add(name)
    return hits


def run_round(tools, parent, staged, timeout=1800):
    """staged: {rel: text}. Returns {check: {"code", "seconds", "completed", "flags": {rel: [reasons]}}}."""
    root = make_tree(tools.sigma, parent)
    try:
        for rel, text in sorted(staged.items()):
            stage(root, rel, text)
        out = {}
        for check, cmd in tools.commands(root).items():
            t0 = time.time()
            p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=timeout,
                               env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", "/root"),
                                    "LANG": "C.UTF-8", "PYTHONHASHSEED": "0", "NO_COLOR": "1"})
            text = p.stdout + p.stderr
            flags = attribute(check, root, text, list(staged)) if p.returncode != 0 else {}
            out[check] = {"code": p.returncode, "seconds": round(time.time() - t0, 1),
                          "completed": completed(check, p.returncode, text),
                          "flags": {rel: sorted(r) for rel, r in sorted(flags.items())},
                          "tail": text[-400:] if not completed(check, p.returncode, text) else ""}
        return out
    finally:
        shutil.rmtree(root, ignore_errors=True)


def run_rounds(tools, parent, rounds, workers=2):
    """rounds: list of {rel: text}. Returns results in the same order."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda st: run_round(tools, parent, st), rounds))


def schedule(items_by_rel):
    """items_by_rel: {rel: [item, ...]} in a fixed order. Round j holds the j-th item of every rule that has one."""
    n = max((len(v) for v in items_by_rel.values()), default=0)
    return [{rel: items[j] for rel, items in sorted(items_by_rel.items()) if j < len(items)} for j in range(n)]
