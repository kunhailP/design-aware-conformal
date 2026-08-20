"""E54 — small-area transport on the ESS, built to survive the objections that
sank E48/E49.

The withdrawn frontier failed for four reasons, all of them design rather than
arithmetic, and this experiment removes each at the source.

  (1) INCONSISTENT ESTIMAND. E49 centred a region on its country's mean region
      curve only when that country contributed two or more qualifying regions,
      leaving the rest on raw levels -- and the share left raw tracked the sweep
      variable. Here the estimand is fixed once and applies to every unit: a
      region's departure from its own NATIONAL curve,
      D_g = F_g - F_nation, estimated from the whole country sample.
  (2) WRONG DESIGN VARIANCE. E49 used the raw curve's v_g for the demeaned
      object, which overstates rho. Here a single stratified-PSU bootstrap is
      run over the whole country and BOTH F_g and F_nation are recomputed from
      each replicate, so v_g is the design SD of the difference, with the
      induced covariance handled automatically.
  (3) CONTAMINATED UNITS. The ESS missing-value sentinel (99999) was being
      treated as a region, and three countries enter with a single "region"
      that IS the country. Both are excluded; countries with fewer than two
      usable regions cannot express a within-country departure and are dropped.
  (4) UNDISCLOSED HETEROGENEITY. `region` mixes NUTS levels across countries.
      We cannot fix that with this file, so we report the composition and, as a
      sensitivity, restrict to the countries whose codes sit at a common level.

The question is the paper's own: at a unit where many exchangeable populations
each carry real sampling noise, does the FROZEN selector -- same constants, no
tuning -- activate the design-aware branch it never activates across countries?

Output: results/small_area_transport.csv
Run:    python -m pcb.experiments.e54_small_area_transport   (~1-2 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb import dapcb
from pcb.dapcb import RHO0, delta_ucb, gate_b_feasible
from pcb.util import det_seed
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import (deconv_reliability, deconv_target_scale,
                                        rho_lcb)
from pcb.experiments.e12_ess_decline import CORE_T

CORE = np.flatnonzero(CORE_T)
ALPHA = 0.10
B = 400
ROUNDS = (9, 10, 11)
MIN_SIZES = (400, 300, 200, 150, 100, 80, 60, 40)
SENTINEL = {"99999", "9999", "999", "nan", "", "None"}


def _load():
    import pyreadstat
    df, _ = pyreadstat.read_dta(
        "data/ess/Datafile-subset.dta",
        usecols=["essround", "cntry", "region", "psu", "stratum",
                 "anweight", "pspwght", "trstprl"])
    d = df[df.essround.isin(ROUNDS)].copy()
    d["_w"] = d["anweight"].fillna(d["pspwght"])
    d = d[d._w.notna() & (d._w > 0) & d["trstprl"].notna()]
    d = d[d.psu.notna() & d.stratum.notna()]
    d["region"] = d["region"].astype(str)
    d = d[~d.region.isin(SENTINEL)]
    # a "region" identical to the country code carries no subnational content
    return d[d.region != d.cntry.astype(str)]


def _country_draws(sub, min_n, rng):
    """One stratified-PSU bootstrap of the WHOLE country; returns per-region
    departures from the national curve, point estimate and design SD."""
    y = sub["trstprl"].to_numpy(float); w = sub["_w"].to_numpy(float)
    reg = sub["region"].to_numpy()
    psu = sub["psu"].to_numpy(); strat = sub["stratum"].to_numpy()

    ind = w[:, None] * (y[:, None] <= CORE[None, :])          # (n, |core|)
    key = pd.MultiIndex.from_arrays([strat, psu, reg])
    g = pd.DataFrame(np.column_stack([ind, w]), index=key).groupby(
        level=[0, 1, 2], observed=True).sum()
    cnt, tot = g.values[:, :len(CORE)], g.values[:, len(CORE)]
    s_lab = g.index.get_level_values(0).to_numpy()
    r_lab = g.index.get_level_values(2).to_numpy()

    regions = [r for r in np.unique(r_lab)
               if tot[r_lab == r].sum() > 0]
    # keep regions meeting the size and PSU requirements
    keep = []
    for r in regions:
        m = r_lab == r
        if int((sub.region == r).sum()) >= min_n and m.sum() >= 2:
            keep.append(r)
    if len(keep) < 2:
        return None

    idx_by_stratum = {s: np.flatnonzero(s_lab == s) for s in np.unique(s_lab)}
    def resample():
        pick = []
        for s, rows in idx_by_stratum.items():
            m = len(rows)
            pick.append(rows[rng.integers(0, m, size=m)] if m > 1 else rows)
        return np.concatenate(pick)

    def curves(rows):
        num = cnt[rows]; den = tot[rows]; lab = r_lab[rows]
        nat = num.sum(0) / max(den.sum(), 1e-12)
        out = {}
        for r in keep:
            m = lab == r
            if den[m].sum() <= 0:
                return None
            out[r] = num[m].sum(0) / den[m].sum() - nat
        return out

    point = curves(np.arange(len(tot)))
    if point is None:
        return None
    reps = {r: np.empty((B, len(CORE))) for r in keep}
    for b in range(B):
        c = curves(resample())
        if c is None:                       # a stratum lost a region entirely
            for r in keep:
                reps[r][b] = point[r]
        else:
            for r in keep:
                reps[r][b] = c[r]
    return {r: (point[r], reps[r].std(0), int((sub.region == r).sum()))
            for r in keep}


def _row(D, V, n, min_n, rnd, label):
    K = D.shape[0]
    E = D - (D.sum(0)[None, :] - D) / (K - 1)      # LOO transport deviations
    s = _modulation(E)
    # tighten=False: D_g is a signed departure curve, not a CDF, so the
    # isotonic/[0,1] tightening does not apply (same convention as e55; the
    # branch choice and every recorded diagnostic are computed before
    # tightening, so committed results are unchanged).
    fit = dapcb(E, V, np.zeros(E.shape[1]), alpha=ALPHA, tighten=False)
    sT = deconv_target_scale(E, V)
    rl = float(rho_lcb(E, V)); Dg = float(deconv_reliability(E, V))
    return dict(pool=label, min_n=min_n, essround=rnd, K=K,
                median_region_n=int(np.median(n)),
                rho_hat=round(float(np.sqrt((V ** 2).mean()) / s.mean()), 4),
                rho_lcb=round(rl, 4), D=round(Dg, 4),
                delta_ucb=round(delta_ucb(Dg), 4),
                gate_A=bool(rl > RHO0), gate_B=bool(gate_b_feasible(K)
                                                    and delta_ucb(Dg) <= 0.02),
                branch=fit.selected_branch,
                gain_lcb=(None if fit.gain_lcb != fit.gain_lcb
                          else round(fit.gain_lcb, 4)),
                width_ratio=round(float(np.mean(sT) / np.mean(s)), 4),
                coverage=round(fit.coverage_level, 4),
                fallback=fit.fallback_reason)


def main():
    os.makedirs("results", exist_ok=True)
    d = _load()
    lvl = (d.groupby("cntry", observed=True).region
           .apply(lambda x: int(np.median([len(v) for v in x.unique()]))))
    print("NUTS level composition (region code length): "
          + ", ".join(f"{k}:{v}" for k, v in lvl.value_counts().items()))
    common = set(lvl[lvl == lvl.value_counts().idxmax()].index)
    print(f"most common level covers {len(common)} countries\n")

    rows = []
    for min_n in MIN_SIZES:
        for rnd in ROUNDS:
            cells, ctry = {}, {}
            for c, sub in d[d.essround == rnd].groupby("cntry", observed=True):
                rng = np.random.default_rng(det_seed("e54", str(c), int(rnd), min_n))
                got = _country_draws(sub, min_n, rng)
                if got:
                    for r, v in got.items():
                        cells[(str(c), r)] = v
                        ctry[(str(c), r)] = str(c)
            if len(cells) < 10:
                continue
            keys = list(cells)
            Dm = np.array([cells[k][0] for k in keys])
            Vm = np.array([cells[k][1] for k in keys])
            nm = np.array([cells[k][2] for k in keys])
            rows.append(_row(Dm, Vm, nm, min_n, rnd, "all countries"))
            sel = [i for i, k in enumerate(keys) if ctry[k] in common]
            if len(sel) >= 10:
                rows.append(_row(Dm[sel], Vm[sel], nm[sel], min_n, rnd,
                                 "common NUTS level"))
        r = [x for x in rows if x["min_n"] == min_n and x["pool"] == "all countries"]
        for x in r:
            print(f"min_n={min_n:>3} r{x['essround']}: K={x['K']:>3} "
                  f"rho_LCB={x['rho_lcb']:.3f} D={x['D']:.3f} "
                  f"A={int(x['gate_A'])} B={int(x['gate_B'])} -> {x['branch']}"
                  + (f"  gain={x['gain_lcb']}" if x['gain_lcb'] is not None else ""))
    t = pd.DataFrame(rows)
    t.to_csv("results/small_area_transport.csv", index=False)

    a = t[t.pool == "all countries"]
    fired = a[a.branch == "deconvolution"]
    print("\n=== frozen selector on the small-area estimand ===")
    print(f"  unit-rounds evaluated : {len(a)}")
    print(f"  need gate opens       : {int(a.gate_A.sum())}")
    print(f"  reliability gate opens: {int(a.gate_B.sum())}")
    print(f"  DECONVOLUTION FIRES   : {len(fired)}")
    if len(fired):
        print(fired[["min_n", "essround", "K", "rho_lcb", "D", "gain_lcb",
                     "width_ratio", "coverage"]].to_string(index=False))
    c = t[t.pool == "common NUTS level"]
    if len(c):
        print(f"\n  common-level sensitivity: {int((c.branch=='deconvolution').sum())}"
              f" of {len(c)} fire; max rho_LCB {c.rho_lcb.max():.3f}")


if __name__ == "__main__":
    main()
