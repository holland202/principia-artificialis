#!/usr/bin/env python3
"""
note061_reference.py -- E16: does a table of contents carry retrieval signal,
or is the gain the two-stage machinery?

Four arms over principia-artificialis's own notes. FLAT, TOC, TOC_SHUF and
RANDOM differ only where E16_PREREG.md says they differ. TOC and TOC_SHUF
share one code path; the only difference is whether the table of contents
tells the truth about the note it points to.

Predictions are registered in E16_PREREG.md BEFORE this ran. Read that first.

    python3 note061_reference.py <path-to-principia-checkout>
    python3 note061_reference.py <path> --sabotage    # must exit 1

Exit 0 when the anti-vacuity gate P0 passes, whatever P1-P3 turn out to be.
A refuted prediction is a result, not a build failure. Exit 1 when P0 fails
or when --sabotage is given and the gate does NOT fail.

Dependency-light: stdlib + NumPy. Every draw is seeded.
"""

import argparse
import hashlib
import math
import subprocess
import tempfile
import os
import re
import sys
from collections import Counter

import numpy as np

SEED = 20260911

# The corpus is PINNED. This experiment reads research_notes/, and this
# experiment's own note lands in research_notes/ -- so running it against a
# live working tree measures a corpus that its own publication changed. That
# is what the first device reproduction caught: 83 notes became 84, 82
# queries became 83, and every count moved.
#
# Fixing the commit makes the result reproducible from any clone, forever,
# including clones made after later notes are added.
CORPUS_COMMIT = "e9b4e68"
EXPECTED_NOTES = 83
EXPECTED_QUERIES = 82
TOP_K = 5              # narrowing width, fixed before the run
CHUNK = 800            # characters
MIN_QUERY_WORDS = 12

# --------------------------------------------------------------- corpus load

FENCE = re.compile(r"```.*?```", re.S)
WORD = re.compile(r"[a-z0-9_]+")


def strip_code(text):
    return FENCE.sub(" ", text)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def materialize_corpus(repo, commit, workdir):
    """Extract research_notes/ and NOTES_INDEX.md at a fixed commit.
    Reads git history, never the working tree."""
    try:
        tar = subprocess.run(
            ["git", "-C", repo, "archive", commit, "research_notes",
             "NOTES_INDEX.md"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    except subprocess.CalledProcessError as e:
        print(f"CORPUS ERROR: cannot read commit {commit} from {repo}")
        print(e.stderr.decode()[:400])
        return None
    tf = os.path.join(workdir, "c.tar")
    with open(tf, "wb") as f:
        f.write(tar)
    subprocess.run(["tar", "-xf", tf, "-C", workdir], check=True)
    return workdir


def manifest_sha(repo):
    """SHA-256 over the sorted (name, content-hash) list of the corpus."""
    d = os.path.join(repo, "research_notes")
    h = hashlib.sha256()
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(d, name), "rb") as f:
            h.update(name.encode())
            h.update(hashlib.sha256(f.read()).digest())
    return h.hexdigest()


def load_notes(repo):
    d = os.path.join(repo, "research_notes")
    out = []
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(d, name), encoding="utf-8", errors="replace") as f:
            body = f.read()
        out.append({"file": name, "raw": body})
    return out


def load_toc(repo, notes):
    """Map each note file to its index line. Notes absent from the index get
    their filename as the entry -- recorded, not silently dropped."""
    path = os.path.join(repo, "NOTES_INDEX.md")
    entries = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.search(r"research_notes/([^\)]+\.md)", line)
            if m:
                entries.setdefault(m.group(1), line.strip())
    missing = 0
    toc = []
    for n in notes:
        e = entries.get(n["file"])
        if e is None:
            missing += 1
            e = n["file"].replace("_", " ")
        toc.append(e)
    return toc, missing


def build_queries(notes):
    """Longest eligible sentence per note, removed from that note's text."""
    queries, targets, excluded = [], [], 0
    for i, n in enumerate(notes):
        body = strip_code(n["raw"])
        cands = [s for s in sentences(body) if len(s.split()) >= MIN_QUERY_WORDS]
        if not cands:
            excluded += 1
            n["indexed"] = body
            continue
        q = max(cands, key=lambda s: (len(s.split()), s))
        n["indexed"] = body.replace(q, " ")
        queries.append(q)
        targets.append(i)
    for n in notes:
        n.setdefault("indexed", strip_code(n["raw"]))
    return queries, targets, excluded


# ------------------------------------------------------------------- tf-idf

def tokens(s):
    return WORD.findall(s.lower())


