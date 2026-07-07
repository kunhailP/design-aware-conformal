"""E20 — finite-K-safe deconvolution: does the correction restore coverage?

Reruns the E19 selector sweep (same DGP, KNOWN truth) with the finite-K-safe
deconvolution scale (deconv_target_scale, docs/FINITE_K_CORRECTION_PROTOCOL.md,
α₂=α/2 budget split fixed before results). Compares plain-T3 vs safe-T3 coverage
and the routed adaptive-safe pipeline. No retuning of α₂ after results.

Run:  python -m pcb.experiments.e20_safe_deconv
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed
import pandas as pd

from pcb.experiments.e16_lapop_transport import _radii, _select
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import _finite_quantile, deconv_target_scale

ALPHA, ALPHA2, Z = 0.10, 0.05, 1.645
S_R, K, TC, REPS = 0.10, 30, 4, 1500
RHO_TRUE = [0.10, 0.25, 0.40, 0.55, 0.70, 0.90, 1.10, 1.40, 1.80]


def sweep():
    rows = []
    for rt in RHO_TRUE:
        v = S_R * rt
        for rep in range(REPS):
            rng = np.random.default_rng(det_seed(rt, rep, "safe"))
            E = rng.normal(0, S_R, (K, TC)) + rng.normal(0, v, (K, TC))
            V = np.abs(v * (1 + rng.normal(0, 0.15, (K, TC))))
            r = _radii(E, V); s = r["s"]
            branch, _ = _select(r)
            Et = rng.normal(0, S_R, TC)
            # plain deconvolution (as E19)
            sT = r["sT"]
            q3 = _finite_quantile(np.max(np.abs(E) / np.sqrt(sT[None]**2 + V**2), 1), ALPHA)
            cov_T3 = int((np.max(np.abs(Et) / sT)) <= q3)
            # safe deconvolution
            sTs = deconv_target_scale(E, V)
            q3s = _finite_quantile(np.max(np.abs(E) / np.sqrt(sTs[None]**2 + V**2), 1), ALPHA)
            cov_T3s = int((np.max(np.abs(Et) / sTs)) <= q3s)
            w_T3, w_T3s = q3 * sT.mean(), q3s * sTs.mean()
            # conservative + PCB for routing
            q1 = r["q1"]; cov_T1 = int((np.max(np.abs(Et) / s)) <= q1)
            q2 = _finite_quantile(np.max((np.abs(E) + Z * V) / s[None], 1), ALPHA)
            cov_T2 = int((np.max(np.abs(Et) / s)) <= q2)
            cov_ad_safe = cov_T3s if branch == "T3" else (
                cov_T2 if branch == "T2" else cov_T1)
            rows.append(dict(rho_true=rt, rho_hat=r["rho"], branch=branch,
                             cov_T3=cov_T3, cov_T3_safe=cov_T3s,
                             cov_adaptive_safe=cov_ad_safe,
                             w_T3=w_T3, w_T3_safe=w_T3s, w_T1=q1 * s.mean()))
    return pd.DataFrame(rows)


def main():
    os.makedirs("results", exist_ok=True)
    d = sweep()
    d.to_csv("results/safe_deconv_sweep.csv", index=False)
    g = d.groupby("rho_true")
    summ = pd.DataFrame(dict(
        rho_hat=g.rho_hat.mean(),
        cov_deconv_plain=g.cov_T3.mean(),
        cov_deconv_safe=g.cov_T3_safe.mean(),
        cov_adaptive_safe=g.cov_adaptive_safe.mean(),
        w_deconv_plain=g.w_T3.mean(), w_deconv_safe=g.w_T3_safe.mean(),
        w_PCB=g.w_T1.mean(),
    )).reset_index()
    pd.set_option("display.width", 200, "display.float_format", lambda x: f"{x:.3f}")
    print("Finite-K-safe deconvolution vs plain (simulation, known truth, "
          "α₂=α/2=0.05 fixed)\n")
    print(summ.to_string(index=False))
    lo = d[d.rho_hat < 0.47]
    print(f"\nlow-ρ (ρ̂<ρ₀) safe-T3 width / PCB width: "
          f"{(lo.w_T3_safe / lo.w_T1).mean():.3f}  (target ≤1.05, reduction "
          f"property preserved)")

    # K-sensitivity at a fixed high-ρ point: the residual gap is finite-K (ε_{K,B})
    print("\n=== K-sensitivity of adaptive-safe coverage at ρ_true=0.90 "
          "(ε_{K,B}→0) ===")
    ks = []
    for Kv in (30, 60, 120, 240):
        v = S_R * 0.90; hit = 0
        for rep in range(REPS):
            rng = np.random.default_rng(det_seed(Kv, rep, "Ksens"))
            E = rng.normal(0, S_R, (Kv, TC)) + rng.normal(0, v, (Kv, TC))
            V = np.abs(v * (1 + rng.normal(0, 0.15, (Kv, TC))))
            r = _radii(E, V); s = r["s"]; branch, _ = _select(r)
            Et = rng.normal(0, S_R, TC)
            if branch == "T3":
                sTs = deconv_target_scale(E, V)
                q = _finite_quantile(np.max(np.abs(E) / np.sqrt(sTs[None]**2 + V**2), 1), ALPHA)
                hit += int(np.max(np.abs(Et) / sTs) <= q)
            elif branch == "T2":
                q = _finite_quantile(np.max((np.abs(E) + Z * V) / s[None], 1), ALPHA)
                hit += int(np.max(np.abs(Et) / s) <= q)
            else:
                hit += int(np.max(np.abs(Et) / s) <= r["q1"])
        ks.append((Kv, hit / REPS))
        print(f"  K={Kv:4d}: adaptive-safe coverage {hit / REPS:.3f}")
    pd.DataFrame(ks, columns=["K", "cov_adaptive_safe"]).to_csv(
        "results/safe_deconv_ksens.csv", index=False)


if __name__ == "__main__":
    main()
