"""The paper's thesis, as a picture: coverage collapses when the band is
attached to the wrong unit, and the collapse deepens with trajectory length.

Sections 1-5 otherwise carry no display item, so the claim that motivates the
whole construction reaches the reader only as four numbers inside a sentence.
This is that sentence, drawn.

figures/wrong_unit_coverage.png  (after e28_wrong_unit_coverage)
Run:  python -m pcb.figures.fig_wrong_unit
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
from pcb.figures.style import use as _style_use
_style_use()
import matplotlib.pyplot as plt
import os
import pandas as pd

TEXT, MUTED, GRID, SURF = "#1a1a19", "#6b6a63", "#e5e4dd", "#fcfcfb"
RED, BLUE, GOLD = "#D55E00", "#0072B2", "#E69F00"

SERIES = [("marginal", RED, "s", "per threshold (marginal)"),
          ("per_round", GOLD, "^", "per round"),
          ("trajectory", BLUE, "o", "per country trajectory (ours)")]


def main():
    d = pd.read_csv("results/wrong_unit_coverage.csv")
    fig, ax = plt.subplots(figsize=(5.4, 3.5), facecolor=SURF)
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)

    ax.axhline(90, color=MUTED, lw=1.2, ls="--", zorder=1)
    # the ours-line runs along 90, so the reference label sits clear of it
    ax.text(1.75, 94.5, "nominal 90%", fontsize=8, color=MUTED, va="bottom")

    for key, col, mk, lab in SERIES:
        q = d[d.method == key].sort_values("L")
        ax.plot(q.L, q.traj_cov_pct, "-", color=col, lw=1.9, zorder=2)
        ax.plot(q.L, q.traj_cov_pct, mk, color=col, ms=7, mec=SURF, mew=1.2,
                label=lab, zorder=3)
    # label the two endpoints that carry the argument
    for key, col in (("marginal", RED), ("per_round", GOLD)):
        q = d[d.method == key].sort_values("L")
        v = float(q.traj_cov_pct.iloc[-1])
        ax.annotate(f"{v:.1f}%", (8, v), textcoords="offset points",
                    xytext=(9, -3), fontsize=9, color=col, fontweight="bold")

    ax.set_xticks(sorted(d.L.unique()))
    ax.set_xlim(1.6, 9.4)
    ax.set_ylim(0, 100)
    ax.set_xlabel("trajectory length $L$ (survey rounds)", fontsize=9.5, color=TEXT)
    ax.set_ylabel("whole-trajectory coverage (%)", fontsize=9.5, color=TEXT)
    ax.legend(fontsize=8, frameon=False, labelcolor=TEXT, loc="lower left")

    fig.tight_layout()
    os.makedirs("figures", exist_ok=True)
    fig.savefig("figures/wrong_unit_coverage.png", dpi=300, bbox_inches="tight")
    fig.savefig("figures/wrong_unit_coverage.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/wrong_unit_coverage.png")


if __name__ == "__main__":
    main()
