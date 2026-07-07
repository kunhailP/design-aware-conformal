"""M0 — Standard within-population bootstrap interval.

Captures only ε^within (household sampling error). Expected to *collapse* under
population shift (RESEARCH_DESIGN §4, Proposition 1; pre-registered H1). This is
the baseline whose failure motivates the paper, not a method we endorse.
"""
from __future__ import annotations
import numpy as np
from .headcount import weighted_headcount


def within_pop_bootstrap_se(
    y_pred: np.ndarray,
    w: np.ndarray,
    thresholds: np.ndarray,
    B: int = 1000,
    seed: int = 0,
) -> np.ndarray:
    """Per-threshold bootstrap SE of the plug-in headcount, resampling households.

    Returns (T,) standard errors. Uses weighted resampling identical to
    scripts/pipeline/03_coverage_naive.py so M0 here reproduces the legacy result.
    """
    rng = np.random.default_rng(seed)
    n = len(y_pred)
    idx = rng.integers(0, n, size=(B, n))
    wb = np.asarray(w)[idx].astype(float)
    wb = wb / wb.sum(1, keepdims=True)
    pcb = np.asarray(y_pred)[idx]  # (B, n)
    boot = np.einsum(
        "bn,bnt->bt", wb, (pcb[:, :, None] < thresholds[None, None, :]).astype(np.float32)
    )
    return boot.std(0)


def standard_interval(theta_hat: np.ndarray, se_within: np.ndarray, z: float = 1.645):
    """[θ̂ ± z·SE_within] — the naive (M0) interval. z=1.645 ≈ 90% nominal."""
    return theta_hat - z * se_within, theta_hat + z * se_within
