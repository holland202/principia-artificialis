#!/usr/bin/env python3
"""QFI-001 public case runner (FAST-1 item 3). Runs every case in a JSON-lines file against qfi_ref.qfi_split_ex.

Each line: {"id", "source", "rho": {"re": [[..]], "im": [[..]]?}, "drho": {...}, "expect": {F_Q?, F_C?, F_R?,
split_resolved?, bookkeeping?}, "tol"?: 1e-10, "why"?}. Only the keys present in "expect" are checked; "bookkeeping":
true requires |F_Q - F_C - F_R| < tol. Public cases only: blind material never goes in these files.
A case with zero active assertions (empty "expect", or only "bookkeeping": false) or with an unknown expect key
fails (A16.1, qfi001/chatgpt/016): it could never disagree with its result, so it is not evidence.
Author: Claude (Anthropic, Opus 5.5). NumPy only. Exit 1 if any case fails or no case ran (fail-closed).

Usage:  python experiments/qfi_001/run_cases.py experiments/qfi_001/cases/public.jsonl [--impl module.path]
"""
import argparse
import importlib
import json
import os
import sys

import numpy as np


KNOWN = {"F_Q", "F_C", "F_R", "split_resolved", "bookkeeping"}


def mat(m):
    re = np.array(m["re"], dtype=float)
    im = np.array(m["im"], dtype=float) if "im" in m else np.zeros_like(re)
    return re + 1j * im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases")
    ap.add_argument("--impl", default="qfi_ref", help="module exposing qfi_split_ex(rho, drho)")
    a = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    impl = importlib.import_module(a.impl)
    n = bad = 0
    with open(a.cases) as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            r = impl.qfi_split_ex(mat(c["rho"]), mat(c["drho"]))
            tol = c.get("tol", 1e-10)
            fails = []
            # A16.1 (qfi001/chatgpt/016): a case whose result could never disagree with its expectation is not
            # evidence. Active = a key that is actually compared; "bookkeeping": false compares nothing.
            unknown = sorted(set(c["expect"]) - KNOWN)
            active = [k for k, v in c["expect"].items() if k in KNOWN and not (k == "bookkeeping" and not v)]
            if unknown:
                fails.append(f"unknown expect keys {unknown} (would never be checked)")
            if not active:
                fails.append("zero active assertions (result could never fail)")
            for k, v in c["expect"].items():
                if k in unknown:
                    continue
                if k == "bookkeeping":
                    res = abs(r["F_Q"] - r["F_C"] - r["F_R"])
                    if v and not res < tol:
                        fails.append(f"bookkeeping residual {res:.3e}")
                elif k == "split_resolved":
                    if bool(r[k]) is not v:
                        fails.append(f"split_resolved {r[k]} != {v}")
                elif not (np.isfinite(r[k]) and abs(r[k] - v) < tol):
                    fails.append(f"{k} {r[k]!r} != {v!r}")
            n += 1
            bad += bool(fails)
            print(f"{c['id']} ({c['source']}): F_Q={r['F_Q']:.12g} F_C={r['F_C']:.12g} F_R={r['F_R']:.12g} "
                  f"split_resolved={r['split_resolved']} -> {'FAIL ' + '; '.join(fails) if fails else 'PASS'}")
    print(f"cases {n}, failed {bad}, impl {a.impl}, numpy {np.__version__}")
    print(f"VERDICT {'PASS' if n and not bad else 'FAIL'}")
    return 0 if n and not bad else 1


if __name__ == "__main__":
    sys.exit(main())
