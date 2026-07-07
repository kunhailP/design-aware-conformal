"""M3 — Shift-weighted population conformal (efficiency under structured shift).

Not all source populations are equally informative about the target. Weight each
calibration population by similarity to the target, d(P_i, P_target), and take a
*weighted* empirical quantile of the transport errors (Tibshirani et al. 2019,
lifted to the population level). Goal: maintain coverage while shrinking width
when the shift is STRUCTURED; ~no gain under homogeneous shift (pre-registered
H4 — falsifiable on purpose). Reduces to M2 when weights are uniform.
"""
from __future__ import annotations
import numpy as np
from .population_conformal import _two_sided_quantile_levels
from .conformal_band import _modulation, isotonic_tighten


def population_distance(feats_i, feats_target, metric: str = "covariate_mean") -> float:
    """Distance d(P_i, P_target) between two populations' covariate distributions.

    feats_i, feats_target : (n_i, d), (n_t, d) covariate matrices.
    metric ∈ {"covariate_mean", "mmd"} (ablated in E2; §12 decision #3).
    """
    Xi, Xt = np.asarray(feats_i), np.asarray(feats_target)
    if metric == "covariate_mean":
        return float(np.linalg.norm(Xi.mean(0) - Xt.mean(0)))
    if metric == "mmd":  # linear-kernel MMD (cheap, sufficient for mean+cov shift)
        return float(np.linalg.norm(Xi.mean(0) - Xt.mean(0)) ** 2)
    raise ValueError(f"unknown metric {metric}")


def distance_to_weights(distances, tau: float | None = None) -> np.ndarray:
    """softmax(-d/τ); τ defaults to the median distance (scale-free)."""
    d = np.asarray(distances, dtype=float)
    if tau is None:
        med = np.median(d[d > 0]) if np.any(d > 0) else 1.0
        tau = med if med > 0 else 1.0
    z = -d / tau
    z -= z.max()
    w = np.exp(z)
    return w / w.sum()


def _weighted_quantile(values, weights, q):
    """Weighted empirical quantile of `values` at level q ∈ [0,1].

    Uses the type-7 ("linear") plotting-position convention generalised to
    weights, so that under UNIFORM weights it equals np.quantile exactly — this
    is what makes M3 reduce to M2 cleanly at any n (plotting position of order
    stat i is i/(n-1) when weights are equal).
    """
    v = np.asarray(values, dtype=float)
    order = np.argsort(v)
    v, ww = v[order], np.asarray(weights, dtype=float)[order]
    cw = np.cumsum(ww)
    denom = cw[-1] - ww[-1]
    if denom <= 0:  # degenerate (one effective point)
        return float(v[-1])
    pp = (cw - ww) / denom            # uniform → i/(n-1)
    return float(np.interp(q, pp, v))


def weighted_conformal_interval(cal_errors: np.ndarray, weights: np.ndarray,
                                alpha: float = 0.1):
    """Weighted empirical-quantile band. cal_errors (G,T), weights (G,).

    Returns (lo, hi) offsets (T,). With uniform weights ≈ M2 conformal.
    """
    E = np.asarray(cal_errors)
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    n, T = E.shape
    # Use the SAME finite-sample conformal levels as M2 so that uniform weights
    # reduce M3 to M2 exactly (coverage-preserving normalisation, cf. Tibshirani
    # 2019 finite-sample correction). This is the fix the E2 pre-reg flagged.
    lo_lvl, hi_lvl = _two_sided_quantile_levels(n, alpha)
    lo = np.array([_weighted_quantile(E[:, t], w, lo_lvl) for t in range(T)])
    hi = np.array([_weighted_quantile(E[:, t], w, hi_lvl) for t in range(T)])
    return lo, hi


def weighted_conformal_band(cal_errors, cal_feats, target_feat, center,
                            alpha=0.1, tau=None, tighten=True):
    """Covariate-shift PCB: a SIMULTANEOUS band valid under population shift.

    When the target population is structurally novel (e.g. a held-out world
    region), the calibration populations are no longer exchangeable with it and
    the unweighted PCB under-covers. Covariate-shift conformal (Tibshirani et al.
    2019, lifted to the population level) fixes this by reweighting calibration
    populations toward the target and using the finite-sample test-weight-
    corrected quantile of the sup-scores R_i = max_t |E_i(t)|/s(t).

    The price of broken exchangeability surfaces honestly as WIDTH and, when no
    covariate-similar population exists, ABSTENTION — the band returns [0,1]
    rather than a confident-but-wrong interval.

    cal_errors  : (K,T) source transport-error curves.
    cal_feats   : (K,d) population summaries; target_feat : (d,).
    center      : (T,) target plug-in F̂.   Returns (lo, hi) absolute in [0,1]^T.
    """
    E = np.asarray(cal_errors, float)
    Z = np.asarray(cal_feats, float)
    zt = np.asarray(target_feat, float)
    s = _modulation(E)
    R = np.max(np.abs(E) / s, axis=1)                       # (K,) sup-scores

    sd = np.maximum(Z.std(0), 1e-12)                        # scale-balance features
    d = np.sqrt(np.sum(((Z - zt) / sd) ** 2, axis=1))
    if tau is None:                                         # sharp default (median/4)
        pos = d[d > 0]
        tau = (np.median(pos) / 4.0) if pos.size else 1.0
    w = np.exp(-(d / max(tau, 1e-12)))
    w_test = 1.0                                            # target is most similar to itself

    order = np.argsort(R)
    cum = np.cumsum(w[order]) / (w.sum() + w_test)          # test point mass at +inf
    k = int(np.searchsorted(cum, 1 - alpha))
    center = np.asarray(center, float)
    if k >= len(R):                                         # insufficient mass -> abstain
        return np.zeros_like(center), np.ones_like(center)
    q = R[order][k]
    lo, hi = center - q * s, center + q * s
    if tighten:
        return isotonic_tighten(lo, hi)
    return np.clip(lo, 0, 1), np.clip(hi, 0, 1)
