"""E51 — the exchangeable unit is a design parameter, and it has an optimum.

Everything in this paper turns on a choice nobody in the cluster-conformal
literature treats as a choice: at what unit do you make the populations
exchangeable? Countries are the default in cross-national work, individuals the
default in ordinary conformal, and neither is argued for.

The choice is not free, and the cost is computable. Write the deployed band's
half-width at unit size n as

    W(n)  =  q_{1-alpha}(K(n))  *  s_total(n),
    s_total(n)^2 = s_R(n)^2 + vbar(n)^2,        vbar(n)^2 ~ kappa / n,

with K(n) the number of units. Refining the unit pulls the two factors in
opposite directions:

  * q_{1-alpha}(K) is the ceil((1-alpha)(K+1))-th order statistic of K scores.
    It is INFINITE for K < 1/alpha - 1 (the level exceeds the sample), falls
    steeply while K is small, and settles onto the population quantile. Coarse
    units are therefore catastrophic, not merely inefficient.
  * vbar(n)^2 is the per-unit design variance, which grows as the sample behind
    each unit shrinks. Fine units are noisy.

So W is infinite at the coarse end, rises again at the fine end, and has an
interior minimum in between: an OPTIMAL UNIT. This experiment locates it on the
ESS by sweeping the minimum region size and recording the actual deployed
half-width, its two factors, and the number of units.

Honest caveat, reported with the result: changing the size threshold changes
which regions qualify, so the sweep mixes unit refinement with selection on
region size. The mechanism -- q(K) exploding at small K, vbar growing at small
n -- is separable and does not depend on which regions are in the pool, but the
location of the minimum on the ESS does. We report both factors so the reader
can see which one is binding where.

Output: results/optimal_unit.csv
Run:    python -m pcb.experiments.e51_optimal_unit   (~1 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import _finite_quantile
from pcb.experiments.e12_ess_decline import CORE_T, _design_boot, _wcdf
import pcb.experiments.e48_subnational_regions as e48

CORE = np.flatnonzero(CORE_T)
ALPHA = 0.10
SIZES = (600, 400, 300, 200, 150, 100, 80, 60, 50, 40, 30, 25, 20)
ROUNDS = (9, 10, 11)


def _cell(sub, key):
    y = sub["trstprl"].to_numpy(float); w = sub["_w"].to_numpy(float)
    rng = np.random.default_rng(det_seed("e51", *key))
    F = _wcdf(y, w)
    B = _design_boot(y, w, sub["stratum"].to_numpy(), sub["psu"].to_numpy(), rng)
    return F[CORE], B[:, CORE].std(0), len(sub)


def _sweep(d, min_n, rnd):
    cells = {}
    for (c, r, g), sub in d.groupby(["cntry", "essround", "region"], observed=True):
        if r != rnd or len(sub) < min_n or sub.psu.nunique() < 2:
            continue
        cells[(str(c), str(g))] = _cell(sub, (str(c), str(g), str(int(r))))
    K = len(cells)
    if K < 5:
        return None
    keys = list(cells)
    F = np.array([cells[k][0] for k in keys])
    V = np.array([cells[k][1] for k in keys])
    n = np.array([cells[k][2] for k in keys])
    ctry = np.array([k[0] for k in keys])
    Fd = F.copy()
    for c in np.unique(ctry):                    # the small-area estimand
        m = ctry == c
        if m.sum() >= 2:
            Fd[m] = F[m] - F[m].mean(0)[None, :]
    E = Fd - (Fd.sum(0)[None, :] - Fd) / (K - 1)
    scores = np.max(np.abs(E), 1)
    q = _finite_quantile(scores, ALPHA)
    s = _modulation(E)
    idx = int(np.ceil((1 - ALPHA) * (K + 1)))
    return dict(min_n=min_n, essround=rnd, K=K, median_unit_n=int(np.median(n)),
                halfwidth=float(q), quantile_index=idx,
                quantile_feasible=bool(idx <= K),
                s_between=float(s.mean()),
                v_design=float(np.sqrt((V ** 2).mean())),
                s_total=float(np.sqrt(s.mean() ** 2 + (V ** 2).mean())))


def main():
    os.makedirs("results", exist_ok=True)
    d = e48._load()
    rows = [r for m in SIZES for rr in ROUNDS
            if (r := _sweep(d, m, rr)) is not None]
    t = pd.DataFrame(rows)
    t.to_csv("results/optimal_unit.csv", index=False)

    g = (t.groupby("min_n")
         .agg(K=("K", "median"), halfwidth=("halfwidth", "median"),
              s_between=("s_between", "median"), v_design=("v_design", "median"),
              feasible=("quantile_feasible", "all"))
         .reset_index().sort_values("min_n"))
    print("unit-size sweep (medians over rounds 9-11; trust in parliament)\n")
    print(g.round(4).to_string(index=False))

    fin = g[np.isfinite(g.halfwidth)]
    i = fin.halfwidth.idxmin()
    best = g.loc[i]
    coarse = g[g.min_n == g.min_n.max()].iloc[0]
    fine = g[g.min_n == g.min_n.min()].iloc[0]
    print(f"\noptimal unit: min size {int(best.min_n)} respondents, "
          f"K={int(best.K)}, half-width {best.halfwidth:.4f}")
    print(f"  coarsest unit tried ({int(coarse.min_n)}, K={int(coarse.K)}): "
          f"half-width {coarse.halfwidth}")
    print(f"  finest unit tried  ({int(fine.min_n)}, K={int(fine.K)}): "
          f"half-width {fine.halfwidth:.4f} "
          f"({fine.halfwidth / best.halfwidth:.2f}x the optimum)")
    infeas = g[~g.feasible]
    if len(infeas):
        print(f"  conformal level infeasible (K < ceil((1-a)(K+1))) at min size "
              f">= {int(infeas.min_n.min())}: the band is [0,1] at any width")
    print("\nfactors at the optimum vs the ends:")
    print(f"  q(K):  explodes below K~{int(1/ALPHA - 1)}; "
          f"s_between falls with n, v_design rises as 1/sqrt(n)")


if __name__ == "__main__":
    main()
