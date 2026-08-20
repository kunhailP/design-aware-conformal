"""Contract tests for the LOO-deployment validity proposition (supplement).

Pins the two identities the proof rides on, exactly, on random draws --
(a) the target scores of the deployed and the fully symmetric (infeasible)
constructions COINCIDE, and (b) each symmetric calibration score is bounded
by the deployed score plus R*/K -- and then the theorem's conclusion: the
K/(K-1)-inflated deployed band covers at least the exact-construction floor,
distribution-free, at several K and error families.
"""
from __future__ import annotations

import numpy as np

from pcb.inference.conformal_band import loo_exact_inflation

ALPHA = 0.10


def _scores(X):
    K = X.shape[0] - 1
    S = X[:K].sum(0)
    a = np.array([np.max(np.abs(X[c] - (S - X[c]) / (K - 1)))
                  for c in range(K)])
    Rstar = np.max(np.abs(X[K] - S / K))
    e = (K + 1) / K * (X - X.sum(0) / (K + 1))
    en = np.max(np.abs(e), axis=1)
    return a, Rstar, en


def test_proof_identities_hold_exactly():
    rng = np.random.default_rng(0)
    for _ in range(300):
        K, T = int(rng.integers(3, 40)), int(rng.integers(1, 8))
        X = rng.standard_t(4, (K + 1, T))
        a, Rstar, en = _scores(X)
        assert abs(en[K] - Rstar) < 1e-9          # target scores coincide
        assert np.all(en[:K] <= a + Rstar / K + 1e-9)   # sandwich


def test_inflated_loo_band_meets_the_floor():
    rng = np.random.default_rng(1)
    for K, df in [(12, 4), (15, 3), (30, 6)]:
        m = int(np.ceil((1 - ALPHA) * (K + 1)))
        floor = m / (K + 1)
        reps, hit_inf, hit_raw = 6000, 0, 0
        for _ in range(reps):
            X = rng.standard_t(df, (K + 1, 5))
            a, Rstar, _ = _scores(X)
            q = np.sort(a)[m - 1]
            hit_raw += Rstar <= q
            hit_inf += Rstar <= q * loo_exact_inflation(K)
        se = np.sqrt(floor * (1 - floor) / reps)
        assert hit_inf / reps >= floor - 3 * se, (K, hit_inf / reps, floor)
        # the uninflated deficit delta_K is small (O(1/K)); sanity, not the pin
        assert hit_raw / reps >= floor - 3 * se - 1.5 / K


def test_inflation_factor():
    assert abs(loo_exact_inflation(30) - 30 / 29) < 1e-12
    assert loo_exact_inflation(2) == 2.0
