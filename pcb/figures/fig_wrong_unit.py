"""Figure 1 — the wrong unit of uncertainty, as a visual theorem.

  A  the unit mismatch: three ways to attach uncertainty to the same
     trajectory F_{c,r}(t) -- per threshold, per round, whole trajectory --
     with the claim living at the trajectory level.
  B  the coverage landscape (e60): whole-trajectory coverage of the
     marginal-unit band over trajectory length L and round-to-round
     dependence, collapsing along an effective-multiplicity surface.
  C  slices at the e28 benchmark: the three units against L, with the
     independent-rounds reference 0.9^L, and the trajectory unit holding
     nominal 90% by exchangeability.

Reads results/wrong_unit_coverage.csv and results/wrong_unit_landscape.csv.
Writes figures/wrong_unit_coverage.{pdf,png} at print width (5.5 in).
Run:  python -m pcb.figures.fig_wrong_unit   (after e28, e60)
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


def _deframe(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(DARK_GRAY)
    ax.tick_params(colors=DARK_GRAY, labelsize=7)


def panel_a(ax):
    ax.axis("off")
    rng = np.random.default_rng(3)
    L, T = 4, 5
    base = np.linspace(0.25, 0.75, T)
    curves = [np.clip(base + 0.05 * r + rng.normal(0, 0.02, T), 0, 1)
              for r in range(L)]
    x0 = np.linspace(0.08, 0.92, T)
    for r, cv in enumerate(curves):
        y = 0.80 - 0.17 * r
        ax.plot(x0, y + 0.10 * (cv - cv.mean()), "-", color=NAVY, lw=1.1)
        ax.text(-0.05, y, f"$r{{=}}{r+1}$", fontsize=6, color=DARK_GRAY,
                va="center", ha="right")
    # unit brackets
    ax.add_patch(plt.Rectangle((0.235, 0.115), 0.075, 0.78, fill=False,
                               edgecolor=RUST, lw=1.0, ls=":"))
    ax.text(0.27, 0.965, "per threshold\n$(r,t)$ cells", fontsize=6.0,
            color=RUST, ha="center", va="bottom")
    ax.add_patch(plt.Rectangle((0.045, 0.585), 0.91, 0.135, fill=False,
                               edgecolor=MID_GRAY, lw=1.0, ls="--"))
    ax.text(0.75, 0.745, "per round", fontsize=6.0, color=MID_GRAY,
            va="bottom")
    ax.add_patch(plt.Rectangle((0.02, 0.09), 0.965, 0.84, fill=False,
                               edgecolor=TEAL, lw=1.3))
    ax.text(0.5, 0.015, r"the claim: whole $\{F_{c,r}(t)\}_{r,t}$",
            fontsize=6.6, color=TEAL, ha="center", va="top")
    ax.set_xlim(-0.17, 1.04)
    ax.set_ylim(-0.12, 1.12)


def panel_b(ax, land):
    m = land[land.method == "marginal"].pivot(index="dep", columns="L",
                                              values="traj_cov_pct")
    Ls, deps = m.columns.to_numpy(), m.index.to_numpy()
    im = ax.imshow(m.to_numpy(), origin="lower", aspect="auto",
                   cmap="viridis", vmin=0, vmax=90,
                   extent=(Ls.min() - 0.5, Ls.max() + 0.5,
                           -0.1125, 1.0125))
    cs = ax.contour(Ls, deps, m.to_numpy(), levels=[5, 15, 30],
                    colors="white", linewidths=0.7)
    ax.clabel(cs, fmt="%.0f%%", fontsize=5.6)
    ax.set_yticks(deps)
    ax.set_xticks([2, 4, 6, 8, 10])
    _deframe(ax)
    ax.set_xlabel("trajectory length $L$", fontsize=7.2, color=BLACK)
    ax.set_ylabel("round-to-round dependence", fontsize=7.2, color=BLACK)
    cb = plt.colorbar(im, ax=ax, fraction=0.045, pad=0.015)
    cb.ax.tick_params(labelsize=5.8, colors=DARK_GRAY)
    cb.set_label("coverage %", fontsize=5.8, color=DARK_GRAY,
                 labelpad=1)
    cb.outline.set_visible(False)


def panel_c(ax, d):
    series = [("trajectory", TEAL, "-", "o", "trajectory"),
              ("per_round", MID_GRAY, "--", "^", "per round"),
              ("marginal", RUST, ":", "s", "per threshold")]
    for key, col, ls, mk, lab in series:
        q = d[d.method == key].sort_values("L")
        ax.plot(q.L, q.traj_cov_pct, ls, color=col, lw=1.3, zorder=2)
        ax.plot(q.L, q.traj_cov_pct, mk, color=col, ms=3.6,
                mfc=col if key == "trajectory" else "white", mew=1.0,
                zorder=3)
        v = float(q.traj_cov_pct.iloc[-1])
        dy = {"trajectory": 5, "per_round": -8, "marginal": -3}[key]
        ax.annotate(f"{lab}  {v:.1f}", (8, v), textcoords="offset points",
                    xytext=(6, dy), fontsize=6.2, color=col,
                    fontweight="bold" if key == "trajectory" else "normal")
    Ls = np.array(sorted(d.L.unique()))
    ax.plot(Ls, 100 * 0.9 ** Ls, color=NEUTRAL, lw=0.9, ls="-.", zorder=1)
    ax.annotate("$0.9^{L}$ benchmark", (Ls[1], 100 * 0.9 ** Ls[1]),
                textcoords="offset points", xytext=(-12, -13), fontsize=5.8,
                color=NEUTRAL)
    ax.axhline(90, color=NAVY, lw=0.8, ls="--", zorder=1)
    ax.text(2.05, 92.5, "nominal 90%", fontsize=5.8, color=NAVY)
    _deframe(ax)
    ax.set_xticks(Ls)
    ax.set_xlim(1.7, 11.9)
    ax.set_ylim(0, 100)
    ax.set_xlabel("trajectory length $L$", fontsize=7.2, color=BLACK)
    ax.set_ylabel("coverage (%)", fontsize=7.2, color=BLACK)
    ax.grid(color=GRID_GRAY, lw=0.4)
    ax.set_axisbelow(True)


def main():
    d = pd.read_csv("results/wrong_unit_coverage.csv")
    land = pd.read_csv("results/wrong_unit_landscape.csv")
    fig = plt.figure(figsize=(5.5, 2.45), facecolor="white")
    gs = GridSpec(1, 3, width_ratios=[1.0, 1.5, 1.35], wspace=0.5)
    axA = fig.add_subplot(gs[0])
    axB = fig.add_subplot(gs[1])
    axC = fig.add_subplot(gs[2])
    panel_a(axA)
    panel_b(axB, land)
    panel_c(axC, d)
    axA.set_title("A.  The unit mismatch", fontsize=7.6, color=BLACK,
                  loc="left")
    axB.set_title("B.  Wrong-unit collapse surface", fontsize=7.6, color=BLACK,
                  loc="left")
    axC.set_title("C.  Slices at the benchmark", fontsize=7.6, color=BLACK,
                  loc="left")
    fig.savefig("figures/wrong_unit_coverage.pdf", bbox_inches="tight")
    fig.savefig("figures/wrong_unit_coverage.png", dpi=300,
                bbox_inches="tight")
    print("wrote figures/wrong_unit_coverage.pdf")


if __name__ == "__main__":
    main()
