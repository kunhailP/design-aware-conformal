"""Out-of-sample prediction protocols (leakage control = RESEARCH_DESIGN §9 / C3).

All transport-error calibration uses OOS predictions only:
  * leave_one_population_out  — 24 pseudo-populations (survey×strata), for E1-A.
  * leave_one_survey_out      — honest cross-survey shift, for E1-B.
Lifted from scripts/pipeline/02 and 04.
"""
from __future__ import annotations
import numpy as np
from .train_lgbm import fit_base_model, predict_consumption


def leave_one_population_out(df, feat, popcol, seed=0):
    """Return OOS predicted consumption for every household (LOPO over popcol)."""
    pred = np.full(len(df), np.nan)
    for g in sorted(df[popcol].unique()):
        te = df[df[popcol] == g]
        m = fit_base_model(df[df[popcol] != g], feat, seed=seed)
        pred[te.index] = predict_consumption(m, te[feat])
    return pred


def leave_one_survey_out(df, feat, surveycol="survey_id", seed=0):
    """Honest variant: hold out an entire survey at a time (model never sees it)."""
    return leave_one_population_out(df, feat, surveycol, seed=seed)
