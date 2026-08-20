"""Figure 2 — the feasibility frontier as a quantitative phase diagram.

Three linked layers in two panels:
  A  the theoretical object: the maximum attainable width reduction
     G(rho) = 1 - sqrt(1 - rho^2) as a continuous surface with labeled
     contours, the frozen boundaries rho_0 and K = 1 + 2/tau_D^2 = 94 on top;
     real-data cells with their estimation uncertainty (rho_LCB to rho_hat),
     datasets by color+shape, activated cells haloed.
  B  what activation buys where it happens: the deconvolved band's width
     against the conservative envelope in the four activating cells, point
     ratio and certified bound, with the do-nothing reference at 1.

Reads results/feasibility_frontier.csv and results/small_area_transport.csv.
Writes figures/feasibility_frontier.{pdf,png} at print width (5.5 in).
Run:  python -m pcb.figures.fig_frontier   (after e57)
"""
import matplotlib
matplotlib.use("Agg")
from pcb.figures.style import (use as _style_use, BLACK, DARK_GRAY, MID_GRAY,
                               GRID_GRAY, NAVY, TEAL, RUST, AMBER)
_style_use()
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd

RHO0 = 0.47
TAU_D = (0.02 - 0.0061) / 0.0943
KSTAR = int(np.ceil(1 + 2 / TAU_D ** 2))

STYLES = {"WVS full-coverage items": (AMBER, "s", "WVS items"),
          "ESS national-unit scan": (RUST, "o", "ESS national"),
          "ESS small-area (e54)": (TEAL, "^", "ESS small-area"),
          "ESS small-area, common NUTS level": (TEAL, "D",
                                                "small-area, one NUTS level")}


def _deframe(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(DARK_GRAY)
    ax.tick_params(colors=DARK_GRAY, labelsize=7.5)


def main():
    d = pd.read_csv("results/feasibility_frontier.csv")
    sa = pd.read_csv("results/small_area_transport.csv")
    fired = sa[(sa.pool == "all countries") & (sa.branch == "deconvolution")]

    fig = plt.figure(figsize=(5.5, 3.6), facecolor="white")
    gs = GridSpec(1, 2, width_ratios=[2.9, 1.0], wspace=0.34)

    # ---------------- A: phase surface ----------------
    ax = fig.add_subplot(gs[0])
    _deframe(ax)
    ax.set_xscale("log")
    ax.set_xlim(8, 420)
    ax.set_ylim(0, 0.62)

    rr = np.linspace(0, 0.62, 200)
    G = (1 - np.sqrt(1 - rr ** 2))[:, None] * np.ones((1, 2))
    ax.imshow(G, extent=(8, 420, 0, 0.62), origin="lower", aspect="auto",
              cmap="cividis", alpha=0.35, vmin=0, vmax=0.25, zorder=0)
    for g, lab in [(0.02, "2%"), (0.05, "5%"), (0.10, "10%"), (0.20, "cut 20%")]:
        r_g = np.sqrt(1 - (1 - g) ** 2)
        ax.axhline(r_g, color="white", lw=0.7, alpha=0.9, zorder=1)
        ax.text(430, r_g, lab, fontsize=6.5, color=DARK_GRAY,
                va="center", ha="left", clip_on=False)

    ax.axhline(RHO0, color=NAVY, lw=1.1, ls="--", zorder=3)
    ax.plot([KSTAR, KSTAR], [0, 0.62], color=NAVY, lw=1.1, ls="--", zorder=3)
    ax.text(8.6, RHO0 + 0.012, r"need gate $\rho_0$", fontsize=7, color=NAVY)
    ax.text(KSTAR * 1.06, 0.015,
            r"reliability floor $K=1{+}2/\tau_D^2$", fontsize=6.6, color=NAVY,
            rotation=90, va="bottom")
    ax.text(11, 0.585, "unlearnable", fontsize=8, color=DARK_GRAY,
            style="italic", va="top")
    ax.text(KSTAR * 1.5, 0.585, "feasible", fontsize=8, color=DARK_GRAY,
            style="italic", va="top")
    ax.text(11, 0.035, "unnecessary", fontsize=8, color=DARK_GRAY,
            style="italic")

    for name, (col, mk, lab) in STYLES.items():
        g = d[d.dataset == name]
        ax.vlines(g.K, g.rho_lcb, g.rho_hat, color=col, lw=0.8, alpha=0.55,
                  zorder=4)
        idle, act = g[~g.activated], g[g.activated]
        ax.scatter(idle.K, idle.rho_lcb, s=16, facecolors="white",
                   edgecolors=col, marker=mk, lw=1.0, zorder=5, label=lab)
        if len(act):
            ax.scatter(act.K, act.rho_lcb, s=56, facecolors="none",
                       edgecolors=NAVY, marker="o", lw=1.2, zorder=6)
            ax.scatter(act.K, act.rho_lcb, s=22, facecolors=col,
                       edgecolors=col, marker=mk, zorder=6,
                       label="selector activated")
    ax.set_xlabel("exchangeable populations  $K$ (log scale)", fontsize=8,
                  color=BLACK)
    ax.set_ylabel(r"design-to-total ratio  $\hat\rho$"
                  "  (whisker: LCB to estimate)", fontsize=8, color=BLACK)
    ax.legend(fontsize=6.6, frameon=False, labelcolor=BLACK, loc="lower right",
              bbox_to_anchor=(0.995, 0.03), handletextpad=0.25,
              borderaxespad=0.1, labelspacing=0.35)
    ax.set_title("A.  Where correction pays, and where it can be learned",
                 fontsize=8.5, color=BLACK, loc="left")

    # ---------------- B: what activation buys ----------------
    ax2 = fig.add_subplot(gs[1])
    _deframe(ax2)
    ys = np.arange(len(fired))[::-1]
    ratio = 1 - (fired.gain_lcb.values + 0.05)
    cert = 1 - fired.gain_lcb.values
    ax2.axvline(1.0, color=RUST, lw=1.0, ls="--")
    ax2.text(0.995, -0.5, "conservative\nenvelope", fontsize=6.3, color=RUST,
             ha="right", va="bottom")
    for y, r, c in zip(ys, ratio, cert):
        ax2.plot([r, c], [y, y], color=MID_GRAY, lw=1.4, zorder=2)
        ax2.plot([c], [y], "|", color=MID_GRAY, ms=7, zorder=3)
        ax2.plot([r], [y], "^", color=TEAL, ms=6, zorder=4)
    ax2.set_yticks(ys)
    ax2.set_yticklabels([f"$K{{=}}{int(k)}$" for k in fired.K], fontsize=7)
    ax2.set_xlim(0.62, 1.1)
    ax2.set_ylim(-0.6, len(fired) - 0.2)
    ax2.set_xticks([0.7, 0.8, 0.9, 1.0])
    ax2.set_xlabel("width vs conservative\n($\\blacktriangle$ point; "
                   "$|$ certified bound)", fontsize=7.5, color=BLACK)
    ax2.set_title("B.  What activation buys", fontsize=8.5, color=BLACK,
                  loc="left")
    ax2.grid(axis="x", color=GRID_GRAY, lw=0.45)
    ax2.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig("figures/feasibility_frontier.pdf", bbox_inches="tight")
    fig.savefig("figures/feasibility_frontier.png", dpi=300,
                bbox_inches="tight")
    print("wrote figures/feasibility_frontier.pdf")


if __name__ == "__main__":
    main()
