"""Parametric and macro plug-in predictors for transported distribution curves.

These map population-level summaries to a headcount / CDF curve over a threshold
grid --- the plug-in F-hat whose *transport error* the conformal machinery
calibrates. They are collected here (rather than in any one experiment driver)
because they are shared across the cross-country and breadth experiments.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LinearRegression


def lognormal_curve(mean, gini, thr):
    """Lognormal-implied headcount curve ``P(Y < t)`` from a population's mean and
    Gini --- the structural plug-in used for the World Bank PIP poverty curves.

    Parameters are arrays over populations; ``thr`` is the threshold grid. Returns
    an ``(n_populations, n_thresholds)`` array of cumulative shares.
    """
    g = np.clip(gini, 1e-3, 0.99)
    sigma = np.sqrt(2.0) * norm.ppf((g + 1) / 2)
    mu = np.log(np.maximum(mean, 1e-6)) - sigma ** 2 / 2
    return norm.cdf((np.log(thr)[None, :] - mu[:, None]) / sigma[:, None])


def loco_curve_predict(df, curve_cols, thr):
    """Leave-one-country-out macro prediction of a monotone curve.

    For each country, a per-threshold linear regression on ``[log GDP, year,
    region dummies]`` is fit on all *other* countries and used to predict the held
    out country's curve, which is then isotonic-projected back to a monotone
    ``[0, 1]`` CDF. This is the genuine survey-less transport predictor used for the
    cross-country poverty and the educational-attainment breadth experiments.

    ``df`` must contain ``country_code``, ``region_code``, ``reporting_gdp``,
    ``year`` and the ``curve_cols``. Returns an ``(n_rows, n_thresholds)`` array.
    """
    country = df["country_code"].values
    reg = pd.get_dummies(df["region_code"], prefix="r").to_numpy(dtype=float)
    Z = np.column_stack([
        np.log(df["reporting_gdp"].clip(lower=1)).to_numpy(),
        df["year"].to_numpy(dtype=float),
        reg,
    ])
    F_true = df[curve_cols].to_numpy(dtype=float)
    F_hat = np.zeros_like(F_true)
    iso = IsotonicRegression(y_min=0.0, y_max=1.0, increasing=True)
    for c in np.unique(country):
        tr, te = country != c, country == c
        for j in range(len(thr)):
            F_hat[te, j] = LinearRegression().fit(Z[tr], F_true[tr, j]).predict(Z[te])
        for i in np.where(te)[0]:
            F_hat[i] = iso.fit_transform(thr, np.clip(F_hat[i], 0, 1))
    return F_hat
