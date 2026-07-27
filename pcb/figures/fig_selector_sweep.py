"""Selector-transition sweep figure (simulation, known truth).

figures/selector_sweep.png : two panels vs ρ̂ —
  (top) branch share PCB → deconvolution → conservative fallback;
  (bottom) coverage of PCB (over-covers), deconvolution (under-covers at finite K),
  and the routed adaptive pipeline, against the nominal 0.90 line.
Honest: shows the transition AND the finite-K deconvolution undercoverage.

Run:  python -m pcb.figures.fig_selector_sweep   (after e19_selector_sweep)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd

BLUE, AQUA, YELLOW, GREEN = "#2a78d6", "#1baf7a", "#eda100", "#008300"
RED, MUTED2 = "#e34948", "#8a897f"
TEXT, MUTED, GRID = "#1a1a19", "#6b6a63", "#e5e4dd"


def _ax(ax):
    ax.set_facecolor("#fcfcfb")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)


def main():
    d = pd.read_csv("results/selector_sweep_sim.csv")
    g = d.groupby("rho_true")
    x = g.rho_hat.mean().to_numpy()
    pcb = g.branch.apply(lambda s: (s == "T1").mean()).to_numpy()
    dec = g.branch.apply(lambda s: (s == "T3").mean()).to_numpy()
    con = g.branch.apply(lambda s: (s == "T2").mean()).to_numpy()
    cov_ad = g.cov_adaptive.mean().to_numpy()
    cov_p = g.cov_T1.mean().to_numpy()
    cov_d = g.cov_T3.mean().to_numpy()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.6, 6.2), sharex=True,
                                   facecolor="#fcfcfb")
    _ax(ax1); _ax(ax2)
    ax1.stackplot(x, pcb, dec, con, colors=[MUTED2, BLUE, YELLOW],
                  labels=["PCB", "deconvolution", "conservative fallback"],
                  edgecolor="#fcfcfb", linewidth=0.5)
    ax1.axvline(0.47, color=RED, lw=1.6, ls="--")
    ax1.text(0.47, 1.02, "ρ₀=0.47", color=RED, fontsize=8.5, ha="center",
             fontweight="bold")
    ax1.set_ylim(0, 1); ax1.set_ylabel("branch share", fontsize=9, color=TEXT)
    ax1.legend(fontsize=8, frameon=False, loc="center left", labelcolor=TEXT)
    ax1.set_title("Selector transition (simulation, known truth): "
                  "PCB → deconvolution → conservative fallback",
                  fontsize=10, color=TEXT, loc="left")

    ax2.axhline(0.90, color=MUTED, lw=1.2, ls=":")
    ax2.text(x[0], 0.905, "nominal 0.90", fontsize=8, color=MUTED)
    ax2.plot(x, cov_p, "-o", color=MUTED2, ms=4, lw=1.8, label="PCB (over-covers)")
    ax2.plot(x, cov_d, "-o", color=BLUE, ms=4, lw=1.8,
             label="deconvolution (finite-K undercoverage)")
    ax2.plot(x, cov_ad, "-o", color=GREEN, ms=5, lw=2.2, label="adaptive (routed)")
    ax2.axvline(0.47, color=RED, lw=1.6, ls="--")
    ax2.set_ylim(0.25, 1.02)
    ax2.set_xlabel("ρ̂  (estimated design/transport SD ratio)", fontsize=9, color=TEXT)
    ax2.set_ylabel("coverage of latent target", fontsize=9, color=TEXT)
    ax2.legend(fontsize=8, frameon=False, loc="lower left", labelcolor=TEXT)
    ax2.set_title("Honest finite-K (K=30) picture: deconvolution undercovers in the "
                  "transition\nregime (ε_{K,B}); real data never reaches ρ̂>0.23",
                  fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/selector_sweep.png", dpi=200)
    plt.close(fig)
    print("wrote figures/selector_sweep.png")


if __name__ == "__main__":
    main()
