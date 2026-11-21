"""TLM-001 generation checks (registered). Usage: python3 gencheck.py RUN_PREFIX [d L h]
Writes RUN_PREFIX.samples.txt and RUN_PREFIX.gen.json. Claude (Anthropic, Opus 5.5), 2026-11-21. SELF-TESTED only."""
import json, re, sys
import numpy as np, torch
from gpt import GPT
P = sys.argv[1]; d, L, h = (int(a) for a in sys.argv[2:5]) if len(sys.argv) > 4 else (128, 5, 4)
N, MAXLEN, TEMP, SPAN = 20, 1000, 0.8, 50
END = b"<|endoftext|>"
train = open("data/v2_train_200MB.txt", "rb").read()
vocab = set(re.findall(rb"[a-z]+", train.lower()))

def generate(m, prompt, seed):
    g = torch.Generator().manual_seed(seed); x = list(prompt)
    with torch.no_grad():
        for _ in range(MAXLEN):
            lg = m(torch.tensor([x[-256:]]))[0, -1] / TEMP
            x.append(int(torch.multinomial(lg.softmax(-1), 1, generator=g)))
            if bytes(x[-len(END):]) == END: break
    return bytes(x)

def checks(texts):
    words = [w for t in texts for w in re.findall(rb"[a-z]{3,}", t.lower())]
    known = sum(w in vocab for w in words) / max(len(words), 1)
    spans = [t[i:i + SPAN] for t in texts for i in range(0, len(t) - SPAN + 1, SPAN)]
    copied = sum(s in train for s in spans) / max(len(spans), 1)
    return {"words": len(words), "known_word_rate": round(known, 4), "spans": len(spans), "copied_span_rate": round(copied, 4)}

if __name__ == "__main__":
    m = GPT(d, L, h)
    if P != "UNTRAINED":
        m.load_state_dict(torch.load(P + ".pt", weights_only=True))
    else:
        torch.manual_seed(991)
    m.eval()
    texts = [generate(m, b"Once upon a time", 5000 + i) for i in range(N)]
    r = checks(texts)
    # instrument check (anti-vacuity): real validation stories must score high known-word rate and low copied rate
    real = open("data/v2_valid.txt", "rb").read().split(END)[:N]
    r["valid_stories_reference"] = checks(real)
    print(json.dumps(r))
    if P != "UNTRAINED":
        open(P + ".samples.txt", "wb").write(b"\n\n=====\n\n".join(texts)); json.dump(r, open(P + ".gen.json", "w"), indent=1)
