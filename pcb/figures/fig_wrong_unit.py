"""Figure 1 (APSR grammar) — coverage collapses at the wrong unit.

Black filled trajectory series in front, gray dashed/dotted wrong units
behind; identity by linetype+marker; thin +/-2 MC-SE bars; direct labels,
no legend; thin nominal-90 rule. figures/wrong_unit_coverage.{pdf,png}.
Run:  python -m pcb.figures.fig_wrong_unit   (after e28)
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
from pcb.figures.style import apsr, apsr_box, INK, GR1, GR2
apsr()
import matplotlib.pyplot as plt
import os
import pandas as pd

SERIES = [("trajectory", INK,  "-",  "o", True,  "Trajectory"),
          ("per_round",  GR1, "--", "^", False, "Round"),
          ("marginal",   GR2, ":",  "s", False, "Threshold")]


def main():
    d = pd.read_csv("results/wrong_unit_coverage.csv")
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    apsr_box(ax)
    ax.axhline(90, color=INK, lw=0.7, zorder=1)
    ax.text(4.9, 91.3, "Nominal 90%", fontsize=8, color=INK, ha="center")
    for k, c, ls, mk, filled, lab in SERIES:
        q = d[d.method == k].sort_values("L")
        ax.errorbar(q.L, q.traj_cov_pct, yerr=2 * q.cov_se, color=c,
                    lw=0, elinewidth=0.7, capsize=1.6, capthick=0.7, zorder=2)
        ax.plot(q.L, q.traj_cov_pct, ls, color=c, lw=1.1, zorder=3)
        ax.plot(q.L, q.traj_cov_pct, mk, color=c, ms=4.3,
                mfc=c if filled else "white", mew=0.9, zorder=4)
        v = float(q.traj_cov_pct.iloc[-1])
        ax.annotate(f"{lab}  {v:.1f}", (8, v), textcoords="offset points",
                    xytext=(7, 4 if filled else -3), fontsize=8, color=c)
    ax.set_xticks([2, 4, 6, 8])
    ax.set_xlim(1.7, 10.6)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Trajectory length (survey rounds)", fontsize=9)
    ax.set_ylabel("Whole-trajectory coverage (%)", fontsize=9)
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True)
    fig.savefig("figures/wrong_unit_coverage.pdf", bbox_inches="tight")
    fig.savefig("figures/wrong_unit_coverage.png", dpi=300,
                bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/wrong_unit_coverage.pdf")


if __name__ == "__main__":
    main()
