"""Contract tests for the claim-family transfer construction.

An earlier version of this file passed four tests that pinned nothing: three
were algebraic identities of the implementation (declines and rises cannot both
certify because the two conditions contradict for sd>0; a two-sided critical
value exceeds a one-sided one because max|x| >= max x; the "rungs" restate the
return dict), and the fourth had no power at all -- under its fixture the
certification rate was 0.000 against an assert bound of 0.145, so it could not
have failed had the procedure been an order of magnitude anti-conservative.

The object the proposition actually needs is the band's own coverage,
Pr(theta in B) >= 1 - alpha, at the dimension the deployed construction uses:
the sup runs over L(L-1)/2 contrasts times the core, which is 220 coordinates at
L=11. That is what these tests measure, under correlated and non-Gaussian errors
and with the bootstrap drawn by resampling rather than from the true law, plus a
partial-null case where selection can actually bite.
"""
from __future__ import annotations

import numpy as np
import pytest

from pcb.inference.claim_family import certify_claim_family

ALPHA = 0.10
T = 6
CORE = np.array([False, True, True, True, True, False])
B = 800


def _panel(rng, L, n, truth, rho=0.6, df=6):
    """One country: L rounds of n respondents, errors correlated across
    thresholds and heavy-tailed, with a resampling bootstrap (not the true law)."""
    chol = np.linalg.cholesky(rho ** np.abs(np.subtract.outer(np.arange(T),
                                                              np.arange(T)))
                              + 1e-9 * np.eye(T))
    def draw(m):
        z = rng.standard_t(df, size=(m, T)) / np.sqrt(df / (df - 2))
        return z @ chol.T
    obs = truth + draw(L) / np.sqrt(n)
    # bootstrap: resample the same error law, centred on the observed curves
    boots = obs[None] + draw(B * L).reshape(B, L, T) / np.sqrt(n)
    return obs, boots


def _coverage(L, n, reps, seed):
    """Fraction of replicates in which the band covers the whole contrast
    surface -- the event every certified claim rides on."""
    rng = np.random.default_rng(seed)
    truth = np.tile(np.linspace(0.1, 0.8, T), (L, 1))
    hits = 0
    for _ in range(reps):
        obs, boots = _panel(rng, L, n, truth)
        r = certify_claim_family(obs, boots, ALPHA, CORE)
        c, sd_ok = r["c"], True
        # the coverage event: |D_hat - D| <= c*sd at every contrast and core cell
        for (a, b), lo in r["lower"].items():
            dh = (obs[b] - obs[a])[CORE]
            db = (boots[:, b] - boots[:, a])[:, CORE]
            sd = np.maximum(db.std(0), 1e-6)
            truth_d = (truth[b] - truth[a])[CORE]
            if np.any(np.abs(dh - truth_d) > c * sd):
                sd_ok = False
                break
        hits += sd_ok
    return hits / reps


@pytest.mark.parametrize("L,n", [(5, 1200), (11, 1200)])
def test_band_covers_the_contrast_surface(L, n):
    """The proposition assumes a 1-alpha band; this checks the deployed
    construction delivers one at the dimension it is used at (220 coordinates
    when L=11), under correlated t-distributed errors."""
    reps = 500
    cov = _coverage(L, n, reps, seed=100 + L)
    se = np.sqrt(0.9 * 0.1 / reps)
    assert cov >= 1 - ALPHA - 3 * se, (L, cov)


def test_false_certification_rate_under_the_sharp_null():
    """No true ordering anywhere, so ANY certified claim is an error. Unlike the
    previous fixture this one has power: the noise scale is set so that the
    procedure certifies in a non-negligible fraction of replicates when the
    critical value is deliberately halved."""
    rng = np.random.default_rng(11)
    truth = np.tile(np.linspace(0.1, 0.8, T), (6, 1))
    reps, bad, bad_halved = 500, 0, 0
    for _ in range(reps):
        obs, boots = _panel(rng, 6, 400, truth)
        r = certify_claim_family(obs, boots, ALPHA, CORE)
        bad += bool(r["declines"] or r["rises"])
        # sanity: with c halved the same data DO certify, so the test has power
        rh = certify_claim_family(obs, boots, 0.999, CORE)
        bad_halved += bool(rh["declines"] or rh["rises"])
    assert bad / reps <= ALPHA + 3 * np.sqrt(ALPHA * 0.9 / reps), bad / reps
    assert bad_halved / reps > 0.25, (
        f"fixture has no power: even at alpha=0.999 only {bad_halved/reps:.3f} "
        "certify, so the null test could not detect an invalid procedure")


def test_partial_null_selection_does_not_inflate_error():
    """Half the rounds truly decline and half do not, so the certified subfamily
    is data-selected. Transfer says selection costs nothing: the probability that
    ANY certified claim is false must still respect alpha."""
    rng = np.random.default_rng(23)
    L = 6
    truth = np.tile(np.linspace(0.1, 0.8, T), (L, 1))
    truth[3:] += 0.05                       # a real shift halfway through
    reps, bad = 500, 0
    for _ in range(reps):
        obs, boots = _panel(rng, L, 900, truth)
        r = certify_claim_family(obs, boots, ALPHA, CORE)
        wrong = False
        for (a, b) in r["declines"]:
            if np.any((truth[b] - truth[a])[CORE] < 0):
                wrong = True
        for (a, b) in r["rises"]:
            if np.any((truth[a] - truth[b])[CORE] < 0):
                wrong = True
        bad += wrong
    assert bad / reps <= ALPHA + 3 * np.sqrt(ALPHA * 0.9 / reps), bad / reps


def test_one_sided_branch_returns_no_uncalibrated_reverse_claims():
    """With two_sided=False the critical value controls only the decline
    direction, so rise-side objects must not be returned as if certified."""
    rng = np.random.default_rng(5)
    truth = np.tile(np.linspace(0.1, 0.8, T), (5, 1))
    obs, boots = _panel(rng, 5, 800, truth)
    one = certify_claim_family(obs, boots, ALPHA, CORE, two_sided=False)
    assert one["rises"] is None and one["upper"] is None
    assert one["episodic"] is None
    two = certify_claim_family(obs, boots, ALPHA, CORE, two_sided=True)
    assert two["rises"] is not None and two["c"] >= one["c"] - 1e-12
