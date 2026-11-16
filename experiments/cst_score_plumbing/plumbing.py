"""CST score plumbing check (Claude, 2026-11-16): can we read the model's log-odds between two answer codes at the
decision position, with the Qwen2.5-7B Q4 GGUF used in CST, in both formats?

Toy prompts only (arithmetic yes/no). No CST case, split, exposure or holdout is touched. Instrument qualification,
not an experiment. Checks:
  P1 short format: prefill "DECISION:" and read the full next-token distribution; log-odds(A vs B) has the right sign
     on the toy questions, and flips sign when the A/B mapping is swapped.
  P2 determinism: the same prompt gives a bit-identical log-odds on a second evaluation.
  P3 long format: generate a free reply, locate the model's own "DECISION:" and read the log-odds there by
     re-evaluating prompt + reply prefix; it matches the letter the model actually wrote.
  P4 tokenisation: " A" and " B" (and "A", "B") are single tokens; report which is used.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction. SELF-TESTED.
"""
import math
import os
import sys

import numpy as np
from llama_cpp import Llama

GGUF = os.path.expanduser("~/models/qwen25-7b-gguf/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf")
llm = Llama(model_path=GGUF, n_ctx=2048, n_threads=os.cpu_count(), seed=0, logits_all=True, verbose=False)

TOYS = [("Is 7 greater than 3?", True), ("Is 12 an odd number?", False), ("Is 9 times 3 equal to 27?", True),
        ("Is 100 less than 10?", False), ("Is 5 plus 5 equal to 10?", True), ("Is 2 a multiple of 3?", False)]


def tok(s):
    return llm.tokenize(s.encode(), add_bos=False, special=False)


def chat_prefix(user):
    # Qwen2.5 chat template, written out (the default system line kept, as in the CST runs)
    return ("<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n"
            f"<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n")


def next_logprobs(text):
    ids = llm.tokenize(text.encode(), add_bos=False, special=True)
    llm.reset()
    llm.eval(ids)
    logits = np.array(llm.scores[llm.n_tokens - 1], dtype=np.float64)
    m = logits.max()
    return logits - (m + math.log(np.exp(logits - m).sum()))


def logodds(text, a_id, b_id):
    lp = next_logprobs(text)
    return float(lp[a_id] - lp[b_id]), float(lp[a_id]), float(lp[b_id])


def question(q, yes_code):
    no_code = "B" if yes_code == "A" else "A"
    return (f"{q} Answer {yes_code} for yes or {no_code} for no. End your answer with exactly one line, "
            f"\"DECISION: A\" or \"DECISION: B\".")


def main():
    for s in (" A", " B", "A", "B"):
        print(f"P4 token ids for {s!r}: {tok(s)}")
    A, B = tok(" A"), tok(" B")
    ok4 = len(A) == 1 and len(B) == 1
    print(f"P4 single-token ' A'/' B': {ok4}")
    A, B = A[0], B[0]

    rows, ok1 = [], True
    for q, truth in TOYS:
        for yes_code in ("A", "B"):
            lo, la, lb = logodds(chat_prefix(question(q, yes_code)) + "DECISION:", A, B)
            want_a = (truth and yes_code == "A") or (not truth and yes_code == "B")
            right = (lo > 0) == want_a
            ok1 &= right
            rows.append((q, yes_code, truth, lo))
            print(f"P1 {q:28} yes={yes_code} truth={truth!s:5} logodds(A-B)={lo:+8.3f} "
                  f"P(A)+P(B)={math.exp(la) + math.exp(lb):.3f} {'ok' if right else 'WRONG'}")
    flips = sum((r1[3] > 0) != (r2[3] > 0) for r1, r2 in zip(rows[0::2], rows[1::2]))
    print(f"P1 sign correct on all {len(rows)}: {ok1}; sign flips with mapping on {flips}/{len(TOYS)} questions")

    t = chat_prefix(question(TOYS[0][0], "A")) + "DECISION:"
    a1, a2 = logodds(t, A, B)[0], logodds(t, A, B)[0]
    print(f"P2 repeat identical: {a1 == a2} ({a1!r} vs {a2!r})")

    ok3 = True
    for q, truth in TOYS[:3]:
        prompt = chat_prefix("Think briefly first. " + question(q, "A"))
        out = llm.create_completion(prompt, max_tokens=160, temperature=0.0, top_k=1, seed=0)["choices"][0]["text"]
        i = out.rfind("DECISION:")
        if i < 0:
            print(f"P3 {q:28} no DECISION line in reply: {out[-80:]!r}")
            ok3 = False
            continue
        written = out[i + len("DECISION:"):].strip()[:1]
        lo = logodds(prompt + out[:i + len("DECISION:")], A, B)[0]
        match = (lo > 0) == (written == "A")
        ok3 &= match
        print(f"P3 {q:28} reply {len(out)} chars, wrote {written!r}, logodds at its DECISION {lo:+.3f}, "
              f"consistent={match}")
    print(f"P3 long-format readout consistent with written letter: {ok3}")
    allok = ok1 and ok4 and (a1 == a2) and ok3 and flips == len(TOYS)
    print("PLUMBING", "PASS" if allok else "FAIL")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
