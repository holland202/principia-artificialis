#!/usr/bin/env python3
"""QFI-001 Q5 harness (development run on dev pairs) and Q6 harness (--split test, run once, unchanged).

Registration: Q4_PREREG.md (23679c2) + Q4_AMENDMENT1.md (d9337c3) + Q4_AMENDMENT2.md (2fc82ad), each committed before
this file existed. Authority: Chad Holland's delegation, PR #181 comment 7141782954. It imports qfi_ref (Amendment 4
code, 5c6f772), q3_run (rho_drho, split_resolved_support, run_controls, synth_A, rot, load_models, save_npz),
q3_feasibility_counts (pinned identities) and q4_feasibility_counts (frames, words, split rule); it copies none of
their functions. Author: Claude (Anthropic, Opus 5.5). SELF-TESTED only. Needs numpy, torch, transformers,
safetensors, tokenizers, and network access to huggingface.co (weights fetched by pinned revision, checked by sha256,
never committed).

Implementation choices the registration does not fix (each is disclosed in Q5_RESULTS.md):
  I1  G2's dtype check cannot fail on its own: eager attention casts the float32 softmax back to float64. G2 also
      requires that some attention weight is not exactly representable in float32 (a float32 softmax would make every
      weight representable), and that the in-memory softmax patch is installed.
  I2  G6 "symmetric": the raw rho = A^T A / tr, before the registered symmetrisation, has max|rho - rho^T| <= 1e-14
      (Q3's R3 tolerance). After symmetrisation the check would be vacuous.
  I3  N1, N2 and the Q4 flag of S3 use the exact derivative of a rotation path, drho = G rho + rho G^T, at theta = 0.
      S1-S3 (Q3) are run unchanged through q3_run.run_controls (central differences).
  I4  z = numpy.random.default_rng(20261126).standard_normal(364), one draw per pair of the full registered pair list
      in list order; pair i uses z[i] at Q5 and Q6, on both models. Standard deviations use ddof = 0.
  I5  A layer whose A model is rank-deficient is ineligible in layer selection, like SSE_A = 0.
  I6  PC/NC are run on both models; P3 is judged on both. OUTCOME-SCREENED is applied if either model crosses 5%.
  I7  Verdict precedence (Amendment 2 item 4) is applied literally: any UNDECIDABLE or CONTESTED component (H1 on
      either model, PC/NC, H2-P, H2-own) sets the row, and EXCLUSION-SENSITIVE sets INDETERMINATE even if H1 fails on
      trained. The Q4_PREREG and Amendment 1 verdicts are printed alongside.
  I8  Pre-dev gates (G12, G0, G1, G2, G3, G9, G10) stop the run when one fails: no Q4 pair is then computed.
  I9  The interchange subset is the first dev pair in list order, theta in {0, 0.5, 1}, all layers, both models,
      with A, dA(h) and dA(h'), plus this harness's F values and flags.
  I10 The digest covers every per-point record, numbers formatted to 10 significant digits, plus tau_q4.

Usage:  python -I experiments/qfi_001/q5_run.py --selftest                        (G12 only, model-free)
        python -I experiments/qfi_001/q5_run.py [--sabotage] [--cache DIR]       (Q5, dev pairs)
        python -I experiments/qfi_001/q5_run.py --split test --q5-results results/qfi_001/q5/results.json   (Q6)
        (--child is internal: the G7 repeat in a second process, prints only the DIGEST line)
"""
import argparse
import hashlib
import itertools
import json
import math
import os
import resource
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import qfi_ref  # noqa: E402
import q3_run as q3  # noqa: E402
import q3_feasibility_counts as fc  # noqa: E402
import q4_feasibility_counts as f4  # noqa: E402

EPS = qfi_ref.EPS              # 1e-12
SMALL = 1e-6                   # no eigenvalue in (eps/2, 1e-6]; also the tau floor
H1_STEP, H2_STEP = 1e-4, 1e-5  # h and h'
THETAS = [i / 10 for i in range(11)]
LAYERS = 7
D_MODEL = 128
FLOOR = 1e-300
PAIR_LIST_SHA256 = "ad19d82764d30b7ede6c720f60f51407b790892a0ae3be2760b33b0109c247a4"
N_DEV, N_TEST = 123, 241
RNG_SEED = 20261126
LABELS = list(fc.REVS)         # [trained, step0]
SABOTAGE = False


# ================================================================ statistics (model-free; G12 exercises these)

def binom_tail(n, k):
    """P(Binom(n, 1/2) >= k), exact."""
    if n == 0:
        return 1.0
    return sum(math.comb(n, j) for j in range(max(k, 0), n + 1)) / 2 ** n


def design(F, with_r):
    cols = [np.ones(len(F["c"])), F["c"], F["s"], F["h"]] + ([F["r"]] if with_r else [])
    return np.column_stack(cols)


def ols(X, y):
    """Least squares with a rank check. Returns (beta, full_rank)."""
    full = bool(np.linalg.matrix_rank(X) == X.shape[1]) if len(y) >= X.shape[1] else False
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return beta, full


def loo_errors(X, y):
    """Leave-one-pair-out errors (explicit refits). Returns (errors, all folds and the full fit full rank)."""
    n = len(y)
    _, full = ols(X, y)
    e = np.zeros(n)
    for i in range(n):
        m = np.arange(n) != i
        b, ok = ols(X[m], y[m])
        full &= ok
        e[i] = y[i] - X[i] @ b
    return e, full


def h1_procedure(eA, eB, frames, frame_ids):
    """H1 (a), (b), (c) on given errors; Amendment 1 sections 3 and 7. Returns a dict with outcome in
    {HOLDS, FAILS, CONTESTED, UNDECIDABLE}."""
    eA, eB = np.asarray(eA, float), np.asarray(eB, float)
    assert len(eA) == len(eB) == len(frames), "A and B must be compared on the identical set of pairs"
    N = len(eA)
    sA, sB = float(np.sum(eA ** 2)), float(np.sum(eB ** 2))
    out = {"N": N, "SSE_A": sA, "SSE_B": sB}
    if N == 0 or sA == 0.0:
        out.update(outcome="UNDECIDABLE", why="no pairs" if N == 0 else "SSE_A = 0")
        return out
    G = (sA - sB) / sA
    k = int(np.sum(eB ** 2 < eA ** 2))  # ties count as not favouring B and stay in N
    p = binom_tail(N, k)
    gf = {}
    for f in frame_ids:
        m = np.array([x == f for x in frames])
        a = float(np.sum(eA[m] ** 2))
        gf[f] = None if (m.sum() == 0 or a == 0.0) else (a - float(np.sum(eB[m] ** 2))) / a
    m_pos = sum(1 for v in gf.values() if v is not None and v > 0)
    a_, b_, c_ = bool(G >= 0.05), bool(p <= 0.05), bool(m_pos >= 4)
    outcome = "HOLDS" if (a_ and b_ and c_) else ("CONTESTED" if (a_ and c_ and not b_) else "FAILS")
    out.update(G=G, k=k, p=p, frame_gain=gf, m=m_pos, m_tail=binom_tail(len(frame_ids), m_pos),
               a=a_, b=b_, c=c_, outcome=outcome)
    return out


def h2_paired(eA_t, eB_t, eA_s, eB_s, scale_t, scale_s):
    """Paired sign test on d_i = u_i(trained) - u_i(step0), u_i = (eA^2 - eB^2) / scale. Arrays are over P."""
    nP = len(eA_t)
    if nP == 0:
        return {"outcome": "UNDECIDABLE", "why": "empty P", "nP": 0}
    if scale_t == 0.0 or scale_s == 0.0:
        return {"outcome": "UNDECIDABLE", "why": "zero denominator", "nP": nP}
    u_t = (np.asarray(eA_t) ** 2 - np.asarray(eB_t) ** 2) / scale_t
    u_s = (np.asarray(eA_s) ** 2 - np.asarray(eB_s) ** 2) / scale_s
    d = u_t - u_s
    k = int(np.sum(d > 0))  # ties count against
    p = binom_tail(nP, k)
    return {"outcome": "HOLDS" if p <= 0.05 else "FAILS", "nP": nP, "k": k, "p": p, "d": d.tolist(),
            "d_median": float(np.median(d))}


