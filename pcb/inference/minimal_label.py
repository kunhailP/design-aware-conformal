"""M5 — Minimal-label / audit-design conformal update.

Policy reality (RESEARCH_DESIGN §6 E5, RQ3): a full survey of the target
population is expensive, but a small audit sample of k labelled households is
feasible. Use those k labels to (a) directly estimate part of the target
headcount and (b) recalibrate the conformal offsets, mixing population-level and
target-direct information. Sweep k ∈ {0, 25, 50, 100, 250} (pre-registered H7).

Connects to the Legal-IR "minimal labels" theme in the broader portfolio.
STATUS: stub — implement after M2 is validated.
"""
from __future__ import annotations
import numpy as np


def minimal_label_update(
    base_offsets: tuple[np.ndarray, np.ndarray],
    target_labels: np.ndarray,
    target_pred: np.ndarray,
    target_w: np.ndarray,
    thresholds: np.ndarray,
    alpha: float = 0.1,
):
    """Tighten/recenter the conformal band using k observed target labels.

    base_offsets : (lo, hi) from M2/M3. target_labels : (k,) observed Y on the
    audit sample. target_pred : (k,) Ŷ on the same households (for residuals).
    Returns updated (lo, hi). With k=0 must return base_offsets unchanged.
    """
    raise NotImplementedError("M5: minimal_label_update — Phase 3 (E5).")


def select_audit_sample(target_feats: np.ndarray, k: int, strategy: str = "random"):
    """Choose which k target households to label (active calibration).

    strategy ∈ {"random", "uncertainty", "coverage_spread"}. Returns indices.
    """
    raise NotImplementedError("M5: select_audit_sample — Phase 3 (E5).")
