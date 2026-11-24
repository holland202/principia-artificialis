"""CCC-001 accept-shift decomposition on the GPU7B outputs. Registration: ACCBIAS7B_PREREG.md (commit 37fe6ac).

Pure Python, no model. Reuses accbias.py's definitions (Delta_M = p_E - p_D of M's letter, equal item weights,
stored-key assertion). Development-only (C-EXPLORE). No qualification verdict changes whatever this prints (M12).

Usage:
  python3 experiments/ccc_001/accbias7b.py --dry                 # 1.5B committed files: reproduce ACCBIAS REF
  python3 experiments/ccc_001/accbias7b.py --dir <returned dir> [--sabotage] [--json out.json]

Gates V (custody) and P0 (bookkeeping), predictions T1 (REF d_acc > 0 per pi) and T2 (stage Q d_acc > 0).
Prints `VERDICT n of 3 as registered` and a `DIGEST`. Exit 0 only on the outcome pinned in RECORDED.
"""
import argparse
import ast
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from accbias import ITEM_MEANING, MEANINGS, PI, RES, item_equal_mean  # noqa: E402
from probes import OPTIONS  # noqa: E402

RECORDED = ((True, False, True), "ae276cb60a19fff6954b77198e267182e4d28f94e5e83c6abbfe3d888b41110d")  # pinned after the 7B run at c04d1a9

LENGTHS = ("REF", "N016", "STRESS")
ACCBIAS_REF_15B = (0.105711, 0.093951, 0.313284)  # ACCBIAS_RESULTS.md, P3 line