def h2_both(t, s):
    """t, s: dict pair_id -> (eA, eB) on each model's own usable set. Returns (H2-P, H2-own)."""
    P = sorted(set(t) & set(s))
    eAt, eBt = np.array([t[i][0] for i in P]), np.array([t[i][1] for i in P])
    eAs, eBs = np.array([s[i][0] for i in P]), np.array([s[i][1] for i in P])
    # Amendment 2 item 1: scale on P only
    scP_t = float(np.sum(eAt ** 2)) / len(P) if P else 0.0
    scP_s = float(np.sum(eAs ** 2)) / len(P) if P else 0.0
    # Amendment 1 section 5: each model's own N
    sc_t = float(np.sum([v[0] ** 2 for v in t.values()])) / len(t) if t else 0.0
    sc_s = float(np.sum([v[0] ** 2 for v in s.values()])) / len(s) if s else 0.0
    hp = h2_paired(eAt, eBt, eAs, eBs, scP_t, scP_s)
    ho = h2_paired(eAt, eBt, eAs, eBs, sc_t, sc_s)
    hp["scale_t"], hp["scale_s"], ho["scale_t"], ho["scale_s"] = scP_t, scP_s, sc_t, sc_s
    return hp, ho


def verdict(h1_t, h1_s, pcnc, h2p, h2o):
    """Amendment 2 item 4 precedence, applied literally (I7). h1_*: outcome strings after anti-vacuity.
    pcnc: list of UNDECIDABLE sources from PC/NC and degenerate cases. Returns (verdict, reasons, registered, amend1)."""
    reasons = []
    und = [f"H1 trained {h1_t}" if h1_t == "UNDECIDABLE" else None,
           f"H1 step0 {h1_s}" if h1_s == "UNDECIDABLE" else None,
           "H2-P UNDECIDABLE" if h2p["outcome"] == "UNDECIDABLE" else None,
           "H2-own UNDECIDABLE" if h2o["outcome"] == "UNDECIDABLE" else None] + list(pcnc)
    und = [u for u in und if u]
    excl_sens = (h2p["outcome"] in ("HOLDS", "FAILS") and h2o["outcome"] in ("HOLDS", "FAILS")
                 and h2p["outcome"] != h2o["outcome"])
    if und:
        v, reasons = "UNDECIDABLE", und
    elif "CONTESTED" in (h1_t, h1_s):
        v, reasons = "CONTESTED", [f"H1 trained {h1_t}, H1 step0 {h1_s}"]
    elif excl_sens:
        v, reasons = "INDETERMINATE", ["EXCLUSION-SENSITIVE (H2-P and H2-own disagree)"]
    elif h1_t == "FAILS":
        v = "NONE"
    elif h2p["outcome"] == "HOLDS":
        v = "LEARNED"
    elif h1_s == "HOLDS":
        v = "ARCHITECTURAL"
    else:
        v, reasons = "INDETERMINATE", ["H1 holds on trained; H2-P and H1 on step0 both fail"]
    t_ok, s_ok = h1_t == "HOLDS", h1_s == "HOLDS"
    registered = "NONE" if not t_ok else ("ARCHITECTURAL" if s_ok else "LEARNED")
    if not t_ok:
        a1 = "NONE"
    elif h2o["outcome"] == "HOLDS":
        a1 = "LEARNED"
    elif s_ok:
        a1 = "ARCHITECTURAL"
    else:
        a1 = "INDETERMINATE"
    return v, reasons, registered, a1


def selftest():
    """G12 (Amendment 2 item 5): ChatGPT's note-027 table from invented errors, plus empty P and SSE_A(P) = 0.
    Extra self-checks of the verdict table follow (author-written, SELF-TESTED)."""
    ok = True
    sh = {i: (1.0, math.sqrt(0.75)) for i in range(12)}
    print("G12 fixture (invented errors; e_A^2 = 1, e_B^2 = 0.75 on 12 shared pairs for both models)")
    for name, s_extra in (("shared only", {}), ("add 12 step0-only A2=9", {100 + i: (3.0, 3.0) for i in range(12)})):
        s = {**sh, **s_extra}
        hp, ho = h2_both(dict(sh), s)
        print(f"{name:24s} amend1(own N): step0 MSE {ho['scale_s']:g} d {ho['d_median']:.2f} k {ho['k']}/{ho['nP']} "
              f"p {ho['p']!r}")
        print(f"{'':24s} scale on P:        d {abs(hp['d_median']):.2f} k {hp['k']}/{hp['nP']} p {hp['p']!r}")
        if s_extra:
            ok &= (ho["k"] == 12 and ho["nP"] == 12 and abs(ho["d_median"] - 0.20) < 1e-12
                   and hp["k"] == 0 and hp["nP"] == 12 and abs(hp["d_median"]) < 1e-12)
        else:
            ok &= ho["k"] == 0 and hp["k"] == 0 and abs(ho["d_median"]) < 1e-12
    hp, _ = h2_both({1: (1.0, 0.5)}, {2: (1.0, 0.5)})
    print(f"empty P: H2-P {hp['outcome']} ({hp.get('why')})")
    ok &= hp["outcome"] == "UNDECIDABLE"
    hp, _ = h2_both({1: (1.0, 0.5), 2: (1.0, 0.5)}, {1: (0.0, 0.0), 2: (0.0, 0.0), 3: (2.0, 1.0)})
    print(f"SSE_A(P) = 0 on step0: H2-P {hp['outcome']} ({hp.get('why')})")
    ok &= hp["outcome"] == "UNDECIDABLE"
    # extra self-checks (not registered): binomial tail, ties, frames, precedence
    extra = []
    extra.append(binom_tail(12, 12) == 0.000244140625 and binom_tail(6, 6) == 1 / 64 and binom_tail(6, 5) == 7 / 64)
    r = h1_procedure([1, 1, 1, 1], [1, 1, 1, 1], ["F1"] * 4, ["F1"])
    extra.append(r["k"] == 0 and r["N"] == 4 and r["outcome"] == "FAILS")
    r = h1_procedure([0, 0], [0, 0], ["F1", "F2"], ["F1", "F2"])
    extra.append(r["outcome"] == "UNDECIDABLE")
    fr = ["F1", "F2", "F3", "F4"] * 3
    r = h1_procedure([1.0] * 12, [0.5] * 12, fr, ["F1", "F2", "F3", "F4", "F5", "F6"])
    extra.append(r["outcome"] == "HOLDS" and r["m"] == 4)  # frames F5, F6 have no pair: counted not > 0
    r = h1_procedure([1.0] * 4, [0.5] * 4, ["F1", "F2", "F3", "F4"], ["F1", "F2", "F3", "F4", "F5", "F6"])
    extra.append(r["outcome"] == "CONTESTED")  # (a) and (c) hold, k = 4 of 4 gives p = 1/16 > 0.05
    H, F, U = {"outcome": "HOLDS"}, {"outcome": "FAILS"}, {"outcome": "UNDECIDABLE"}
    extra.append(verdict("HOLDS", "FAILS", [], H, H)[0] == "LEARNED")
    extra.append(verdict("HOLDS", "HOLDS", [], F, F)[0] == "ARCHITECTURAL")
    extra.append(verdict("HOLDS", "FAILS", [], F, F)[0] == "INDETERMINATE")
    extra.append(verdict("FAILS", "FAILS", [], F, F)[0] == "NONE")
    extra.append(verdict("HOLDS", "HOLDS", [], H, F)[0] == "INDETERMINATE")
    extra.append(verdict("CONTESTED", "HOLDS", [], H, F)[0] == "CONTESTED")
    extra.append(verdict("CONTESTED", "HOLDS", [], U, F)[0] == "UNDECIDABLE")
    extra.append(verdict("HOLDS", "FAILS", ["PC fails"], H, H)[0] == "UNDECIDABLE")
    print(f"extra self-checks (not registered): {sum(extra)} of {len(extra)}")
    ok &= all(extra)
    print(f"G12: {'PASS' if ok else 'FAIL'}")
    return bool(ok)


# ================================================================ pairs and model

