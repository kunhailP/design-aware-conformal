"""The feasibility frontier in the (K, rho) plane (E57).

Writes figures/feasibility_frontier.pdf
       figures/feasibility_frontier.png

Three regimes from two universal quantities: the maximal width gain
1 - sqrt(1 - rho^2) (AW-1) and the reliability floor sqrt(2/(K-1))
(Lemma: universal floor). Boundaries drawn at the frozen instantiations
rho_0 = 0.47 and K = 1 + 2/tau_D^2 = 94; points are real-data cells from the
committed results (WVS gate probe, ESS national-unit scan, ESS small-area
transport), filled where the frozen selector activated.

Run:  python -m pcb.figures.fig_frontier   (after e57_feasibility_frontier)
"""
import matplotlib
matplotlib.use("Agg")
from pcb.figures.style import use as _style_use
_style_use()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TEXT, MUTED, GRID, SURF = "#1a1a19", "#6b6a63", "#e5e4dd", "#fcfcfb"
RED, BLUE, GREEN = "#D55E00", "#0072B2", "#0e7a52"
RHO0 = 0.47
TAU_D = (0.02 - 0.0061) / 0.0943
KSTAR = int(np.ceil(1 + 2 / TAU_D ** 2))          # 94


def main():
    d = pd.read_csv("results/feasibility_frontier.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.4), facecolor=SURF)
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.set_xscale("log")
    ax.set_xlim(8, 420); ax.set_ylim(0, 0.62)

    # regimes
    ax.axhspan(0, RHO0, color="#efeee8", zorder=0)
    ax.axvspan(8, KSTAR, ymin=RHO0 / 0.62, ymax=1, color="#f6e3d3", zorder=0)
    ax.axvspan(KSTAR, 420, ymin=RHO0 / 0.62, ymax=1, color="#e2efe6", zorder=0)
    ax.axhline(RHO0, color=RED, lw=1.1, ls="--")
    ax.axvline(KSTAR, color=GREEN, lw=1.1, ls="--")
    ax.text(9, RHO0 - 0.045, f"unnecessary: ρ̂$_{{LCB}}$ ≤ ρ₀ = {RHO0}",
            fontsize=10, color=MUTED)
    ax.text(9, 0.56, "unlearnable:\nK < 1 + 2/τ²", fontsize=10, color=RED)
    ax.text(KSTAR * 1.1, 0.56, f"feasible: K ≥ {KSTAR}", fontsize=10,
            color=GREEN)

    marks = {"WVS full-coverage items": (BLUE, "o"),
             "ESS national-unit scan": (RED, "s"),
             "ESS small-area (e54)": (GREEN, "^"),
             "ESS small-area, common NUTS level": ("#8a7a1e", "D")}
    for name, (col, mk) in marks.items():
        g = d[d.dataset == name]
        fired = g[g.activated]
        idle = g[~g.activated]
        ax.scatter(idle.K, idle.rho_lcb, s=34, facecolors="none",
                   edgecolors=col, marker=mk, label=name, lw=1.2)
        if len(fired):
            ax.scatter(fired.K, fired.rho_lcb, s=44, facecolors=col,
                       edgecolors=col, marker=mk,
                       label=name + " — selector fired")
    ax.set_xlabel("number of exchangeable populations  K (log scale)",
                  fontsize=10.5, color=TEXT)
    ax.set_ylabel("design-to-total ratio  ρ̂$_{LCB}$", fontsize=10.5,
                  color=TEXT)
    ax.legend(fontsize=9, frameon=False, labelcolor=TEXT, loc="center right")
    fig.tight_layout()
    fig.savefig("figures/feasibility_frontier.pdf")
    fig.savefig("figures/feasibility_frontier.png", dpi=200)
    print("wrote figures/feasibility_frontier.pdf")


if __name__ == "__main__":
    main()
