"""The feasibility frontier in the (K, rho) plane — main Figure 2.

Visual grammar: the three regimes are white / very light gray fills with black
dashed boundaries; datasets are distinguished by SHAPE, not color; the only
color is the accent fill on the cells where the frozen selector actually
activated. Region formulas live in the caption, not the plot. Generated at
the manuscript's print width (5.5 in).

Writes figures/feasibility_frontier.pdf / .png
Run:  python -m pcb.figures.fig_frontier   (after e57_feasibility_frontier)
"""
import matplotlib
matplotlib.use("Agg")
from pcb.figures.style import (use as _style_use, BLACK, DARK_GRAY, MID_GRAY,
                               GRID_GRAY, REGION_GRAY, ACCENT_BLUE)
_style_use()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RHO0 = 0.47
TAU_D = (0.02 - 0.0061) / 0.0943
KSTAR = int(np.ceil(1 + 2 / TAU_D ** 2))          # 94

MARKS = {"WVS full-coverage items": ("s", "WVS items"),
         "ESS national-unit scan": ("o", "ESS national"),
         "ESS small-area (e54)": ("^", "ESS small-area"),
         "ESS small-area, common NUTS level": ("D", "small-area, one NUTS level")}


def main():
    d = pd.read_csv("results/feasibility_frontier.csv")
    fig, ax = plt.subplots(figsize=(5.5, 3.6), facecolor="white")
    ax.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(DARK_GRAY)
    ax.tick_params(colors=DARK_GRAY, labelsize=8)
    ax.set_xscale("log")
    ax.set_xlim(8, 420)
    ax.set_ylim(0, 0.62)

    # regimes: fills carry meaning (correction pointless / blocked / open)
    ax.axhspan(0, RHO0, color=REGION_GRAY, zorder=0)
    ax.axvspan(KSTAR, 420, ymin=RHO0 / 0.62, ymax=1, color=REGION_GRAY,
               zorder=0)
    ax.axhline(RHO0, color=BLACK, lw=0.9, ls="--")
    ax.plot([KSTAR, KSTAR], [RHO0, 0.62], color=BLACK, lw=0.9, ls="--")
    ax.text(8.7, 0.055, "unnecessary", fontsize=8.5, color=DARK_GRAY,
            style="italic")
    ax.text(24, 0.575, "unlearnable", fontsize=8.5, color=DARK_GRAY,
            style="italic", va="top")
    ax.text(KSTAR * 1.09, 0.575, "feasible", fontsize=8.5, color=DARK_GRAY,
            style="italic", va="top")

    for name, (mk, lab) in MARKS.items():
        g = d[d.dataset == name]
        idle = g[~g.activated]
        fired = g[g.activated]
        ax.scatter(idle.K, idle.rho_lcb, s=22, facecolors="white",
                   edgecolors=BLACK, marker=mk, lw=0.9, label=lab, zorder=3)
        if len(fired):
            ax.scatter(fired.K, fired.rho_lcb, s=30, facecolors=ACCENT_BLUE,
                       edgecolors=ACCENT_BLUE, marker=mk, zorder=4,
                       label="selector activated")
    ax.set_xlabel("exchangeable populations  $K$ (log scale)", fontsize=8.5,
                  color=BLACK)
    ax.set_ylabel(r"design-to-total ratio  $\hat\rho_{\mathrm{LCB}}$",
                  fontsize=8.5, color=BLACK)
    fig.legend(fontsize=7.5, frameon=False, labelcolor=BLACK, ncol=3,
               loc="upper center", bbox_to_anchor=(0.5, 0.04),
               handletextpad=0.3, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig("figures/feasibility_frontier.pdf", bbox_inches="tight")
    fig.savefig("figures/feasibility_frontier.png", dpi=300, bbox_inches="tight")
    print("wrote figures/feasibility_frontier.pdf")


if __name__ == "__main__":
    main()