def pair_list(tok):
    """The registered Q4 pair list, rebuilt with q4_feasibility_counts' frames, words and split rule; checked by
    sha256 against Q4_PREREG."""
    pairs = []
    for fid, frame, cls in f4.FRAMES:
        for wa, wb in itertools.combinations(f4.WORDS[cls], 2):
            if len(tok.encode(" " + wa).ids) != 1 or len(tok.encode(" " + wb).ids) != 1:
                continue
            ia, ib = tok.encode(frame.format(wa)).ids, tok.encode(frame.format(wb)).ids
            if len(ia) != len(ib) or sum(x != y for x, y in zip(ia, ib)) != 1 or {wa, wb} in f4.Q3_WORD_PAIRS:
                continue
            pairs.append({"frame": fid, "wa": wa, "wb": wb, "split": f4.split_of(fid, wa, wb), "n": len(ia),
                          "ia": ia, "ib": ib})
    sha = hashlib.sha256("\n".join("|".join(map(str, (p["frame"], p["wa"], p["wb"], p["split"], p["n"])))
                                   for p in pairs).encode()).hexdigest()
    for i, p in enumerate(pairs):
        p["idx"] = i
    return pairs, sha


def patch_softmax64():
    """Keep the eager GPT-NeoX softmax in float64 (the dtype=float32 argument dropped), in memory only, as in
    q3_explore_step.py --softmax64 (Q3 results item 1). Returns a check that the patch is installed."""
    import torch
    import transformers.models.gpt_neox.modeling_gpt_neox as g
    orig = torch.nn.functional.softmax

    class _F:
        def __getattr__(self, k):
            return getattr(torch.nn.functional, k)

        @staticmethod
        def softmax(x, dim=None, dtype=None, **kw):
            return orig(x, dim=dim, **kw)

    class _NN:
        functional = _F()

        def __getattr__(self, k):
            return getattr(torch.nn, k)

    g.nn = _NN()
    return lambda: isinstance(g.nn, _NN)


class Forward5:
    """Hidden states (7 entries) and last-position logits along the slot path, float64, inputs_embeds."""

    def __init__(self, model):
        import torch
        self.torch, self.m = torch, model
        self.E = model.gpt_neox.embed_in.weight.detach()
        self.times = []

    def __call__(self, ia, ib, th, attentions=False):
        torch = self.torch
        e = self.E[ia].clone()
        j = [k for k in range(len(ia)) if ia[k] != ib[k]][0]
        e[j] = (1.0 - th) * self.E[ia[j]] + th * self.E[ib[j]]
        t0 = time.perf_counter()
        with torch.no_grad():
            out = self.m(inputs_embeds=e.unsqueeze(0), output_hidden_states=True, output_attentions=attentions)
        self.times.append(time.perf_counter() - t0)
        hs = out.hidden_states
        if len(hs) != LAYERS:
            raise RuntimeError(f"hidden_states has {len(hs)} entries, registered {LAYERS}")
        res = ([h[0].numpy().copy() for h in hs], out.logits[0, -1].numpy().copy())
        if attentions:
            return res + (out.attentions,)
        return res


def dA_of(Am, Ap, h):
    """Central difference. --sabotage sets dA = 0 (registered anti-vacuity switch)."""
    if SABOTAGE:
        return np.zeros_like(Am)
    return (Ap - Am) / (2.0 * h)


def sym(X):
    return (X + X.T) / 2.0


def flags_q4(p, blocks, n_tokens, tau):
    """split_resolved_q4 (Q4_PREREG): split_resolved_support exactly as in Q3 (q3_run.split_resolved_support, with
    its threshold set to tau), structural zeros exactly d - n, no eigenvalue in (eps/2, 1e-6]."""
    old = q3.TAU_FLAG
    q3.TAU_FLAG = tau
    try:
        srs, tk, to, gp, gks = q3.split_resolved_support(p, blocks)
    finally:
        q3.TAU_FLAG = old
    half = EPS / 2
    n_struct = int(np.sum(p <= half))
    n_small = int(np.sum((p > half) & (p <= SMALL)))
    q4 = bool(srs and n_struct == len(p) - n_tokens and n_small == 0)
    return {"srs": srs, "q4": q4, "n_struct": n_struct, "n_small": n_small, "tied_kernel": tk, "tied_other": to,
            "gap_positive": gp, "gap_kernel_support": gks}


def point_geometry(A, dAh, dAh2, n_tokens, tau, tau_reg):
    """All per-layer quantities at one point."""
    Mraw = A.T @ A
    raw_rho = Mraw / np.trace(Mraw)
    rho, drho = q3.rho_drho(A, dAh)
    _, drho2 = q3.rho_drho(A, dAh2)
    rho, drho, drho2 = sym(rho), sym(drho), sym(drho2)
    r1 = qfi_ref.qfi_split_ex(rho, drho)
    r2 = qfi_ref.qfi_split_ex(rho, drho2)
    p = np.linalg.eigh(rho)[0]
    blocks = qfi_ref.tie_blocks(p)
    fl = flags_q4(p, blocks, n_tokens, tau)
    fl_reg = flags_q4(p, blocks, n_tokens, tau_reg)
    nA = float(np.sum(A ** 2))
    S1 = float(np.sum(dAh ** 2)) / nA if nA > 0 else 0.0
    S2 = float(np.sum(dAh2 ** 2)) / nA if nA > 0 else 0.0
    return {
        "F_Q": r1["F_Q"], "F_C": r1["F_C"], "F_R": r1["F_R"], "S": S1,
        "F_Q2": r2["F_Q"], "F_C2": r2["F_C"], "F_R2": r2["F_R"], "S2": S2,
        "residual": abs(r1["F_Q"] - r1["F_C"] - r1["F_R"]),
        "tr_err": abs(float(np.trace(rho)) - 1.0), "sym_err": float(np.max(np.abs(raw_rho - raw_rho.T))),
        "q4": fl["q4"], "srs": fl["srs"], "q4_reg": fl_reg["q4"], "n_struct": fl["n_struct"],
        "n_small": fl["n_small"], "tied_kernel": fl["tied_kernel"], "tied_other": fl["tied_other"],
        "p_max": float(p[-1]),
        "finite": bool(np.all(np.isfinite(rho)) and np.all(np.isfinite(drho)) and np.all(np.isfinite(drho2))),
    }


def output_quantities(z0, zm, zp, zm2, zp2):
    """F_out at h and h', entropy H, and the G11 form Var_p(dz) (Amendment 1 item 6)."""
    import torch

    def lsm(z):
        return torch.log_softmax(torch.from_numpy(z), dim=-1).numpy()

    lp0 = lsm(z0)
    p = np.exp(lp0)
    dl1 = (lsm(zp) - lsm(zm)) / (2 * H1_STEP)
    dl2 = (lsm(zp2) - lsm(zm2)) / (2 * H2_STEP)
    dz = (zp - zm) / (2 * H1_STEP)
    F1, F2 = float(p @ dl1 ** 2), float(p @ dl2 ** 2)
    var = float(p @ dz ** 2 - (p @ dz) ** 2)
    H = float(-(p @ lp0))
    return {"F_out": F1, "F_out2": F2, "H": H, "var_dz": var}


def lnd(a, b):
    if a > 0 and b > 0:
        return abs(math.log(a) - math.log(b))
    return float("inf")


def usable_flags(g, o):
    """Per-point gate terms (Q4_PREREG G4/G5, Amendment 1 item 1)."""
    t = {
        "g4_FQ": abs(g["F_Q"] - g["F_Q2"]) <= 1e-4 * g["F_Q2"] + 1e-15,
        "g4_FC": abs(g["F_C"] - g["F_C2"]) <= 1e-4 * g["F_Q2"] + 1e-15,
        "g4_FR": abs(g["F_R"] - g["F_R2"]) <= 1e-4 * g["F_Q2"] + 1e-15,
        "g4_Fout": abs(o["F_out"] - o["F_out2"]) <= 1e-4 * o["F_out2"] + 1e-15,
        "g4b_FC": lnd(g["F_C"], g["F_C2"]) <= 1e-3, "g4b_FR": lnd(g["F_R"], g["F_R2"]) <= 1e-3,
        "g4b_S": lnd(g["S"], g["S2"]) <= 1e-3, "g4b_Fout": lnd(o["F_out"], o["F_out2"]) <= 1e-3,
        "g5": g["q4"],
        "fl_FC": g["F_C"] > FLOOR, "fl_FR": g["F_R"] > FLOOR, "fl_S": g["S"] > FLOOR, "fl_Fout": o["F_out"] > FLOOR,
    }
    t = {k: bool(v) for k, v in t.items()}
    t["usable"] = all(t.values())
    t["usable_noFout"] = all(v for k, v in t.items() if k not in ("usable", "g4_Fout", "g4b_Fout", "fl_Fout"))
    t["g4_all"] = t["g4_FQ"] and t["g4_FC"] and t["g4_FR"] and t["g4_Fout"]
    return t


