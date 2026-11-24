#!/usr/bin/env python3
"""QFI-001 reference code (Q1): quantum Fisher information, its classical/rotation split,
Bures distance and measurement Fisher information, checked against closed forms.

Registration: experiments/qfi_001/Q1_PREREG.md (bc44b2e) plus Amendment 1 (0f01126).
Author: Claude (Anthropic, Opus 5.5). NumPy only. Deterministic (seed 4).

Usage:  python experiments/qfi_001/qfi_ref.py [--sabotage]
"""
import argparse
import sys

import numpy as np

EPS = 1e-12
SABOTAGE = False


# ---------------------------------------------------------------- instrument

def _denom(pk, pl):
    """Denominator of the QFI sum. --sabotage swaps in a wrong one (anti-vacuity, M3)."""
    if SABOTAGE:
        return 2.0 * np.maximum(pk, pl)
    return pk + pl


def qfi_split(rho, drho):
    """Return (F_Q, F_C, F_R) for state rho and derivative drho (both Hermitian)."""
    p, V = np.linalg.eigh(rho)
    X = V.conj().T @ drho @ V  # <k|drho|l>
    d = len(p)
    FQ = FC = FR = 0.0
    for k in range(d):
        for l in range(d):
            s = p[k] + p[l]
            if s <= EPS:
                continue
            term = 2.0 * abs(X[k, l]) ** 2 / _denom(p[k], p[l])
            FQ += term
            if k != l:
                FR += term
    for k in range(d):
        if p[k] > EPS:
            FC += X[k, k].real ** 2 / p[k]
    return FQ, FC, FR


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
    global SABOTAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true")
    SABOTAGE = ap.parse_args().sabotage
    print(f"QFI-001 Q1 reference run; sabotage={SABOTAGE}; numpy {np.__version__}")
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
    c5_worst = c6_worst = c7_worst = c8a_worst = c8b_worst = 0.0
    shares, pmins, pmaxs, fqs = [], [], [], []
    nan_seen = False
    for i in range(n):
        rho_of = random_family(rng)
        rho = rho_of(0.0)
        drho = (rho_of(h) - rho_of(-h)) / (2 * h)
        drho = (drho + drho.conj().T) / 2
        FQ, FC, FR = qfi_split(rho, drho)
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
        # C8 (independent split)
        fcfd = fc_fd(rho_of, 0.0)
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
    print(f"C8 F_C vs F_C^fd (rel < 1e-4): {c8a_pass} of {n}; worst {c8a_worst:.3e}")
    print(f"C8 F_R vs F_Q - F_C^fd (rel < 1e-4): {c8b_pass} of {n}; worst {c8b_worst:.3e}")
    print(f"C8 C1 F_C^fd < 1e-8: {c8_c1}; C2 |F_C^fd - Var| < 1e-6: {c8_c2}")

    ok["C4"] = c4_viol == 0
    ok["C5"] = c5_pass >= 195
    ok["C6"] = c6_pass >= 195
    ok["C7"] = c7_pass == n
    ok["C8"] = c8a_pass >= 195 and c8b_pass >= 195 and c8_c1 and c8_c2
    ok["finite"] = not nan_seen
    for k in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "finite"]:
        print(f"{k}: {'PASS' if ok.get(k) is True else 'FAIL'}")
    verdict = "PASS" if all(ok.get(k) is True for k in
                            ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "finite"]) else "FAIL"
    print(f"VERDICT {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
