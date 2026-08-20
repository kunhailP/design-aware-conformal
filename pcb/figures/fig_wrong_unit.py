"""The paper's thesis, as a picture: coverage collapses when the band is
attached to the wrong unit, and the collapse deepens with trajectory length.

Visual grammar (PA main-figure convention): the estimand-matched unit is the
only black series; the wrong units recede to grays; the single reference line
(nominal 90%) is the only color. Direct labels replace the legend. Generated
at the manuscript's print width (5.5 in), so on-page font sizes are the
plotted ones.

figures/wrong_unit_coverage.pdf  (after e28_wrong_unit_coverage)
Run:  python -m pcb.figures.fig_wrong_unit
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
from pcb.figures.style import (use as _style_use, BLACK, DARK_GRAY,
                               LIGHT_GRAY, GRID_GRAY, ACCENT_RED)
_style_use()
import matplotlib.pyplot as plt
import os
import pandas as pd

SERIES = [("trajectory", BLACK, "-", "o", True, "country trajectory"),
          ("per_round", DARK_GRAY, "--", "^", False, "per round"),
          ("marginal", LIGHT_GRAY, ":", "s", False, "per threshold")]


def main():
    d = pd.read_csv("results/wrong_unit_coverage.csv")
    fig, ax = plt.subplots(figsize=(5.5, 3.1), facecolor="white")
    ax.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(DARK_GRAY)
    ax.tick_params(colors=DARK_GRAY, labelsize=8)
    ax.grid(color=GRID_GRAY, lw=0.45)
    ax.set_axisbelow(True)

    ax.axhline(90, color=ACCENT_RED, lw=1.0, ls="--", zorder=1)
    ax.text(2.0, 93.5, "nominal 90%", fontsize=7.5, color=ACCENT_RED,
            va="bottom")

    for key, col, ls, mk, filled, lab in SERIES:
        q = d[d.method == key].sort_values("L")
        ax.plot(q.L, q.traj_cov_pct, ls, color=col, lw=1.5, zorder=2)
        ax.plot(q.L, q.traj_cov_pct, mk, color=col, ms=5,
                mfc=(col if filled else "white"), mew=1.1, zorder=3)
        v = float(q.traj_cov_pct.iloc[-1])
        dy = 5.5 if filled else -2.5      # lift the black label off the 90% line
        ax.annotate(f"{lab}   {v:.1f}", (8, v), textcoords="offset points",
                    xytext=(8, dy), fontsize=8, color=col if key != "marginal"
                    else DARK_GRAY,
                    fontweight="bold" if filled else "normal")

    ax.set_xticks(sorted(d.L.unique()))
    ax.set_xlim(1.6, 11.6)
    ax.set_ylim(0, 100)
    ax.set_xlabel("trajectory length $L$ (survey rounds)", fontsize=8.5,
                  color=BLACK)
    ax.set_ylabel("whole-trajectory coverage (%)", fontsize=8.5, color=BLACK)

    fig.tight_layout()
    os.makedirs("figures", exist_ok=True)
    fig.savefig("figures/wrong_unit_coverage.png", dpi=300,
                bbox_inches="tight")
    fig.savefig("figures/wrong_unit_coverage.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/wrong_unit_coverage.pdf")


if __name__ == "__main__":
    main()
