#!/usr/bin/env python3
"""QFI-001 Q3 harness: feasibility of the QFI split on pythia-14m (trained main vs step0). Counts and cost only.

Registration: experiments/qfi_001/Q3_PREREG.md (e533438), committed before this file existed. This harness imports
qfi_ref (Amendment 4 code, 5c6f772) and q3_feasibility_counts (pinned identities, candidate pairs); it copies neither.
Author: Claude (Anthropic, Opus 5.5). SELF-TESTED only. Needs numpy, torch, transformers, safetensors, tokenizers, and
network access to huggingface.co (weights are fetched by pinned revision and checked by sha256; never committed).

Implementation choices the registration does not fix (disclosed in Q3_RESULTS.md):
  - attention implementation "eager"; checkpoint key embed_out.weight loaded as lm_head.weight (strict load);
  - S1 path p(theta) = softmax(log p0 + theta * a), p0 = (0.5, 0.3, 0.2), a = (1, 0, -1), d = 5;
  - R5 is judged on the main run's wall time; the R6 repeat in a second process is timed and printed separately;
  - the results digest uses every per-point record field formatted to 10 significant digits (exploratory fields too).

Usage:  python -I experiments/qfi_001/q3_run.py [--sabotage] [--cache DIR]
        (--child is internal: the R6 repeat in a second process, prints only the DIGEST line)
"""
import argparse
import hashlib
import io
import json
import os
import resource
import subprocess
import sys
import time
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import qfi_ref  # noqa: E402
import q3_feasibility_counts as fc  # noqa: E402

EPS = qfi_ref.EPS            # 1e-12
TAU_FLAG = qfi_ref.TAU_FLAG  # 1e-6
SUPPORT = 1e-6               # item 1: support means > 1e-6
EPS_ALT = 1e-10              # item 6
H = 1e-4                     # central difference step
H_ALT = 1e-3                 # item 6 step check
THETAS = [i / 10 for i in range(11)]
CHOSEN = [0, 1, 2]           # registered pairs (first three that qualify)
LAYERS = 7
D_MODEL = 128
SABOTAGE = False


# ---------------------------------------------------------------- shared rho / drho code (model and S1-S3)

def deriv(A_minus, A_plus, h):
    """Central difference of A. --sabotage sets dA = 0 (registered anti-vacuity switch)."""
    if SABOTAGE:
        return np.zeros_like(A_minus)
    return (A_plus - A_minus) / (2.0 * h)


def rho_drho(A, dA):
    """rho = A^T A / tr, drho = dM/t - rho tr(dM)/t with dM = dA^T A + A^T dA (registration, Design)."""
    M = A.T @ A
    dM = dA.T @ A + A.T @ dA
    t = np.trace(M)
    rho = M / t
    drho = dM / t - rho * (np.trace(dM) / t)
    return rho, drho


def split_resolved_support(p, blocks):
    half = EPS / 2
    kern = p <= half
    tied_kernel = sum(len(b) for b in blocks if len(b) > 1 and all(p[i] <= half for i in b))
    tied_other = sum(len(b) for b in blocks if len(b) > 1) - tied_kernel
    pos = p[~kern]
    gap_pos = float(np.min(np.diff(pos))) if len(pos) > 1 else float("inf")
    gap_ks = float(pos[0] - p[kern].max()) if kern.any() and len(pos) else float("inf")
    srs = bool(tied_other == 0 and gap_pos > TAU_FLAG and gap_ks > TAU_FLAG)
    return srs, tied_kernel, tied_other, gap_pos, gap_ks


