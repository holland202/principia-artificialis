"""TLM-005 span attributor (T3). Frozen registration: REGISTRATION_TLM005.md at d8800f5 (FREEZE_TLM005.md).

For TLM-004's 40 committed samples and 10 blocks of 20 real held-out stories it computes, on gencheck.py's window
grid (50 bytes, stride 50, offset 0):
  - masks: windows overlapping the first 16 bytes after leading whitespace; windows containing bytes of an
    appended <|endoftext|> (model text only, which is the only text that carries one);
  - document frequency df(w): distinct training stories containing w, exact duplicate stories collapsed by SHA-256
    of the story bytes (raw distinct-story counts are kept too); classes U (df = 1), R (df >= 2), B (found in the
    slice but only across a story boundary), N (not found);
  - longest match per text inside a single training story, opening bytes and appended end marker excluded. Any
    such match of 99 bytes or more contains a full grid window that matches, so it is found by extending around
    matching windows. Texts with no matching window get the bound "<99".
Then the fidelity gate, block maxima, drop-one and the registered outcome, fail-closed.

usage: python3 tlm005_attrib.py [--no-mask] [--df-any] [--fixtures FILE ...] [--json OUT]
  --fixtures FILE: score each text of FILE (texts split on \\n\\n=====\\n\\n) and print per-text U, R, B, N and
  longest match. No verdict is computed in that mode.
Claude (Anthropic, Opus 5.5), 2026-11-24. SELF-TESTED only; author of this code must not see the blind fixtures.
"""
import argparse
import bisect
import hashlib
import json
import multiprocessing as mp
import os
import sys

END = b"<|endoftext|>"
SPAN, OPEN, N, BLOCKS = 50, 16, 20, 10
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_SHA = {"data/v2_train_200MB.txt": "ee5242d9d94d6df3b5813e01adb0ee278eb77aa3bb7395fbd22cbe6e368869e9",
            "data/v2_valid.txt": "6874bae9a4c1a4e7edcf0e53b86c17817e9cf881fc75ff2368da457b80c0585d"}
SAMPLES = {"41": "results/tiny_lm/004/runs/t41.samples.txt", "42": "results/tiny_lm/004/runs/t42.samples.txt"}

TRAIN = b""  # set in main; shared with workers by fork


def sha(b):
    return hashlib.sha256(b).hexdigest()


def occurrences(w):
    out, i = [], TRAIN.find(w)
    while i != -1:
        out.append(i)
        i = TRAIN.find(w, i + 1)
    return w, out


def opening(t):
    ws = len(t) - len(t.lstrip())
    return ws, ws + OPEN


def opening_end(t):
    return opening(t)[1]


def end_region(t, is_model):
    if is_model and t.endswith(END):
        return len(t) - len(END)
    return len(t)


def windows(t, is_model, mask):
    """Grid windows as (start, bytes, masked)."""
    (ws, o), e = opening(t), end_region(t, is_model)
    out = []
    for i in range(0, len(t) - SPAN + 1, SPAN):
        m = (i < o and i + SPAN > ws) or (i + SPAN > e)
        out.append((i, t[i:i + SPAN], m and mask))
    return out


class Index:
    def __init__(self, train):
        self.ends, i = [], train.find(END)
        while i != -1:
            self.ends.append(i)
            i = train.find(END, i + 1)
        starts = [0] + [e + len(END) for e in self.ends]
        stops = self.ends + [len(train)]
        self.starts, self.stops = starts, stops
        self.hash = [sha(train[a:b]) for a, b in zip(starts, stops)]
        self.n_stories, self.n_unique = len(self.hash), len(set(self.hash))

    def story(self, p, length):
        """Story index if [p, p+length) lies inside one story, else None."""
        k = bisect.bisect_right(self.starts, p) - 1
        return k if p + length <= self.stops[k] else None


def classify(occ, idx, df_any):
    if not occ:
        return "N", 0, 0
    inside = [idx.story(p, SPAN) for p in occ]
    stories = {k for k in inside if k is not None}
    if not stories:
        return "B", 0, 0
    df, raw = len({idx.hash[k] for k in stories}), len(stories)
    if df_any:
        return "U", df, raw
    return ("U" if df == 1 else "R"), df, raw


