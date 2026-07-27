"""Mechanism-illustration figures for the finite-K deconvolution theory (T2/T3').

Self-contained: generates its own controlled Monte Carlo (fixed det_seed, Gaussian
transport DGP at a single moderate ρ in the deconvolution regime) so the two panels
isolate the *mechanism* rather than re-reporting the frozen confirmatory holdout
(e22). Nothing here feeds the validation; it only illustrates why the finite-K floor
is needed and that the safe scale tracks the oracle from above.

  figures/theory_shrinkage.png : score-scale shrinkage ratio ŝ/s_plug vs K, for the
      oracle, the naive plug-in (subtract mean v² outright), and the finite-K-safe
      scale. Naive over-shrinks below the oracle at small K (→ undercoverage); safe
      stays ≥ oracle (conservative) and converges as K grows.
  figures/theory_coverage.png : coverage vs K faceted by trajectory length L, for
      clustered PCB, naive deconvolution, and the safe-adaptive selector, against the
      0.90 nominal line. Naive dips below nominal at small K; the safe selector holds.

Run:  python -m pcb.figures.fig_theory_illustration
"""
from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
import os
import numpy as np

from pcb.dapcb import dapcb
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import (_finite_quantile, deconv_target_scale)
from pcb.util import det_seed

# --- house style ------------------------------------------------------------
TEXT, MUTED, GRID, SURF = "#1a1a19", "#6b6a63", "#e5e4dd", "#fcfcfb"
COL = {"oracle": "#1a1a19", "naive": "#e34948",
       "safe": "#eda100", "safe_dec": "#eda100", "selector": "#1baf7a"}
KS = [25, 40, 80, 160, 320]
LS = [4, 8, 16]
S_R, RHO, ALPHA, REPS = 1.0, 0.90, 0.10, 2000   # ρ = design SD / transport SD
Z = 1.6448536
FLOOR_FRAC = 0.05
MASTER = 20260707


def _ax(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def _logk(ax):
    """Log-K x-axis showing exactly the sampled K values, no minor-tick clutter."""
    ax.set_xscale("log")
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_locator(FixedLocator(KS))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(round(v))}"))
    ax.set_xlim(KS[0] * 0.9, KS[-1] * 1.1)


def _gen(K, L, rng):
    """Gaussian transport DGP: E = R + ξ, latent target deviation Et."""
    v = S_R * RHO
    R = rng.normal(0, S_R, (K, L))
    Et = rng.normal(0, S_R, L)
    xi = rng.normal(0, 1, (K, L)) * v
    E = R + xi
    V = np.abs(v * (1 + rng.normal(0, 0.15, (K, L))))    # noisy reported design SD
    return E, V, Et


def _naive_scale(E, V):
    """Naive plug-in deconvolved scale: subtract mean v² outright (no finite-K
    guard), floored — matches the T3 scale of e19/e16."""
    s_plug = _modulation(E)
    floor = (FLOOR_FRAC * s_plug.max()) ** 2
    return np.sqrt(np.maximum(s_plug**2 - (V**2).mean(0), floor))


def simulate():
    """Return (shrink, cov): shrink[K] = mean scale/s_plug ratios at L=8;
    cov[(L,K)] = coverage of the latent target curve by method.

    Three deconvolution deployments share the same calibrate-with-design-noise,
    deploy-on-clean-target structure (the finite-K mechanism): the calibration
    score divides |E| by the per-cell sqrt(sT²+V²); the target is covered at the
    aggregate deconvolved scale sT. Naive uses the outright subtraction; safe uses
    the z-guarded floor (deconv_target_scale); the selector is the deployed dapcb.
    """
    shrink, cov = {}, {}
    for L in LS:
        for K in KS:
            r_or, r_na, r_sd = [], [], []
            c_na, c_sd, c_sel = [], [], []
            for rep in range(REPS):
                rng = np.random.default_rng(det_seed(MASTER, "illus", K, L, rep))
                E, V, Et = _gen(K, L, rng)
                s = _modulation(E)
                sN = _naive_scale(E, V)              # naive deconvolved scale
                sS = deconv_target_scale(E, V)       # finite-K-safe scale
                qN = _finite_quantile(np.max(np.abs(E) / np.sqrt(sN[None]**2 + V**2), 1), ALPHA)
                qS = _finite_quantile(np.max(np.abs(E) / np.sqrt(sS[None]**2 + V**2), 1), ALPHA)
                qP = _finite_quantile(np.max(np.abs(E) / s, 1), ALPHA)
                qC = _finite_quantile(np.max((np.abs(E) + Z * V) / s, 1), ALPHA)
                c_na.append(int(np.max(np.abs(Et) / sN) <= qN))
                c_sd.append(int(np.max(np.abs(Et) / sS) <= qS))
                # deployed adaptive selector: coverage of the branch it routes to
                # (clip-free max-score, as in e22 — the band's [0,1] clip is a
                # display detail, not the guarantee)
                fit = dapcb(E, V, np.full(L, 0.5), alpha=ALPHA, tighten=False)
                br = fit.selected_branch
                if br == "deconvolution":
                    c_sel.append(int(np.max(np.abs(Et) / sS) <= qS))
                elif br == "conservative":
                    c_sel.append(int(np.max(np.abs(Et) / s) <= qC))
                else:                                    # PCB
                    c_sel.append(int(np.max(np.abs(Et) / s) <= qP))
                r_or.append(S_R / s.mean())
                r_na.append((sN / s).mean())
                r_sd.append((sS / s).mean())
            cov[(L, K)] = {"naive": np.mean(c_na), "safe_dec": np.mean(c_sd),
                           "selector": np.mean(c_sel)}
            if L == 8:
                shrink[K] = {"oracle": np.mean(r_or), "naive": np.mean(r_na),
                             "safe": np.mean(r_sd)}
    return shrink, cov


