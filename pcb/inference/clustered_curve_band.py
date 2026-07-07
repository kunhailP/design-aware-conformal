"""Clustered curve PCB — estimand A: ONE country-round curve, honestly
calibrated at the country level.

Claim protected:  Pr[ θ_{c*,r*}(t) ∈ B(t)  ∀t ] ≥ 1 − α
for a SINGLE target round r* of a held-out country c*.

Construction: each calibration country contributes exactly ONE error curve
(selection rule fixed a priori — default: its most recent available round, the
round that matches the nowcasting task). With one curve per country the
scores are exchangeable across countries, and the band is numerically
IDENTICAL to the original PCB run on the selected (K, T) error matrix
(tests/test_single_round_reduces_to_pcb.py asserts this reduction). What this
module adds over calling PCB directly is the selection discipline: it is
impossible to feed two rounds of the same country into the calibration set.

This is the honest replacement for the gate-2 `round_cal` construction, whose
quantile pooled all rounds of every calibration country (dependent scores,
nominal K inflated from ~34 to ~243; see docs/ESS_CLUSTER_VALIDITY.md).
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from .conformal_band import population_conformal_band


def select_one_round_per_country(E: np.ndarray, countries: np.ndarray,
                                 rounds: np.ndarray, rule: str = "latest"):
    """Pick one error curve per country. Returns (E_sel, labels, sel_rounds)."""
    df = pd.DataFrame({"c": countries, "r": rounds, "i": np.arange(len(countries))})
    if rule == "latest":
        pick = df.sort_values("r").groupby("c", observed=True).tail(1)
    elif rule == "earliest":
        pick = df.sort_values("r").groupby("c", observed=True).head(1)
    else:
        raise ValueError(f"unknown selection rule {rule}")
    pick = pick.sort_values("c")
    idx = pick.i.to_numpy()
    return E[idx], pick.c.to_numpy(), pick.r.to_numpy()


def clustered_curve_band(E_cal: np.ndarray, countries_cal: np.ndarray,
                         rounds_cal: np.ndarray, center: np.ndarray,
                         alpha: float = 0.1, rule: str = "latest",
                         tighten: bool = True):
    """Band for one target round; calibration = one curve per country.

    E_cal must already exclude every round of the target country.
    """
    E_sel, _, _ = select_one_round_per_country(E_cal, countries_cal,
                                               rounds_cal, rule)
    return population_conformal_band(E_sel, center, alpha, tighten)
