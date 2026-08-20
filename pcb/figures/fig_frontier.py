"""Figure 2 (APSR grammar) — the feasibility frontier, observations first.

The real-data cells and their estimation uncertainty are the protagonists;
the frozen boundaries are thin dashed rules pushed behind the data, regime
words are three small italic labels, and there are no fills or colors.
figures/feasibility_frontier.{pdf,png}.
Run:  python -m pcb.figures.fig_frontier   (after e57)
"""
import matplotlib
matplotlib.use("Agg")
from pcb.figures.style import apsr, apsr_box, INK, GR1, GR2
apsr()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RHO0 = 0.47
TAU_D = (0.02 - 0.0061) / 0.0943
KSTAR = int(np.ceil(1 + 2 / TAU_D ** 2))
MARKS = {"WVS full-coverage items": ("s", "WVS items"),
         "ESS national-unit scan": ("o", "ESS national"),
         "ESS small-area (e54)": ("^", "ESS small-area"),
         "ESS small-area, common NUTS level": ("D",
                                               "Small-area, one NUTS level")}


def main():
    d = pd.read_csv("results/feasibility_frontier.csv")
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    apsr_box(ax, ygrid=False)
    ax.set_xscale("log")
    ax.set_xlim(8, 420)
    ax.set_ylim(0, 0.62)
    # boundaries: thin, behind the data
    ax.axhline(RHO0, color=GR2, lw=0.7, ls="--", zorder=1)
    ax.axvline(KSTAR, color=GR2, lw=0.7, ls="--", zorder=1)
    ax.text(8.7, RHO0 + 0.014, r"$\rho_0$", fontsize=8, color=GR1)
    ax.text(KSTAR * 0.93, 0.598, r"$K=94$", fontsize=8, color=GR1, va="top", ha="right")
    for t, xy, va in [("Unnecessary", (150, 0.02), "baseline"),
                      ("Unlearnable", (9, 0.585), "top"),
                      ("Feasible", (160, 0.585), "top")]:
        ax.text(*xy, t, fontsize=7.5, style="italic", color=GR2, va=va)
    for name, (mk, lab) in MARKS.items():
        g = d[d.dataset == name]
        ax.vlines(g.K, g.rho_lcb, g.rho_hat, color=GR2, lw=0.6, zorder=2)
        idle, act = g[~g.activated], g[g.activated]
        ax.scatter(idle.K, idle.rho_lcb, s=20, facecolors="white",
                   edgecolors=INK, marker=mk, lw=0.8, label=lab, zorder=3)
        if len(act):
            ax.scatter(act.K, act.rho_lcb, s=27, facecolors=INK,
                       edgecolors=INK, marker=mk, zorder=4,
                       label="Selector activated")
    ax.set_xlabel("Exchangeable populations, K (log scale)", fontsize=9)
    ax.set_ylabel(r"Design-to-total ratio, $\hat\rho$"
                  "  (bar: LCB to estimate)", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="lower left",
              handletextpad=0.15, labelspacing=0.3, borderaxespad=0.3)
    fig.tight_layout()
    fig.savefig("figures/feasibility_frontier.pdf", bbox_inches="tight")
    fig.savefig("figures/feasibility_frontier.png", dpi=300,
                bbox_inches="tight")
    print("wrote figures/feasibility_frontier.pdf")


if __name__ == "__main__":
    main()
