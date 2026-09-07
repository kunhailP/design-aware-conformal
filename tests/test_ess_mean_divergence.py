"""Contracts for the narrow ESS mean-versus-CDF comparison."""
from __future__ import annotations

import numpy as np
import pandas as pd

from pcb.experiments.e64_ess_mean_divergence import (
    _mean_decline_bound,
    _mean_from_cdf,
)


def _point_mass_cdf(value: int) -> np.ndarray:
    return (value <= np.arange(10)).astype(float)


def test_mean_is_recovered_from_ordinal_cdf():
    for value in range(11):
        assert _mean_from_cdf(_point_mass_cdf(value)) == value


def test_mean_decline_bound_uses_first_minus_last_direction():
    curves = np.stack([_point_mass_cdf(6), _point_mass_cdf(4)])
    boots = np.repeat(curves[None], 100, axis=0)
    out = _mean_decline_bound(curves, boots)
    assert out["mean_first"] == 6
    assert out["mean_last"] == 4
    assert out["mean_decline"] == 2
    assert out["mean_certified"]


def test_zero_mean_change_is_not_called_certified():
    curves = np.stack([_point_mass_cdf(5), _point_mass_cdf(5)])
    boots = np.repeat(curves[None], 100, axis=0)
    out = _mean_decline_bound(curves, boots)
    assert out["mean_decline"] == 0
    assert out["mean_lower"] == 0
    assert not out["mean_certified"]


def test_recorded_result_closes_the_figure_gate():
    result = pd.read_csv("results/ess_mean_divergence.csv")
    assert len(result) == 15
    assert result.cdf_net.all()
    assert result.mean_certified.all()
    assert not result.divergence.any()
