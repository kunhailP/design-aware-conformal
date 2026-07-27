"""figures/optimal_unit.pdf — the exchangeable unit has an interior optimum (E51).

Left: the deployed band half-width against unit size, with the infeasible coarse
region marked and the minimum circled. Right: the two factors that produce it —
the conformal factor q(K), which explodes as units coarsen, and the per-unit
design SD, which grows as units refine.

Run:  python -m pcb.figures.fig_optimal_unit   (after e51_optimal_unit)
"""
from __future__ import annotations
import os

import matplotlib

matplotlib.use("Agg")
from pcb.figures.style import (use as _style_use, save, ax_clean, BLUE, ORANGE,
                               VERMILION, MUTED, TEXT, COL)
_style_use()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    d = pd.read_csv("results/optimal_unit.csv")
    g = (d.groupby("min_n")
         .agg(K=("K", "median"), half=("halfwidth", "median"),
              s=("s_between", "median"), v=("v_design", "median"),
              stot=("s_total", "median"), feas=("quantile_feasible", "all"))
         .reset_index().sort_values("min_n"))
    g["factor"] = g.half / g.stot          # standardized conformal factor
    x = np.arange(len(g))
    lab = [str(int(v)) for v in g.min_n]
    fin = np.isfinite(g.half.values)

    fig, axes = plt.subplots(1, 2, figsize=(COL * 1.55, 2.9))

    ax = axes[0]; ax_clean(ax)
    ax.plot(x[fin], g.half.values[fin], "o-", color=BLUE, ms=3.8)
    bad = ~g.feas.values
    if bad.any():
        ax.axvspan(x[bad].min() - 0.5, x[-1] + 0.5, color=VERMILION, alpha=.10, lw=0)
        ax.text(x[bad].min() - 0.35, np.nanmax(g.half.values[fin]) * 0.95,
                "conformal level\ninfeasible: band $=[0,1]$", fontsize=6.8,
                color=VERMILION, va="top", ha="right")
    i = int(np.nanargmin(np.where(fin, g.half.values, np.inf)))
    ax.plot([x[i]], [g.half.values[i]], "o", ms=8, mfc="none", mec=VERMILION, mew=1.5)
    ax.annotate(f"optimum\n$K={int(g.K.values[i])}$", (x[i], g.half.values[i]),
                textcoords="offset points", xytext=(6, 14), fontsize=7,
                color=VERMILION)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=6.8)
    ax.set_xlabel("minimum respondents per unit")
    ax.set_ylabel("band half-width")
    ax.set_title("the unit has an interior optimum", loc="left")

    ax = axes[1]; ax_clean(ax)
    fac = np.where(np.isfinite(g.factor.values), g.factor.values, np.nan)
    ax.plot(x, fac, "o-", color=BLUE, ms=3.5)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=6.8)
    ax.set_xlabel("minimum respondents per unit")
    ax.set_ylabel(r"conformal factor $\widehat q/s_{\rm total}$", color=BLUE)
    ax.tick_params(axis="y", colors=BLUE)
    ax.annotate("explodes as $K$ falls", (x[-3], np.nanmax(fac)),
                textcoords="offset points", xytext=(-8, -4), fontsize=7,
                color=BLUE, ha="right")
    ax2 = ax.twinx(); ax2.grid(False)
    ax2.plot(x, g.stot, "s--", color=ORANGE, ms=3.0, lw=1.2)
    ax2.set_ylabel(r"total scale $s_{\rm total}$", color=ORANGE)
    ax2.tick_params(axis="y", colors=ORANGE, labelsize=7)
    ax2.spines["top"].set_visible(False)
    ax2.annotate("grows as units refine", (x[1], g.stot.values[1]),
                 textcoords="offset points", xytext=(10, 8), fontsize=7,
                 color=ORANGE)
    ax.set_title(r"$W=\widehat q\;=\;$ factor $\times\;s_{\rm total}$", loc="left")

    fig.tight_layout()
    save(fig, "optimal_unit")
    print("wrote figures/optimal_unit.pdf/.png")


if __name__ == "__main__":
    main()
