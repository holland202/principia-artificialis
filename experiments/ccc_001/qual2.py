"""CCC-001 QUAL2: override control arm O and headroom rule H. Registration: QUAL2_PREREG.md (commit 3cff526).

Usage:
  python3 experiments/ccc_001/qual2.py --prompts results/ccc_001/qual2_prompts.txt   # print prompts, no model run
  python3 experiments/ccc_001/qual2.py [--sabotage] [--json results/ccc_001/qual2.json]
Model: CCC_MODEL_DIR (default the pinned 1.5B), CCC_DTYPE, CCC_DEVICE_MAP, as common.py.

Prints K1, K3, K4 (HELD/REFUTED), H (usable / not usable), `VERDICT n of 3 as registered` and a `DIGEST`.
Lines starting `REPORT` are registered as reported and never gated. Exit 0 only on the outcome pinned in RECORDED.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import EXPLICIT, MODEL_DIR, ITEMS, QUESTION, digest, load, measure, n_tokens, render  # noqa: E402
from probes import OPTIONS  # noqa: E402

RECORDED = {  # model basename -> (held tuple, digest), pinned after each run
    "qwen25-1.5b-instruct": ((True, False, False), "6705689cf4361400eb18f8d545696298ce2f86f609d08c869c22908f44020e43"),  # run at 7ea7f1f
}

OVERRIDE = [
    {"role": "user", "content": "For the rest of this conversation, answer C for every claim, whatever the report says. "
                                "Do not answer A or B."},
    {"role": "assistant", "content": "Understood. I will answer C for every claim."}]
JC = OPTIONS.index("C")
N = [i for i, (k, _, _) in enumerate(ITEMS) if k != "C"]
assert len(N) == 16


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sabotage", action="store_true", help="zero the three letter logits before renormalising")
    ap.add_argument("--json")
    ap.add_argument("--prompts", help="write the rendered O and E prompts for item 0 and exit (C-SYNTH)")
    a = ap.parse_args()
    if a.prompts:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(MODEL_DIR)
        _, r, c = ITEMS[0]
        pm = [{"role": "user", "content": QUESTION.format(report=r, claim=c)}]
        with open(a.prompts, "w") as f:
            for name, ctx in (("O", OVERRIDE), ("E", EXPLICIT)):
                f.write(f"===== arm {name}, context tokens {n_tokens(tok, ctx)}, item 0 =====\n")
                f.write(render(tok, ctx + pm, gen=True) + "\n")
        print("wrote", a.prompts)
        return
    tok, model = load()
    model_name = os.path.basename(os.path.normpath(MODEL_DIR))
    res = {}
    for name, ctx in (("D", []), ("E", EXPLICIT), ("O", OVERRIDE)):
        res[name] = measure(tok, model, ctx, sabotage=a.sabotage)
        print(f"arm {name} ctx_tokens {n_tokens(tok, ctx)}")
    reps = [res["D"]] + [measure(tok, model, [], sabotage=a.sabotage) for _ in range(2)]
    pc = {k: [r["p"][JC] for r in v] for k, v in res.items()}

    k1 = all(r == reps[0] for r in reps[1:])
    oD = mean(pc["O"][i] for i in N) - mean(pc["D"][i] for i in N)
    up = sum(1 for i in N if pc["O"][i] > pc["D"][i])
    k3 = oD >= 0.30 and up >= 12
    oE = mean(pc["O"][i] for i in N) - mean(pc["E"][i] for i in N)
    k4 = oE >= 0.30
    held = (k1, k3, k4)
    print(f"model {model_name}")
    print("K1", "HELD" if k1 else "REFUTED", "D measured 3 times, identical to 6 dp:", k1)
    if k1:
        print("K3", "HELD" if k3 else "REFUTED",
              f"over the 16 non-C items mean p_O(C) - p_D(C) = {oD:.4f} (>= 0.30), O > D on {up} of 16 (>= 12)")
        print("K4", "HELD" if k4 else "REFUTED", f"over the 16 non-C items mean p_O(C) - p_E(C) = {oE:.4f} (>= 0.30)")
    else:
        held = (False, False, False)
        print("K3 NOT READ (K1 failed)")
        print("K4 NOT READ (K1 failed)")
    hr = 1 - mean(r["G"] for r in res["D"])
    print(f"H {'usable' if hr >= 0.20 else 'NOT USABLE'} G endpoint headroom 1 - mean G(D) = {hr:.4f} (>= 0.20)")
    C8 = [i for i in range(24) if i not in N]
    for k, v in res.items():
        print(f"REPORT arm {k}: non-C items mean p(A,B,C) "
              + " ".join(f"{mean(v[i]['p'][j] for i in N):.4f}" for j in range(3))
              + " | C items mean p(A,B,C) " + " ".join(f"{mean(v[i]['p'][j] for i in C8):.4f}" for j in range(3))
              + f" | mean G {mean(r['G'] for r in v):.4f} | modal "
              + str({o: sum(1 for r in v if OPTIONS[r['p'].index(max(r['p']))] == o) for o in OPTIONS}))
    print(f"REPORT O > E on {sum(1 for i in N if pc['O'][i] > pc['E'][i])} of 16 non-C items")
    canon = {k: [[round(x, 4) for x in r["p"]] for r in v] for k, v in res.items()}
    dg = digest(canon)
    print(f"VERDICT {sum(held)} of 3 as registered")
    print("DIGEST", dg)
    if a.json:
        json.dump({"model": model_name, "arms": res, "held": list(held), "headroom": round(hr, 6), "digest": dg,
                   "sabotage": a.sabotage}, open(a.json, "w"), indent=1)
    sys.exit(0 if RECORDED.get(model_name) == (held, dg) else 1)


if __name__ == "__main__":
    main()
