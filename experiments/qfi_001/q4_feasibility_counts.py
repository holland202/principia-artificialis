#!/usr/bin/env python3
"""QFI-001 Q4, C-FEAS step: count the input pairs the Q4 design depends on, before Q4 is registered.

Counts only (CONTROLS.md C-FEAS). It tokenises the template sentences with the pinned pythia-14m tokenizer and prints
how many pairs qualify, per frame and per split, and the cost the design implies. No model is run, no activation and
no output distribution is computed, and no truth value exists for these inputs.

The frames, word lists, qualifying rule, exclusion rule and split rule below were written before this script was first
run. Author: Claude (Anthropic, Opus 5.5). Needs `tokenizers` and network access to huggingface.co.
Usage:  python -I experiments/qfi_001/q4_feasibility_counts.py [cache_dir]
"""
import hashlib
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import q3_feasibility_counts as fc  # noqa: E402  (pinned identities and fetch; not copied)

# Frames: one slot "{}" each, no final punctuation, so the last position predicts a content word.
FRAMES = [
    ("F1", "The {} sat on the", "N"),
    ("F2", "My friend bought a {} and put it in the", "N"),
    ("F3", "She saw a {} house near the", "A"),
    ("F4", "He was very {} when he heard the", "E"),
    ("F5", "They {} to the store and bought some", "V"),
    ("F6", "In the {} we went to the", "T"),
]
WORDS = {
    "N": ["cat", "dog", "bird", "horse", "cow", "book", "cup", "box", "car", "boy", "girl", "man", "woman",
          "child", "chair", "table"],
    "A": ["big", "small", "old", "new", "red", "blue", "green", "white", "black", "tall"],
    "E": ["happy", "sad", "angry", "tired", "afraid", "surprised", "glad", "calm", "proud", "excited"],
    "V": ["went", "ran", "walked", "drove", "rushed", "hurried"],
    "T": ["morning", "evening", "afternoon", "summer", "winter", "spring", "night"],
}
# Q3's calibration pairs moved these word pairs; a Q4 pair that moves the same two words is excluded.
Q3_WORD_PAIRS = [{"cat", "dog"}, {"smiled", "cried"}, {"cold", "warm"}]
THETAS = 11
LAYERS = 7
MODELS = 2
STEPS = 2            # h = 1e-4 and h = 1e-5 (step-convergence gate)
SPLIT_SALT = "qfi001-q4-split"
DEV_BELOW = 86       # first byte of sha256(salt|frame|w_a|w_b) < 86 -> dev (about one third), else test


def split_of(frame_id, wa, wb):
    b0 = hashlib.sha256(f"{SPLIT_SALT}|{frame_id}|{wa}|{wb}".encode()).digest()[0]
    return "dev" if b0 < DEV_BELOW else "test"


def main():
    cache = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.cache/qfi001_q3")
    rev = fc.REVS["trained (main, step143000)"]
    t = fc.fetch(rev, "tokenizer.json", cache)
    good = fc.git_blob_sha1(t) == fc.BLOB["tokenizer.json"]
    print(f"tokenizer rev {rev[:12]} identity {'MATCH' if good else 'MISMATCH'}")
    from tokenizers import Tokenizer
    tk = Tokenizer.from_file(t)

    single = {}
    for cls, ws in WORDS.items():
        ok = [w for w in ws if len(tk.encode(" " + w).ids) == 1]
        single[cls] = ok
        print(f"class {cls}: {len(ws)} words, single-token with leading space {len(ok)}; dropped "
              f"{sorted(set(ws) - set(ok))}")

    pairs = []
    for fid, frame, cls in FRAMES:
        n_ok = n_bad = n_excl = 0
        lens = set()
        for wa, wb in itertools.combinations(WORDS[cls], 2):
            if wa not in single[cls] or wb not in single[cls]:
                continue
            ia, ib = tk.encode(frame.format(wa)).ids, tk.encode(frame.format(wb)).ids
            same = len(ia) == len(ib)
            ndiff = sum(x != y for x, y in zip(ia, ib)) if same else None
            if not (same and ndiff == 1):
                n_bad += 1
                continue
            if {wa, wb} in Q3_WORD_PAIRS:
                n_excl += 1
                continue
            n_ok += 1
            lens.add(len(ia))
            pairs.append((fid, wa, wb, split_of(fid, wa, wb), len(ia)))
        print(f"{fid} '{frame}': qualifying pairs {n_ok}, not one-position {n_bad}, excluded as Q3 {n_excl}, "
              f"token lengths {sorted(lens)}")

    n_dev = sum(p[3] == "dev" for p in pairs)
    n_test = sum(p[3] == "test" for p in pairs)
    print(f"total qualifying pairs {len(pairs)}: dev {n_dev}, test {n_test}")
    for fid, _, _ in FRAMES:
        d = sum(p[3] == "dev" and p[0] == fid for p in pairs)
        e = sum(p[3] == "test" and p[0] == fid for p in pairs)
        print(f"  {fid}: dev {d} test {e}")
    words_dev = {w for p in pairs if p[3] == "dev" for w in p[1:3]}
    words_test = {w for p in pairs if p[3] == "test" for w in p[1:3]}
    print(f"distinct moved words: dev {len(words_dev)}, test {len(words_test)}, in both {len(words_dev & words_test)}")
    for split, n in (("dev", n_dev), ("test", n_test)):
        pts = MODELS * n * THETAS * LAYERS
        fwd = MODELS * n * THETAS * (1 + 2 * STEPS)
        print(f"{split}: points {MODELS} models x {n} pairs x {THETAS} thetas x {LAYERS} layers = {pts}; "
              f"forward passes {fwd} (theta, and theta +- h for 2 steps)")
    lst = hashlib.sha256("\n".join("|".join(map(str, p)) for p in pairs).encode()).hexdigest()
    print(f"pair list sha256 {lst}")
    ok = good and n_dev >= 40 and n_test >= 80
    print("FEASIBILITY COUNTS", "COMPLETE" if ok else "INCOMPLETE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
