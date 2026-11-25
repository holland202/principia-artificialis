#!/usr/bin/env python3
"""QFI-001 reference code (Q1): quantum Fisher information, its classical/rotation split,
Bures distance and measurement Fisher information, checked against closed forms.

Registration: experiments/qfi_001/Q1_PREREG.md (bc44b2e) plus Amendment 1 (0f01126) and Amendment 2 (088c544:
exact numerical ties resolved inside the tied block, near-ties flagged, C9-C10, --no-tie-fix).
Author: Claude (Anthropic, Opus 5.5). NumPy only. Deterministic (seed 4).

Usage:  python experiments/qfi_001/qfi_ref.py [--sabotage] [--no-tie-fix]
"""
import argparse
import sys

import numpy as np

EPS = 1e-12
TAU_TIE = 1e-12   # Amendment 2 item 2: numerical ties only
TAU_FLAG = 1e-6   # Amendment 2 item 3: near-ties are flagged, never repaired
SABOTAGE = False
NO_TIE_FIX = False


# ---------------------------------------------------------------- instrument

def _denom(pk, pl):
    """Denominator of the QFI sum. --sabotage swaps in a wrong one (anti-vacuity, M3)."""
    if SABOTAGE:
        return 2.0 * np.maximum(pk, pl)
    return pk + pl


def tie_blocks(p):
    """Maximal runs of sorted eigenvalues whose neighbours differ by <= TAU_TIE (Amendment 2 item 2)."""
    blocks, cur = [], [0]
    for k in range(1, len(p)):
        if p[k] - p[k - 1] <= TAU_TIE:
            cur.append(k)
        else:
            blocks.append(cur)
            cur = [k]
    blocks.append(cur)
    return blocks


def split_in_basis(p, V, drho):
    """Split in the eigenbasis V (columns, eigenvalues p ascending). Inside each tied block, rotate to the basis that
    diagonalises that block of <k|drho|l> (degenerate perturbation basis), unless --no-tie-fix.
    Returns dict with F_Q, F_C, F_R, near_tie, min_gap, n_tied."""
    V = V.copy()
    X = V.conj().T @ drho @ V  # <k|drho|l>
    d = len(p)
    FQ = 0.0
    for k in range(d):
        for l in range(d):
            if p[k] + p[l] > EPS:
                FQ += 2.0 * abs(X[k, l]) ** 2 / _denom(p[k], p[l])
    blocks = tie_blocks(p)
    if not NO_TIE_FIX:
        for b in blocks:
            if len(b) > 1:
                _, R = np.linalg.eigh(X[np.ix_(b, b)])
                V[:, b] = V[:, b] @ R
        X = V.conj().T @ drho @ V
    FC = FR = 0.0
    for k in range(d):
        for l in range(d):
            if k != l and p[k] + p[l] > EPS:
                FR += 2.0 * abs(X[k, l]) ** 2 / _denom(p[k], p[l])
    for k in range(d):
        if p[k] > EPS:
            FC += X[k, k].real ** 2 / p[k]
    gaps = [p[blocks[i + 1][0]] - p[blocks[i][-1]] for i in range(len(blocks) - 1)]
    min_gap = min(gaps) if gaps else np.inf
    return {"F_Q": FQ, "F_C": FC, "F_R": FR, "near_tie": bool(min_gap <= TAU_FLAG), "min_gap": min_gap,
            "n_tied": sum(len(b) for b in blocks if len(b) > 1)}


def qfi_split_ex(rho, drho):
    p, V = np.linalg.eigh(rho)
    return split_in_basis(p, V, drho)


def qfi_split(rho, drho):
    """Return (F_Q, F_C, F_R) for state rho and derivative drho (both Hermitian)."""
    r = qfi_split_ex(rho, drho)
    return r["F_Q"], r["F_C"], r["F_R"]


def sld(rho, drho):
    """Symmetric logarithmic derivative, always with the correct denominator (Amendment 1, item 4)."""
    p, V = np.linalg.eigh(rho)
    X = V.conj().T @ drho @ V
    S = p[:, None] + p[None, :]
    L = np.where(S > EPS, 2.0 * X / np.where(S > EPS, S, 1.0), 0.0)
    return V @ L @ V.conj().T