def digest(obj):  # identical to common.digest (common imports torch)
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def shards():
    tree = ast.parse(open(os.path.join(HERE, "kaggle_gpu7b.py")).read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "SHARDS":
            return ast.literal_eval(node.value)
    raise SystemExit("SHARDS not found")


def log_digest(path):
    ds = re.findall(r"^\s*DIGEST ([0-9a-f]{64})\s*$", open(path).read(), re.M)
    return ds[-1] if ds else None


def canon_q(j):  # qualify.py
    return {k: [[round(x, 4) for x in r["p"]] for r in v] for k, v in j["arms"].items()}


def canon_l(j):  # longctx.py
    c = {k: [[round(x, 4) for x in r["p"]] + [round(r["mass"], 4)] for r in v] for k, v in j["cells"].items()}
    c["D0_repeat"] = [[round(x, 4) for x in r["p"]] for r in j["D0_repeat"]]
    if j.get("D0_full_logits") is not None:
        c["D0_full_logits"] = [[round(x, 4) for x in r["p"]] for r in j["D0_full_logits"]]
    return c


def pairs_from(cellD, cellE, lam):
    out = []
    for i in range(24):
        for r in (cellD[i], cellE[i]):
            assert r["key"] == lam[ITEM_MEANING[i]], (i, r["key"])
            assert all(math.isfinite(x) for x in r["p"]) and len(r["p"]) == 3
        out.append({"item": i, "letters": lam, "pD": cellD[i]["p"], "pE": cellE[i]["p"]})
    return out


def d(p, m):
    j = OPTIONS.index(p["letters"][m])
    return p["pE"][j] - p["pD"][j]


def summary(prs):
    s = {m: item_equal_mean([(p["item"], d(p, m)) for p in prs]) for m in MEANINGS}
    s["up"] = sum(1 for p in prs if d(p, "accept") > 0)
    s["down"] = sum(1 for p in prs if d(p, "accept") < 0)
    return s


def fmt(s):
    return (f"d_acc {s['accept']:+.6f} d_rej {s['reject']:+.6f} d_ne {s['notenough']:+.6f} "
            f"| items d_acc up/down {s['up']}/{s['down']} of 24")


def load_sets(q, L, sabotage):
    """q: qualify json or None; L: {length: longctx json}. Returns {name: pairs}."""
    sets = {}
    if q is not None:
        a = q["arms"]
        sets["Q E-D"] = pairs_from(a["D"], a["E"], PI[0])
        sets["Q EF64-F64"] = pairs_from(a["F64"], a["EF64"], PI[0])
    for n, j in L.items():
        for k in (0, 1, 2):
            sets[f"{n} pi{k}"] = pairs_from(j["cells"][f"D{k}"], j["cells"][f"E{k}"], PI[k])
    if sabotage:
        sets = {n: [dict(p, pE=p["pD"]) for p in v] for n, v in sets.items()}
    return sets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir")
    ap.add_argument("--dry", action="store_true", help="1.5B committed files only; reproduce ACCBIAS REF values")
    ap.add_argument("--sabotage", action="store_true", help="replace every arm-E reading by its arm-D reading")
    ap.add_argument("--json")
    a = ap.parse_args()

    q15 = json.load(open(os.path.join(RES, "qualify.json")))
    l15 = json.load(open(os.path.join(RES, "longctx_ref.json")))
    base = load_sets(q15, {"REF": l15}, False)
    if a.dry:
        got = tuple(round(summary(base[f"REF pi{k}"])["accept"], 6) for k in (0, 1, 2))
        ok = got == ACCBIAS_REF_15B
        print(f"DRY 1.5B LONGCTX REF d_acc per pi {list(got)} vs ACCBIAS {list(ACCBIAS_REF_15B)}: equal {ok}")
        for n in sorted(base):
            print(f"DRY 1.5B {n}: {fmt(summary(base[n]))}")
        sys.exit(0 if ok else 1)

    D = a.dir
    # Gate V
    vl, v = [], []
    run = open(os.path.join(D, "runner.txt")).read()
    sh = all(re.search(rf"{re.escape(f)} {h} OK", run) for f, h in shards().items())
    v.append(sh)
    vl.append(f"V  runner.txt shows all four registered shard hashes OK: {sh}")
    q = json.load(open(os.path.join(D, "qualify_7b.json")))
    want, got = log_digest(os.path.join(D, "stageq.txt")), digest(canon_q(q))
    v.append(want == got)
    vl.append(f"V  qualify_7b.json rehash {got[:16]}... vs stageq.txt DIGEST {str(want)[:16]}...: {want == got}")
    L, absent = {}, []
    for n in LENGTHS:
        jp = os.path.join(D, f"longctx_{n}_7b.json")
        if not os.path.exists(jp):
            absent.append(n)
            continue
        j = json.load(open(jp))
        want, got = log_digest(os.path.join(D, f"longctx_{n}.txt")), digest(canon_l(j))
        v.append(want == got)
        vl.append(f"V  longctx_{n}_7b.json rehash {got[:16]}... vs longctx_{n}.txt DIGEST {str(want)[:16]}...: "
                  f"{want == got}")
        L[n] = j
    for n in absent:
        vl.append(f"V  {n} ABSENT (no JSON returned; not a failure of V)")
    gV = all(v)
    for x in vl:
        print(x)
    print(f"V {'HELD' if gV else 'REFUTED'} custody gate")
    held = [False, False, False]
    sets, rep = {}, {}
    if gV:
        sets = load_sets(q, L, a.sabotage)  # stored-key and finiteness assertions fail closed here
        bk = max(abs(sum(d(p, m) for m in MEANINGS)) for v_ in sets.values() for p in v_)
        ident = load_sets(q, L, True)
        zero = all(summary(v_)[m] == 0.0 for v_ in ident.values() for m in MEANINGS)
        held[0] = bk <= 5e-6 and zero
        print(f"P0 {'HELD' if held[0] else 'REFUTED'} keys and finite p asserted; bookkeeping max {bk:.2e} "
              f"(<= 5e-6); E:=D gives 0 in every cell: {zero}")
    else:
        print("P0 NOT READ (V failed)")
    if held[0]:
        rep = {n: summary(v_) for n, v_ in sets.items()}
        if "REF" in L:
            vals = [rep[f"REF pi{k}"]["accept"] for k in (0, 1, 2)]
            held[1] = all(x > 0 for x in vals)
            print(f"T1 {'HELD' if held[1] else 'REFUTED'} 7B REF d_acc per pi "
                  f"[{', '.join(f'{x:.6f}' for x in vals)}] (> 0 each)")
        else:
            print("T1 NOT READ (REF absent)")
        x = rep["Q E-D"]["accept"]
        held[2] = x > 0
        print(f"T2 {'HELD' if held[2] else 'REFUTED'} 7B stage Q d_acc (E-D, pi0) {x:.6f} (> 0)")
    else:
        print("T1 NOT READ (gate failed)")
        print("T2 NOT READ (gate failed)")
    if rep:
        for n in sorted(rep):
            print(f"REPORT 7B   {n}: {fmt(rep[n])}")
            if n in base:
                print(f"REPORT 1.5B {n}: {fmt(summary(base[n]))}")
        for n in absent:
            print(f"REPORT {n} ABSENT")
    canon = {"held": held, "absent": absent,
             "sets": {n: {k: (round(val, 6) if isinstance(val, float) else val) for k, val in s.items()}
                      for n, s in rep.items()},
             "per_item": {n: [[p["item"], [round(d(p, m), 6) for m in MEANINGS]] for p in v_]
                          for n, v_ in sets.items()}}
    dg = digest(canon)
    print(f"VERDICT {sum(held)} of 3 as registered")
    print(f"DIGEST {dg}")
    if a.json:
        json.dump(dict(canon, sabotage=a.sabotage, digest=dg), open(a.json, "w"), indent=1)
    sys.exit(0 if RECORDED is not None and (tuple(held), dg) == RECORDED else 1)


if __name__ == "__main__":
    main()
