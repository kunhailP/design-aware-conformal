"""Figure 4 — where the surviving deconsolidation lives, and how strongly.

  A  what the stricter claim does, per battery item: country counts from the
     marginal wave-pair reading to persistent plug-in to persistent
     design-aware (the 2.6-6.5x and 1.9-4.8x decompositions, drawn).
  B  world geography: countries shaded by number of certified items; the
     13-country core outlined.
  C  the core, magnitude-aware: circle area = certified minimum decline
     (the persistent band's simultaneous lower bound, e59), so the matrix
     reports evidence strength, not just membership.

Reads results/wvs_deconsolidation.csv, certified_core.csv,
      wvs_core_magnitudes.csv, assets/ne_110m_countries.geojson.
Writes paper/figures/certified_core.{pdf,png} (main) and keeps
       certified_core_full.{pdf,png} (supplement) unchanged.
Run:  python -m pcb.figures.fig_certified_core
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
from pcb.figures.style import (use as _style_use, BLACK, DARK_GRAY, MID_GRAY,
                               GRID_GRAY, NAVY, TEAL, RUST, AMBER, NEUTRAL,
                               OFFWHITE)
_style_use()
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd

ITEMS = ["imp_dem", "rej_leader", "rej_army", "sup_demsys", "confid_parl"]
ITEM_SHORT = ["democracy\nessential", "reject strong\nleader",
              "reject army\nrule", "democratic\nsystem",
              "confidence in\nparliament"]
SEQ = ["#DDDBD3", "#B9C7CE", "#7FA3B5", "#41758F", "#2B4C7E"]  # 0..4 items


def _deframe(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(DARK_GRAY)
    ax.tick_params(colors=DARK_GRAY, labelsize=7)


def panel_a(ax, w):
    stages = ["marginal\nwave-pair", "persistent\nplug-in",
              "persistent\ndesign-aware"]
    xs = np.arange(3)
    rows = list(w.iterrows())
    finals = sorted(range(len(rows)), key=lambda i: rows[i][1].persist)
    dodge = {}
    last = None
    for rank, i in enumerate(finals):
        y = rows[i][1].persist
        dodge[i] = 0.0
        if last is not None and abs(y - last[0]) < 2.6:
            dodge[i] = last[1] + 2.6 - (y - last[0])
        last = (y, dodge[i])
    for i, (_, r) in enumerate(rows):
        ys = [r.anypair_plugin, r.persist_plugin, r.persist]
        ax.plot(xs, ys, "-", color=MID_GRAY, lw=0.9, zorder=2)
        ax.plot(xs, ys, "o", ms=3.4, color=NAVY, zorder=3)
        ax.annotate(r["item_label"], (2, ys[-1] + dodge[i]),
                    textcoords="offset points", xytext=(5, -2), fontsize=5.8,
                    color=DARK_GRAY)
    _deframe(ax)
    ax.set_xticks(xs)
    ax.set_xticklabels(stages, fontsize=6.4, color=BLACK)
    ax.set_ylabel("countries certified", fontsize=7, color=BLACK)
    ax.set_xlim(-0.25, 2.9)
    ax.grid(axis="y", color=GRID_GRAY, lw=0.4)
    ax.set_axisbelow(True)


def panel_b(ax, core):
    gj = json.load(open(os.path.join(os.path.dirname(__file__), "assets",
                                     "ne_110m_countries.geojson")))
    n_by_iso = dict(zip(core.iso.astype(int), core.n_items.astype(int)))
    core_iso = set(core[core.core].iso.astype(int))
    polys, cols, edges, lws = [], [], [], []
    for f in gj["features"]:
        try:
            iso = int(f["properties"].get("ISO_N3") or -1)
        except ValueError:
            iso = -1
        n = n_by_iso.get(iso, 0)
        geom = f["geometry"]
        rings = ([geom["coordinates"]] if geom["type"] == "Polygon"
                 else geom["coordinates"])
        for poly in rings:
            polys.append(np.asarray(poly[0]))
            cols.append(SEQ[min(n, 4)])
            edges.append(NAVY if iso in core_iso else "white")
            lws.append(0.9 if iso in core_iso else 0.25)
    ax.add_collection(PolyCollection(polys, facecolors=cols,
                                     edgecolors=edges, linewidths=lws))
    ax.set_xlim(-168, 180)
    ax.set_ylim(-58, 84)
    ax.set_aspect(1.25)
    ax.axis("off")
    # sequential legend
    for i, c in enumerate(SEQ):
        ax.add_patch(plt.Rectangle((-165 + i * 13, -52), 12, 7,
                                   facecolor=c, edgecolor=DARK_GRAY, lw=0.3))
    ax.text(-165, -42, "certified items 0 – 4", fontsize=6.0, color=DARK_GRAY)
    ax.text(-165 + 5 * 13 + 6, -50, "— core outline", fontsize=6.0,
            color=NAVY)


def panel_c(ax, core, mags):
    d = core[core.core].sort_values(["n_items", "country"],
                                    ascending=[False, True]).reset_index(drop=True)
    mag = {(int(r.iso), r["item"]): r.magnitude_lb
           for _, r in mags[mags.certified].iterrows()}
    scale = 950.0
    for y, (_, r) in enumerate(d.iterrows()):
        for x, item in enumerate(ITEMS):
            m = mag.get((int(r.iso), item))
            if m is not None:
                ax.scatter(x, y, s=max(22, scale * m), color=TEAL,
                           alpha=0.9, zorder=3, edgecolors="white", lw=0.5)
            else:
                ax.scatter(x, y, s=8, color=GRID_GRAY, zorder=2)
        ax.text(len(ITEMS) - 0.35, y, str(int(r.n_items)), va="center",
                ha="center", fontsize=7.4, color=BLACK, fontweight="bold")
    ax.text(len(ITEMS) - 0.35, -1.0, "# items", ha="center", fontsize=6.4,
            color=DARK_GRAY, style="italic")
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(d.country, fontsize=7.2, color=BLACK)
    ax.set_xticks(range(len(ITEMS)))
    ax.set_xticklabels(ITEM_SHORT, fontsize=6.2, color=BLACK)
    ax.tick_params(axis="x", labeltop=True, labelbottom=False, length=0)
    ax.tick_params(axis="y", length=0)
    ax.invert_yaxis()
    ax.set_xlim(-0.6, len(ITEMS) + 0.35)
    ax.set_ylim(len(d) + 1.1, -1.55)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.grid(False)
    # size key: horizontal, below the matrix
    ky = len(d) + 0.55
    ax.text(-0.45, ky, "certified decline (CDF pts):", fontsize=6.2,
            color=DARK_GRAY, va="center", ha="left", clip_on=False)
    for i, m in enumerate([0.02, 0.10, 0.30]):
        kx = 2.15 + i * 0.75
        ax.scatter(kx, ky, s=max(22, scale * m), color=TEAL, alpha=0.9,
                   edgecolors="white", lw=0.5, clip_on=False)
        ax.text(kx + 0.22, ky, f"{m:g}", fontsize=6.2, color=DARK_GRAY,
                va="center", clip_on=False)


def main():
    w = pd.read_csv("results/wvs_deconsolidation.csv")
    w["item_label"] = ["democracy", "strong leader", "army rule",
                       "dem. system", "parliament"][:len(w)]
    core = pd.read_csv("results/certified_core.csv")
    mags = pd.read_csv("results/wvs_core_magnitudes.csv")

    fig = plt.figure(figsize=(5.5, 6.3), facecolor="white")
    gs = GridSpec(2, 2, width_ratios=[1.0, 1.55], height_ratios=[1.0, 1.55],
                  hspace=0.38, wspace=0.18)
    axA = fig.add_subplot(gs[0, 0])
    axB = fig.add_subplot(gs[0, 1])
    axC = fig.add_subplot(gs[1, :])

    panel_a(axA, w)
    panel_b(axB, core)
    panel_c(axC, core, mags)
    axA.set_title("A.  The claim discipline, per item", fontsize=8,
                  color=BLACK, loc="left")
    axB.set_title("B.  Where certification concentrates", fontsize=8,
                  color=BLACK, loc="left")
    axC.set_title("C.  The certified core, by evidence strength", fontsize=8,
                  color=BLACK, loc="left")
    fig.savefig("paper/figures/certified_core.pdf", bbox_inches="tight")
    fig.savefig("paper/figures/certified_core.png", dpi=300,
                bbox_inches="tight")
    print("wrote paper/figures/certified_core.pdf")


if __name__ == "__main__":
    main()
