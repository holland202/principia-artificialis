"""TOR-001 code (T4). Frozen registration: REGISTRATION_TOR001.md at 3dbfed0 (FREEZE_TOR001.md, e994fff).

usage:
  python3 tor001.py gen OUTDIR        write F1, F2, F3 as field directories (train.npy, test.npy, meta.json), run G1,
                                      and render first frames to OUTDIR/first_frames.png (C-SYNTH; look before training)
  python3 tor001.py score FIELD_DIR   fit every arm on train.npy, then open test.npy and score (blind fields too)
  python3 tor001.py run OUTDIR        gen + score F1, F2, F3, P1..P6 and the frozen precedence table
  python3 tor001.py selftest          decide() on synthetic error tables; no data
Arms: L4, L* (POD + DMD), T2 (projected torus), NP (T2 without projection), K4 (free R^4, linear A), E2 (R^2, MLP).
Named choices not fixed by the registration (stand-ins, M4): one hidden layer with tanh in every MLP; E2's dynamics
map z -> MLP(z) directly; K4's A starts at the identity; T2/NP's omega starts at (0.5, 0.5); the loss is the mean squared
error of the 1-step and 10-step decoded predictions, summed; batches are random start times in the training trajectory.
Pinned environment (registration: "version pinned when the code is committed"): torch 2.15.0+cpu, numpy 2.5.3,
Python 3.13; both versions are printed at the start of every run. The run warns if they differ.
Claude (Anthropic, Opus 5.5), 2026-11-26. SELF-TESTED only. The author must not see ChatGPT's blind fields.
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

N, DT, KAPPA, SIGMA = 32, 0.1, 8.0, 0.01
TRAIN_T, N_TEST, TEST_H = 4000, 20, 1000
OMEGA = np.array([1.0, math.sqrt(2.0), math.sqrt(3.0)])
HORIZONS = (0, 1, 10, 100, 1000)
SEEDS = (0, 1, 2)
STEPS, BATCH, LR = 20000, 64, 1e-3
LEARNED = ("T2", "NP", "K4", "E2")
EVENTS = []  # file-open and fit-finished order (interface check)

_g = np.arange(N) * 2 * np.pi / N
X, Y = np.meshgrid(_g, _g, indexing="ij")


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ------------------------------------------------------------------ fields

def field(name, th):
    """th: (T, k) phases -> (T, N, N)."""
    th = np.atleast_2d(th)
    a = (X + Y)[None] - th[:, 0, None, None]
    b = (2 * X - Y)[None] - th[:, 1, None, None]
    if name == "F1":
        return 0.6 * np.sin(a) + 0.4 * np.sin(b)
    p = lambda z: np.exp(KAPPA * (np.cos(z) - 1))  # noqa: E731
    u = p(a) + p(b)
    if name == "F3":
        u = u + p((X - 2 * Y)[None] - th[:, 2, None, None])
    return u


def phases(name, th0, T):
    k = 3 if name == "F3" else 2
    t = np.arange(T)[:, None] * DT
    return th0[None, :k] + OMEGA[None, :k] * t


def gen(outdir):
    os.makedirs(outdir, exist_ok=True)
    rng7 = np.random.default_rng(7)
    starts = rng7.uniform(0, 2 * np.pi, size=(N_TEST, 3))
    g1 = True
    for name in ("F1", "F2", "F3"):
        d = os.path.join(outdir, name)
        os.makedirs(d, exist_ok=True)
        th = phases(name, np.zeros(3), TRAIN_T)
        clean = field(name, th)
        again = field(name, th)
        noise = np.random.default_rng(1).normal(0, SIGMA, size=clean.shape)
        test = np.stack([field(name, phases(name, s, TEST_H + 1)) for s in starts])
        test2 = np.stack([field(name, phases(name, s, TEST_H + 1)) for s in starts])
        regen = max(np.abs(clean - again).max(), np.abs(test - test2).max())
        ok = regen <= 1e-12
        g1 &= ok
        np.save(os.path.join(d, "train.npy"), clean + noise)
        np.save(os.path.join(d, "test.npy"), test)
        json.dump({"dt": DT}, open(os.path.join(d, "meta.json"), "w"))
        print(f"G1 {name} regeneration max abs diff {regen:.1e} {'OK' if ok else 'FAILED'}; "
              f"train {clean.shape} test {test.shape}; field range {clean.min():.3f}..{clean.max():.3f}")
        for f in ("train.npy", "test.npy", "meta.json"):
            print(f"  {name}/{f} sha256 {sha_file(os.path.join(d, f))}")
        if name == "F1":
            s = np.linalg.svd(clean.reshape(TRAIN_T, -1), compute_uv=False) ** 2
            e = s / s.sum()
            n4 = int((e > 1e-8).sum())
            print(f"G1 rank oracle (clean F1, uncentred): normalised squared singular values > 1e-8: {n4} "
                  f"(need exactly 4); top 6 {np.round(e[:6], 10).tolist()}")
            g1 &= n4 == 4
        if name == "F2":
            s = np.linalg.svd((clean + noise).reshape(TRAIN_T, -1), compute_uv=False) ** 2
            print(f"  F2 noisy-training POD: modes for 99.9% energy {int(np.searchsorted(np.cumsum(s) / s.sum(), 0.999) + 1)}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(3, 4, figsize=(8, 6))
        for i, name in enumerate(("F1", "F2", "F3")):
            tr = np.load(os.path.join(outdir, name, "train.npy"))
            for j, t in enumerate((0, 1, 10, 100)):
                ax[i, j].imshow(tr[t], cmap="viridis")
                ax[i, j].set_title(f"{name} t={t}", fontsize=8)
                ax[i, j].axis("off")
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "first_frames.png"), dpi=80)
        print("first frames ->", os.path.join(outdir, "first_frames.png"))
    except Exception as ex:  # rendering is a look, not a gate
        print("first frames not rendered:", ex)
    print("G1", "HELD" if g1 else "FAILED")
    return g1


# ------------------------------------------------------------------ arms

def fit_linear(train, rank):
    Xf = train.reshape(len(train), -1)
    _, s, Vt = np.linalg.svd(Xf, full_matrices=False)
    if rank is None:
        e = np.cumsum(s ** 2) / np.sum(s ** 2)
        rank = int(np.searchsorted(e, 0.999) + 1)
    V = Vt[:rank].T
    a = Xf @ V
    Am, *_ = np.linalg.lstsq(a[:-1], a[1:], rcond=None)  # a[t+1] = a[t] @ Am
    return {"rank": rank, "V": V, "A": Am, "params": V.size + Am.size}


def roll_linear(m, u0, hs):
    a = u0.reshape(len(u0), -1) @ m["V"]
    out, cur, t = {}, a, 0
    for h in sorted(hs):
        while t < h:
            cur, t = cur @ m["A"], t + 1
        out[h] = (cur @ m["V"].T).reshape(u0.shape)
    return out


def torch_arm(kind, seed, train):
    import torch
    import torch.nn as nn
    torch.set_num_threads(2)
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    D = N * N
    lat = 2 if kind == "E2" else 4
    enc = nn.Sequential(nn.Linear(D, 128), nn.Tanh(), nn.Linear(128, lat))
    dec = nn.Sequential(nn.Linear(lat, 128), nn.Tanh(), nn.Linear(128, D))
    mods = [enc, dec]
    if kind in ("T2", "NP"):
        om = nn.Parameter(torch.tensor([0.5, 0.5], dtype=torch.float64))
        extra = [om]
    elif kind == "K4":
        Amat = nn.Parameter(torch.eye(4, dtype=torch.float64))
        extra = [Amat]
    else:
        dyn = nn.Sequential(nn.Linear(2, 32), nn.Tanh(), nn.Linear(32, 2))
        mods.append(dyn)
        extra = []
    for mm in mods:
        mm.double()
    params = [p for mm in mods for p in mm.parameters()] + extra

    def project(z):
        if kind == "T2":
            z = z.view(-1, 2, 2)
            return (z / z.norm(dim=-1, keepdim=True).clamp_min(1e-12)).view(-1, 4)
        return z

    def step(z):
        if kind in ("T2", "NP"):
            c, s = torch.cos(om * DT), torch.sin(om * DT)
            z = z.view(-1, 2, 2)
            x, y = z[..., 0], z[..., 1]
            return torch.stack([c * x - s * y, s * x + c * y], -1).view(-1, 4)
        if kind == "K4":
            return z @ Amat.T
        return dyn(z)

    opt = torch.optim.Adam(params, lr=LR)
    tr = torch.from_numpy(train.reshape(len(train), -1))
    t0 = time.time()
    for it in range(STEPS):
        ix = torch.from_numpy(rng.integers(0, len(train) - 10, size=BATCH))
        z = project(enc(tr[ix]))
        loss = 0.0
        for h in range(1, 11):
            z = step(z)
            if h in (1, 10):
                loss = loss + ((dec(z) - tr[ix + h]) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    fit_s = time.time() - t0
    n_par = sum(p.numel() for p in params)

    def roll(u0, hs):
        with torch.no_grad():
            z = project(enc(torch.from_numpy(u0.reshape(len(u0), -1))))
            out, t = {}, 0
            for h in sorted(hs):
                while t < h:
                    z, t = step(z), t + 1
                out[h] = dec(z).numpy().reshape(u0.shape)
            return out
    diag = {"omega": om.detach().numpy().round(4).tolist()} if kind in ("T2", "NP") else {}
    return {"roll": roll, "params": n_par, "latent": lat, "fit_s": round(fit_s, 1), "final_loss": float(loss), **diag}


def rel_err(pred, true):
    num = np.sqrt(((pred - true) ** 2).reshape(len(true), -1).sum(1))
    den = np.sqrt((true ** 2).reshape(len(true), -1).sum(1))
    return float(np.mean(num / den))


def score(fdir):
    EVENTS.clear()
    EVENTS.append(("open", "train.npy"))
    train = np.load(os.path.join(fdir, "train.npy"))
    dt = json.load(open(os.path.join(fdir, "meta.json")))["dt"]
    assert abs(dt - DT) < 1e-15, dt
    models = {"L4": fit_linear(train, 4), "L*": fit_linear(train, None)}
    EVENTS.append(("fit", "L4"))
    EVENTS.append(("fit", "L*"))
    for k in LEARNED:
        for s in SEEDS:
            models[f"{k}/{s}"] = torch_arm(k, s, train)
            EVENTS.append(("fit", f"{k}/{s}"))
            print(f"  fitted {os.path.basename(fdir)} {k} seed {s}: params {models[f'{k}/{s}']['params']} "
                  f"fit {models[f'{k}/{s}']['fit_s']} s final loss {models[f'{k}/{s}']['final_loss']:.3e} "
                  f"{models[f'{k}/{s}'].get('omega', '')}", flush=True)
    EVENTS.append(("open", "test.npy"))
    test = np.load(os.path.join(fdir, "test.npy"))
    opened_test = EVENTS.index(("open", "test.npy"))
    order_ok = all(i < opened_test for i, e in enumerate(EVENTS) if e[0] == "fit")
    print(f"interface: {len([e for e in EVENTS if e[0] == 'fit'])} fits finished before test.npy was opened: {order_ok}")
    u0 = test[:, 0]
    errs = {}
    for name, m in models.items():
        pr = roll_linear(m, u0, HORIZONS) if name in ("L4", "L*") else m["roll"](u0, HORIZONS)
        errs[name] = {h: rel_err(pr[h], test[:, h]) for h in HORIZONS}
    for k in ("L4", "L*"):
        print(f"  {os.path.basename(fdir)} {k}: rank {models[k]['rank']} params {models[k]['params']} | " +
              " ".join(f"h{h} {errs[k][h]:.4f}" for h in HORIZONS))
    for k in LEARNED:
        for s in SEEDS:
            print(f"  {os.path.basename(fdir)} {k}/{s}: " + " ".join(f"h{h} {errs[f'{k}/{s}'][h]:.4f}" for h in HORIZONS))
    return errs, order_ok


# ------------------------------------------------------------------ decision (pure)

def med(errs, arm, h):
    return float(np.median([errs[f"{arm}/{s}"][h] for s in SEEDS]))


def decide(E, gates):
    """E: {'F1','F2','F3': errs}; errs[arm or arm/seed][horizon] -> float. gates: {'G1': bool, 'order': bool}.
    Returns (row, outcome, predictions dict)."""
    try:
        if not (gates["G1"] is True and gates["order"] is True):
            return 1, "INCONCLUSIVE", {}
        # Full table first (ChatGPT note tor001/chatgpt/010): every field x arm/seed x horizon must be present and
        # finite, including entries no prediction uses. A missing or extra entry gives row 1.
        arms = ["L4", "L*"] + [f"{k}/{s}" for k in LEARNED for s in SEEDS]
        if set(E) != {"F1", "F2", "F3"}:
            return 1, "INCONCLUSIVE", {}
        for f in ("F1", "F2", "F3"):
            if set(E[f]) != set(arms):
                return 1, "INCONCLUSIVE", {}
            for a in arms:
                if set(E[f][a]) != set(HORIZONS) or \
                        not all(isinstance(E[f][a][h], float) and math.isfinite(E[f][a][h]) for h in HORIZONS):
                    return 1, "INCONCLUSIVE", {}
        F1, F2, F3 = E["F1"], E["F2"], E["F3"]
        t2 = med(F2, "T2", 1000)
        P = {"P1": F1["L4"][1000] < 0.01,
             "P2": t2 < 0.10 and med(F2, "K4", 1000) >= 3 * t2 and F2["L4"][1000] >= 3 * t2,
             "P3": t2 <= F2["L*"][1000],
             "P4": med(F2, "E2", 1) >= 3 * med(F2, "T2", 1),
             "P5": med(F3, "T2", 100) > 0.30,
             "P6": t2 <= 0.5 * med(F2, "NP", 1000) and
             sum(F2[f"T2/{s}"][1000] < F2[f"NP/{s}"][1000] for s in SEEDS) >= 2}
        if not P["P5"]:
            return 2, "WRONG-TOPOLOGY CONTROL DID NOT SEPARATE", P
        if P["P2"] and P["P3"] and P["P6"]:
            return 3, "TORUS PROJECTION EARNS ITS PLACE (on F2)", P
        if P["P2"] and P["P3"] and not P["P6"]:
            return 4, "T2 BEATS THE NAMED BASELINES; NO PROJECTION BENEFIT MET P6", P
        if P["P2"] and not P["P3"]:
            return 5, "TORUS BEATS SMALL MODELS ONLY", P
        if not P["P2"]:
            return 6, "NO TORUS ADVANTAGE DETECTED", P
        return 7, "INCONCLUSIVE (fallback)", P
    except (KeyError, TypeError, ValueError):
        return 1, "INCONCLUSIVE", {}


def selftest():
    def errs(t2, np_, k4, e2_1, t2_1, l4, ls):
        e = {"L4": {h: l4 for h in HORIZONS}, "L*": {h: ls for h in HORIZONS}}
        for s in SEEDS:
            e[f"T2/{s}"] = {h: (t2_1 if h == 1 else t2) for h in HORIZONS}
            e[f"NP/{s}"] = {h: np_ for h in HORIZONS}
            e[f"K4/{s}"] = {h: k4 for h in HORIZONS}
            e[f"E2/{s}"] = {h: e2_1 for h in HORIZONS}
        return e
    g = {"G1": True, "order": True}
    F1 = errs(0.05, 0.05, 0.05, 0.05, 0.05, 0.001, 0.001)
    F3bad = errs(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
    cases = [
        ("projection earns", {"F1": F1, "F2": errs(0.05, 0.2, 0.2, 0.3, 0.01, 0.2, 0.06), "F3": F3bad}, g, 3),
        ("chatgpt note 004 case", {"F1": F1, "F2": errs(0.05, 0.05, 0.20, 0.3, 0.01, 0.20, 0.06), "F3": F3bad}, g, 4),
        ("high-rank linear as good", {"F1": F1, "F2": errs(0.05, 0.2, 0.2, 0.3, 0.01, 0.2, 0.04), "F3": F3bad}, g, 5),
        ("no advantage", {"F1": F1, "F2": errs(0.15, 0.2, 0.2, 0.3, 0.01, 0.2, 0.04), "F3": F3bad}, g, 6),
        ("F3 does not separate", {"F1": F1, "F2": errs(0.05, 0.2, 0.2, 0.3, 0.01, 0.2, 0.06),
                                  "F3": errs(0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1)}, g, 2),
        ("G1 failed", {"F1": F1, "F2": errs(0.05, 0.2, 0.2, 0.3, 0.01, 0.2, 0.06), "F3": F3bad},
         {"G1": False, "order": True}, 1),
        ("test opened early", {"F1": F1, "F2": errs(0.05, 0.2, 0.2, 0.3, 0.01, 0.2, 0.06), "F3": F3bad},
         {"G1": True, "order": False}, 1),
        ("NaN", {"F1": F1, "F2": errs(float("nan"), 0.2, 0.2, 0.3, 0.01, 0.2, 0.06), "F3": F3bad}, g, 1),
    ]
    # Regression for ChatGPT note tor001/chatgpt/010: an entry no prediction uses is deleted -> row 1, not row 6
    E = {k: errs(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5) for k in ("F1", "F2", "F3")}
    cases.append(("complete table (all 0.5)", E, g, 6))
    E2 = {k: errs(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5) for k in ("F1", "F2", "F3")}
    del E2["F1"]["L*"][10]
    cases.append(("unused entry deleted", E2, g, 1))
    bad = 0
    for name, E, gg, want in cases:
        got = decide(E, gg)[0]
        print(f"selftest {name}: row {got} want {want} {'ok' if got == want else 'WRONG'}")
        bad += got != want
    print("SELFTEST", "PASS" if bad == 0 else f"FAIL ({bad})")
    return bad == 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    if not selftest():
        sys.exit("decide() selftest failed")
    import torch
    print(f"numpy {np.__version__} torch {torch.__version__}; code sha256 {sha_file(os.path.abspath(__file__))}")
    if (np.__version__, torch.__version__) != ("2.5.3", "2.15.0+cpu"):
        print("WARNING: environment differs from the pinned torch 2.15.0+cpu / numpy 2.5.3")
    if cmd == "gen":
        gen(sys.argv[2])
    elif cmd == "score":
        score(sys.argv[2])
    elif cmd == "run":
        out = sys.argv[2]
        g1 = gen(out)
        E, order = {}, True
        for name in ("F1", "F2", "F3"):
            E[name], ok = score(os.path.join(out, name))
            order &= ok
        row, outcome, P = decide(E, {"G1": g1, "order": order})
        for k, v in P.items():
            print(f"{k}: {'HELD' if v else 'REFUTED'}")
        print(f"VERDICT row {row}: {outcome}")
        json.dump({"errors": E, "predictions": P, "verdict": [row, outcome]},
                  open(os.path.join(out, "tor001_results.json"), "w"), indent=1, default=str)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
