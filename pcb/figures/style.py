"""Publication figure style — shared by every generator.

Print-first design: figures are laid out at their final column width
(Political Analysis text block ~5.5 in) with type sizes that land at 7–9 pt in
print, an Okabe–Ito colorblind-safe palette, and vector PDF as the primary
output (PNG kept for quick viewing). Import and call `use()` before plotting;
save with `save(fig, name)`.
"""
from __future__ import annotations
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Okabe–Ito (colorblind-safe)
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILION = "#D55E00"
SKY = "#56B4E9"
PURPLE = "#CC79A7"
YELLOW = "#F0E442"
TEXT = "#1a1a19"
MUTED = "#6b6a63"
GRID = "#e5e4dd"
BG = "white"

# final print widths (inches)
COL = 5.5          # PA text-block width
COL_HALF = 2.65


def use():
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
        "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
        "axes.edgecolor": MUTED, "axes.labelcolor": TEXT,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
        "axes.axisbelow": True,
        "lines.linewidth": 1.4, "axes.linewidth": 0.8,
        "legend.frameon": False,
        "pdf.fonttype": 42, "ps.fonttype": 42,   # embed TrueType (editable text)
        "figure.dpi": 110,
    })


def ax_clean(ax, grid_axis="y"):
    ax.grid(False)
    ax.grid(axis=grid_axis, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def save(fig, name, formats=("pdf", "png")):
    """Write figures/<name>.{pdf,png}; PDF is the print artifact."""
    os.makedirs("figures", exist_ok=True)
    for ext in formats:
        fig.savefig(f"figures/{name}.{ext}", dpi=300 if ext == "png" else None,
                    bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