def measure(rho, drho):
    """Items 1-5 at one point, using qfi_ref.qfi_split_ex and qfi_ref.tie_blocks unchanged."""
    r = qfi_ref.qfi_split_ex(rho, drho)
    p = np.linalg.eigh(rho)[0]  # the same call qfi_split_ex makes, so the same eigenvalues
    blocks = qfi_ref.tie_blocks(p)
    srs, tk, to, gp, gks = split_resolved_support(p, blocks)
    half = EPS / 2
    return {
        "F_Q": r["F_Q"], "F_C": r["F_C"], "F_R": r["F_R"],
        "residual": abs(r["F_Q"] - r["F_C"] - r["F_R"]),
        "n_struct": int(np.sum(p <= half)), "n_small": int(np.sum((p > half) & (p <= SUPPORT))),
        "n_support": int(np.sum(p > SUPPORT)), "p_min": float(p[0]), "p_max": float(p[-1]),
        "top_share": float(p[-1] / np.sum(p)),
        "tied_kernel": tk, "tied_other": to, "near_tie": r["near_tie"], "min_gap": float(r["min_gap"]),
        "gap_positive": gp, "gap_kernel_support": gks,
        "split_resolved": r["split_resolved"], "split_resolved_support": srs,
    }


def fq_with_eps(rho, drho, eps):
    old = qfi_ref.EPS
    qfi_ref.EPS = eps
    try:
        return qfi_ref.qfi_split_ex(rho, drho)["F_Q"]
    finally:
        qfi_ref.EPS = old


def rel(a, b):
    if a == b:
        return 0.0
    return abs(a - b) / abs(b) if b != 0 else float("inf")


# ---------------------------------------------------------------- S1-S3 pipeline controls

def rot(d, a, b, th):
    R = np.eye(d)
    c, s = np.cos(th), np.sin(th)
    R[a, a] = R[b, b] = c
    R[a, b], R[b, a] = -s, s
    return R


def synth_A(p, R):
    n = len(p)
    return np.diag(np.sqrt(p)) @ R[:, :n].T


def control_point(A_of):
    A0, Am, Ap = A_of(0.0), A_of(-H), A_of(H)
    rho, drho = rho_drho(A0, deriv(Am, Ap, H))
    return measure(rho, drho)


def run_controls():
    p0 = np.array([0.5, 0.3, 0.2])
    a = np.array([1.0, 0.0, -1.0])
    d = 5

    def s1(th):
        z = np.exp(np.log(p0) + th * a)
        return synth_A(z / z.sum(), np.eye(d))

    out = {}
    m = control_point(s1)
    ok = bool(m["F_R"] < 1e-8 and abs(m["F_Q"] - m["F_C"]) < 1e-8 * m["F_Q"])
    var = float(p0 @ a ** 2 - (p0 @ a) ** 2)
    print(f"S1 commuting: F_Q={m['F_Q']:.12f} F_C={m['F_C']:.12f} F_R={m['F_R']:.3e} (Var_p(a)={var:.12f}) -> "
          f"{'PASS' if ok else 'FAIL'}")
    out["S1"] = ok
    m = control_point(lambda th: synth_A(p0, rot(d, 0, 1, th)))
    e = 4 * (p0[0] - p0[1]) ** 2 / (p0[0] + p0[1])
    ok = bool(rel(m["F_Q"], e) < 1e-6 and m["F_C"] < 1e-8)
    print(f"S2 rotation (0,1): F_Q={m['F_Q']:.12f} F_C={m['F_C']:.3e} F_R={m['F_R']:.12f} (expect F_Q {e:.12f}) -> "
          f"{'PASS' if ok else 'FAIL'}")
    out["S2"] = ok
    m = control_point(lambda th: synth_A(p0, rot(d, 1, 3, th)))
    e = 4 * p0[1]
    ok = bool(rel(m["F_Q"], e) < 1e-6 and m["F_C"] < 1e-8 and m["split_resolved"] is False
              and m["split_resolved_support"] is True)
    print(f"S3 rotation into kernel (1,3): F_Q={m['F_Q']:.12f} F_C={m['F_C']:.3e} F_R={m['F_R']:.12f} "
          f"split_resolved={m['split_resolved']} split_resolved_support={m['split_resolved_support']} "
          f"(expect F_Q {e:.12f}, False, True) -> {'PASS' if ok else 'FAIL'}")
    out["S3"] = ok
    return out


# ---------------------------------------------------------------- model

