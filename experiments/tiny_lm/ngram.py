"""Simplest rival (M14): byte n-gram model with interpolated absolute discounting (D=0.75), orders 1..8.
Usage: python3 ngram.py TRAIN_BYTES N_EVAL. Trains on the first TRAIN_BYTES of the train slice; scores bits per
byte on valid bytes 1..N_EVAL (each byte predicted from the bytes before it in the valid stream).
Claude (Anthropic, Opus 5.5), 2026-11-21. SELF-TESTED only."""
import math, sys
import numpy as np
NTR, NEV, D = int(sys.argv[1]), int(sys.argv[2]), 0.75
tr = np.fromfile("data/v2_train_200MB.txt", dtype=np.uint8, count=NTR).astype(np.int64)
va = np.fromfile("data/v2_valid.txt", dtype=np.uint8, count=NEV + 1).astype(np.int64)

def keys(a, n):                      # int64 key of each n-gram ending at position i (i >= n-1)
    k = np.zeros(len(a) - n + 1, np.int64)
    for j in range(n):
        k = (k << 8) | a[j:len(a) - n + 1 + j]
    return k

uni = np.bincount(tr, minlength=256).astype(np.float64)
p = np.tile((uni + 1) / (uni.sum() + 256), 1)          # order 1 (add-one), indexed by next byte
prob = p[va[1:]]                                       # probability of each eval byte under the current order
print(f"order 1  valid bpb {-np.log2(prob).mean():.4f}")
for n in range(2, 9):
    g = keys(tr, n); ug, cg = np.unique(g, return_counts=True)
    ctx = ug >> 8; uc, first, nplus = np.unique(ctx, return_index=True, return_counts=True)
    ch = np.add.reduceat(cg, first).astype(np.float64)
    q = keys(va, n)                                    # eval n-grams: targets va[n-1:], we score positions >= 1
    qc = q >> 8
    gi = np.searchsorted(ug, q); gi[gi >= len(ug)] = 0; cnt = np.where(ug[gi] == q, cg[gi], 0).astype(np.float64)
    ci = np.searchsorted(uc, qc); ci[ci >= len(uc)] = 0; seen = uc[ci] == qc
    chq = np.where(seen, ch[ci], 0.0); npq = np.where(seen, nplus[ci], 0)
    lower = prob[n - 2:]                               # lower-order prob for the same targets (positions n-1..)
    newp = np.where(seen, np.maximum(cnt - D, 0) / np.maximum(chq, 1) + D * npq / np.maximum(chq, 1) * lower, lower)
    prob = np.concatenate([prob[:n - 2], newp])        # first n-2 targets keep the lower order (too little context)
    print(f"order {n}  valid bpb {-np.log2(prob).mean():.4f}", flush=True)
