"""TLM-006 generation (T5): gencheck_tok.py's procedure (prompt "Once upon a time", temperature 0.8, at most 330
tokens, stop at <|endoftext|>, which is appended to the text) for a range of generation seeds.

usage: python3 tlm006_gen.py RUN_PREFIX FIRST_SEED COUNT OUT [--confirmatory]
  Seeds 5000..5019 (TLM-004's, already seen) are allowed for gate G2. Seeds >= 5020 are the frozen held-out samples
  (REGISTRATION_TLM006.md at 834ff9b) and are refused unless --confirmatory is given, which needs Chad Holland's go
  on PR #185. Texts are joined with \\n\\n=====\\n\\n as in TLM-004.
Claude (Anthropic, Opus 5.5), 2026-11-26. SELF-TESTED only.
"""
import hashlib
import sys

import torch
from tokenizers import Tokenizer

from gpt import GPT

P, first, count, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
if first + count > 5020 and "--confirmatory" not in sys.argv:
    sys.exit("refused: seeds >= 5020 are the held-out confirmatory samples (needs --confirmatory and Chad's go)")
tk = Tokenizer.from_file("tok1024.json")
END = tk.token_to_id("<|endoftext|>")
m = GPT(120, 5, 4, 1024)
m.load_state_dict(torch.load(P + ".pt", weights_only=True))
m.eval()


def generate(seed):
    g = torch.Generator().manual_seed(seed)
    x = tk.encode("Once upon a time").ids
    with torch.no_grad():
        for _ in range(330):
            nxt = int(torch.multinomial((m(torch.tensor([x[-256:]]))[0, -1] / 0.8).softmax(-1), 1, generator=g))
            x.append(nxt)
            if nxt == END:
                break
    return tk.decode(x).encode("utf-8") + (b"<|endoftext|>" if x[-1] == END else b"")


texts = [generate(s) for s in range(first, first + count)]
blob = b"\n\n=====\n\n".join(texts)
open(out, "wb").write(blob)
print(f"weights {P}.pt sha256 {hashlib.sha256(open(P + '.pt', 'rb').read()).hexdigest()}")
print(f"seeds {first}..{first + count - 1} texts {len(texts)} -> {out} sha256 {hashlib.sha256(blob).hexdigest()}")
