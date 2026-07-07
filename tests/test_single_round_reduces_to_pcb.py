"""Estimand A must reduce exactly to the original PCB on a one-curve-per-
country calibration matrix, and refuse dependence by construction."""
import numpy as np

from pcb.inference.clustered_curve_band import (clustered_curve_band,
                                                select_one_round_per_country)
from pcb.inference.conformal_band import population_conformal_band
from pcb.inference.fixed_trajectory_band import (fixed_trajectory_band,
                                                 stack_trajectories)


def _fake_panel(K=20, rounds_per=3, T=10, seed=0):
    rng = np.random.default_rng(seed)
    E = rng.normal(0, 0.05, size=(K * rounds_per, T))
    countries = np.repeat(np.arange(K), rounds_per)
    rounds = np.tile(np.arange(rounds_per), K)
    return E, countries, rounds


def test_selection_takes_exactly_one_latest_round_per_country():
    E, c, r = _fake_panel()
    E_sel, labels, sel_r = select_one_round_per_country(E, c, r, "latest")
    assert len(labels) == len(np.unique(c)) == E_sel.shape[0]
    assert np.all(sel_r == r.max())


def test_curve_band_equals_pcb_on_selected_matrix():
    E, c, r = _fake_panel()
    center = np.linspace(0.1, 0.9, E.shape[1])
    E_sel, _, _ = select_one_round_per_country(E, c, r, "latest")
    lo0, hi0 = population_conformal_band(E_sel, center, 0.1)
    lo1, hi1 = clustered_curve_band(E, c, r, center, 0.1, "latest")
    assert np.allclose(lo0, lo1) and np.allclose(hi0, hi1)


def test_trajectory_band_with_L1_equals_curve_band():
    E, c, r = _fake_panel()
    center = np.linspace(0.1, 0.9, E.shape[1])
    traj, labels, dropped = stack_trajectories(E, c, r, L=1)
    assert not dropped
    lo_t, hi_t, _ = fixed_trajectory_band(traj, center[None, :], 0.1)
    lo_c, hi_c = clustered_curve_band(E, c, r, center, 0.1, "latest")
    assert np.allclose(lo_t[0], lo_c) and np.allclose(hi_t[0], hi_c)
