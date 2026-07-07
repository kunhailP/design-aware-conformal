"""E2 driver — run the simulation grid; collect coverage/width per cell.

For each cell, repeat R times: draw populations → fit a fixed base predictor on
pooled SOURCE households → compute every interval procedure (M0–M3) → record
whether the TARGET population's true headcount is covered, plus width. The
exchangeable unit is the population: calibration uses the K source transport
errors, the target is the held-out (K+1)-th draw.

Also records the Proposition 1 prediction for naive (M0) coverage so the §4
formula can be checked against the empirical M0 collapse.

CPU-bound; no GPU. Run:  python -m pcb.simulation.run_sim_grid
"""
from __future__ import annotations
from itertools import product
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LinearRegression

from .generate_populations import SimConfig, generate_population_hierarchy
from ..inference.headcount import weighted_headcount
from ..inference.bootstrap_intervals import within_pop_bootstrap_se
from ..inference.population_conformal import population_conformal_interval
from ..inference.variance_inflation import variance_inflation_interval
from ..inference.weighted_conformal import (
    population_distance, distance_to_weights, weighted_conformal_interval)

Z = 1.645          # 90% nominal
B_BOOT = 50        # within-pop bootstrap reps (SE only)
METHODS = ["M0", "M1", "M2", "M3"]


def _fit_predict(sim):
    """Fixed base predictor: linear log-consumption on X, trained on sources."""
    pops, K = sim["pops"], sim["K"]
    Xtr = np.vstack([p["X"] for p in pops[:K]])
    ytr = np.concatenate([np.log(p["y"]) for p in pops[:K]])
    m = LinearRegression().fit(Xtr, ytr)
    return [np.exp(m.predict(p["X"])) for p in pops]


def _errors(sim, preds):
    thr, pops = sim["thresholds"], sim["pops"]
    E = np.zeros((len(pops), len(thr)))
    SE = np.zeros_like(E)
    for i, p in enumerate(pops):
        E[i] = weighted_headcount(preds[i], p["w"], thr) - sim["theta_true"][i]
        SE[i] = within_pop_bootstrap_se(preds[i], p["w"], thr, B=B_BOOT, seed=i)
    return E, SE


def run_config(cfg: SimConfig, reps: int, seed0: int = 0) -> dict:
    """Run one grid cell over `reps` independent population draws."""
    T = cfg.n_thresholds
    cov = {m: [] for m in METHODS}
    wid = {m: [] for m in METHODS}
    ratios, m0_pred = [], []
    for r in range(reps):
        rng = np.random.default_rng(seed0 + 1009 * (r + 1) + cfg.seed)
        sim = generate_population_hierarchy(cfg, rng=rng)
        preds = _fit_predict(sim)
        E, SE = _errors(sim, preds)
        K = sim["K"]
        Es, Et, SEt = E[:K], E[K], SE[K]          # source errors / target error & SE
        sigma_b = Es.std(0)
        bias = Es.mean(0)
        ratios.append(float(sigma_b.mean() / max(SE[:K].mean(), 1e-9)))
        # Proposition 1: predicted naive coverage given measured bias & σ_between
        sig = np.sqrt(sigma_b ** 2 + SEt ** 2)
        m0_pred.append(np.mean(
            norm.cdf((Z * SEt - bias) / sig) - norm.cdf((-Z * SEt - bias) / sig)))

        # M0 naive within-pop
        cov["M0"].append(np.abs(Et) <= Z * SEt); wid["M0"].append(2 * Z * SEt)
        # M1 variance inflation (Gaussian)
        lo1, hi1 = variance_inflation_interval(np.zeros(T), SEt, Es, z=Z)
        cov["M1"].append((Et >= lo1) & (Et <= hi1)); wid["M1"].append(hi1 - lo1)
        # M2 population conformal
        lo2, hi2 = population_conformal_interval(Es, alpha=0.1)
        cov["M2"].append((Et >= lo2) & (Et <= hi2)); wid["M2"].append(hi2 - lo2)
        # M3 shift-weighted conformal
        Xt = sim["pops"][K]["X"]
        dist = [population_distance(sim["pops"][i]["X"], Xt) for i in range(K)]
        lo3, hi3 = weighted_conformal_interval(Es, distance_to_weights(dist), alpha=0.1)
        cov["M3"].append((Et >= lo3) & (Et <= hi3)); wid["M3"].append(hi3 - lo3)

    row = dict(K=cfg.K, shift=cfg.shift, misspec=cfg.misspec,
               threshold_focus=cfg.threshold_focus, n_per_pop=cfg.n_per_pop,
               structured=cfg.structured, reps=reps, ratio=float(np.mean(ratios)),
               cov_M0_pred=float(np.mean(m0_pred)) * 100)
    for m in METHODS:
        row[f"cov_{m}"] = float(np.mean(cov[m])) * 100
        row[f"width_{m}"] = float(np.mean(wid[m]))
    return row


def run_grid(grid: dict, reps: int = 80, base: SimConfig | None = None) -> pd.DataFrame:
    """Sweep `grid` (dict of lists), holding other factors at `base`."""
    base = base or SimConfig()
    keys = list(grid)
    rows = []
    for combo in product(*(grid[k] for k in keys)):
        cfg = SimConfig(**{**base.__dict__, **dict(zip(keys, combo))})
        rows.append(run_config(cfg, reps))
        r = rows[-1]
        print(f"  K={r['K']:>3} shift={r['shift']:<6} mis={r['misspec']:<6} "
              f"ratio={r['ratio']:.1f}x | M0 {r['cov_M0']:4.1f}% "
              f"(pred {r['cov_M0_pred']:4.1f}) | M1 {r['cov_M1']:4.1f}% | "
              f"M2 {r['cov_M2']:4.1f}% | M3 {r['cov_M3']:4.1f}%", flush=True)
    return pd.DataFrame(rows)


def main(out="results/sim_grid.csv"):
    import time
    t0 = time.time()
    print("=== E2-a: K sweep (shift=high, misspec=severe) — H1 collapse, H3 K-growth ===")
    df_k = run_grid({"K": [3, 5, 10, 20, 50]}, reps=80,
                    base=SimConfig(shift="high", misspec="severe", threshold_focus="median"))
    print("\n=== E2-b: shift-type sweep (K=20) — H4 weighted vs uniform ===")
    df_s = run_grid({"shift": ["none", "low", "medium", "high"]}, reps=80,
                    base=SimConfig(K=20, misspec="severe", threshold_focus="median"))
    print("\n=== E2-c: structured vs unstructured shift (K=20, high) — H4 proper test ===")
    df_c = run_grid({"structured": [False, True]}, reps=80,
                    base=SimConfig(K=20, shift="high", misspec="severe", threshold_focus="median"))
    out_df = pd.concat([df_k.assign(sweep="K"), df_s.assign(sweep="shift"),
                        df_c.assign(sweep="structured")], ignore_index=True)
    out_df.to_csv(out, index=False)
    print(f"\nwrote {out}  ({time.time()-t0:.0f}s)")
    return out_df


if __name__ == "__main__":
    main()
