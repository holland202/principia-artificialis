"""Tiny in-context engine: an attention-only transformer with rotary (relative) positions, trained from scratch on a
mix of in-context tasks, then tested on lengths it never saw. See REGISTRATION.md.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-16. SELF-TESTED only."""
import math

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

N_CONTENT = 127                    # content tokens 1..127
BOS, SEP, QRY = 0, 128, 129
VOCAB = 130
CFG = dict(d_model=128, n_heads=2, n_layers=2, train_lens=(32, 64, 96, 128), batch=64, lr=1e-3, steps=6000)
PERIODS_SEEN = tuple(L for L in range(4, 25) if L not in (7, 11, 15, 19, 23))
PERIODS_HELD = (7, 11, 15, 19, 23)


# ---------------------------------------------------------------- tasks: (tokens, loss mask), mask marks positions whose
# NEXT token is determined by the context, so the score is only over learnable predictions.
def task_periodic(rng, T, periods):
    L = int(rng.choice(periods))
    seg = rng.integers(1, N_CONTENT + 1, size=L)
    x = np.concatenate([[BOS], np.resize(seg, T - 1)])
    m = np.zeros(T, bool)
    m[L:T - 1] = True              # predicting x[t+1] from position t, for t+1 > L
    return x, m


KEYS = np.arange(1, 64)            # keys and values come from disjoint halves of the vocabulary, so a key token can
VALS = np.arange(64, N_CONTENT + 1)  # never also appear as a value (that made the first version of this task ambiguous)


