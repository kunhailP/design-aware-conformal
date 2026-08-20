"""Certified-core figure: the co-certification matrix of the WVS reanalysis.

paper/figures/certified_core.png : countries (rows, sorted by number of
    certified items) x the five deconsolidation battery items (columns); a
    filled cell means the persistent, distribution-wide, weights-aware decline
    is certified for that country-item (E26). The left block is the certified
    core (>= 2 items); consolidated-West countries are marked to show how thin
    their presence is, and on which items it occurs.

Run:  python -m pcb.figures.fig_certified_core   (after e30_certified_core)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
from pcb.figures.style import use as _style_use
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
ITEMS = ["imp_dem", "rej_leader", "rej_army", "sup_demsys", "confid_parl"]
ITEM_LABELS = ["democracy\nessential", "reject strong\nleader", "reject army\nrule",
               "democratic\nsystem", "confidence in\nparliament"]


def main():
    df = pd.read_csv("results/certified_core.csv")
    df = df.sort_values(["n_items", "country"], ascending=[False, True])
    fig, ax = plt.subplots(figsize=(8.6, 9.2), facecolor="#fcfcfb")
    for y, (_, r) in enumerate(df.iterrows()):
        have = set(str(r["items"]).split(";"))
        for x, item in enumerate(ITEMS):
            if item in have:
                ax.scatter(x, y, s=150, marker="s",
                           color=FILL.get(r.group, MUTED), zorder=3)
            else:
                ax.scatter(x, y, s=150, marker="s", facecolors="none",
                           edgecolors="#dddcd6", linewidths=0.8, zorder=2)
    n_core = int(df.core.sum())
    ax.axhline(n_core - 0.5, color=TEXT, lw=0.8, ls=(0, (4, 3)))
    ax.text(len(ITEMS) - 0.4, n_core - 0.5, " certified core\n (≥2 items)",
            va="center", fontsize=9, color=TEXT)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df.country, fontsize=9,
                       color=TEXT)
    for lab, (_, r) in zip(ax.get_yticklabels(), df.iterrows()):
        lab.set_color(FILL.get(r.group, MUTED))
    ax.set_xticks(range(len(ITEMS)))
    ax.set_xticklabels(ITEM_LABELS, fontsize=9, color=TEXT)
    ax.invert_yaxis()
    ax.set_xlim(-0.6, len(ITEMS) + 1.6)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(length=0)
    handles = [plt.Line2D([], [], marker="s", ls="", color=c, label=g)
               for g, c in FILL.items() if g != "other"]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8.5)
    ax.set_title("Persistent distribution-wide deconsolidation, certified per item\n"
                 "(WVS/EVS 1981–2022; weights-aware simultaneous bands)",
                 fontsize=11, color=TEXT, loc="left")
    fig.tight_layout()
    fig.savefig("paper/figures/certified_core.png", dpi=300, bbox_inches="tight"); fig.savefig("paper/figures/certified_core.pdf", bbox_inches="tight")
    print("wrote paper/figures/certified_core.png")


if __name__ == "__main__":
    main()
