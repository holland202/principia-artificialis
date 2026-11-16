"""Follow-up, written after plumbing.py's run (not part of its registered checks): P3 did not exercise reasoning
(the model replied in 11 characters). Force two sentences of reasoning, then read log-odds at the model's own
DECISION. Toy prompts only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import plumbing as P  # noqa: E402

A, B = P.tok(" A")[0], P.tok(" B")[0]
ok = True
for q, truth in P.TOYS:
    prompt = P.chat_prefix("Explain your reasoning in two sentences first. " + P.question(q, "B"))
    out = P.llm.create_completion(prompt, max_tokens=200, temperature=0.0, top_k=1, seed=0)["choices"][0]["text"]
    i = out.rfind("DECISION:")
    if i < 0:
        print(f"{q:28} NO DECISION LINE: {out[-100:]!r}")
        ok = False
        continue
    written = out[i + len("DECISION:"):].strip()[:1]
    lo = P.logodds(prompt + out[:i + len("DECISION:")], A, B)[0]
    print(f"{q:28} reply {len(out):3d} chars, wrote {written!r}, logodds {lo:+.3f}, "
          f"consistent={(lo > 0) == (written == 'A')}, model_correct={(written == 'B') == truth}")
    ok &= (lo > 0) == (written == "A")
print("LONG-FORMAT READOUT", "CONSISTENT" if ok else "INCONSISTENT")
