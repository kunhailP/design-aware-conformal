"""E33 — fresh sealed validation of the FINAL deployed pipeline.

The original holdout (E22) was compromised as confirmation: its sealed run
scored a band the package does not deploy, its failures motivated the switch to
the U0 base band and the Theorem 5' architecture, and its sealed config was not
preserved. E22's corrected-scorer rerun therefore validates the final pipeline
on a grid its own design process had seen. This experiment is the genuinely
fresh seal the final pipeline had not had:

  * SIX DGP families disjoint from E22's ten (lognormal country effects,
    AR(2) rounds, scale-mixture countries, extreme design-effect dispersion,
    threshold-correlated design noise, long trajectories with few thresholds);
  * a K grid {20, 30, 50, 120, 250} and rho_gen grid {0.15, 0.35, 0.55, 0.75}
    disjoint from E22's values except at the K=94 feasibility boundary's
    neighborhood; 600 reps per cell; a fresh master seed fixed in this file
    BEFORE the first execution (sha256 of this file at seal time recorded in
    configs/final_validation_manifest.json).
  * Run ONCE; results reported as produced, pass or fail.

Criteria (preregistered here): F1 every cell's coverage within 2 MC-SE of its
guarantee floor (1 - alpha at K < 94; 1 - alpha - delta_ucb mean at K >= 94);
F2 deconvolution never activates at K < 94 (must be 0 by the algorithmic
floor); F3 low-noise cells' width within 1.05x of plain U0 PCB.

Run:  python -m pcb.experiments.e33_final_validation
Output: results/final_validation.csv
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.dapcb import dapcb, gate_b_feasible

ALPHA = 0.10
T = 6
REPS = 600
K_GRID = [20, 30, 50, 120, 250]
RHO_GRID = [0.15, 0.35, 0.55, 0.75]
MASTER = 33_2026_0717          # sealed with this file; do not change after first run
S_R = 0.1
FAMILIES = ["lognormal_country", "ar2_rounds", "scale_mixture",
            "extreme_deff", "corr_noise", "long_traj"]


def _gen(fam, K, rho, rng):
    L = 12 if fam == "long_traj" else T
    if fam == "lognormal_country":
        R = (np.exp(rng.standard_normal((K, L)) * 0.6) - np.exp(0.18)) * S_R
        Rt = (np.exp(rng.standard_normal(L) * 0.6) - np.exp(0.18)) * S_R
    elif fam == "ar2_rounds":
        # SEAL-2 AMENDMENT (disclosed): the first sealed run normalized each
        # generated batch by its own sample SD — the (1, L) target batch by the
        # SD of a single autocorrelated trajectory — an asymmetry between
        # target and calibration that violates exchangeability in the
        # GENERATOR (caught because an exact-at-any-K guarantee failed at
        # K=20, which no valid DGP can produce). Normalization is now the
        # analytic stationary SD, a deterministic constant, symmetric for all
        # units. Both runs are reported in docs/FINAL_VALIDATION_RESULTS.md.
        AR2_SD = 1.4979    # stationary SD of x_t = .5x_{t-1} + .3x_{t-2} + e_t
        def ar2(n, L):
            x = np.zeros((n, L + 2))
            e = rng.standard_normal((n, L + 2))
            for j in range(2, L + 2):
                x[:, j] = 0.5 * x[:, j - 1] + 0.3 * x[:, j - 2] + e[:, j]
            return x[:, 2:] / AR2_SD * S_R
        R, Rt = ar2(K, L), ar2(1, L)[0]
    elif fam == "scale_mixture":
        sc = np.where(rng.random((K, 1)) < 0.2, 2.0, 0.75) * S_R
        R = rng.standard_normal((K, L)) * sc
        Rt = rng.standard_normal(L) * (2.0 if rng.random() < 0.2 else 0.75) * S_R
    else:
        R = rng.standard_normal((K, L)) * S_R
        Rt = rng.standard_normal(L) * S_R
    v = S_R * rho
    if fam == "extreme_deff":
        vc = v * rng.lognormal(0, 0.9, (K, 1))
    else:
        vc = np.full((K, 1), v)
    if fam == "corr_noise":
        sh = rng.standard_normal((K, 1))
        xi = (np.sqrt(0.6) * sh + np.sqrt(0.4) * rng.standard_normal((K, L))) * vc
    else:
        xi = rng.standard_normal((K, L)) * vc
    V = np.abs(vc * (1 + rng.normal(0, 0.15, (K, L))))
    return R + xi, V, Rt


def main(out="results/final_validation.csv"):
    rows = []
    for fam in FAMILIES:
        for K in K_GRID:
            for rho in RHO_GRID:
                for rep in range(REPS):
                    rng = np.random.default_rng(det_seed(MASTER, fam, K,
                                                         int(rho * 100), rep))
                    E, V, Rt = _gen(fam, K, rho, rng)
                    L = E.shape[1]
                    center = np.full(L, 0.5)
                    fit = dapcb(E, V, center, alpha=ALPHA, tighten=False)
                    lo, hi = fit.band
                    r_half = (hi - lo) / 2.0
                    rows.append(dict(family=fam, K=K, rho=rho,
                                     branch=fit.selected_branch,
                                     cov=int(np.all(np.abs(Rt) <= r_half + 1e-12)),
                                     cov_level=fit.coverage_level,
                                     w=float(r_half.mean())))
        print(f"  done {fam}")
    df = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    cells = df.groupby(["family", "K", "rho"]).agg(
        coverage=("cov", "mean"), reps=("cov", "size"),
        cov_level=("cov_level", "mean"),
        dec=("branch", lambda s: (s == "deconvolution").mean()),
        con=("branch", lambda s: (s == "conservative").mean()),
        w=("w", "mean")).reset_index().round(4)
    cells.to_csv(out, index=False)
    mc2 = 2 * np.sqrt(cells.cov_level * (1 - cells.cov_level) / cells.reps)
    f1 = (cells.coverage >= cells.cov_level - mc2)
    f2 = ((cells.K >= 94) | (cells.dec == 0)).all()
    print(f"\nF1 floor-compatible: {int(f1.sum())}/{len(cells)}  "
          f"worst cell {cells.coverage.min():.4f}")
    if (~f1).any():
        print(cells[~f1].to_string(index=False))
    print(f"F2 no deconv below K=94: {'PASS' if f2 else 'FAIL'}")
    dcells = cells[cells.dec > 0]
    print(f"deconv-active cells: {len(dcells)} (K values: "
          f"{sorted(dcells.K.unique()) if len(dcells) else '-'})")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
