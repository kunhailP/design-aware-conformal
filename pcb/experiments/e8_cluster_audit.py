"""E8 — conformal-calibration-unit audit (blocking gate before any further
ESS work).

Verdict sought: is the exchangeable unit behind the gate-2 numbers 250
country-rounds or ~35 countries?  Two calibrations are compared on identical
predictions (temporal transport: LOCF, the target's own earlier round — NOT
unseen-country transport):

  round-cal    quantile over country-round sup-scores (gate-2 construction;
               target country fully excluded from scores AND modulation)
  cluster-cal  one score per country trajectory, R_c = max_{r,t}|E|/s(t);
               quantile over K = (#countries - 1) country scores

Both are scored at two levels: country-round simultaneous coverage (band
contains that round's whole curve) and COUNTRY-level coverage (all rounds and
all thresholds of the held-out country simultaneously). Exact covered counts,
95% Wilson intervals, effective K, and the attainable conformal level
ceil((1-a)(K+1))/(K+1) are reported — with ~35 countries the granularity is
coarse and decimal differences are noise.

Robustness: `balanced` restricts to countries with >= 4 LOCF rounds,
truncated to their last 4, so trajectory length cannot drive the country
scores.

Run:  python -m pcb.experiments.e8_cluster_audit
        -> results/ess_cluster_audit.csv
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.data.ess_panel import OUT as PANEL_PATH, T_GRID
from pcb.experiments.e7_ess_gate2 import curves, locf_pairs
from pcb.inference.clustered_band import (clustered_quantile, country_scores)
from pcb.inference.conformal_band import _modulation

ALPHA = 0.10


def wilson(k: int, n: int, z: float = 1.96):
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return c - h, c + h


def audit_layer(pairs: pd.DataFrame, outcome: str, label: str) -> list[dict]:
    th_hat = pairs[[f"hat_t{t}" for t in range(T_GRID)]].to_numpy()
    E = th_hat - curves(pairs, outcome)
    cn = pairs.cntry.to_numpy()
    countries = np.unique(cn)

    per_method = {m: dict(cty_cov=[], rnd_cov=[], width=[], qs=[])
                  for m in ("round_cal", "cluster_cal")}
    for c_star in countries:
        cal = cn != c_star
        E_cal, E_tgt = E[cal], E[cn == c_star]
        s = _modulation(E_cal)                      # target country excluded
        tgt_scores = np.max(np.abs(E_tgt) / s[None, :], axis=1)  # per round

        # round-cal: quantile over country-round sup-scores
        rs = np.max(np.abs(E_cal) / s[None, :], axis=1)
        q_r = clustered_quantile(rs, ALPHA)
        # cluster-cal: quantile over country trajectory scores
        _, cs = country_scores(E_cal, cn[cal], s)
        q_c = clustered_quantile(cs, ALPHA)

        for m, q in (("round_cal", q_r), ("cluster_cal", q_c)):
            per_method[m]["cty_cov"].append(float(np.all(tgt_scores <= q)))
            per_method[m]["rnd_cov"].extend((tgt_scores <= q).tolist())
            per_method[m]["width"].append(float(2 * q * s.mean()))
            per_method[m]["qs"].append(q)

    K_round = len(pairs) - int(pd.Series(cn).value_counts().mean())
    rows = []
    for m, d in per_method.items():
        n_c = len(countries)
        k_cov = int(np.sum(d["cty_cov"]))
        eff_K = n_c - 1 if m == "cluster_cal" else int(np.round(K_round))
        attain = np.ceil((1 - ALPHA) * (eff_K + 1)) / (eff_K + 1)
        lo, hi = wilson(k_cov, n_c)
        rows.append(dict(
            outcome=outcome, layer=label, method=m,
            eff_K=eff_K, granularity=round(1 / (eff_K + 1), 3),
            attainable_level=round(attain, 3),
            countries=n_c, covered_countries=k_cov,
            country_cov=round(k_cov / n_c, 3),
            country_cov_ci=f"[{lo:.2f},{hi:.2f}]",
            round_cov=round(float(np.mean(d["rnd_cov"])), 3),
            mean_width=round(float(np.mean(d["width"])), 3),
            max_width=round(float(np.max(d["width"])), 3)))
    return rows


def main():
    panel = pd.read_parquet(PANEL_PATH)
    rows = []
    for outcome in ("trstprl", "stfdem"):
        pairs = locf_pairs(panel, outcome)
        rows += audit_layer(pairs, outcome, "all")
        counts = pairs.cntry.value_counts()
        keep = counts[counts >= 4].index
        bal = (pairs[pairs.cntry.isin(keep)]
               .sort_values(["cntry", "essround"])
               .groupby("cntry", observed=True).tail(4))
        rows += audit_layer(bal, outcome, "balanced")
    df = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/ess_cluster_audit.csv", index=False)
    pd.set_option("display.width", 220)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
