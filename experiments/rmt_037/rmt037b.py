"""RMT-037b: the edge test on OPT-125m and OPT-350m (REGISTRATION_B.md). Reuses rmt037.py's statistic, objects and
arms unchanged; only the weight loader is new.

Usage: python3 experiments/rmt_037/rmt037b.py --opt125 PATH/pytorch_model.bin --opt350 PATH/pytorch_model.bin
       [--expect-digest D]
Exit: 0 ran and every control held; 1 a control failed or the digest differs.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-16. SELF-TESTED only.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmt037 as r  # noqa: E402


def load_opt(path, n_layer):
    """Per layer, a (d_model, 2*d_model) matrix [W_Q | W_K] in rmt037's x @ W convention (nn.Linear weight transposed)."""
    import torch
    sd = torch.load(path, map_location="cpu", weights_only=True)
    out = []
    for layer in range(n_layer):
        pre = next(p for p in (f"model.decoder.layers.{layer}.self_attn.", f"decoder.layers.{layer}.self_attn.")
                   if p + "q_proj.weight" in sd)
        wq = sd[pre + "q_proj.weight"].to(torch.float64).numpy().T
        wk = sd[pre + "k_proj.weight"].to(torch.float64).numpy().T
        out.append(np.hstack([wq, wk]))
    return out


def run_model(name, path, n_layer, n_head, out, lines):
    layers = load_opt(path, n_layer)
    again = load_opt(path, n_layer)
    same = all(np.array_equal(a, b) for a, b in zip(layers, again))
    arms = {"TRAINED": r.collect(layers, n_head, "TRAINED", np.random.default_rng(r.SEED)),
            "INIT": r.collect(layers, n_head, "INIT", np.random.default_rng(r.SEED)),
            "SHUF": r.collect(layers, n_head, "SHUF", np.random.default_rng(r.SEED))}
    lines.append(f"\n== {name}: {n_layer} layers x {n_head} heads, d_model {layers[0].shape[0]}; "
                 f"weights read twice identical: {same}")
    for arm, rows in arms.items():
        lines.append(f"  {arm:7} QK levels {r.summary(rows, 'QK')}")
    for region in ("bulk", "edge"):
        for arm, rows in arms.items():
            m, se, k, z = r.pooled(rows, "QK", region)
            out[f"{name}/QK/{region}/{arm}"] = [round(m, 6), round(se, 6), k, z]
            lines.append(f"  QK {region:4} {arm:7} <r> = {m:.4f} +- {se:.4f}  (ratios {k}, zero gaps {z})")
    return same


def main(argv=None):
    ap = argparse.ArgumentParser(description="RMT-037b")
    ap.add_argument("--opt125", required=True)
    ap.add_argument("--opt350", required=True)
    ap.add_argument("--expect-digest")
    a = ap.parse_args(argv)
    lines = [f"RMT-037b | python {sys.version.split()[0]} numpy {np.__version__}"]
    for label, p in (("opt-125m", a.opt125), ("opt-350m", a.opt350)):
        with open(p, "rb") as fh:
            lines.append(f"{label} weights sha256 {hashlib.sha256(fh.read()).hexdigest()}")
    rng = np.random.default_rng(r.SEED + 1)
    c1 = r.ref_pool("POIS", 64, "bulk", rng)
    c2 = r.ref_pool("GOE", 64, "bulk", rng)
    w = np.random.default_rng(r.SEED + 2).normal(size=(768, 64))
    direct = np.sort(np.linalg.svd(w @ w.T, compute_uv=False))[::-1][:64]
    c3 = float(np.max(np.abs(direct - np.sort(r.qk_levels(w, w))[::-1]) / direct))
    controls = {"C1 POIS(64) bulk within 0.02 of 0.3863": abs(c1[0] - r.R_POI) <= 0.02,
                "C2 GOE(64) bulk within 0.02 of 0.5307": abs(c2[0] - r.R_GOE) <= 0.02,
                "C3 QK via QR equals full SVD to 1e-8 relative": c3 <= 1e-8}
    lines.append(f"references: POIS(64) bulk {c1[0]:.4f}; GOE(64) bulk {c2[0]:.4f}; C3 max rel diff {c3:.3e}")
    out = {"refs": [round(c1[0], 6), round(c2[0], 6)]}
    s1 = run_model("opt-125m", a.opt125, 12, 12, out, lines)
    s2 = run_model("opt-350m", a.opt350, 24, 16, out, lines)
    controls["C4 weights read twice identical"] = s1 and s2
    g = lambda k: out[k][0]
    preds = {}
    for i, m in (("E1", "opt-125m"), ("E2", "opt-350m")):
        d = g(f"{m}/QK/edge/INIT") - g(f"{m}/QK/edge/TRAINED")
        preds[f"{i} {m} edge INIT - TRAINED = {d:+.4f} >= 0.02"] = d >= 0.02
    b = [abs(g(f"{m}/QK/bulk/TRAINED") - g(f"{m}/QK/bulk/INIT")) for m in ("opt-125m", "opt-350m")]
    preds[f"E3 bulk |TRAINED - INIT| = {b[0]:.4f}, {b[1]:.4f} both <= 0.02"] = all(x <= 0.02 for x in b)
    s = [g(f"{m}/QK/edge/SHUF") - g(f"{m}/QK/edge/TRAINED") for m in ("opt-125m", "opt-350m")]
    preds[f"E4 edge SHUF - TRAINED = {s[0]:+.4f}, {s[1]:+.4f} both >= 0.02"] = all(x >= 0.02 for x in s)
    lines.append("")
    for k, v in preds.items():
        lines.append(f"{'HELD   ' if v else 'REFUTED'} {k}")
    lines.append("")
    rc = 0
    for k, v in controls.items():
        lines.append(f"{'HELD  ' if v else 'FAILED'} {k}")
        rc |= 0 if v else 1
    dg = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()
    lines.append(f"DIGEST {dg}")
    if a.expect_digest and a.expect_digest != dg:
        lines.append(f"DIGEST MISMATCH (expected {a.expect_digest})")
        rc = 1
    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main())
