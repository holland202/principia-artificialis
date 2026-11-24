"""CCC-001: full-prompt token lengths of a relay snapshot under the frozen rendering (feasibility only, no model).

Feasibility input for LONGCTX_PREREG.md (relay turn 019). It counts tokens; it does not run a model and it is not
an arm-A reading. It reuses the frozen rendering's scratch path in `render_feasibility.py` (jinja2 + tokenizers),
not transformers, so it is the same unindependent path that produced the registered fixture values.

For the original order and the frozen shuffle order of checkpoint k it prints:
  - context tokens (messages 1-2, no generation prompt) and a token-ID digest of the full prompt with a synthetic probe
  - the full prompt length with each of the 24 development probes (min / median / max)
  - chat-control token counts in the whole prompt, and inside message 1's content (must be 0)
  - which slots hold turns whose bytes escaping changes

usage: python prompt_lengths.py <tokenizer dir with tokenizer.json, tokenizer_config.json, config.json> <relay_prefix_k.json>
"""
import hashlib
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_feasibility as rf  # noqa: E402  (frozen rendering constants, imported, not copied)
import relay_extract as rx  # noqa: E402
from probes import ITEMS, QUESTION  # noqa: E402

IM_START, IM_END = 151644, 151645


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(tokdir, snap_path):
    from tokenizers import Tokenizer
    import jinja2
    tok = Tokenizer.from_file(os.path.join(tokdir, "tokenizer.json"))
    tmpl = json.load(open(os.path.join(tokdir, "tokenizer_config.json")))["chat_template"]
    L = json.load(open(os.path.join(tokdir, "config.json")))["max_position_embeddings"]
    ct = jinja2.Environment(trim_blocks=True, lstrip_blocks=True).from_string(tmpl)

    def msgs(turns, probe):
        m = [{"role": "user", "content": rf.content(turns)}, {"role": "assistant", "content": rf.ACK}]
        return m + ([{"role": "user", "content": probe}] if probe is not None else [])

    def ids(s):
        return tok.encode(s, add_special_tokens=False).ids

    for f in ("tokenizer.json", "tokenizer_config.json", "config.json"):
        print(f, "sha256", sha(open(os.path.join(tokdir, f), "rb").read()))
    print("max_position_embeddings L", L)
    fx = ids(ct.render(messages=msgs(rf.FIXTURE, rf.PROBE), add_generation_prompt=True, tools=None))
    print("fixture check tokens", len(fx), "ids sha256", sha(json.dumps(fx, separators=(",", ":")).encode()))

    snap = json.load(open(snap_path))
    k = snap["checkpoint"]
    by_n = {t["nnn"]: t for t in snap["turns"]}
    assert sorted(by_n) == list(range(1, k + 1))
    print("snapshot", os.path.basename(snap_path), "sha256", sha(open(snap_path, "rb").read()), "turns", k)
    dev = [QUESTION.format(report=r, claim=c) for _, r, c in ITEMS]
    print("development probes", len(dev), "probe-only tokens min/max",
          min(len(ids(p)) for p in dev), max(len(ids(p)) for p in dev))
    changed = [n for n in range(1, k + 1) if rf.esc(by_n[n]["rendered"]) != by_n[n]["rendered"]]
    print("turns changed by escaping", changed, "speakers", sorted({by_n[n]["speaker"] for n in changed}))

    for name, order in (("original", list(range(1, k + 1))), ("shuffle", rx.shuffle_perm(k))):
        turns = [(by_n[n]["speaker"], by_n[n]["rendered"]) for n in order]
        slots_alt = all(by_n[n]["speaker"] == ("claude" if i % 2 == 0 else "chatgpt") for i, n in enumerate(order))
        ctx = ids(ct.render(messages=msgs(turns, None), add_generation_prompt=False, tools=None))
        body_ids = ids(rf.content(turns))
        syn = ids(ct.render(messages=msgs(turns, rf.PROBE), add_generation_prompt=True, tools=None))
        full = [len(ids(ct.render(messages=msgs(turns, p), add_generation_prompt=True, tools=None))) for p in dev]
        print(f"[{name}] order {order} labels alternate {slots_alt}")
        print(f"[{name}] escaped-turn slots {[order.index(n) + 1 for n in changed]}")
        print(f"[{name}] context tokens {len(ctx)} | message-1 content tokens {len(body_ids)}")
        print(f"[{name}] control tokens in message-1 content: im_start {body_ids.count(IM_START)} im_end {body_ids.count(IM_END)}")
        print(f"[{name}] synthetic-probe prompt tokens {len(syn)} im_start {syn.count(IM_START)} im_end {syn.count(IM_END)}"
              f" ids sha256 {sha(json.dumps(syn, separators=(',', ':')).encode())}")
        print(f"[{name}] dev-probe full prompt tokens min {min(full)} median {statistics.median(full)} max {max(full)}"
              f" | under L: {max(full) < L}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
