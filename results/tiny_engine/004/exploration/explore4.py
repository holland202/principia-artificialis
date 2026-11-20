"""TINY-ENGINE-004 exploration (not registered). Usage: python3 -I explore4.py ENGINE_DIR ARM SEED OUT.json
Claude (Anthropic, Opus 5.5), 2026-11-20. SELF-TESTED only."""
import json, sys, time
sys.path.insert(0, sys.argv[1])
import torch
import engine as E, eval3
torch.set_num_threads(1)
ARM, SEED, OUT = sys.argv[2], int(sys.argv[3]), sys.argv[4]
cfg = {"A": E.CFG3, "B": E.CFG4B, "C": E.CFG4C}[ARM]
# fresh case seeds for exploration: shift eval3's fixed seeds by 20000
_tf, _fr = eval3.tf_acc, eval3.free_whole
eval3.tf_acc = lambda m, f, k, s, n=eval3.N_TF: _tf(m, f, k, s + 20000, n)
eval3.free_whole = lambda m, f, k, s, n=eval3.N_FREE: _fr(m, f, k, s + 20000, n)
t = time.time()
m = E.train(SEED, cfg)
r = dict(E.evaluate(m), **eval3.evaluate3(m))
json.dump({"arm": ARM, "seed": SEED, "train_s": round(time.time() - t), "params": E.n_params(m), "scores": r},
          open(OUT, "w"), indent=1)
print(ARM, json.dumps({k: round(v, 4) for k, v in r.items()}), flush=True)
