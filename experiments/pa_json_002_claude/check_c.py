#!/usr/bin/env python3
"""Part C of Claude's PA-JSON-002 check (REGISTRATION.md, Amendment 1).

Source-derived predictions, registered after reading sqlite3AtoF() and before running these families.
  python3 experiments/pa_json_002_claude/check_c.py WORK OUT A_OUT
WORK holds the verified build (check.py build); A_OUT holds Part A's observations.json. Exit 0 = scored, 1 = an
instrument control failed, 2 = cannot run.
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check as A  # noqa: E402

D1_N = list(range(99900, 100101)) + [131072]
X1_K = range(-5, 321)
X2_J = range(-5, 331)
X3 = [(c, k) for c in ("42", "-7", "123456789") for k in (0, 3)]
NZERO = 0x8000000000000000
EXP = re.compile(r"^(.*[eE][+-]?)(\d+)$")


def model_token(tok):
    """sqlite3AtoF's exponent rule, as read from the source: an explicit exponent above 99,999 becomes 10,000."""
    m = EXP.match(tok)
    if not m:
        return tok
    return m.group(1) + (m.group(2) if int(m.group(2)) <= 99999 else "10000")


def corpus():
    c = [("control", None, t) for t in A.CONTROLS] + [("malformed", None, t) for t in A.MALFORMED]
    c += [("D1_F1", n, "1" + "0" * n + "e-" + str(n)) for n in D1_N]
    c += [("D1_F2", n, "0." + "0" * n + "1e" + str(n + 1)) for n in D1_N]
    c += [("X1", k, "1" + "0" * (10000 + k) + "e-100000") for k in X1_K]
    c += [("X2", j, "0." + "0" * (9999 + j) + "1e100000") for j in X2_J]
    c += [("X3", f"{co}:{k}", co + "0" * (10000 + k) + "e-100000") for co, k in X3]
    return c


def main(work, out, a_out):
    os.makedirs(out, exist_ok=True)
    c = corpus()
    head, rows = A.observe(work, [t for _, _, t in c], out)
    if head != f"#{A.VERSION}\t{A.SOURCE_ID}":
        sys.exit(f"observer reports {head!r}: COULD NOT RUN AS REGISTERED")
    recs = []
    for (fam, n, tok), row in zip(c, rows):
        r = {"family": fam, "n": n, "len": len(tok), **A.parse_row(row)}
        if fam != "malformed":
            r["oracle"] = A.oracle_exact(tok)
            r["oracle_float_str"] = A.bits(float(tok))
            r["model"] = A.oracle_exact(model_token(tok))
        recs.append(r)
    by = lambda f: [r for r in recs if r["family"] == f]  # noqa
    exact = lambda r: r["json"] == r["oracle"] and r["cast"] == r["oracle"]  # noqa

    ctrl = by("control")
    controls = {"K1": ctrl[0]["json"] != ctrl[1]["json"] and exact(ctrl[0]) and exact(ctrl[1]),
                "K2": all(r["oracle"] == r["oracle_float_str"] for r in recs if "oracle" in r),
                "K3": all(r["valid"] == 0 for r in by("malformed")),
                "K4": all(exact(r) and r["valid"] == 1 for r in ctrl)}

    d1 = all(exact(r) == (r["n"] <= 99999) for r in by("D1_F1")) and \
        all(r["json"] == A.INF for r in by("D1_F1") if r["n"] >= 100000) and \
        all(exact(r) == (r["n"] <= 99998) for r in by("D1_F2")) and \
        all(r["json"] == A.PZERO for r in by("D1_F2") if r["n"] >= 99999)

    def p10(k):
        from fractions import Fraction
        return A.bits(float(Fraction(10) ** k)) if k >= 0 else A.bits(float(Fraction(1, 10 ** -k)))
    x1 = by("X1")
    x2 = by("X2")
    d2_x1 = all(r["oracle"] == A.PZERO for r in x1) and \
        all(A.within_ulp(r["json"], p10(r["n"])) for r in x1 if r["n"] <= 308) and \
        all(r["json"] == A.INF for r in x1 if r["n"] >= 309)
    d2_x2 = all(r["oracle"] == A.INF for r in x2) and \
        all(A.within_ulp(r["json"], p10(-r["n"])) for r in x2 if r["n"] <= 323) and \
        all(r["json"] == A.PZERO for r in x2 if r["n"] >= 324)
    x3 = by("X3")
    d4 = all(r["oracle"] in (A.PZERO, NZERO) and A.within_ulp(r["json"], r["model"]) and r["json"] != r["oracle"]
             for r in x3)
    longs = [r for r in recs if r["family"] not in ("control", "malformed")]
    d5 = all(r["valid"] == 1 and r["json_type"] == "real" and r["json"] == r["cast"] for r in longs)

    # D3: the model explains every long token of Part A and Part C.
    a_obs = json.load(open(os.path.join(a_out, "observations.json")))
    a_toks = [t for _, _, t in A.corpus()]
    if len(a_obs) != len(a_toks):
        sys.exit("Part A observations do not line up with Part A's corpus: COULD NOT RUN AS REGISTERED")
    a_fail, a_checked = [], 0
    for r, tok in zip(a_obs, a_toks):
        if r["family"] in ("control", "malformed", "oracle_cal"):
            continue
        a_checked += 1
        if not A.within_ulp(int(r["json"], 16), A.oracle_exact(model_token(tok))):
            a_fail.append([r["family"], r["n"]])
    c_fail = [[r["family"], r["n"]] for r in longs if not A.within_ulp(r["json"], r["model"])]
    d3 = not a_fail and not c_fail

    v = {"D1": d1, "D2_X1": d2_x1, "D2_X2": d2_x2, "D3": d3, "D4": d4, "D5": d5}
    show = {r["n"]: f"{r['json']:016x}" for r in x3}
    summary = {"observer_header": head, "controls": controls,
               "verdicts": {k: "HELD" if x else "REFUTED" for k, x in v.items()},
               "D3_checked": {"part_A_long_tokens": a_checked, "part_C_long_tokens": len(longs),
                              "failures_A": a_fail[:20], "failures_C": c_fail[:20]},
               "X1_examples": {k: f"{r['json']:016x}" for r in x1 for k in [r["n"]] if k in (-5, 0, 1, 2, 308, 309)},
               "X2_examples": {j: f"{r['json']:016x}" for r in x2 for j in [r["n"]] if j in (-5, 0, 1, 323, 324)},
               "X3_bits": show, "tokens": len(recs), "max_len_X": max(r["len"] for r in x1 + x2 + x3)}
    compact = [{k: (f"{x:016x}" if isinstance(x, int) and k in ("json", "cast", "oracle", "oracle_float_str",
                                                                 "model") else x) for k, x in r.items()} for r in recs]
    blob = json.dumps(compact, sort_keys=True, separators=(",", ":")).encode()
    summary["observations_sha256"] = hashlib.sha256(blob).hexdigest()
    open(os.path.join(out, "observations.json"), "wb").write(blob)
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0 if all(controls.values()) else 1


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:]))
