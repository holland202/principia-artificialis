"""TLM-004 generation checks for token models: same prompt, temperature, seeds and checks as gencheck.py; stories end at
<|endoftext|> or after 330 tokens (about 1,000 bytes). Usage: python3 gencheck_tok.py RUN_PREFIX d L h
Claude (Anthropic, Opus 5.5), 2026-11-21. SELF-TESTED only."""
import json, sys
import torch
from tokenizers import Tokenizer
from gpt import GPT
import gencheck as G
P = sys.argv[1]; d, L, h = (int(a) for a in sys.argv[2:5])
tk = Tokenizer.from_file("tok1024.json"); END = tk.token_to_id("<|endoftext|>")
m = GPT(d, L, h, 1024); m.load_state_dict(torch.load(P + ".pt", weights_only=True)); m.eval()

def generate(seed):
    g = torch.Generator().manual_seed(seed); x = tk.encode("Once upon a time").ids
    with torch.no_grad():
        for _ in range(330):
            nxt = int(torch.multinomial((m(torch.tensor([x[-256:]]))[0, -1] / 0.8).softmax(-1), 1, generator=g))
            x.append(nxt)
            if nxt == END: break
    return tk.decode(x).encode("utf-8") + (b"<|endoftext|>" if x[-1] == END else b"")

texts = [generate(5000 + i) for i in range(G.N)]
r = G.checks(texts)
r["valid_stories_reference"] = G.checks(open("data/v2_valid.txt", "rb").read().split(G.END)[:G.N])
print(json.dumps(r))
open(P + ".samples.txt", "wb").write(b"\n\n=====\n\n".join(texts)); json.dump(r, open(P + ".gen.json", "w"), indent=1)
