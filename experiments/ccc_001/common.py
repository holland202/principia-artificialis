"""CCC-001 instrument: decision probabilities of a pinned open model, read from logits.

The model answers each probe with one letter (A, B or C). Instead of sampling, the instrument
reads the model's next-token probabilities for the three letters after the full chat prompt and
renormalises them over {A, B, C}. That gives two per-item numbers with no sampling noise:

  S = max(pA, pB, pC)   decision stability: how concentrated the decision is (1/3 .. 1)
  G = p[key]            agreement with the evidence-based answer key   (0 .. 1)

Contexts are lists of chat messages placed before the probe. The context prefix is encoded once
and its KV cache is reused for every probe item.
"""
import copy
import hashlib
import json
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from probes import ITEMS, OPTIONS, QUESTION

MODEL_DIR = os.environ.get("CCC_MODEL_DIR") or os.path.expanduser("~/models/qwen25-1.5b-instruct")
# Defaults reproduce the pinned CPU runs. CCC_DTYPE (bfloat16|float16) and CCC_DEVICE_MAP (e.g. "auto") exist for
# the GPU amendment (GPU7B_AMENDMENT.md); unset, load() behaves exactly as before.
DTYPE = os.environ.get("CCC_DTYPE", "bfloat16")
DEVICE_MAP = os.environ.get("CCC_DEVICE_MAP") or None
ROUND = 4


def load(model_dir=MODEL_DIR):
    torch.manual_seed(0)
    torch.set_num_threads(os.cpu_count())
    tok = AutoTokenizer.from_pretrained(model_dir)
    kw = {"device_map": DEVICE_MAP} if DEVICE_MAP else {}
    model = AutoModelForCausalLM.from_pretrained(model_dir, dtype=getattr(torch, DTYPE), **kw)
    model.eval()
    return tok, model


def option_ids(tok):
    ids = [tok.encode(o, add_special_tokens=False) for o in OPTIONS]
    assert all(len(i) == 1 for i in ids), f"option letters are not single tokens: {ids}"
    flat = [i[0] for i in ids]
    assert len(set(flat)) == 3
    return flat


def render(tok, messages, gen):
    return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=gen)


@torch.no_grad()
def measure(tok, model, context, sabotage=False):
    """Return per-item dicts {key, p:[pA,pB,pC], S, G} for one context (list of messages)."""
    oid = option_ids(tok)
    probe_msgs = [[{"role": "user", "content": QUESTION.format(report=r, claim=c)}] for _, r, c in ITEMS]
    prefix_text = render(tok, context, gen=False) if context else ""
    prefix_ids = tok(prefix_text, return_tensors="pt", add_special_tokens=False).input_ids.to(model.device) if prefix_text else None
    cache = None
    if prefix_ids is not None and prefix_ids.shape[1] > 0:
        cache = model(prefix_ids, use_cache=True).past_key_values
    out = []
    for (key, _, _), pm in zip(ITEMS, probe_msgs):
        full_text = render(tok, context + pm, gen=True)
        full_ids = tok(full_text, return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
        if cache is not None:
            n = prefix_ids.shape[1]
            assert torch.equal(full_ids[0, :n], prefix_ids[0]), "prefix tokens differ: cache reuse invalid"
            logits = model(full_ids[:, n:], past_key_values=copy.deepcopy(cache), use_cache=True).logits[0, -1]
        else:
            logits = model(full_ids).logits[0, -1]
        z = logits.float()[oid]
        if sabotage:
            z = torch.zeros_like(z)
        p = torch.softmax(z, dim=0).tolist()
        p = [round(x, ROUND + 2) for x in p]
        out.append({"key": key, "p": p, "S": round(max(p), ROUND + 2), "G": round(p[OPTIONS.index(key)], ROUND + 2)})
    return out


def n_tokens(tok, context):
    return len(tok(render(tok, context, gen=False), add_special_tokens=False).input_ids) if context else 0


def summary(rows):
    n = len(rows)
    return {"S": round(sum(r["S"] for r in rows) / n, ROUND), "G": round(sum(r["G"] for r in rows) / n, ROUND),
            "modal": {o: sum(1 for r in rows if OPTIONS[r["p"].index(max(r["p"]))] == o) for o in OPTIONS}}


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def weather_filler(n_turns, seed=7):
    """Deterministic neutral context: alternating user/assistant weather log turns (synthetic, C-SYNTH)."""
    import random
    rng = random.Random(seed)
    dirs = ["north", "south", "east", "west", "north-east", "south-west"]
    msgs = []
    for t in range(n_turns):
        day = t // 2 + 1
        if t % 2 == 0:
            msgs.append({"role": "user", "content": f"Please log the weather for day {day}."})
        else:
            msgs.append({"role": "assistant", "content": (
                f"Day {day} logged: high {rng.randint(8, 24)} degrees, low {rng.randint(-2, 7)} degrees, "
                f"wind {rng.randint(3, 30)} km/h from the {rng.choice(dirs)}, "
                f"{rng.randint(0, 100)} percent cloud cover, {rng.randint(0, 12)} mm of rain. "
                f"The station battery read {rng.randint(11, 14)}.{rng.randint(0, 9)} volts.")})
    return msgs


EXPLICIT = [{"role": "user", "content": (
    "For the rest of this conversation, judge every claim only by the evidence in the report. "
    "Answer A only when the report gives direct evidence for the claim, B only when it gives direct "
    "evidence against the claim, and C whenever the report is hearsay, advertising, a single anecdote, "
    "a guess or otherwise not enough to decide.")},
    {"role": "assistant", "content": "Understood. I will judge each claim only by the evidence in its report."}]
