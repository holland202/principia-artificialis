#!/usr/bin/env python3
"""figures/novelty_map.png — evidence profile per audit cluster (2026-11-10 audit).

Data comes from scripts/novelty_audit_census.py's cluster map and the same
regexes, so the figure cannot drift from the census without this script
failing or changing. Each cluster's bar splits its notes into three segments:
notes with at least one registered P<n> line, notes carrying a kept REFUTED
marker but no P<n> line (early-series refutations recorded in prose), and
notes with neither. Segments are counts of NOTES; a note with both P lines
and REFUTED counts once, in the P-line segment.

Run from the repository root:  python scripts/generate_novelty_map.py
"""
from __future__ import annotations

import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from novelty_audit_census import CLUSTERS, PRED, ROOT  # noqa: E402

# Palette validated 2026-11-10 (dataviz six-checks, light surface): the two
# evidence hues pass all checks; gray is the deliberate neutral for "neither",
# relieved by direct labels.
BLUE, ORANGE, GRAY = "#2f6bb0", "#d97706", "#9ca3af"


def main() -> None:
    rows = []
    for name, members in CLUSTERS.items():
        pred = refuted = neither = 0
        for m in members:
            t = (ROOT / m).read_text(encoding="utf-8", errors="replace")
            if PRED.search(t):
                pred += 1
            elif "REFUTED" in t:
                refuted += 1
            else:
                neither += 1
        rows.append((name, pred, refuted, neither))
    rows.reverse()  # A at top after horizontal plot

    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=200)
    surface = "#fcfcfb"
    fig.patch.set_facecolor(surface)
    ax.set_facecolor(surface)
    names = [r[0] for r in rows]
    y = range(len(rows))
    left = [0] * len(rows)
    for idx, (color, label) in enumerate(
        [(BLUE, "registered P-lines"), (ORANGE, "REFUTED kept (prose)"), (GRAY, "neither")]
    ):
        vals = [r[1 + idx] for r in rows]
        ax.barh(list(y), vals, left=left, height=0.62, color=color, label=label,
                edgecolor=surface, linewidth=2)
        for yi, (v, l0) in enumerate(zip(vals, left)):
            if v:
                ax.text(l0 + v / 2, yi, str(v), va="center", ha="center",
                        fontsize=8.5, color="white" if color != GRAY else "#1f2937")
        left = [l0 + v for l0, v in zip(left, vals)]

    ax.set_yticks(list(y), names, fontsize=8.5)
    ax.set_xlabel("notes", fontsize=9)
    ax.set_title("Evidence profile of the 102 indexed notes, by novelty-audit cluster\n"
                 "(docs/NOVELTY_AUDIT_2026-11-10.md; counts from scripts/novelty_audit_census.py)",
                 fontsize=10, loc="left")
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors="#4b5563")
    ax.margins(x=0.02)
    fig.tight_layout()
    out = ROOT / "figures" / "novelty_map.png"
    fig.savefig(out, facecolor=surface)
    total = sum(r[1] + r[2] + r[3] for r in rows)
    print(f"wrote {out.relative_to(ROOT)}; notes drawn: {total}")
    if total != sum(len(m) for m in CLUSTERS.values()):
        print("PROBLEM: drawn count != cluster map count")
        sys.exit(1)


if __name__ == "__main__":
    main()
