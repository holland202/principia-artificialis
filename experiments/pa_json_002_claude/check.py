#!/usr/bin/env python3
"""Claude's check of PA-JSON-002 (registered in REGISTRATION.md, committed with this file before any run).

Separately written from the PA-JSON-002 protocol and the public SQLite API. ChatGPT's run.py and cases.py were not
read before this file was committed. Standard library only, plus gcc for the observer.

  curl -sSO https://www.sqlite.org/2026/sqlite-amalgamation-3540100.zip    (into WORK)
  python3 experiments/pa_json_002_claude/check.py build WORK                 verify hashes, compile observer.c
  python3 experiments/pa_json_002_claude/check.py run WORK OUT [--sabotage]  corpus, observer, oracles, verdicts

Exit codes for run: 0 = scored; 1 = an instrument control failed (or --sabotage was caught); 2 = cannot run.
"""
import hashlib, json, math, os, re, struct, subprocess, sys, zipfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = "sqlite-amalgamation-3540100.zip"
ZIP_SHA3 = "92281c86e2957f9b9305890f9ac04204caa7b677cc868dc326d942689df28e30"   # sqlite.org/download.html
C_SHA3 = "e2b869d3003b33c942b7dd7063604fbc53553e1b66609570df39b9b7b558ee81"     # releaselog/3_54_1.html
VERSION = "3.54.1"
SOURCE_ID = "2026-10-16 14:45:20 555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76"
DENSE = range(0, 12001)
SPARSE = sorted(set(range(12001, 131073, 1009)) | {20000, 50000, 100000, 131072})
R1_N = sorted({0, 1, 10, 100, 1000, 5000, 9999, 10000, 10001, 20000, 100000, 131072} | set(range(9990, 10011)))
NEG_N = sorted({0, 1, 100, 9999, 10000, 10001, 10002, 10100, 10308, 10309, 20000, 100000})
INF, PZERO, ONE = 0x7FF0000000000000, 0x0000000000000000, 0x3FF0000000000000
SIGN = 0x8000000000000000
CONTROLS = ["1e0", "2e0", "0.5", "1.5e10", "-3.25e-5", "1e308", "1e-300"]   # SQLite expected exact
# Oracle calibration: hard rounding cases with known answers. They check the oracles, not SQLite; SQLite's
# results on them are recorded but not scored.
ORACLE_CAL = {"9007199254740993": 0x4340000000000000, "9007199254740995": 0x4340000000000002,
              "4.9e-324": 0x0000000000000001, "2.4703282292062328e-324": 0x0000000000000001,
              "2.4703282292062327e-324": 0x0000000000000000, "0.1": 0x3FB999999999999A}
MALFORMED = ["1e", "-", "01"]
TOK = re.compile(r"^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$")
sys.set_int_max_str_digits(0)


