#!/usr/bin/env python3
"""note080 driver: compensating decimal exponents across number parsers. Registered with note080 before any run.

  python3 experiments/note080_crossparse/run.py build WORK          compile/build the non-Python observers into WORK
  python3 experiments/note080_crossparse/run.py run WORK OUT [--sabotage]

Environment: PYVENV = a Python with the third-party packages (orjson ujson simplejson python-rapidjson pysimdjson
msgspec yyjson duckdb); SQLITE_OBSERVER = the verified SQLite 3.54.1 observer from experiments/pa_json_002_claude.
Every observer prints <name>\t<index>\t<OK|ERR|EXACT|OTHER>\t<value>. The driver computes the correctly rounded
binary64 value of each token from its exact rational value, classifies every result, and prints the verdicts.
Exit codes for run: 0 = scored; 1 = a classifier control failed (or --sabotage was caught); 2 = cannot run.
"""
import json, os, re, struct, subprocess, sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
OBS = os.path.join(HERE, "observers")
sys.set_int_max_str_digits(0)
TOK = re.compile(r"^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$")
SIZES = [330, 1000, 2000, 10000, 20000, 100000]


def tokens():
    """(label, kind, token). kind: control | witness. Every witness's exact value is stated by its construction."""
    t = [("c_1e0", "control", "1e0"), ("c_0.1", "control", "0.1"), ("c_1.5e10", "control", "1.5e10")]
    for n in SIZES:
        t.append((f"int_pad_{n}", "witness", "1" + "0" * n + "e-" + str(n)))          # exactly 1
        t.append((f"frac_pad_{n}", "witness", "0." + "0" * n + "1e" + str(n + 1)))    # exactly 1
    t.append(("x3_42", "witness", "42" + "0" * 10000 + "e-100000"))                  # 42e-90000, rounds to +0
    t.append(("x2_tenth", "witness", "0." + "0" * 10000 + "1e100000"))               # 1e89999, rounds to +inf
    return t


def exact(tok):
    sign, ip, fp, ex = TOK.match(tok).groups()
    fp, ex = fp or "", int(ex or 0)
    num, scale = int(ip + fp), ex - len(fp)
    f = Fraction(num * 10 ** scale) if scale >= 0 else Fraction(num, 10 ** -scale)
    return -f if sign else f


def rounded_bits(f):
    try:
        d = float(f)
    except OverflowError:
        d = float("inf") if f > 0 else float("-inf")
    return struct.unpack(">Q", struct.pack(">d", d))[0]


def build(work):
    os.makedirs(work, exist_ok=True)
    steps = [
        ["gcc", "-O2", os.path.join(OBS, "obs_strtod.c"), "-o", os.path.join(work, "obs_strtod")],
        ["go", "build", "-o", os.path.join(work, "obs_go"), os.path.join(OBS, "obs_go.go")],
        ["javac", "-d", work, os.path.join(OBS, "Obs.java")],
        ["cargo", "build", "--release", "--quiet", "--manifest-path", os.path.join(OBS, "obs_rust", "Cargo.toml"),
         "--target-dir", os.path.join(work, "rust-target")],
    ]
    for s in steps:
        p = subprocess.run(s, capture_output=True, text=True)
        if p.returncode != 0:
            sys.exit(f"build failed: {' '.join(s[:2])}\n{p.stderr[-1500:]}")
    print("built: obs_strtod, obs_go, Obs.class, obs_rust")


def observers(work, path):
    py = os.environ.get("PYVENV")
    sq = os.environ.get("SQLITE_OBSERVER")
    if not py or not sq:
        sys.exit("set PYVENV and SQLITE_OBSERVER")
    return [
        [py, os.path.join(OBS, "obs_python.py"), path],
        ["node", os.path.join(OBS, "obs_node.js"), path],
        [os.path.join(work, "obs_strtod"), path],
        [os.path.join(work, "obs_go"), path],
        [os.path.join(work, "rust-target", "release", "obs_rust"), path],
        ["java", "-cp", work, "Obs", path],
        ["bash", os.path.join(OBS, "obs_scripts.sh"), path],
        ["SQLITE", sq, path],
    ]


def sqlite_rows(observer, path, n):
    """Adapt the PA-JSON-002 observer (index, valid, json rc/type/bits, cast rc/type/bits) to this format."""
    p = subprocess.run([observer, path], capture_output=True, text=True)
    lines = p.stdout.splitlines()
    out = [f"#versions\t{json.dumps({'sqlite-observer': lines[0][1:].split(chr(9))[0]})}"]
    for row in lines[1:]:
        f = row.split("\t")
        i = f[0]
        out.append(f"sqlite-3.54.1-json\t{i}\t" + (f"OK\t{f[4]}" if f[1] == "1" and f[2] == "100" and
                                                    not f[4].endswith("!notfloat") else "ERR\tinvalid-or-error"))
        out.append(f"sqlite-3.54.1-cast\t{i}\t" + (f"OK\t{f[7]}" if f[5] == "100" and not f[7].endswith("!notfloat")
                                                    else "ERR\terror"))
    return out


