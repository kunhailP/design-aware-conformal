"""Certified-core figures: the co-certification matrix of the WVS reanalysis.

Two outputs after E30:
  paper/figures/certified_core.{pdf,png}       MAIN: the 13-country certified
      core (>= 2 items) only, grayscale cells (filled = certified), a region
      abbreviation column and an item count column. The substantive claim is
      which country x item certifies; geography is secondary annotation.
  paper/figures/certified_core_full.{pdf,png}  SUPPLEMENT: all countries
      certifying >= 1 item, with the regional color coding.

Run:  python -m pcb.figures.fig_certified_core   (after e30_certified_core)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
from pcb.figures.style import (use as _style_use, BLACK, DARK_GRAY, MID_GRAY,
                               GRID_GRAY)
_style_use()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TEXT, MUTED = "#1a1a19", "#6b6a63"
FILL = {"post-communist": "#0072B2",
        "MENA / Arab-Spring aftermath": "#E69F00",
        "Latin America & Caribbean": "#56B4E9",
        "Sub-Saharan Africa": "#8d5fd3",
        "Consolidated West": "#d6452a",
        "Asia": "#008394", "other": "#6b6a63"}
ABBR = {"post-communist": "PC",
        "MENA / Arab-Spring aftermath": "MENA",
        "Latin America & Caribbean": "LAC",
        "Sub-Saharan Africa": "SSA",
        "Consolidated West": "West",
        "Asia": "Asia", "other": "--"}
ITEMS = ["imp_dem", "rej_leader", "rej_army", "sup_demsys", "confid_parl"]
ITEM_LABELS = ["democracy\nessential", "reject strong\nleader",
               "reject army\nrule", "democratic\nsystem",
               "confidence in\nparliament"]


def _core(df):
    """MAIN: 13 x 5 grayscale matrix with region and count columns."""
    d = df[df.core].sort_values(["n_items", "country"],
                                ascending=[False, True]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(5.0, 3.7), facecolor="white")
    ax.grid(False)
    for y, (_, r) in enumerate(d.iterrows()):
        have = set(str(r["items"]).split(";"))
        for x, item in enumerate(ITEMS):
            filled = item in have
            ax.add_patch(plt.Rectangle((x - 0.38, y - 0.36), 0.76, 0.72,
                                       facecolor=BLACK if filled else "white",
                                       edgecolor=MID_GRAY, lw=0.6, zorder=2))
        ax.text(len(ITEMS) - 0.25, y, str(int(r.n_items)), va="center",
                ha="center", fontsize=8.5, color=BLACK, fontweight="bold")
        ax.text(len(ITEMS) + 0.55, y, ABBR.get(r.group, "--"), va="center",
                ha="left", fontsize=7.5, color=DARK_GRAY)
    ax.text(len(ITEMS) - 0.25, -0.95, "# items", ha="center", fontsize=7.5,
            color=DARK_GRAY, style="italic")
    ax.text(len(ITEMS) + 0.55, -0.95, "region", ha="left", fontsize=7.5,
            color=DARK_GRAY, style="italic")
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(d.country, fontsize=8.5, color=BLACK)
    ax.set_xticks(range(len(ITEMS)))
    ax.set_xticklabels(["democracy essential", "reject strong leader",
                        "reject army rule", "democratic system",
                        "confidence in parliament"], fontsize=7.5,
                       color=BLACK, rotation=30, ha="left")
    ax.tick_params(axis="x", labeltop=True, labelbottom=False)
    ax.invert_yaxis()
    ax.set_xlim(-0.6, len(ITEMS) + 1.5)
    ax.set_ylim(len(d) - 0.4, -1.6)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(length=0)
    fig.tight_layout()
    fig.savefig("paper/figures/certified_core.png", dpi=300,
                bbox_inches="tight")
    fig.savefig("paper/figures/certified_core.pdf", bbox_inches="tight")
    plt.close(fig)


def _full(df):
    """SUPPLEMENT: every country certifying >= 1 item, regional colors."""
    d = df.sort_values(["n_items", "country"],
                       ascending=[False, True]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(6.4, 8.2), facecolor="white")
    for y, (_, r) in enumerate(d.iterrows()):
        have = set(str(r["items"]).split(";"))
        for x, item in enumerate(ITEMS):
            if item in have:
                ax.scatter(x, y, s=110, marker="s",
                           color=FILL.get(r.group, MUTED), zorder=3)
            else:
                ax.scatter(x, y, s=110, marker="s", facecolors="none",
                           edgecolors=GRID_GRAY, linewidths=0.8, zorder=2)
    n_core = int(d.core.sum())
    ax.axhline(n_core - 0.5, color=TEXT, lw=0.8, ls=(0, (4, 3)))
    ax.text(len(ITEMS) - 0.4, n_core - 0.5, " certified core\n (≥2 items)",
            va="center", fontsize=8.5, color=TEXT)
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(d.country, fontsize=8)
    for lab, (_, r) in zip(ax.get_yticklabels(), d.iterrows()):
        lab.set_color(FILL.get(r.group, MUTED))
    ax.set_xticks(range(len(ITEMS)))
    ax.set_xticklabels(ITEM_LABELS, fontsize=8, color=TEXT)
    ax.invert_yaxis()
    ax.set_xlim(-0.6, len(ITEMS) + 1.6)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(length=0)
    handles = [plt.Line2D([], [], marker="s", ls="", color=c, label=g)
               for g, c in FILL.items() if g != "other"]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig("paper/figures/certified_core_full.png", dpi=300,
                bbox_inches="tight")
    fig.savefig("paper/figures/certified_core_full.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    df = pd.read_csv("results/certified_core.csv")
    _core(df)
    _full(df)
    print("wrote paper/figures/certified_core.pdf (main, 13-core) and "
          "certified_core_full.pdf (supplement, all countries)")


if __name__ == "__main__":
    main()
