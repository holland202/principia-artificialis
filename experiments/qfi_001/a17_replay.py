#!/usr/bin/env python3
"""QFI-001 A17.1: replay the saved support cutoff cases in a second environment. Registered in A17_REGISTRATION.md
(f8d9644) before this file existed. Reports state and SLD-operator eigenvalues against their masks, exact
eigenvalues of the stored float64 matrices (mpmath), the float64 decidability verdict, and both implementations'
outputs. Author: Claude (Anthropic, Opus 5.5). Exit 0 on a completed run whatever the verdicts; exit 2 if a
required case is missing (fail-closed: nothing was measured).

Usage: OPENBLAS_NUM_THREADS=1 python experiments/qfi_001/a17_replay.py
"""
import json
import os
import platform
import sys

import mpmath as mp
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d1_sld  # noqa: E402
import qfi_ref  # noqa: E402

CASES = ("support-1-rotated", "support-1.01-rotated")
CUT = 5e-13           # reference: 2p > 1e-12  <=>  p > 5e-13; D1: operator weight > 5e-13
U = 2.0 ** -53
mp.mp.dps = 60


def mat(m):
    re = np.array(m["re"], dtype=float)
    im = np.array(m["im"], dtype=float) if "im" in m else np.zeros_like(re)
    return re + 1j * im


def exact_eigs_2x2(rho):
    a, d = mp.mpf(rho[0, 0].real), mp.mpf(rho[1, 1].real)
    b = mp.mpc(rho[0, 1].real, rho[0, 1].imag)
    c = mp.mpc(rho[1, 0].real, rho[1, 0].imag)
    # the stored matrix need not be exactly Hermitian; report the asymmetry and use its Hermitian part
    herm_b = (b + mp.conj(c)) / 2
    mid, half = (a + d) / 2, (a - d) / 2
    r = mp.sqrt(half ** 2 + abs(herm_b) ** 2)
    return mid - r, mid + r, abs(b - mp.conj(c)), abs(mp.mpf(rho[0, 0].imag)) + abs(mp.mpf(rho[1, 1].imag))


def side(x, cut=CUT):
    return "KEPT (above)" if x > cut else "MASKED (at or below)"


def main():
    rows = {}
    with open(os.path.join(HERE, "cases", "d1_replay.jsonl")) as f:
        for line in f:
            if line.strip():
                c = json.loads(line)
                rows[c["id"]] = c
    missing = [c for c in CASES if c not in rows]
    if missing:
        print(f"MISSING cases {missing}: nothing measured")
        return 2
    print(f"env python={sys.version.split()[0]} numpy={np.__version__} machine={platform.machine()} "
          f"OPENBLAS_NUM_THREADS={os.environ.get('OPENBLAS_NUM_THREADS')} mpmath={mp.__version__} dps={mp.mp.dps}")
    for cid in CASES:
        c = rows[cid]
        rho, drho = mat(c["rho"]), mat(c["drho"])
        print(f"\n== {cid}  expect={c['expect']}")
        state = np.linalg.eigvalsh(rho)
        print("state eigvalsh   :", [repr(float(x)) for x in state], "| small ->", side(state[0]))
        op = (np.kron(np.eye(2), rho) + np.kron(rho.T, np.eye(2))) / 2
        w = np.linalg.eigh(op)[0]
        print("SLD-op weights   :", [repr(float(x)) for x in w], "| kept by D1:", int(np.sum(w > CUT)),
              "of 4 | smallest ->", side(w[0]))
        lo, hi, asym, imdiag = exact_eigs_2x2(rho)
        print("exact (60 dig)   : lo =", mp.nstr(lo, 25), " hi =", mp.nstr(hi, 25))
        print("stored asymmetry : |b - conj(c)| =", mp.nstr(asym, 5), "| |Im diag| =", mp.nstr(imdiag, 5))
        norm = float(np.linalg.norm(rho, 2))
        margin = abs(lo - mp.mpf(CUT))
        bound = 4 * U * norm
        verdict = "DECIDABLE" if margin > bound else "UNDECIDABLE"
        print(f"margin |lo-5e-13| = {mp.nstr(margin, 6)}  vs 4u*||rho||2 = {bound:.3e}  -> {verdict}; "
              f"exact lo is {'above' if lo > CUT else 'at/below'} the cutoff")
        print("numpy lo - exact :", mp.nstr(mp.mpf(float(state[0])) - lo, 6),
              "| op smallest - exact:", mp.nstr(mp.mpf(float(w[0])) - lo, 6))
        for name, impl in (("qfi_ref", qfi_ref), ("d1_sld", d1_sld)):
            r = impl.qfi_split_ex(rho, drho)
            print(f"{name:8s}: F_Q={r['F_Q']!r} F_C={r['F_C']!r} F_R={r['F_R']!r} "
                  f"split_resolved={r['split_resolved']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
