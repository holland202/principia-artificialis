#!/usr/bin/env python3
"""score.py - NOTE076-X1 scorer (REGISTRATION.md). Stdlib only.

  score.py vectors --sv-root R -- CMD ...    every vector, every mismatch, counted by id class (L, S, X)
  score.py probes  --sv-root R -- CMD ...    the six registered probes, one process per probe
  score.py compare REF.txt ARM.txt           AGREE or DIFFER on each probe of two `probes` outputs

Fails closed (C-BUILD): a probe whose process exits non-zero, prints no line, or prints a line that is not a
decision for that probe is CRASH, never a decision. `vectors` uses the pinned checkout's own run_command, so a port
that cannot answer every vector is COULD NOT RUN (exit 2), as in gate_contract.py.
Exit: vectors 0 conforms, 1 differs, 2 could not run | probes 0 | compare 0 all agree, 1 any differ, 2 bad input.
"""
import argparse
import copy
import importlib.util
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True

# REGISTRATION.md, "Probes, fixed now": (id, capability.min_evidence_quality, record.evidence_quality)
PROBES = [
    ("Q1", 10 ** 400, 0.2),
    ("Q2", -(10 ** 400), 0.2),
    ("Q3", 2 ** 1024, 0.2),
    ("Q4", 10 ** 308, 0.2),
    ("Q5", 10 ** 400, 10 ** 400),
    ("Q6", 0.5, -(10 ** 400)),
]


def load_gct(sv_root):
    path = os.path.join(os.path.abspath(sv_root), "tools", "gate_contract.py")
    spec = importlib.util.spec_from_file_location("gate_contract", path)
    gct = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gct)
    return gct


def probe_inputs(vectors):
    base = next((v["input"] for v in vectors if v["expect"]["decision"] == "ALLOW"), None)
    if base is None:
        raise SystemExit("no ALLOW vector")
    out = []
    for pid, floor, quality in PROBES:
        inp = copy.deepcopy(base)
        inp["record"]["evidence_quality"] = quality
        inp["capability"]["min_evidence_quality"] = floor
        out.append((pid, inp))
    return out


def run_one(cmd, pid, inp, canon):
    line = canon({"id": pid, "input": inp}) + "\n"
    try:
        p = subprocess.run(cmd, input=line, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"outcome": "CRASH", "detail": f"{type(exc).__name__}: {exc}"}
    lines = [s for s in p.stdout.splitlines() if s.strip()]
    err = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""
    if p.returncode != 0 or len(lines) != 1:
        return {"outcome": "CRASH", "detail": f"exit {p.returncode}, {len(lines)} lines; stderr: {err}"}
    try:
        o = json.loads(lines[0])
    except ValueError:
        return {"outcome": "CRASH", "detail": f"not JSON: {lines[0][:120]!r}"}
    ok = (isinstance(o, dict) and o.get("id") == pid and isinstance(o.get("decision"), str)
          and isinstance(o.get("reasons"), list) and all(isinstance(r, str) for r in o["reasons"]))
    if not ok:
        return {"outcome": "CRASH", "detail": f"not a decision line: {lines[0][:120]!r}"}
    return {"outcome": [o["decision"], o["reasons"]]}


def cmd_probes(args):
    gct = load_gct(args.sv_root)
    vectors = gct.read_vectors()
    for pid, inp in probe_inputs(vectors):
        r = run_one(args.cmd, pid, inp, gct.canon)
        print(f"PROBE {pid} " + json.dumps(r, sort_keys=True, ensure_ascii=False))
    return 0


def cmd_vectors(args):
    gct = load_gct(args.sv_root)
    vectors = gct.read_vectors()
    rows = gct.run_command(args.cmd, vectors)  # exits 2 (COULD NOT RUN) itself
    expected = gct.conformance_digest([(v["id"], v["expect"]["decision"], v["expect"]["reasons"]) for v in vectors])
    got = gct.conformance_digest(rows)
    counts = {"L": 0, "S": 0, "X": 0, "other": 0}
    bad = []
    for v, (rid, d, reasons) in zip(vectors, rows):
        if rid != v["id"] or [d, list(reasons)] != [v["expect"]["decision"], v["expect"]["reasons"]]:
            cls = v["id"][0] if v["id"][:1] in ("L", "S", "X") else "other"
            counts[cls] += 1
            bad.append((v, d, reasons))
    for v, d, reasons in bad:
        if v["id"].startswith("X"):
            print(f"  MISMATCH {v['id']}: expected {v['expect']['decision']} {v['expect']['reasons']}, got {d} {list(reasons)}")
    print(f"vectors {len(vectors)} | mismatches L={counts['L']} S={counts['S']} X={counts['X']} other={counts['other']}")
    print(f"conformance digest {got}  (expected {expected})")
    verdict = "CONFORMS" if not bad and got == expected else f"{len(bad)} of {len(vectors)} vectors differ"
    print(f"VERDICT  {verdict}")
    return 0 if verdict == "CONFORMS" else 1


def read_probe_file(path):
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("PROBE "):
                _, pid, rest = line.split(" ", 2)
                out[pid] = json.loads(rest)
    if sorted(out) != sorted(p[0] for p in PROBES):
        raise ValueError(f"{path}: probes {sorted(out)}")
    return out


def cmd_compare(args):
    try:
        ref, arm = read_probe_file(args.ref), read_probe_file(args.arm)
    except (OSError, ValueError) as exc:
        print(f"BAD INPUT: {exc}")
        return 2
    differ = 0
    for pid, _, _ in PROBES:
        a, b = ref[pid]["outcome"], arm[pid]["outcome"]
        # REGISTRATION.md: the outcome is the (decision, reasons) pair or CRASH, compared for identity.
        same = a == b
        differ += not same
        print(f"{pid} {'AGREE ' if same else 'DIFFER'} ref={json.dumps(a)} arm={json.dumps(b)}")
    print(f"COMPARE {args.ref} vs {args.arm}: {6 - differ} agree, {differ} differ")
    return 0 if differ == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    for m in ("vectors", "probes"):
        s = sub.add_parser(m)
        s.add_argument("--sv-root", required=True)
        s.add_argument("cmd", nargs=argparse.REMAINDER)
    c = sub.add_parser("compare")
    c.add_argument("ref")
    c.add_argument("arm")
    args = ap.parse_args(argv)
    if args.mode in ("vectors", "probes"):
        if args.cmd[:1] == ["--"]:
            args.cmd = args.cmd[1:]
        if not args.cmd:
            ap.error("no command after --")
        return cmd_vectors(args) if args.mode == "vectors" else cmd_probes(args)
    return cmd_compare(args)


if __name__ == "__main__":
    sys.exit(main())
