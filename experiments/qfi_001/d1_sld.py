"""D1 public development implementation. See D1_REGISTRATION.md."""
import numpy as np


def qfi_split_ex(rho, drho):
    identity = np.eye(len(rho))
    operator = (np.kron(identity, rho) + np.kron(rho.T, identity)) / 2
    weights, modes = np.linalg.eigh(operator)
    keep = weights > 5e-13
    derivative = drho.ravel(order="F")
    coefficients = modes[:, keep].conj().T @ derivative
    solution = modes[:, keep] @ (coefficients / weights[keep])
    total = float(np.vdot(derivative, solution).real)

    p, basis = np.linalg.eigh(rho)
    classical = 0.0
    gaps = np.diff(p)
    for group in np.split(np.arange(len(p)), np.flatnonzero(gaps > 1e-12) + 1):
        block = basis[:, group]
        if len(group) == 1:
            projector = block @ block.conj().T
            slopes = [np.trace(projector @ drho).real]
        else:
            slopes = np.linalg.eigvalsh(block.conj().T @ drho @ block)
        for index, slope in zip(group, slopes):
            if 2 * p[index] > 1e-12:
                classical += slope ** 2 / p[index]
    return dict(F_Q=total, F_C=float(classical), F_R=float(total-classical),
                split_resolved=bool(np.all(gaps > 1e-6)))
