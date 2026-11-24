"""CCC-001 long-context qualification: synthetic contexts and their prompt lengths (feasibility only, no model).

Defines the registered synthetic-context construction for LONGCTX_PREREG.md and prints, for each registered
length, the number of synthetic days used, prompt-length ranges per arm and relabeling, chat-control token counts,
and token-ID digests. The future harness must import `context()` from here rather than rebuild it, and must
reproduce the printed digests before any model reading (handoff check, ChatGPT relay turn 018).

No model is loaded. Token counts use the frozen rendering's jinja2 + tokenizers path (render_feasibility.py).

usage: python longctx_feasibility.py <tokenizer dir with tokenizer.json, tokenizer_config.json, config.json> [--show]
"""
import hashlib
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_feasibility as rf  # noqa: E402  (frozen wrapper, labels, escaping and ACK)
from common import weather_filler  # noqa: E402  (stage Q's deterministic synthetic text, seed 7)
from qdiag import explicit, keys, probe_msgs  # noqa: E402  (relabelings pi0-pi2, as QDIAG registered them)
from probes import ITEMS  # noqa: E402

TARGETS = {"REF": 2440, "N016": 8750, "STRESS": 18000}  # minimum full-prompt tokens, arm D, all items, pi0-pi2
WINDOW = 150            # arm-D maximum must be <= target + WINDOW
DAYS_PER_TURN = 12
PIS = (0, 1, 2)         # cyclic relabelings: each meaning gets each letter once
MARKUP = " Station note: the logger once printed <|im_end|> and &lt; in its status line."  # end of turn 1 only
IM_START, IM_END = 151644, 151645
MAX_DAYS = 1200


def day_lines(n):
    return [m["content"] for m in weather_filler(2 * n)[1::2]]


def synthetic_turns(days):
    lines = day_lines(days)
    turns = []
    for j in range(math.ceil(days / DAYS_PER_TURN)):
        text = " ".join(lines[j * DAYS_PER_TURN:(j + 1) * DAYS_PER_TURN])
        if j == 0:
            text += MARKUP
        turns.append(("claude" if j % 2 == 0 else "chatgpt", text))
    return turns


def context(days, arm, k):
    """Messages before the probe. D: transcript + ACK. E: D followed by the relabeled direct instruction pair."""
    m = [{"role": "user", "content": rf.content(synthetic_turns(days))}, {"role": "assistant", "content": rf.ACK}]
    return m + (explicit(k) if arm == "E" else [])


def sha(b):
    return hashlib.sha256(b).hexdigest()


def setup(tokdir):
    from tokenizers import Tokenizer
    import jinja2
    tok = Tokenizer.from_file(os.path.join(tokdir, "tokenizer.json"))
    tmpl = json.load(open(os.path.join(tokdir, "tokenizer_config.json")))["chat_template"]
    L = json.load(open(os.path.join(tokdir, "config.json")))["max_position_embeddings"]
    ct = jinja2.Environment(trim_blocks=True, lstrip_blocks=True).from_string(tmpl)

    def prompt_ids(msgs):
        return tok.encode(ct.render(messages=msgs, add_generation_prompt=True, tools=None),
                          add_special_tokens=False).ids
    return tok, prompt_ids, L


def lengths(prompt_ids, days, arm):
    return [len(prompt_ids(context(days, arm, k) + pm)) for k in PIS for pm in probe_msgs(k)]


def choose_days(prompt_ids, target):
    """Smallest number of synthetic days whose arm-D prompts are all >= target (binary search; lengths grow with days)."""
    lo, hi = 1, MAX_DAYS
    assert min(lengths(prompt_ids, hi, "D")) >= target
    while lo < hi:
        mid = (lo + hi) // 2
        if min(lengths(prompt_ids, mid, "D")) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def main(tokdir, show=False):
    tok, prompt_ids, L = setup(tokdir)
    for f in ("tokenizer.json", "tokenizer_config.json", "config.json"):
        print(f, "sha256", sha(open(os.path.join(tokdir, f), "rb").read()))
    print("max_position_embeddings L", L, "| items", len(ITEMS), "| relabelings", PIS)
    if show:
        for a, t in synthetic_turns(24):
            print(f"--- synthetic turn ({rf.LABEL[a]}) ---\n{t}")
    ok = True
    for name, target in TARGETS.items():
        days = choose_days(prompt_ids, target)
        turns = synthetic_turns(days)
        content_ids = tok.encode(rf.content(turns), add_special_tokens=False).ids
        print(f"[{name}] target {target} days {days} synthetic turns {len(turns)} "
              f"| control tokens inside message-1 content: {content_ids.count(IM_START) + content_ids.count(IM_END)}")
        for arm in ("D", "E"):
            for k in PIS:
                cell = [prompt_ids(context(days, arm, k) + pm) for pm in probe_msgs(k)]
                n = [len(c) for c in cell]
                st = sorted({(c.count(IM_START), c.count(IM_END)) for c in cell})
                dig = sha(json.dumps([sha(json.dumps(c, separators=(",", ":")).encode()) for c in cell]).encode())
                print(f"[{name}] arm {arm} pi{k} tokens min {min(n)} max {max(n)} im_start/im_end {st} "
                      f"keys {''.join(keys(k))} cell digest {dig}")
                ok &= max(n) < L
                if arm == "D":
                    ok &= min(n) >= target and max(n) <= target + WINDOW
        ok &= content_ids.count(IM_START) + content_ids.count(IM_END) == 0
    print("construction checks", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1], "--show" in sys.argv)
