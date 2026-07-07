"""M2 — Population-level split-conformal interval (the main method).

Exchangeable unit = POPULATION, not household (RESEARCH_DESIGN §2.4). The
calibration set is the leave-one-population-out plug-in errors
    E_i(t) = θ̂_t(P_i) − θ_t(P_i),    i over source populations,
and the interval for an unseen target is θ̂_target ± (empirical conformal
quantiles of E). Distribution-free: captures bias and heavy tails of the
transport error that the Gaussian inflation (M1) misses.

Two variants:
  * `population_conformal_interval` — per-threshold (marginal) coverage.
  * `simultaneous_conformal_interval` — joint over all T thresholds via a
    max-type nonconformity score (RESEARCH_DESIGN §12 open decision #2).

Honest caveat (pre-registered H3): with few source populations the empirical
quantile undercovers (Dunn et al. 2022 small-k phenomenon).
"""
from __future__ import annotations
import numpy as np
from .headcount import weighted_headcount


def leave_one_population_out_errors(pred, cons, w, popid, thresholds):
    """Return (G, T) plug-in errors θ̂−θ for each population.

    pred : predicted consumption (Ŷ); cons : true consumption (Y);
    w : weights; popid : population id per household; thresholds : (T,).
    """
    G = np.array(sorted(np.unique(popid)))
    E = np.zeros((len(G), len(thresholds)))
    for i, g in enumerate(G):
        m = popid == g
        E[i] = weighted_headcount(pred[m], w[m], thresholds) - weighted_headcount(
            cons[m], w[m], thresholds
        )
    return G, E


def _two_sided_quantile_levels(n: int, alpha: float):
    """Finite-sample conformal quantile levels (lower, upper) for n calib points."""
    lo = max(0.0, np.floor((n + 1) * (alpha / 2)) / n)
    hi = min(1.0, np.ceil((n + 1) * (1 - alpha / 2)) / n)
    return lo, hi


def population_conformal_interval(cal_errors: np.ndarray, alpha: float = 0.1):
    """Per-threshold signed two-sided conformal band (offsets, not absolute).

    Returns (lo, hi) each (T,): the lower/upper empirical quantiles of the
    calibration errors E_i = θ̂_i − θ_i. Since θ = θ̂ − E, the band for the
    TARGET truth is [θ̂ − hi, θ̂ − lo] (note the sign flip and swap; this matters
    only when E is asymmetric, i.e. under transport bias). Equivalently, coverage
    can be checked in error space as E_target ∈ [lo, hi].
    """
    E = np.asarray(cal_errors)
    n = E.shape[0]
    lo_lvl, hi_lvl = _two_sided_quantile_levels(n, alpha)
    lo = np.quantile(E, lo_lvl, axis=0)
    hi = np.quantile(E, hi_lvl, axis=0)
    return lo, hi


def simultaneous_conformal_interval(cal_errors: np.ndarray, alpha: float = 0.1):
    """Joint band covering the whole curve with prob ≥ 1−α.

    Nonconformity = max_t |E_i(t)| / s(t) (studentised by per-threshold scale).
    Returns (lo, hi) each (T,) offsets. See RESEARCH_DESIGN §12.
    """
    E = np.asarray(cal_errors)
    n = E.shape[0]
    s = np.maximum(E.std(0), 1e-8)
    scores = np.max(np.abs(E) / s[None, :], axis=1)  # (G,)
    lvl = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
    q = np.quantile(scores, lvl)
    half = q * s
    return -half, half