def measurement_fi(rho, drho, basis):
    """Classical Fisher information of the projective measurement onto the columns of `basis`."""
    F = 0.0
    for m in range(basis.shape[1]):
        v = basis[:, m]
        pm = (v.conj() @ rho @ v).real
        dpm = (v.conj() @ drho @ v).real
        if pm > EPS:
            F += dpm ** 2 / pm
    return F


def _psd_sqrt(A):
    w, V = np.linalg.eigh(A)
    return (V * np.sqrt(np.clip(w, 0.0, None))) @ V.conj().T


def bures_sq(rho, sigma):
    """d_B^2 = 2(1 - sqrt(F)), F = (tr sqrt(sqrt(rho) sigma sqrt(rho)))^2."""
    r = _psd_sqrt(rho)
    w = np.linalg.eigvalsh(r @ sigma @ r)
    root_fid = np.sum(np.sqrt(np.clip(w, 0.0, None)))
    return 2.0 * (1.0 - root_fid)


def fc_fd(rho_of, theta, h=1e-6):
    """Independent route to F_C (Amendment 1, C8): finite-differenced sorted eigenvalues."""
    pp = np.linalg.eigvalsh(rho_of(theta + h))
    pm = np.linalg.eigvalsh(rho_of(theta - h))
    p0 = np.linalg.eigvalsh(rho_of(theta))
    dp = (pp - pm) / (2 * h)
    keep = p0 > EPS
    return float(np.sum(dp[keep] ** 2 / p0[keep]))


# ---------------------------------------------------------------- families

