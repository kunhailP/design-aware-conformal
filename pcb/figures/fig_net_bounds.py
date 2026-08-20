"""Figure 3 (APSR grammar) — the certified net-decline lower bounds, per country.

The statistical object itself, not a summary count: for each of the 33
countries, the joint band's simultaneous lower bound on the first-to-last
(net) decline in parliamentary trust, 2002-2024, read off one band per
country at alpha = 0.10. Positive bound = certified (the eight, filled);
an asterisk marks the six countries named by the closed-testing prevalence
bound (at least six true decliners at 90% simultaneous confidence).
figures/ess_net_bounds.{pdf,png}.
Run:  python -m pcb.figures.fig_net_bounds   (after e50, e56)
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
from pcb.figures.style import apsr, apsr_box, INK, GR1, GR2
apsr()
import matplotlib.pyplot as plt
import os
import pandas as pd

NAMES = {"AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH":
         "Switzerland", "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany",
         "DK": "Denmark", "EE": "Estonia", "ES": "Spain", "FI": "Finland",
         "FR": "France", "GB": "United Kingdom", "GR": "Greece", "HR":
         "Croatia", "HU": "Hungary", "IE": "Ireland", "IL": "Israel", "IS":
         "Iceland", "IT": "Italy", "LT": "Lithuania", "LV": "Latvia", "ME":
         "Montenegro", "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
         "PT": "Portugal", "RU": "Russia", "RS": "Serbia", "SE": "Sweden", "SI": "Slovenia",
         "SK": "Slovakia", "UA": "Ukraine", "XK": "Kosovo"}


def main():
    d = pd.read_csv("results/ess_joint_claims.csv")
    t = d[d.outcome == "trstprl"].copy().sort_values("net_lower")
    p = pd.read_csv("results/ess_prevalence.csv")
    named = set(p[p.outcome == "trstprl"].nsmallest(6, "p_net").cntry)
    t["pts"] = 100 * t.net_lower
    t["label"] = [NAMES.get(c, c) + ("*" if c in named else "")
                  for c in t.cntry]

    fig, ax = plt.subplots(figsize=(5.2, 5.6))
    apsr_box(ax, ygrid=False, xgrid=True)
    ys = range(len(t))
    ax.axvline(0, color=INK, lw=0.8, zorder=2)
    for y, (_, r) in zip(ys, t.iterrows()):
        cert = r.net_lower > 0
        ax.plot([0, r.pts], [y, y], color=GR2 if not cert else INK,
                lw=0.7, zorder=2)
        ax.plot(r.pts, y, "o", ms=4.2, mfc=INK if cert else "white",
                mec=INK, mew=0.8, zorder=3)
    ax.set_yticks(list(ys))
    ax.set_yticklabels(t.label, fontsize=7.6)
    ax.set_ylim(-0.8, len(t) - 0.2)
    ax.set_xlabel("Certified lower bound on net decline, 2002–2024 (CDF points)",
                  fontsize=8.6)
    ax.text(11.5, 13.5, "Certified\n(bound > 0)", fontsize=8,
            color=INK, ha="left", va="center")
    ax.annotate("", xy=(10.5, 13.5), xytext=(2.0, 13.5),
                arrowprops=dict(arrowstyle="->", color=GR1, lw=0.7))
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True)
    fig.savefig("figures/ess_net_bounds.pdf", bbox_inches="tight")
    fig.savefig("figures/ess_net_bounds.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/ess_net_bounds.pdf")


if __name__ == "__main__":
    main()