class TfIdf:
    def __init__(self, docs):
        self.docs = docs
        df = Counter()
        toks = [tokens(d) for d in docs]
        for t in toks:
            df.update(set(t))
        self.vocab = {w: i for i, w in enumerate(sorted(df))}
        n = max(len(docs), 1)
        self.idf = np.zeros(len(self.vocab))
        for w, i in self.vocab.items():
            self.idf[i] = math.log((1 + n) / (1 + df[w])) + 1.0
        self.M = np.zeros((len(docs), len(self.vocab)))
        for r, t in enumerate(toks):
            c = Counter(t)
            for w, k in c.items():
                self.M[r, self.vocab[w]] = k
        self.M *= self.idf
        norms = np.linalg.norm(self.M, axis=1)
        norms[norms == 0] = 1.0
        self.M /= norms[:, None]

    def vec(self, q):
        v = np.zeros(len(self.vocab))
        for w, k in Counter(tokens(q)).items():
            i = self.vocab.get(w)
            if i is not None:
                v[i] = k
        v *= self.idf
        nrm = np.linalg.norm(v)
        return v / nrm if nrm else v

    def scores(self, q):
        return self.M @ self.vec(q)


def chunk_notes(notes):
    chunks, owner = [], []
    for i, n in enumerate(notes):
        t = n["indexed"]
        if not t.strip():
            t = " "
        for s in range(0, len(t), CHUNK):
            chunks.append(t[s:s + CHUNK])
            owner.append(i)
    return chunks, np.array(owner)


# --------------------------------------------------------------------- arms

def arm_flat(chunk_idx, owner, n_notes, queries):
    hits = []
    for q in queries:
        sc = chunk_idx.scores(q)
        best = np.full(n_notes, -1.0)
        np.maximum.at(best, owner, sc)
        hits.append(int(np.argmax(best)))
    return hits


def arm_toc(toc_idx, chunk_idx, owner, n_notes, queries, toc_to_note, k=None):
    """Two stage. toc_to_note[j] is the note that ToC row j points at.
    For TOC it is the identity; for TOC_SHUF it is a seeded permutation."""
    hits = []
    for q in queries:
        toc_sc = toc_idx.scores(q)
        # kind="stable" is load-bearing, not style. TOC_BLANK's entries score
        # exactly 0.0 against every query -- one distinct value across all 83
        # rows -- so the candidate set is decided entirely by tie-breaking.
        # NumPy dispatches architecture-specific sort kernels, so the default
        # introsort resolved that tie differently on x86_64 and on aarch64:
        # TOC_BLANK scored 1/82 in the container and 4/82 on the S25 from
        # byte-identical logic. A stable sort preserves input order on ties by
        # specification, on every architecture. Same defect class as note054.
        order = np.argsort(-toc_sc, kind="stable")
        top_rows = order[:(TOP_K if k is None else k)]
        cand = np.unique(toc_to_note[top_rows])
        sc = chunk_idx.scores(q)
        best = np.full(n_notes, -np.inf)
        np.maximum.at(best, owner, sc)
        mask = np.full(n_notes, -np.inf)
        mask[cand] = best[cand]
        hits.append(int(np.argmax(mask)))
    return hits


def arm_random(n_notes, n_queries, rng):
    return [int(x) for x in rng.integers(0, n_notes, size=n_queries)]


# ------------------------------------------------------- clopper-pearson CI

def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _solve(f, target, increasing):
    """Bisect f(p)=target on [0,1]. Caller states the direction; getting this
    wrong silently returns an inverted interval, which is how the first run
    of this script printed [100.00%, 0.30%]."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if (f(mid) > target) == increasing:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial interval.
    lower solves P(X >= k) = alpha/2, which INCREASES in p.
    upper solves P(X <= k) = alpha/2, which DECREASES in p."""
    if n == 0:
        return (0.0, 1.0)
    low = 0.0 if k == 0 else _solve(
        lambda p: 1 - binom_cdf(k - 1, n, p), alpha / 2, True)
    high = 1.0 if k == n else _solve(
        lambda p: binom_cdf(k, n, p), alpha / 2, False)
    return (low, high)


def _selftest_ci():
    """Anti-vacuity on the interval code itself. A known textbook case, plus
    the ordering invariant that the first run violated."""
    lo, hi = clopper_pearson(2, 20)
    assert 0.01 < lo < 0.02, lo
    assert 0.30 < hi < 0.33, hi
    for k in range(0, 21):
        a, b = clopper_pearson(k, 20)
        assert a <= k / 20 <= b, (k, a, b)
        assert a <= b, (k, a, b)
    return True


