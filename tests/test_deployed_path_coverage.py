"""Coverage of the DEPLOYED code path — tighten=True, CDF-shaped truth.

The prior suite's coverage tests all passed tighten=False, so the isotonic
tightening (Lemma PCB-2) — the default every deployment uses — had structural
checks but no Monte-Carlo coverage evidence. This test closes that gap with a
monotone [0,1]-valued truth (the object the lemma is about) and additionally
exercises the grand-mean-vs-LOO center asymmetry fix: scores built with
leave-one-out centers keep the guarantee an unsurveyed-target deployment needs.
"""
import numpy as np

from pcb.dapcb import dapcb
from pcb.inference.conformal_band import loo_deviations

ALPHA = 0.10
T = 9
GRID = np.linspace(-2, 2, T)


def _cdf(shift, scale):
    return 1.0 / (1.0 + np.exp(-(GRID - shift) / scale))


def _panel(rng, K):
    """K+1 latent country CDFs = logistic curves with random shift/scale."""
    shifts = rng.normal(0, 0.4, K + 1)
    scales = np.exp(rng.normal(0, 0.15, K + 1))
    return np.array([_cdf(sh, sc) for sh, sc in zip(shifts, scales)])


def test_tightened_band_covers_monotone_truth_with_loo_centers():
    rng = np.random.default_rng(21)
    K, reps = 30, 1200
    floor = np.ceil((1 - ALPHA) * (K + 1)) / (K + 1)      # attainable level
    mc3 = 3 * np.sqrt(floor * (1 - floor) / reps)
    cover = 0
    for _ in range(reps):
        F = _panel(rng, K)                                  # (K+1, T) CDFs
        cal, target = F[:K], F[K]
        E = loo_deviations(cal)                             # symmetric scores
        center = cal.mean(0)                                # unsurveyed-target center
        fit = dapcb(E, np.zeros_like(E), center, alpha=ALPHA, tighten=True)
        lo, hi = fit.band
        cover += int(np.all((target >= lo - 1e-12) & (target <= hi + 1e-12)))
    assert cover / reps >= floor - mc3, cover / reps


def test_grand_mean_centers_are_anticonservative_relative_to_loo():
    """Documents the direction of the center asymmetry the fix removes:
    grand-mean calibration scores are stochastically smaller than LOO ones,
    so their quantile — hence coverage — can only be lower."""
    rng = np.random.default_rng(22)
    K = 12                                                  # small K: bias visible
    diffs = []
    for _ in range(400):
        F = _panel(rng, K)[:K]
        e_grand = np.max(np.abs(F - F.mean(0)), axis=1)
        e_loo = np.max(np.abs(loo_deviations(F)), axis=1)
        m = int(np.ceil((1 - ALPHA) * (K + 1)))
        if m <= K:
            diffs.append(np.sort(e_loo)[m - 1] - np.sort(e_grand)[m - 1])
    diffs = np.array(diffs)
    assert diffs.mean() > 0                                  # LOO quantile larger
    assert np.mean(diffs >= -1e-12) > 0.99                   # and ≥ draw-by-draw
