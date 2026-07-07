"""E21 — Gate 5E: safe-adaptive selector with a finite-K safety gate.

Preregistered in docs/SAFE_SELECTOR_PROTOCOL.md. Adds the third gate the old
selector lacked — "can we SAFELY use deconvolution at THIS K?" — via the
reliability diagnostic D ≤ τ, with τ calibrated ONCE on a simulation calibration
grid (known truth) to guarantee coverage ≥ 1−α−δ (δ=0.02, floor 0.88), then
FROZEN and evaluated on a DISJOINT grid. Simulation with known truth (same DGP as
E19/E20).

Safe selector (per target, calibration only):
  need     A: ρ̂_LCB > ρ₀
  safety   B: D ≤ τ
  stable   C: s_plug² − mean(v̂²) > floor
  worth-it D: width(safe-deconv) ≤ 0.95·width(conservative)
  all four → safe deconvolution;  A fails → PCB;  else → conservative fallback.

Run:  python -m pcb.experiments.e21_safe_selector
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed
import pandas as pd

from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import (_finite_quantile, deconv_reliability,
                                        deconv_target_scale, rho_lcb)

ALPHA, DELTA, RHO0, Z = 0.10, 0.02, 0.47, 1.645
FLOOR_COV = 1 - ALPHA - DELTA                       # 0.88
S_R, TC = 0.10, 4
KS = [30, 60, 120, 240]
RHO_TRUE = [0.10, 0.25, 0.40, 0.55, 0.70, 0.90, 1.10, 1.40, 1.80]
REPS = 1000


def _one(K, rt, rep, tag):
    """One replication → dict of per-branch coverage/width + gate diagnostics."""
    rng = np.random.default_rng(det_seed(K, rt, rep, tag))
    v = S_R * rt
    E = rng.normal(0, S_R, (K, TC)) + rng.normal(0, v, (K, TC))
    V = np.abs(v * (1 + rng.normal(0, 0.15, (K, TC))))
    Et = rng.normal(0, S_R, TC)
    s = _modulation(E)
    sTs = deconv_target_scale(E, V)
    q_pcb = _finite_quantile(np.max(np.abs(E) / s[None], 1), ALPHA)
    q_dec = _finite_quantile(np.max(np.abs(E) / np.sqrt(sTs[None]**2 + V**2), 1), ALPHA)
    q_con = _finite_quantile(np.max((np.abs(E) + Z * V) / s[None], 1), ALPHA)
    w_pcb, w_dec, w_con = q_pcb * s.mean(), q_dec * sTs.mean(), q_con * s.mean()
    cov_pcb = int(np.max(np.abs(Et) / s) <= q_pcb)
    cov_dec = int(np.max(np.abs(Et) / sTs) <= q_dec)
    cov_con = int(np.max(np.abs(Et) / s) <= q_con)
    stable = (s**2 - (V**2).mean(0) > (0.05 * s.max())**2).all()
    return dict(K=K, rho_true=rt, rlcb=rho_lcb(E, V), D=deconv_reliability(E, V),
                stable=bool(stable), w_pcb=w_pcb, w_dec=w_dec, w_con=w_con,
                cov_pcb=cov_pcb, cov_dec=cov_dec, cov_con=cov_con)


def _grid(tag):
    return pd.DataFrame([_one(K, rt, rep, tag)
                         for K in KS for rt in RHO_TRUE for rep in range(REPS)])


def _would_activate(df, tau):
    return ((df.rlcb > RHO0) & (df.D <= tau) & df.stable
            & (df.w_dec <= 0.95 * df.w_con))


def calibrate_tau(cal):
    """Largest τ s.t. reps that would activate with D≤τ have deconv cov ≥ FLOOR."""
    cand = cal[(cal.rlcb > RHO0) & cal.stable & (cal.w_dec <= 0.95 * cal.w_con)]
    if len(cand) == 0:
        return 0.0
    cand = cand.sort_values("D")
    cov = cand.cov_dec.expanding().mean().to_numpy()      # coverage of D≤ prefix
    ok = np.where(cov >= FLOOR_COV)[0]
    return float(cand.D.to_numpy()[ok[-1]]) if len(ok) else 0.0


def apply_safe(df, tau):
    act = _would_activate(df, tau)
    branch = np.where(act, "deconv",
                      np.where(df.rlcb > RHO0, "conservative", "PCB"))
    cov = np.where(branch == "deconv", df.cov_dec,
                   np.where(branch == "conservative", df.cov_con, df.cov_pcb))
    width = np.where(branch == "deconv", df.w_dec,
                     np.where(branch == "conservative", df.w_con, df.w_pcb))
    out = df.assign(branch=branch, cov_safe=cov, w_safe=width)
    return out


def main():
    os.makedirs("results", exist_ok=True)
    cal = _grid("calib")
    tau = calibrate_tau(cal)
    ev = apply_safe(_grid("eval"), tau)
    ev.to_csv("results/safe_selector_grid.csv", index=False)

    print(f"Safe-adaptive selector (calibrated τ = {tau:.3f} on disjoint grid; "
          f"ρ₀={RHO0}, floor {FLOOR_COV})\n")
    g = ev.groupby(["K", "rho_true"])
    tab = g.agg(rho_hat=("rlcb", "mean"), cov_safe=("cov_safe", "mean"),
                cov_deconv_alone=("cov_dec", "mean"),
                pct_deconv=("branch", lambda s: (s == "deconv").mean() * 100),
                pct_cons=("branch", lambda s: (s == "conservative").mean() * 100),
                w_safe=("w_safe", "mean"), w_con=("w_con", "mean"),
                w_pcb=("w_pcb", "mean")).reset_index()
    tab["cov_ok"] = np.where(tab.cov_safe >= FLOOR_COV - 0.01, "ok", "LOW")
    pd.set_option("display.width", 240, "display.float_format", lambda x: f"{x:.3f}")
    for K in KS:
        print(f"--- K = {K} ---")
        print(tab[tab.K == K][["rho_true", "cov_safe", "cov_deconv_alone",
                               "pct_deconv", "pct_cons", "w_safe", "w_con",
                               "cov_ok"]].to_string(index=False))
        print()
    worst = tab.cov_safe.min()
    print(f"WORST safe coverage over all cells: {worst:.3f} "
          f"(floor {FLOOR_COV}); cells below floor: "
          f"{int((tab.cov_safe < FLOOR_COV - 0.01).sum())}/{len(tab)}")
    lo = ev[ev.rlcb <= RHO0]
    print(f"low-ρ safe width / PCB width: {(lo.w_safe / lo.w_pcb).mean():.3f}")
    hiK = ev[(ev.K == 240) & (ev.rho_true >= 0.7) & (ev.branch == 'deconv')]
    if len(hiK):
        print(f"K=240 high-ρ activated-deconv width / conservative: "
              f"{(hiK.w_safe / hiK.w_con).mean():.3f}")


if __name__ == "__main__":
    main()
