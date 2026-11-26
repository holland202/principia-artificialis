#!/usr/bin/env python3
"""QFI-001 Q3, C-FEAS step: print the counts the Q3 design depends on, before Q3 is registered.

Counts only (CONTROLS.md C-FEAS): file identities, model shape, token counts of the candidate input pairs, and the
number of points and forward passes the design implies. No model is run and no activation is computed.

Author: Claude (Anthropic, Opus 5.5). Needs `tokenizers` and network access to huggingface.co.
Usage:  python -I experiments/qfi_001/q3_feasibility_counts.py [cache_dir]
"""
import hashlib
import json
import os
import struct
import sys
import urllib.request

REPO = "EleutherAI/pythia-14m"
REVS = {  # revision name -> pinned commit
    "trained (main, step143000)": "cf967c0a9a04383db6f7b1108d86b2962634b4ac",
    "untrained (step0)": "56079904bb80b7f36d3b794089f146e7a4d6efae",
}
# Pinned identities: git blob sha1 for small files, sha256 for the LFS weights (from the Hub tree API).
BLOB = {"config.json": "d79c7e3f60eb0966575057b690330e3d6d4fcd5c",
        "tokenizer.json": "eb39a3d940ed41b696b46287f39ba3b76aad03f6"}
WEIGHTS_SHA256 = {"cf967c0a9a04383db6f7b1108d86b2962634b4ac":
                  "116a02532db461f91386a5b20f942ff2c8d4de7341e21b55caafc3d7b25f49a1",
                  "56079904bb80b7f36d3b794089f146e7a4d6efae":
                  "495e509ae82ddbe9cf39558a13b10973822c7bcedd0c6fd7d3225620b9e2edb5"}

# Candidate pairs, in this order. Selection rule (fixed before any count was seen): keep a pair only if both sides
# have the same token count and differ at exactly one token position; take the first three that qualify.
CANDIDATES = [
    ("The cat sat on the mat.", "The dog sat on the mat."),
    ("She opened the door and smiled.", "She opened the door and cried."),
    ("The river was cold in the morning.", "The river was warm in the morning."),
    ("He put the book on the table.", "He put the cup on the table."),
    ("The children played in the park.", "The children played in the snow."),
    ("A small bird sang near the window.", "A small dog barked near the window."),
]
THETAS = 11          # theta = 0, 0.1, ..., 1
FD_EVALS = 3         # theta - h, theta, theta + h
LAYERS_NOTE = "all hidden_states entries (embeddings + each block)"


def fetch(rev, name, cache):
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, f"{rev[:12]}_{name}")
    if not os.path.exists(path):
        url = f"https://huggingface.co/{REPO}/resolve/{rev}/{name}"
        with urllib.request.urlopen(url, timeout=120) as r, open(path + ".part", "wb") as f:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                f.write(b)
        os.replace(path + ".part", path)
    return path


def git_blob_sha1(path):
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def safetensors_counts(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        hdr = json.loads(f.read(n))
    hdr.pop("__metadata__", None)
    params = 0
    dtypes = set()
    for v in hdr.values():
        k = 1
        for s in v["shape"]:
            k *= s
        params += k
        dtypes.add(v["dtype"])
    return len(hdr), params, sorted(dtypes)


def main():
    cache = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.cache/qfi001_q3")
    ok = True
    cfg = None
    tok_path = None
    for label, rev in REVS.items():
        c = fetch(rev, "config.json", cache)
        t = fetch(rev, "tokenizer.json", cache)
        w = fetch(rev, "model.safetensors", cache)
        cb, tb, ws = git_blob_sha1(c), git_blob_sha1(t), sha256(w)
        good = cb == BLOB["config.json"] and tb == BLOB["tokenizer.json"] and ws == WEIGHTS_SHA256[rev]
        ok &= good
        nt, npar, dts = safetensors_counts(w)
        print(f"{label:28s} rev {rev[:12]} identities {'MATCH' if good else 'MISMATCH'} "
              f"tensors {nt} stored-values {npar} dtypes {dts}")
        cfg = json.load(open(c))
        tok_path = t
    print("config: hidden_size {hidden_size} layers {num_hidden_layers} heads {num_attention_heads} "
          "vocab {vocab_size} rotary_pct {rotary_pct} parallel_residual {use_parallel_residual}".format(**cfg))
    d, L = cfg["hidden_size"], cfg["num_hidden_layers"]

    from tokenizers import Tokenizer
    tk = Tokenizer.from_file(tok_path)
    chosen = []
    for i, (a, b) in enumerate(CANDIDATES):
        ia, ib = tk.encode(a).ids, tk.encode(b).ids
        same_len = len(ia) == len(ib)
        ndiff = sum(x != y for x, y in zip(ia, ib)) if same_len else None
        qual = same_len and ndiff == 1
        if qual and len(chosen) < 3:
            chosen.append(i)
        print(f"pair {i}: tokens {len(ia)} vs {len(ib)} differing positions {ndiff} qualifies {qual}")
    print(f"chosen pairs (first three that qualify): {chosen}")
    ok &= len(chosen) == 3
    n_tok = [len(tk.encode(CANDIDATES[i][0]).ids) for i in chosen]
    layers = L + 1
    points = len(REVS) * len(chosen) * THETAS * layers
    passes = len(REVS) * len(chosen) * THETAS * FD_EVALS
    print(f"density matrix size d = {d}; tokens per input n = {n_tok}; structural kernel d - n = {[d - n for n in n_tok]}")
    print(f"layers per point: {layers} ({LAYERS_NOTE}); points = {len(REVS)} models x {len(chosen)} pairs x "
          f"{THETAS} thetas x {layers} layers = {points}")
    print(f"forward passes (central difference, all layers per pass) = {passes}, plus the noise and step checks")
    print("FEASIBILITY COUNTS", "COMPLETE" if ok else "INCOMPLETE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