def classify(status, value, ref, f):
    if status == "ERR":
        return "ERROR"
    if status == "OK":
        return "CORRECT" if int(value, 16) == ref else "WRONG"
    if status == "EXACT":
        return "CORRECT" if Fraction(value) == f else "WRONG"
    return "WRONG"   # a non-numeric result for a numeric token


def run(work, out, sabotage):
    os.makedirs(out, exist_ok=True)
    toks = tokens()
    path = os.path.join(out, "tokens.txt")
    with open(path, "w", encoding="ascii") as fh:
        fh.write("".join(t + "\n" for _, _, t in toks))
    lines, versions = [], {}
    for cmd in observers(work, path):
        if cmd[0] == "SQLITE":
            got = sqlite_rows(cmd[1], cmd[2], len(toks))
        else:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            if p.returncode != 0:
                sys.exit(f"observer failed: {cmd[:2]} exit {p.returncode}\n{p.stderr[-800:]}: COULD NOT RUN")
            got = p.stdout.splitlines()
        for ln in got:
            if ln.startswith("#versions\t"):
                versions.update(json.loads(ln.split("\t", 1)[1]))
            elif ln.strip():
                lines.append(ln)
    os.remove(path)
    refs = [(exact(t), None) for _, _, t in toks]
    refs = [(f, rounded_bits(f)) for f, _ in refs]
    res = {}
    for ln in lines:
        name, i, status, value = ln.split("\t", 3)
        i = int(i)
        if sabotage and name == "python-json" and i == 0:      # planted: one wrong bit on 1e0
            status, value = "OK", f"{refs[0][1] ^ 1:016x}"
        res.setdefault(name, {})[toks[i][0]] = {"status": status, "value": value,
                                                "class": classify(status, value, refs[i][1], refs[i][0])}
    labels = [lab for lab, _, _ in toks]
    complete = all(set(v) == set(labels) for v in res.values())

    # Classifier controls: planted wrong bits and a planted error must be classified correctly.
    f1, b1 = refs[0]
    k = {"K1_wrong_bit_is_WRONG": classify("OK", f"{b1 ^ 1:016x}", b1, f1) == "WRONG",
         "K2_error_is_ERROR": classify("ERR", "x", b1, f1) == "ERROR",
         "K3_exact_int_is_CORRECT": classify("EXACT", "1", b1, f1) == "CORRECT",
         "K4_every_observer_answered_every_token": complete,
         "K5_known_good_correct_on_controls": all(res[o][c]["class"] == "CORRECT" for o in
                                                  ("python-json", "node-JSON.parse", "glibc-strtod")
                                                  for c in ("c_1e0", "c_0.1", "c_1.5e10"))}
    witnesses = [lab for lab, kind, _ in toks if kind == "witness"]
    controls = [lab for lab, kind, _ in toks if kind == "control"]
    # An observer that is not exact on the three plain controls is INVALID (likely a harness or API error): it is
    # listed, and excluded from P2 and P3, so a harness mistake cannot pass for a parser's behaviour.
    invalid = sorted(o for o in res if any(res[o][c]["class"] != "CORRECT" for c in controls))
    sqlite = [o for o in res if o.startswith("sqlite")]
    sqlite_bad = ["int_pad_100000", "frac_pad_100000", "x3_42", "x2_tenth"]
    known_good = ["python-json", "node-JSON.parse", "glibc-strtod", "go-strconv", "java-Double.parseDouble"]
    others = [o for o in res if o not in sqlite and o not in invalid]
    wrong_others = {o: [w for w in witnesses if res[o][w]["class"] == "WRONG"] for o in others}
    v = {"P1": all(res[o][w]["class"] == "WRONG" for o in sqlite for w in sqlite_bad) and
         all(res[o][c]["class"] == "CORRECT" for o in sqlite for c in ("c_1e0", "c_0.1", "c_1.5e10")),
         "P2": all(o not in invalid for o in known_good) and
         all(res[o][x]["class"] != "WRONG" for o in known_good for x in labels),
         "P3": any(wrong_others.values())}
    table = {o: {lab: res[o][lab]["class"] for lab in labels} for o in sorted(res)}
    summary = {"versions": versions, "controls": k, "verdicts": {p: "HELD" if x else "REFUTED" for p, x in v.items()},
               "wrong_outside_sqlite": {o: w for o, w in wrong_others.items() if w},
               "invalid_observers": invalid,
               "error_counts": {o: sum(c == "ERROR" for c in t.values()) for o, t in table.items()},
               "observers": len(res), "tokens": len(labels), "sabotage": sabotage}
    if not sabotage:
        json.dump({"tokens": labels, "results": res, "table": table}, open(os.path.join(out, "observations.json"), "w"),
                  indent=1, sort_keys=True)
        json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True))
    w = max(len(o) for o in table)
    print("\n" + " " * w + "  " + " ".join(f"{lab[:9]:>9}" for lab in labels))
    for o, row in table.items():
        print(f"{o:<{w}}  " + " ".join(f"{row[lab][:9]:>9}" for lab in labels))
    if not all(k.values()):
        print("CLASSIFIER OR COVERAGE CONTROL FAILED: verdicts are not scorable")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "build":
        build(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "run":
        sys.exit(run(sys.argv[2], sys.argv[3], "--sabotage" in sys.argv[4:]))
    else:
        sys.exit(__doc__)
