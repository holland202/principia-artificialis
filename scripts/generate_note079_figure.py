#!/usr/bin/env python3
"""Figure for note079, drawn from the authors' published counts with note079's own reference functions.

  python3 scripts/generate_note079_figure.py      -> figures/note079_sim_real_intervals.png

Left: Wilson 95% intervals for ToyBlocks' Molmo 2 + ManiFlow success, 111/200 in simulation and 15/30 on the real
robot. Right: power to detect the observed 5.5-point gap as real episodes grow, with the simulation arm fixed at 200,
against equal arms. Prints every number it draws. Requires matplotlib.
"""
import os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import note079_reference as ref  # noqa: E402

OUT = os.path.join(ROOT, "figures", "note079_sim_real_intervals.png")


def main():
    plt.rcParams.update({"figure.facecolor": "#0d1117", "axes.facecolor": "#161b22", "text.color": "#c9d1d9",
                         "axes.labelcolor": "#c9d1d9", "xtick.color": "#8b949e", "ytick.color": "#8b949e",
                         "axes.edgecolor": "#30363d", "font.size": 11})
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 5.2))
    p1, p2 = ref.SIM[0] / ref.SIM[1], ref.REAL[0] / ref.REAL[1]
    for x, (label, (k, n), c) in enumerate((("simulation", ref.SIM, "#a371f7"), ("real robot", ref.REAL, "#3fb950"))):
        lo, hi = ref.wilson(k, n)
        a.errorbar([x], [k / n], yerr=[[k / n - lo], [hi - k / n]], fmt="o", color=c, ms=9, capsize=8, lw=2)
        a.annotate(f"{k}/{n} = {k / n:.1%}\n95% [{lo:.1%}, {hi:.1%}]", (x, hi), textcoords="offset points",
                   xytext=(0, 8), ha="center", fontsize=10)
        print(f"{label}: {k}/{n} = {k / n:.4f}; Wilson 95% [{lo:.4f}, {hi:.4f}]")
    a.set_xticks([0, 1], ["simulation\n(200 episodes)", "real robot\n(30 episodes)"])
    a.set_xlim(-0.6, 1.6)
    a.set_ylim(0.2, 0.85)
    a.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a.set_ylabel("task success")
    a.set_title(f"Fisher exact p = {float(ref.fisher_two_sided(*ref.SIM, *ref.REAL)):.4f}: the gap is not resolved",
                fontsize=12)
    ns = [10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000, 10000]
    fixed = [ref.power(p1, ref.SIM[1], p2, n) for n in ns]
    equal = [ref.power(p1, n, p2, n) for n in ns]
    b.plot(ns, fixed, "o-", color="#d29922", ms=4, label="simulation fixed at 200")
    b.plot(ns, equal, "o-", color="#58a6ff", ms=4, label="equal episodes in both arms")
    cap = ref.PHI(abs(p1 - p2) / (p1 * (1 - p1) / ref.SIM[1]) ** 0.5 - ref.Z_A)
    b.axhline(cap, color="#d29922", ls=":", lw=1)
    b.axhline(0.8, color="#8b949e", ls="--", lw=1)
    b.annotate(f"ceiling {cap:.3f} with simulation at 200", (ns[0], cap), xytext=(0, 6), textcoords="offset points",
               fontsize=9, color="#d29922")
    b.annotate("80% power", (ns[0], 0.8), xytext=(0, 6), textcoords="offset points", fontsize=9, color="#8b949e")
    n80 = ref.equal_n(p1, p2)
    b.axvline(n80, color="#58a6ff", ls=":", lw=1)
    b.annotate(f"{n80} per arm", (n80, 0.05), xytext=(6, 0), textcoords="offset points", fontsize=9, color="#58a6ff")
    b.scatter([30], [ref.power(p1, 200, p2, 30)], s=80, facecolors="none", edgecolors="#f85149", lw=2, zorder=5)
    b.annotate(f"published design: {ref.power(p1, 200, p2, 30):.3f}", (30, ref.power(p1, 200, p2, 30)),
               xytext=(8, -14), textcoords="offset points", fontsize=9, color="#f85149")
    b.set_xscale("log")
    b.set_ylim(0, 1)
    b.set_xlabel("real-robot episodes (log)")
    b.set_ylabel("power to detect 55.5% vs 50.0% (α = 0.05)")
    b.set_title("More real episodes alone cannot settle it", fontsize=12)
    b.legend(loc="center right", fontsize=9, facecolor="#161b22", edgecolor="#30363d")
    print(f"power at the published design {ref.power(p1, 200, p2, 30):.4f}; ceiling {cap:.4f}; equal arms need {n80}")
    fig.suptitle("note079 — ToyBlocks (Ai2): what 30 real episodes can show", fontsize=13, color="#c9d1d9")
    fig.text(0.5, 0.01, "Counts are the authors' (Ai2 blog, 2026-11-06), not re-run. Power: normal approximation, "
             "two-sided. Code: scripts/note079_reference.py", ha="center", fontsize=9, color="#8b949e")
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig(OUT, dpi=150)
    print(f"wrote {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
