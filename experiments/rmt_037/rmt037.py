"""RMT-037: spacing-ratio statistics of GPT-2 QK circuits against matched random arms (REGISTRATION.md).

Usage:  python3 experiments/rmt_037/rmt037.py --small PATH/model.safetensors --medium PATH/model.safetensors
        [--expect-digest D]
Weights: openai-community/gpt2 and gpt2-medium safetensors from Hugging Face (SHA-256 printed).
Exit: 0 ran and every control held; 1 a control failed or the digest differs; 2 could not load.
Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-14. SELF-TESTED only.
"""
import argparse
import hashlib
import json
import sys

import numpy as np
from scipy import stats

SEED = 20261114
R_GOE, R_POI = 0.5307, 2 * np.log(2) - 1


# ---------------------------------------------------------------- statistic
def ratios(levels):
    """Consecutive spacing ratios min/max over sorted levels; zero-gap pairs dropped (counted)."""
    lv = np.sort(np.asarray(levels, float))
    s = np.diff(lv)
    a, b = s[:-1], s[1:]
    mx = np.maximum(a, b)
    ok = mx > 0
    return np.minimum(a, b)[ok] / mx[ok], int((~ok).sum())


def regions(levels):
    lv = np.sort(np.asarray(levels, float))
    n = len(lv)
    return {"bulk": lv[int(0.1 * n):int(0.9 * n)], "edge": lv[int(0.9 * n):]}


# ---------------------------------------------------------------- objects
def qk_levels(wq, wk):
    """Non-zero singular values of wq @ wk.T, via thin QR (exact in exact arithmetic)."""
    _, rq = np.linalg.qr(wq)
    _, rk = np.linalg.qr(wk)
    return np.linalg.svd(rq @ rk.T, compute_uv=False)


def sym_levels(wq, wk):
    """Non-zero eigenvalues of (wq wk^T + wk wq^T)/2, computed in the span of [wq wk]."""
    a = np.hstack([wq, wk])
    _, r = np.linalg.qr(a)
    d = wq.shape[1]
    j = np.zeros((2 * d, 2 * d))
    j[:d, d:] = j[d:, :d] = 0.5 * np.eye(d)
    m = r @ j @ r.T
    return np.linalg.eigvalsh((m + m.T) / 2)


def heads_from(c_attn, n_head):
    d_model = c_attn.shape[0]
    dh = d_model // n_head
    for h in range(n_head):
        yield h, c_attn[:, h * dh:(h + 1) * dh], c_attn[:, d_model + h * dh:d_model + (h + 1) * dh]


def load(path, n_layer):
    from safetensors.numpy import load_file
    w = load_file(path)
    out = []
    for layer in range(n_layer):
        key = next(k for k in (f"h.{layer}.attn.c_attn.weight", f"transformer.h.{layer}.attn.c_attn.weight") if k in w)
        out.append(np.asarray(w[key], np.float64))
    return out


# ---------------------------------------------------------------- arms
def collect(layers, n_head, arm, rng):
    """Per layer, per head: QK and SYM levels for the trained (or transformed) weights."""
    res = []
    for layer, c in enumerate(layers):
        if arm == "INIT":
            c = rng.normal(0.0, 0.02, size=c.shape)
        for h, wq, wk in heads_from(c, n_head):
            if arm == "SHUF":
                wq = rng.permutation(wq.ravel()).reshape(wq.shape)
                wk = rng.permutation(wk.ravel()).reshape(wk.shape)
            res.append((layer, h, qk_levels(wq, wk), sym_levels(wq, wk)))
    return res


def pooled(rows, obj, region, layer=None):
    rs, zero = [], 0
    for lay, _, qk, sym in rows:
        if layer is not None and lay != layer:
            continue
        r, z = ratios(regions(qk if obj == "QK" else sym)[region])
        rs.append(r)
        zero += z
    r = np.concatenate(rs)
    return float(r.mean()), float(r.std(ddof=1) / np.sqrt(len(r))), len(r), zero


def goe_levels(n, rng):
    a = rng.standard_normal((n, n))
    return np.linalg.eigvalsh((a + a.T) / np.sqrt(2 * n))


def ref_pool(kind, n, region, rng, reps=1000):
    rs = []
    for _ in range(reps):
        lv = goe_levels(n, rng) if kind == "GOE" else rng.uniform(size=n)
        rs.append(ratios(regions(lv)[region])[0])
    r = np.concatenate(rs)
    return float(r.mean()), float(r.std(ddof=1) / np.sqrt(len(r))), len(r)


def note037_pipeline_rejects(n, rng, reps=1000, deg=5):
    """note037's reference pipeline applied to true GOE spectra: fraction with KS p < 0.05 vs a Wigner sample."""
    rej = 0
    for _ in range(reps):
        ev = np.sort(goe_levels(n, rng))
        coeffs = np.polyfit(ev, np.arange(1, n + 1), deg)
        sp = np.diff(np.poly1d(coeffs)(ev))
        sp = sp[(sp > 0) & (sp < 5)]
        ref = rng.rayleigh(scale=np.sqrt(2 / np.pi), size=len(sp))
        rej += stats.ks_2samp(sp, ref).pvalue < 0.05
    return rej / reps


def summary(rows, obj):
    lv = np.concatenate([qk if obj == "QK" else sym for _, _, qk, sym in rows])
    return f"min {lv.min():.4g} median {np.median(lv):.4g} max {lv.max():.4g} (n={len(lv)})"


