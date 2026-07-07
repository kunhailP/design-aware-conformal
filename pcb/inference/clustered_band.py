"""Country-clustered PCB — one conformal score per COUNTRY TRAJECTORY.

Country-blocked prediction and country-level calibration are different
things. Excluding the target country's rounds from the calibration set stops
predictor leakage, but if the conformal quantile is computed over
country-round scores, the calibration units are still country-rounds — and
rounds of the same country are serially dependent, so they are not
exchangeable draws. The honest exchangeable unit in a repeated cross-national
survey is the country trajectory.

Construction (target country c*): with s(t) a modulation computed from the
calibration errors only (all rounds of c* excluded),

    R_c = max_{r in rounds(c)} max_t |E_{c,r}(t)| / s(t),   c != c*,

q = ceil((1-alpha)(K+1))-th order statistic of the K country scores, and the
band for EVERY round r of the target is theta_hat_{c*,r} +/- q * s(t). The
covered event is {R_{c*} <= q}: ALL rounds and ALL thresholds of the held-out
country simultaneously. Validity needs exchangeability of whole trajectories
(the trajectory, including its round count, is the draw from Pi); round-count
heterogeneity is a caveat audited empirically in e8.
"""
from __future__ import annotations
import numpy as np

from .conformal_band import _modulation, isotonic_tighten


def country_scores(E_cal: np.ndarray, countries_cal: np.ndarray,
                   s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """One sup-score per calibration country. Returns (labels, scores)."""
    per_row = np.max(np.abs(E_cal) / s[None, :], axis=1)
    labels = np.unique(countries_cal)
    return labels, np.array([per_row[countries_cal == c].max() for c in labels])


def clustered_quantile(scores: np.ndarray, alpha: float = 0.1) -> float:
    K = scores.shape[0]
    idx = int(np.ceil((1 - alpha) * (K + 1)))
    return np.inf if idx > K else float(np.sort(scores)[idx - 1])


def clustered_band(E_cal: np.ndarray, countries_cal: np.ndarray,
                   centers: np.ndarray, alpha: float = 0.1,
                   tighten: bool = True):
    """Bands for every round of the held-out country.

    E_cal    : (N, T) calibration error curves (country-rounds, target country
               fully excluded — also from the modulation).
    countries_cal : (N,) country label per calibration row.
    centers  : (R, T) predicted curves for the target country's R rounds.
    Returns (lo, hi) each (R, T).
    """
    E_cal = np.asarray(E_cal, float)
    s = _modulation(E_cal)
    _, scores = country_scores(E_cal, np.asarray(countries_cal), s)
    q = clustered_quantile(scores, alpha)
    centers = np.atleast_2d(np.asarray(centers, float))
    if np.isinf(q):
        lo = np.zeros_like(centers)
        hi = np.ones_like(centers)
    else:
        lo, hi = centers - q * s[None, :], centers + q * s[None, :]
    out_lo, out_hi = np.empty_like(lo), np.empty_like(hi)
    for r in range(centers.shape[0]):
        if tighten:
            out_lo[r], out_hi[r] = isotonic_tighten(lo[r], hi[r])
        else:
            out_lo[r], out_hi[r] = np.clip(lo[r], 0, 1), np.clip(hi[r], 0, 1)
    return out_lo, out_hi
