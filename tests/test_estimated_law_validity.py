"""Theorem 4′ — estimated-law validity of the deconvolution band.

Machine checks for the three clauses, on a DGP satisfying assumption (A1)
(Gaussian scale family: observed curves = sqrt(s_R² + v_c²)·W_c, latent target
= s_R·W, common W law):

  (i)   ORACLE EXACTNESS: with true scales the studentized order-statistic
        band hits the attainable level two-sided — the scale-family argument
        makes deconvolution exact, not approximate.
  (ii)  ESTIMATED-SCALE FLOOR: with ŝ_T from `deconv_target_scale` and noisy
        design SDs, latent coverage respects 1 − α − ε at K = 120 and the
        remainder is visibly smaller at K = 400.
  (iii) GUARD DIRECTION: the finite-K-safe scale errs wide — mean coverage sits
        at or above nominal, not below.
"""
import numpy as np

from pcb.inference.design_aware import _finite_quantile, deconv_target_scale

ALPHA = 0.10
T = 4
S_R = 0.1


def _panel(rng, K, noise_ratio, b_relerr=0.0):
    W = rng.standard_normal((K + 1, T))
    v = S_R * noise_ratio * (0.5 + rng.random((K, 1)))     # heteroskedastic
    E = np.sqrt(S_R**2 + v**2) * W[:K]                     # observed (A1)
    Et = S_R * W[K]                                        # latent target
    V = np.abs(v * (1 + b_relerr * rng.standard_normal((K, 1)))) * np.ones((1, T))
    return E, V, Et, v


def test_oracle_scales_are_exact():
    rng = np.random.default_rng(31)
    K, reps = 40, 3000
    m = int(np.ceil((1 - ALPHA) * (K + 1)))
    attain = m / (K + 1)
    cover = 0
    for _ in range(reps):
        E, _, Et, v = _panel(rng, K, noise_ratio=0.8)
        scores = np.max(np.abs(E) / np.sqrt(S_R**2 + v**2), axis=1)
        q = np.sort(scores)[m - 1]
        cover += int(np.max(np.abs(Et) / S_R) <= q)
    mc3 = 3 * np.sqrt(attain * (1 - attain) / reps)
    assert abs(cover / reps - attain) <= mc3, (cover / reps, attain)


def _estimated_coverage(K, reps, seed, b_relerr):
    rng = np.random.default_rng(seed)
    cover = 0
    for _ in range(reps):
        E, V, Et, _ = _panel(rng, K, noise_ratio=0.8, b_relerr=b_relerr)
        sT = deconv_target_scale(E, V)
        scores = np.max(np.abs(E) / np.sqrt(sT[None] ** 2 + V**2), axis=1)
        q = _finite_quantile(scores, ALPHA)
        cover += int(np.all(np.abs(Et) <= q * sT))
    return cover / reps


def test_estimated_scale_floor_and_K_decay():
    cov_small = _estimated_coverage(K=120, reps=1200, seed=32, b_relerr=0.15)
    cov_large = _estimated_coverage(K=400, reps=1200, seed=33, b_relerr=0.15)
    mc3 = 3 * np.sqrt(0.9 * 0.1 / 1200)
    assert cov_small >= (1 - ALPHA) - 0.03 - mc3, cov_small
    assert cov_large >= (1 - ALPHA) - 0.015 - mc3, cov_large


def test_safe_guard_errs_wide_not_narrow():
    # clause (iii): across a modest run, mean coverage at or above nominal
    cov = _estimated_coverage(K=200, reps=1500, seed=34, b_relerr=0.15)
    mc2 = 2 * np.sqrt(0.9 * 0.1 / 1500)
    assert cov >= (1 - ALPHA) - mc2, cov