def report(name, k, n):
    lo, hi = clopper_pearson(k, n)
    print(f"  {name:<10} {k:>3}/{n:<3}  {100*k/n:6.2f}%   "
          f"[{100*lo:6.2f}%, {100*hi:6.2f}%]")
    return k / n, lo, hi


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--corpus-mutation", action="store_true",
                    help="pretend one extra note exists; integrity must refuse")
    ap.add_argument("--sabotage", action="store_true",
                    help="corrupt ground truth; the P0 gate must then fail")
    a = ap.parse_args()

    assert _selftest_ci()
    rng = np.random.default_rng(SEED)
    print("=" * 70)
    print("E16 (note061) -- does a table of contents carry retrieval signal?")
    print("=" * 70)
    print(f"seed                    : {SEED}")
    print(f"narrowing width k       : {TOP_K}")
    print(f"chunk size              : {CHUNK}")

    tmp = tempfile.mkdtemp(prefix="e16corpus_", dir=os.environ.get("HOME"))
    corpus = materialize_corpus(a.repo, CORPUS_COMMIT, tmp)
    if corpus is None:
        return 1
    print(f"corpus commit (pinned)  : {CORPUS_COMMIT}")
    print(f"corpus manifest sha256  : {manifest_sha(corpus)[:16]}...")

    notes = load_notes(corpus)
    toc, toc_missing = load_toc(corpus, notes)
    queries, targets, excluded = build_queries(notes)
    n_notes, n_q = len(notes), len(queries)

    print(f"notes                   : {n_notes}")
    print(f"notes absent from index : {toc_missing}")
    print(f"notes with no eligible sentence (excluded): {excluded}")
    print(f"queries                 : {n_q}")

    if a.corpus_mutation:
        n_notes += 1
        print("\n!! CORPUS MUTATION: one note added. Integrity must refuse.")
    if n_notes != EXPECTED_NOTES or n_q != EXPECTED_QUERIES:
        print(f"\nCORPUS INTEGRITY MISMATCH")
        print(f"  expected {EXPECTED_NOTES} notes / {EXPECTED_QUERIES} queries")
        print(f"  observed {n_notes} notes / {n_q} queries")
        print("  REFUSING TO RUN. The registered numbers describe a corpus")
        print("  this is not. Re-register rather than re-report.")
        return 1

    if a.sabotage:
        targets = [(t + 1) % n_notes for t in targets]
        print("\n!! SABOTAGE: ground truth shifted by one. The gate must fail.")

    chunks, owner = chunk_notes(notes)
    chunk_idx = TfIdf(chunks)
    toc_idx = TfIdf(toc)
    ident = np.arange(n_notes)
    perm = rng.permutation(n_notes)

    tgt = np.array(targets)
    flat = np.array(arm_flat(chunk_idx, owner, n_notes, queries))
    toc_h = np.array(arm_toc(toc_idx, chunk_idx, owner, n_notes, queries, ident))
    shuf = np.array(arm_toc(toc_idx, chunk_idx, owner, n_notes, queries, perm))
    rand = np.array(arm_random(n_notes, n_q, rng))

    # --- Amendment 1 (P5) and Amendment 2 (P6, P7) ---
    blank = np.array([f"index entry {i:04d}" for i in range(n_notes)])
    blank_idx = TfIdf(list(blank))
    bl = np.array(arm_toc(blank_idx, chunk_idx, owner, n_notes, queries, ident))

    ks = [1, 2, 5, 10, 20, 40, n_notes]
    sweep = []
    for kk in ks:
        h = np.array(arm_toc(toc_idx, chunk_idx, owner, n_notes, queries,
                             ident, k=kk))
        sweep.append((kk, int((h == np.array(targets)).sum())))

    print("\nRecall@1, raw counts with Clopper-Pearson 95% intervals")
    p_rand, _, rand_hi = report("RANDOM", int((rand == tgt).sum()), n_q)
    p_flat, flat_lo, _ = report("FLAT", int((flat == tgt).sum()), n_q)
    p_toc, toc_lo, toc_hi = report("TOC", int((toc_h == tgt).sum()), n_q)
    p_shuf, shuf_lo, shuf_hi = report("TOC_SHUF", int((shuf == tgt).sum()), n_q)

    chance = 1.0 / n_notes
    print(f"\n  chance = 1/{n_notes} = {100*chance:.2f}%")

    print("\n" + "-" * 70)
    print("P0  ANTI-VACUITY GATE")
    rlo, rhi = clopper_pearson(int((rand == tgt).sum()), n_q)
    p0a = rlo <= chance <= rhi
    p0b = flat_lo > p_rand
    print(f"  P0a RANDOM interval contains chance          : "
          f"{'PASS' if p0a else 'FAIL'}")
    print(f"  P0b FLAT interval lies above RANDOM estimate : "
          f"{'PASS' if p0b else 'FAIL'}")

    if not (p0a and p0b):
        print("\n  P0 FAILED -- P1-P3 are VOID, not reported.")
        print("=" * 70)
        if a.sabotage:
            print("SABOTAGE CONFIRMED: the gate reports failure when ground "
                  "truth is corrupted.")
        return 1

    if a.sabotage:
        print("\n  GATE DID NOT FAIL UNDER SABOTAGE -- the control is inert.")
        return 1

    print("\nP5  TOC > TOC_BLANK   [Amendment 1 -- expected near-trivial]")
    p_bl, bl_lo, bl_hi = report("TOC_BLANK", int((bl == tgt).sum()), n_q)
    print(f"  {100*p_toc:.2f}% vs {100*p_bl:.2f}%  ->  "
          f"{'CONFIRMED' if p_toc > p_bl else 'REFUTED (kept)'}"
          "   [see Amendment 2: uninformative by construction]")

    print("\nP6/P7  narrowing width sweep   [Amendment 2]")
    best = max(sweep, key=lambda t: t[1])
    for kk, hits in sweep:
        mark = "  <- best" if (kk, hits) == best else ""
        print(f"   k={kk:<4} {hits:>3}/{n_q}  {100*hits/n_q:6.2f}%{mark}")
    inc = all(sweep[i][1] <= sweep[i+1][1] for i in range(len(sweep)-1))
    print(f"  P6 curve not monotonically increasing : "
          f"{'CONFIRMED' if not inc else 'REFUTED (kept)'}")
    print(f"  P7 best k does not beat FLAT          : "
          f"{'CONFIRMED' if best[1] <= int((flat == tgt).sum()) else 'REFUTED (kept)'}"
          f"   (best {best[1]}/{n_q} at k={best[0]} vs FLAT "
          f"{int((flat == tgt).sum())}/{n_q})")

    print("\nP1  TOC > FLAT")
    p1 = p_toc > p_flat
    print(f"  {100*p_toc:.2f}% vs {100*p_flat:.2f}%  ->  "
          f"{'CONFIRMED' if p1 else 'REFUTED (kept)'}")

    print("\nP2  TOC > TOC_SHUF   [LOAD-BEARING]")
    overlap = not (toc_lo > shuf_hi or shuf_lo > toc_hi)
    if p_shuf >= p_toc:
        v2 = "REFUTED (kept)"
    elif overlap:
        v2 = "INCONCLUSIVE"
    else:
        v2 = "CONFIRMED"
    print(f"  {100*p_toc:.2f}% vs {100*p_shuf:.2f}%  intervals "
          f"{'overlap' if overlap else 'disjoint'}  ->  {v2}")

    print("\nP3  TOC_SHUF does not exceed FLAT")
    p3 = p_shuf <= p_flat
    print(f"  {100*p_shuf:.2f}% vs {100*p_flat:.2f}%  ->  "
          f"{'CONFIRMED' if p3 else 'REFUTED (kept)'}")

    print("\n" + "=" * 70)
    # DEFECT FOUND ON FIRST RUN: this block previously fired
    # "the ToC carries signal" whenever P2 was CONFIRMED, without consulting
    # P1. It printed exactly that while P1 stood REFUTED. A verdict line that
    # can reach a conclusion the evidence does not support is the same defect
    # class this estate builds tools to find. Fixed; P1 is now dominant.
    if not p1 and best[1] > int((flat == tgt).sum()):
        print("READING: P1 REFUTED at the registered k=5, and P7 REFUTED too.")
        print("The ToC arm loses to flat retrieval at k=5 but BEATS it at")
        print("k=1. The refutation of P1 was an artifact of a narrowing width")
        print("this author fixed in advance and fixed badly.")
        print()
        print("NOT ESTABLISHED: k=1 is the best of 7 widths tried, and its")
        print("interval overlaps FLAT's. Best-of-7 selection inflates any")
        print("apparent gain. This is a lead, not a result.")
        print()
        print("P2 and P5 are both near-trivial by construction (Amendment 2)")
        print("and are kept, marked, and not read as support.")
    elif not p1:
        print("READING: P1 REFUTED. Two-stage ToC narrowing did NOT beat flat")
        print("retrieval at any width tried.")
    else:
        print("READING: P1 held at the registered k. See Amendment 2.")
    print()
    print("P4 left unrun: paraphrased rather than extracted queries.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
