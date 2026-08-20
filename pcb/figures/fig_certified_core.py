"""Figure 4 (APSR grammar) — the certified core, magnitude-aware.

MAIN  paper/figures/certified_core.{pdf,png}: the 13-country core (>=2 of
      five battery items), circle AREA = the persistent band's simultaneous
      lower bound on the per-pair decline (e59), so the matrix reports
      evidence strength, not membership alone. Black ink only.
SUPP  paper/figures/certified_core_full.{pdf,png}: all countries certifying
      >=1 item, regional color coding (unchanged from the original figure).

Run:  python -m pcb.figures.fig_certified_core   (after e30, e59)
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
from pcb.figures.style import (use as _style_use, apsr, apsr_box, INK, GR1,
                               GR2, GR3)
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
LBL = ["Democracy\nessential", "Reject\nstrong leader", "Reject\narmy rule",
       "Democratic\nsystem", "Confidence\nin parliament"]


def _core_mag():
    apsr()
    core = pd.read_csv("results/certified_core.csv")
    mags = pd.read_csv("results/wvs_core_magnitudes.csv")
    mag = {(int(r.iso), r["item"]): r.magnitude_lb
           for _, r in mags[mags.certified.astype(bool)].iterrows()}
    d = core[core.core].sort_values(["n_items", "country"],
                                    ascending=[False, True]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(5.8, 4.1))
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, labelsize=8.3)
    ax.grid(False)
    scale = 620.0
    for y, (_, r) in enumerate(d.iterrows()):
        for x, it in enumerate(ITEMS):
            m = mag.get((int(r.iso), it))
            if m is not None:
                ax.scatter(x, y, s=max(14, scale * m), color=INK, zorder=3)
            else:
                ax.scatter(x, y, s=7, facecolors="white", edgecolors=GR2,
                           lw=0.6, zorder=2)
        ax.text(5.0, y, str(int(r.n_items)), va="center", ha="center",
                fontsize=8.3)
    ax.text(5.0, -1.02, "Items", ha="center", fontsize=8, style="italic",
            color=GR1)
    # size key, horizontal beneath the matrix
    ky = len(d) + 0.75
    ax.text(-0.42, ky, "Certified minimum decline (CDF points):",
            fontsize=8, color=GR1, va="center", ha="left")
    for i, m in enumerate([0.02, 0.10, 0.30]):
        kx = 3.42 + i * 0.72
        ax.scatter(kx, ky, s=max(14, scale * m), color=INK, clip_on=False)
        ax.text(kx + 0.21, ky, f"{m:g}", fontsize=8, color=GR1, va="center")
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(d.country, fontsize=8.3)
    ax.set_xticks(range(5))
    ax.set_xticklabels(LBL, fontsize=7.3)
    ax.tick_params(axis="x", labeltop=True, labelbottom=False)
    ax.invert_yaxis()
    ax.set_xlim(-0.6, 5.45)
    ax.set_ylim(len(d) + 1.35, -1.65)
    fig.tight_layout()
    fig.savefig("paper/figures/certified_core.pdf", bbox_inches="tight")
    fig.savefig("paper/figures/certified_core.png", dpi=300,
                bbox_inches="tight")
    plt.close(fig)


def _full():
    df = pd.read_csv("results/certified_core.csv")
    d = df.sort_values(["n_items", "country"],
                       ascending=[False, True]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(6.4, 8.4), facecolor="#fcfcfb")
    for y, (_, r) in enumerate(d.iterrows()):
        have = set(str(r["items"]).split(";"))
        for x, item in enumerate(ITEMS):
            if item in have:
                ax.scatter(x, y, s=110, marker="s",
                           color=FILL.get(r.group, MUTED), zorder=3)
            else:
                ax.scatter(x, y, s=110, marker="s", facecolors="none",
                           edgecolors="#dddcd6", linewidths=0.8, zorder=2)
    n_core = int(d.core.sum())
    ax.axhline(n_core - 0.5, color=TEXT, lw=0.8, ls=(0, (4, 3)))
    ax.text(len(ITEMS) - 0.4, n_core - 0.5, " certified core\n (≥2 items)",
            va="center", fontsize=8.5, color=TEXT)
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(d.country, fontsize=8)
    for lab, (_, r) in zip(ax.get_yticklabels(), d.iterrows()):
        lab.set_color(FILL.get(r.group, MUTED))
    ax.set_xticks(range(len(ITEMS)))
    ax.set_xticklabels(LBL, fontsize=8, color=TEXT)
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
    _core_mag()
    _full()
    print("wrote paper/figures/certified_core.pdf (main) and "
          "certified_core_full.pdf (supplement)")


if __name__ == "__main__":
    main()