def load_models(cache):
    import torch
    from safetensors.torch import load_file
    from tokenizers import Tokenizer
    from transformers import GPTNeoXConfig, GPTNeoXForCausalLM
    torch.set_num_threads(2)
    models, ident_ok, tok = {}, True, None
    for label, rev in fc.REVS.items():
        c, t, w = (fc.fetch(rev, f, cache) for f in ("config.json", "tokenizer.json", "model.safetensors"))
        good = (fc.git_blob_sha1(c) == fc.BLOB["config.json"] and fc.git_blob_sha1(t) == fc.BLOB["tokenizer.json"]
                and fc.sha256(w) == fc.WEIGHTS_SHA256[rev])
        ident_ok &= good
        cfg = GPTNeoXConfig(**json.load(open(c)))
        cfg._attn_implementation = "eager"
        m = GPTNeoXForCausalLM(cfg).to(torch.float64).eval()
        sd = {("lm_head.weight" if k == "embed_out.weight" else k): v.to(torch.float64)
              for k, v in load_file(w).items()}
        m.load_state_dict(sd, strict=True)
        models[label] = m
        tok = Tokenizer.from_file(t)
        print(f"R1 {label}: rev {rev[:12]} identities {'MATCH' if good else 'MISMATCH'}")
    return models, tok, ident_ok


def chosen_pairs(tok):
    chosen = []
    for i, (a, b) in enumerate(fc.CANDIDATES):
        ia, ib = tok.encode(a).ids, tok.encode(b).ids
        if len(ia) == len(ib) and sum(x != y for x, y in zip(ia, ib)) == 1 and len(chosen) < 3:
            chosen.append((i, ia, ib))
    return chosen


class Forward:
    def __init__(self, model):
        import torch
        self.torch = torch
        self.m = model
        self.E = model.gpt_neox.embed_in.weight.detach()
        self.times = []

    def __call__(self, ia, ib, th):
        torch = self.torch
        e = self.E[ia].clone()
        j = [k for k in range(len(ia)) if ia[k] != ib[k]][0]
        e[j] = (1.0 - th) * self.E[ia[j]] + th * self.E[ib[j]]
        t0 = time.perf_counter()
        with torch.no_grad():
            hs = self.m(inputs_embeds=e.unsqueeze(0), output_hidden_states=True).hidden_states
        self.times.append(time.perf_counter() - t0)
        if len(hs) != LAYERS:
            raise RuntimeError(f"hidden_states has {len(hs)} entries, registered {LAYERS}")
        return [h[0].numpy().copy() for h in hs]


def fmt(v):
    if isinstance(v, bool) or isinstance(v, (int, np.integer)) or isinstance(v, str):
        return str(v)
    return f"{float(v):.9e}"


def digest(records):
    keys = sorted(records[0])
    lines = ["|".join(f"{k}={fmt(r[k])}" for k in keys) for r in records]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def compute_points(models, tok):
    pairs = chosen_pairs(tok)
    if [i for i, _, _ in pairs] != CHOSEN:
        raise RuntimeError(f"chosen pairs {[i for i, _, _ in pairs]} differ from the registered {CHOSEN}")
    records, inter, full_hash, fwds = [], {}, hashlib.sha256(), {}
    for label, m in models.items():
        f = fwds[label] = Forward(m)
        for pi, ia, ib in pairs:
            for ti, th in enumerate(THETAS):
                A0 = f(ia, ib, th)
                Am, Ap = f(ia, ib, th - H), f(ia, ib, th + H)
                Am3, Ap3 = f(ia, ib, th - H_ALT), f(ia, ib, th + H_ALT)
                for L in range(LAYERS):
                    A = A0[L]
                    dA = deriv(Am[L], Ap[L], H)
                    full_hash.update(np.ascontiguousarray(A, "<f8").tobytes())
                    full_hash.update(np.ascontiguousarray(dA, "<f8").tobytes())
                    rho, drho = rho_drho(A, dA)
                    rec = {"model": label, "pair": pi, "theta": round(th, 10), "layer": L, "n_tokens": len(ia)}
                    rec.update(measure(rho, drho))
                    rec["rel_eps"] = rel(fq_with_eps(rho, drho, EPS_ALT), rec["F_Q"])
                    _, drho3 = rho_drho(A, deriv(Am3[L], Ap3[L], H_ALT))
                    rec["rel_h"] = rel(qfi_ref.qfi_split_ex(rho, drho3)["F_Q"], rec["F_Q"])
                    rec["tr_err"] = abs(float(np.trace(rho)) - 1.0)
                    rec["sym_err"] = float(np.max(np.abs(rho - rho.T)))
                    rec["drho_asym"] = float(np.max(np.abs(drho - drho.T)))  # exploratory, not registered
                    rec["finite"] = bool(np.all(np.isfinite(rho)) and np.all(np.isfinite(drho)) and
                                         all(np.isfinite(rec[k]) for k in ("F_Q", "F_C", "F_R", "rel_eps", "rel_h")))
                    records.append(rec)
                    if pi == 0 and ti in (0, 5, 10):
                        inter[(label, ti, L)] = (A, dA, rec)
    return records, inter, full_hash.hexdigest(), fwds, pairs