def sha3(path):
    h = hashlib.sha3_256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def build(work):
    z = os.path.join(work, ZIP)
    if not os.path.exists(z):
        sys.exit(f"download {ZIP} into {work} first (see the docstring)")
    if sha3(z) != ZIP_SHA3:
        sys.exit("zip SHA3-256 does not match sqlite.org's published value: COULD NOT RUN AS REGISTERED")
    with zipfile.ZipFile(z) as zf:
        zf.extractall(work)
    amal = os.path.join(work, ZIP[:-4])
    c = sha3(os.path.join(amal, "sqlite3.c"))
    if c != C_SHA3:
        sys.exit("sqlite3.c SHA3-256 does not match the release log: COULD NOT RUN AS REGISTERED")
    cmd = ["gcc", "-O2", "-I", amal, os.path.join(HERE, "observer.c"), os.path.join(amal, "sqlite3.c"),
           "-o", os.path.join(work, "observer"), "-lm", "-lpthread", "-ldl"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("compile failed:\n" + p.stderr[-2000:])
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    info = {"zip_sha3": ZIP_SHA3, "sqlite3_c_sha3": c, "gcc": gcc, "compile": " ".join(cmd[:2] + ["-I", "AMAL",
            "observer.c", "AMAL/sqlite3.c", "-o", "observer", "-lm", "-lpthread", "-ldl"])}
    json.dump(info, open(os.path.join(work, "build.json"), "w"), indent=1)
    print(f"zip SHA3-256 matches; sqlite3.c SHA3-256 {c} matches the release log; compiled with {gcc}")


def exact(tok):
    sign, ip, fp, ex = TOK.match(tok).groups()
    fp, ex = fp or "", int(ex or 0)
    num, scale = int(ip + fp), ex - len(fp)
    f = Fraction(num * 10 ** scale) if scale >= 0 else Fraction(num, 10 ** -scale)
    return -f if sign else f


def bits(d):
    return struct.unpack(">Q", struct.pack(">d", d))[0]


def oracle_exact(tok):
    f = exact(tok)
    try:
        return bits(float(f))   # Fraction.__float__ is int/int true division: correctly rounded in CPython
    except OverflowError:
        return bits(math.inf if f > 0 else -math.inf)


def within_ulp(a, b):
    return (a & SIGN) == (b & SIGN) and abs((a & ~SIGN) - (b & ~SIGN)) <= 1


def corpus():
    c = [("control", None, t) for t in CONTROLS] + [("malformed", None, t) for t in MALFORMED]
    c += [("oracle_cal", None, t) for t in ORACLE_CAL]
    c += [("witness", 100000, "1" + "0" * 100000 + "e-100000"), ("witness", 100000, "0." + "0" * 100000 + "1e100001")]
    for n in list(DENSE) + SPARSE:
        c.append(("F1", n, "1" + "0" * n + "e-" + str(n)))
        c.append(("F2", n, "0." + "0" * n + "1e" + str(n + 1)))
    c += [("R1", n, "1.0" + "0" * n + "e0") for n in R1_N]
    c += [("NEG_F1", n, "-1" + "0" * n + "e-" + str(n)) for n in NEG_N]
    c += [("NEG_F2", n, "-0." + "0" * n + "1e" + str(n + 1)) for n in NEG_N]
    return c


def observe(work, toks, out):
    path = os.path.join(out, "tokens.txt")
    with open(path, "w") as f:
        for t in toks:
            f.write(t + "\n")
    p = subprocess.run([os.path.join(work, "observer"), path], capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"observer failed ({p.returncode}): {p.stderr[-500:]}")
    lines = p.stdout.splitlines()
    head, rows = lines[0], lines[1:]
    if len(rows) != len(toks):
        sys.exit(f"observer returned {len(rows)} rows for {len(toks)} tokens: COULD NOT RUN AS REGISTERED")
    os.remove(path)
    return head, rows


def parse_row(r):
    f = r.split("\t")
    hx = lambda s: None if s == "-" or s.endswith("!notfloat") else int(s, 16)  # noqa
    return {"valid": int(f[1]), "json_rc": f[2], "json_type": f[3], "json": hx(f[4]),
            "cast_rc": f[5], "cast_type": f[6], "cast": hx(f[7])}


def run(work, out, sabotage):
    os.makedirs(out, exist_ok=True)
    c = corpus()
    head, rows = observe(work, [t for _, _, t in c], out)
    if head != f"#{VERSION}\t{SOURCE_ID}":
        sys.exit(f"observer reports {head!r}, not the pinned release: COULD NOT RUN AS REGISTERED")
    recs = []
    for (fam, n, tok), row in zip(c, rows):
        o = parse_row(row)
        rec = {"family": fam, "n": n, "len": len(tok), **o}
        if fam != "malformed":
            rec["oracle"] = oracle_exact(tok)
            rec["oracle_float_str"] = bits(float(tok))
        recs.append(rec)
    if sabotage:   # flip the lowest observed bit of 1e0's JSON result, in memory only
        recs[0]["json"] ^= 1
    by = lambda fam: [r for r in recs if r["family"] == fam]  # noqa
    ok = lambda r: r["json"] == r["oracle"] and r["cast"] == r["oracle"]  # noqa

    # Instrument controls
    ctrl = by("control")
    k1 = ctrl[0]["json"] != ctrl[1]["json"] and ok(ctrl[0]) and ok(ctrl[1])
    k2 = all(r["oracle"] == r["oracle_float_str"] for r in recs if "oracle" in r)
    k3 = all(r["valid"] == 0 for r in by("malformed"))
    k4 = all(ok(r) and r["valid"] == 1 for r in ctrl)
    cal = [(t, r) for t, r in zip(ORACLE_CAL, by("oracle_cal"))]
    k5 = all(r["oracle"] == ORACLE_CAL[t] for t, r in cal)
    controls = {"K1_1e0_vs_2e0_distinguished": k1, "K2_two_oracles_agree": k2, "K3_malformed_rejected": k3,
                "K4_ordinary_controls_exact": k4, "K5_oracle_matches_known_bits": k5}
    cal_sqlite = {t: {"json": f"{r['json']:016x}" if r["json"] is not None else None,
                      "expected": f"{ORACLE_CAL[t]:016x}"} for t, r in cal}

    # C2: the two witnesses
    w1, w2 = by("witness")
    c2 = all(w["valid"] == 1 and w["json_type"] == "real" and w["cast_type"] == "real" for w in (w1, w2)) and \
        w1["json"] == w1["cast"] == INF and w2["json"] == w2["cast"] == PZERO and \
        ctrl[0]["json"] == ctrl[0]["cast"] == ONE

    # C3a/C3b: thresholds and bands in the dense range
    def threshold(fam):
        dense = [r for r in by(fam) if r["n"] in DENSE]
        good = [ok(r) for r in dense]
        if all(good):
            return None, dense
        first_bad = good.index(False)
        return first_bad - 1, dense

    res = {}
    for fam, width, top, power in (("F1", 308, INF, lambda k: Fraction(10) ** k),
                                   ("F2", 323, PZERO, lambda k: Fraction(1, 10 ** k))):
        N, dense = threshold(fam)
        r = {"threshold": N}
        if N is None:
            r.update(c3a=False, c3b=False)
        else:
            after = dense[N + 1:]
            r["monotone"] = all(not ok(x) for x in after)
            r["c3a"] = 9000 <= N <= 10999 and r["monotone"]
            band = [x for x in after if x["n"] - N <= width]
            beyond = [x for x in after if x["n"] - N > width]
            r["band_n"] = [band[0]["n"], band[-1]["n"]] if band else None
            r["band_ok"] = all(within_ulp(x["json"], bits(float(power(x["n"] - N)))) for x in band)
            r["beyond_n"] = [beyond[0]["n"], beyond[-1]["n"]] if beyond else None
            r["beyond_ok"] = all(x["json"] == top for x in beyond)
            r["band_failures"] = [x["n"] for x in band
                                  if not within_ulp(x["json"], bits(float(power(x["n"] - N))))][:20]
            r["c3b"] = r["band_ok"] and r["beyond_ok"]
        res[fam] = r

    longs = by("F1") + by("F2") + by("R1") + by("NEG_F1") + by("NEG_F2") + by("witness")
    c3c = all(x["json"] == x["cast"] for x in longs)
    c3d = all(x["valid"] == 1 and x["json_type"] == "real" for x in longs)
    c3e = all(ok(x) for x in by("R1"))
    pos = {(f, x["n"]): x for f in ("F1", "F2") for x in by(f)}
    c3f = all(x["json"] == pos[(f[4:], x["n"])]["json"] ^ SIGN for f in ("NEG_F1", "NEG_F2") for x in by(f))
    sparse_wrong = {f: [x["n"] for x in by(f) if x["n"] in SPARSE and not ok(x)] for f in ("F1", "F2")}
    verdicts = {"C2": c2, "C3a": res["F1"]["c3a"] and res["F2"]["c3a"], "C3b": res["F1"]["c3b"] and res["F2"]["c3b"],
                "C3c": c3c, "C3d": c3d, "C3e": c3e, "C3f": c3f}
    summary = {"observer_header": head, "controls": controls, "verdicts": {k: "HELD" if v else "REFUTED"
               for k, v in verdicts.items()}, "families": res, "sparse_wrong_count": {k: len(v) for k, v in
               sparse_wrong.items()}, "sparse_total": len(SPARSE), "tokens": len(recs),
               "total_token_bytes": sum(r["len"] for r in recs), "sabotage": sabotage,
               "oracle_cal_sqlite_unscored": cal_sqlite}
    compact = [{k: (f"{v:016x}" if isinstance(v, int) and k in ("json", "cast", "oracle", "oracle_float_str") else v)
                for k, v in r.items()} for r in recs]
    blob = json.dumps(compact, sort_keys=True, separators=(",", ":")).encode()
    summary["observations_sha256"] = hashlib.sha256(blob).hexdigest()
    if not sabotage:
        with open(os.path.join(out, "observations.json"), "wb") as f:
            f.write(blob)
        json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True))
    if not all(controls.values()):
        print("INSTRUMENT CONTROL FAILED: verdicts are not scorable")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "build":
        build(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "run":
        sys.exit(run(sys.argv[2], sys.argv[3], "--sabotage" in sys.argv[4:]))
    else:
        sys.exit(__doc__)
