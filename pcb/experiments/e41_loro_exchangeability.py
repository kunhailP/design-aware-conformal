"""E41 — the promised leave-one-region-out (LORO) exchangeability audit (paper §2).

The transport band's identifying assumption is country exchangeability. If
regional blocs (North/West/South/post-communist East) have systematically
different trajectory laws, a band calibrated on the other regions should
under-cover the held-out region. Audit: for each region R, calibrate the U0
clustered trajectory band (leave-one-out centers, alpha=0.10) on the countries
outside R and record, for every country in R, whether its full trajectory over
the core rounds (9-11) falls inside the band. Report per-region coverage counts
against nominal 90%; and, as a finer probe, the same with every region's
countries scored against an all-country calibration (the exchangeable baseline).

Unit = whole country trajectory over rounds 9-11 x thresholds t1..t4 (the
preregistered low-trust core), trust in parliament and satisfaction with
democracy separately. Small-N caveat: 4-11 countries per region; we report
counts, not rates with false precision.

Output: results/loro_exchangeability.csv
Run:    python -m pcb.experiments.e41_loro_exchangeability
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

REGIONS = {
    "North": ["DK", "FI", "IS", "NO", "SE", "EE", "LT", "LV"],
    "West": ["AT", "BE", "CH", "DE", "FR", "GB", "IE", "LU", "NL"],
    "South": ["CY", "ES", "GR", "IT", "MT", "PT", "IL"],
    "East": ["BG", "CZ", "HR", "HU", "ME", "MK", "PL", "RO", "RS",
             "SI", "SK", "AL", "UA", "XK", "GE", "TR", "RU"],
}
CORE_T = [1, 2, 3, 4]
ALPHA = 0.10
ROUNDS = (9, 10, 11)


def _traj(p, outcome):
    """country -> (L, |core|) trajectory matrix over available core rounds."""
    cols = [f"{outcome}_t{t}" for t in CORE_T]
    out = {}
    for c, g in p[p.essround.isin(ROUNDS)].groupby("cntry"):
        g = g.sort_values("essround")
        if len(g) < 2:
            continue
        out[c] = g[cols].to_numpy(float)
    return out


def _score(F, mu_rows):
    """sup-|deviation| of a trajectory from per-round centers (align by round)."""
    return float(np.nanmax(np.abs(F - mu_rows)))


def _loo_scores(trajs, members):
    """Calibration scores with leave-one-out centers over `members`."""
    scores = {}
    for c in members:
        others = [trajs[o] for o in members if o != c]
        mu = _round_mean(others)
        scores[c] = _score(trajs[c], mu[: trajs[c].shape[0]])
    return scores


def _round_mean(mats):
    L = max(m.shape[0] for m in mats)
    out = np.full((L, len(CORE_T)), np.nan)
    for r in range(L):
        rows = [m[r] for m in mats if m.shape[0] > r]
        out[r] = np.nanmean(rows, axis=0)
    return out


def main():
    os.makedirs("results", exist_ok=True)
    p = pd.read_parquet("data/ess/panel.parquet")
    p = p[p["sample"] == "core"]
    rows = []
    for outcome in ("trstprl", "stfdem"):
        trajs = _traj(p, outcome)
        have = sorted(trajs)
        region_of = {c: r for r, cs in REGIONS.items() for c in cs}
        for region in REGIONS:
            cal = [c for c in have if region_of.get(c) != region]
            test = [c for c in have if region_of.get(c) == region]
            if not test:
                continue
            cal_scores = _loo_scores(trajs, cal)
            q_idx = int(np.ceil((1 - ALPHA) * (len(cal) + 1))) - 1
            q = np.sort(list(cal_scores.values()))[min(q_idx, len(cal) - 1)]
            mu = _round_mean([trajs[c] for c in cal])
            covered = sum(_score(trajs[c], mu[: trajs[c].shape[0]]) <= q
                          for c in test)
            rows.append(dict(outcome=outcome, region=region, n_test=len(test),
                             n_cal=len(cal), covered=covered,
                             coverage=round(covered / len(test), 3),
                             q_loro=round(q, 4)))
        # exchangeable baseline: full-pool LOO self-coverage
        scores = _loo_scores(trajs, have)
        q_idx = int(np.ceil((1 - ALPHA) * (len(have) + 1))) - 1
        qs = np.sort(list(scores.values()))
        q = qs[min(q_idx, len(have) - 1)]
        cov = sum(s <= q for s in scores.values())
        rows.append(dict(outcome=outcome, region="ALL (LOO baseline)",
                         n_test=len(have), n_cal=len(have) - 1, covered=cov,
                         coverage=round(cov / len(have), 3), q_loro=round(q, 4)))
    res = pd.DataFrame(rows)
    res.to_csv("results/loro_exchangeability.csv", index=False)
    print(res.to_string(index=False))
    worst = res[res.region != "ALL (LOO baseline)"].coverage.min()
    print(f"\nworst held-out-region coverage: {worst:.3f} (nominal 0.90; "
          f"binomial noise on n<=11 is large — read counts, not rates)")


if __name__ == "__main__":
    main()
