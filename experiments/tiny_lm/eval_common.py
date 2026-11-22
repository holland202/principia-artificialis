"""TLM-004 common evaluator: bits per byte of one fixed text for byte models and token models alike.
Text: the first 200 stories of TinyStoriesV2-GPT4-valid.txt, each followed by <|endoftext|>. Sliding windows of 256
units (bytes or tokens), stride 128: the first window scores all its predictions, later windows score only their last
128, so every unit after the first is predicted once with at least 128 units of context (fewer only at the start).
bpb = total bits / UTF-8 bytes of the text. Claude (Anthropic, Opus 5.5), 2026-11-21. SELF-TESTED only."""
import math
import numpy as np, torch, torch.nn.functional as F
END = "<|endoftext|>"
_v = open("data/v2_valid.txt", "rb").read().decode("utf-8").split(END)
TEXT = "".join(s + END for s in _v[:200])
NBYTES = len(TEXT.encode("utf-8"))

def units(tokenizer=None):
    if tokenizer is None:
        return np.frombuffer(TEXT.encode("utf-8"), dtype=np.uint8).astype(np.int64)
    ids = []
    for s in _v[:200]:
        ids += tokenizer.encode(s).ids + [tokenizer.token_to_id(END)]
    return np.array(ids, dtype=np.int64)

@torch.no_grad()
def bpb(m, u, T=256, S=128):
    m.eval(); bits = 0.0; n = 0; starts = list(range(0, len(u) - 1, S))
    for st in starts:
        x = torch.from_numpy(u[st:st + T + 1][None])
        if x.shape[1] < 2: break
        lp = F.cross_entropy(m(x[:, :-1])[0], x[0, 1:], reduction="none")
        keep = lp if st == 0 else lp[T - S:]
        bits += keep.sum().item() / math.log(2); n += keep.numel()
        if st + T + 1 >= len(u): break
    return bits / NBYTES, n

# Anti-vacuity text: the same characters in a fixed random order (numpy seed 0). Same byte count as TEXT.
_chars = list(TEXT)
SHUF = "".join(np.array(_chars, dtype=object)[np.random.default_rng(0).permutation(len(_chars))])

def units_shuffled(tokenizer=None):
    if tokenizer is None:
        return np.frombuffer(SHUF.encode("utf-8"), dtype=np.uint8).astype(np.int64)
    return np.array(tokenizer.encode(SHUF).ids, dtype=np.int64)
