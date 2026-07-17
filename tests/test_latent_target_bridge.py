"""Theorem 2(b) — the T1→T2 (observed→latent) bridge, and its counterexample.

Two machine checks:

1. COUNTEREXAMPLE (Remark on the latent-target bridge): symmetric design noise
   alone does NOT make the observed-score conformal band conservative for the
   latent target. With a bimodal latent score law (masses 0.85/0.15 at 0/10)
   and ±1 symmetric noise, Q_0.9 of the noisy score is ≈9 < 10 = Q_0.9 of the
   latent score, and latent coverage drops to ≈0.867 < 0.90. The test asserts
   the failure PERSISTS (i.e. documents that the old "mean-preserving spread ⇒
   conservative" claim is false), so a future edit restoring that claim
   without shape conditions will trip this test.

2. BOUND (Theorem 2(b), inflated form): the noise-inflated band with radius
   q̂ + u covers the latent target at level ≥ 1 − α − P(|ξ| > u). With u = 1
   (the noise's support bound) the guarantee is the full 1 − α, and the test
   asserts it holds on the same adversarial DGP.
"""
import numpy as np

ALPHA = 0.10
K = 200
REPS = 4000


def _draw_R(rng, n):
    comp = rng.random(n) < 0.15
    return np.where(comp, 10.0 + 0.01 * rng.standard_normal(n),
                    np.abs(0.01 * rng.standard_normal(n)))


def _sim(inflate: float):
    rng = np.random.default_rng(7)
    m = int(np.ceil((1 - ALPHA) * (K + 1)))
    cover = 0
    for _ in range(REPS):
        R_cal = _draw_R(rng, K)
        xi = rng.choice([-1.0, 1.0], K)
        q = np.sort(R_cal + xi)[m - 1]
        cover += _draw_R(rng, 1)[0] <= q + inflate
    return cover / REPS


def test_symmetric_noise_is_not_sufficient_for_latent_conservativeness():
    cov = _sim(inflate=0.0)
    mc3 = 3 * np.sqrt(0.9 * 0.1 / REPS)          # ≈ 0.014
    # the naive band UNDERCOVERS the latent target despite symmetric noise
    assert cov < (1 - ALPHA) - mc3, cov


def test_noise_inflated_band_restores_the_guarantee():
    cov = _sim(inflate=1.0)                      # u = noise support bound
    mc3 = 3 * np.sqrt(0.9 * 0.1 / REPS)
    assert cov >= (1 - ALPHA) - mc3, cov
