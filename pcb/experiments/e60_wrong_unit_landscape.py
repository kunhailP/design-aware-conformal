"""E60 — the wrong-unit coverage LANDSCAPE (Figure 1B).

e28 shows the collapse along one axis (trajectory length L) at one dependence
level. This maps the whole surface: whole-trajectory coverage of a band whose
score is attached to the wrong unit, over trajectory length L and
within-trajectory (round-to-round) dependence r. The right-unit band holds 90%
everywhere by exchangeability; the wrong-unit bands collapse along an
effective-multiplicity surface, with the independence benchmark 0.9^m as the
analytic reference slice at r = 0.

Same DGP family as e28 (K=30 countries, T=6 thresholds, AR(r) errors across
rounds, correlated thresholds), marginal and per-round scoring.

Output: results/wrong_unit_landscape.csv (L, dep, method, traj_cov_pct)
Run:    python -m pcb.experiments.e60_wrong_unit_landscape   (~2 min)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed

ALPHA, K, T, REPS = 0.10, 30, 6, 2000
LS = [2, 3, 4, 5, 6, 7, 8, 9, 10]
DEPS = [0.0, 0.3, 0.6, 0.9]


def _draw(rng, L, dep):
    """(K+1, L, T) error curves: AR(dep) across rounds, correlated thresholds."""
    cholT = np.linalg.cholesky(0.5 ** np.abs(np.subtract.outer(np.arange(T),
                                                               np.arange(T)))
                               + 1e-9 * np.eye(T))
    e = rng.standard_normal((K + 1, L, T)) @ cholT.T
    for r in range(1, L):
        e[:, r] = dep * e[:, r - 1] + np.sqrt(1 - dep ** 2) * e[:, r]
    return e


def _cell(L, dep):
    hit = dict(marginal=0, per_round=0, trajectory=0)
    for rep in range(REPS):
        rng = np.random.default_rng(det_seed("e60", L, int(dep * 10), rep))
        e = _draw(rng, L, dep)
        cal, tgt = e[:K], e[K]
        m = int(np.ceil((1 - ALPHA) * (K + 1)))
        # trajectory unit: one sup score per country
        q = np.sort(np.max(np.abs(cal), axis=(1, 2)))[m - 1]
        hit["trajectory"] += np.max(np.abs(tgt)) <= q
        # per-round unit: quantile per round, joint coverage demanded
        qr = np.sort(np.max(np.abs(cal), axis=2), axis=0)[m - 1]
        hit["per_round"] += np.all(np.max(np.abs(tgt), axis=1) <= qr)
        # marginal unit: per (round, threshold) cell
        qc = np.sort(np.abs(cal), axis=0)[m - 1]
        hit["marginal"] += np.all(np.abs(tgt) <= qc)
    return [dict(L=L, dep=dep, method=k, traj_cov_pct=100 * v / REPS)
            for k, v in hit.items()]


def main():
    os.makedirs("results", exist_ok=True)
    rows = [r for L in LS for dep in DEPS for r in _cell(L, dep)]
    d = pd.DataFrame(rows)
    d.to_csv("results/wrong_unit_landscape.csv", index=False)
    w = d[d.method == "marginal"].pivot(index="dep", columns="L",
                                        values="traj_cov_pct")
    print("marginal-unit whole-trajectory coverage (%):")
    print(w.round(1).to_string())
    t = d[d.method == "trajectory"]
    print(f"\ntrajectory-unit: min {t.traj_cov_pct.min():.1f}% "
          f"(nominal 90; exchangeability holds at every cell)")


if __name__ == "__main__":
    main()
