"""Gate-4A figures: self-inclusion shrinkage and coverage over K x L.

figures/modulation_score_shrinkage.png : calibration/target score ratio vs K,
    faceted by trajectory length L (heteroskedastic regime). Ratio < 1 means
    the in-sample modulation shrinks calibration scores relative to the
    target's — the mechanism behind S3's undercoverage.
figures/coverage_by_K_L.png : trajectory simultaneous coverage vs K, same
    facets, nominal level marked.

Run:  python -m pcb.figures.fig_modulation   (after e10_modulation_validity)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# fixed categorical slot order (validated: worst adjacent CVD dE 24.2)
COLORS = {"U0": "#2a78d6", "S1": "#1baf7a", "S2": "#eda100", "S3": "#008300"}
LABELS = {"U0": "U0 unstudentized (exact)",
          "S1": "S1 split modulation (exact)",
          "S2": "S2 pooled in-sample (empirical)",
          "S3": "S3 slotwise in-sample (empirical)"}
TEXT, MUTED = "#1a1a19", "#6b6a63"


def _panel_grid(title, ylabel):
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.1), sharey=True,
                             facecolor="#fcfcfb")
    for ax in axes:
        ax.set_facecolor("#fcfcfb")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(MUTED)
        ax.tick_params(colors=MUTED, labelsize=8)
        ax.grid(axis="y", color="#e5e4dd", lw=0.6)
        ax.set_axisbelow(True)
        ax.set_xlabel("K (countries)", fontsize=8, color=TEXT)
    axes[0].set_ylabel(ylabel, fontsize=9, color=TEXT)
    fig.suptitle(title, fontsize=11, color=TEXT, x=0.01, ha="left")
    return fig, axes


def _draw(axes, sim, value, ref=None, ref_label=""):
    for ax, L in zip(axes, (1, 2, 4, 8)):
        sub = sim[(sim.L == L) & (sim.hetero == 1)]
        if ref is not None:
            ax.axhline(ref, color=MUTED, lw=1, ls=(0, (4, 3)))
        for m in ("U0", "S1", "S2", "S3"):
            d = sub[sub.method == m].sort_values("K")
            ax.plot(d.K, d[value], color=COLORS[m], lw=1.8, marker="o",
                    ms=4.5, mec="#fcfcfb", mew=0.8, label=LABELS[m])
        ax.set_title(f"L = {L}", fontsize=9, color=TEXT)
        ax.set_xticks((20, 30, 50, 100))
    # direct label only where the curves separate (S3); legend carries the rest
    last = sim[(sim.L == 8) & (sim.hetero == 1) & (sim.K == 100)]
    y = last[last.method == "S3"][value].iloc[0]
    axes[3].annotate("S3", xy=(100, y), xytext=(103, y), fontsize=8,
                     color=TEXT, va="center", annotation_clip=False)
    if ref_label:
        axes[0].annotate(ref_label, xy=(20, ref), xytext=(20, ref),
                         fontsize=7.5, color=MUTED, va="bottom")
    axes[0].legend(fontsize=7.5, frameon=False, loc="lower right",
                   labelcolor=TEXT)


def main():
    sim = pd.read_csv("results/modulation_simulation.csv")

    fig, axes = _panel_grid(
        "Self-inclusion shrinkage of in-sample modulation "
        "(calibration/target score ratio; heteroskedastic thresholds)",
        "cal / target score ratio")
    _draw(axes, sim, "cal_target_ratio", ref=1.0, ref_label="symmetric (=1)")
    fig.tight_layout(rect=(0, 0, 0.985, 0.93))
    fig.savefig("figures/modulation_score_shrinkage.png", dpi=200)
    plt.close(fig)

    fig, axes = _panel_grid(
        "Trajectory simultaneous coverage by modulation choice "
        "(nominal 90%, heteroskedastic thresholds)",
        "coverage")
    _draw(axes, sim, "coverage", ref=0.90, ref_label="nominal")
    axes[0].set_ylim(0.75, 1.0)
    fig.tight_layout(rect=(0, 0, 0.985, 0.93))
    fig.savefig("figures/coverage_by_K_L.png", dpi=200)
    plt.close(fig)
    print("wrote figures/modulation_score_shrinkage.png, "
          "figures/coverage_by_K_L.png")


if __name__ == "__main__":
    main()