SX = np.array([[0, 1], [1, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def c1_rho(t, r=0.6):
    return (I2 + r * (np.cos(t) * SX + np.sin(t) * SZ)) / 2


def c1_drho(t, r=0.6):
    return r * (-np.sin(t) * SX + np.cos(t) * SZ) / 2


A2 = np.array([0.0, 1.0, 2.0, 3.0])


def c2_p(t):
    z = np.exp(t * A2)
    return z / z.sum()


def c2_rho(t):
    return np.diag(c2_p(t)).astype(complex)


def c2_drho(t):
    p = c2_p(t)
    return np.diag(p * (A2 - p @ A2)).astype(complex)


def c3_rho(t):
    psi = np.array([np.cos(t), np.sin(t)], dtype=complex)
    return np.outer(psi, psi.conj())


def c3_drho(t):
    psi = np.array([np.cos(t), np.sin(t)], dtype=complex)
    dpsi = np.array([-np.sin(t), np.cos(t)], dtype=complex)
    return np.outer(dpsi, psi.conj()) + np.outer(psi, dpsi.conj())


def random_family(rng, d=4):
    A = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    H = (A + A.conj().T) / 2
    lam, W = np.linalg.eigh(H)
    b = rng.normal(size=d)
    c = rng.normal(size=d)

    def rho_of(t):
        U = (W * np.exp(1j * t * lam)) @ W.conj().T
        Dg = np.exp(b + t * c)
        Dg = Dg / Dg.sum()
        return U @ np.diag(Dg) @ U.conj().T

    return rho_of


def random_unitary(rng, d=4):
    Z = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    Q, R = np.linalg.qr(Z)
    return Q * (np.diag(R) / np.abs(np.diag(R)))


# ---------------------------------------------------------------- run

def main():
    global SABOTAGE, NO_TIE_FIX
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true")
    ap.add_argument("--no-tie-fix", action="store_true")
    a = ap.parse_args()
    SABOTAGE, NO_TIE_FIX = a.sabotage, a.no_tie_fix
    print(f"QFI-001 Q1 reference run; sabotage={SABOTAGE}; no_tie_fix={NO_TIE_FIX}; numpy {np.__version__}")
    ok = {}

    def close(x, y, tol=1e-10):
        return bool(np.isfinite(x) and abs(x - y) < tol)

    # C1
    t = 0.7
    FQ, FC, FR = qfi_split(c1_rho(t), c1_drho(t))
    fcfd = fc_fd(c1_rho, t)
    print(f"C1 qubit rotation: F_Q={FQ:.12f} F_C={FC:.3e} F_R={FR:.12f} F_C^fd={fcfd:.3e} (expect 0.36, 0, 0.36)")
    ok["C1"] = close(FQ, 0.36) and close(FC, 0.0) and close(FR, 0.36)
    c8_c1 = bool(np.isfinite(fcfd) and fcfd < 1e-8)

    # C2
    t = 0.4
    p = c2_p(t)
    var = float(p @ A2 ** 2 - (p @ A2) ** 2)
    FQ, FC, FR = qfi_split(c2_rho(t), c2_drho(t))
    fcfd = fc_fd(c2_rho, t)
    print(f"C2 commuting: F_Q={FQ:.12f} F_C={FC:.12f} F_R={FR:.3e} Var_p(a)={var:.12f} F_C^fd={fcfd:.12f}")
    ok["C2"] = close(FQ, var) and close(FC, var) and close(FR, 0.0)
    c8_c2 = bool(np.isfinite(fcfd) and abs(fcfd - var) < 1e-6)

    # C3
    t = 0.3
    FQ, FC, FR = qfi_split(c3_rho(t), c3_drho(t))
    print(f"C3 pure qubit: F_Q={FQ:.12f} F_C={FC:.3e} F_R={FR:.12f} (expect F_Q = 4)")
    ok["C3"] = close(FQ, 4.0)

    # C4-C8 on 200 random d=4 families, seed 4
    rng = np.random.default_rng(4)
    h = 1e-6
    delta = 1e-4
    n = 200
    c4_viol = 0
    c4_worst = -np.inf
    c5_pass = c6_pass = c7_pass = c8a_pass = c8b_pass = 0
    c8_elig = 0
    n_flag = 0
    c5_worst = c6_worst = c7_worst = c8a_worst = c8b_worst = 0.0
    shares, pmins, pmaxs, fqs = [], [], [], []
    nan_seen = False
    for i in range(n):
        rho_of = random_family(rng)
        rho = rho_of(0.0)
        drho = (rho_of(h) - rho_of(-h)) / (2 * h)
        drho = (drho + drho.conj().T) / 2
        r = qfi_split_ex(rho, drho)
        FQ, FC, FR = r["F_Q"], r["F_C"], r["F_R"]
        n_flag += r["near_tie"]
        vals = [FQ, FC, FR]
        p = np.linalg.eigvalsh(rho)
        pmins.append(p.min()); pmaxs.append(p.max()); fqs.append(FQ)
        shares.append(FR / FQ if FQ > 0 else np.nan)
        # C4
        for _ in range(50):
            Fm = measurement_fi(rho, drho, random_unitary(rng))
            vals.append(Fm)
            c4_worst = max(c4_worst, Fm - FQ)
            if not Fm <= FQ + 1e-9:
                c4_viol += 1
        # C5
        L = sld(rho, drho)
        _, B = np.linalg.eigh(L)
        Fs = measurement_fi(rho, drho, B)
        e5 = abs(Fs - FQ) / FQ
        c5_worst = max(c5_worst, e5); c5_pass += e5 < 1e-8
        # C6
        d2 = bures_sq(rho, rho_of(delta))
        e6 = abs(d2 / delta ** 2 - FQ / 4) / (FQ / 4)
        c6_worst = max(c6_worst, e6); c6_pass += e6 < 1e-3
        # C7 (bookkeeping)
        e7 = abs(FQ - (FC + FR))
        c7_worst = max(c7_worst, e7); c7_pass += e7 < 1e-10
        # C8 (independent split), eligible families only (Amendment 2 item 6)
        fcfd = fc_fd(rho_of, 0.0)
        if np.min(np.diff(p)) > 1e3 * h:
            c8_elig += 1
            e8a = abs(FC - fcfd) / max(FC, 1e-12)
            e8b = abs(FR - (FQ - fcfd)) / FQ
            c8a_worst = max(c8a_worst, e8a); c8a_pass += e8a < 1e-4
            c8b_worst = max(c8b_worst, e8b); c8b_pass += e8b < 1e-4
        vals += [Fs, d2, fcfd]
        if not np.all(np.isfinite(vals)):
            nan_seen = True

    shares = np.array(shares)
    print(f"generated inputs: {n} families, d=4; eigenvalue min {min(pmins):.4f} max {max(pmaxs):.4f}; "
          f"F_Q range {min(fqs):.4f}..{max(fqs):.4f}; "
          f"F_R/F_Q share min {np.nanmin(shares):.4f} median {np.nanmedian(shares):.4f} max {np.nanmax(shares):.4f}")
    print(f"C4 measurement FI <= F_Q + 1e-9: violations {c4_viol} of {n*50}; worst (FI - F_Q) {c4_worst:.3e}")
    print(f"C5 SLD basis attains F_Q (rel < 1e-8): {c5_pass} of {n}; worst rel {c5_worst:.3e}")
    print(f"C6 Bures d^2/delta^2 vs F_Q/4 (rel < 1e-3): {c6_pass} of {n}; worst rel {c6_worst:.3e}")
    print(f"C7 F_Q = F_C + F_R (abs < 1e-10, bookkeeping): {c7_pass} of {n}; worst abs {c7_worst:.3e}")
    need8 = int(np.ceil(0.975 * c8_elig))
    print(f"near_tie flags (min gap <= {TAU_FLAG:g}) among the {n} families: {n_flag}")
    print(f"C8 eligible (min eigengap > 1e-3): {c8_elig} of {n} (floor 150); need {need8} per half")
    print(f"C8 F_C vs F_C^fd (rel < 1e-4): {c8a_pass} of {c8_elig}; worst {c8a_worst:.3e}")
    print(f"C8 F_R vs F_Q - F_C^fd (rel < 1e-4): {c8b_pass} of {c8_elig}; worst {c8b_worst:.3e}")
    print(f"C8 C1 F_C^fd < 1e-8: {c8_c1}; C2 |F_C^fd - Var| < 1e-6: {c8_c2}")

    ok["C4"] = c4_viol == 0
    ok["C5"] = c5_pass >= 195
    ok["C6"] = c6_pass >= 195
    ok["C7"] = c7_pass == n
    ok["C8"] = c8_elig >= 150 and c8a_pass >= need8 and c8b_pass >= need8 and c8_c1 and c8_c2

    # C9: exact tie on a commuting path (Amendment 2 item 4)
    rng9 = np.random.default_rng(0)
    U = random_unitary(rng9, 3)
    rho9 = U @ np.diag([0.5, 0.25, 0.25]).astype(complex) @ U.conj().T
    drho9 = U @ np.diag([0.0, 0.1, -0.1]).astype(complex) @ U.conj().T
    r9 = qfi_split_ex(rho9, drho9)
    print(f"C9 exact tie: F_Q={r9['F_Q']:.12f} F_C={r9['F_C']:.12f} F_R={r9['F_R']:.3e} tied={r9['n_tied']} "
          f"(expect 0.08, 0.08, 0)")
    c9a = close(r9["F_Q"], 0.08) and close(r9["F_C"], 0.08) and bool(np.isfinite(r9["F_R"]) and r9["F_R"] < 1e-10)
    p9, V9 = np.linalg.eigh(rho9)
    blk = [b for b in tie_blocks(p9) if len(b) > 1]
    rngR = np.random.default_rng(9)
    inv_worst = np.inf if len(blk) != 1 else 0.0
    if len(blk) == 1:
        b = blk[0]
        for _ in range(20):
            Rf = np.eye(3, dtype=complex)
            Rf[np.ix_(b, b)] = random_unitary(rngR, len(b))
            rr = split_in_basis(p9, V9 @ Rf, drho9)
            inv_worst = max(inv_worst, abs(rr["F_C"] - r9["F_C"]), abs(rr["F_R"] - r9["F_R"]),
                            abs(rr["F_Q"] - r9["F_Q"]))
    print(f"C9 basis invariance over 20 in-block unitaries: worst abs difference {inv_worst:.3e} (< 1e-10)")
    ok["C9"] = c9a and bool(inv_worst < 1e-10)

    # C10: near-tie, ChatGPT note qfi001/chatgpt/008 (Amendment 2 item 5)
    r10 = qfi_split_ex(np.diag([0.5 + 1e-9, 0.5 - 1e-9]).astype(complex),
                       np.array([[0, 0.1], [0.1, 0]], dtype=complex))
    print(f"C10 near tie: F_Q={r10['F_Q']:.12f} F_C={r10['F_C']:.3e} F_R={r10['F_R']:.12f} "
          f"near_tie={r10['near_tie']} min_gap={r10['min_gap']:.3e} (expect 0.04, 0, 0.04, True)")
    ok["C10"] = close(r10["F_Q"], 0.04) and close(r10["F_C"], 0.0) and close(r10["F_R"], 0.04) and r10["near_tie"]

    ok["finite"] = not nan_seen
    for k in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "finite"]:
        print(f"{k}: {'PASS' if ok.get(k) is True else 'FAIL'}")
    verdict = "PASS" if all(ok.get(k) is True for k in
                            ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "finite"]) else "FAIL"
    print(f"VERDICT {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
