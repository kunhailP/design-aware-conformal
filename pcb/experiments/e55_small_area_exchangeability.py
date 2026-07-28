"""E55 — does the small-area unit of E54 actually satisfy exchangeability?

E54 calibrates a transport band across K = 228-287 ESS *regions* and reports the
first real-data activation of the design-aware branch. But those regions are not
a flat pool: they nest inside 27-28 countries, roughly nine regions each, and a
country's regional departures share a national curve, a survey design, and a
political context. If the country is the true exchangeable unit, the effective K
is ~27 -- below this paper's own K >= 94 floor -- and E54's activation would be
an instance of exactly the wrong-unit error Section 1 diagnoses.

That objection is decided by data, not argument, so we measure it two ways and
report the gap between them.

  LORO  leave-one-REGION-out. Train on every other region, INCLUDING the held-
        out region's country-mates. This is the deployment mode a survey analyst
        is actually in (you hold the whole country's sample and want a band for
        a thinly-sampled region of it), and it is the mode E54's construction
        implicitly assumes.
  LOCO  leave-one-COUNTRY-out. Train only on regions of the other 26 countries,
        then cover every region of the held-out country. Nothing about the
        target country is in the calibration set, so this is the strict
        cross-population exchangeability stress test.

Coverage is scored three ways per held-out unit: against the radius the FROZEN
selector actually chose, and against the two anchor branches. The plug-in PCB
anchor is the clean read on exchangeability, because its target lives on the
same observed scale as the realized departure; the deconvolution branch targets
the LATENT departure, so an observed-scale check understates it by construction
and we report it as a lower bound rather than a verdict.

Output: results/small_area_exchangeability.csv   (cell x scheme summary)
        results/small_area_loco_by_country.csv   (per held-out country)
Run:    python -m pcb.experiments.e55_small_area_exchangeability   (~30 min)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb import dapcb
from pcb.util import det_seed
from pcb.inference.conformal_band import conformal_band_quantile, loo_deviations
from pcb.experiments.e54_small_area_transport import (ALPHA, CORE, MIN_SIZES,
                                                      ROUNDS, _country_draws,
                                                      _load)

# the cells E54 reports on: the two that activate (60, 40) plus their immediate
# neighbours, so the comparison is not read off the activating cells alone
CELLS = [(mn, r) for mn in (100, 80, 60, 40) for r in ROUNDS]
assert set(m for m, _ in CELLS) <= set(MIN_SIZES)


def _fit(F_tr, V_tr):
    """Radii of the selected branch and of the plug-in PCB anchor, plus the
    transport center for a new unit. `tighten=False` with a zero center makes
    the returned upper edge the raw radius: the isotonic/[0,1] tightening in
    `dapcb` is built for a CDF target and does not apply to a departure."""
    E = loo_deviations(F_tr)
    fit = dapcb(E, V_tr, np.zeros(E.shape[1]), alpha=ALPHA, tighten=False)
    r_sel = np.asarray(fit.band[1], float)
    q_pcb, _ = conformal_band_quantile(E, ALPHA, studentize=False)
    r_pcb = np.full(E.shape[1], q_pcb)
    return r_sel, r_pcb, F_tr.mean(0), fit


def _covered(D_new, center, radius):
    return bool(np.all(np.abs(D_new - center) <= radius))


def _cell(cells, ctry):
    keys = list(cells)
    F = np.array([cells[k][0] for k in keys])
    V = np.array([cells[k][1] for k in keys])
    c_of = np.array([ctry[k] for k in keys])
    rows = []

    # --- LORO: hold out one region, keep its country-mates ------------------
    for i in range(len(keys)):
        m = np.ones(len(keys), bool); m[i] = False
        r_sel, r_pcb, mu, fit = _fit(F[m], V[m])
        rows.append(dict(scheme="LORO", held=c_of[i], K_train=int(m.sum()),
                         branch=fit.selected_branch, nominal=fit.coverage_level,
                         cov_sel=_covered(F[i], mu, r_sel),
                         cov_pcb=_covered(F[i], mu, r_pcb)))

    # --- LOCO: hold out a whole country -------------------------------------
    for c in np.unique(c_of):
        m = c_of != c
        if m.sum() < 10:
            continue
        r_sel, r_pcb, mu, fit = _fit(F[m], V[m])
        for i in np.flatnonzero(~m):
            rows.append(dict(scheme="LOCO", held=c, K_train=int(m.sum()),
                             branch=fit.selected_branch,
                             nominal=fit.coverage_level,
                             cov_sel=_covered(F[i], mu, r_sel),
                             cov_pcb=_covered(F[i], mu, r_pcb)))
    return pd.DataFrame(rows)


def _between_share(F, c_of):
    """Share of the variance in the sup-departure that sits BETWEEN countries --
    the clustering the LOCO scheme is testing for."""
    s = np.abs(F).max(1)
    grand = s.mean()
    b = w = 0.0
    for c in np.unique(c_of):
        m = c_of == c
        b += m.sum() * (s[m].mean() - grand) ** 2
        w += ((s[m] - s[m].mean()) ** 2).sum()
    return float(b / (b + w)) if (b + w) > 0 else float("nan")


def main():
    os.makedirs("results", exist_ok=True)
    d = _load()
    summ, bycty = [], []

    for min_n, rnd in CELLS:
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
        F = np.array([cells[k][0] for k in keys])
        c_of = np.array([ctry[k] for k in keys])
        bshare = _between_share(F, c_of)

        t = _cell(cells, ctry)
        t.insert(0, "essround", rnd); t.insert(0, "min_n", min_n)

        for scheme, g in t.groupby("scheme"):
            summ.append(dict(min_n=min_n, essround=rnd, scheme=scheme,
                             K=len(keys), n_countries=int(len(np.unique(c_of))),
                             between_country_var_share=round(bshare, 4),
                             n_eval=len(g),
                             branch=g.branch.mode().iat[0],
                             nominal=round(float(g.nominal.mean()), 4),
                             cov_selected=round(float(g.cov_sel.mean()), 4),
                             cov_pcb_anchor=round(float(g.cov_pcb.mean()), 4)))
        lo = t[t.scheme == "LOCO"]
        for c, g in lo.groupby("held"):
            bycty.append(dict(min_n=min_n, essround=rnd, cntry=c,
                              n_regions=len(g), K_train=int(g.K_train.iat[0]),
                              branch=g.branch.iat[0],
                              cov_selected=round(float(g.cov_sel.mean()), 4),
                              cov_pcb_anchor=round(float(g.cov_pcb.mean()), 4)))

        a = summ[-2:]
        print(f"min_n={min_n:>3} r{rnd}: K={len(keys)} "
              f"({len(np.unique(c_of))} countries, between-share {bshare:.2f})")
        for x in a:
            print(f"    {x['scheme']}: branch={x['branch']:<14} "
                  f"nominal={x['nominal']:.3f}  "
                  f"cov_selected={x['cov_selected']:.3f}  "
                  f"cov_PCB={x['cov_pcb_anchor']:.3f}")

    S = pd.DataFrame(summ); C = pd.DataFrame(bycty)
    S.to_csv("results/small_area_exchangeability.csv", index=False)
    C.to_csv("results/small_area_loco_by_country.csv", index=False)

    print("\n=== is the region an exchangeable unit across countries? ===")
    for scheme, g in S.groupby("scheme"):
        print(f"  {scheme}: PCB-anchor coverage {g.cov_pcb_anchor.min():.3f}"
              f"-{g.cov_pcb_anchor.max():.3f} (target 0.900), "
              f"selected-branch {g.cov_selected.min():.3f}-{g.cov_selected.max():.3f}")
    act = S[(S.branch == "deconvolution")]
    if len(act):
        print("\n  cells where the frozen selector activated:")
        print(act[["min_n", "essround", "scheme", "K", "nominal",
                   "cov_selected", "cov_pcb_anchor"]].to_string(index=False))
    if len(C):
        w = C.sort_values("cov_pcb_anchor").head(5)
        print("\n  worst LOCO countries (PCB anchor):")
        print(w[["min_n", "essround", "cntry", "n_regions",
                 "cov_pcb_anchor"]].to_string(index=False))


if __name__ == "__main__":
    main()
