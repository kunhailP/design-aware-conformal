"""Closed-testing shortcuts (Simes and Bonferroni local tests) vs exhaustive
closed testing, and the Bonferroni sensitivity of the shipped ESS bound.

Simes local tests need independent / PRDS p-values across countries -- a
design assumption stated in the manuscript; Bonferroni local tests need no
dependence assumption. Both shortcuts must agree with brute-force closure on
small families (full-family d and every post-hoc subset), and the shipped
ESS p-values must give the numbers the supplement reports under each.
"""
from __future__ import annotations

import os
from itertools import combinations

import numpy as np
import pandas as pd
import pytest

from pcb.inference.prevalence import (closed_testing_bruteforce,
                                      prevalence_lower_bound,
                                      true_discoveries,
                                      true_discoveries_subset)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.parametrize("local", ["simes", "bonferroni"])
def test_shortcuts_match_exhaustive_closed_testing(local):
    rng = np.random.default_rng(56)
    for rep in range(60):
        m = int(rng.integers(3, 9))
        # a mix of small (true-discovery-like) and uniform p-values
        p = np.where(rng.random(m) < 0.4, rng.random(m) * 0.05, rng.random(m))
        alpha = float(rng.choice([0.05, 0.10, 0.20]))
        full = list(range(m))
        assert true_discoveries(p, alpha, local) == \
            closed_testing_bruteforce(full, p, alpha, local)
        for k in range(1, m + 1):
            for S in combinations(full, k):
                assert true_discoveries_subset(p[list(S)], p, alpha, local) == \
                    closed_testing_bruteforce(S, p, alpha, local), (local, p, S)


def test_bonferroni_is_never_less_conservative_than_simes():
    rng = np.random.default_rng(7)
    for _ in range(200):
        p = rng.random(12) ** 3
        assert true_discoveries(p, 0.1, "bonferroni") <= \
            true_discoveries(p, 0.1, "simes")


def test_ess_prevalence_bonferroni_sensitivity():
    """Supplement S4 / Sec. 7: the assumption-free Bonferroni local test gives
    the same d = 6 on both outcomes and names the same six countries."""
    path = os.path.join(ROOT, "results", "ess_prevalence.csv")
    if not os.path.exists(path):
        pytest.skip("ess_prevalence.csv not present")
    d = pd.read_csv(path)
    for oc in ("trstprl", "stfdem"):
        g = d[d.outcome == oc]
        simes = prevalence_lower_bound(dict(zip(g.cntry, g.p_net)), 0.10, "simes")
        bonf = prevalence_lower_bound(dict(zip(g.cntry, g.p_net)), 0.10,
                                      "bonferroni")
        assert simes["d"] == 6 and bonf["d"] == 6, (oc, simes["d"], bonf["d"])
        assert set(simes["countries_named"]) == set(bonf["countries_named"]), oc
