"""Small byte-level GPT for TinyStories (pre-LN, RoPE, GELU MLP, tied embeddings). Claude (Anthropic, Opus 5.5)."""
import math, torch, torch.nn as nn, torch.nn.functional as F
VOCAB = 256

def rope(x):
    t, d = x.shape[-2], x.shape[-1]
    inv = 1.0 / 10000 ** (torch.arange(0, d, 2, dtype=torch.float32) / d)
    a = torch.arange(t, dtype=torch.float32)[:, None] * inv[None]
    c, s = a.cos(), a.sin(); x1, x2 = x[..., 0::2], x[..., 1::2]
    return torch.stack([x1 * c - x2 * s, x1 * s + x2 * c], -1).flatten(-2)

class Block(nn.Module):
    def __init__(s, d, h):
        super().__init__(); s.h = h; s.ln1, s.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        s.qkv = nn.Linear(d, 3 * d, bias=False); s.o = nn.Linear(d, d, bias=False)
        s.up = nn.Linear(d, 4 * d, bias=False); s.down = nn.Linear(4 * d, d, bias=False)
    def forward(s, x):
        b, t, d = x.shape
        q, k, v = s.qkv(s.ln1(x)).view(b, t, 3, s.h, d // s.h).permute(2, 0, 3, 1, 4)
        y = F.scaled_dot_product_attention(rope(q), rope(k), v, is_causal=True)
        x = x + s.o(y.transpose(1, 2).reshape(b, t, d))
        return x + s.down(F.gelu(s.up(s.ln2(x))))

class GPT(nn.Module):
    def __init__(s, d, L, h, vocab=VOCAB):   # vocab added for TLM-004; default keeps TLM-001..003 unchanged
        super().__init__(); s.emb = nn.Embedding(vocab, d)
        s.blocks = nn.ModuleList(Block(d, h) for _ in range(L)); s.lnf = nn.LayerNorm(d)
    def forward(s, x):
        h = s.emb(x)
        for blk in s.blocks: h = blk(h)
        return s.lnf(h) @ s.emb.weight.T

def n_params(m): return sum(p.numel() for p in m.parameters())
