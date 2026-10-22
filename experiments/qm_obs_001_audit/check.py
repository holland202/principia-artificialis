import numpy as np
rng = np.random.default_rng(20261022); n = 4; I = np.eye(n)
def superop(H, Ls):
    S = -1j*(np.kron(I, H) - np.kron(H.T, I))            # column-stacking vec convention
    for L in Ls:
        LdL = L.conj().T @ L
        S += np.kron(L.conj(), L) - 0.5*np.kron(I, LdL) - 0.5*np.kron(LdL.T, I)
    return S
def herm(): A = rng.normal(size=(n,n)) + 1j*rng.normal(size=(n,n)); return (A + A.conj().T)/2
def embed(Ls):                                            # rates matrix -> diagonal operators via classical MDS
    lam = np.array([np.real(np.diag(L)) for L in Ls])     # K x n
    D = ((lam[:, :, None] - lam[:, None, :])**2).sum(0)   # squared Euclidean distances between basis states
    J = I - np.ones((n, n))/n; G = -0.5*J@D@J
    w, V = np.linalg.eigh(G); X = V*np.sqrt(np.clip(w, 0, None))
    return [np.diag(X[:, k]).astype(complex) for k in range(n) if w[k] > 1e-14]
worst, ctrl_min, maxops = 0, np.inf, 0
for _ in range(200):
    H = herm(); Ls = [np.diag(rng.normal(size=n)).astype(complex) for _ in range(rng.integers(1, 7))]
    E = embed(Ls); maxops = max(maxops, len(E))
    worst = max(worst, np.abs(superop(H, Ls) - superop(H, E)).max())
    Lc = Ls + [herm()*0.5]; Ec = embed([L for L in Lc if np.allclose(L, np.diag(np.diag(L)))])
    ctrl_min = min(ctrl_min, np.abs(superop(H, Lc) - superop(H, Ec)).max())
print(f"equivalence: worst residual {worst:.2e} over 200 cases; max operators needed {maxops} (n-1={n-1})")
print(f"control (non-diagonal operator added): min residual {ctrl_min:.2e}")
print("CLAIM D", "HELD" if worst <= 1e-12 and maxops <= n-1 else "FAILED", "| CONTROL", "HELD" if ctrl_min > 1e-3 else "FAILED")
