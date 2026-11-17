"""EXPLORATION (C-EXPLORE): seed 900 only, to check the engine trains at all and how long it takes. Not confirmatory."""
import json, sys, time
import engine as E
t = time.time()
m = E.train(900, dict(E.CFG, steps=int(sys.argv[1])), log=lambda s, l: print(f"  step {s} loss {l:.3f}", flush=True))
print(f"train {time.time()-t:.0f}s", json.dumps({k: round(v, 3) for k, v in E.evaluate(m).items()}), flush=True)
