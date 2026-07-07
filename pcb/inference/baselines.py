"""Reviewer-killer baselines for the simultaneous poverty-curve band.

Two bands a referee will immediately propose as "why not just ...":

  * bonferroni_band   — per-threshold conformal at level alpha/T, union-bounded
                        to simultaneous validity. Distribution-free but pays the
                        full multiplicity correction at every threshold.
  * gaussian_sup_band — the classical (Scheffe-type) simultaneous confidence
                        band: estimate the threshold covariance and use the
                        sup-Gaussian critical value. Parametric, mean-zero.

Both return ABSOLUTE bands [lo, hi] clipped to [0,1], matching
`conformal_band.population_conformal_band`, so coverage/width are directly
comparable to PCB. The point of the comparison (PROOFS.md Thm 3): PCB is never
wider than Bonferroni, and unlike the Gaussian sup-band it needs no
Gaussian/unbiasedness assumption — so it keeps coverage under transport bias.
"""
from __future__ import annotations

import numpy as np

from .population_conformal import population_conformal_interval


def bonferroni_band(cal_errors, center, alpha=0.1):
    """Per-threshold conformal at alpha/T, union-bounded -> simultaneous valid.

    cal_errors : (K, T) leave-one-population-out error curves E_i(t)=θ̂−θ.
    center     : (T,) target plug-in curve F̂.
    Returns (lo, hi) absolute, clipped to [0,1].
    """
    E = np.asarray(cal_errors, float)
    T = E.shape[1]
    lo_off, hi_off = population_conformal_interval(E, alpha=alpha / T)
    # θ = θ̂ − E, so the band for the truth is [center − hi, center − lo].
    lo = np.clip(center - hi_off, 0.0, 1.0)
    hi = np.clip(center - lo_off, 0.0, 1.0)
    return lo, hi


def bonferroni_studentized_band(cal_errors, center, alpha=0.1, floor_frac=0.05):
    """Theory-faithful Bonferroni: SYMMETRIC studentized, matched to PCB.

    Per threshold t, q_t = (1−α/T) empirical quantile of |E_i(t)|/s(t); band is
    center ± q_t·s(t). This is the construction the efficiency theorem compares to
    (PROOFS.md Thm 3: the sup-quantile c_α ≤ the per-threshold Bonferroni
    quantile), so PCB should be no wider than this. Contrast with `bonferroni_band`
    (asymmetric signed quantiles), which can be tighter under transport bias and
    motivates the localized/bias-corrected band.
    """
    E = np.asarray(cal_errors, float)
    K, T = E.shape
    s = np.maximum(E.std(0), floor_frac * max(E.std(0).max(), 1e-12))
    U = np.abs(E) / s                                   # studentized |error|
    lvl = min(1.0, np.ceil((K + 1) * (1 - alpha / T)) / K)
    q = np.quantile(U, lvl, axis=0)                     # (T,) per-threshold
    lo = np.clip(center - q * s, 0.0, 1.0)
    hi = np.clip(center + q * s, 0.0, 1.0)
    return lo, hi


def plugin_quantile_band(cal_errors, center, alpha=0.1, tighten=True,
                         floor_frac=0.05):
    """Asymptotic 'plug-in' sup-quantile band.

    Identical sup-score and modulation to PCB, but uses the PLAIN (1-alpha) empirical
    quantile of the scores instead of the conformal order statistic
    ceil((1-alpha)(K+1))/(K+1). This is the band a practitioner builds without the
    finite-sample correction; it coincides with PCB as K -> infinity, so the coverage
    gap between them isolates exactly what the conformal correction buys. Returns
    (lo, hi) absolute, clipped to [0,1], matching PCB.
    """
    from .conformal_band import isotonic_tighten
    E = np.asarray(cal_errors, float)
    center = np.asarray(center, float)
    s = E.std(0)
    s = np.maximum(s, floor_frac * max(s.max(), 1e-12))
    R = np.max(np.abs(E) / s, axis=1)                # sup-scores (studentized)
    q = float(np.quantile(R, 1 - alpha))             # PLAIN quantile, no (K+1) correction
    lo, hi = center - q * s, center + q * s
    if tighten:
        lo, hi = isotonic_tighten(lo, hi)
    else:
        lo, hi = np.clip(lo, 0, 1), np.clip(hi, 0, 1)
    return lo, hi


def gaussian_sup_band(cal_errors, center, alpha=0.1, n_mc=20000, seed=0,
                      floor_frac=0.05):
    """Classical Scheffe-type simultaneous band around the plug-in curve.

    Models the standardized error field as mean-zero Gaussian with the empirical
    threshold-correlation, and uses the (1-alpha) quantile of max_t |Z(t)| as the
    critical value: band = center ± crit · s(t). Mean-zero by construction (a
    classical confidence band assumes the estimator is unbiased), which is exactly
    why it under-covers when transport induces a nonzero bias b_t.

    Returns (lo, hi) absolute, clipped to [0,1].
    """
    E = np.asarray(cal_errors, float)
    K, T = E.shape
    bias = E.mean(0)                             # estimated transport bias b̂_t
    s = E.std(0)
    s = np.maximum(s, floor_frac * max(s.max(), 1e-12))
    W = (E - bias) / s                           # standardized residual field
    R = np.corrcoef(W, rowvar=False)
    R = np.atleast_2d(R)
    # Symmetrize + jitter for a valid covariance, then Cholesky-sample.
    R = (R + R.T) / 2 + 1e-9 * np.eye(T)
    L = np.linalg.cholesky(R)
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((n_mc, T)) @ L.T
    crit = np.quantile(np.max(np.abs(Z), axis=1), 1 - alpha)
    # Bias-corrected predictor of the truth: θ ≈ (center − b̂) ± crit·s.
    # This is the STRONG Gaussian baseline (M1 done simultaneously); it still
    # under-covers where the standardized error field is non-Gaussian/heavy-tailed.
    mid = center - bias
    lo = np.clip(mid - crit * s, 0.0, 1.0)
    hi = np.clip(mid + crit * s, 0.0, 1.0)
    return lo, hi
