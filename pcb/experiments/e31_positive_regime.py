"""E31 — the positive regime: where the design-aware correction actually pays.

The survey-scale story is an impossibility (Prop 1: gate B needs K >= 94; no
repeated cross-national survey clears both barriers). This experiment supplies
the CONTRAST the scope result leaves open: a many-unit, MRP-style small-area
calibration (hundreds of areas, appreciable posterior noise) where the frozen
deployed pipeline — unchanged constants, Theorem 5' alpha-budget architecture —
actually opens the gates, rides deconvolution, and pays out.

For each (K, noise-to-signal) cell we simulate small-area calibration curves
E = R + xi with known heteroskedastic posterior SDs v (the e29 'mrp' DGP), run
`dapcb` verbatim, and score the returned band against the latent target curve:

  * activation: share of draws where the deconvolution branch fires;
  * validity:   latent-target coverage of the deployed band vs 1 - alpha - delta;
  * efficiency: deployed width relative to the conservative envelope, against
                the oracle sqrt(1 - rho^2) law.

Deterministic (pcb.util.det_seed). Writes results/positive_regime.csv.

Run:  python -m pcb.experiments.e31_positive_regime
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.dapcb import dapcb

ALPHA = 0.10
T = 6
REPS = 800
K_GRID = [60, 94, 150, 220, 300]
NOISE_GRID = [0.3, 0.5, 0.7, 0.9]      # posterior-SD / between-area-signal ratio
MASTER = 20260718


def _draw(K, noise, rng, sig=0.1):
    """MRP-style small-area panel (e29 'mrp' DGP, rescaled so the bands live
    inside the unit interval and the deployed [0,1] clip never binds): latent
    area curves R, heteroskedastic known posterior SDs v (mean = noise·sig),
    observed E = R + xi, plus a latent target curve Rt (its posterior noise
    plays no role: the deployment target is the latent small-area curve)."""
    area = rng.standard_normal((K, 1)) * sig
    patt = rng.standard_normal((K, T)) * (0.4 * sig)
    R = area + patt
    v = np.abs(rng.gamma(4.0, noise * sig / 4.0, size=(K, 1))) * np.ones((1, T))
    xi = rng.standard_normal((K, T)) * v
    Rt = rng.standard_normal() * sig + rng.standard_normal(T) * (0.4 * sig)
    return R + xi, v, Rt


def main(out="results/positive_regime.csv"):
    rows = []
    for K in K_GRID:
        for noise in NOISE_GRID:
            for rep in range(REPS):
                rng = np.random.default_rng(det_seed(MASTER, "pos", K, noise, rep))
                E, V, Rt = _draw(K, noise, rng)
                center = np.full(T, 0.5)
                # fixed-center symmetric construction: exact uninflated
                fit = dapcb(E, V, center, alpha=ALPHA, tighten=False,
                            loo_center=False)
                lo, hi = fit.band
                r_half = (hi - lo) / 2.0            # constant clip-free radii here
                cov = int(np.all(np.abs(Rt) <= r_half + 1e-12))
                rows.append(dict(K=K, noise=noise, branch=fit.selected_branch,
                                 cov=cov, width=float(r_half.mean()),
                                 rho_lcb=fit.rho_lcb, delta=fit.delta_ucb,
                                 cov_level=fit.coverage_level))
    df = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    cells = df.groupby(["K", "noise"]).agg(
        coverage=("cov", "mean"), reps=("cov", "size"),
        dec=("branch", lambda s: (s == "deconvolution").mean()),
        con=("branch", lambda s: (s == "conservative").mean()),
        pcb=("branch", lambda s: (s == "PCB").mean()),
        width=("width", "mean"), rho_lcb=("rho_lcb", "mean"),
        cov_level=("cov_level", "mean")).reset_index().round(4)
    # width of the deconvolution draws relative to conservative draws, per cell
    wd = (df[df.branch == "deconvolution"].groupby(["K", "noise"])["width"].mean()
          / df[df.branch == "conservative"].groupby(["K", "noise"])["width"].mean()
          ).rename("w_dec_over_con").round(4)
    cells = cells.merge(wd, on=["K", "noise"], how="left")
    cells.to_csv(out, index=False)

    print(f"E31 positive regime: alpha={ALPHA}, {REPS} reps/cell\n")
    print(cells.to_string(index=False))
    act = cells[cells.dec > 0]
    print(f"\ncells with deconvolution active: {len(act)}/{len(cells)} "
          f"(all at K >= {act.K.min() if len(act) else '-'})")
    if len(act):
        worst = act.coverage.min()
        print(f"worst active-cell coverage {worst:.4f} vs floor "
              f"{(1 - ALPHA - 0.02):.2f}; "
              f"deconv/conservative width {act.w_dec_over_con.mean():.3f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