def task_recall(rng, T):
    """BOS k1 v1 ... kn vn, then queries 'QRY k v' about earlier pairs, filling length T."""
    n = min(len(KEYS), max(2, (T - 1) * 2 // 5 // 2 * 2 // 2))
    nq = (T - 1 - 2 * n) // 3
    while nq < 1:
        n -= 1
        nq = (T - 1 - 2 * n) // 3
    keys = rng.choice(KEYS, size=n, replace=False)
    vals = rng.choice(VALS, size=n)
    x = [BOS] + [t for kv in zip(keys, vals) for t in kv]
    m = [False] * len(x)
    for j in rng.integers(0, n, size=nq):
        x += [QRY, keys[j], vals[j]]
        m += [False, True, False]                       # position of the key predicts the value
    pad = T - len(x)
    x += list(rng.integers(1, N_CONTENT + 1, size=pad))
    m += [False] * pad
    return np.array(x), np.array(m)


def task_copy(rng, T):
    """BOS s SEP s: s has distinct tokens (so copying is unambiguous); length fills T."""
    k = min((T - 2) // 2, N_CONTENT)
    s = rng.choice(np.arange(1, N_CONTENT + 1), size=k, replace=False)
    x = np.concatenate([[BOS], s, [SEP], s])
    m = np.zeros(len(x), bool)
    m[k + 1:len(x) - 1] = True                          # from SEP onward, each next token is the copy
    pad = T - len(x)
    x = np.concatenate([x, rng.integers(1, N_CONTENT + 1, size=pad)])
    m = np.concatenate([m, np.zeros(pad, bool)])
    return x, m


def task_copy_rep(rng, T, alpha=None):
    """TINY-ENGINE-003: BOS s SEP s where s draws, with replacement, from an alphabet of `alpha` distinct symbols
    (random size 2..127 when alpha is None), so symbols repeat inside s. Same layout and mask as task_copy."""
    k = min((T - 2) // 2, N_CONTENT)
    a = int(rng.integers(2, N_CONTENT + 1)) if alpha is None else alpha
    sym = rng.choice(np.arange(1, N_CONTENT + 1), size=a, replace=False)
    s = rng.choice(sym, size=k, replace=True)
    x = np.concatenate([[BOS], s, [SEP], s])
    m = np.zeros(len(x), bool)
    m[k + 1:len(x) - 1] = True
    pad = T - len(x)
    return (np.concatenate([x, rng.integers(1, N_CONTENT + 1, size=pad)]),
            np.concatenate([m, np.zeros(pad, bool)]))


TASKS = ("periodic", "recall", "copy")


def make_batch(rng, n, T, task=None, periods=PERIODS_SEEN, rep_frac=0.0):
    """rep_frac (TINY-ENGINE-003): share of copy examples drawn by task_copy_rep. At 0.0 no extra random numbers are
    drawn, so CFG and CFG2 batches are unchanged."""
    xs, ms = [], []
    for _ in range(n):
        t = task or TASKS[int(rng.integers(len(TASKS)))]
        x, m = (task_periodic(rng, T, periods) if t == "periodic" else task_recall(rng, T) if t == "recall"
                else task_copy_rep(rng, T) if rep_frac and rng.random() < rep_frac else task_copy(rng, T))
        xs.append(x); ms.append(m)
    return torch.tensor(np.array(xs)).long(), torch.tensor(np.array(ms))


# ---------------------------------------------------------------- model
def rope(x, base=10000.0, frac=1.0):
    """Rotary position embedding on the first `frac` of the last dim of (b, h, t, d); the rest is left position-free."""
    if frac < 1.0:
        r = int(x.shape[-1] * frac) // 2 * 2
        return torch.cat([rope(x[..., :r], base), x[..., r:]], -1)
    t, d = x.shape[-2], x.shape[-1]
    inv = 1.0 / base ** (torch.arange(0, d, 2, dtype=torch.float32) / d)
    ang = torch.arange(t, dtype=torch.float32)[:, None] * inv[None]
    cos, sin = ang.cos(), ang.sin()
    x1, x2 = x[..., 0::2], x[..., 1::2]
    return torch.stack([x1 * cos - x2 * sin, x1 * sin + x2 * cos], -1).flatten(-2)


class Attn(nn.Module):
    def __init__(self, d, h, use_rope=True, rope_frac=1.0):
        super().__init__()
        self.h, self.dh, self.use_rope, self.rope_frac = h, d // h, use_rope, rope_frac
        self.q, self.k, self.v, self.o = (nn.Linear(d, d, bias=False) for _ in range(4))

    def forward(self, x):
        b, t, d = x.shape
        sh = lambda z: z.view(b, t, self.h, self.dh).transpose(1, 2)
        q, k = sh(self.q(x)), sh(self.k(x))
        if self.use_rope:
            q, k = rope(q, frac=self.rope_frac), rope(k, frac=self.rope_frac)
        y = F.scaled_dot_product_attention(q, k, sh(self.v(x)), is_causal=True)
        return self.o(y.transpose(1, 2).reshape(b, t, d))


class TinyEngine(nn.Module):
    """Token embedding (no position embedding: positions enter only through rotary attention), attention-only
    pre-LN blocks, separate (untied) unembedding. Tying the unembedding to the embedding stopped learning entirely
    in exploration (0.00 periodic accuracy after 1,500 steps at d_model 256; untied reached 1.00)."""

    def __init__(self, cfg=CFG):
        super().__init__()
        d = cfg["d_model"]
        self.pos_kind = cfg.get("pos", "rope")
        self.emb = nn.Embedding(VOCAB, d)
        self.pos = nn.Embedding(1024, d) if self.pos_kind == "learned" else None
        self.lns = nn.ModuleList(nn.LayerNorm(d) for _ in range(cfg["n_layers"]))
        nope = set(cfg.get("nope_layers", ()))       # layers with no positional encoding at all (content-only)
        self.attn = nn.ModuleList(Attn(d, cfg["n_heads"], self.pos_kind == "rope" and i not in nope,
                                       cfg.get("rope_frac", 1.0)) for i in range(cfg["n_layers"]))
        self.lnf = nn.LayerNorm(d)
        self.head = None if cfg.get("tied", False) else nn.Linear(d, VOCAB, bias=False)

    def forward(self, x):
        h = self.emb(x)
        if self.pos is not None:
            h = h + self.pos(torch.arange(x.shape[1]))
        for ln, at in zip(self.lns, self.attn):
            h = h + at(ln(h))
        h = self.lnf(h)
        return self.head(h) if self.head is not None else h @ self.emb.weight.T


def n_params(m):
    return sum(p.numel() for p in m.parameters())


# ---------------------------------------------------------------- evaluation
@torch.no_grad()
def accuracy(m, task, T, seed, n=256, periods=PERIODS_SEEN):
    x, mask = make_batch(np.random.default_rng(seed), n, T, task, periods)
    pred = m(x).argmax(-1)[:, :-1]
    ok = (pred == x[:, 1:])[mask[:, :-1]]
    return float(ok.float().mean())


EVAL_LENS = (128, 256, 512, 1024)   # 128 = longest trained; 256, 512, 1024 = 2x, 4x and 8x beyond it
# TINY-ENGINE-002: the fix. Layer 1 (the layer that matches content) gets no positional encoding, so matching an
# earlier token cannot depend on how far back it is. Layer 0 keeps rotary positions (it needs order to look one
# token back). Same parameter count as CFG.
CFG2 = dict(CFG, nope_layers=(1,))
# TINY-ENGINE-003: CFG2 with half of the copy examples using repeated symbols (task_copy_rep). Same model and size.
CFG3 = dict(CFG2, copy_rep_frac=0.5)


def evaluate(m):
    m.eval()
    r = {}
    for L in EVAL_LENS:
        n = 256 if L <= 128 else 96
        r[f"periodic_heldout_L{L}"] = accuracy(m, "periodic", L, 100 + L, n, periods=PERIODS_HELD)
        r[f"recall_L{L}"] = accuracy(m, "recall", L, 200 + L, n)
        r[f"copy_L{L}"] = accuracy(m, "copy", L, 300 + L, n)
    r["periodic_seen_L128"] = accuracy(m, "periodic", 128, 99)
    m.train()
    return r


def train(seed, cfg=CFG, log=None):
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    rng = np.random.default_rng(seed)
    m = TinyEngine(cfg)
    opt = torch.optim.AdamW(m.parameters(), lr=cfg["lr"], weight_decay=0.0)
    for step in range(1, cfg["steps"] + 1):
        x, mask = make_batch(rng, cfg["batch"], int(rng.choice(cfg["train_lens"])), rep_frac=cfg.get("copy_rep_frac", 0.0))
        logits = m(x)[:, :-1]
        loss = F.cross_entropy(logits[mask[:, :-1]], x[:, 1:][mask[:, :-1]])
        opt.zero_grad(); loss.backward(); opt.step()
        if log and step % 500 == 0:
            log(step, float(loss.detach()))
    return m
