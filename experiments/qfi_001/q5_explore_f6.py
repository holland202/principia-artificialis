#!/usr/bin/env python3
"""QFI-001 Q5, EXPLORATORY (C-EXPLORE; written after the registered Q5 run was seen). Author: Claude (Anthropic, Opus 5.5).
Question: why does split_resolved_q4 fail at trained layer 0 only in frame F6? Usage: python -I experiments/qfi_001/q5_explore_f6.py"""
# Post-run check (C-EXPLORE): why G5 fails at layer 0 in frame F6 only. Dev pairs only; Q5 has already run.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q5_run as q, numpy as np, qfi_ref
q.patch_softmax64()
models, tok, ok = q.q3.load_models(os.path.expanduser("~/.cache/qfi001_q3"))
pairs, _ = q.pair_list(tok)
for fid, frame, _ in q.f4.FRAMES:
    ids = tok.encode(frame.format("X")).ids
    dup = len(ids) - len(set(ids))
    print(f"{fid} '{frame}': tokens {len(ids)}, repeated token ids {dup}")
P = next(p for p in pairs if p["frame"] == "F6" and p["split"] == "dev")
f = q.Forward5(models[q.LABELS[0]])
for L in (0, 1):
    for th in (0.0, 0.5):
        hs, _ = f(P["ia"], P["ib"], th)
        A = hs[L]
        rho = q.sym(A.T @ A / np.trace(A.T @ A)); pe = np.linalg.eigh(rho)[0]
        fl = q.flags_q4(pe, qfi_ref.tie_blocks(pe), A.shape[0], 1e-6)
        print(f"F6 pair {P['wa']}/{P['wb']} L{L} theta {th}: n {A.shape[0]}, rank(A) {np.linalg.matrix_rank(A)}, "
              f"structural zeros {fl['n_struct']} (d - n = {128 - A.shape[0]}), q4 {fl['q4']}, srs {fl['srs']}")
