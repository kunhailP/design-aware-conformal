"""The conformal quantile must be the exact order statistic m = ceil((1-a)(K+1)),
never an interpolation quantile."""
import numpy as np

from pcb.inference.clustered_band import clustered_quantile
from pcb.inference.fixed_trajectory_band import trajectory_quantile


def test_exact_order_statistic_small_k():
    scores = np.arange(1.0, 11.0)          # K = 10
    # m = ceil(0.9 * 11) = 10 -> the 10th smallest = 10.0
    assert clustered_quantile(scores, 0.10) == 10.0
    q, m, attain = trajectory_quantile(scores, 0.10)
    assert (q, m) == (10.0, 10) and np.isclose(attain, 10 / 11)
    # an interpolation quantile would give np.quantile(scores, .9) = 9.1
    assert not np.isclose(q, np.quantile(scores, 0.9))


def test_small_k_returns_trivial_band_level():
    scores = np.arange(1.0, 6.0)           # K = 5, m = ceil(.9*6) = 6 > 5
    assert np.isinf(clustered_quantile(scores, 0.10))
    q, m, attain = trajectory_quantile(scores, 0.10)
    assert np.isinf(q) and m == 6 and attain == 1.0


def test_order_index_matches_manual_formula():
    rng = np.random.default_rng(0)
    for K in (7, 20, 34, 116, 243):
        scores = rng.exponential(size=K)
        for alpha in (0.05, 0.10, 0.20):
            m = int(np.ceil((1 - alpha) * (K + 1)))
            expected = np.inf if m > K else np.sort(scores)[m - 1]
            assert np.array_equal(clustered_quantile(scores, alpha), expected)
