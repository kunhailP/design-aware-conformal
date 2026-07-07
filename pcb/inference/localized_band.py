"""M3' — Localized (bias-corrected) Population Conformal Band.

PCB centers the band at the target plug-in F̂ and pays ~2× width for simultaneous
validity. When the shift is structured (transport error predictable from observable
population summaries), we can RECENTER: regress the calibration transport errors
E_i(·) on population features z_i, predict the target's bias b̂(·), and run the
conformal band on the RESIDUALS. Valid under population exchangeability (residual
scores are exchangeable when the regression is fit symmetrically; we use closed-form
leave-one-out residuals for the calibration set). Narrower than PCB exactly when the
bias is predictable — the lever E2 showed plain reweighting (M3) could not pull.

Reduces to PCB when features carry no information (b̂ ≈ 0).
"""
from __future__ import annotations
import numpy as np
from .conformal_band import conformal_band_quantile, isotonic_tighten


def _loo_fit(Z, E):
    """Per-threshold OLS of E (K,T) on Z (K,p). Returns (loo_residuals (K,T),
    beta (p,T)) using the closed-form leave-one-out residual e_i/(1-h_ii)."""
    ZtZ_inv = np.linalg.pinv(Z.T @ Z)
    H = Z @ ZtZ_inv @ Z.T                      # hat matrix (K,K)
    h = np.clip(np.diag(H), 0, 1 - 1e-8)       # leverages
    beta = ZtZ_inv @ Z.T @ E                   # (p,T)
    resid = E - Z @ beta                       # in-sample residuals (K,T)
    loo = resid / (1.0 - h)[:, None]           # leave-one-out residuals
    return loo, beta


def localized_conformal_band(cal_errors, cal_feats, target_feat, center,
                             alpha=0.1, tighten=True):
    """Bias-corrected simultaneous band.

    cal_errors  : (K,T) source transport-error curves E_i(·).
    cal_feats   : (K,d) population summaries (e.g. covariate means).
    target_feat : (d,) target population summary.
    center      : (T,) target plug-in F̂(·).
    Returns (lo, hi) absolute band in [0,1]^T, plus the fitted target bias b̂.
    """
    E = np.asarray(cal_errors, float)
    Zc = np.column_stack([np.ones(len(cal_feats)), np.asarray(cal_feats, float)])
    zt = np.concatenate([[1.0], np.asarray(target_feat, float)])
    loo, beta = _loo_fit(Zc, E)
    b_target = zt @ beta                                   # (T,) predicted bias
    # conformal band on LOO residuals (exchangeable scores)
    q, s = conformal_band_quantile(loo, alpha)
    center = np.asarray(center, float)
    if np.isinf(q):
        lo, hi = np.zeros_like(center), np.ones_like(center)
    else:
        c = center - b_target                              # recenter by predicted bias
        lo, hi = c - q * s, c + q * s
    if tighten:
        lo, hi = isotonic_tighten(lo, hi)
    else:
        lo, hi = np.clip(lo, 0, 1), np.clip(hi, 0, 1)
    return lo, hi, b_target
