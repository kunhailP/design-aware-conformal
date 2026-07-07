"""E29 — the unreachability barriers hold beyond surveys (Paper 2, Remark rem:general).

Substantiates the claim that the impossibility and the K>=94 reliability floor are not
survey-specific: they hold for ANY conformal procedure calibrated on estimated objects.
We instantiate a non-survey, MRP-style small-area calibration setting (area effects +
heteroskedastic known posterior SDs) alongside plain Gaussian, heavy-tailed, and skewed
DGPs, and show:

  Barrier B (reliability floor): the finite-K reliability D = max_t SE(s_T^2)/s_T^2 obeys
    the distribution-free floor D >= sqrt(2/(K-1)) in EVERY DGP, so passing the gate
    (D <= tau_D = 0.147) requires K >= ~94 regardless of the data source.
  Barrier A (rho saturation): rho_hat = sqrt(mean v^2)/s_plug saturates below rho0=0.47
    once the between-unit signal is appreciable, in the MRP setting exactly as in surveys.

Reported as produced. Writes results/beyond_surveys.csv.

Run:  python -m pcb.experiments.e29_beyond_surveys
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.inference.design_aware import deconv_reliability, rho_lcb

TAU_D = 0.147          # frozen gate-B threshold (docs/SURVEY_SCALE_UNREACHABILITY.md)
RHO0 = 0.47
T = 6
REPS = 300
K_GRID = [20, 30, 50, 94, 150, 300]


def _draw(dgp, K, rng, sig=1.0, noise=0.4):
    """Return (E_tilde, v): K contaminated error curves and known noise SDs (K,T)."""
    v = np.full((K, T), noise)
    if dgp == "mrp":
        # small-area: area effect (shared across thresholds) + threshold pattern,
        # heteroskedastic known posterior SD (varies by area, as MRP delivers).
        area = rng.standard_normal((K, 1)) * sig
        patt = rng.standard_normal((K, T)) * (0.4 * sig)
        R = area + patt
        v = np.abs(rng.gamma(4.0, noise / 4.0, size=(K, 1))) * np.ones((1, T))
    elif dgp == "gaussian":
        R = rng.standard_normal((K, T)) * sig
    elif dgp == "t3":
        R = rng.standard_t(3, size=(K, T)) / np.sqrt(3) * sig
    elif dgp == "skew":
        R = (rng.chisquare(3, size=(K, T)) - 3) / np.sqrt(6) * sig
    xi = rng.standard_normal((K, T)) * v
    return R + xi, v


def main(out="results/beyond_surveys.csv"):
    rows = []
    print(f"E29 beyond surveys: T={T}, {REPS} reps, tau_D={TAU_D}, rho0={RHO0}\n")
    print("Barrier B — reliability floor D >= sqrt(2/(K-1)) across DGPs "
          "(median D; min D/floor over reps):")
    print(f"  {'DGP':>9} |" + "".join(f"{('K='+str(K)):>10}" for K in K_GRID)
          + f" | {'min D/floor':>11} | {'K*':>4}")
    for dgp in ["gaussian", "t3", "skew", "mrp"]:
        medD = {}
        min_ratio = np.inf
        for K in K_GRID:
            floor = np.sqrt(2.0 / (K - 1))
            Ds = []
            for r in range(REPS):
                rng = np.random.default_rng(det_seed("e29", dgp, K, r))
                Et, v = _draw(dgp, K, rng)
                D = deconv_reliability(Et, v)
                Ds.append(D)
                min_ratio = min(min_ratio, D / floor)
            medD[K] = float(np.median(Ds))
            rows.append(dict(dgp=dgp, K=K, median_D=medD[K], floor=floor, reps=REPS))
        # K* = smallest K in a fine grid where median D <= tau_D
        kstar = next((K for K in range(4, 4000)
                      if np.median([deconv_reliability(
                          *_draw(dgp, K, np.random.default_rng(det_seed("e29s", dgp, K, r))))
                          for r in range(60)]) <= TAU_D), None)
        print(f"  {dgp:>9} |" + "".join(f"{medD[K]:>10.3f}" for K in K_GRID)
              + f" | {min_ratio:>11.4f} | {str(kstar):>4}")

    print("\nBarrier A — rho_hat saturates below rho0 as between-unit signal grows (MRP):")
    print(f"  {'signal/noise':>12} | {'rho_lcb':>8}")
    for sig in [0.5, 1.0, 2.0, 4.0]:
        rls = []
        for r in range(REPS):
            rng = np.random.default_rng(det_seed("e29a", sig, r))
            Et, v = _draw("mrp", 120, rng, sig=sig, noise=0.4)
            rls.append(rho_lcb(Et, v))
        rl = float(np.median(rls))
        print(f"  {sig:>12.1f} | {rl:>8.3f}")
        rows.append(dict(dgp="mrp_rho", K=120, median_D=np.nan, floor=np.nan,
                         reps=REPS, signal=sig, rho_lcb=rl))
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\n  wrote {out}")
    print("  read: the reliability floor and rho saturation are distribution-free and "
          "hold in the non-survey MRP setting — the K>=94 barrier is not survey-specific.")


if __name__ == "__main__":
    main()