# ================================================================ stage 0, gates before any Q4 pair

def q3_pairs(tok):
    pairs = q3.chosen_pairs(tok)
    if [i for i, _, _ in pairs] != q3.CHOSEN:
        raise RuntimeError("Q3 calibration pairs differ from the registered ones")
    return pairs


def stage0(models, tok):
    """G3 (C-NOISE: nu, nu_rel) and delta-lambda on the 3 Q3 pairs (462 points, float64 attention)."""
    pairs = q3_pairs(tok)
    dl = 0.0
    for lab in LABELS:
        f = Forward5(models[lab])
        for _, ia, ib in pairs:
            for th in THETAS:
                hs, _ = f(ia, ib, th)
                for L in range(LAYERS):
                    A = hs[L]
                    n = A.shape[0]
                    t = float(np.sum(A ** 2))
                    big = np.linalg.eigvalsh(A.T @ A / t)[-n:]
                    sm = np.linalg.eigvalsh(A @ A.T / t)
                    dl = max(dl, float(np.max(np.abs(np.sort(big) - np.sort(sm)))))
    _, ia, ib = pairs[0]
    nu = nu_rel = 0.0
    nu_logit = 0.0
    for lab in LABELS:
        f = Forward5(models[lab])
        runs = [f(ia, ib, 0.5) for _ in range(3)]
        for r in runs[1:]:
            for L in range(LAYERS):
                nu = max(nu, float(np.max(np.abs(r[0][L] - runs[0][0][L]))))
                nu_rel = max(nu_rel, float(np.linalg.norm(r[0][L] - runs[0][0][L]) / np.linalg.norm(runs[0][0][L])))
            nu_logit = max(nu_logit, float(np.max(np.abs(r[1] - runs[0][1]))))
    terms = {"1e-6": SMALL, "1e4*dlambda": 1e4 * dl, "1e4*nu_rel": 1e4 * nu_rel}
    tau = max(terms.values())
    setter = max(terms, key=lambda k: terms[k])
    tau_reg = max(SMALL, 1e4 * dl, 1e4 * nu)
    return {"dlambda": dl, "nu": nu, "nu_rel": nu_rel, "nu_logit": nu_logit, "tau_q4": tau, "tau_setter": setter,
            "tau_registered": tau_reg}


