"""E9 — exact clustered constructions on ESS (gate-3 lock-in).

Two estimands, kept strictly apart (docs/ESS_CLUSTER_THEORY.md):
  A  single-round curve  : one score per country (latest LOCF round);
                           protects one country-round curve.
  B  fixed-L trajectory  : L = 4 most recent rounds per country (main spec);
                           protects the whole recent trajectory.
  S  all-round trajectory: variable-length sup-score — SENSITIVITY only
                           (trajectory-length heterogeneity), plus the audit
                           of the gate-3 31/35 figure.

Every held-out target logs: calibration country count, conformal order index,
attainable level, trajectory length, target sup-score, critical value,
coverage indicator, mean/max width  ->  results/ess_cluster_exact_audit.csv.

Predictor is LOCF (temporal transport). LOCF fits nothing: the prediction for
(c, r) is country c's own round r-1 curve, so no calibration country's error
can involve the target country's data — the country-blocked OOF requirement
is satisfied structurally. It becomes a real constraint when fitted
predictors (functional regression, GBM) arrive and must then use a
leave-one-country-out OOF error tensor.

Run:  python -m pcb.experiments.e9_cluster_exact
"""
from __future__ import annotations
import os
from math import comb

import numpy as np
import pandas as pd

from pcb.data.ess_panel import OUT as PANEL_PATH, T_GRID
from pcb.experiments.e7_ess_gate2 import curves, locf_pairs
from pcb.inference.clustered_curve_band import select_one_round_per_country
from pcb.inference.conformal_band import _modulation
from pcb.inference.fixed_trajectory_band import (fixed_trajectory_band,
                                                 stack_trajectories,
                                                 trajectory_modulation,
                                                 trajectory_quantile,
                                                 trajectory_scores)

ALPHA = 0.10
L = 4


def _record(outcome, estimand, cty, K, m, attain, length, score, q, s_mean,
            covered):
    width = np.inf if np.isinf(q) else 2 * q * s_mean
    return dict(outcome=outcome, estimand=estimand, target=cty,
                cal_countries=K, order_index=m, attainable=round(attain, 3),
                traj_len=length, target_score=round(float(score), 3),
                critical=round(float(q), 3) if np.isfinite(q) else np.inf,
                covered=int(covered), mean_width=round(float(width), 3))


def estimand_A(pairs, outcome):
    th_hat = pairs[[f"hat_t{t}" for t in range(T_GRID)]].to_numpy()
    E = th_hat - curves(pairs, outcome)
    cn, rd = pairs.cntry.to_numpy(), pairs.essround.to_numpy()
    rows = []
    for c in np.unique(cn):
        mine = np.flatnonzero(cn == c)
        tgt = mine[np.argmax(rd[mine])]                    # latest round
        cal = cn != c
        E_sel, _, _ = select_one_round_per_country(E[cal], cn[cal], rd[cal])
        s = _modulation(E_sel)
        scores = np.max(np.abs(E_sel) / s, axis=1)
        q, m, attain = trajectory_quantile(scores, ALPHA)
        sc = float(np.max(np.abs(E[tgt]) / s))
        rows.append(_record(outcome, "A_curve", c, len(E_sel), m, attain, 1,
                            sc, q, s.mean(), sc <= q))
    return rows


def estimand_B(pairs, outcome, modulation="pooled"):
    th_hat = pairs[[f"hat_t{t}" for t in range(T_GRID)]].to_numpy()
    E = th_hat - curves(pairs, outcome)
    cn, rd = pairs.cntry.to_numpy(), pairs.essround.to_numpy()
    traj, labels, dropped = stack_trajectories(E, cn, rd, L)
    rows = []
    for i, c in enumerate(labels):
        cal = traj[np.arange(len(labels)) != i]
        s = trajectory_modulation(cal, modulation)
        q, m, attain = trajectory_quantile(trajectory_scores(cal, s), ALPHA)
        sc = float(np.max(np.abs(traj[i]) / s))
        tag = f"B_traj_L{L}" if modulation == "pooled" \
            else f"B_traj_L{L}_{modulation}"
        rows.append(_record(outcome, tag, c, len(cal), m, attain,
                            L, sc, q, s.mean(), sc <= q))
    return rows, dropped


def sensitivity_allround(pairs, outcome, fixed_modulation=False):
    th_hat = pairs[[f"hat_t{t}" for t in range(T_GRID)]].to_numpy()
    E = th_hat - curves(pairs, outcome)
    cn = pairs.cntry.to_numpy()
    lengths = pd.Series(cn).value_counts()
    s_glob = _modulation(E)
    rows = []
    for c in np.unique(cn):
        cal = cn != c
        s = s_glob if fixed_modulation else _modulation(E[cal])
        per_row = np.max(np.abs(E[cal]) / s, axis=1)
        labs = cn[cal]
        scores = np.array([per_row[labs == d].max() for d in np.unique(labs)])
        q, m, attain = trajectory_quantile(scores, ALPHA)
        sc = float(np.max(np.abs(E[cn == c]) / s))
        tag = "S_allround_fixed_s" if fixed_modulation else "S_allround"
        rows.append(_record(outcome, tag, c, len(scores), m, attain,
                            int(lengths[c]), sc, q, s.mean(), sc <= q))
    return rows


def binom_tail_leq(k, n, p):
    return sum(comb(n, j) * p**j * (1 - p)**(n - j) for j in range(k + 1))


def main():
    panel = pd.read_parquet(PANEL_PATH)
    all_rows = []
    for outcome in ("trstprl", "stfdem"):
        pairs = locf_pairs(panel, outcome)
        all_rows += estimand_A(pairs, outcome)
        rows_b, dropped = estimand_B(pairs, outcome)
        all_rows += rows_b
        all_rows += estimand_B(pairs, outcome, modulation='per_slot')[0]
        all_rows += sensitivity_allround(pairs, outcome)
        all_rows += sensitivity_allround(pairs, outcome, fixed_modulation=True)
        if outcome == "trstprl" and dropped:
            print(f"[B] dropped (<{L} rounds): {sorted(dropped)}")
    df = pd.DataFrame(all_rows)
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/ess_cluster_exact_audit.csv", index=False)

    print("\n=== summary (exact counts; nominal 90%) ===")
    g = df.groupby(["outcome", "estimand"])
    summ = g.agg(targets=("covered", "size"), covered=("covered", "sum"),
                 attainable=("attainable", "first"),
                 mean_width=("mean_width", lambda x: round(np.mean(
                     x[np.isfinite(x)]), 3)))
    summ["coverage"] = (summ.covered / summ.targets).round(3)
    print(summ.to_string())

    print("\n=== audit of the all-round 31/35 (trstprl) ===")
    s_all = df[(df.outcome == "trstprl") & (df.estimand == "S_allround")]
    missed = s_all[s_all.covered == 0]
    print(f"missed countries: {list(missed.target)}")
    print(f"trajectory length, missed vs covered: "
          f"{missed.traj_len.mean():.1f} vs "
          f"{s_all[s_all.covered == 1].traj_len.mean():.1f}")
    k, n, p = int(s_all.covered.sum()), len(s_all), float(s_all.attainable.iloc[0])
    print(f"binomial check: P(X <= {k} | n={n}, p={p:.3f}) = "
          f"{binom_tail_leq(k, n, p):.3f}")
    fx = df[(df.outcome == "trstprl") & (df.estimand == "S_allround_fixed_s")]
    print(f"fixed-global-modulation diagnostic: {int(fx.covered.sum())}/{len(fx)} "
          f"(per-target modulation: {k}/{n})")


if __name__ == "__main__":
    main()
