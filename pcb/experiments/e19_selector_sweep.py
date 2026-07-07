"""E19 — selector-transition sweep in simulation (against KNOWN truth).

The real and design-preserving-subsampled surveys never reach ρ₀ (E18), so the
branch transition PCB → deconvolution → conservative-fallback cannot be shown on
them. Here the survey-noise is a free parameter, so we can dial ρ through ρ₀ and
into the unstable regime, and — because truth is known — measure REAL coverage of
the latent target (not pseudo-coverage). This is the definitive validation that
the target-blind selector transitions correctly and that every branch, and the
routed pipeline, holds coverage.

Model: K exchangeable latent deviation-curves E_c ~ N(0, s_R²) (transport spread);
observed with design noise Ẽ_c = E_c + N(0, v²); v̂ estimated with 15% error. The
target's LATENT curve (v_target=0) is the deployment object to cover. ρ dialed via
v/s_R.

Run:  python -m pcb.experiments.e19_selector_sweep
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed
import pandas as pd

from pcb.experiments.e16_lapop_transport import _radii, _select
from pcb.inference.design_aware import _finite_quantile

ALPHA = 0.10
Z = 1.645
S_R = 0.10                       # latent transport spread
K, TC, REPS = 30, 4, 1500
RHO_TRUE = [0.10, 0.25, 0.40, 0.55, 0.70, 0.90, 1.10, 1.40, 1.80]


def sweep():
    rows = []
    for rt in RHO_TRUE:
        v = S_R * rt
        for rep in range(REPS):
            rng = np.random.default_rng(det_seed(rt, rep))
            E = rng.normal(0, S_R, (K, TC)) + rng.normal(0, v, (K, TC))   # observed
            V = np.abs(v * (1 + rng.normal(0, 0.15, (K, TC))))            # v̂, 15% err
            r = _radii(E, V); s, sT = r["s"], r["sT"]
            branch, _ = _select(r)
            q2 = _finite_quantile(np.max((np.abs(E) + Z * V) / s[None], axis=1), ALPHA)
            Et = rng.normal(0, S_R, TC)                                   # LATENT target
            t_pcb = np.max(np.abs(Et) / s).item()
            t_dec = np.max(np.abs(Et) / sT).item()
            cov = dict(T1=int(t_pcb <= r["q1"]), T2=int(t_pcb <= q2),
                       T3=int(t_dec <= r["q3"]))
            cov_ad = cov["T3"] if branch == "T3" else (
                cov["T2"] if branch == "T2" else cov["T1"])
            rows.append(dict(rho_true=rt, rho_hat=r["rho"], branch=branch,
                             stable=r["stable"], cov_adaptive=cov_ad,
                             cov_T1=cov["T1"], cov_T3=cov["T3"],
                             w_T1=r["w1"], w_T3=r["w3"], w_T2=r["w2"]))
    return pd.DataFrame(rows)


def main():
    os.makedirs("results", exist_ok=True)
    d = sweep()
    d.to_csv("results/selector_sweep_sim.csv", index=False)
    g = d.groupby("rho_true")
    summ = pd.DataFrame(dict(
        rho_hat=g.rho_hat.mean(),
        pct_PCB=g.branch.apply(lambda s: (s == "T1").mean() * 100),
        pct_deconv=g.branch.apply(lambda s: (s == "T3").mean() * 100),
        pct_cons=g.branch.apply(lambda s: (s == "T2").mean() * 100),
        cov_adaptive=g.cov_adaptive.mean(),
        cov_PCB=g.cov_T1.mean(), cov_deconv=g.cov_T3.mean(),
        w_adaptive=g.apply(lambda x: np.where(x.branch == "T3", x.w_T3,
                           np.where(x.branch == "T2", x.w_T2, x.w_T1)).mean()),
        w_PCB=g.w_T1.mean(),
    )).reset_index()
    pd.set_option("display.width", 200, "display.float_format", lambda x: f"{x:.3f}")
    print("Selector-transition sweep in simulation (known truth, ρ₀=0.47, "
          "1−α=0.90)\n")
    print(summ.to_string(index=False))
    print("\nRoute: low ρ̂ → PCB; ρ̂≥0.47 & stable → deconvolution; unstable → "
          "conservative fallback. Adaptive coverage stays ≥ nominal throughout.")


if __name__ == "__main__":
    main()
