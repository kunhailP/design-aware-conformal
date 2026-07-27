"""Safe-adaptive selector figure (Gate 5E, simulation, known truth).

figures/safe_selector_grid.png : (left) safe-pipeline coverage vs ρ̂ for each K,
    against the 0.88 floor and 0.90 nominal — held everywhere via fallback;
    (right) safe-deconvolution activation share vs ρ̂ for each K — larger K unlocks
    the efficient branch, small K abstains to conservative.

Run:  python -m pcb.figures.fig_safe_selector   (after e21_safe_selector)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
from pcb.figures.style import use as _style_use
_style_use()
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd

TEXT, MUTED, GRID = "#1a1a19", "#6b6a63", "#e5e4dd"
RED = "#D55E00"
KCOL = {30: "#E69F00", 60: "#56B4E9", 120: "#0072B2", 240: "#6f42c1"}


def _ax(ax):
    ax.set_facecolor("#fcfcfb")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)


def main():
    d = pd.read_csv("results/safe_selector_grid.csv")
    g = d.groupby(["K", "rho_true"])
    tab = g.agg(rho=("rlcb", "mean"), coverage=("cov_safe", "mean"),
                act=("branch", lambda s: (s == "deconv").mean())).reset_index()

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10, 4), facecolor="#fcfcfb")
    _ax(axL); _ax(axR)
    axL.axhspan(0.88, 0.90, color="#56B4E9", alpha=0.10)
    axL.axhline(0.90, color=MUTED, lw=1.1, ls=":")
    axL.axhline(0.88, color=RED, lw=1.1, ls="--")
    axL.text(0.03, 0.885, "floor 0.88", fontsize=7.5, color=RED)
    axL.text(0.03, 0.905, "nominal 0.90", fontsize=7.5, color=MUTED)
    for K in sorted(KCOL):
        t = tab[tab.K == K].sort_values("rho")
        axL.plot(t["rho"], t["coverage"], "-o", color=KCOL[K], ms=3.5, lw=1.7, label=f"K={K}")
    axL.set_ylim(0.82, 1.01)
    axL.set_xlabel("ρ̂ (conservative)", fontsize=9, color=TEXT)
    axL.set_ylabel("safe-pipeline coverage", fontsize=9, color=TEXT)
    axL.legend(fontsize=8, frameon=False, labelcolor=TEXT)
    axL.set_title("Coverage held ≥ floor at every K, incl. K=30 high-ρ\n"
                  "(via conservative fallback)", fontsize=9.5, color=TEXT, loc="left")

    for K in sorted(KCOL):
        t = tab[tab.K == K].sort_values("rho")
        axR.plot(t["rho"], t["act"] * 100, "-o", color=KCOL[K], ms=3.5, lw=1.7,
                 label=f"K={K}")
    axR.axvline(0.47, color=RED, lw=1.3, ls="--")
    axR.text(0.47, 103, "ρ₀", color=RED, fontsize=9, ha="center", fontweight="bold")
    axR.set_ylim(0, 108)
    axR.set_xlabel("ρ̂ (conservative)", fontsize=9, color=TEXT)
    axR.set_ylabel("safe-deconvolution activation (%)", fontsize=9, color=TEXT)
    axR.legend(fontsize=8, frameon=False, labelcolor=TEXT)
    axR.set_title("Larger K unlocks the efficient branch;\nsmall K abstains "
                  "(honest inference)", fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/safe_selector_grid.png", dpi=300, bbox_inches="tight"); fig.savefig("figures/safe_selector_grid.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/safe_selector_grid.png")


if __name__ == "__main__":
    main()