def g2_check(models, tok, patched):
    """G2: float64 attention at all 6 layers (with I1), and Q3's explore point (pair 2, theta 0.4, layer 6, trained)
    re-run: F_Q at h and h' within 1e-6 relative."""
    pairs = {i: (ia, ib) for i, ia, ib in q3_pairs(tok)}
    f = Forward5(models[LABELS[0]])
    ia, ib = pairs[2]
    hs, _, att = f(ia, ib, 0.4, attentions=True)
    dtypes = [str(a.dtype) for a in att]
    not32 = []
    for a in att:
        x = a.detach()
        not32.append(bool((x.float().double() != x).any()))
    hm, _ = f(ia, ib, 0.4 - H1_STEP)
    hp, _ = f(ia, ib, 0.4 + H1_STEP)
    hm2, _ = f(ia, ib, 0.4 - H2_STEP)
    hp2, _ = f(ia, ib, 0.4 + H2_STEP)
    A = hs[6]
    fq1 = qfi_ref.qfi_split_ex(*map(sym, q3.rho_drho(A, dA_of(hm[6], hp[6], H1_STEP))))["F_Q"]
    fq2 = qfi_ref.qfi_split_ex(*map(sym, q3.rho_drho(A, dA_of(hm2[6], hp2[6], H2_STEP))))["F_Q"]
    rel = q3.rel(fq1, fq2)
    ok = bool(len(dtypes) == 6 and all(d == "torch.float64" for d in dtypes) and all(not32) and patched()
              and rel <= 1e-6)
    print(f"G2 attention dtypes {dtypes}; weight not float32-representable at {sum(not32)} of {len(not32)} layers; "
          f"patch installed {patched()}; explore point F_Q(h)={fq1:.9e} F_Q(h')={fq2:.9e} rel {rel:.3e} -> "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


def exact_rot_drho(p, d, a, b):
    """rho = diag(p, 0...) in R^{d x d}; exact derivative of R(th) rho R(th)^T at th = 0, rotation in plane (a, b)."""
    rho = np.zeros((d, d))
    rho[:len(p), :len(p)] = np.diag(p)
    G = np.zeros((d, d))
    G[a, b], G[b, a] = -1.0, 1.0
    if SABOTAGE:
        return rho, np.zeros((d, d))
    return rho, G @ rho + rho @ G.T


def g9_controls(tau):
    """G9: S1-S3 (Q3, unchanged) and the Q4 flag controls S3, N1, N2 (exact drho; I3)."""
    q3.SABOTAGE = SABOTAGE
    S = q3.run_controls()
    res = dict(S)

    def flag(p, d, a, b):
        rho, drho = exact_rot_drho(np.array(p), d, a, b)
        r = qfi_ref.qfi_split_ex(rho, drho)
        pe = np.linalg.eigh(rho)[0]
        return flags_q4(pe, qfi_ref.tie_blocks(pe), len(p), tau), r

    fl, r = flag([0.5, 0.3, 0.2], 5, 1, 3)
    ok = fl["q4"] is True and abs(r["F_Q"] - 4 * 0.3) < 1e-12
    print(f"S3 (Q4 flag, exact drho): F_Q={r['F_Q']:.12f} (expect 1.2) split_resolved_q4={fl['q4']} (expect True) -> "
          f"{'PASS' if ok else 'FAIL'}")
    res["S3q4"] = bool(ok)
    fl, _ = flag([0.4, 0.4, 0.2], 5, 0, 3)
    ok = fl["q4"] is False
    print(f"N1 support tie p=(0.4,0.4,0.2), d=5: split_resolved_q4={fl['q4']} (expect False) -> "
          f"{'PASS' if ok else 'FAIL'}")
    res["N1"] = bool(ok)
    dlt = 2.5e-13
    fl, _ = flag([1 - dlt, dlt], 4, 0, 2)
    ok = fl["srs"] is True and fl["q4"] is False
    print(f"N2 p=(1-d, d, 0, 0), d=2.5e-13: split_resolved_support={fl['srs']} (expect True) split_resolved_q4="
          f"{fl['q4']} (expect False; structural zeros {fl['n_struct']}, d - n = 2) -> {'PASS' if ok else 'FAIL'}")
    res["N2"] = bool(ok)
    return all(res.values()), res


def g10_invariance(models, tok, tau):
    """G10 (Amendment 1 item 2): Q3 pair 0, theta 0.5, trained, all layers: 1e3*A, 1e3*dA."""
    _, ia, ib = q3_pairs(tok)[0]
    f = Forward5(models[LABELS[0]])
    hs, _ = f(ia, ib, 0.5)
    hm, _ = f(ia, ib, 0.5 - H1_STEP)
    hp, _ = f(ia, ib, 0.5 + H1_STEP)
    worst_rho = worst_drho = worst_F = 0.0
    flag_same = True
    for L in range(LAYERS):
        A, dA = hs[L], dA_of(hm[L], hp[L], H1_STEP)
        out = []
        for s in (1.0, 1e3):
            rho, drho = map(sym, q3.rho_drho(s * A, s * dA))
            r = qfi_ref.qfi_split_ex(rho, drho)
            pe = np.linalg.eigh(rho)[0]
            out.append((rho, drho, r, flags_q4(pe, qfi_ref.tie_blocks(pe), A.shape[0], tau)["q4"]))
        (r0, d0, f0, q0), (r1, d1, f1, q1) = out
        worst_rho = max(worst_rho, float(np.max(np.abs(r1 - r0))))
        worst_drho = max(worst_drho, float(np.max(np.abs(d1 - d0))))
        for k in ("F_Q", "F_C", "F_R"):
            worst_F = max(worst_F, q3.rel(f1[k], f0[k]))
        flag_same &= q0 == q1
    ok = bool(worst_rho <= 1e-15 and worst_drho <= 1e-15 and worst_F <= 1e-12 and flag_same)
    print(f"G10 scale invariance (x1e3): max|d rho| {worst_rho:.3e} max|d drho| {worst_drho:.3e} max rel dF "
          f"{worst_F:.3e} flag unchanged {flag_same} -> {'PASS' if ok else 'FAIL'}")
    return ok


# ================================================================ points

def compute_points(models, pairs, split, tau, tau_reg, inter_pair=None):
    records, inter, fwds = [], {}, {}
    for lab in LABELS:
        f = fwds[lab] = Forward5(models[lab])
        for P in pairs:
            if P["split"] != split:
                continue
            ia, ib = P["ia"], P["ib"]
            for ti, th in enumerate(THETAS):
                hs0, z0 = f(ia, ib, th)
                hm, zm = f(ia, ib, th - H1_STEP)
                hp, zp = f(ia, ib, th + H1_STEP)
                hm2, zm2 = f(ia, ib, th - H2_STEP)
                hp2, zp2 = f(ia, ib, th + H2_STEP)
                o = output_quantities(z0, zm, zp, zm2, zp2)
                for L in range(LAYERS):
                    dA1, dA2 = dA_of(hm[L], hp[L], H1_STEP), dA_of(hm2[L], hp2[L], H2_STEP)
                    g = point_geometry(hs0[L], dA1, dA2, P["n"], tau, tau_reg)
                    rec = {"model": lab, "pair": P["idx"], "frame": P["frame"], "theta": round(th, 10), "layer": L}
                    rec.update(g)
                    rec.update(o)
                    rec.update(usable_flags(g, o))
                    rec["g11"] = bool(abs(o["F_out"] - o["var_dz"]) <= 1e-8 * o["F_out"])
                    records.append(rec)
                    if inter_pair is not None and P["idx"] == inter_pair and ti in (0, 5, 10):
                        inter[(lab, ti, L)] = (hs0[L], dA1, dA2, rec)
    return records, inter, fwds


def fmt(v):
    if isinstance(v, (bool, np.bool_)) or isinstance(v, (int, np.integer)) or isinstance(v, str):
        return str(v)
    return f"{float(v):.9e}"


def digest(records, tau):
    keys = sorted(records[0])
    lines = [f"tau_q4={fmt(tau)}"] + ["|".join(f"{k}={fmt(r[k])}" for k in keys) for r in records]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def pair_features(records, model, layer):
    """Usable pairs (>= 9 of 11 usable theta) and their features (means over usable theta)."""
    by = {}
    for r in records:
        if r["model"] == model and r["layer"] == layer:
            by.setdefault(r["pair"], []).append(r)
    feats = {}
    for pid, rs in sorted(by.items()):
        u = [r for r in rs if r["usable"]]
        if len(u) >= 9:
            feats[pid] = {"frame": rs[0]["frame"], "c": np.mean([math.log(r["F_C"]) for r in u]),
                          "r": np.mean([math.log(r["F_R"]) for r in u]), "s": np.mean([math.log(r["S"]) for r in u]),
                          "h": np.mean([r["H"] for r in u]), "y": np.mean([math.log(r["F_out"]) for r in u])}
    return feats


def as_arrays(feats):
    ids = sorted(feats)
    F = {k: np.array([feats[i][k] for i in ids]) for k in ("c", "r", "s", "h", "y")}
    return ids, F, [feats[i]["frame"] for i in ids]


def exclusions(records, pairs, split):
    """Amendment 1 item 4: counts by reason, model, frame and layer (points and pairs)."""
    reasons = ["g4_FQ", "g4_FC", "g4_FR", "g4_Fout", "g4b_FC", "g4b_FR", "g4b_S", "g4b_Fout", "g5",
               "fl_FC", "fl_FR", "fl_S", "fl_Fout"]
    frames = [f for f, _, _ in f4.FRAMES]
    print("EXCLUSIONS (Amendment 1 item 4). Point counts failing each term; pairs usable (>= 9 of 11), "
          "usable ignoring the F_out terms, and excluded only by an F_out term")
    print("model  L  pts usable " + " ".join(f"{r:>8s}" for r in reasons) + "  pairs usable noFout onlyFout lt9")
    table = {}
    for lab in LABELS:
        for L in range(LAYERS):
            rs = [r for r in records if r["model"] == lab and r["layer"] == L]
            cnt = {k: sum(not r[k] for r in rs) for k in reasons}
            by = {}
            for r in rs:
                by.setdefault(r["pair"], []).append(r)
            pu = sum(sum(r["usable"] for r in v) >= 9 for v in by.values())
            pn = sum(sum(r["usable_noFout"] for r in v) >= 9 for v in by.values())
            only = sum(sum(r["usable_noFout"] for r in v) >= 9 and sum(r["usable"] for r in v) < 9
                       for v in by.values())
            lt9 = len(by) - pu
            table[(lab, L)] = {"points": len(rs), "usable_points": sum(r["usable"] for r in rs), "fail": cnt,
                               "pairs": len(by), "pairs_usable": pu, "pairs_noFout": pn, "only_Fout": only,
                               "lt9": lt9}
            print(f"{'trained' if lab == LABELS[0] else 'step0  '} {L} {len(rs):4d} {sum(r['usable'] for r in rs):6d} "
                  + " ".join(f"{cnt[k]:8d}" for k in reasons) + f"  {len(by):5d} {pu:6d} {pn:6d} {only:8d} {lt9:3d}")
    print("usable points by frame (trained / step0), summed over layers:")
    for fr in frames:
        a = [sum(r["usable"] for r in records if r["model"] == lab and r["frame"] == fr) for lab in LABELS]
        n = [sum(1 for r in records if r["model"] == lab and r["frame"] == fr) for lab in LABELS]
        print(f"  {fr}: {a[0]}/{n[0]}  {a[1]}/{n[1]}")
    return table


def g4b_report(records):
    """Amendment 1 item 1: per X, points passing G4 but failing G4b, and the largest |d ln X| among G4 passes."""
    print("G4b report (Amendment 1 item 1), per model:")
    out = {}
    for lab in LABELS:
        rs = [r for r in records if r["model"] == lab and r["g4_all"]]
        row = {}
        for X, a, b in (("F_C", "F_C", "F_C2"), ("F_R", "F_R", "F_R2"), ("S", "S", "S2"),
                        ("F_out", "F_out", "F_out2")):
            k = "g4b_" + ("Fout" if X == "F_out" else X.replace("_", ""))
            n_fail = sum(not r[k] for r in rs)
            worst = max((lnd(r[a], r[b]) for r in rs), default=float("nan"))
            row[X] = (n_fail, worst)
        out[lab] = row
        print(f"  {lab}: G4 passes {len(rs)}; " + "; ".join(f"{X} fail G4b {v[0]} max|dln| {v[1]:.3e}"
                                                         for X, v in row.items()))
    return out


def profiles(records):
    print("LAYER PROFILE (descriptive): median F_R/F_Q over usable points, by model and layer")
    for lab in LABELS:
        row = []
        for L in range(LAYERS):
            v = [r["F_R"] / r["F_Q"] for r in records if r["model"] == lab and r["layer"] == L and r["usable"]]
            row.append(f"L{L} {np.median(v):.3e}" if v else f"L{L} n/a")
        print(f"  {lab}: " + "  ".join(row))


# ================================================================ Q5 statistics (dev)

def layer_selection(records):
    sel = {}
    print("LAYER SELECTION (trained, dev, leave-one-pair-out). G_loo = (SSE_A - SSE_B)/SSE_A")
    for L in range(LAYERS):
        ids, F, _ = as_arrays(pair_features(records, LABELS[0], L))
        if len(ids) < 6:
            sel[L] = {"N": len(ids), "eligible": False, "why": "fewer pairs than columns + 1"}
        else:
            eA, okA = loo_errors(design(F, False), F["y"])
            eB, okB = loo_errors(design(F, True), F["y"])
            sA, sB = float(np.sum(eA ** 2)), float(np.sum(eB ** 2))
            if sA == 0.0:
                sel[L] = {"N": len(ids), "eligible": False, "why": "SSE_A = 0"}
            elif not (okA and okB):
                sel[L] = {"N": len(ids), "eligible": False, "why": "rank-deficient (I5)"}
            else:
                sel[L] = {"N": len(ids), "eligible": True, "G_loo": (sA - sB) / sA, "SSE_A": sA, "SSE_B": sB}
        s = sel[L]
        print(f"  L{L}: usable pairs {s['N']}; " + (f"G_loo {s['G_loo']:.6f}" if s["eligible"]
                                                    else f"ineligible ({s['why']})"))
    elig = [L for L in range(LAYERS) if sel[L]["eligible"]]
    if not elig:
        return None, sel
    best = max(sel[L]["G_loo"] for L in elig)
    lstar = max(L for L in elig if sel[L]["G_loo"] == best)  # ties go to the higher layer
    return lstar, sel


def residual_sd(F):
    X = design(F, False)
    b, _ = ols(X, F["r"])
    return float(np.std(F["r"] - X @ b))


def controls_y(F, z_of, ids, sigma, sd_y):
    z = np.array([z_of[i] for i in ids])
    return {"pc": F["r"] + 0.3 * sigma * z, "nc": F["c"] + F["s"] + F["h"] + 0.3 * sd_y * z}


def q5_stats(records, frames_all):
    lstar, sel = layer_selection(records)
    out = {"layer_selection": {str(k): v for k, v in sel.items()}, "l_star": lstar}
    if lstar is None:
        print("Q5 UNDECIDABLE: no layer is eligible (Amendment 1 item 3)")
        out["undecidable"] = ["no eligible layer"]
        return out
    print(f"l* = {lstar}")
    z_all = np.random.default_rng(RNG_SEED).standard_normal(N_DEV + N_TEST)
    frozen, h1dev, und = {}, {}, []
    for lab in LABELS:
        ids, F, fr = as_arrays(pair_features(records, lab, lstar))
        name = "trained" if lab == LABELS[0] else "step0"
        sigma = residual_sd(F) if len(ids) > 5 else 0.0
        sd_y = float(np.std(F["y"])) if len(ids) else 0.0
        ys = {"real": F["y"]}
        ys.update(controls_y(F, z_all, ids, sigma, sd_y))
        fz = {"N_dev": len(ids), "sigma": sigma, "sd_dev_y": sd_y, "coef": {}}
        h1dev[name] = {}
        for arm, y in ys.items():
            XA, XB = design(F, False), design(F, True)
            bA, okA = ols(XA, y)
            bB, okB = ols(XB, y)
            eA, okA2 = loo_errors(XA, y)
            eB, okB2 = loo_errors(XB, y)
            fz["coef"][arm] = {"A": bA.tolist(), "B": bB.tolist(), "full_rank": bool(okA and okB)}
            r = h1_procedure(eA, eB, fr, frames_all)
            deg = []
            if not (okA and okB and okA2 and okB2):
                deg.append("rank-deficient")
            if arm == "pc" and sigma == 0.0:
                deg.append("sigma = 0")
            if arm == "nc" and sd_y == 0.0:
                deg.append("sd_dev(y) = 0")
            if deg:
                r["outcome"] = "UNDECIDABLE"
                r["why"] = ", ".join(deg)
                und.append(f"{name} {arm}: {r['why']}")
            h1dev[name][arm] = r
            gtxt = (f"G {r['G']:.6f} k {r['k']}/{r['N']} p {r['p']:.6g} frames>0 {r['m']} of 6 "
                    f"(tail {r['m_tail']:.4f}) a={r['a']} b={r['b']} c={r['c']}") if "G" in r else r.get("why", "")
            print(f"  {name} {arm:4s} (dev LOO at l*): {gtxt} -> {r['outcome']}")
            if "frame_gain" in r:
                print("      frame gains: " + " ".join(f"{k} {'n/a' if v is None else f'{v:.4f}'}"
                                                     for k, v in r["frame_gain"].items()))
        fz["pair_ids"] = ids
        frozen[name] = fz
    out.update(frozen=frozen, h1_dev=h1dev, undecidable=und)
    return out


# ================================================================ Q6 statistics (test)

def q6_stats(records, frames_all, q5):
    lstar = q5["l_star"]
    z_all = np.random.default_rng(RNG_SEED).standard_normal(N_DEV + N_TEST)
    errs, h1, und = {}, {}, []
    for lab in LABELS:
        name = "trained" if lab == LABELS[0] else "step0"
        fz = q5["frozen"][name]
        ids, F, fr = as_arrays(pair_features(records, lab, lstar))
        ys = {"real": F["y"]}
        ys.update(controls_y(F, z_all, ids, fz["sigma"], fz["sd_dev_y"]))
        h1[name], errs[name] = {}, {}
        for arm, y in ys.items():
            c = fz["coef"][arm]
            eA = y - design(F, False) @ np.array(c["A"]) if len(ids) else np.array([])
            eB = y - design(F, True) @ np.array(c["B"]) if len(ids) else np.array([])
            r = h1_procedure(eA, eB, fr, frames_all)
            deg = []
            if not c["full_rank"]:
                deg.append("rank-deficient at Q5")
            if arm == "pc" and fz["sigma"] == 0.0:
                deg.append("sigma = 0")
            if arm == "nc" and fz["sd_dev_y"] == 0.0:
                deg.append("sd_dev(y) = 0")
            if deg:
                r["outcome"], r["why"] = "UNDECIDABLE", ", ".join(deg)
                und.append(f"{name} {arm}: {r['why']}")
            h1[name][arm] = r
            errs[name][arm] = {i: (float(a), float(b)) for i, a, b in zip(ids, eA, eB)}
            gtxt = (f"G {r['G']:.6f} k {r['k']}/{r['N']} p {r['p']:.6g} frames>0 {r['m']} of 6 "
                    f"(tail {r['m_tail']:.4f}) a={r['a']} b={r['b']} c={r['c']}") if "G" in r else r.get("why", "")
            print(f"  {name} {arm:4s} (test, frozen dev coefficients): {gtxt} -> {r['outcome']}")
            if "frame_gain" in r:
                print("      frame gains: " + " ".join(f"{k} {'n/a' if v is None else f'{v:.4f}'}"
                                                     for k, v in r["frame_gain"].items()))
    outc = {}
    for name in ("trained", "step0"):
        o = h1[name]["real"]["outcome"]
        if h1[name]["pc"]["outcome"] != "HOLDS" or h1[name]["nc"]["outcome"] in ("HOLDS", "CONTESTED"):
            und.append(f"{name} anti-vacuity: PC {h1[name]['pc']['outcome']}, NC {h1[name]['nc']['outcome']}")
            o = "UNDECIDABLE"
        outc[name] = o
    hp, ho = h2_both(errs["trained"]["real"], errs["step0"]["real"])
    print(f"  H2-P: |P| {hp['nP']} " + (f"k {hp['k']} p {hp['p']:.6g} median d {hp['d_median']:.6g}"
                                         if "k" in hp else hp.get("why", "")) + f" -> {hp['outcome']}")
    print(f"  H2-own: " + (f"k {ho['k']} p {ho['p']:.6g} median d {ho['d_median']:.6g}" if "k" in ho
                           else ho.get("why", "")) + f" -> {ho['outcome']}")
    if "d" in hp:
        print("  d_i (H2-P): " + " ".join(f"{x:.4g}" for x in hp["d"]))
    v, reasons, reg, a1 = verdict(outc["trained"], outc["step0"], [u for u in und if "anti-vacuity" not in u],
                                  hp, ho)
    return {"h1_test": h1, "h1_outcome": outc, "h2_P": hp, "h2_own": ho, "verdict": v, "reasons": reasons,
            "verdict_registered": reg, "verdict_amend1": a1, "undecidable": und}


# ================================================================ main

def run_cases_gate():
    pub = subprocess.run([sys.executable, "-I", os.path.join(HERE, "run_cases.py"),
                          os.path.join(HERE, "cases", "public.jsonl")], capture_output=True, text=True)
    neg = subprocess.run([sys.executable, "-I", os.path.join(HERE, "run_cases.py"),
                          os.path.join(HERE, "cases", "a16_must_fail.jsonl")], capture_output=True, text=True)
    pl = [x for x in pub.stdout.splitlines() if x.startswith("cases ")]
    nl = [x for x in neg.stdout.splitlines() if x.startswith("cases ")]
    ok = bool(pub.returncode == 0 and pl and pl[0].startswith("cases 8, failed 0")
              and neg.returncode == 1 and nl and nl[0].startswith("cases 3, failed 3"))
    print(f"G0 public: rc={pub.returncode} {pl}; must-fail: rc={neg.returncode} {nl} -> {'PASS' if ok else 'FAIL'}")
    return ok


def write_interchange(inter, outdir, pair):
    th_idx = (0, 5, 10)
    n = inter[(LABELS[0], 0, 0)][0].shape[0]
    shp = (len(LABELS), len(th_idx), LAYERS)
    A, dA, dA2 = np.zeros(shp + (n, D_MODEL)), np.zeros(shp + (n, D_MODEL)), np.zeros(shp + (n, D_MODEL))
    keys = ("F_Q", "F_C", "F_R", "q4", "srs")
    ref = {k: np.zeros(shp) for k in keys}
    for a, lab in enumerate(LABELS):
        for b, ti in enumerate(th_idx):
            for L in range(LAYERS):
                A[a, b, L], dA[a, b, L], dA2[a, b, L], rec = inter[(lab, ti, L)]
                for k in keys:
                    ref[k][a, b, L] = float(rec[k])
    arrays = {"A": A, "dA": dA, "dA_h2": dA2, "theta": np.array([THETAS[i] for i in th_idx]),
              "h": np.array(H1_STEP), "h2": np.array(H2_STEP), "models": np.array(LABELS),
              "pair": np.array([pair["frame"], pair["wa"], pair["wb"]]), "symmetrised": np.array(True),
              **{"ref_" + ("split_resolved_q4" if k == "q4" else "split_resolved_support" if k == "srs" else k): v
                 for k, v in ref.items()}}
    path = os.path.join(outdir, "interchange_subset.npz")
    q3.save_npz(path, arrays)
    return path, fc.sha256(path)


def main():
    global SABOTAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--q5-results", default=None)
    ap.add_argument("--cache", default=os.path.expanduser("~/.cache/qfi001_q3"))
    a = ap.parse_args()
    SABOTAGE = a.sabotage
    t_start = time.perf_counter()

    if a.selftest:
        return 0 if selftest() else 1

    q5 = None
    if a.split == "test":
        if not a.q5_results or not os.path.exists(a.q5_results):
            print("REFUSED: --split test needs --q5-results (the Q5 results file)")
            return 2
        q5 = json.load(open(a.q5_results))
        if q5.get("split") != "dev" or q5.get("l_star") is None or "frozen" not in q5:
            print("REFUSED: the Q5 results file has no l*, tau_q4 or frozen coefficients")
            return 2

    patched = patch_softmax64()

    if a.child:
        models, tok, _ = q3.load_models(a.cache)
        pairs, _ = pair_list(tok)
        s0 = None if q5 else stage0(models, tok)
        tau = q5["tau_q4"] if q5 else s0["tau_q4"]
        tau_reg = q5["tau_registered"] if q5 else s0["tau_registered"]
        records, _, _ = compute_points(models, pairs, a.split, tau, tau_reg)
        print(f"DIGEST {digest(records, tau)}")
        return 0

    import torch
    import transformers
    print(f"QFI-001 {'Q5 (dev)' if a.split == 'dev' else 'Q6 (test)'} run; sabotage={SABOTAGE}; python "
          f"{sys.version.split()[0]}; numpy {np.__version__}; torch {torch.__version__}; transformers "
          f"{transformers.__version__}; threads 2; float64; softmax kept in float64 (in-memory patch)")
    if q5:
        print(f"Q5 results file {a.q5_results} sha256 {fc.sha256(a.q5_results)}")
    G = {}

    def stop(gate):
        print(f"INFEASIBLE: first failure {gate} (fail-closed; no Q4 pair computed)")
        print("VERDICT INFEASIBLE")
        return 1

    G["G12"] = selftest()
    if not G["G12"]:
        return stop("G12")
    G["G0"] = run_cases_gate()
    if not G["G0"]:
        return stop("G0")
    models, tok, ident_ok = q3.load_models(a.cache)
    pairs, sha = pair_list(tok)
    nd, nt = sum(p["split"] == "dev" for p in pairs), sum(p["split"] == "test" for p in pairs)
    G["G1"] = bool(ident_ok and sha == PAIR_LIST_SHA256 and nd == N_DEV and nt == N_TEST)
    print(f"G1 identities (lines above are q3_run.load_models' own, labelled R1) {ident_ok}; pair list sha256 {sha} "
          f"dev {nd} test {nt} -> {'PASS' if G['G1'] else 'FAIL'}")
    if not G["G1"]:
        return stop("G1")
    G["G2"] = g2_check(models, tok, patched)
    if not G["G2"]:
        return stop("G2")
    s0 = stage0(models, tok)
    print(f"G3 C-NOISE (Q3 pair 0, theta 0.5, both models, 3 repeats): nu {s0['nu']:.3e} nu_rel {s0['nu_rel']:.3e} "
          f"(predicted 0); last-position logits max|d| {s0['nu_logit']:.3e} (descriptive)")
    G["G3"] = bool(np.isfinite(s0["nu"]) and np.isfinite(s0["nu_rel"]))
    print(f"stage 0: dlambda {s0['dlambda']:.3e} over 462 points; terms 1e-6, 1e4*dlambda {1e4 * s0['dlambda']:.3e}, "
          f"1e4*nu_rel {1e4 * s0['nu_rel']:.3e}; tau_q4 = {s0['tau_q4']!r} (set by {s0['tau_setter']}); "
          f"registered tau (absolute nu) = {s0['tau_registered']!r}")
    tau, tau_reg = s0["tau_q4"], s0["tau_registered"]
    if q5:
        print(f"Q6 uses Q5's tau_q4 = {q5['tau_q4']!r} and registered tau = {q5['tau_registered']!r} "
              f"(this run's stage 0 is printed above for comparison)")
        tau, tau_reg = q5["tau_q4"], q5["tau_registered"]
    g9, _ = g9_controls(tau)
    G["G9"] = bool(g9)
    print(f"G9 S1-S3, S3 (Q4 flag), N1, N2 -> {'PASS' if g9 else 'FAIL'}")
    if not G["G9"]:
        return stop("G9")
    G["G10"] = g10_invariance(models, tok, tau)
    if not G["G10"]:
        return stop("G10")

    inter_pair = next(p for p in pairs if p["split"] == a.split)
    records, inter, fwds = compute_points(models, pairs, a.split, tau, tau_reg, inter_pair["idx"])
    npts = len(records)
    g6 = sum(r["finite"] and r["residual"] <= 1e-10 * max(1.0, r["F_Q"]) and r["tr_err"] <= 1e-12
             and r["sym_err"] <= 1e-14 for r in records)
    G["G6"] = bool(g6 == npts and npts > 0)
    print(f"G6 residual <= 1e-10 max(1, F_Q), |tr rho - 1| <= 1e-12, raw rho symmetric to 1e-14 (I2), finite: "
          f"{g6} of {npts}; worst residual {max(r['residual'] for r in records):.3e} tr_err "
          f"{max(r['tr_err'] for r in records):.3e} sym_err {max(r['sym_err'] for r in records):.3e} -> "
          f"{'PASS' if G['G6'] else 'FAIL'}")
    usable = [r for r in records if r["usable"]]
    g11 = sum(r["g11"] for r in usable)
    worst11 = max((abs(r["F_out"] - r["var_dz"]) / r["F_out"] for r in usable), default=float("nan"))
    G["G11"] = bool(g11 == len(usable))
    print(f"G11 |F_out - Var_p(dz)| <= 1e-8 F_out at usable points: {g11} of {len(usable)}; worst relative "
          f"{worst11:.3e} -> {'PASS' if G['G11'] else 'FAIL'}")
    ng4 = {lab: sum(r["g4_all"] for r in records if r["model"] == lab) for lab in LABELS}
    ng5 = {lab: sum(r["g5"] for r in records if r["model"] == lab) for lab in LABELS}
    print(f"G4 (all terms) passes: " + ", ".join(f"{k} {v}" for k, v in ng4.items()) + f" of {npts // 2} each")
    print(f"G5 split_resolved_q4: " + ", ".join(f"{k} {v}" for k, v in ng5.items()) + f" of {npts // 2} each")
    diff_tau = sum(r["q4"] != r["q4_reg"] for r in records)
    print(f"points whose split_resolved_q4 differs between tau_q4 and the registered tau: {diff_tau}")
    g4b = g4b_report(records)
    excl = exclusions(records, pairs, a.split)
    profiles(records)
    frames_all = [f for f, _, _ in f4.FRAMES]

    trained = LABELS[0]
    per_layer_pts = []
    for L in range(LAYERS):
        rs = [r for r in records if r["model"] == trained and r["layer"] == L]
        per_layer_pts.append(sum(r["usable"] for r in rs) / len(rs))
    print("trained usable point share by layer: " + " ".join(f"L{L} {v:.4f}" for L, v in enumerate(per_layer_pts)))

    dig = digest(records, tau)
    t_main = time.perf_counter() - t_start
    ft = np.array([t for f in fwds.values() for t in f.times])
    print(f"G8 cost: main run wall {t_main:.1f} s ({t_main / 60:.2f} min); forward passes {len(ft)}, median "
          f"{np.median(ft) * 1e3:.2f} ms, total {ft.sum():.1f} s; peak RSS "
          f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MiB")
    G["G8"] = bool(t_main < 3600)

    results = {"split": a.split, "registration": ["23679c2", "d9337c3", "2fc82ad"], "tau_q4": tau,
               "tau_registered": tau_reg, "stage0": s0, "digest": dig, "exclusions":
               {f"{k[0]}|L{k[1]}": v for k, v in excl.items()}, "g4b": g4b,
               "usable_point_share_trained": per_layer_pts,
               "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "torch": torch.__version__,
                            "transformers": transformers.__version__}}
    if a.split == "dev":
        st = q5_stats(records, frames_all)
        results.update(st)
        lstar = st["l_star"]
        pu = (len(pair_features(records, trained, lstar)) / N_DEV) if lstar is not None else 0.0
        feasible = bool(all(v >= 0.95 for v in per_layer_pts) and pu >= 0.90)
        print(f"FEASIBLE: trained usable point share >= 0.95 at every layer {all(v >= 0.95 for v in per_layer_pts)}; "
              f"dev pairs usable at l* {pu:.4f} (>= 0.90 {pu >= 0.90}) -> {feasible}")
        results["feasible"] = feasible
        only_f = {lab: excl[(lab, lstar)]["only_Fout"] / max(1, excl[(lab, lstar)]["pairs_noFout"])
                  for lab in LABELS} if lstar is not None else {}
        print("share of otherwise-usable dev pairs at l* excluded only by an F_out term (descriptive at Q5): "
              + ", ".join(f"{k} {v:.4f}" for k, v in only_f.items()))
    else:
        st = q6_stats(records, frames_all, q5)
        results.update(st)
        lstar = q5["l_star"]
        only_f = {lab: excl[(lab, lstar)]["only_Fout"] / max(1, excl[(lab, lstar)]["pairs_noFout"]) for lab in LABELS}
        screened = any(v > 0.05 for v in only_f.values())
        results["outcome_screened"] = screened
        print("share of otherwise-usable test pairs at l* excluded only by an F_out term: "
              + ", ".join(f"{k} {v:.4f}" for k, v in only_f.items()) + f" -> OUTCOME-SCREENED {screened}")

    t1 = time.perf_counter()
    cmd = [sys.executable, "-I", os.path.abspath(__file__), "--child", "--cache", a.cache, "--split", a.split] + \
        (["--sabotage"] if SABOTAGE else []) + (["--q5-results", a.q5_results] if q5 else [])
    ch = subprocess.run(cmd, capture_output=True, text=True)
    child = [x.split()[1] for x in ch.stdout.splitlines() if x.startswith("DIGEST ")]
    print(f"G7 second process: rc={ch.returncode} digest {child[0] if child else None} ({time.perf_counter() - t1:.1f} s);"
          f" this process {dig}")
    G["G7"] = bool(ch.returncode == 0 and child == [dig])
    G["G4"] = G["G5"] = True  # G4 and G5 define "usable"; they are not fail-closed by themselves

    for k in ["G12", "G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "G11"]:
        print(f"{k}: {'PASS' if G.get(k) is True else 'FAIL'}")
    gates_ok = all(G.get(k) is True for k in ["G12", "G0", "G1", "G2", "G3", "G6", "G7", "G8", "G9", "G10", "G11"])
    results["gates"] = G

    if a.split == "dev":
        P = {}
        P["P1"] = bool(all(G.get(k) is True for k in ["G0", "G1", "G2", "G3", "G6", "G7", "G8", "G9"])
                       and results["feasible"])
        P["P2"] = bool(s0["dlambda"] < 1e-10 and s0["nu"] < 1e-10 and s0["tau_registered"] == 1e-6)
        if lstar is not None:
            h = st["h1_dev"]
            P["P3"] = bool(all(h[m]["pc"]["outcome"] == "HOLDS" and h[m]["nc"]["outcome"] in ("FAILS",)
                               for m in ("trained", "step0")))
        else:
            P["P3"] = False
        p6 = []
        for L in range(LAYERS):
            rs = [r for r in records if r["model"] == trained and r["layer"] == L and r["g4_all"]]
            p6.append(sum(r["g4b_FC"] and r["g4b_FR"] and r["g4b_S"] and r["g4b_Fout"] for r in rs) / max(1, len(rs)))
        print("P6 detail: share of trained G4 passes that pass G4b, by layer: "
              + " ".join(f"L{L} {v:.4f}" for L, v in enumerate(p6)))
        P["P6"] = bool(all(v >= 0.95 for v in p6))
        P["P7"] = bool(G["G10"] and G["G11"] and s0["nu_rel"] == 0.0 and s0["tau_q4"] == 1e-6
                       and s0["tau_registered"] == 1e-6)
        for k, v in P.items():
            print(f"{k} {'HELD' if v else 'REFUTED'}")
        print("P4, P5, P8 NOT RUN (Q6 predictions)")
        held = sum(P.values())
        results["P"] = P
        state = "INFEASIBLE" if not (gates_ok and results["feasible"]) else (
            "UNDECIDABLE" if (lstar is None or st.get("undecidable")) else "FEASIBLE")
        print(f"Q5 STATE {state}. Dev gains above are descriptive and in-sample (l* was chosen on them). "
              f"F_R is not interpreted until ChatGPT's d1_sld agreement on the interchange subset is posted (FAST-1).")
    else:
        print(f"Q6 VERDICT {st['verdict']}" + (f" ({'; '.join(st['reasons'])})" if st["reasons"] else "")
              + (" OUTCOME-SCREENED" if results["outcome_screened"] else ""))
        print(f"  registered rule (Q4_PREREG): {st['verdict_registered']}; Amendment 1 rule (H2-own): "
              f"{st['verdict_amend1']}")
        state = "INFEASIBLE" if not gates_ok else st["verdict"]

    if not SABOTAGE:
        outdir = os.path.join(ROOT, "results", "qfi_001", "q5" if a.split == "dev" else "q6")
        os.makedirs(outdir, exist_ok=True)
        ipath, isha = write_interchange(inter, outdir, inter_pair)
        print(f"interchange: {os.path.relpath(ipath, ROOT)} sha256 {isha} ({os.path.getsize(ipath)} bytes)")
        results["interchange_sha256"] = isha
        results["state"] = state
        rpath = os.path.join(outdir, "results.json")
        with open(rpath, "w") as fh:
            json.dump(results, fh, indent=1, sort_keys=True, default=float)
        print(f"results: {os.path.relpath(rpath, ROOT)} sha256 {fc.sha256(rpath)}")
    if a.split == "dev":
        print(f"VERDICT {held} of 5 as registered (P1, P2, P3, P6, P7)")
    print(f"DIGEST {dig}")
    return 0 if state not in ("INFEASIBLE", "UNDECIDABLE") else 1


if __name__ == "__main__":
    sys.exit(main())
