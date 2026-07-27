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
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd

BLUE, AQUA, YELLOW, GREEN = "#2a78d6", "#1baf7a", "#eda100", "#008300"
RED = "#e34948"
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
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/plug_in_vs_design_aware_certification.png", dpi=200)
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
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/country_reclassification_map.png", dpi=200)
    plt.close(fig)


def _funnel(ax, levels, title, legend=False, ylabel=False):
    _ax(ax)
    x = np.arange(len(levels)); w = 0.38
    plug = [l[1] for l in levels]; da = [l[2] for l in levels]
    b1 = ax.bar(x - w / 2, plug, w, color=YELLOW, edgecolor="#fcfcfb",
                linewidth=1.5, label="plug-in (no survey uncertainty)")
    b2 = ax.bar(x + w / 2, da, w, color=BLUE, edgecolor="#fcfcfb",
                linewidth=1.5, label="design-aware")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.25,
                    str(int(b.get_height())), ha="center", fontsize=9.5,
                    color=TEXT, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([l[0] for l in levels], fontsize=8.5,
                                         color=TEXT)
    ax.set_ylim(0, max(plug) + 3.0)
    ax.set_title(title, fontsize=9.5, color=TEXT, loc="left")
    if ylabel:
        ax.set_ylabel("countries with certified\ntrust decline", fontsize=9,
                      color=TEXT)
    if legend:
        ax.legend(fontsize=8, frameon=False, loc="upper right", labelcolor=TEXT)


def _levels(p):
    return [("any-pair\n(marginal)", int(p.any_plugin.sum()), int(p.any_da.sum())),
            ("repeated\n(≥2 pairs)", int((p.pair_plugin >= 2).sum()),
             int((p.pair_da >= 2).sum())),
            ("net decline\n(first→last)", int(p.net_plugin.sum()),
             int(p.net_da.sum())),
            ("persistent\n(country-wide)", int(p.persist_plugin.sum()),
             int(p.persist_da.sum()))]


def fig_hierarchy(cty):
    """Guarantee-unit funnel (trstprl): rounds 9-11 beside the full 2002-24
    record (e36) — one persistent country in the short window, none over the
    long one."""
    p = cty[cty.outcome == "trstprl"]
    panels = [("Rounds 9–11 (2018–24), K=30", _levels(p))]
    try:
        lw = pd.read_csv("results/ess_long_window.csv")
        panels.append(("Full record 1–11 (2002–24), K=34",
                       _levels(lw[lw.outcome == "trstprl"])))
    except FileNotFoundError:
        pass
    fig, axes = plt.subplots(1, len(panels),
                             figsize=(4.9 * len(panels) + 1.0, 3.9),
                             facecolor="#fcfcfb")
    axes = np.atleast_1d(axes)
    for i, (ax, (title, levels)) in enumerate(zip(axes, panels)):
        _funnel(ax, levels, title, legend=(i == 0), ylabel=(i == 0))
    fig.suptitle("Certified trust declines collapse up the guarantee hierarchy",
                 fontsize=10.5, color=TEXT, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    os.makedirs("figures", exist_ok=True)
    fig.savefig("figures/guarantee_hierarchy.png", dpi=200)
    plt.close(fig)


def main():
    pair = pd.read_csv("results/ess_design_aware_decline.csv")
    cty = pd.read_csv("results/ess_country_certification.csv")
    fig_counts(pair)
    fig_reclass(pair)
    fig_hierarchy(cty)
    print("wrote figures/plug_in_vs_design_aware_certification.png, "
          "figures/country_reclassification_map.png, "
          "figures/guarantee_hierarchy.png")


if __name__ == "__main__":
    main()
