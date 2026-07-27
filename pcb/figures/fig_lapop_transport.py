"""Gate-5D Part B figures — Candidate B transport on LAPOP.

figures/lapop_candidate_b_vs_conservative.png : T1/T2/T3 mean width per outcome —
    B reduces to PCB (T3≈T1) and is narrower than the conservative envelope (T2).
figures/lapop_width_by_rho.png : ρ̂ distribution across targets with the ρ₀
    fallback cutoff — why real transport is a low-ρ regime (B → PCB).
figures/lapop_transport_certification.png : stress-test pseudo-coverage vs width,
    showing T3 matches T2's coverage at less width.

Run:  python -m pcb.figures.fig_lapop_transport   (after e16_lapop_transport)
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd

BLUE, AQUA, YELLOW, GREEN = "#2a78d6", "#1baf7a", "#eda100", "#008300"
RED, MUTED2 = "#e34948", "#8a897f"
TEXT, MUTED, GRID = "#1a1a19", "#6b6a63", "#e5e4dd"
LAB = {"b13": "Trust in\nlegislature", "sat": "Satisfaction\nw/ democracy",
       "ing4": "Support for\ndemocracy"}


def _ax(ax):
    ax.set_facecolor("#fcfcfb")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)


def fig_width(loco):
    outs = list(LAB)
    fig, ax = plt.subplots(figsize=(7.4, 3.9), facecolor="#fcfcfb")
    _ax(ax)
    x = np.arange(len(outs)); w = 0.26
    for i, (col, key, lab) in enumerate((
            (MUTED2, "w_T1", "T1 clustered PCB"),
            (YELLOW, "w_T2", "T2 worst-case (conservative)"),
            (BLUE, "w_T3", "T3 Candidate B"))):
        vals = [loco[loco.outcome == o][key].mean() for o in outs]
        ax.bar(x + (i - 1) * w, vals, w, color=col, edgecolor="#fcfcfb",
               linewidth=1.4, label=lab)
    top = max(loco.w_T2.mean(), loco[loco.outcome == "sat"].w_T2.mean())
    ax.set_ylim(0, top * 1.42)
    for o_i, o in enumerate(outs):
        p = loco[loco.outcome == o]
        ax.text(o_i + w, p.w_T3.mean() + top * 0.03,
                f"T3/T1 {p.ratio_T3_T1.mean():.2f}\nT3/T2 {p.ratio_T3_T2.mean():.2f}",
                ha="center", fontsize=7.5, color=TEXT)
    ax.set_xticks(x); ax.set_xticklabels([LAB[o] for o in outs], fontsize=8.5,
                                         color=TEXT)
    ax.set_ylabel("mean band half-width", fontsize=9, color=TEXT)
    ax.legend(fontsize=8, frameon=False, loc="upper left", labelcolor=TEXT)
    ax.set_title("Candidate B reduces to clustered PCB (T3≈T1) and stays narrower "
                 "than\nthe conservative envelope (T3 < T2) — low-ρ regime: "
                 "no harm + efficiency", fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/lapop_candidate_b_vs_conservative.png", dpi=200)
    plt.close(fig)


def fig_rho(loco):
    fig, ax = plt.subplots(figsize=(7.2, 3.7), facecolor="#fcfcfb")
    _ax(ax)
    ax.hist(loco.rho, bins=np.linspace(0, 0.55, 34), color=BLUE,
            edgecolor="#fcfcfb", linewidth=0.6)
    ax.axvline(0.47, color=RED, lw=1.8)
    ax.text(0.455, ax.get_ylim()[1] * 0.9, "ρ₀ = 0.47\nfallback cutoff",
            fontsize=8.5, color=RED, ha="right", va="top", fontweight="bold")
    ax.text(0.15, ax.get_ylim()[1] * 0.6,
            "all targets ρ̂ ≪ ρ₀\n→ reduce to clustered PCB",
            fontsize=9, color=TEXT, ha="center")
    ax.set_xlabel("ρ̂ = design-noise SD / transport-score SD  (per target, LOCO)",
                  fontsize=9, color=TEXT)
    ax.set_ylabel("target countries", fontsize=9, color=TEXT)
    ax.set_title("Real cross-national transport is a LOW-ρ regime: between-country "
                 "signal\ndwarfs within-country survey noise (n≈1500/cell)",
                 fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/lapop_width_by_rho.png", dpi=200)
    plt.close(fig)


def fig_stress(stress):
    fig, ax = plt.subplots(figsize=(6.4, 3.7), facecolor="#fcfcfb")
    _ax(ax)
    m = list(stress.method)
    cols = {"T1 PCB": MUTED2, "T2 worst-case": YELLOW, "T3 Candidate B": BLUE}
    names = {"T1": "T1 PCB", "T2": "T2 worst-case", "T3": "T3 Candidate B"}
    x = np.arange(len(m))
    bars = ax.bar(x, stress.mean_width, 0.6,
                  color=[cols[names[k]] for k in m], edgecolor="#fcfcfb",
                  linewidth=1.5)
    for b, cov, wv in zip(bars, stress.pseudo_coverage, stress.mean_width):
        ax.text(b.get_x() + b.get_width() / 2, wv + 0.004,
                f"cov {cov:.3f}", ha="center", fontsize=9, color=TEXT,
                fontweight="bold")
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels([names[k] for k in m], fontsize=9,
                                         color=TEXT)
    ax.set_ylabel("mean band width (stress test)", fontsize=9, color=TEXT)
    ax.set_ylim(0, stress.mean_width.max() * 1.18)
    ax.set_title("Design-resampling stress test: T3 matches the conservative "
                 "coverage\n(0.929 ≥ 0.90 nominal) at 7% less width",
                 fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/lapop_transport_certification.png", dpi=200)
    plt.close(fig)


def main():
    loco = pd.read_csv("results/lapop_transport_loco.csv")
    stress = pd.read_csv("results/lapop_design_resampling.csv")
    fig_width(loco); fig_rho(loco); fig_stress(stress)
    print("wrote figures/lapop_candidate_b_vs_conservative.png, "
          "figures/lapop_width_by_rho.png, "
          "figures/lapop_transport_certification.png")


if __name__ == "__main__":
    main()
