"""Figure 3 — what survives different political claims, and why.

  A  the claim family as it is: a Hasse diagram of the partial order
     (persistent implies net and any-pair; net and any-pair incomparable),
     annotated with certified counts under both uncertainty layers.
  B  country-level intersection structure (UpSet): which combinations of
     claims each of the 30 countries certifies, design-aware.
  C  the mechanism of reclassification: decline signal against design noise
     for every plug-in-certified adjacent pair, SNR isolines, retained vs
     reclassified under the design-aware band.

Reads results/ess_country_certification.csv, results/ess_design_aware_decline.csv.
Writes figures/guarantee_hierarchy.{pdf,png} at print width (5.5 in).
Run:  python -m pcb.figures.fig_ess_claims
"""
import matplotlib
matplotlib.use("Agg")
from pcb.figures.style import (use as _style_use, BLACK, DARK_GRAY, MID_GRAY,
                               GRID_GRAY, NAVY, TEAL, RUST, NEUTRAL)
_style_use()
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd

OUT = "trstprl"


def _deframe(ax, keep=("left", "bottom")):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)
        if s in keep:
            ax.spines[s].set_color(DARK_GRAY)
    ax.tick_params(colors=DARK_GRAY, labelsize=7)


def panel_a(ax, t):
    """Hasse diagram with counts (design-aware / plug-in)."""
    ax.axis("off")
    pos = {"pairwise": (0.5, 0.05), "any": (0.09, 0.52), "net": (0.91, 0.52),
           "persist": (0.5, 0.97)}
    for a, b in [("pairwise", "any"), ("pairwise", "net"),
                 ("any", "persist"), ("net", "persist")]:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]],
                color=MID_GRAY, lw=1.1, zorder=1)
    counts = {
        "pairwise": ("marginal", int(t.any_plugin.sum()), None),
        "any": ("any-pair", int(t.any_da.sum()), int(t.any_plugin.sum())),
        "net": ("net", int(t.net_da.sum()), int(t.net_plugin.sum())),
        "persist": ("persistent", int(t.persist_da.sum()),
                    int(t.persist_plugin.sum()))}
    for k, (lab, da, pi) in counts.items():
        x, y = pos[k]
        ax.scatter([x], [y], s=2050, facecolors="white", edgecolors=NAVY,
                   lw=1.2, zorder=2)
        ax.text(x, y + 0.030, lab, ha="center", va="center", fontsize=6.2,
                color=BLACK, zorder=3)
        tail = "" if pi is None else f" ({pi})"
        ax.text(x, y - 0.042, f"{da}{tail}", ha="center", va="center",
                fontsize=8.4, color=TEAL, fontweight="bold", zorder=3)
    ax.text(0.5, -0.10, "certified countries, design-aware (plug-in)",
            ha="center", fontsize=6.4, color=DARK_GRAY, transform=ax.transAxes)
    ax.text(0.5, 0.30, "no edge:\nincomparable", ha="center", fontsize=6.0,
            color=NEUTRAL, style="italic")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.06)


