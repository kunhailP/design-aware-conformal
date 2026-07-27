"""E52 — the unit-size tradeoff without the confounds: PSU-built units.

E51 swept a minimum size threshold over ESS NUTS regions and found an interior
optimum in band width. Two confounds make that sweep an unreliable estimate of
the mechanism it is meant to demonstrate, and we found both ourselves:

  (a) `region` is not one nesting level. Region codes run three to five
      characters (NUTS1/2/3) and countries use different levels, so the pooled
      "units" differ in geographic and demographic scale by an order of
      magnitude (Germany: 16 regions averaging 545 respondents; Croatia: 21
      averaging 76).
  (b) Changing the size threshold changes which regions qualify, so the sweep
      mixes unit refinement with selection on region size -- and with country
      composition, since whole countries drop out at the coarse end.

This experiment removes both. Within each country-round we partition the sample
into units of a TARGET size by grouping whole PSUs at random (respecting strata),
so that

  * unit size is controlled by construction, not by a filter;
  * every country contributes at every unit size, so composition is fixed;
  * units are groups of whole PSUs, so each carries genuine clustered design
    noise from its own stratified-PSU bootstrap;
  * within-country exchangeability holds by construction, because the
    assignment of PSUs to units is random.

The units are not substantively meaningful areas, and that is the point: the
proposition is about the statistical cost of the unit, and this design isolates
it. If the interior optimum survives here, it is a property of the tradeoff and
not of ESS geography.

Output: results/controlled_unit_size.csv
Run:    python -m pcb.experiments.e52_controlled_unit_size   (~1-2 h)
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
TARGETS = (1500, 1000, 700, 500, 350, 250, 175, 125, 90, 60, 40)
ROUNDS = (9, 10, 11)
REPS = 3          # independent random PSU->unit assignments per configuration


def _units(sub, target, rng):
    """Group whole PSUs at random into units of ~target respondents."""
    psu_sizes = sub.groupby("psu", observed=True).size()
    psus = np.array(psu_sizes.index.to_numpy(), copy=True)
    rng.shuffle(psus)
    sizes = psu_sizes.loc[psus].to_numpy()
    units, cur, cur_n = [], [], 0
    for p, n in zip(psus, sizes):
        cur.append(p); cur_n += n
        if cur_n >= target:
            units.append(cur); cur, cur_n = [], 0
    if cur and units and cur_n < target / 2:
        units[-1].extend(cur)                    # absorb a small remainder
    elif cur:
        units.append(cur)
    return units


def _cell(sub, rng):
    y = sub["trstprl"].to_numpy(float); w = sub["_w"].to_numpy(float)
    F = _wcdf(y, w)
    B = _design_boot(y, w, sub["stratum"].to_numpy(), sub["psu"].to_numpy(), rng)
    return F[CORE], B[:, CORE].std(0), len(sub)


def _one(d, target, rnd, rep):
    rows_F, rows_V, rows_n, ctry = [], [], [], []
    for c, sub in d[d.essround == rnd].groupby("cntry", observed=True):
        if sub.psu.nunique() < 4 or len(sub) < 2 * target:
            continue
        rng = np.random.default_rng(det_seed("e52", str(c), int(rnd), target, rep))
        for u in _units(sub, target, rng):
            s = sub[sub.psu.isin(u)]
            if len(s) < max(20, target // 3) or s.psu.nunique() < 2:
                continue
            F, V, n = _cell(s, rng)
            rows_F.append(F); rows_V.append(V); rows_n.append(n); ctry.append(str(c))
    K = len(rows_F)
    if K < 5:
        return None
    F = np.array(rows_F); V = np.array(rows_V); n = np.array(rows_n)
    ctry = np.array(ctry)
    Fd = F.copy()
    for c in np.unique(ctry):
        m = ctry == c
        if m.sum() >= 2:
            Fd[m] = F[m] - F[m].mean(0)[None, :]
    E = Fd - (Fd.sum(0)[None, :] - Fd) / (K - 1)
    q = _finite_quantile(np.max(np.abs(E), 1), ALPHA)
    s = _modulation(E)
    v = float(np.sqrt((V ** 2).mean()))
    return dict(target=target, essround=rnd, rep=rep, K=K,
                n_countries=int(len(np.unique(ctry))),
                median_unit_n=int(np.median(n)), halfwidth=float(q),
                s_between=float(s.mean()), v_design=v,
                s_total=float(np.sqrt(s.mean() ** 2 + v ** 2)),
                feasible=bool(np.ceil((1 - ALPHA) * (K + 1)) <= K))


def main():
    os.makedirs("results", exist_ok=True)
    d = e48._load()
    rows = []
    for target in TARGETS:
        for rnd in ROUNDS:
            for rep in range(REPS):
                r = _one(d, target, rnd, rep)
                if r:
                    rows.append(r)
        g = [x for x in rows if x["target"] == target]
        if g:
            hw = np.median([x["halfwidth"] for x in g])
            print(f"target={target:>5}  K={np.median([x['K'] for x in g]):.0f}  "
                  f"countries={g[0]['n_countries']:2d}  half-width="
                  f"{hw:.4f}  v={np.median([x['v_design'] for x in g]):.4f}  "
                  f"s={np.median([x['s_between'] for x in g]):.4f}")
    t = pd.DataFrame(rows)
    t.to_csv("results/controlled_unit_size.csv", index=False)

    g = (t.groupby("target")
         .agg(K=("K", "median"), half=("halfwidth", "median"),
              s=("s_between", "median"), v=("v_design", "median"),
              nc=("n_countries", "median"), feas=("feasible", "all"))
         .reset_index().sort_values("target"))
    print("\ncontrolled sweep (medians over rounds and PSU assignments)\n")
    print(g.round(4).to_string(index=False))
    fin = g[np.isfinite(g.half)]
    if len(fin):
        i = fin.half.idxmin()
        print(f"\noptimum at target {int(g.loc[i,'target'])} respondents per unit "
              f"(K={int(g.loc[i,'K'])}, half-width {g.loc[i,'half']:.4f})")
        print(f"  finest tried {int(fin.target.min())}: "
              f"{float(fin[fin.target==fin.target.min()].half.iloc[0])/g.loc[i,'half']:.2f}x")
        print(f"  coarsest tried {int(fin.target.max())}: "
              f"{float(fin[fin.target==fin.target.max()].half.iloc[0])/g.loc[i,'half']:.2f}x")
        print(f"  country composition constant at {int(g.nc.median())} countries "
              f"across the sweep: {bool(g.nc.nunique()==1)}")


if __name__ == "__main__":
    main()