def longest(t, is_model, wins, occ_of, idx):
    """Longest substring of t (after the opening, before an appended end marker) inside one training story."""
    lo_lim, hi_lim = opening_end(t), end_region(t, is_model)
    best = 0
    for start, w, masked in wins:
        if masked or start < lo_lim or start + SPAN > hi_lim:
            continue
        for p in occ_of[w]:
            k = idx.story(p, SPAN)
            if k is None:
                continue
            a, b = start, start + SPAN
            q0, q1 = p, p + SPAN
            while a > lo_lim and q0 > idx.starts[k] and t[a - 1] == TRAIN[q0 - 1]:
                a -= 1
                q0 -= 1
            while b < hi_lim and q1 < idx.stops[k] and t[b] == TRAIN[q1]:
                b += 1
                q1 += 1
            best = max(best, b - a)
    return best if best else None  # None means "<99" (no matching window)


def score_texts(texts, is_model, mask, df_any, occ_of, idx):
    rows = []
    for t in texts:
        wins = windows(t, is_model, mask)
        cls = []
        for start, w, masked in wins:
            if masked:
                continue
            c, df, raw = classify(occ_of[w], idx, df_any)
            cls.append({"start": start, "class": c, "df": df, "raw": raw})
        lm = longest(t, is_model, wins, occ_of, idx)
        rows.append({"windows": len(wins), "eligible": len(cls),
                     "U": sum(c["class"] == "U" for c in cls), "R": sum(c["class"] == "R" for c in cls),
                     "B": sum(c["class"] == "B" for c in cls), "N": sum(c["class"] == "N" for c in cls),
                     "longest": lm, "cls": cls})
    return rows


def agg(rows, drop=None):
    rs = [r for i, r in enumerate(rows) if i != drop]
    E = sum(r["eligible"] for r in rs)
    U, R, B = (sum(r[k] for r in rs) for k in "URB")
    share = sum((r["longest"] or 0) >= 200 for r in rs) / len(rs)
    return {"E": E, "U": U, "R": R, "B": B, "u": U / E, "r": R / E, "b": B / E, "copy": (U + R + B) / E,
            "share200": share}


