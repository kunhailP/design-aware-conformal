"""E48 — the many-unit regime, on real survey data: ESS subnational regions.

The paper's boundary result says the design-aware deconvolution is unreachable at
cross-national scale, because the two gates fail in opposite ways: the ESS has
genuine clustered design noise but only K<=33 countries, while the WVS has
K~100 populations and negligible weights-only noise. Both barriers are about the
*unit*, not about surveys: take a smaller exchangeable unit and K grows while
the per-unit sample shrinks, which raises the design-to-total ratio rho at the
same time as it relieves the reliability floor.

ESS regions (harmonized NUTS `region`) are that unit. Within rounds 9-11 the
integrated file ships PSU/stratum, and PSUs nest inside regions, so each region
carries a genuine stratified-PSU design bootstrap. This experiment asks whether
the frozen selector -- unchanged, same constants -- activates the deconvolution
branch on real data for the first time.

Design. Unit = (country, region) in one round. Curve = weighted CDF of trust in
parliament over the preregistered low-trust core. Transport = leave-one-region-out:
the center for region g is the mean curve of all other regions, so calibration
errors E_g are LOO deviations (the deployed unsurveyed-target construction) and
v_g is the region's own stratified-PSU bootstrap SD. We then call `dapcb`
verbatim and record the branch, the gates, and the width ratio.

Two nested universes are reported, because the exchangeability claim differs:
  ALL     -- regions pooled across countries (K largest; between-region signal
             includes cross-national differences);
  WITHIN  -- regions of a single country (K small per country, but the
             exchangeability postulate is far more credible).

Output: results/subnational_regions.csv
Run:    python -m pcb.experiments.e48_subnational_regions   (~1 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb import dapcb
from pcb.util import det_seed
from pcb.dapcb import gate_b_feasible, RHO0
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import (deconv_reliability, rho_lcb,
                                        deconv_target_scale)
from pcb.experiments.e12_ess_decline import CORE_T, _design_boot, _wcdf

OUTCOME = "trstprl"
ROUNDS = (9, 10, 11)
MIN_N = 100          # respondents per region-round
MIN_PSU = 2
B_DESIGN = 400
ALPHA = 0.10
CORE = np.flatnonzero(CORE_T)


def _load():
    import pyreadstat
    df, _ = pyreadstat.read_dta(
        "data/ess/Datafile-subset.dta",
        usecols=["essround", "cntry", "region", "psu", "stratum",
                 "anweight", "pspwght", OUTCOME])
    d = df[df.essround.isin(ROUNDS)].copy()
    d["_w"] = d["anweight"].fillna(d["pspwght"])
    d = d[d._w.notna() & (d._w > 0) & d[OUTCOME].notna()]
    return d[d.psu.notna() & d.stratum.notna()]


def _cells(d):
    """(country, region, round) -> (F_core, v_core) with a real design bootstrap."""
    out = {}
    for (c, r, g), sub in d.groupby(["cntry", "essround", "region"], observed=True):
        if len(sub) < MIN_N or sub.psu.nunique() < MIN_PSU:
            continue
        y = sub[OUTCOME].to_numpy(float); w = sub["_w"].to_numpy(float)
        st = sub["stratum"].to_numpy(); ps = sub["psu"].to_numpy()
        rng = np.random.default_rng(det_seed("e48", str(c), str(g), int(r)))
        F = _wcdf(y, w)
        Bd = _design_boot(y, w, st, ps, rng)
        out[(str(c), str(g), int(r))] = (F[CORE], Bd[:, CORE].std(0))
    return out


def _loo_transport(keys, cells):
    """Leave-one-out deviations and design SDs over a set of region keys."""
    F = np.array([cells[k][0] for k in keys])
    V = np.array([cells[k][1] for k in keys])
    K = len(keys)
    if K < 3:
        return None
    tot = F.sum(0)
    E = F - (tot[None, :] - F) / (K - 1)          # LOO deviations
    return E, V


def _diag(E, V, label, extra):
    s = _modulation(E)
    rho = float(np.sqrt((V ** 2).mean()) / s.mean())
    rl = float(rho_lcb(E, V))
    D = float(deconv_reliability(E, V))
    K = E.shape[0]
    fit = dapcb(E, V, np.full(E.shape[1], 0.5), alpha=ALPHA)
    sT = deconv_target_scale(E, V)
    return dict(universe=label, K=K, rho_hat=round(rho, 4),
                rho_lcb=round(rl, 4), D=round(D, 4),
                floor=round(float(np.sqrt(2 / max(K - 1, 1))), 4),
                gate_A=bool(rl > RHO0), gate_B_feasible=bool(gate_b_feasible(K)),
                delta_ucb=round(fit.delta_ucb, 4), branch=fit.selected_branch,
                gain_lcb=(None if np.isnan(fit.gain_lcb) else round(fit.gain_lcb, 4)),
                coverage=round(fit.coverage_level, 4),
                width_ratio=round(float(np.mean(sT) / np.mean(s)), 4),
                **extra)


def main():
    os.makedirs("results", exist_ok=True)
    d = _load()
    cells = _cells(d)
    print(f"{len(cells)} region-round cells with n>={MIN_N} and >={MIN_PSU} PSUs, "
          f"{len({(c, g) for c, g, _ in cells})} distinct regions\n")

    rows = []
    # --- ALL: regions pooled across countries, per round ----------------------
    for r in ROUNDS:
        keys = [k for k in cells if k[2] == r]
        out = _loo_transport(keys, cells)
        if out is None:
            continue
        E, V = out
        rows.append(_diag(E, V, "all-countries", dict(essround=r, cntry="")))
        print(f"[all r{r}] K={E.shape[0]:3d} rho={rows[-1]['rho_hat']:.3f} "
              f"(LCB {rows[-1]['rho_lcb']:.3f})  D={rows[-1]['D']:.3f} "
              f"floor={rows[-1]['floor']:.3f}  gateA={rows[-1]['gate_A']} "
              f"gateB_feas={rows[-1]['gate_B_feasible']}  -> {rows[-1]['branch']}")

    # --- WITHIN: regions of one country, per round ----------------------------
    for r in ROUNDS:
        for c in sorted({k[0] for k in cells if k[2] == r}):
            keys = [k for k in cells if k[2] == r and k[0] == c]
            out = _loo_transport(keys, cells)
            if out is None:
                continue
            E, V = out
            rows.append(_diag(E, V, "within-country", dict(essround=r, cntry=c)))

    res = pd.DataFrame(rows)
    res.to_csv("results/subnational_regions.csv", index=False)

    w = res[res.universe == "within-country"]
    print(f"\n=== within-country region transport ({len(w)} country-rounds) ===")
    print(f"  rho_hat: median {w.rho_hat.median():.3f}, max {w.rho_hat.max():.3f}"
          f"  (rho0={RHO0})")
    print(f"  gate A (need) opens in {int(w.gate_A.sum())} of {len(w)}")
    print(f"  gate B feasible (K>=94) in {int(w.gate_B_feasible.sum())}")
    print(f"  branches: {w.branch.value_counts().to_dict()}")
    a = res[res.universe == "all-countries"]
    print(f"\n=== pooled across countries ===")
    print(a[["essround", "K", "rho_hat", "rho_lcb", "D", "floor", "gate_A",
             "gate_B_feasible", "branch", "width_ratio"]].to_string(index=False))
    fired = res[res.branch == "deconvolution"]
    if len(fired):
        print(f"\n*** deconvolution ACTIVATED on real data in {len(fired)} "
              f"universe-rounds ***")
        print(fired[["universe", "cntry", "essround", "K", "rho_lcb", "D",
                     "gain_lcb", "coverage", "width_ratio"]].to_string(index=False))
    else:
        print("\nno activation: the frozen selector still abstains at this unit")


if __name__ == "__main__":
    main()
