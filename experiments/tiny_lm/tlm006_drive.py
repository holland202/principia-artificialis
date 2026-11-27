"""TLM-006 driver (T5). Frozen registration: REGISTRATION_TLM006.md at 834ff9b (FREEZE_TLM006.md, ac09ea6).

Imports TLM-005's attributor (tlm005_attrib.py at 66966b7, sha256 93948c3c...0590) unchanged: window grid, masks, df with
duplicate collapse, classes U/R/B/N, per-text rows, pooled aggregation.

Sets scored:
  t41, t42  : 200 model samples each (generation seeds 5020..5219, file from tlm006_gen.py), split on \\n\\n=====\\n\\n
  ref01..10 : valid stories 200..2199 (10 blocks of 200), split on <|endoftext|> as in TLM-005
  null      : valid stories 2200..2399 (reported, not gated)
  pos       : training stories 1000..1199 (positive control; must clear the threshold on r or u)
  rfix      : one fixture text holding RFIX_PHRASE (in >= 2 distinct non-duplicate training stories) on the grid
G0 (before anything else): on TLM-004's 40 committed samples and valid stories 0..19, the imported functions must
reproduce TLM-005's lines t41 E 247 U 3 R 10 B 0, t42 E 236 U 4 R 5 B 0, block01 E 338 U 7 R 8 B 0.
G3: the valid file must hold >= 2,600 stories.

decide() is a pure function of per-text counts and gate flags and returns one of the ten frozen precedence rows.
Sensitivity S1 (references cut to the model's token length through tok1024.json) and S2 (per-text mean r) are
reported, not part of the verdict. S1 interpretation (disclosed): a model text holds the prompt's tokens plus at most
330 generated tokens, so references are cut at len(prompt ids) + 330 tokens.

usage: python3 tlm006_drive.py --data DIR --tok TOK1024.json --s41 FILE --s42 FILE [--df-any] [--json OUT]
       python3 tlm006_drive.py --data DIR --gates-only      (G0, G3 and the R fixture; no model samples read)
       python3 tlm006_drive.py --selftest                   (decide() on synthetic counts; no data read)
Claude (Anthropic, Opus 5.5), 2026-11-26. SELF-TESTED only; the author must not see ChatGPT's blind decision cases.
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tlm005_attrib as A  # noqa: E402

END = A.END
SUB, NSUB, REFBLK, NREF = 20, 10, 200, 10
RFIX_PHRASE = b" there was a little girl named Lily. She loved to "
DATA_SHA = {"v2_train_200MB.txt": "ee5242d9d94d6df3b5813e01adb0ee278eb77aa3bb7395fbd22cbe6e368869e9",
            "v2_valid.txt": "6874bae9a4c1a4e7edcf0e53b86c17817e9cf881fc75ff2368da457b80c0585d"}
G0_WANT = {"t41": (247, 3, 10, 0), "t42": (236, 4, 5, 0), "block01": (338, 7, 8, 0)}
OUTCOMES = {1: "STOP / INCONCLUSIVE", 2: "CONTROL FAILED", 3: "INCONCLUSIVE (E = 0)", 4: "INCONCLUSIVE (B != 0)",
            5: "INCONCLUSIVE (drop-one-block)", 6: "SEED-41 ONLY", 7: "BOTH", 8: "SEED-42 ONLY",
            9: "NEITHER CLEARED", 10: "INCONCLUSIVE (fallback)"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ pure decision layer

def pooled(rows, key):
    E = sum(r["E"] for r in rows)
    return None if E == 0 else sum(r[key] for r in rows) / E


def subsets(rows):
    """The full set and the 10 drop-one-block subsets (blocks of SUB consecutive texts)."""
    n = len(rows) // SUB
    return [rows] + [rows[:j * SUB] + rows[(j + 1) * SUB:] for j in range(n)]


def clears(rows, refs, key):
    """'yes' (above the max of the reference sets, on the full set and every drop-one-block subset), 'dropone' (full
    set above, some subset not), 'no', or None when any rate is undefined (E = 0)."""
    mx = [pooled(r, key) for r in refs]
    vals = [pooled(s, key) for s in subsets(rows)]
    if any(v is None for v in mx + vals):
        return None
    m = max(mx)
    if vals[0] <= m:
        return "no"
    return "yes" if all(v > m for v in vals[1:]) else "dropone"


def decide(counts, gates):
    """counts: {'t41','t42','pos': [200 rows], 'ref01'..'ref10': [200 rows]}; each row {'E','U','R','B'} (ints).
    gates: {'G0': bool, 'G3': bool, 'rfix_R': int, 'rfix_R_dfany': int, 'dfany_R_total': int}.
    Returns (row number 1..10, outcome text). Fail-closed: anything missing gives row 1."""
    try:
        need = ["t41", "t42", "pos"] + [f"ref{b:02d}" for b in range(1, NREF + 1)]
        if not (gates["G0"] is True and gates["G3"] is True):
            return 1, OUTCOMES[1]
        for k in need:
            if k not in counts or len(counts[k]) != REFBLK:
                return 1, OUTCOMES[1]
            for r in counts[k]:
                for f in "EURB":
                    if not isinstance(r[f], int) or r[f] < 0:
                        return 1, OUTCOMES[1]
        refs = [counts[f"ref{b:02d}"] for b in range(1, NREF + 1)]
        pos_ok = "yes" in (clears(counts["pos"], refs, "R"), clears(counts["pos"], refs, "U"))
        if not pos_ok or gates["rfix_R"] < 1 or gates["rfix_R_dfany"] != 0 or gates["dfany_R_total"] != 0:
            return 2, OUTCOMES[2]
        allsets = [counts[k] for k in need]
        if any(pooled(s, "R") is None for k in need for s in subsets(counts[k])):
            return 3, OUTCOMES[3]
        if any(sum(r["B"] for r in s) != 0 for s in allsets):
            return 4, OUTCOMES[4]
        c41, c42 = clears(counts["t41"], refs, "R"), clears(counts["t42"], refs, "R")
        if "dropone" in (c41, c42):
            return 5, OUTCOMES[5]
        if (c41, c42) == ("yes", "no"):
            return 6, OUTCOMES[6]
        if (c41, c42) == ("yes", "yes"):
            return 7, OUTCOMES[7]
        if (c41, c42) == ("no", "yes"):
            return 8, OUTCOMES[8]
        if (c41, c42) == ("no", "no"):
            return 9, OUTCOMES[9]
        return 10, OUTCOMES[10]
    except (KeyError, TypeError):
        return 1, OUTCOMES[1]


def selftest():
    def rows(n, E, U, R, B=0):
        return [{"E": E, "U": U, "R": R, "B": B} for _ in range(n)]
    ok_g = {"G0": True, "G3": True, "rfix_R": 1, "rfix_R_dfany": 0, "dfany_R_total": 0}
    base = {f"ref{b:02d}": rows(200, 10, 0, b % 3) for b in range(1, 11)}  # ref r max = 2/10
    base["pos"] = rows(200, 10, 4, 6)
    cases = [
        ("neither", dict(base, t41=rows(200, 10, 0, 1), t42=rows(200, 10, 0, 2)), ok_g, 9),
        ("seed41 only", dict(base, t41=rows(200, 10, 0, 3), t42=rows(200, 10, 0, 1)), ok_g, 6),
        ("both", dict(base, t41=rows(200, 10, 0, 3), t42=rows(200, 10, 0, 3)), ok_g, 7),
        ("seed42 only", dict(base, t41=rows(200, 10, 0, 1), t42=rows(200, 10, 0, 3)), ok_g, 8),
        ("dropone", dict(base, t41=rows(20, 10, 0, 10) + rows(180, 10, 0, 2), t42=rows(200, 10, 0, 1)), ok_g, 5),
        ("B != 0", dict(base, t41=rows(200, 10, 0, 1, 1), t42=rows(200, 10, 0, 1)), ok_g, 4),
        ("E = 0 subset", dict(base, t41=rows(200, 0, 0, 0), t42=rows(200, 10, 0, 1)), ok_g, 3),
        ("dead R fixture", dict(base, t41=rows(200, 10, 0, 1), t42=rows(200, 10, 0, 1)), dict(ok_g, rfix_R=0), 2),
        ("df-any leaves R", dict(base, t41=rows(200, 10, 0, 1), t42=rows(200, 10, 0, 1)),
         dict(ok_g, dfany_R_total=5), 2),
        ("pos control fails", dict(base, pos=rows(200, 10, 0, 1), t41=rows(200, 10, 0, 1), t42=rows(200, 10, 0, 1)),
         ok_g, 2),
        ("G0 fails", dict(base, t41=rows(200, 10, 0, 3), t42=rows(200, 10, 0, 3)), dict(ok_g, G0=False), 1),
        ("missing set", {k: v for k, v in dict(base, t41=rows(200, 10, 0, 3)).items()}, ok_g, 1),
    ]
    bad = 0
    for name, c, g, want in cases:
        got = decide(c, g)[0]
        print(f"selftest {name}: row {got} want {want} {'ok' if got == want else 'WRONG'}")
        bad += got != want
    print("SELFTEST", "PASS" if bad == 0 else f"FAIL ({bad})")
    return bad == 0


# ------------------------------------------------------------------ measurement layer (TLM-005 functions)

def score(sets, mask, df_any, idx):
    allw = sorted({w for texts, m in sets.values() for t in texts for _, w, _ in A.windows(t, m, False)})
    print("distinct windows searched", len(allw), flush=True)
    with mp.get_context("fork").Pool(2) as pool:
        occ_of = dict(pool.map(A.occurrences, allw, chunksize=16))
    res = {k: A.score_texts(texts, m, mask, df_any, occ_of, idx) for k, (texts, m) in sets.items()}
    return {k: [{"E": r["eligible"], "U": r["U"], "R": r["R"], "B": r["B"], "longest": r["longest"]} for r in rows]
            for k, rows in res.items()}


def summary(rows):
    E = sum(r["E"] for r in rows)
    U, R, B = (sum(r[k] for r in rows) for k in "URB")
    f = (lambda x: x / E) if E else (lambda x: float("nan"))
    return f"E {E} U {U} R {R} B {B} | u {f(U):.4f} r {f(R):.4f} copy {f(U + R + B):.4f}"


def dist(xs):
    s = sorted(xs)
    q = lambda p: s[min(len(s) - 1, int(p * (len(s) - 1) + 0.5))]  # noqa: E731
    return f"min {s[0]} q1 {q(.25)} median {q(.5)} q3 {q(.75)} max {s[-1]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    ap.add_argument("--tok")
    ap.add_argument("--s41")
    ap.add_argument("--s42")
    ap.add_argument("--df-any", action="store_true")
    ap.add_argument("--gates-only", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if not selftest():
        print("VERDICT NONE (decide() selftest failed)")
        sys.exit(2)
    for f, h in DATA_SHA.items():
        got = sha(open(os.path.join(a.data, f), "rb").read())
        print(f, "sha256", got, "OK" if got == h else "MISMATCH")
        if got != h:
            print("VERDICT", OUTCOMES[1], "(data hash mismatch)")
            sys.exit(2)
    for f in ("tlm005_attrib.py", "tlm006_drive.py"):
        print("code", f, "sha256", sha(open(os.path.join(HERE, f), "rb").read()))
    print("flags df_any", a.df_any)
    A.TRAIN = open(os.path.join(a.data, "v2_train_200MB.txt"), "rb").read()
    idx = A.Index(A.TRAIN)
    print("training stories", idx.n_stories, "unique by sha256", idx.n_unique)
    valid = open(os.path.join(a.data, "v2_valid.txt"), "rb").read().split(END)
    g3 = len(valid) >= 2600
    print("G3 valid stories", len(valid), "(need >= 2600)", "HELD" if g3 else "FAILED")

    # G0: TLM-005 reproduction on TLM-004's committed samples and valid stories 0..19
    root = os.path.dirname(os.path.dirname(HERE))
    old = {"t41": (open(os.path.join(root, A.SAMPLES["41"]), "rb").read().split(b"\n\n=====\n\n"), True),
           "t42": (open(os.path.join(root, A.SAMPLES["42"]), "rb").read().split(b"\n\n=====\n\n"), True),
           "block01": (valid[:20], False)}
    g0r = score(old, True, False, idx)
    got0 = {k: (sum(r["E"] for r in v), sum(r["U"] for r in v), sum(r["R"] for r in v), sum(r["B"] for r in v))
            for k, v in g0r.items()}
    g0 = got0 == G0_WANT
    for k in ("t41", "t42", "block01"):
        print(f"G0 {k}: E {got0[k][0]} U {got0[k][1]} R {got0[k][2]} B {got0[k][3]} want {G0_WANT[k]}")
    print("G0", "HELD" if g0 else "FAILED")

    # R fixture: filler window (masked: overlaps the opening) then the phrase on the grid at offset 50
    rfix_text = b"x" * 50 + RFIX_PHRASE
    rf = {"rfix": ([rfix_text], False)}
    rf_n = score(rf, True, False, idx)["rfix"][0]
    rf_d = score(rf, True, True, idx)["rfix"][0]
    print(f"R fixture: normal U {rf_n['U']} R {rf_n['R']} | --df-any U {rf_d['U']} R {rf_d['R']} "
          f"(need R >= 1, then R = 0)")
    if a.gates_only:
        print("VERDICT NONE (gates only; no model samples read)")
        return

    # Study sets
    sets = {}
    for s, f in (("t41", a.s41), ("t42", a.s42)):
        texts = open(f, "rb").read().split(b"\n\n=====\n\n")
        print(f"samples {s} {f} sha256 {sha(open(f, 'rb').read())} texts {len(texts)}")
        sets[s] = (texts, True)
    for b in range(NREF):
        sets[f"ref{b + 1:02d}"] = (valid[REFBLK * (b + 1):REFBLK * (b + 2)], False)
    sets["null"] = (valid[2200:2400], False)
    sets["pos"] = ([A.TRAIN[idx.starts[k]:idx.stops[k]] for k in range(1000, 1200)], False)
    for k, (texts, m) in sets.items():
        lens = [len(t) for t in texts]
        print(f"lengths {k}: n {len(texts)} bytes {dist(lens)}")
    C = score(sets, True, False, idx)
    D = score(sets, True, True, idx)
    dfany_R = sum(r["R"] for rows in D.values() for r in rows)
    for k, rows in C.items():
        print(f"{k}: {summary(rows)} | E per text {dist([r['E'] for r in rows])}")
    print("--df-any R total over every set:", dfany_R, "(need 0)")

    gates = {"G0": g0, "G3": g3, "rfix_R": rf_n["R"], "rfix_R_dfany": rf_d["R"], "dfany_R_total": dfany_R}
    refs = [C[f"ref{b:02d}"] for b in range(1, NREF + 1)]
    for key in ("R", "U"):
        mx = max(pooled(r, key) for r in refs if pooled(r, key) is not None)
        for k in ("t41", "t42", "pos", "null"):
            print(f"{key.lower()} {k}: {pooled(C[k], key):.4f} vs reference max {mx:.4f} -> {clears(C[k], refs, key)}")
    for k in ("t41", "t42"):
        subs = [pooled(C[k][j * SUB:(j + 1) * SUB], "R") for j in range(NSUB)]
        print(f"same-input noise {k}: r per 20-sample sub-block",
              [None if v is None else round(v, 4) for v in subs])

    # Sensitivity S2: per-text mean r (texts with E = 0 excluded and counted)
    def ptm(rows):
        xs = [r["R"] / r["E"] for r in rows if r["E"]]
        return (sum(xs) / len(xs) if xs else None), sum(1 for r in rows if not r["E"])
    m2 = max(ptm(r)[0] for r in refs)
    for k in ("t41", "t42"):
        v, z = ptm(C[k])
        print(f"S2 {k}: per-text mean r {v:.4f} vs reference max {m2:.4f} (E = 0 texts excluded: {z})")

    # Sensitivity S1: references cut to the model's token length
    from tokenizers import Tokenizer
    tk = Tokenizer.from_file(a.tok)
    cap = len(tk.encode("Once upon a time").ids) + 330
    cut = {f"ref{b:02d}": ([tk.decode(tk.encode(t.decode("utf-8", "ignore")).ids[:cap]).encode("utf-8")
                            for t in sets[f"ref{b:02d}"][0]], False) for b in range(1, NREF + 1)}
    C1 = score(cut, True, False, idx)
    refs1 = [C1[f"ref{b:02d}"] for b in range(1, NREF + 1)]
    for k in ("t41", "t42"):
        print(f"S1 {k}: r {pooled(C[k], 'R'):.4f} vs cut-reference max "
              f"{max(pooled(r, 'R') for r in refs1):.4f} -> {clears(C[k], refs1, 'R')} (token cap {cap})")

    if a.df_any:
        print("VERDICT NONE (sabotage switch set)")
        return
    row, out = decide({k: [{f: r[f] for f in 'EURB'} for r in v] for k, v in C.items()}, gates)
    print("gates", gates)
    print(f"VERDICT row {row}: {out}")
    if a.json:
        json.dump({"gates": gates, "counts": C, "cut_refs": C1, "verdict": [row, out]}, open(a.json, "w"), indent=1)
        print("json", a.json, "sha256", sha(open(a.json, "rb").read()))


if __name__ == "__main__":
    main()