# ---------------------------------------------------------------- main
def run_model(name, path, n_layer, n_head, out, lines):
    layers = load(path, n_layer)
    again = load(path, n_layer)
    same = all(np.array_equal(a, b) for a, b in zip(layers, again))
    rng = np.random.default_rng(SEED)
    arms = {"TRAINED": collect(layers, n_head, "TRAINED", rng),
            "INIT": collect(layers, n_head, "INIT", np.random.default_rng(SEED)),
            "SHUF": collect(layers, n_head, "SHUF", np.random.default_rng(SEED))}
    lines.append(f"\n== {name}: {n_layer} layers x {n_head} heads; weights read twice identical: {same}")
    for arm, rows in arms.items():
        lines.append(f"  {arm:7} QK levels {summary(rows, 'QK')} | SYM levels {summary(rows, 'SYM')}")
    for obj in ("QK", "SYM"):
        for region in ("bulk", "edge"):
            for arm, rows in arms.items():
                m, se, k, z = pooled(rows, obj, region)
                out[f"{name}/{obj}/{region}/{arm}"] = [round(m, 6), round(se, 6), k, z]
                lines.append(f"  {obj:3} {region:4} {arm:7} <r> = {m:.4f} +- {se:.4f}  (ratios {k}, zero gaps {z})")
    for layer in range(n_layer):
        m, se, k, _ = pooled(arms["TRAINED"], "QK", "bulk", layer)
        mi, _, _, _ = pooled(arms["INIT"], "QK", "bulk", layer)
        out[f"{name}/QK/bulk/layer{layer}"] = [round(m, 6), round(se, 6), k, round(mi, 6)]
        lines.append(f"  layer {layer:2} QK bulk TRAINED {m:.4f} +- {se:.4f} (n {k}) | INIT {mi:.4f}")
    return same


def main(argv=None):
    ap = argparse.ArgumentParser(description="RMT-037")
    ap.add_argument("--small", required=True)
    ap.add_argument("--medium", required=True)
    ap.add_argument("--expect-digest")
    a = ap.parse_args(argv)
    lines = [f"RMT-037 | python {sys.version.split()[0]} numpy {np.__version__} scipy {stats.__name__ and __import__('scipy').__version__}"]
    for label, p in (("small", a.small), ("medium", a.medium)):
        with open(p, "rb") as fh:
            lines.append(f"{label} weights sha256 {hashlib.sha256(fh.read()).hexdigest()}")
    out = {}
    rng = np.random.default_rng(SEED + 1)
    # controls on the statistic and the object code, before any model number is printed
    c1 = ref_pool("POIS", 64, "bulk", rng)
    c2 = ref_pool("GOE", 64, "bulk", rng)
    g128 = ref_pool("GOE", 128, "bulk", rng)
    ge64 = ref_pool("GOE", 64, "edge", rng)
    w = np.random.default_rng(SEED + 2).normal(size=(768, 64))
    direct = np.sort(np.linalg.svd(w @ w.T, compute_uv=False))[::-1][:64]
    viaqr = np.sort(qk_levels(w, w))[::-1]
    c3 = float(np.max(np.abs(direct - viaqr) / direct))
    controls = {"C1 POIS(64) bulk <r> within 0.02 of 0.3863": abs(c1[0] - R_POI) <= 0.02,
                "C2 GOE(64) bulk <r> within 0.02 of 0.5307": abs(c2[0] - R_GOE) <= 0.02,
                "C3 QK via QR equals full SVD to 1e-8 relative": c3 <= 1e-8}
    lines.append(f"references: POIS(64) bulk {c1[0]:.4f} +- {c1[1]:.4f}; GOE(64) bulk {c2[0]:.4f} +- {c2[1]:.4f}; "
                 f"GOE(128) bulk {g128[0]:.4f}; GOE(64) edge {ge64[0]:.4f}; C3 max rel diff {c3:.3e}")
    out["refs"] = [round(c1[0], 6), round(c2[0], 6), round(g128[0], 6), round(ge64[0], 6)]
    r5 = note037_pipeline_rejects(64, np.random.default_rng(SEED + 3))
    out["R5"] = r5
    lines.append(f"note037 pipeline on true GOE(64): rejects {r5:.3f} of 1000 at p < 0.05")
    same_s = run_model("small", a.small, 12, 12, out, lines)
    same_m = run_model("medium", a.medium, 24, 16, out, lines)
    controls["C4 weights read twice are identical"] = same_s and same_m

    g = lambda k: out[k][0]
    preds = {
        "R1 small QK bulk |TRAINED - INIT| <= 0.02": abs(g("small/QK/bulk/TRAINED") - g("small/QK/bulk/INIT")) <= 0.02,
        "R2 small QK bulk TRAINED >= 0.50": g("small/QK/bulk/TRAINED") >= 0.50,
        "R3 small: no layer's QK bulk < 0.45": all(out[f"small/QK/bulk/layer{i}"][0] >= 0.45 for i in range(12)),
        "R4 small QK edge |TRAINED - INIT| > 0.05": abs(g("small/QK/edge/TRAINED") - g("small/QK/edge/INIT")) > 0.05,
        "R5 note037 pipeline rejects > 10% of true GOE(64)": r5 > 0.10,
        "R6 medium: R1 and R2 hold": abs(g("medium/QK/bulk/TRAINED") - g("medium/QK/bulk/INIT")) <= 0.02
                                     and g("medium/QK/bulk/TRAINED") >= 0.50,
    }
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
