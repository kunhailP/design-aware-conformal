"""E25 — small-K base-band correction validation (preregistered SMALLK_CORRECTION_PREREG).

The frozen holdout (E22) exposed that the *studentized* base band (S2, in-sample pooled
modulation) undercovers at small K (worst 0.843). The preregistered fix is to deploy the
UNSTUDENTIZED clustered conformal band (U0), which is finite-sample exact at any K:
P(cover) ≥ ⌈(1−α)(K+1)⌉/(K+1) ≥ 1−α by exchangeability. This confirms the fix ONCE on a
fresh grid (new K, disjoint seed salt), reporting U0 vs S2 exactly as produced.

Run:  python -m pcb.experiments.e25_smallk_validation
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.experiments.e22_holdout_validation import _gen
from pcb.inference.design_aware import _finite_quantile
from pcb.inference.conformal_band import _modulation

ALPHA = 0.10
S_R = 0.10
T = 4
REPS = 3000
KS = [15, 20, 25, 30, 40, 60]                 # fresh, dense at small K
RHOS = [0.10, 0.25]                           # low-ρ base-band regime
FAMILIES = ("gaussian", "skewed_noise", "heavy_tail_country", "hetero_design_var",
            "unequal_psu", "unequal_weights", "irregular_length", "noise_misspec",
            "weak_dep_rounds", "strong_dep_rounds")


def _cell(fam, K, rho):
    L = T * 3 if fam.endswith("dep_rounds") else T
    c_s2 = c_u0 = 0
    w_s2 = w_u0 = 0.0
    for rep in range(REPS):
        rng = np.random.default_rng(det_seed("e25_smallk", fam, K, rho, rep))
        E, V, Et = _gen(fam, K, L, S_R, rho, rng)
        # S2: in-sample pooled modulation (studentized)
        s = _modulation(E)
        q2 = _finite_quantile(np.max(np.abs(E) / s, 1), ALPHA)
        c_s2 += int(np.max(np.abs(Et) / s) <= q2); w_s2 += q2 * s.mean()
        # U0: unstudentized (exact)
        q0 = _finite_quantile(np.max(np.abs(E), 1), ALPHA)
        c_u0 += int(np.max(np.abs(Et)) <= q0); w_u0 += q0
    m = int(np.ceil((1 - ALPHA) * (K + 1)))
    return dict(family=fam, K=K, rho=rho, L=L, reps=REPS,
                cov_S2=c_s2 / REPS, cov_U0=c_u0 / REPS,
                w_S2=w_s2 / REPS, w_U0=w_u0 / REPS,
                vovk_floor=m / (K + 1),
                mc_se=np.sqrt(0.9 * 0.1 / REPS))


def main():
    os.makedirs("results", exist_ok=True)
    rows = [_cell(f, K, r) for f in FAMILIES for K in KS for r in RHOS]
    d = pd.DataFrame(rows)
    d["w_ratio"] = d.w_U0 / d.w_S2
    d.to_csv("results/smallk_validation.csv", index=False)

    # preregistered criteria
    c1 = bool((d.cov_U0 >= d.vovk_floor - 2 * d.mc_se).all())
    d20 = d[d.K >= 20]
    c2 = bool((d20.cov_U0 >= 0.88).all() and (d.cov_U0 >= d.cov_S2 - 1e-9).all())
    c3 = bool((d.w_ratio <= 1.10).all())

    pd.set_option("display.width", 200, "display.max_rows", 300,
                  "display.float_format", lambda x: f"{x:.3f}")
    print("E25 small-K correction validation (U0 exact vs S2 studentized), α=0.10, "
          f"{REPS} reps/cell, {len(d)} cells\n")
    print("worst cells by U0 coverage:")
    print(d.sort_values("cov_U0")[["family", "K", "rho", "cov_S2", "cov_U0",
                                   "vovk_floor", "w_ratio"]].head(12).to_string(index=False))
    print(f"\nS2 worst cell coverage = {d.cov_S2.min():.3f} "
          f"({d.loc[d.cov_S2.idxmin(),'family']} K={d.loc[d.cov_S2.idxmin(),'K']} "
          f"ρ={d.loc[d.cov_S2.idxmin(),'rho']})")
    print(f"U0 worst cell coverage = {d.cov_U0.min():.3f} "
          f"({d.loc[d.cov_U0.idxmin(),'family']} K={d.loc[d.cov_U0.idxmin(),'K']} "
          f"ρ={d.loc[d.cov_U0.idxmin(),'rho']})")
    print(f"U0/S2 width ratio: min {d.w_ratio.min():.3f}  mean {d.w_ratio.mean():.3f}  "
          f"max {d.w_ratio.max():.3f}")
    print(f"\nC1 (U0 ≥ Vovk floor − 2·MC-SE, all cells): {c1}")
    print(f"C2 (U0 ≥ 0.88 for K≥20 AND U0 ≥ S2 everywhere): {c2}")
    print(f"C3 (U0 width ≤ 1.10× S2, all cells): {c3}")
    print(f"\nVERDICT: {'ADOPT U0' if (c1 and c2 and c3) else 'DO NOT ADOPT — criterion failed'}")


if __name__ == "__main__":
    main()
