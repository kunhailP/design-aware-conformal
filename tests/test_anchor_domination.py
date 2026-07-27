"""Contract test for the anchor-domination lemma (supplement, Lemma S-dominate).

Claim: under the scale family (A1), each contaminated calibration score
R_c = max_t sqrt(s_R^2 + v_c^2)|W_c(t)| dominates the latent-target score
max_t s_R(t)|W_c(t)| pointwise, so the unstudentized anchor band calibrated on
contaminated scores is valid for the LATENT target, not only for the
survey-estimate target. This is what lets the K >= 94 clause of Theorem 5' be
stated for the latent target under (A1)-(A3).

Two checks:
  1. the pathwise domination itself (an identity of the construction), and
  2. simultaneous latent-target coverage at or above nominal, on a scale-family
     DGP, at the K where the clause applies.
"""
from __future__ import annotations

import numpy as np

from pcb.inference.design_aware import _finite_quantile

ALPHA = 0.10
T = 8


def _draw(rng, K, s_R, v):
    """(A1): a common shape process W, scaled by sqrt(s_R^2+v^2) when observed
    through a survey and by s_R for the latent curve."""
    W = rng.standard_normal((K + 1, T))
    obs = np.sqrt(s_R[None, :] ** 2 + v[None, :] ** 2) * W
    lat = s_R[None, :] * W
    return obs, lat


def test_pathwise_domination():
    rng = np.random.default_rng(11)
    s_R = 0.04 + 0.02 * np.linspace(0, 1, T)
    v = 0.01 + 0.03 * rng.random(T)
    obs, lat = _draw(rng, 200, s_R, v)
    # pointwise, hence on the sup: the observed score is never below the latent
    assert np.all(np.abs(obs) >= np.abs(lat) - 1e-12)
    assert np.all(np.max(np.abs(obs), 1) >= np.max(np.abs(lat), 1) - 1e-12)


def test_latent_coverage_of_the_anchor_band():
    """The anchor band calibrated on contaminated scores covers the LATENT
    target at or above nominal under (A1)."""
    rng = np.random.default_rng(2026)
    s_R = 0.04 + 0.02 * np.linspace(0, 1, T)
    v = 0.01 + 0.03 * rng.random(T)
    K, reps = 120, 4000
    hits = 0
    for _ in range(reps):
        obs, lat = _draw(rng, K, s_R, v)
        q = _finite_quantile(np.max(np.abs(obs[:K]), 1), ALPHA)   # anchor radius
        hits += int(np.max(np.abs(lat[K])) <= q)                  # latent target
    cov = hits / reps
    # valid (>= nominal, up to Monte-Carlo error) and conservative, as the
    # domination lemma predicts: contaminated scores are the wider ruler.
    assert cov >= 1 - ALPHA - 3 * np.sqrt(ALPHA * (1 - ALPHA) / reps), cov
    assert cov >= 0.95, ("domination should make the latent-target band "
                         f"conservative, not merely valid; got {cov}")
