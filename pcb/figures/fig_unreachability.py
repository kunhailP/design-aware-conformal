"""Survey-scale unreachability of design-aware deconvolution (E24).

Two independent structural barriers, both measured on real ESS data, both decisive:

  figures/unreachability.png
    Left  (gate A, ρ saturation): estimated SD-ratio ρ̂ (and its LCB) per age-band
        subpopulation, against ρ₀=0.47. Even the narrowest youth cells reach only
        ρ̂≈0.29 — design noise never dominates the between-country transport signal
        for high-variation political outcomes.
    Right (gate B, reliability floor): the finite-K reliability D vs K, against the
        distribution-free floor D ≥ √(2/(K−1)) (which the ESS cells sit right on)
        and the gate-B feasibility threshold τ_D=0.147. Passing gate B needs
        K ≥ 94 exchangeable populations; ESS has ≤ 33. The feasible region (green)
        is empty at survey scale.

Run:  python -m pcb.figures.fig_unreachability   (after e24_subgroup_rho_scan)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
import os
import numpy as np
import pandas as pd

TEXT, MUTED, GRID, SURF = "#1a1a19", "#6b6a63", "#e5e4dd", "#fcfcfb"
RED, BLUE, GREEN, GOLD = "#e34948", "#2a78d6", "#1baf7a", "#eda100"
RHO0, TAU_D = 0.47, (0.02 - 0.0061) / 0.0943      # gate-A cutoff, gate-B D-threshold
KSTAR = 1 + 2 / TAU_D**2                           # min K for gate B (≈94)

ORDER = ["youth_18_24", "youth_18_29", "young_25_34", "mid_35_49",
         "older_50_64", "oldest_65p", "full_18plus"]
NICE = {"youth_18_24": "18–24", "youth_18_29": "18–29", "young_25_34": "25–34",
        "mid_35_49": "35–49", "older_50_64": "50–64", "oldest_65p": "65+",
        "full_18plus": "all 18+"}


def _ax(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)


def main():
    d = pd.read_csv("results/ess_subgroup_rho_scan.csv")
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11, 4.3), facecolor=SURF)
    _ax(axA); _ax(axB)

    # -- Panel A: gate A, ρ saturation --------------------------------------
    xs = np.arange(len(ORDER))
    hi = [d[d.subgroup == sg].rho_hat.max() for sg in ORDER]
    lc = [d[d.subgroup == sg].rho_lcb.max() for sg in ORDER]
    axA.vlines(xs, lc, hi, color=BLUE, lw=1.0, alpha=0.5)
    axA.plot(xs, hi, "o", color=BLUE, ms=6, label="ρ̂ (max over min-n)")
    axA.plot(xs, lc, "o", color=BLUE, ms=5, mfc="white", label="ρ̂ lower CB")
    axA.axhline(RHO0, color=RED, lw=1.4, ls="--")
    axA.text(0.05, RHO0 + 0.012, f"ρ₀ = {RHO0} (deconvolution needs ρ̂$_{{LCB}}$ above this)",
             fontsize=8, color=RED)
    axA.axhspan(RHO0, 1.0, color=RED, alpha=0.05)
    axA.set_xticks(xs); axA.set_xticklabels([NICE[s] for s in ORDER], rotation=30,
                                            ha="right", fontsize=8.5)
    axA.set_ylim(0, 0.62)
    axA.set_ylabel("estimated SD-ratio  ρ̂", fontsize=9.5, color=TEXT)
    axA.set_xlabel("ESS age-band subpopulation", fontsize=9.5, color=TEXT)
    axA.legend(fontsize=8, frameon=False, labelcolor=TEXT, loc="upper right")
    axA.set_title("Gate A: ρ̂ saturates far below ρ₀\n(design noise never dominates "
                  "the transport signal)", fontsize=9.5, color=TEXT, loc="left")

    # -- Panel B: gate B, reliability floor ---------------------------------
    Kgrid = np.arange(4, 400)
    floor = np.sqrt(2 / (Kgrid - 1))
    # feasible region: K >= KSTAR AND D <= TAU_D
    axB.axhspan(0, TAU_D, xmin=(np.log(KSTAR) - np.log(4)) / (np.log(399) - np.log(4)),
                xmax=1.0, color=GREEN, alpha=0.10)
    axB.plot(Kgrid, floor, "-", color=TEXT, lw=1.6,
             label="floor  D ≥ √(2/(K−1))")
    axB.scatter(d.K, d.D, s=26, color=GOLD, edgecolor=TEXT, lw=0.4, zorder=3,
                label="ESS cells (all subpopulations)")
    axB.axhline(TAU_D, color=RED, lw=1.4, ls="--")
    axB.text(4.3, TAU_D - 0.028, f"gate-B threshold  τ$_D$={TAU_D:.3f}",
             fontsize=8, color=RED)
    axB.axvline(KSTAR, color=GREEN, lw=1.3, ls=":")
    axB.text(KSTAR * 1.03, 0.62, f"K* = {KSTAR:.0f}\n(min K for gate B)",
             fontsize=8, color="#0e7a52")
    axB.annotate("ESS: K ≤ 33", xy=(33, np.sqrt(2 / 32)), xytext=(46, 0.44),
                 fontsize=8.5, color=TEXT,
                 arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0))
    axB.set_xscale("log")
    ticks = [4, 10, 33, 94, 300]
    axB.xaxis.set_minor_locator(NullLocator())
    axB.xaxis.set_major_locator(FixedLocator(ticks))
    axB.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}"))
    axB.set_xlim(4, 399)
    axB.set_ylim(0, 0.92)
    axB.set_xlabel("number of exchangeable populations  K", fontsize=9.5, color=TEXT)
    axB.set_ylabel("finite-K reliability  D", fontsize=9.5, color=TEXT)
    axB.legend(fontsize=8, frameon=False, labelcolor=TEXT, loc="upper right")
    axB.set_title("Gate B: reliability floor needs K ≥ 94\n(the feasible region is "
                  "empty at survey scale)", fontsize=9.5, color=TEXT, loc="left")

    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/unreachability.png", dpi=200)
    plt.close(fig)
    print(f"τ_D={TAU_D:.4f}  K*={KSTAR:.1f}  "
          f"max ρ̂={d.rho_hat.max():.3f}  max ρ̂_LCB={d.rho_lcb.max():.3f}  "
          f"min D={d.D.min():.3f} at K={int(d.loc[d.D.idxmin(),'K'])}")
    print("wrote figures/unreachability.png")


if __name__ == "__main__":
    main()
