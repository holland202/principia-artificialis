#!/usr/bin/env python3
"""Figure for note052 P10, drawn only from the committed P10 records (no re-run, no new numbers).

  python3 scripts/generate_note052_p10_figure.py      -> figures/note052_p10_ci_vs_checks.png

Left: share of repositories with at least one hand-checked TP (a check that cannot fail), with Wilson 95%
intervals, by CI at the 2022 pin (primary definition). Right: verification-shaped files per repository.
Prints every number it draws, so the figure can be checked against note052. Requires matplotlib.
"""
import json, math, os, random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P10 = os.path.join(ROOT, "experiments", "note052_p6", "results_p10")
OUT = os.path.join(ROOT, "figures", "note052_p10_ci_vs_checks.png")
Z = 1.959963984540054


def wilson(k, n):
    p = k / n
    c = (p + Z * Z / (2 * n)) / (1 + Z * Z / n)
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / (1 + Z * Z / n)
    return c - h, c + h


def main():
    scan = json.load(open(os.path.join(P10, "scan.json")))
    strata = json.load(open(os.path.join(P10, "strata.json")))
    key = json.load(open(os.path.join(P10, "blind_key.json")))["key"]
    sheet = {s["id"]: s["verdict"] for s in json.load(open(os.path.join(P10, "handcheck.json")))}
    tp = {r: 0 for r in scan}
    for g, k in key.items():
        tp[k["repo"]] += sheet[g] == "TP"
    # In P10's records stratum "B" is no CI and "A" is CI (run_p10.score: P10a predicted share_B > share_A).
    groups = {"no CI": [r for r in scan if strata[r]["primary"] == "B" and scan[r]["verification_shaped"] is not None],
              "CI": [r for r in scan if strata[r]["primary"] == "A" and scan[r]["verification_shaped"] is not None]}
    plt.rcParams.update({"figure.facecolor": "#0d1117", "axes.facecolor": "#161b22", "text.color": "#c9d1d9",
                         "axes.labelcolor": "#c9d1d9", "xtick.color": "#8b949e", "ytick.color": "#8b949e",
                         "axes.edgecolor": "#30363d", "font.size": 11})
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [1, 1.3]})
    colors = {"no CI": "#d29922", "CI": "#58a6ff"}
    for x, (g, rs) in enumerate(groups.items()):
        k, n = sum(tp[r] > 0 for r in rs), len(rs)
        lo, hi = wilson(k, n)
        a.errorbar([x], [k / n], yerr=[[k / n - lo], [hi - k / n]], fmt="o", color=colors[g], ms=9, capsize=8, lw=2)
        a.annotate(f"{k}/{n} = {k / n:.1%}\n95% [{lo:.1%}, {hi:.1%}]", (x, hi), textcoords="offset points",
                   xytext=(0, 8), ha="center", fontsize=10)
        print(f"{g}: {k}/{n} repositories with a TP = {k / n:.4f}; Wilson 95% [{lo:.4f}, {hi:.4f}]")
    a.set_xticks([0, 1], list(groups))
    a.set_xlim(-0.6, 1.6)
    a.set_ylim(0, 0.45)
    a.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a.set_ylabel("repositories with a check that cannot fail")
    a.set_title("P10a refuted: the same rate with or without CI", color="#f85149", fontsize=12)
    rng = random.Random(52)
    for x, (g, rs) in enumerate(groups.items()):
        vals = sorted(scan[r]["verification_shaped"] for r in rs)
        xs = [x + rng.uniform(-0.18, 0.18) for _ in vals]
        b.scatter(xs, [v + 1 for v in vals], s=22, color=colors[g], alpha=0.75, edgecolors="none")
        m = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
        b.hlines(m + 1, x - 0.3, x + 0.3, color="#c9d1d9", lw=2)
        b.annotate(f"median {m:g}", (x + 0.32, m + 1), va="center", fontsize=10)
        zero = sum(v == 0 for v in vals)
        print(f"{g}: n={len(vals)}, median verification-shaped files {m:g}, zero in {zero} ({zero / len(vals):.1%})")
    b.set_yscale("log")
    b.set_xticks([0, 1], list(groups))
    b.set_xlim(-0.6, 1.9)
    b.set_ylabel("verification-shaped files per repository + 1 (log)")
    b.set_title("P10b: fewer checks without CI (confirmed)", color="#3fb950", fontsize=12)
    fig.suptitle("note052 P10 — 80 small Python repositories at their last commit before 2022-12-01",
                 fontsize=13, color="#c9d1d9")
    fig.text(0.5, 0.01, "CI = primary definition at the pin. TPs hand-checked by Claude (one AI), blind to stratum. "
             "Data: experiments/note052_p6/results_p10/", ha="center", fontsize=9, color="#8b949e")
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig(OUT, dpi=150)
    print(f"wrote {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
