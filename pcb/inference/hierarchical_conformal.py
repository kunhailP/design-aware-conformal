"""M4 — Hierarchical / partial-pooling conformal (small-K regime).

Problem (RESEARCH_DESIGN §5, RQ3): with only 2–3 source surveys the population
calibration set is tiny → undercoverage (Dunn et al. 2022). The survey→strata→
household hierarchy gives more *effective* calibration units that are not fully
independent. Partial-pool strata-level transport errors within survey to
stabilise the between-population quantile, traded against bias.

Framed in the paper as a *finite-population efficiency improvement*, NOT an exact
finite-sample guarantee. STATUS: stub — implement & stress-test on E2.
"""
from __future__ import annotations
import numpy as np


def hierarchical_conformal_interval(
    cal_errors_by_level: dict, alpha: float = 0.1, pool_strength: float | None = None
):
    """Partial-pooling band combining survey-level and strata-level errors.

    cal_errors_by_level : {"survey": (K, T), "strata": (S, T), "strata_survey": (S,)}
        strata_survey maps each strata row to its survey index (for pooling).
    pool_strength : λ in the shrinkage between strata-level spread and survey-level
        spread; None ⇒ choose by leave-one-survey-out on the calibration set.
    Returns (lo, hi) offsets (T,).
    """
    raise NotImplementedError("M4: hierarchical_conformal_interval — Phase 0 (E2).")
