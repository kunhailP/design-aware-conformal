"""U0 (unstudentized score) must be finite-sample exact under trajectory
exchangeability alone — no scale is estimated, so heteroskedasticity and
heavy tails cannot break rank symmetry."""
import numpy as np

from pcb.inference.fixed_trajectory_band import (trajectory_modulation,
                                                 trajectory_quantile,
                                                 trajectory_scores)

K, L, T, SIMS, ALPHA = 30, 4, 10, 800, 0.10


def _draw_heavy(rng, n):
    """Heteroskedastic + heavy-tailed (t3) trajectory errors."""
    h = np.linspace(0.3, 2.0, T)
    a = rng.standard_t(3, size=(n, 1, 1)) * 0.02
    b = rng.normal(0, 0.02, size=(n, L, 1))
    return a + b + rng.standard_t(3, size=(n, L, T)) * 0.01 * h


def test_unstudentized_coverage_at_attainable_level():
    rng = np.random.default_rng(21)
    hits = 0
    for _ in range(SIMS):
        E = _draw_heavy(rng, K + 1)
        cal, tgt = E[:K], E[K]
        s = trajectory_modulation(cal, "none")
        assert np.all(s == 1.0)
        q, m, attain = trajectory_quantile(trajectory_scores(cal, s), ALPHA)
        hits += float(np.max(np.abs(tgt)) <= q)
    cov = hits / SIMS
    attain = np.ceil((1 - ALPHA) * (K + 1)) / (K + 1)
    mc3 = 3 * np.sqrt(attain * (1 - attain) / SIMS)
    assert attain - mc3 <= cov <= attain + mc3, \
        f"U0 coverage {cov:.3f} not at attainable {attain:.3f} ± {mc3:.3f}"


def test_unstudentized_score_is_scale_free():
    """Multiplying all errors by a constant scales scores and quantile alike,
    leaving the coverage decision invariant."""
    rng = np.random.default_rng(22)
    E = _draw_heavy(rng, K + 1)
    s = np.ones((L, T))
    q1, _, _ = trajectory_quantile(trajectory_scores(E[:K], s), ALPHA)
    q2, _, _ = trajectory_quantile(trajectory_scores(3.7 * E[:K], s), ALPHA)
    t1 = np.max(np.abs(E[K]))
    assert np.isclose(q2, 3.7 * q1)
    assert (t1 <= q1) == (3.7 * t1 <= q2)