def fig_shrinkage(shrink):
    fig, ax = plt.subplots(figsize=(5.4, 4.0), facecolor=SURF)
    _ax(ax)
    x = KS
    for key, lab, ls, mk in [("oracle", "oracle  $s_R/s_{\\rm plug}$", "--", None),
                             ("naive", "naive plug-in", "-", "o"),
                             ("safe", "finite-$K$-safe", "-", "s")]:
        y = [shrink[K][key] for K in x]
        ax.plot(x, y, ls, color=COL[key], lw=1.9, marker=mk, ms=4.5,
                label=lab, zorder=3 if key != "oracle" else 2)
    _logk(ax)
    lo = min(shrink[KS[0]]["naive"], min(shrink[K]["oracle"] for K in KS))
    hi = max(shrink[K]["safe"] for K in KS)
    ax.set_ylim(lo - 0.03, hi + 0.03)
    ax.set_xlabel("number of source populations  $K$", fontsize=9.5, color=TEXT)
    ax.set_ylabel("score-scale shrinkage ratio  $\\hat s / s_{\\rm plug}$",
                  fontsize=9.5, color=TEXT)
    ax.legend(fontsize=8.5, frameon=False, labelcolor=TEXT, loc="lower right")
    # direct annotation of the mechanism
    yn = shrink[KS[0]]["naive"]
    ax.annotate("naive over-shrinks most\n(→ worst undercoverage)",
                xy=(KS[0], yn), xytext=(KS[1] * 1.02, yn - 0.010),
                fontsize=8, color=COL["naive"], va="top",
                arrowprops=dict(arrowstyle="->", color=COL["naive"], lw=1.0))
    ax.set_title("Both estimated scales over-shrink below the oracle at small $K$;\n"
                 "the safe guard shrinks less, and both converge as $K$ grows",
                 fontsize=9.5, color=TEXT, loc="left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/theory_shrinkage.png", dpi=200)
    plt.close(fig)
    print("wrote figures/theory_shrinkage.png")


def fig_coverage(cov):
    fig, axes = plt.subplots(1, len(LS), figsize=(11, 3.7), facecolor=SURF,
                             sharey=True)
    for j, L in enumerate(LS):
        ax = axes[j]
        _ax(ax)
        ax.axhline(1 - ALPHA, color=MUTED, lw=1.2, ls=":")
        if j == 0:
            ax.text(KS[0], 1 - ALPHA + 0.008, "nominal 0.90", fontsize=7.6, color=MUTED)
        # draw order: naive underneath, safe deconvolution, deployed selector on top
        for key, lab, mk, z, lw in [("naive", "naive deconvolution", "o", 2, 1.8),
                                    ("safe_dec", "finite-$K$-safe deconv.", "D", 3, 1.8),
                                    ("selector", "adaptive selector (ours)", "s", 4, 2.1)]:
            y = [cov[(L, K)][key] for K in KS]
            ax.plot(KS, y, "-", color=COL[key], lw=lw, marker=mk, ms=5.0,
                    label=lab, zorder=z)
        _logk(ax)
        ax.set_xlabel("$K$", fontsize=9.5, color=TEXT)
        ax.set_title(f"trajectory length  $L={L}$", fontsize=9.5, color=TEXT, loc="left")
        if j == 0:
            ax.set_ylabel("empirical coverage", fontsize=9.5, color=TEXT)
            ax.legend(fontsize=8, frameon=False, labelcolor=TEXT, loc="lower left")
    ymin = min(cov[(L, K)]["naive"] for L in LS for K in KS)
    axes[0].set_ylim(min(0.80, ymin - 0.03), 1.012)
    fig.suptitle("Both naive and finite-$K$-safe deconvolution undercover at small "
                 "$K$ (worse as $L$ grows); the deployed selector abstains and stays "
                 "valid", fontsize=10.5, color=TEXT, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    os.makedirs("figures", exist_ok=True); fig.savefig("figures/theory_coverage.png", dpi=200)
    plt.close(fig)
    print("wrote figures/theory_coverage.png")


def main():
    shrink, cov = simulate()
    print(f"ρ={RHO} (design/transport), reps={REPS}")
    print("shrinkage ratio ŝ/s_plug at L=8:")
    for K in KS:
        print(f"  K={K:>3}: oracle {shrink[K]['oracle']:.3f}  "
              f"naive {shrink[K]['naive']:.3f}  safe {shrink[K]['safe']:.3f}")
    print("coverage (naive / safe-deconv / selector):")
    for L in LS:
        for K in KS:
            c = cov[(L, K)]
            print(f"  L={L:>2} K={K:>3}: {c['naive']:.3f} / {c['safe_dec']:.3f} "
                  f"/ {c['selector']:.3f}")
    fig_shrinkage(shrink)
    fig_coverage(cov)


if __name__ == "__main__":
    main()