def panel_b(ax_bar, ax_dot, t):
    """UpSet of design-aware claim membership over the 30 countries."""
    sets = [("marginal", t.any_plugin), ("any-pair", t.any_da),
            ("net", t.net_da), ("persistent", t.persist_da)]
    names = [n for n, _ in sets]
    M = np.column_stack([v.astype(bool).to_numpy() for _, v in sets])
    pats = {}
    for row in M:
        pats[tuple(row)] = pats.get(tuple(row), 0) + 1
    pats = sorted(pats.items(), key=lambda kv: -kv[1])
    xs = np.arange(len(pats))
    ax_bar.bar(xs, [c for _, c in pats], width=0.62, color=NAVY)
    for x, (_, c) in zip(xs, pats):
        ax_bar.text(x, c + 0.25, str(c), ha="center", fontsize=6.6,
                    color=BLACK)
    _deframe(ax_bar, keep=("left",))
    ax_bar.set_xticks([])
    ax_bar.set_ylabel("countries", fontsize=7, color=BLACK)
    ax_bar.set_xlim(-0.6, len(pats) - 0.4)
    ax_bar.grid(axis="y", color=GRID_GRAY, lw=0.4)
    ax_bar.set_axisbelow(True)

    for j, name in enumerate(names):
        y = len(names) - 1 - j
        ax_dot.scatter(xs, [y] * len(xs), s=26,
                       facecolors=["white"] * len(xs),
                       edgecolors=GRID_GRAY, lw=0.8, zorder=1)
        for x, (pat, _) in zip(xs, pats):
            if pat[j]:
                ax_dot.scatter([x], [y], s=30, color=NAVY, zorder=2)
        col = [x for x, (pat, _) in zip(xs, pats) if pat[j]]
    for x, (pat, _) in zip(xs, pats):
        on = [len(names) - 1 - j for j in range(len(names)) if pat[j]]
        if len(on) > 1:
            ax_dot.plot([x, x], [min(on), max(on)], color=NAVY, lw=1.1,
                        zorder=1)
    ax_dot.set_yticks(range(len(names)))
    ax_dot.set_yticklabels(names[::-1], fontsize=6.6, color=BLACK)
    ax_dot.set_xticks([])
    ax_dot.set_xlim(-0.6, len(pats) - 0.4)
    ax_dot.set_ylim(-0.6, len(names) - 0.4)
    _deframe(ax_dot, keep=())
    ax_dot.tick_params(length=0)


def panel_c(ax, pair):
    p = pair[(pair.outcome == OUT) & (pair.M0_plugin == 1)].copy()
    kept = p[p.M4_design == 1]
    lost = p[p.M4_design == 0]
    lim = max(p.design_sd.max() * 1.15, 0.055)
    ymax = p.signal.max() * 1.12
    for k, ls in [(1, ":"), (2, "--"), (4, "-")]:
        xs = np.array([0, lim])
        ax.plot(xs, k * xs, color=GRID_GRAY, lw=0.9, ls=ls, zorder=1)
        if k * lim <= ymax:
            ax.text(lim * 0.98, k * lim, f"SNR {k}", fontsize=6.0,
                    color=NEUTRAL, ha="right", va="bottom")
        else:
            ax.text(ymax / k * 0.94, ymax * 0.965, f"SNR {k}", fontsize=6.0,
                    color=NEUTRAL, ha="right", va="top")
    ax.scatter(lost.design_sd, lost.signal, s=17, facecolors="white",
               edgecolors=RUST, lw=0.9, zorder=3,
               label="reclassified inconclusive")
    ax.scatter(kept.design_sd, kept.signal, s=17, color=TEAL, zorder=3,
               label="retained")
    _deframe(ax)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, ymax)
    ax.set_xlabel("design noise (SD)", fontsize=7.4, color=BLACK)
    ax.set_ylabel("decline signal (CDF pts)", fontsize=7.4, color=BLACK)
    ax.legend(fontsize=6.2, frameon=False, loc="upper left", labelcolor=BLACK,
              handletextpad=0.2)


def main():
    cty = pd.read_csv("results/ess_country_certification.csv")
    t = cty[cty.outcome == OUT]
    pair = pd.read_csv("results/ess_design_aware_decline.csv")

    fig = plt.figure(figsize=(5.5, 3.1), facecolor="white")
    gs = GridSpec(2, 3, width_ratios=[1.05, 1.35, 1.15],
                  height_ratios=[1.35, 1.0], hspace=0.06, wspace=0.42)
    axA = fig.add_subplot(gs[:, 0])
    axB1 = fig.add_subplot(gs[0, 1])
    axB2 = fig.add_subplot(gs[1, 1], sharex=axB1)
    axC = fig.add_subplot(gs[:, 2])

    panel_a(axA, t)
    panel_b(axB1, axB2, t)
    panel_c(axC, pair)
    axA.set_title("A.  The claim family", fontsize=8, color=BLACK, loc="left")
    axB1.set_title("B.  Countries by claim set", fontsize=8, color=BLACK,
                   loc="left")
    axC.set_title("C.  Why countries reclassify", fontsize=8, color=BLACK,
                  loc="left")
    fig.savefig("figures/guarantee_hierarchy.pdf", bbox_inches="tight")
    fig.savefig("figures/guarantee_hierarchy.png", dpi=300,
                bbox_inches="tight")
    print("wrote figures/guarantee_hierarchy.pdf")


if __name__ == "__main__":
    main()
