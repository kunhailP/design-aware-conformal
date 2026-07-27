"""Finite-K-safe deconvolution figure.

figures/safe_deconv_coverage.png : (left) coverage vs ρ̂ — plain deconvolution,
    safe deconvolution, routed adaptive-safe, and PCB, against nominal; (right)
    K-sensitivity of adaptive-safe coverage at ρ_true=0.90 approaching nominal
    (ε_{K,B}→0).

Run:  python -m pcb.figures.fig_safe_deconv   (after e20_safe_deconv)
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

BLUE, AQUA, GREEN, YELLOW = "#0072B2", "#56B4E9", "#009E73", "#E69F00"
RED, MUTED2 = "#D55E00", "#8a897f"
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
    d = pd.read_csv("results/safe_deconv_sweep.csv")
    ks = pd.read_csv("results/safe_deconv_ksens.csv")
    g = d.groupby("rho_true")
    x = g.rho_hat.mean().to_numpy()

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10, 4), facecolor="#fcfcfb",
                                   gridspec_kw={"width_ratios": [1.55, 1]})
    _ax(axL); _ax(axR)
    axL.axhline(0.90, color=MUTED, lw=1.2, ls=":")
    axL.text(x[0], 0.905, "nominal 0.90", fontsize=8, color=MUTED)
    axL.plot(x, g.cov_T3.mean(), "-o", color=RED, ms=4, lw=1.6,
             label="deconvolution (plain)")
    axL.plot(x, g.cov_T3_safe.mean(), "-o", color=BLUE, ms=4, lw=1.8,
             label="deconvolution (finite-K-safe)")
    axL.plot(x, g.cov_adaptive_safe.mean(), "-o", color=GREEN, ms=5, lw=2.2,
             label="adaptive-safe (routed)")
    axL.axvline(0.47, color=RED, lw=1.4, ls="--")
    axL.text(0.47, 0.32, "ρ₀", color=RED, fontsize=9, ha="center", fontweight="bold")
    axL.set_ylim(0.28, 1.0)
    axL.set_xlabel("ρ̂", fontsize=9, color=TEXT)
    axL.set_ylabel("coverage of latent target", fontsize=9, color=TEXT)
    axL.legend(fontsize=8, frameon=False, loc="lower left", labelcolor=TEXT)
    axL.set_title("The preregistered α/2-budget correction lifts coverage and\n"
                  "reduces to PCB at low ρ (real-data regime)", fontsize=9.5,
                  color=TEXT, loc="left")

    axR.axhline(0.90, color=MUTED, lw=1.2, ls=":")
    axR.plot(ks.K, ks.cov_adaptive_safe, "-o", color=GREEN, ms=6, lw=2.2)
    for _, r in ks.iterrows():
        axR.text(r.K, r.cov_adaptive_safe - 0.006, f"{r.cov_adaptive_safe:.3f}",
                 ha="center", va="top", fontsize=8, color=TEXT)
    axR.set_xscale("log", base=2)
    axR.set_xticks(ks.K); axR.set_xticklabels(ks.K.astype(int))
    axR.set_ylim(0.80, 0.92)
    axR.set_xlabel("K (calibration countries)", fontsize=9, color=TEXT)
    axR.set_ylabel("adaptive-safe coverage", fontsize=9, color=TEXT)
    axR.set_title("Residual gap is finite-K:\ncoverage → nominal as K grows "
                  "(ε_{K,B}→0)", fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/safe_deconv_coverage.png", dpi=300, bbox_inches="tight"); fig.savefig("figures/safe_deconv_coverage.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/safe_deconv_coverage.png")


if __name__ == "__main__":
    main()
