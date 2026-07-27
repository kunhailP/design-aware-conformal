"""Gate-5D Part C figures — LAPOP change-function transport.

figures/lapop_level_vs_change_rho.png : ρ̂ for level (Part B) vs change (Part C)
    transport per outcome, against the ρ₀ fallback cutoff — change raises ρ but
    both stay in the low-ρ regime.
figures/lapop_change_width_by_method.png : T1/T2/T3 mean width for change
    transport with the AW-1/AW-2 ratio annotations.

Run:  python -m pcb.figures.fig_lapop_change   (after e17_lapop_change_transport)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd

BLUE, AQUA, YELLOW = "#2a78d6", "#1baf7a", "#eda100"
RED, MUTED2 = "#e34948", "#8a897f"
TEXT, MUTED, GRID = "#1a1a19", "#6b6a63", "#e5e4dd"
LAB = {"b13": "Trust in\nlegislature", "sat": "Satisfaction\nw/ democracy",
       "ing4": "Support for\ndemocracy"}


def _ax(ax):
    ax.set_facecolor("#fcfcfb")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)


def fig_rho(level, change):
    outs = list(LAB)
    fig, ax = plt.subplots(figsize=(7.4, 3.9), facecolor="#fcfcfb")
    _ax(ax)
    x = np.arange(len(outs)); w = 0.34
    lv = [level[level.outcome == o].rho.mean() for o in outs]
    ch = [change[change.outcome == o].rho.mean() for o in outs]
    ax.bar(x - w / 2, lv, w, color=AQUA, edgecolor="#fcfcfb", linewidth=1.4,
           label="level transport (Part B)")
    ax.bar(x + w / 2, ch, w, color=BLUE, edgecolor="#fcfcfb", linewidth=1.4,
           label="change transport (Part C)")
    for xi, (a, b) in enumerate(zip(lv, ch)):
        ax.text(xi - w / 2, a + 0.008, f"{a:.2f}", ha="center", fontsize=8, color=TEXT)
        ax.text(xi + w / 2, b + 0.008, f"{b:.2f}", ha="center", fontsize=8,
                color=TEXT, fontweight="bold")
    ax.axhline(0.47, color=RED, lw=1.8)
    ax.text(len(outs) - 0.5, 0.47 + 0.01, "ρ₀ = 0.47 fallback cutoff — never reached",
            ha="right", fontsize=8.5, color=RED, fontweight="bold")
    ax.set_ylim(0, 0.55)
    ax.set_xticks(x); ax.set_xticklabels([LAB[o] for o in outs], fontsize=8.5,
                                         color=TEXT)
    ax.set_ylabel("ρ̂ = design SD / transport SD", fontsize=9, color=TEXT)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left", labelcolor=TEXT)
    ax.set_title("Transporting CHANGE curves raises ρ (~1.5×) but both estimands "
                 "stay\nlow-ρ — real cross-national inference never reaches the "
                 "deconvolution regime", fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/lapop_level_vs_change_rho.png", dpi=200)
    plt.close(fig)


def fig_width(change):
    outs = list(LAB)
    fig, ax = plt.subplots(figsize=(7.4, 3.9), facecolor="#fcfcfb")
    _ax(ax)
    x = np.arange(len(outs)); w = 0.26
    for i, (col, key, lab) in enumerate((
            (MUTED2, "w_T1", "T1 clustered PCB"),
            (YELLOW, "w_T2", "T2 worst-case"),
            (BLUE, "w_T3", "T3 Candidate B"))):
        vals = [change[change.outcome == o][key].mean() for o in outs]
        ax.bar(x + (i - 1) * w, vals, w, color=col, edgecolor="#fcfcfb",
               linewidth=1.4, label=lab)
    top = change.w_T2.max()
    ax.set_ylim(0, top * 1.4)
    for xi, o in enumerate(outs):
        p = change[change.outcome == o]
        ax.text(xi + w, p.w_T3.mean() + top * 0.03,
                f"T3/T1 {p.ratio_T3_T1.mean():.2f}\nT3/T2 {p.ratio_T3_T2.mean():.2f}",
                ha="center", fontsize=7.5, color=TEXT)
    ax.set_xticks(x); ax.set_xticklabels([LAB[o] for o in outs], fontsize=8.5,
                                         color=TEXT)
    ax.set_ylabel("mean band half-width (change transport)", fontsize=9, color=TEXT)
    ax.legend(fontsize=8, frameon=False, loc="upper left", labelcolor=TEXT)
    ax.set_title("Change-transport widths match the adaptive-width theory: "
                 "T3/T1≈1−½ρ²\n(AW-1), T3/T2<1 conservative dominance (AW-2)",
                 fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/lapop_change_width_by_method.png", dpi=200)
    plt.close(fig)


def main():
    level = pd.read_csv("results/lapop_transport_loco.csv")
    change = pd.read_csv("results/lapop_change_transport.csv")
    fig_rho(level, change)
    fig_width(change)
    print("wrote figures/lapop_level_vs_change_rho.png, "
          "figures/lapop_change_width_by_method.png")


if __name__ == "__main__":
    main()
