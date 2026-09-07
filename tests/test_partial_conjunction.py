"""Contracts for WVS persistent p-values and cross-item conjunctions."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pcb.experiments.e63_wvs_partial_conjunction import _country_results
from pcb.inference.decline_certify import (
    certify_decline_differences,
    decline_difference_pvalue,
)
from pcb.inference.prevalence import partial_conjunction_pvalue


CORE = np.array([False, True, True, True, False])


def test_decline_pvalue_inverts_persistent_band():
    rng = np.random.default_rng(20260907)
    pairs, thresholds, nboot = 4, 5, 2000
    diff_hat = np.full((pairs, thresholds), 0.035)
    noise = rng.normal(0, 0.02, size=(nboot, pairs, thresholds))
    diff_boot = diff_hat[None] + noise
    pvalue = decline_difference_pvalue(diff_hat, diff_boot, CORE)

    for alpha in (0.05, 0.10, 0.20):
        certified = certify_decline_differences(
            diff_hat, diff_boot, alpha, CORE
        )["design_aware"]
        if abs(pvalue - alpha) > 2 / nboot:
            assert (pvalue <= alpha) == certified


def test_nonpositive_cell_cannot_certify_persistent_decline():
    diff_hat = np.ones((2, 3))
    diff_hat[1, 1] = 0
    diff_boot = np.repeat(diff_hat[None], 100, axis=0)
    assert decline_difference_pvalue(diff_hat, diff_boot) == 1.0


def test_bonferroni_partial_conjunction_known_vector():
    pvalues = [0.01, 0.02, 0.40, 0.80, 0.90]
    assert partial_conjunction_pvalue(pvalues, k=2) == pytest.approx(0.08)
    assert partial_conjunction_pvalue(pvalues[:3], k=2) == pytest.approx(0.04)
    assert partial_conjunction_pvalue([0.01], k=2) == 1.0


def test_simes_partial_conjunction_known_vector():
    pvalues = [0.01, 0.02, 0.03, 0.80, 0.90]
    # Simes on the largest four p-values:
    # min(4*.02/1, 4*.03/2, 4*.80/3, 4*.90/4) = .06.
    assert partial_conjunction_pvalue(
        pvalues, k=2, method="simes"
    ) == pytest.approx(0.06)


def test_partial_conjunction_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        partial_conjunction_pvalue([0.1, np.nan])
    with pytest.raises(ValueError):
        partial_conjunction_pvalue([0.1, 1.1])
    with pytest.raises(ValueError):
        partial_conjunction_pvalue([0.1, 0.2], k=0)
    with pytest.raises(ValueError):
        partial_conjunction_pvalue([0.1, 0.2], method="unknown")


def test_country_results_preserve_descriptive_and_valid_cores():
    rows = pd.DataFrame([
        dict(iso=1, item="a", p_persistent=0.01, certifies_alpha10=True),
        dict(iso=1, item="b", p_persistent=0.02, certifies_alpha10=True),
        dict(iso=1, item="c", p_persistent=0.80, certifies_alpha10=False),
        dict(iso=2, item="a", p_persistent=0.04, certifies_alpha10=True),
        dict(iso=2, item="b", p_persistent=0.06, certifies_alpha10=True),
        dict(iso=2, item="c", p_persistent=0.90, certifies_alpha10=False),
    ])
    out = _country_results(rows).set_index("iso")
    assert bool(out.loc[1, "pc_bonferroni"])
    assert not bool(out.loc[2, "pc_bonferroni"])
    assert int(out.loc[1, "n_certified_alpha10"]) == 2
    assert int(out.loc[2, "n_certified_alpha10"]) == 2
