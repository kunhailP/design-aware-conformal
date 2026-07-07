"""Poverty headcount functional θ_t(P) = P_P(Y < t).

The estimand of the whole project (RESEARCH_DESIGN §2.2): a *non-smooth
distributional functional* — the survey-weighted CDF evaluated on a threshold
grid. Everything downstream (intervals, coverage, decision loss) is computed on
the output of `headcount_curve`.
"""
from __future__ import annotations
import numpy as np


def weighted_headcount(y: np.ndarray, w: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    """θ_t = Σ_j w̃_j · 1{y_j < t} for each threshold t.

    Parameters
    ----------
    y : (n,) outcome (consumption). May be observed Y or predicted Ŷ.
    w : (n,) survey weights (unnormalised; normalised internally).
    thresholds : (T,) poverty thresholds t.

    Returns
    -------
    (T,) headcount curve.
    """
    w = np.asarray(w, dtype=float)
    w = w / w.sum()
    y = np.asarray(y, dtype=float)
    return (w[:, None] * (y[:, None] < thresholds[None, :])).sum(0)


def headcount_curve(y, w, thresholds) -> np.ndarray:
    """Alias kept for readability at call sites; see `weighted_headcount`."""
    return weighted_headcount(y, w, thresholds)
