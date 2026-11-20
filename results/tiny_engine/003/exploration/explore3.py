"""TINY-ENGINE-003 exploration (not registered). Usage: python3 -I explore3.py ENGINE_DIR ARM SEED OUT.json
Claude (Anthropic, Opus 5.5), 2026-11-20. SELF-TESTED only."""
import json, sys, time
sys.path.insert(0, sys.argv[1])
import numpy as np, torch, torch.nn.functional as F
import engine as E
torch.set_num_threads(1)
ARM, SEED, OUT = sys.argv[2], int(sys.argv[3]), sys.argv[4]

def copy_rep(rng, T, alpha=None):
    k = min((T - 2) // 2, E.N_CONTENT)
    a = int(rng.integers(2, E.N_CONTENT + 1)) if alpha is None else alpha
    sym = rng.choice(np.arange(1, E.N_CONTENT + 1), size=a, replace=False)
    s = rng.choice(sym, size=k, replace=True)
    x = np.concatenate([[E.BOS], s, [E.SEP], s]); m = np.zeros(len(x), bool); m[k + 1:len(x) - 1] = True
    pad = T - len(x)
    return (np.concatenate([x, rng.integers(1, E.N_CONTENT + 1, size=pad)]), np.concatenate([m, np.zeros(pad, bool)]))

orig = E.task_copy
if ARM == "B":
    E.task_copy = lambda rng, T: copy_rep(rng, T) if rng.random() < 0.5 else orig(rng, T)

def fam_case(rng, k, fam):
    T = 2 * k + 2
    if fam == "distinct": return orig(rng, T)
    return copy_rep(rng, T, {"alpha32": 32, "alpha8": 8}[fam])

@torch.no_grad()
def tf_acc(m, fam, k, seed, n=256):
    rng = np.random.default_rng(seed)
    xs, ms = zip(*[fam_case(rng, k, fam) for _ in range(n)])
    x, mask = torch.tensor(np.array(xs)), torch.tensor(np.array(ms))
    pred = m(x).argmax(-1)[:, :-1]
    return float((pred == x[:, 1:])[mask[:, :-1]].float().mean())

@torch.no_grad()
def free_whole(m, fam, k, seed, n=100):
    rng = np.random.default_rng(seed)
    xs = [fam_case(rng, k, fam)[0] for _ in range(n)]
    src = torch.tensor(np.array([x[1:k + 1] for x in xs]))
    y = torch.tensor(np.array([x[:k + 2] for x in xs]))
    for _ in range(k):
        y = torch.cat([y, m(y)[:, -1:].argmax(-1)], 1)
    return float((y[:, -k:] == src).all(1).float().mean())

def report(m):
    m.eval(); r = {}
    for fam in ("distinct", "alpha32", "alpha8"):
        for k in (63, 127):
            r[f"tf_{fam}_k{k}"] = round(tf_acc(m, fam, k, 5000 + k + len(fam)), 4)
    r["free_alpha8_k63"] = free_whole(m, "alpha8", 63, 6001)
    r["free_distinct_k127"] = free_whole(m, "distinct", 127, 6002)
    for L in (128, 1024):
        n = 256 if L == 128 else 96
        r[f"periodic_heldout_L{L}"] = round(E.accuracy(m, "periodic", L, 7100 + L, n, periods=E.PERIODS_HELD), 4)
        r[f"recall_L{L}"] = round(E.accuracy(m, "recall", L, 7200 + L, n), 4)
    return r

torch.manual_seed(991)
untrained = report(E.TinyEngine(E.CFG2))
t = time.time()
m = E.train(SEED, E.CFG2)
res = {"arm": ARM, "seed": SEED, "train_s": round(time.time() - t), "untrained": untrained, "trained": report(m)}
json.dump(res, open(OUT, "w"), indent=1); print(json.dumps(res))
