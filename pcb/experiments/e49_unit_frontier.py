"""E49 — the unit-refinement frontier: where the design-aware correction becomes
reachable, on real survey data.

Proposition 1 says the deployed deconvolution needs both a *need* gate
(rho_LCB > rho0) and a *reliability* gate (K >= 94), and Section 6 shows they
fail in opposite ways across national surveys: the ESS has clustered design
noise but K <= 33, the WVS has K ~ 100 and negligible weights-only noise. That
diagnosis is about the UNIT, not about survey research. Refining the unit does
two things at once: it multiplies the number of exchangeable populations
(relieving the reliability floor D >= sqrt(2/(K-1))) and it shrinks the sample
behind each one (raising the design-to-total ratio rho). The two barriers move
together, in the same direction, and the question is whether they cross.

This experiment answers that empirically, on the ESS itself. The unit is the
harmonized NUTS region, which PSUs nest inside, so each region-round carries a
genuine stratified-PSU design bootstrap. We sweep the minimum region size from
400 respondents down to 25, and at each step run the FROZEN selector -- same
constants, no tuning -- on the leave-one-out region transport problem, recording
K, rho_LCB, D, the four gates, and the width gain on offer.

Country effects are removed before transport (each region curve is taken
relative to its own country's mean region curve), which is the small-area
estimand this regime is actually about: predicting a region's departure from its
national distribution. Pooling raw region curves instead keeps K but puts
cross-national heterogeneity into the denominator of rho, and is reported as a
sensitivity.

Output: results/unit_frontier.csv
Run:    python -m pcb.experiments.e49_unit_frontier   (~1-2 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb import dapcb
from pcb.dapcb import (DELTA_MAX, GAIN_MARGIN, G_MIN, RHO0, delta_ucb,
                       gate_b_feasible)
from pcb.util import det_seed
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import (deconv_reliability, deconv_target_scale,
                                        rho_lcb)
from pcb.experiments.e12_ess_decline import CORE_T, _design_boot, _wcdf
import pcb.experiments.e48_subnational_regions as e48

CORE = np.flatnonzero(CORE_T)
MIN_SIZES = (400, 300, 200, 150, 100, 80, 60, 50, 40, 30, 25)
ROUNDS = (9, 10, 11)
ALPHA = 0.10


def _cells(d, min_n):
    out = {}
    for (c, r, g), sub in d.groupby(["cntry", "essround", "region"], observed=True):
        if len(sub) < min_n or sub.psu.nunique() < 2:
            continue
        y = sub["trstprl"].to_numpy(float); w = sub["_w"].to_numpy(float)
        rng = np.random.default_rng(det_seed("e49", str(c), str(g), int(r)))
        F = _wcdf(y, w)
        B = _design_boot(y, w, sub["stratum"].to_numpy(), sub["psu"].to_numpy(), rng)
        out[(str(c), str(g), int(r))] = (F[CORE], B[:, CORE].std(0), len(sub))
    return out


def _transport(cells, rnd, demean):
    keys = [k for k in cells if k[2] == rnd]
    if len(keys) < 10:
        return None
    F = np.array([cells[k][0] for k in keys])
    V = np.array([cells[k][1] for k in keys])
    n = np.array([cells[k][2] for k in keys])
    if demean:
        ctry = np.array([k[0] for k in keys])
        for c in np.unique(ctry):
            m = ctry == c
            if m.sum() >= 2:
                F[m] = F[m] - F[m].mean(0)[None, :]
    K = len(keys)
    E = F - (F.sum(0)[None, :] - F) / (K - 1)      # leave-one-out deviations
    return E, V, n


def _row(E, V, n, min_n, rnd, demean):
    s = _modulation(E)
    sT = deconv_target_scale(E, V)
    rl = float(rho_lcb(E, V))
    D = float(deconv_reliability(E, V))
    K = E.shape[0]
    fit = dapcb(E, V, np.full(E.shape[1], 0.5), alpha=ALPHA)
    stable = bool((s ** 2 - (V ** 2).mean(0) > (0.05 * s.max()) ** 2).all())
    raw_gain = float(1 - np.mean(sT) / np.mean(s))
    return dict(
        min_n=min_n, essround=rnd, estimand=("within-country deviation" if demean
                                             else "raw region curve"),
        K=K, median_region_n=int(np.median(n)),
        rho_hat=round(float(np.sqrt((V ** 2).mean()) / s.mean()), 4),
        rho_lcb=round(rl, 4), D=round(D, 4),
        floor=round(float(np.sqrt(2 / max(K - 1, 1))), 4),
        delta_ucb=round(delta_ucb(D), 4),
        gate_A_need=bool(rl > RHO0),
        gate_B_reliability=bool(gate_b_feasible(K) and delta_ucb(D) <= DELTA_MAX),
        gate_C_efficiency=bool(fit.gain_lcb > G_MIN) if fit.gain_lcb == fit.gain_lcb else False,
        gate_D_stability=stable,
        raw_width_gain=round(raw_gain, 4),
        gain_lcb=(None if fit.gain_lcb != fit.gain_lcb else round(fit.gain_lcb, 4)),
        branch=fit.selected_branch, coverage=round(fit.coverage_level, 4))


def main():
    os.makedirs("results", exist_ok=True)
    d = e48._load()
    rows = []
    for min_n in MIN_SIZES:
        cells = _cells(d, min_n)
        for demean in (True, False):
            for rnd in ROUNDS:
                out = _transport(cells, rnd, demean)
                if out is None:
                    continue
                rows.append(_row(*out, min_n, rnd, demean))
        r = [x for x in rows if x["min_n"] == min_n
             and x["estimand"].startswith("within")]
        if r:
            b = r[0]
            print(f"min_n={min_n:>3}  K={b['K']:>3}  rho_LCB={b['rho_lcb']:.3f}  "
                  f"D={b['D']:.3f}  gates A/B/C/D="
                  f"{int(b['gate_A_need'])}{int(b['gate_B_reliability'])}"
                  f"{int(b['gate_C_efficiency'])}{int(b['gate_D_stability'])}  "
                  f"gain={b['raw_width_gain']:.3f}  -> {b['branch']}")
    res = pd.DataFrame(rows)
    res.to_csv("results/unit_frontier.csv", index=False)

    w = res[res.estimand.str.startswith("within")]
    open_ab = w[w.gate_A_need & w.gate_B_reliability]
    print("\n=== the frontier ===")
    print(f"  reliability gate first feasible at K>=94: min_n<= "
          f"{w[w.gate_B_reliability].min_n.max() if len(w[w.gate_B_reliability]) else 'never'}")
    print(f"  need gate first opens at min_n <= "
          f"{open_ab.min_n.max() if len(open_ab) else 'never'} "
          f"(rho_LCB crosses {RHO0})")
    if len(open_ab):
        print(f"\n*** both binding gates open on real ESS data in "
              f"{len(open_ab)} unit-rounds ***")
        print(open_ab[["min_n", "essround", "K", "rho_lcb", "D", "raw_width_gain",
                       "gain_lcb", "gate_C_efficiency", "branch"]].to_string(index=False))
        if (open_ab.branch == "deconvolution").any():
            print("  -> the deployed selector ACTIVATES deconvolution")
        else:
            print(f"  -> the deployed selector still abstains, on efficiency: the "
                  f"raw width gain of {open_ab.raw_width_gain.max():.1%} does not "
                  f"clear g_min={G_MIN} after the frozen {GAIN_MARGIN} margin")
    print("\n(raw region curves, no country demeaning, as sensitivity:)")
    print(res[~res.estimand.str.startswith("within")]
          .groupby("min_n")[["K", "rho_lcb", "D"]].median().round(3).to_string())


if __name__ == "__main__":
    main()
