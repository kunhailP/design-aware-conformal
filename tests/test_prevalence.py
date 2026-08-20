"""Contract tests for cross-country prevalence inference.

Three things are pinned. (1) The alpha-inversion agrees with the deployed
certification: a span's p-value is at most alpha exactly when
`certify_claim_family` certifies it at alpha (up to the finite-B quantile
convention). (2) The Goeman-Solari/Simes shortcut returns the textbook answers
on known p-vectors. (3) End to end, the 90% lower bound on true discoveries
exceeds the number of truly declining countries in at most ~10% of
replications, under the same correlated heavy-tailed panel generator the
claim-family tests use, with the bootstrap drawn by resampling rather than
from the true law -- and it has power when declines are real.
"""
from __future__ import annotations

import numpy as np

from pcb.inference.claim_family import certify_claim_family
from pcb.inference.prevalence import (claim_family_pvalues,
                                      prevalence_lower_bound,
                                      true_discoveries)

ALPHA = 0.10
T = 6
CORE = np.array([False, True, True, True, True, False])


def _panel(rng, L, n, truth, nboot=400, rho=0.6, df=6):
    chol = np.linalg.cholesky(rho ** np.abs(np.subtract.outer(np.arange(T),
                                                              np.arange(T)))
                              + 1e-9 * np.eye(T))
    def draw(m):
        z = rng.standard_t(df, size=(m, T)) / np.sqrt(df / (df - 2))
        return z @ chol.T
    obs = truth + draw(L) / np.sqrt(n)
    boots = obs[None] + draw(nboot * L).reshape(nboot, L, T) / np.sqrt(n)
    return obs, boots


def test_simes_shortcut_known_vectors():
    # every p tiny: no subset survives, all m are true discoveries
    assert true_discoveries([1e-4] * 10, 0.10) == 10
    # every p large: the full set survives, nothing is claimed
    assert true_discoveries([0.9] * 10, 0.10) == 0
    # mixed: {0.2, 0.9} survives Simes at alpha=.1, {0.001, ...} does not
    assert true_discoveries([0.001, 0.2, 0.9], 0.10) == 1
    # boundary: p exactly at the Simes line does NOT exceed it (strict >)
    assert true_discoveries([0.05, 0.10], 0.10) == 2
    assert true_discoveries([], 0.10) == 0 or true_discoveries([0.5], 0.1) == 0


def test_pvalue_inverts_certification():
    """p <= alpha iff the span certifies, at several alphas, modulo the
    finite-B quantile convention (discrepancies only within 2/B of alpha)."""
    rng = np.random.default_rng(7)
    L, n, nboot = 5, 600, 800
    truth = np.tile(np.linspace(0.1, 0.8, T), (L, 1))
    truth = truth + 0.02 * np.arange(L)[:, None]   # a real decline (CDF rises)
    obs, boots = _panel(rng, L, n, truth, nboot=nboot)
    pv = claim_family_pvalues(obs, boots, CORE)["p_decline"]
    for alpha in (0.05, 0.10, 0.20):
        res = certify_claim_family(obs, boots, alpha, CORE)
        for s, p in pv.items():
            if abs(p - alpha) > 2.0 / nboot:
                assert (p <= alpha) == (s in res["declines"]), (s, p, alpha)


def test_any_adjacent_pvalue_is_min_over_adjacent():
    rng = np.random.default_rng(3)
    truth = np.tile(np.linspace(0.1, 0.8, T), (4, 1))
    obs, boots = _panel(rng, 4, 500, truth)
    out = claim_family_pvalues(obs, boots, CORE)
    adj = [out["p_decline"][(i, i + 1)] for i in range(3)]
    assert out["p_any_adjacent"] == min(adj)
    assert out["p_net"] == out["p_decline"][(0, 3)]


def test_prevalence_bound_validity_and_power():
    """d exceeds the true count in at most ~alpha of replications, and finds
    most of the planted declines when they are crisis-scale."""
    rng = np.random.default_rng(19)
    m, m1, L, n = 10, 4, 4, 1600
    reps, viol, found = 200, 0, 0
    base = np.tile(np.linspace(0.1, 0.8, T), (L, 1))
    for _ in range(reps):
        pvals = {}
        for c in range(m):
            truth = base.copy()
            if c < m1:            # crisis-scale decline: the CDF RISES across
                truth = truth + 0.08 * np.arange(L)[:, None]   # waves (mass moves down-scale)
            obs, boots = _panel(rng, L, n, np.clip(truth, 0, 1), nboot=300)
            pvals[c] = claim_family_pvalues(obs, boots, CORE)["p_net"]
        out = prevalence_lower_bound(pvals, ALPHA)
        viol += out["d"] > m1
        found += out["d"]
    mc = 3 * np.sqrt(ALPHA * (1 - ALPHA) / reps)
    assert viol / reps <= ALPHA + mc, f"anti-conservative: {viol/reps:.3f}"
    assert found / reps >= 0.5 * m1, f"no power: mean d = {found/reps:.2f}"


def test_subset_bound_respects_closure():
    """The named-set logic must use the closure-correct subset bound, not the
    subset run as its own family. Hand-checked example: full p = (.04,.06,.5)
    at alpha=.1 gives d(all)=1 (h=2: {.06,.5} survives its own Simes); the
    naive subset bound on {.04,.06} would claim 2, but H_{.06} is not
    closed-rejected (its superset {.06,.5} survives), so the correct subset
    bound is 1."""
    from pcb.inference.prevalence import (true_discoveries,
                                          true_discoveries_subset)
    full = [0.04, 0.06, 0.5]
    assert true_discoveries(full, 0.10) == 1
    naive = true_discoveries([0.04, 0.06], 0.10)
    assert naive == 2                              # what the naive read gives
    assert true_discoveries_subset([0.04, 0.06], full, 0.10) == 1
    # consistency: subset bound on the full set equals the global bound
    assert true_discoveries_subset(full, full, 0.10) == 1
    # and when everything is tiny, the named prefix re-certifies at full size
    from pcb.inference.prevalence import prevalence_lower_bound
    out = prevalence_lower_bound({c: 0.001 for c in "abcdefgh"}, 0.10)
    assert out["d"] == 8 and len(out["countries_named"]) == 8
    assert out["named_covers_d"]


def test_named_set_recertifies_under_planted_truth():
    """End to end: the returned named set always satisfies d(S)=|S| under the
    closure-correct subset bound, on draws with planted declines."""
    from pcb.inference.prevalence import (prevalence_lower_bound,
                                          true_discoveries_subset)
    rng = np.random.default_rng(29)
    base = np.tile(np.linspace(0.1, 0.8, T), (4, 1))
    for _ in range(30):
        pvals = {}
        for c in range(8):
            truth = base + (0.08 if c < 3 else 0.0) * np.arange(4)[:, None]
            obs, boots = _panel(rng, 4, 1600, np.clip(truth, 0, 1), nboot=300)
            pvals[c] = claim_family_pvalues(obs, boots, CORE)["p_net"]
        out = prevalence_lower_bound(pvals, ALPHA)
        named_p = sorted(pvals.values())[:len(out["countries_named"])]
        if named_p:
            assert true_discoveries_subset(
                named_p, list(pvals.values()), ALPHA) == len(named_p)
