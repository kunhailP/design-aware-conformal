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
        "font.sans-serif": ["Arial", "Verdana", "DejaVu Sans", "Helvetica"],
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


# ---- APSR/AJPS grammar (final main-figure system) --------------------------
# Ink + two grays; identity by linetype+marker, never color; full box frame;
# dotted y-grid; direct labels; (a)/(b) panel tags; Arial 8-9.5pt at print size.
INK, GR1, GR2, GR3 = "#000000", "#4d4d4d", "#8c8c8c", "#c8c8c8"


def apsr():
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 9, "axes.linewidth": 0.8,
        "xtick.direction": "out", "ytick.direction": "out",
        "figure.facecolor": "white", "savefig.facecolor": "white",
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })


def apsr_box(ax, ygrid=True, xgrid=False):
    for s in ax.spines.values():
        s.set_color(INK); s.set_linewidth(0.8); s.set_visible(True)
    ax.tick_params(colors=INK, labelsize=8, width=0.8, length=3)
    if ygrid:
        ax.grid(axis="y", color=GR3, lw=0.5, ls=(0, (1, 2)))
    if xgrid:
        ax.grid(axis="x", color=GR3, lw=0.5, ls=(0, (1, 2)))
    ax.set_axisbelow(True)