def main():
    global TRAIN
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-mask", action="store_true")
    ap.add_argument("--df-any", action="store_true")
    ap.add_argument("--fixtures", nargs="*")
    ap.add_argument("--json")
    a = ap.parse_args()
    os.chdir(ROOT)
    for f, h in DATA_SHA.items():
        got = sha(open(f, "rb").read())
        print(f, "sha256", got, "OK" if got == h else "MISMATCH")
        if got != h:
            print("VERDICT NONE (data hash mismatch)")
            sys.exit(2)
    for s, f in SAMPLES.items():
        print(f, "sha256", sha(open(f, "rb").read()))
    print("code", os.path.basename(__file__), "sha256", sha(open(__file__, "rb").read()))
    print("flags no_mask", a.no_mask, "df_any", a.df_any)
    TRAIN = open("data/v2_train_200MB.txt", "rb").read()
    idx = Index(TRAIN)
    print("training stories", idx.n_stories, "unique by sha256", idx.n_unique)
    mask = not a.no_mask

    if a.fixtures:
        sets = {f: (open(f, "rb").read().split(b"\n\n=====\n\n"), True) for f in a.fixtures}
    else:
        valid = open("data/v2_valid.txt", "rb").read().split(END)[:N * BLOCKS]
        assert len(valid) == N * BLOCKS
        sets = {"t" + s: (open(f, "rb").read().split(b"\n\n=====\n\n"), True) for s, f in SAMPLES.items()}
        for b in range(BLOCKS):
            sets[f"block{b + 1:02d}"] = (valid[b * N:(b + 1) * N], False)
        for k in ("t41", "t42"):
            assert len(sets[k][0]) == N, (k, len(sets[k][0]))

    allw = sorted({w for texts, m in sets.values() for t in texts for _, w, _ in windows(t, m, False)})
    print("distinct windows searched", len(allw))
    with mp.get_context("fork").Pool(2) as pool:
        occ_of = dict(pool.map(occurrences, allw, chunksize=16))

    res = {name: score_texts(texts, m, mask, a.df_any, occ_of, idx) for name, (texts, m) in sets.items()}

    if a.fixtures:
        for name, rows in res.items():
            for i, r in enumerate(rows):
                lm = r["longest"] if r["longest"] is not None else "<99"
                print(f"FIXTURE {os.path.basename(name)} text {i + 1}: E {r['eligible']} U {r['U']} R {r['R']} "
                      f"B {r['B']} N {r['N']} longest {lm} | U windows raw story counts "
                      f"{[c['raw'] for c in r['cls'] if c['class'] == 'U']}")
        print("VERDICT NONE (fixture mode)")
        return

    # Fidelity gate: masks off, df ignored, any occurrence in the raw slice (TLM-004's gencheck count)
    fid = {}
    for name in ("t41", "t42", "block01"):
        texts, m = sets[name]
        ws = [w for t in texts for _, w, _ in windows(t, m, False)]
        fid[name] = (sum(bool(occ_of[w]) for w in ws), len(ws))
    want = {"t41": (30, 273), "t42": (24, 260), "block01": (28, 358)}
    fid_ok = fid == want
    print("FIDELITY", "HELD" if fid_ok else "FAILED", {k: f"{v[0]}/{v[1]}" for k, v in fid.items()},
          "want", {k: f"{v[0]}/{v[1]}" for k, v in want.items()})

    A = {name: agg(rows) for name, rows in res.items()}
    for name, x in A.items():
        print(f"{name}: E {x['E']} U {x['U']} R {x['R']} B {x['B']} | u {x['u']:.4f} r {x['r']:.4f} "
              f"b {x['b']:.4f} copy {x['copy']:.4f} | longest>=200 share {x['share200']:.2f}")
    for s in ("t41", "t42"):
        lm = ["<99" if r["longest"] is None else r["longest"] for r in res[s]]
        print(f"{s} longest per text: {lm}")
    blocks = [A[f"block{b + 1:02d}"] for b in range(BLOCKS)]
    mx = {k: max(x[k] for x in blocks) for k in ("u", "r", "b", "copy", "share200")}
    print("block maxima", {k: round(v, 4) for k, v in mx.items()})
    drop = {s: [agg(res[s], drop=i) for i in range(N)] for s in ("t41", "t42")}
    for s in ("t41", "t42"):
        for k in ("u", "r", "copy"):
            v = [d[k] for d in drop[s]]
            print(f"{s} drop-one {k} min {min(v):.4f} max {max(v):.4f}")

    if a.no_mask or a.df_any:
        print("VERDICT NONE (sabotage switch set; counts above are for the anti-vacuity check)")
        return

    def excess(k):
        full = [A[s][k] > mx[k] for s in ("t41", "t42")]
        if full == [True, True]:
            return "yes" if all(d[k] > mx[k] for s in ("t41", "t42") for d in drop[s]) else "dropone"
        return "no" if full == [False, False] else "disagree"

    ue, re_, ce = excess("u"), excess("r"), excess("copy")
    bsum = sum(A[s]["B"] for s in A)
    print("excess u", ue, "| r", re_, "| masked copy rate", ce, "| B total", bsum)
    if not fid_ok:
        out = "NONE (fidelity gate failed)"
    elif bsum != 0 or "disagree" in (ue, re_) or "dropone" in (ue, re_):
        out = "INCONCLUSIVE"
    elif ue == "yes" and re_ == "no":
        out = "SINGLE-STORY"
    elif ue == "no" and re_ == "yes":
        out = "FORMULA"
    elif ue == "yes" and re_ == "yes":
        out = "MIXED"
    elif ue == "no" and re_ == "no" and ce == "no":
        out = "NO EXCESS"
    else:
        out = "INCONCLUSIVE"
    lmx = [A[s]["share200"] > mx["share200"] for s in ("t41", "t42")]
    print("longest-match share >= 200 above block maximum in both seeds:", lmx == [True, True],
          "(agrees with SINGLE-STORY only if True)")
    print("VERDICT", out)
    if a.json:
        json.dump({"fidelity": {k: list(v) for k, v in fid.items()}, "agg": A, "block_max": mx,
                   "rows": {k: [{kk: vv for kk, vv in r.items()} for r in v] for k, v in res.items()},
                   "verdict": out}, open(a.json, "w"), indent=1)
        print("json", a.json, "sha256", sha(open(a.json, "rb").read()))


if __name__ == "__main__":
    main()
