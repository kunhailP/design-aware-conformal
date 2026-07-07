"""M1 — Gaussian variance-inflation (random-effects) interval.

Adds a between-population variance term to the within-population SE:
    half-width = z · sqrt(SE_within² + σ̂_between²).
σ̂_between is the SD of leave-one-population-out plug-in errors. Partially
recovers coverage but assumes (near-)Gaussian, mean-zero transport error;
predicted to undercover under heavy-tailed / biased transport error
(RESEARCH_DESIGN §5, pre-registered H2).
"""
from __future__ import annotations
import numpy as np


def between_pop_sd(cal_errors: np.ndarray) -> np.ndarray:
    """σ̂_between per threshold from calibration errors E (G_cal × T)."""
    return np.asarray(cal_errors).std(0)


def variance_inflation_interval(
    theta_hat: np.ndarray,
    se_within: np.ndarray,
    cal_errors: np.ndarray,
    z: float = 1.645,
):
    """Symmetric inflated interval around θ̂. Returns (lo, hi) each (T,)."""
    sd = between_pop_sd(cal_errors)
    half = z * np.sqrt(np.asarray(se_within) ** 2 + sd ** 2)
    return theta_hat - half, theta_hat + half
