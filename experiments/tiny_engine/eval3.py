"""TINY-ENGINE-003 evaluation (registered in REGISTRATION_003.md). Fixed case seeds in the 8000 range, never used before
this registration. Claude (Anthropic, Opus 5.5), 2026-11-20. SELF-TESTED only."""
import numpy as np
import torch

import engine as E

FAMS = {"distinct": None, "alpha32": 32, "alpha8": 8}
KS = (63, 127)                     # 63 = longest trained copy, 127 = 2x
N_TF, N_FREE = 256, 100


def case(rng, k, fam):
    T = 2 * k + 2
    return E.task_copy(rng, T) if FAMS[fam] is None else E.task_copy_rep(rng, T, FAMS[fam])


def tf_score(pred, x, mask):
    """Share of masked next tokens predicted correctly. pred = argmax over positions 0..T-2."""
    return float((pred == x[:, 1:])[mask[:, :-1]].float().mean())


@torch.no_grad()
def tf_acc(m, fam, k, seed, n=N_TF):
    rng = np.random.default_rng(seed)
    xs, ms = zip(*[case(rng, k, fam) for _ in range(n)])
    x, mask = torch.tensor(np.array(xs)), torch.tensor(np.array(ms))
    return tf_score(m(x).argmax(-1)[:, :-1], x, mask)


@torch.no_grad()
def free_whole(m, fam, k, seed, n=N_FREE):
    """Share of answers exactly right when the model writes all k copy tokens itself (greedy). The prefix is
    BOS + source + SEP only; the target is never fed in."""
    rng = np.random.default_rng(seed)
    xs = [case(rng, k, fam)[0] for _ in range(n)]
    src = torch.tensor(np.array([x[1:k + 1] for x in xs]))
    y = torch.tensor(np.array([x[:k + 2] for x in xs]))
    for _ in range(k):
        y = torch.cat([y, m(y)[:, -1:].argmax(-1)], 1)
    return float((y[:, -k:] == src).all(1).float().mean())


def evaluate3(m, offset=0):
    """offset (added for TINY-ENGINE-004) shifts every case seed, so a later run can use fresh cases. 0 = as 003."""
    m.eval()
    r = {}
    for i, fam in enumerate(FAMS):
        for k in KS:
            r[f"tf_{fam}_k{k}"] = tf_acc(m, fam, k, offset + 8000 + 10 * i + k)
    r["free_distinct_k127"] = free_whole(m, "distinct", 127, offset + 8501)
    r["free_alpha32_k63"] = free_whole(m, "alpha32", 63, offset + 8502)
    r["free_alpha8_k63"] = free_whole(m, "alpha8", 63, offset + 8503)
    m.train()
    return r
