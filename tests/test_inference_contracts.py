"""Contract tests for the interval methods (run with `make test`).

These pin the invariants the methods MUST satisfy regardless of implementation,
so future edits cannot silently break the guarantees in docs/PROOFS.md.
"""
import numpy as np
from pcb.inference.headcount import weighted_headcount
from pcb.inference.population_conformal import (
    population_conformal_interval, _two_sided_quantile_levels)


def test_headcount_monotone_in_threshold():
    y = np.array([1., 2., 3., 4.]); w = np.ones(4)
    thr = np.array([0.5, 2.5, 5.0])
    hc = weighted_headcount(y, w, thr)
    assert hc[0] <= hc[1] <= hc[2]
    assert abs(hc[2] - 1.0) < 1e-9


def test_conformal_band_brackets_zero_when_errors_symmetric():
    E = np.linspace(-0.1, 0.1, 21)[:, None]  # symmetric calib errors, 1 threshold
    lo, hi = population_conformal_interval(E, alpha=0.1)
    assert lo[0] < 0 < hi[0]


def test_quantile_levels_in_unit_interval():
    lo, hi = _two_sided_quantile_levels(3, 0.1)
    assert 0.0 <= lo <= hi <= 1.0


def test_pcb_band_in_unit_interval_and_isotonic():
    # PCB band must lie in [0,1] and be monotone after tightening (Lemma PCB-2).
    from pcb.inference.conformal_band import population_conformal_band
    rng = np.random.default_rng(0)
    E = rng.normal(scale=0.02, size=(20, 19))
    center = np.sort(rng.uniform(0, 1, size=19))  # a CDF-like curve
    lo, hi = population_conformal_band(E, center, alpha=0.1, tighten=True)
    assert lo.min() >= 0 and hi.max() <= 1
    assert np.all(np.diff(lo) >= -1e-9) and np.all(np.diff(hi) >= -1e-9)
    assert np.all(hi >= lo)


def test_pcb_tightened_never_wider_than_raw():
    # Lemma PCB-2: tightening is coverage-preserving and never widens.
    from pcb.inference.conformal_band import population_conformal_band
    rng = np.random.default_rng(1)
    E = rng.normal(scale=0.03, size=(15, 19))
    center = np.sort(rng.uniform(0, 1, size=19))
    lo_r, hi_r = population_conformal_band(E, center, alpha=0.1, tighten=False)
    lo_t, hi_t = population_conformal_band(E, center, alpha=0.1, tighten=True)
    assert np.mean(hi_t - lo_t) <= np.mean(hi_r - lo_r) + 1e-9


def test_pcb_small_k_returns_trivial_band():
    # Honest small-K penalty: when the level exceeds K, band -> [0,1].
    from pcb.inference.conformal_band import population_conformal_band
    E = np.random.default_rng(2).normal(scale=0.02, size=(3, 19))
    lo, hi = population_conformal_band(E, np.linspace(0, 1, 19), alpha=0.1)
    assert np.allclose(lo, 0) and np.allclose(hi, 1)


def test_weighted_conformal_reduces_to_population_conformal_under_uniform_weights():
    # M3 with uniform weights must ≈ M2 (the key correctness contract).
    from pcb.inference.weighted_conformal import weighted_conformal_interval
    rng = np.random.default_rng(0)
    E = rng.normal(size=(40, 3))
    lo_w, hi_w = weighted_conformal_interval(E, np.ones(40), alpha=0.1)
    lo_c, hi_c = population_conformal_interval(E, alpha=0.1)
    assert np.allclose(lo_w, lo_c, atol=0.05) and np.allclose(hi_w, hi_c, atol=0.05)


def test_localized_band_in_unit_interval_and_monotone():
    from pcb.inference.localized_band import localized_conformal_band
    rng = np.random.default_rng(0)
    feats = rng.normal(size=(20, 5))
    E = 0.01 * feats @ rng.normal(size=(5, 19)) + rng.normal(scale=0.01, size=(20, 19))
    center = np.sort(rng.uniform(0, 1, 19))
    lo, hi, b = localized_conformal_band(E, feats, rng.normal(size=5), center, alpha=0.1)
    assert lo.min() >= 0 and hi.max() <= 1
    assert np.all(np.diff(lo) >= -1e-9) and np.all(np.diff(hi) >= -1e-9)
    assert b.shape == (19,)


def test_localized_band_reduces_to_pcb_when_features_uninformative():
    # If features carry no signal, predicted bias ≈ 0 and the band ≈ plain PCB.
    from pcb.inference.localized_band import localized_conformal_band
    from pcb.inference.conformal_band import population_conformal_band
    rng = np.random.default_rng(3)
    feats = rng.normal(size=(30, 5))                 # unrelated to E
    E = rng.normal(scale=0.02, size=(30, 19))
    center = np.sort(rng.uniform(0, 1, 19))
    target = rng.normal(size=5)
    lo_l, hi_l, _ = localized_conformal_band(E, feats, target, center, alpha=0.1, tighten=False)
    lo_p, hi_p = population_conformal_band(E, center, alpha=0.1, tighten=False)
    # not identical (finite-sample regression noise) but close in mean width
    assert abs(np.mean(hi_l - lo_l) - np.mean(hi_p - lo_p)) < 0.05


# M4/M5 are still design stubs — pin that they are not yet claimed as done.
def test_hierarchical_and_minimal_label_not_yet_implemented():
    import pytest
    from pcb.inference.hierarchical_conformal import hierarchical_conformal_interval
    from pcb.inference.minimal_label import minimal_label_update
    with pytest.raises(NotImplementedError):
        hierarchical_conformal_interval({})
    with pytest.raises(NotImplementedError):
        minimal_label_update((np.zeros(1), np.zeros(1)), np.zeros(1), np.zeros(1),
                             np.ones(1), np.array([1.0]))
