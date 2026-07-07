"""S1 (independent split modulation) must be finite-sample exact: coverage at
the attainable level m/(K+1), from above AND below, under exchangeable
trajectories — including heteroskedastic thresholds where the scale matters."""
import numpy as np

from pcb.inference.fixed_trajectory_band import (slot_modulation,
                                                 trajectory_quantile,
                                                 trajectory_scores)

K_MOD, K_CAL, L, T, SIMS, ALPHA = 12, 24, 4, 10, 800, 0.10


def _draw(rng, n):
    h = np.linspace(0.4, 1.6, T)                    # heteroskedastic thresholds
    a = rng.normal(0, 0.03, size=(n, 1, 1))
    b = rng.normal(0, 0.02, size=(n, L, 1))
    return a + b + rng.normal(0, 0.015, size=(n, L, T)) * h


def test_split_modulation_hits_attainable_level_two_sided():
    rng = np.random.default_rng(11)
    hits = 0
    for _ in range(SIMS):
        E = _draw(rng, K_MOD + K_CAL + 1)
        s = slot_modulation(E[:K_MOD])              # disjoint modulation set
        cal, tgt = E[K_MOD:K_MOD + K_CAL], E[-1]
        q, m, attain = trajectory_quantile(trajectory_scores(cal, s), ALPHA)
        hits += float(np.max(np.abs(tgt) / s) <= q)
    cov = hits / SIMS
    attain = np.ceil((1 - ALPHA) * (K_CAL + 1)) / (K_CAL + 1)
    mc3 = 3 * np.sqrt(attain * (1 - attain) / SIMS)
    assert attain - mc3 <= cov <= attain + mc3, \
        f"S1 coverage {cov:.3f} not at attainable {attain:.3f} ± {mc3:.3f}"


def test_split_scale_is_fixed_for_calibration_and_target():
    """The same s must studentise calibration and target — no refitting."""
    rng = np.random.default_rng(12)
    E = _draw(rng, K_MOD + K_CAL + 1)
    s = slot_modulation(E[:K_MOD])
    s2 = slot_modulation(E[:K_MOD])                 # deterministic given the set
    assert np.array_equal(s, s2)
    assert s.shape == (L, T) and np.all(s > 0)
