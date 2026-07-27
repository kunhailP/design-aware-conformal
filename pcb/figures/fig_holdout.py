"""Holdout confirmatory-validation figure (E22, frozen selector, unseen design).

figures/holdout_validation.png:
  (left)  safe-pipeline coverage vs ρ̂, one line per K, pooled over the 10 DGP
          families (min across families shaded) — against the 0.88 floor / 0.90
          nominal. Shows nominal-safety holds on the unseen grid.
  (right) safe-deconvolution activation share vs ρ̂ per K — larger K unlocks the
          efficient branch; small K abstains.

Run:  python -m pcb.figures.fig_holdout   (after e22_holdout_validation)
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
KCOL = {25: "#E69F00", 40: "#56B4E9", 80: "#0072B2", 160: "#6f42c1", 320: "#009E73"}


def _ax(ax):
    ax.set_facecolor("#fcfcfb")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)


def main():
    cell = pd.read_csv("results/holdout_safe_selector_cells.csv").rename(
        columns={"coverage": "cov", "dec": "act"})
    # pool over families: mean and worst (min) coverage per (K, ρ)
    pk = cell.groupby(["K", "rho"]).agg(
        rho_hat=("rlcb", "mean"), cov_mean=("cov", "mean"),
        cov_min=("cov", "min"), act=("act", "mean")).reset_index()

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.5, 4), facecolor="#fcfcfb")
    _ax(axL); _ax(axR)
    axL.axhspan(0.88, 0.90, color="#56B4E9", alpha=0.10)
    axL.axhline(0.90, color=MUTED, lw=1.1, ls=":")
    axL.axhline(0.88, color=RED, lw=1.1, ls="--")
    axL.text(0.03, 0.905, "nominal 0.90", fontsize=7.5, color=MUTED)
    axL.text(0.03, 0.867, "floor 0.88", fontsize=7.5, color=RED)
    for K in sorted(KCOL):
        t = pk[pk.K == K].sort_values("rho_hat")
        axL.plot(t.rho_hat, t.cov_mean, "-o", color=KCOL[K], ms=3.3, lw=1.6, label=f"K={K}")
        axL.fill_between(t.rho_hat, t.cov_min, t.cov_mean, color=KCOL[K], alpha=0.10)
    axL.set_ylim(0.83, 1.005)
    axL.set_xlabel("ρ̂ (conservative LCB)", fontsize=9, color=TEXT)
    axL.set_ylabel("safe-pipeline coverage", fontsize=9, color=TEXT)
    axL.legend(fontsize=8, frameon=False, labelcolor=TEXT, ncol=2)
    axL.set_title("Coverage on the UNSEEN grid (10 new DGPs, new K, new ρ)\n"
                  "line = mean over families, shade = worst family",
                  fontsize=9.5, color=TEXT, loc="left")

    for K in sorted(KCOL):
        t = pk[pk.K == K].sort_values("rho_hat")
        axR.plot(t.rho_hat, t.act * 100, "-o", color=KCOL[K], ms=3.3, lw=1.6, label=f"K={K}")
    axR.axvline(0.47, color=RED, lw=1.2, ls="--")
    axR.text(0.47, 103, "ρ₀", color=RED, fontsize=9, ha="center", fontweight="bold")
    axR.set_ylim(0, 108)
    axR.set_xlabel("ρ̂ (conservative LCB)", fontsize=9, color=TEXT)
    axR.set_ylabel("safe-deconvolution activation (%)", fontsize=9, color=TEXT)
    axR.legend(fontsize=8, frameon=False, labelcolor=TEXT, ncol=2)
    axR.set_title("Efficient branch unlocks with K;\nsmall K abstains (honest)",
                  fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/holdout_validation.png", dpi=300, bbox_inches="tight"); fig.savefig("figures/holdout_validation.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/holdout_validation.png")


if __name__ == "__main__":
    main()
