"""CST-001 runner: one isolated generation per (arm, pair, version), greedy, appended to a JSONL file; resumable.

Usage: python3 experiments/cst_001/run_model.py --split dev --out results/cst_001/dev_outputs.jsonl
       [--model PATH] [--arms ABCDE] [--limit-seconds 540] [--only N]
Each line: {"arm", "pair", "version", "output", "seconds", "prompt_tokens", "new_tokens"}.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-14.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
import exposures  # noqa: E402

PER_CELL = {"dev": 2, "test": 4, "dev2": 2}
MAX_NEW = 320          # the recorded dev run used 320; --reason uses 400


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=("dev", "test", "dev2"), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=os.path.expanduser("~/models/qwen25-1.5b-instruct"))
    ap.add_argument("--arms", default="ABCDE")
    ap.add_argument("--limit-seconds", type=float, default=540)
    ap.add_argument("--only", type=int, default=0, help="stop after this many new generations (0 = no cap)")
    ap.add_argument("--hop", type=int, choices=(1, 2), help="run only pairs of this hop")
    ap.add_argument("--gguf", help="run a GGUF model through llama.cpp instead of transformers")
    ap.add_argument("--reason", action="store_true",
                    help="EXPLORATORY variant: ask for step-by-step reasoning before the decision line")
    a = ap.parse_args()

    if a.gguf:
        from llama_cpp import Llama
        llm = Llama(model_path=a.gguf, n_ctx=2048, n_threads=os.cpu_count(), seed=0, verbose=False)

        def generate(msgs, max_new):
            r = llm.create_chat_completion(messages=msgs, temperature=0.0, top_k=1, max_tokens=max_new, seed=0)
            u = r["usage"]
            return r["choices"][0]["message"]["content"], u["prompt_tokens"], u["completion_tokens"]
    else:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        torch.manual_seed(0)
        tok = AutoTokenizer.from_pretrained(a.model)
        model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16)
        model.eval()

        def generate(msgs, max_new):
            ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
            with torch.no_grad():
                out = model.generate(**ids, max_new_tokens=max_new, do_sample=False, temperature=None,
                                     top_p=None, top_k=None)
            new = out[0, ids["input_ids"].shape[1]:]
            return tok.decode(new, skip_special_tokens=True), int(ids["input_ids"].shape[1]), int(len(new))

    pairs = [p for p in cases.build(a.split, PER_CELL[a.split]) if not a.hop or p["hop"] == a.hop]
    done = set()
    if os.path.exists(a.out):
        with open(a.out) as fh:
            for line in fh:
                r = json.loads(line)
                done.add((r["arm"], r["pair"], r["version"]))
    jobs = [(arm, p, v) for arm in a.arms for p in pairs for v in p["versions"]
            if (arm, p["pair"], v["version"]) not in done]
    print(f"{len(done)} done, {len(jobs)} to go", flush=True)
    t_start, n = time.time(), 0
    with open(a.out, "a") as fh:
        for arm, p, v in jobs:
            if time.time() - t_start > a.limit_seconds or (a.only and n >= a.only):
                break
            prompt = v["prompt"]
            if a.reason:
                prompt = prompt.replace(cases.ASK, "Think it through step by step first. " + cases.ASK)
            msgs = exposures.history(arm) + [{"role": "user", "content": exposures.test_message(arm, prompt)}]
            t0 = time.time()
            text, n_prompt, n_new = generate(msgs, 400 if a.reason else MAX_NEW)
            rec = {"arm": arm, "pair": p["pair"], "version": v["version"], "output": text,
                   "seconds": round(time.time() - t0, 2), "prompt_tokens": n_prompt, "new_tokens": n_new}
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            n += 1
    left = len(jobs) - n
    print(f"wrote {n}; {left} left; {time.time() - t_start:.0f} s", flush=True)
    return 0 if left == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
