"""E10 — Gate 4A: modulation validity for the clustered trajectory band.

Purpose: separate the EMPIRICAL recovery of pooled in-sample modulation
(27/30 in E9) from FINITE-SAMPLE EXACT validity. Naming discipline enforced
throughout the codebase and docs:

  U0  unstudentized score  R_c = max_{r,t}|E|          — exact (no scale)
  S1  independent split modulation (s from a disjoint modulation-country
      set, fixed for calibration and target)           — exact studentized
  S2  pooled in-sample modulation                      — EMPIRICAL variant
  S3  slotwise in-sample modulation                    — EMPIRICAL, fails

Only U0 and S1 may be described as finite-sample exact; S2/S3 are never
called exact-valid.

Three arms:
  (a) ESS L=4 trajectories, LOCO over countries       -> modulation_validity_ess.csv
  (b) simulation of self-inclusion shrinkage over
      K in {20,30,50,100} x L in {1,2,4,8}, T=10,
      homo/heteroskedastic thresholds                 -> modulation_simulation.csv
  (c) single-round curve estimand REDEFINED with a common forecasting
      horizon (one-step-ahead onto a fixed target round), replacing the
      mixed 'latest available round' of E9; plus the decomposition of the
      old stfdem 30/35 misses.

Run:  python -m pcb.experiments.e10_modulation_validity
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed

from pcb.util import det_seed
import pandas as pd

from pcb.data.ess_panel import OUT as PANEL_PATH, T_GRID
from pcb.experiments.e7_ess_gate2 import curves, locf_pairs
from pcb.inference.conformal_band import _modulation
from pcb.inference.fixed_trajectory_band import (slot_modulation,
                                                 stack_trajectories,
                                                 trajectory_modulation,
                                                 trajectory_quantile)

ALPHA = 0.10
L = 4
N_SPLITS = 20           # random modulation/calibration splits averaged in S1
MOD_FRAC = 1 / 3        # share of calibration countries used as modulation set

REGION = {  # coarse ESS regions for the miss decomposition
    "AT": "West", "BE": "West", "CH": "West", "DE": "West", "FR": "West",
    "GB": "West", "IE": "West", "LU": "West", "NL": "West",
    "DK": "North", "FI": "North", "IS": "North", "NO": "North", "SE": "North",
    "CY": "South", "ES": "South", "GR": "South", "IT": "South", "PT": "South",
    "IL": "South", "TR": "South", "MT": "South",
    "BG": "East", "CZ": "East", "EE": "East", "HR": "East", "HU": "East",
    "LT": "East", "LV": "East", "ME": "East", "MK": "East", "PL": "East",
    "RO": "East", "RS": "East", "RU": "East", "SI": "East", "SK": "East",
    "UA": "East", "AL": "East", "XK": "East", "GE": "East",
}


def _score_stats(scores):
    return dict(cal_mean=float(np.mean(scores)),
                cal_q50=float(np.quantile(scores, .5)),
                cal_q90=float(np.quantile(scores, .9)))


# ---------------------------------------------------------------- (a) ESS arm

def ess_arm(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in ("trstprl", "stfdem"):
        pairs = locf_pairs(panel, outcome)
        th_hat = pairs[[f"hat_t{t}" for t in range(T_GRID)]].to_numpy()
        E = th_hat - curves(pairs, outcome)
        traj, labels, _ = stack_trajectories(
            E, pairs.cntry.to_numpy(), pairs.essround.to_numpy(), L)
        Kc = len(labels)
        for i, c in enumerate(labels):
            cal = traj[np.arange(Kc) != i]
            tgt = traj[i]
            for method in ("U0", "S1", "S2", "S3"):
                if method == "S1":
                    rng = np.random.default_rng(det_seed(outcome, c))
                    covs, wids, ratios, stats = [], [], [], []
                    n_mod = max(8, int(MOD_FRAC * len(cal)))
                    for _ in range(N_SPLITS):
                        perm = rng.permutation(len(cal))
                        s = slot_modulation(cal[perm[:n_mod]])
                        cs = np.max(np.abs(cal[perm[n_mod:]]) / s, axis=(1, 2))
                        q, m, attain = trajectory_quantile(cs, ALPHA)
                        sc = float(np.max(np.abs(tgt) / s))
                        covs.append(sc <= q)
                        wids.append(2 * q * s.mean())
                        ratios.append(np.mean(cs) / sc)
                        stats.append(_score_stats(cs))
                    rec = dict(covered=float(np.mean(covs)),
                               mean_width=float(np.mean(wids)),
                               eff_K=len(cal) - n_mod, attainable=attain,
                               target_score=np.nan,
                               cal_target_ratio=float(np.mean(ratios)),
                               **{k: float(np.mean([s[k] for s in stats]))
                                  for k in stats[0]})
                else:
                    kind = {"U0": "none", "S2": "pooled",
                            "S3": "per_slot"}[method]
                    s = trajectory_modulation(cal, kind)
                    cs = np.max(np.abs(cal) / s[None], axis=(1, 2))
                    q, m, attain = trajectory_quantile(cs, ALPHA)
                    sc = float(np.max(np.abs(tgt) / s))
                    rec = dict(covered=float(sc <= q),
                               mean_width=float(2 * q * s.mean()),
                               eff_K=len(cal), attainable=attain,
                               target_score=sc,
                               cal_target_ratio=float(np.mean(cs) / sc),
                               **_score_stats(cs))
                rows.append(dict(outcome=outcome, method=method, target=c,
                                 **rec))
    return pd.DataFrame(rows)


# -------------------------------------------------------- (b) simulation arm

def simulate_cell(K, L_, T=10, hetero=False, reps=1000, seed=0):
    """E_crt = a_c + b_cr + u_crt; heteroskedastic thresholds optional."""
    rng = np.random.default_rng(seed)
    h = np.linspace(0.4, 1.6, T) if hetero else np.ones(T)
    a = rng.normal(0, 0.03, size=(reps, K + 1, 1, 1))
    b = rng.normal(0, 0.02, size=(reps, K + 1, L_, 1))
    u = rng.normal(0, 0.015, size=(reps, K + 1, L_, T)) * h
    E = a + b + u
    cal, tgt = E[:, :K], E[:, K]

    n_mod = max(8, int(MOD_FRAC * K))
    out = []
    for method in ("U0", "S1", "S2", "S3"):
        if method == "U0":
            s = np.ones((reps, L_, T))
            C = cal
        elif method == "S1":
            mod, C = cal[:, :n_mod], cal[:, n_mod:]
            s = np.maximum(mod.std(1), 1e-8)                      # (reps,L,T)
            s = np.maximum(s, 0.05 * s.max(axis=(1, 2), keepdims=True))
        elif method == "S2":
            flat = cal.reshape(reps, K * L_, T)
            s2 = np.maximum(flat.std(1), 1e-8)                    # (reps,T)
            s2 = np.maximum(s2, 0.05 * s2.max(1, keepdims=True))
            s = np.repeat(s2[:, None, :], L_, axis=1)
            C = cal
        else:  # S3
            s = np.maximum(cal.std(1), 1e-8)                      # (reps,L,T)
            s = np.maximum(s, 0.05 * s.max(axis=(1, 2), keepdims=True))
            C = cal
        cs = np.max(np.abs(C) / s[:, None], axis=(2, 3))          # (reps,Kc)
        Kc = cs.shape[1]
        m = int(np.ceil((1 - ALPHA) * (Kc + 1)))
        q = np.sort(cs, axis=1)[:, m - 1] if m <= Kc \
            else np.full(reps, np.inf)
        ts = np.max(np.abs(tgt) / s, axis=(1, 2))                 # (reps,)
        slot_cov = (np.max(np.abs(tgt) / s, axis=2)
                    <= q[:, None]).mean()                          # round level
        out.append(dict(
            method=method, K=K, L=L_, T=T,
            hetero=int(hetero), eff_K=Kc,
            attainable=round(min(1.0, m / (Kc + 1)), 3),
            coverage=float((ts <= q).mean()),
            round_cov=float(slot_cov),
            mean_width=float(np.mean(2 * q[:, None, None] * s)),
            max_width=float(np.mean(np.max(2 * q[:, None, None] * s,
                                           axis=(1, 2)))),
            cal_mean=float(cs.mean()), cal_q90=float(np.quantile(cs, .9)),
            tgt_mean=float(ts.mean()),
            cal_target_ratio=float(cs.mean() / ts.mean())))
    return out


def simulation_arm() -> pd.DataFrame:
    rows = []
    for K in (20, 30, 50, 100):
        for L_ in (1, 2, 4, 8):
            for hetero in (False, True):
                rows += simulate_cell(K, L_, hetero=hetero,
                                      seed=1000 * K + 10 * L_ + hetero)
    return pd.DataFrame(rows)


# ------------------------- (c) common-horizon single-round + stfdem decomposition

def common_horizon_curve(panel: pd.DataFrame) -> pd.DataFrame:
    """Estimand A2: one-step-ahead onto a COMMON target round r*.

    Every country predicts round r* from round r*−1; countries lacking either
    round are excluded. Same horizon, same calendar period, one score per
    country — replaces E9's mixed latest-available-round design.
    """
    rows = []
    for outcome in ("trstprl", "stfdem"):
        for r_star in (10, 11):
            sub = panel[panel.essround.isin((r_star - 1, r_star))]
            counts = sub.groupby("cntry", observed=True).essround.nunique()
            ok = counts[counts == 2].index
            sub = sub[sub.cntry.isin(ok)].sort_values(["cntry", "essround"])
            prev = curves(sub[sub.essround == r_star - 1], outcome)
            now = curves(sub[sub.essround == r_star], outcome)
            E = prev - now                    # LOCF error, homogeneous horizon
            n = len(ok)
            for meth, kind in (("U0", "none"), ("S2", "pooled")):
                cov = []
                for i in range(n):
                    cal = np.delete(E, i, axis=0)
                    s = np.ones(E.shape[1]) if kind == "none" \
                        else _modulation(cal)
                    cs = np.max(np.abs(cal) / s, axis=1)
                    q, m, attain = trajectory_quantile(cs, ALPHA)
                    cov.append(float(np.max(np.abs(E[i]) / s) <= q))
                rows.append(dict(outcome=outcome, estimand=f"A2_r{r_star}",
                                 method=meth, countries=n,
                                 covered=int(np.sum(cov)),
                                 coverage=round(float(np.mean(cov)), 3),
                                 attainable=round(attain, 3)))
    return pd.DataFrame(rows)


def stfdem_decomposition(panel: pd.DataFrame) -> pd.DataFrame:
    """Decompose the E9 A-curve stfdem misses (old latest-round design)."""
    audit = pd.read_csv("results/ess_cluster_exact_audit.csv")
    a = audit[(audit.estimand == "A_curve") & (audit.outcome == "stfdem")]
    pairs = locf_pairs(panel, "stfdem")
    latest = pairs.sort_values("essround").groupby("cntry", observed=True).tail(1)
    latest = latest.set_index("cntry")
    rec = a.set_index("target").join(latest[["essround", "gap"]])
    rec["region"] = [REGION.get(c, "?") for c in rec.index]
    rec["shock_note"] = np.where(rec.essround <= 5, "pre-2012 exit",
                                 np.where(rec.gap > 1, "gap>1 round", ""))
    return rec.reset_index()[["target", "covered", "essround", "gap",
                              "region", "shock_note", "target_score",
                              "critical"]]


def main():
    panel = pd.read_parquet(PANEL_PATH)
    os.makedirs("results", exist_ok=True)

    ess = ess_arm(panel)
    ess.to_csv("results/modulation_validity_ess.csv", index=False)
    summ = ess.groupby(["outcome", "method"]).agg(
        coverage=("covered", "mean"), eff_K=("eff_K", "first"),
        attainable=("attainable", "first"), width=("mean_width", "mean"),
        cal_target_ratio=("cal_target_ratio", "mean")).round(3)
    print("=== (a) ESS L=4 trajectory, modulation comparison ===")
    print(summ.to_string())

    sim = simulation_arm()
    sim.to_csv("results/modulation_simulation.csv", index=False)
    print("\n=== (b) simulation: coverage by K (L=4, heteroskedastic) ===")
    v = sim[(sim.L == 4) & (sim.hetero == 1)]
    print(v.pivot_table(index="K", columns="method",
                        values="coverage").round(3).to_string())
    print("\ncal/target score ratio (self-inclusion shrinkage), L=4 hetero:")
    print(v.pivot_table(index="K", columns="method",
                        values="cal_target_ratio").round(3).to_string())

    a2 = common_horizon_curve(panel)
    a2.to_csv("results/modulation_validity_ess.csv", mode="a", index=False)
    print("\n=== (c) common-horizon single-round estimand (A2) ===")
    print(a2.to_string(index=False))

    dec = stfdem_decomposition(panel)
    print("\n=== stfdem A-curve miss decomposition (old design) ===")
    print(dec[dec.covered == 0].to_string(index=False))


if __name__ == "__main__":
    main()
