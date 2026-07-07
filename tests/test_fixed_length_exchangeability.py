"""Finite-sample validity of the fixed-L trajectory band under exchangeable
country trajectories (with strong WITHIN-country round dependence, the regime
that breaks pooled country-round calibration)."""
import numpy as np

from pcb.inference.fixed_trajectory_band import (fixed_trajectory_band,
                                                 slot_modulation,
                                                 trajectory_scores,
                                                 trajectory_quantile)

L, T, K, SIMS, ALPHA = 4, 10, 40, 400, 0.10


def _draw_trajectories(rng, n):
    """Country effect shared across rounds -> within-country dependence."""
    a = rng.normal(0, 0.04, size=(n, 1, 1))            # persistent country bias
    e = rng.normal(0, 0.02, size=(n, L, T))
    return a + e


def test_trajectory_coverage_at_least_nominal():
    rng = np.random.default_rng(7)
    hits = 0
    for _ in range(SIMS):
        E = _draw_trajectories(rng, K + 1)
        cal, tgt = E[:K], E[K]
        s = slot_modulation(cal)
        q, _, _ = trajectory_quantile(trajectory_scores(cal, s), ALPHA)
        hits += float(np.max(np.abs(tgt) / s) <= q)
    cov = hits / SIMS
    mc3 = 3 * np.sqrt(0.9 * 0.1 / SIMS)                 # ~4.5pp
    assert cov >= 1 - ALPHA - mc3, f"coverage {cov:.3f} below nominal"


def test_band_object_matches_score_rule():
    rng = np.random.default_rng(8)
    E = _draw_trajectories(rng, K + 1)
    cal, tgt = E[:K], E[K]
    center = np.tile(np.linspace(0.2, 0.8, T), (L, 1))
    lo, hi, audit = fixed_trajectory_band(cal, center, ALPHA, tighten=False)
    truth = center - tgt                                 # theta = theta_hat - E
    in_band = np.all((lo <= truth) & (truth <= hi))
    score_rule = np.max(np.abs(tgt) / audit["s"]) <= audit["critical"]
    assert in_band == score_rule
