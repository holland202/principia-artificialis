"""CCC-001 QUAL2 feasibility counts (QUAL2_PREREG.md). Pure Python, reads committed stage Q and LONGCTX REF files.

Prints, per model: arm-D mean G, items with G(D) >= 0.9, the headroom 1 - mean G(D), and, on the 16 items whose key
is not C, the arm-D and arm-E mean p(not-enough letter), the room the override arm O can move.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from accbias import ITEM_MEANING, PI, RES  # noqa: E402
from probes import OPTIONS  # noqa: E402

FILES = {"1.5B": ("qualify.json", "longctx_ref.json"),
         "7B": ("gpu7b/qualify_7b.json", "gpu7b/longctx_REF_7b.json")}
NE = [i for i, m in enumerate(ITEM_MEANING) if m != "notenough"]
print(f"items whose key is not not-enough: {len(NE)}; not-enough items: {24 - len(NE)}")
for name, (qf, lf) in FILES.items():
    a = json.load(open(os.path.join(RES, qf)))["arms"]
    gD = [r["G"] for r in a["D"]]
    jC = OPTIONS.index(PI[0]["notenough"])
    pcD = sum(a["D"][i]["p"][jC] for i in NE) / len(NE)
    pcE = sum(a["E"][i]["p"][jC] for i in NE) / len(NE)
    print(f"{name} stage Q: mean G(D) {sum(gD) / 24:.4f}; items G(D) >= 0.9: {sum(g >= 0.9 for g in gD)} of 24; "
          f"headroom 1 - mean G(D) {1 - sum(gD) / 24:.4f}; on the 16 non-C items mean p(C) D {pcD:.4f} E {pcE:.4f}")
    c = json.load(open(os.path.join(RES, lf)))["cells"]
    dm = [sum(r["G"] for r in c[f"D{k}"]) / 24 for k in (0, 1, 2)]
    print(f"{name} LONGCTX REF: mean G(D) per pi [{', '.join(f'{x:.4f}' for x in dm)}]; "
          f"headroom 1 - mean over pi {1 - sum(dm) / 3:.4f}")
