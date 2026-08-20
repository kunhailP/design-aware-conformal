"""E57 — the feasibility frontier, assembled from committed results.

Two universal quantities govern the design-aware correction: the maximal width
gain 1 - sqrt(1 - rho^2) (AW-1) and the reliability floor sqrt(2/(K-1))
(supplement Lemma: universal floor -- any unbiased variance estimator from K
exchangeable populations, not just the frozen diagnostic). Their frozen
instantiations rho_0 = 0.47 and K >= 1 + 2/tau_D^2 = 94 split the (K, rho)
plane into three regimes: unnecessary / unlearnable / feasible.

This experiment places every real-data cell the paper reports onto that plane,
from the committed CSVs (no microdata needed):

  WVS full-coverage items    (wvs_gate_probe.csv)        -> unnecessary
  ESS national-unit scan     (ess_subgroup_rho_scan.csv) -> left of the floor
  ESS small-area estimand    (small_area_transport.csv)  -> crosses both;
                                                            fired cells marked

Output: results/feasibility_frontier.csv, figures/feasibility_frontier.pdf
Run:    python -m pcb.experiments.e57_feasibility_frontier
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

RHO0 = 0.47
TAU_D = (0.02 - 0.0061) / 0.0943
KSTAR = int(np.ceil(1 + 2 / TAU_D ** 2))          # 94


def _regime(K: int, rho_lcb: float) -> str:
    if rho_lcb <= RHO0:
        return "unnecessary"
    return "unlearnable" if K < KSTAR else "feasible"


def main():
    os.makedirs("results", exist_ok=True)
    rows = []

    w = pd.read_csv("results/wvs_gate_probe.csv")
    for r in w.itertuples():
        rows.append(dict(dataset="WVS full-coverage items", cell=r.item,
                         K=int(r.K), rho_lcb=float(r.rho_lcb),
                         activated=False))

    e = pd.read_csv("results/ess_subgroup_rho_scan.csv")
    for r in e.itertuples():
        rows.append(dict(dataset="ESS national-unit scan",
                         cell=f"{r.subgroup}/{r.outcome}/{r.min_n}",
                         K=int(r.K), rho_lcb=float(r.rho_lcb),
                         activated=bool(r.branch == "deconvolution")))

    s = pd.read_csv("results/small_area_transport.csv")
    for r in s.itertuples():
        name = ("ESS small-area (e54)" if r.pool == "all countries"
                else "ESS small-area, common NUTS level")
        rows.append(dict(dataset=name,
                         cell=f"min_n{r.min_n}/r{r.essround}",
                         K=int(r.K), rho_lcb=float(r.rho_lcb),
                         activated=bool(r.branch == "deconvolution")))

    d = pd.DataFrame(rows)
    d["regime"] = [_regime(k, rl) for k, rl in zip(d.K, d.rho_lcb)]
    d.to_csv("results/feasibility_frontier.csv", index=False)

    print(f"=== E57: the feasibility frontier (rho0={RHO0}, K*={KSTAR}) ===")
    for name, g in d.groupby("dataset"):
        print(f"\n{name}: {len(g)} cells, K {g.K.min()}-{g.K.max()}, "
              f"rho_LCB {g.rho_lcb.min():.3f}-{g.rho_lcb.max():.3f}")
        print("  regimes:", dict(g.regime.value_counts()))
        if g.activated.any():
            f = g[g.activated]
            print(f"  ACTIVATED in {len(f)} cells (all '{f.regime.unique()}')")
    only_feasible_fires = bool(
        (d.loc[d.activated, "regime"] == "feasible").all())
    print(f"\nthe selector fired only in the feasible regime: "
          f"{only_feasible_fires}")

    try:
        from pcb.figures.fig_frontier import main as _fig
        _fig()
    except Exception as e:                                  # pragma: no cover
        print(f"(figure skipped: {e})")


if __name__ == "__main__":
    main()
