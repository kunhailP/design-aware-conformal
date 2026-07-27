"""figures/unit_frontier.pdf — the unit-refinement frontier (E49).

Left panel: K and the reliability diagnostic D against unit size, with the
gate-B feasibility threshold. Right panel: the design-to-total ratio's lower
confidence bound against unit size, with the need-gate cutoff rho0. Together
they show both barriers of Proposition 1 relaxing as the exchangeable unit is
refined, and where each is crossed on real ESS data.

Run:  python -m pcb.figures.fig_unit_frontier   (after e49_unit_frontier)
"""
from __future__ import annotations
import os

import matplotlib

matplotlib.use("Agg")
from pcb.figures.style import use as _style_use, save, ax_clean, BLUE, ORANGE, VERMILION, MUTED, TEXT, GREEN, COL
_style_use()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RHO0 = 0.47


def main():
    d = pd.read_csv("results/unit_frontier.csv")
    d = d[d.estimand.str.startswith("within")]
    g = d.groupby("min_n").agg(K=("K", "median"), D=("D", "median"),
                               duc=("delta_ucb", "median"),
                               rho=("rho_lcb", "median"),
                               rho_lo=("rho_lcb", "min"),
                               rho_hi=("rho_lcb", "max"),
                               gain=("raw_width_gain", "median")).reset_index()
    g = g.sort_values("min_n", ascending=False)
    x = np.arange(len(g))
    lab = [str(int(v)) for v in g.min_n]

    fig, axes = plt.subplots(1, 2, figsize=(COL * 1.55, 2.9))

    ax = axes[0]; ax_clean(ax)
    ax.plot(x, g.duc, "o-", color=BLUE, ms=3.5,
            label=r"$\widehat\delta_{\mathrm{UCB}}(D)$")
    ax.axhline(0.02, color=VERMILION, ls="--", lw=1.1)
    ax.text(0.15, 0.0205, r"reliability gate  $\delta_{\max}=0.02$",
            color=VERMILION, fontsize=7)
    passed = g[g.duc <= 0.02]
    if len(passed):
        xc = int(x[np.searchsorted(-g.min_n.values, -passed.min_n.max())])
        ax.plot([xc], [passed.iloc[0].duc], "o", ms=7, mfc="none",
                mec=VERMILION, mew=1.4)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=6.8)
    ax.set_xlabel("minimum respondents per region")
    ax.set_ylabel(r"finite-$K$ remainder bound")
    ax.legend(loc="upper right")
    ax2 = ax.twinx(); ax2.grid(False)
    ax2.plot(x, g.K, "-", color=ORANGE, lw=1.2, alpha=.9)
    ax2.set_ylabel("K (regions)", color=ORANGE, fontsize=8)
    ax2.tick_params(axis="y", colors=ORANGE, labelsize=7)
    for s in ("top",):
        ax2.spines[s].set_visible(False)
    ax.set_title("reliability gate: all rounds by 80 per region", loc="left")

    ax = axes[1]; ax_clean(ax)
    ax.fill_between(x, g.rho_lo, g.rho_hi, color=BLUE, alpha=.15, lw=0)
    ax.plot(x, g.rho, "o-", color=BLUE, ms=3.5,
            label=r"$\widehat\rho_{\mathrm{LCB}}$ (median over rounds)")
    ax.axhline(RHO0, color=VERMILION, ls="--", lw=1.1)
    ax.text(0.15, RHO0 - 0.028, r"need gate  $\rho_0=0.47$", color=VERMILION,
            fontsize=7)
    cross = g[g.rho >= RHO0]
    if len(cross):
        xc = x[np.searchsorted(-g.min_n.values, -cross.min_n.max())]
        ax.plot([xc], [cross.iloc[0].rho], "o", ms=7, mfc="none",
                mec=VERMILION, mew=1.4)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=6.8)
    ax.set_xlabel("minimum respondents per region")
    ax.set_ylabel(r"design-to-total ratio (LCB)")
    ax.legend(loc="lower right")
    ax.set_title("need gate: crossed in one round at 25--30", loc="left")

    fig.tight_layout()
    save(fig, "unit_frontier")
    print("wrote figures/unit_frontier.pdf/.png")


if __name__ == "__main__":
    main()
