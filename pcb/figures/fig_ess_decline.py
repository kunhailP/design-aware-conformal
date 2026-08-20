"""Gate-5D figures: plug-in vs design-aware trust-decline certification on ESS.

figures/plug_in_vs_design_aware_certification.png : country-level certified-
    decline counts by method, both outcomes — the N-vs-M over-certification gap.
figures/country_reclassification_map.png : among plug-in-certified pairs, signal
    vs design SD, colored by whether design-awareness keeps or reclassifies —
    shows the reclassified pairs are the weak-signal / high-noise ones.

Run:  python -m pcb.figures.fig_ess_decline   (after e12_ess_decline)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
from pcb.figures.style import use as _style_use
_style_use()
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd

BLUE, AQUA, YELLOW, GREEN = "#0072B2", "#56B4E9", "#E69F00", "#009E73"
RED = "#D55E00"
TEXT, MUTED, GRID = "#1a1a19", "#6b6a63", "#e5e4dd"
METH = [("M0_plugin", "M0 plug-in\n(no uncertainty)", YELLOW),
        ("M1_naive", "M1 naive boot\n(no clustering)", AQUA),
        ("M2_level", "M2 level band\n(non-overlap)", MUTED),
        ("M4_design", "M4 design-aware\n(difference band)", BLUE)]


def _ax(ax):
    ax.set_facecolor("#fcfcfb")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)


def fig_counts(pair):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), facecolor="#fcfcfb")
    for ax, outcome, title in zip(axes, ("trstprl", "stfdem"),
                                  ("Trust in parliament", "Satisfaction w/ democracy")):
        _ax(ax)
        cty = pair[pair.outcome == outcome].groupby("cntry")[
            [m for m, _, _ in METH]].max()
        vals = [int(cty[m].sum()) for m, _, _ in METH]
        cols = [c for _, _, c in METH]
        bars = ax.bar(range(4), vals, color=cols, width=0.66,
                      edgecolor="#fcfcfb", linewidth=1.5)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.3, str(v),
                    ha="center", fontsize=10, color=TEXT, fontweight="bold")
        ax.set_xticks(range(4))
        ax.set_xticklabels([lab for _, lab, _ in METH], fontsize=7.5, color=TEXT)
        ax.set_title(title, fontsize=10, color=TEXT)
        ax.set_ylim(0, max(vals) + 3)
    axes[0].set_ylabel("countries with certified\nnet trust decline",
                       fontsize=9, color=TEXT)
    fig.suptitle("Standard analysis over-certifies trust decline; "
                 "design-aware certification is stricter and valid",
                 fontsize=11, color=TEXT, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/plug_in_vs_design_aware_certification.png", dpi=300, bbox_inches="tight"); fig.savefig("figures/plug_in_vs_design_aware_certification.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_reclass(pair):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True,
                             facecolor="#fcfcfb")
    for ax, outcome, title in zip(axes, ("trstprl", "stfdem"),
                                  ("Trust in parliament", "Satisfaction w/ democracy")):
        _ax(ax)
        p = pair[(pair.outcome == outcome) & (pair.M0_plugin == 1)].copy()
        p["kept"] = p.M4_design == 1
        for keep, col, lab in ((True, BLUE, "kept by design-aware"),
                               (False, RED, "reclassified → inconclusive")):
            q = p[p.kept == keep]
            ax.scatter(q.design_sd, q.signal, s=46, c=col, edgecolor="#fcfcfb",
                       linewidth=0.8, label=lab, zorder=3)
        ax.set_xlabel("design SD of the difference (survey noise)",
                      fontsize=8.5, color=TEXT)
        ax.set_title(title, fontsize=10, color=TEXT)
    axes[0].set_ylabel("low-trust decline signal\n(mean ΔF over core)",
                       fontsize=9, color=TEXT)
    axes[0].legend(fontsize=7.5, frameon=False, loc="upper right",
                   labelcolor=TEXT)
    fig.suptitle("Design-awareness reclassifies the weak-signal / high-noise "
                 "declines, keeps the strong ones",
                 fontsize=11, color=TEXT, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/country_reclassification_map.png", dpi=300, bbox_inches="tight"); fig.savefig("figures/country_reclassification_map.pdf", bbox_inches="tight")
    plt.close(fig)


def _dumbbell(ax, levels, title, xmax, joint=False, legend=False):
    """One row per claim; within a row, plug-in (open gray) and design-aware
    (filled black) joined by a light connector. Rows are NOT joined: the claim
    family is a partial order, not a chain, so a line across claims would
    draw an ordering the mathematics does not assert. The connector's meaning
    is the count shift when survey uncertainty enters."""
    from pcb.figures.style import (BLACK, MID_GRAY, LIGHT_GRAY, GRID_GRAY,
                                   DARK_GRAY)
    ax.set_facecolor("white")
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(DARK_GRAY)
    ax.tick_params(colors=DARK_GRAY, labelsize=8, length=0)
    ax.grid(axis="x", color=GRID_GRAY, lw=0.45)
    ax.set_axisbelow(True)
    ys = np.arange(len(levels))[::-1]
    for y, (lab, plug, da) in zip(ys, levels):
        if not joint:
            ax.plot([da, plug], [y, y], "-", color=LIGHT_GRAY, lw=1.6,
                    zorder=1)
            ax.plot([plug], [y], "o", ms=6, mfc="white", mec=MID_GRAY,
                    mew=1.2, zorder=2)
            ax.annotate(str(int(plug)), (plug, y), textcoords="offset points",
                        xytext=(2, 7), fontsize=8, color=MID_GRAY,
                        ha="center")
        ax.plot([da], [y], "o", ms=6, mfc=BLACK, mec=BLACK, zorder=3)
        ax.annotate(str(int(da)), (da, y), textcoords="offset points",
                    xytext=(-2, 7), fontsize=8, color=BLACK,
                    fontweight="bold", ha="center")
    ax.set_yticks(ys)
    ax.set_yticklabels([l[0] for l in levels], fontsize=8.5, color=BLACK)
    ax.set_ylim(-0.6, len(levels) - 0.15)
    ax.set_xlim(-0.8, xmax)
    ax.set_title(title, fontsize=8.5, color=BLACK, loc="left")
    if legend:
        from matplotlib.lines import Line2D
        ax.legend(handles=[
            Line2D([], [], marker="o", ls="", mfc=BLACK, mec=BLACK,
                   label="design-aware"),
            Line2D([], [], marker="o", ls="", mfc="white", mec=MID_GRAY,
                   label="plug-in")],
            fontsize=7.5, frameon=False, loc="upper left", labelcolor=BLACK,
            handletextpad=0.2, borderaxespad=0.1)


def _levels(p):
    """The claims of Section 7, top of the partial order last."""
    return [("any adjacent pair", int(p.any_plugin.sum()), int(p.any_da.sum())),
            ("net first-to-last", int(p.net_plugin.sum()), int(p.net_da.sum())),
            ("persistent", int(p.persist_plugin.sum()),
             int(p.persist_da.sum()))]


def fig_hierarchy(cty):
    """Claim-family dumbbells (trstprl): rounds 9-11 beside the full record
    read off one joint band; generated at manuscript print width."""
    p = cty[cty.outcome == "trstprl"]
    panels = [("A.  Rounds 9\u201311 (2018\u201324), $K=30$", _levels(p), False)]
    try:
        jc = pd.read_csv("results/ess_joint_claims.csv")
        q = jc[jc.outcome == "trstprl"]
        panels.append((f"B.  Full record, one joint band ($K={len(q)}$)",
                       [("any adjacent pair", int(q.any_pair.sum()),
                         int(q.any_pair.sum())),
                        ("net first-to-last", int(q.net.sum()), int(q.net.sum())),
                        ("persistent", int(q.persistent.sum()),
                         int(q.persistent.sum()))], True))
    except FileNotFoundError:
        pass
    xmax = max(v for _, lv, _ in panels for l in lv for v in l[1:]) + 3.5
    fig, axes = plt.subplots(1, len(panels), sharex=True,
                             figsize=(5.5, 2.4), facecolor="white")
    axes = np.atleast_1d(axes)
    for i, (ax, (title, levels, joint)) in enumerate(zip(axes, panels)):
        _dumbbell(ax, levels, title, xmax, joint=joint,
                  legend=(i == len(panels) - 1))
        if i:
            ax.set_yticklabels([])
    axes[0].set_xlabel("countries certified", fontsize=8.5, color="#222222")
    axes[-1].set_xlabel("countries certified", fontsize=8.5, color="#222222")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True)
    fig.savefig("figures/guarantee_hierarchy.png", dpi=300,
                bbox_inches="tight")
    fig.savefig("figures/guarantee_hierarchy.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    pair = pd.read_csv("results/ess_design_aware_decline.csv")
    fig_counts(pair)
    fig_reclass(pair)
    print("wrote figures/plug_in_vs_design_aware_certification.png, "
          "figures/country_reclassification_map.png, "
          "figures/guarantee_hierarchy.png")


if __name__ == "__main__":
    main()
