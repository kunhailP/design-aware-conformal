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


def test_loo_centered_deconvolution_coverage():
    """Theorem 4' extension (supplement, prop:loodec): run the (A1)
    scale-family DGP THROUGH the deployed leave-one-out centering -- the
    scores are then dependent, summing to zero identically, so the i.i.d.
    theorem does not apply verbatim -- and check the always-deconvolve band
    still covers the latent target at the deconvolution level up to the
    theorem's remainder, with the centering cost itself small (gamma_K).
    Two W families: bounded symmetric (uniform, matching (A3)'s boundedness
    clause LITERALLY, so the Hoeffding step's hypothesis holds verbatim)
    and Gaussian (robustness beyond the literal assumption)."""
    from pcb.inference.conformal_band import loo_deviations
    from pcb.inference.design_aware import (_finite_quantile,
                                            deconv_target_scale)

    rng = np.random.default_rng(3)
    K, T, a_dec, reps = 250, 6, 0.05, 1200
    s_R = 0.05
    r3 = np.sqrt(3.0)                      # unit-variance bounded support
    for fam in ("bounded", "gaussian"):
        hit_loo = hit_ind = 0
        for _ in range(reps):
            v = rng.uniform(0.03, 0.08, K + 1)[:, None] * np.ones((1, T))
            W = (rng.uniform(-r3, r3, (K + 1, T)) if fam == "bounded"
                 else rng.standard_normal((K + 1, T)))
            Y = np.sqrt(s_R**2 + v**2) * W
            mu = 0.3 + 0.05 * np.arange(T)  # common center, removed by LOO
            D = mu[None] + Y[:K]
            E = loo_deviations(D)
            assert np.allclose(E.sum(0), 0, atol=1e-9)  # dependence, verified
            V = v[:K]
            # deployed LOO-centered construction
            sT = deconv_target_scale(E, V)
            q = _finite_quantile(
                np.max(np.abs(E) / np.sqrt(sT[None]**2 + V**2), 1), a_dec)
            err = s_R * W[K] - Y[:K].mean(0)  # latent target vs transport ctr
            hit_loo += np.max(np.abs(err) / sT) <= q
            # independent (A1-verbatim) construction, same draw (gamma_K pin)
            sTi = deconv_target_scale(Y[:K], V)
            qi = _finite_quantile(
                np.max(np.abs(Y[:K]) / np.sqrt(sTi[None]**2 + V**2), 1), a_dec)
            hit_ind += np.max(np.abs(s_R * W[K]) / sTi) <= qi
        cov_loo, cov_ind = hit_loo / reps, hit_ind / reps
        se = np.sqrt(a_dec * (1 - a_dec) / reps)
        # Absolute floor: the theorem's level is 1 - a_dec - epsilon_{K,B} -
        # gamma_K, and epsilon_{K,B} (the SCALE-error remainder, present for
        # the independent construction too) is family-dependent -- measured
        # here at ~0.05 for the bounded-uniform max (large L*q*) and ~0.015
        # Gaussian. The 0.06 allowance is that budget, not slack in gamma_K.
        assert cov_loo >= 1 - a_dec - 3 * se - 0.06, (fam, cov_loo)
        # The gamma_K pin -- the proposition's own content: the LOO centering
        # moves coverage by at most MC noise relative to the independent
        # (A1-verbatim) construction on the SAME draws.
        assert abs(cov_loo - cov_ind) <= 0.02 + 3 * se, (fam, cov_loo, cov_ind)


def test_dapcb_ships_the_inflation_by_default():
    """The deployed API returns the K/(K-1)-inflated anchor radius (the band
    prop:loo(i) certifies), while the gates/diagnostics stay on the frozen
    uninflated rule; loo_center=False recovers the symmetric-construction
    radius exactly."""
    from pcb import dapcb
    from pcb.inference.conformal_band import loo_deviations

    rng = np.random.default_rng(2)
    K, T = 30, 6
    F = rng.normal(0, 0.03, (K, T))
    E = loo_deviations(F)
    V = np.abs(rng.normal(0.002, 0.0004, (K, T)))
    center = np.full(T, 0.5)
    fit = dapcb(E, V, center, alpha=ALPHA, tighten=False)
    ref = dapcb(E, V, center, alpha=ALPHA, tighten=False, loo_center=False)
    r = np.asarray(fit.band[1]) - center
    r0 = np.asarray(ref.band[1]) - center
    assert fit.selected_branch == ref.selected_branch      # frozen rule intact
    assert np.allclose(r, r0 * loo_exact_inflation(K), atol=1e-12)
    # diagnostics identical: the inflation touches the returned radius only
    assert fit.gain_lcb == ref.gain_lcb or (np.isnan(fit.gain_lcb)
                                            and np.isnan(ref.gain_lcb))
    assert fit.coverage_level == ref.coverage_level