def noise_check(models, pairs):
    _, ia, ib = pairs[0]
    drho_max = dfq_max = 0.0
    for label, m in models.items():
        f = Forward(m)
        runs = []
        for _ in range(3):
            A0, Am, Ap = f(ia, ib, 0.5), f(ia, ib, 0.5 - H), f(ia, ib, 0.5 + H)
            runs.append([rho_drho(A0[L], deriv(Am[L], Ap[L], H)) for L in range(LAYERS)])
        for L in range(LAYERS):
            fq0 = qfi_ref.qfi_split_ex(*runs[0][L])["F_Q"]
            for k in (1, 2):
                drho_max = max(drho_max, float(np.max(np.abs(runs[k][L][0] - runs[0][L][0]))))
                dfq_max = max(dfq_max, abs(qfi_ref.qfi_split_ex(*runs[k][L])["F_Q"] - fq0))
    return drho_max, dfq_max


def save_npz(path, arrays):
    """Deterministic .npz (fixed zip timestamps) so the file's sha256 is reproducible."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(arrays):
            buf = io.BytesIO()
            np.lib.format.write_array(buf, np.asarray(arrays[name]), allow_pickle=False)
            z.writestr(zipfile.ZipInfo(name + ".npy", (1980, 1, 1, 0, 0, 0)), buf.getvalue(),
                       compress_type=zipfile.ZIP_DEFLATED)


def write_interchange(inter, outdir):
    labels = list(fc.REVS)
    th_idx = (0, 5, 10)
    n = inter[(labels[0], 0, 0)][0].shape[0]
    shp = (len(labels), len(th_idx), LAYERS)
    A = np.zeros(shp + (n, D_MODEL))
    dA = np.zeros_like(A)
    ref = {k: np.zeros(shp) for k in ("F_Q", "F_C", "F_R", "split_resolved", "split_resolved_support")}
    for a, lab in enumerate(labels):
        for b, ti in enumerate(th_idx):
            for L in range(LAYERS):
                A[a, b, L], dA[a, b, L], rec = inter[(lab, ti, L)]
                for k in ref:
                    ref[k][a, b, L] = float(rec[k])
    arrays = {"A": A, "dA": dA, "theta": np.array([THETAS[i] for i in th_idx]), "h": np.array(H),
              "models": np.array(labels), "pair": np.array(0), **{"ref_" + k: v for k, v in ref.items()}}
    path = os.path.join(outdir, "interchange_subset.npz")
    save_npz(path, arrays)
    return path, fc.sha256(path)


def summary(records):
    print("SUMMARY by model and layer (counts; medians/maxima of items 5-7). No F_R/F_Q or model comparison printed.")
    print("model                        L  pts SR  SRS near struct_min small_max resid_med resid_max "
          "releps_med releps_max relh_med relh_max")
    for lab in fc.REVS:
        for L in range(LAYERS):
            rs = [r for r in records if r["model"] == lab and r["layer"] == L]
            res = np.array([r["residual"] for r in rs])
            re_ = np.array([r["rel_eps"] for r in rs])
            rh = np.array([r["rel_h"] for r in rs])
            print(f"{lab:28s} {L}  {len(rs):3d} {sum(r['split_resolved'] for r in rs):2d} "
                  f"{sum(r['split_resolved_support'] for r in rs):3d} {sum(r['near_tie'] for r in rs):4d} "
                  f"{min(r['n_struct'] for r in rs):10d} {max(r['n_small'] for r in rs):9d} "
                  f"{np.median(res):.2e} {res.max():.2e} {np.median(re_):.2e} {re_.max():.2e} "
                  f"{np.median(rh):.2e} {rh.max():.2e}")
    print("split_resolved_support per pair (F20.3), counts of 11 thetas, pairs 0/1/2:")
    for lab in fc.REVS:
        row = []
        for L in range(LAYERS):
            c = [sum(r["split_resolved_support"] for r in records
                     if r["model"] == lab and r["layer"] == L and r["pair"] == p) for p in CHOSEN]
            row.append(f"L{L} {c[0]}/{c[1]}/{c[2]}")
        print(f"  {lab:28s} " + "  ".join(row))


def main():
    global SABOTAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--cache", default=os.path.expanduser("~/.cache/qfi001_q3"))
    a = ap.parse_args()
    SABOTAGE = a.sabotage
    t_start = time.perf_counter()
    if a.child:
        models, tok, _ = load_models(a.cache)
        records, _, _, _, _ = compute_points(models, tok)
        print(f"DIGEST {digest(records)}")
        return 0

    import torch
    import transformers
    print(f"QFI-001 Q3 run; sabotage={SABOTAGE}; python {sys.version.split()[0]}; numpy {np.__version__}; "
          f"torch {torch.__version__}; transformers {transformers.__version__}; threads 2; float64")
    R = {}
    # R0: public cases first
    pub = subprocess.run([sys.executable, "-I", os.path.join(HERE, "run_cases.py"),
                          os.path.join(HERE, "cases", "public.jsonl")], capture_output=True, text=True)
    neg = subprocess.run([sys.executable, "-I", os.path.join(HERE, "run_cases.py"),
                          os.path.join(HERE, "cases", "a16_must_fail.jsonl")], capture_output=True, text=True)
    pub_line = [x for x in pub.stdout.splitlines() if x.startswith("cases ")]
    neg_line = [x for x in neg.stdout.splitlines() if x.startswith("cases ")]
    print(f"R0 public: rc={pub.returncode} {pub_line}; must-fail: rc={neg.returncode} {neg_line}")
    R["R0"] = bool(pub.returncode == 0 and pub_line and pub_line[0].startswith("cases 8, failed 0")
                   and neg.returncode == 1 and neg_line and neg_line[0].startswith("cases 3, failed 3"))

    models, tok, ident_ok = load_models(a.cache)
    R["R1"] = bool(ident_ok)

    S = run_controls()
    R["R2"] = all(S.values())

    records, inter, full_sha, fwds, pairs = compute_points(models, tok)
    npts = len(records)
    r3 = sum(r["finite"] and r["tr_err"] <= 1e-12 and r["sym_err"] <= 1e-14 for r in records)
    print(f"R3 finite, |tr rho - 1| <= 1e-12, symmetric to 1e-14: {r3} of {npts}; worst tr_err "
          f"{max(r['tr_err'] for r in records):.3e} sym_err {max(r['sym_err'] for r in records):.3e}")
    R["R3"] = bool(npts == 462 and r3 == 462)
    r4 = sum(r["residual"] <= 1e-10 * max(1.0, r["F_Q"]) for r in records)
    print(f"R4 residual <= 1e-10 max(1, F_Q): {r4} of {npts}; worst residual {max(r['residual'] for r in records):.3e}")
    R["R4"] = bool(r4 == 462)

    drho_n, dfq_n = noise_check(models, pairs)
    print(f"R7 same-input noise (pair 0, theta 0.5, both models, 3 repeats): max|d rho| {drho_n:.3e} "
          f"max|d F_Q| {dfq_n:.3e} (predicted 0)")
    R["R7"] = bool(drho_n == 0.0 and dfq_n == 0.0)

    summary(records)
    dig = digest(records)
    t_main = time.perf_counter() - t_start
    ft = np.array([t for f in fwds.values() for t in f.times])
    print(f"R5 cost: main run wall {t_main:.1f} s; forward passes {len(ft)}, median {np.median(ft)*1e3:.2f} ms, "
          f"max {ft.max()*1e3:.2f} ms, total {ft.sum():.1f} s; peak RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f} MiB")
    R["R5"] = bool(t_main < 1800)

    t1 = time.perf_counter()
    cmd = [sys.executable, "-I", os.path.abspath(__file__), "--child", "--cache", a.cache] + \
        (["--sabotage"] if SABOTAGE else [])
    ch = subprocess.run(cmd, capture_output=True, text=True)
    child = [x.split()[1] for x in ch.stdout.splitlines() if x.startswith("DIGEST ")]
    print(f"R6 second process: rc={ch.returncode} digest {child[0] if child else None} "
          f"({time.perf_counter() - t1:.1f} s); this process {dig}")
    R["R6"] = bool(ch.returncode == 0 and child == [dig])

    for k in ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]:
        print(f"{k}: {'PASS' if R.get(k) is True else 'FAIL'}")
    P = {
        "P1": all(R.get(k) is True for k in ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]),
        "P2": bool(npts == 462 and sum(r["split_resolved"] is False for r in records) == 462),
        "P3": bool(npts == 462 and all(r["n_struct"] >= D_MODEL - r["n_tokens"] for r in records)),
    }
    print(f"P2 detail: split_resolved False at {sum(r['split_resolved'] is False for r in records)} of {npts}")
    print(f"P3 detail: structural zeros >= d - n at {sum(r['n_struct'] >= D_MODEL - r['n_tokens'] for r in records)} "
          f"of {npts}")
    for k, v in P.items():
        print(f"{k} {'HELD' if v is True else 'REFUTED'}")
    held = sum(v is True for v in P.values())

    print("DOORS (registration, 'What Q3 decides'):")
    print(f"  FEASIBLE as designed: {P['P1']}")
    trained = list(fc.REVS)[0]
    qual = []
    for L in range(LAYERS):
        c = sum(r["split_resolved_support"] for r in records if r["model"] == trained and r["layer"] == L)
        print(f"  trained layer {L}: split_resolved_support {c} of 33 -> {'can carry' if c >= 17 else 'cannot carry'}")
        qual.append(c >= 17)
    print(f"  layers that qualify: {sum(qual)} of {LAYERS}"
          + ("" if any(qual) else " -> d x d second moment NOT FEASIBLE; Q4 considers the n x n token Gram"))

    if not SABOTAGE:
        outdir = os.path.join(ROOT, "results", "qfi_001", "q3")
        os.makedirs(outdir, exist_ok=True)
        ipath, isha = write_interchange(inter, outdir)
        print(f"interchange: {os.path.relpath(ipath, ROOT)} sha256 {isha} ({os.path.getsize(ipath)} bytes)")
        print(f"full A/dA set (h=1e-4, 462 points, not committed): sha256 {full_sha}")
        with open(os.path.join(outdir, "results.json"), "w") as fh:
            json.dump({"registration": "e533438", "digest": dig, "R": R, "P": P, "S": S,
                       "full_A_dA_sha256": full_sha, "interchange_sha256": isha,
                       "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                                    "torch": torch.__version__, "transformers": transformers.__version__},
                       "points": records}, fh, indent=0, default=float)
    print(f"VERDICT {held} of 3 as registered")
    print(f"DIGEST {dig}")
    return 0 if held == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
