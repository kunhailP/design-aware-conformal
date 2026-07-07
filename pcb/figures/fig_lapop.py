"""Gate-5D LAPOP external-validation figures.

figures/lapop_external_reproduction.png : M0 plug-in vs survey-aware (M3 proper)
    pair-level certification per outcome — the ESS over-certification mechanism
    reproduced in a different survey family.
figures/lapop_design_effect.png : distribution of the design-effect ratio
    deff½ = SD_M3/SD_M2 (proper/naive), showing the real clustering LAPOP has and
    ESS lacked, split high/low regime.

Run:  python -m pcb.figures.fig_lapop   (after e15_lapop_certify)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BLUE, AQUA, YELLOW, GREEN = "#2a78d6", "#1baf7a", "#eda100", "#008300"
RED = "#e34948"
TEXT, MUTED, GRID = "#1a1a19", "#6b6a63", "#e5e4dd"
LABELS = {"b13": "Trust in legislature", "sat": "Satisfaction w/ democracy",
          "ing4": "Support for democracy"}


def _ax(ax):
    ax.set_facecolor("#fcfcfb")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)


def fig_repro(pair):
    outs = list(LABELS)
    fig, ax = plt.subplots(figsize=(7.6, 3.8), facecolor="#fcfcfb")
    _ax(ax)
    x = np.arange(len(outs)); w = 0.26
    for i, (m, col, lab) in enumerate((
            ("M0", YELLOW, "M0 plug-in (no uncertainty)"),
            ("M2", AQUA, "M2 naive survey band"),
            ("M3", BLUE, "M3 proper design band"))):
        vals = [int(pair[pair.outcome == o][m].sum()) for o in outs]
        bars = ax.bar(x + (i - 1) * w, vals, w, color=col, edgecolor="#fcfcfb",
                      linewidth=1.4, label=lab)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.6, str(v), ha="center",
                    fontsize=8.5, color=TEXT, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([LABELS[o] for o in outs], fontsize=9,
                                         color=TEXT)
    ax.set_ylabel("pairs with certified decline\n(of ~125)", fontsize=9, color=TEXT)
    ax.legend(fontsize=8, frameon=False, loc="upper right", labelcolor=TEXT)
    ax.set_title("AmericasBarometer reproduces the ESS mechanism: accounting for "
                 "survey\nuncertainty roughly halves certifications (M0→survey-aware)",
                 fontsize=10, color=TEXT, loc="left")
    fig.tight_layout()
    fig.savefig("figures/lapop_external_reproduction.png", dpi=200)
    plt.close(fig)


def fig_deff(pair):
    fig, ax = plt.subplots(figsize=(7.2, 3.8), facecolor="#fcfcfb")
    _ax(ax)
    p = pair.dropna(subset=["deff_ratio"])
    bins = np.linspace(0.85, 2.0, 26)
    ax.hist(p.deff_ratio, bins=bins, color=BLUE, edgecolor="#fcfcfb", linewidth=0.6)
    ax.axvline(1.0, color=MUTED, lw=1.4, ls="--")
    ax.text(1.005, ax.get_ylim()[1] * 0.92, "naive = proper\n(no design effect, ESS regime)",
            fontsize=8, color=MUTED, va="top")
    med = p.deff_ratio.median()
    ax.axvline(med, color=RED, lw=1.6)
    ax.text(med + 0.01, ax.get_ylim()[1] * 0.66,
            f"median {med:.2f}\n(proper band ~{int((med-1)*100)}% wider)",
            fontsize=8.5, color=RED, va="top", fontweight="bold")
    ax.set_xlabel("design-effect ratio  deff½ = SD(proper PSU) / SD(naive)",
                  fontsize=9, color=TEXT)
    ax.set_ylabel("country-year pairs", fontsize=9, color=TEXT)
    ax.set_title("LAPOP has the real clustering design effect ESS lacked — the\n"
                 "proper stratified-PSU band is materially wider (up to ~1.9×)",
                 fontsize=10, color=TEXT, loc="left")
    fig.tight_layout()
    fig.savefig("figures/lapop_design_effect.png", dpi=200)
    plt.close(fig)


def main():
    pair = pd.read_csv("results/lapop_decline_certification.csv")
    fig_repro(pair)
    fig_deff(pair)
    print("wrote figures/lapop_external_reproduction.png, "
          "figures/lapop_design_effect.png")


if __name__ == "__main__":
    main()
