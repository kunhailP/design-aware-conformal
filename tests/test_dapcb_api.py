"""Contract tests for the public dapcb() API."""
import numpy as np

from pcb import dapcb


def test_low_noise_routes_to_pcb_and_covers():
    rng = np.random.default_rng(0)
    K, T = 40, 6
    E = rng.normal(0, 0.1, (K, T))
    V = np.full((K, T), 0.005)                 # tiny design noise → low ρ
    fit = dapcb(E, V, np.full(T, 0.5))
    assert fit.selected_branch == "PCB"
    assert fit.coverage_level == 0.90
    lo, hi = fit.band
    assert np.all(hi >= lo) and lo.shape == (T,)


def test_high_noise_small_K_abstains_to_conservative():
    """Large design noise at small K must NOT ride the deconvolution branch."""
    rng = np.random.default_rng(1)
    K, T = 30, 4
    E = rng.normal(0, 0.1, (K, T)) + rng.normal(0, 0.12, (K, T))
    V = np.abs(0.12 * (1 + rng.normal(0, 0.15, (K, T))))
    fit = dapcb(E, V, np.full(T, 0.5))
    assert fit.selected_branch in ("conservative", "PCB")   # never risky deconv
    assert fit.coverage_level >= 0.90
    assert fit.fallback_reason != ""


def test_empirical_coverage_at_least_floor():
    """Routed pipeline covers the latent target ≥ floor over many draws.

    center=0.5 keeps the CDF-valued band inside [0,1] (a center at 0 would have
    the [0,1] clip amputate the lower half — an evaluation artifact, not a method
    property). Moderate ρ, K=120 (a regime where the safe deconvolution activates
    and the finite-K remainder is small).
    """
    rng = np.random.default_rng(2)
    K, T, reps, hits = 120, 4, 1500, 0
    for _ in range(reps):
        s_r, v = 0.1, 0.1 * 0.7
        E = rng.normal(0, s_r, (K, T)) + rng.normal(0, v, (K, T))
        V = np.abs(v * (1 + rng.normal(0, 0.15, (K, T))))
        target = 0.5 + rng.normal(0, s_r, T)     # latent target CDF value
        fit = dapcb(E, V, np.full(T, 0.5), tighten=False)
        lo, hi = fit.band
        hits += int(np.all((target >= lo) & (target <= hi)))
    assert hits / reps >= 0.88 - 0.02


def test_pcb_branch_is_exact_unstudentized_at_small_K():
    """The deployed base band is the unstudentized U0 band: finite-sample exact at
    any K (SMALLK_CORRECTION). Check (a) it is constant-width (U0 signature, pre-
    clip) and (b) empirical coverage ≥ the Vovk floor at a small K where the old
    studentized S2 band undercovered."""
    rng = np.random.default_rng(7)
    K, T, reps, hits = 25, 4, 4000, 0
    floor = np.ceil(0.9 * (K + 1)) / (K + 1)          # 24/26 = 0.923
    for _ in range(reps):
        s_r = 0.1
        E = rng.normal(0, s_r, (K, T)) + rng.normal(0, 0.02, (K, T))   # low ρ → PCB
        V = np.full((K, T), 0.02)
        target = 0.5 + rng.normal(0, s_r, T)
        fit = dapcb(E, V, np.full(T, 0.5), tighten=False)
        assert fit.selected_branch == "PCB"
        lo, hi = fit.band
        hits += int(np.all((target >= lo) & (target <= hi)))
    assert hits / reps >= floor - 0.02               # tracks the exact guarantee


def test_shape_validation():
    import pytest
    with pytest.raises(ValueError):
        dapcb(np.zeros((5, 4)), np.zeros((5, 3)), np.zeros(4))
