"""PCB — Population Conformal Band for a transported distribution function.

The candidate methods contribution (docs/PROOFS.md, Path A). A finite-sample
SIMULTANEOUS band for the whole curve t ↦ F_new(t), with population as the
exchangeable unit and the CDF shape exploited for a coverage-preserving width
reduction. Fixes the catastrophic marginal-vs-simultaneous gap of per-threshold
conformal (measured 87.5% marginal vs 37.5% joint on the real data).

Guarantee (Proposition PCB-1): if populations are exchangeable, the band covers
the whole curve with prob ≥ 1−α. Lemma PCB-2: the isotonic tightening preserves
that coverage while never widening the band.
"""
from __future__ import annotations
import numpy as np


def _modulation(E: np.ndarray, floor_frac: float = 0.05) -> np.ndarray:
    """s(t): pointwise spread of the transport error across calibration pops,
    floored to avoid division by ~0 at thresholds with no variation."""
    s = E.std(0)
    return np.maximum(s, floor_frac * max(s.max(), 1e-12))


def conformal_band_quantile(E: np.ndarray, alpha: float = 0.1,
                            studentize: bool = False):
    """Sup-type conformal quantile q̂ and per-threshold scale s(t).

    R_i = max_t |E_i(t)| / s(t); q̂ = ⌈(1−α)(K+1)⌉-th order stat of {R_i}.
    Returns (q̂, s). q̂ = inf when the level exceeds K (honest small-K penalty:
    the band becomes [0,1]).

    studentize=False → s(t) ≡ 1 (variant "U0", the deployed DEFAULT): the scores
        depend only on their own cluster, so {R_i, R_target} are exchangeable and
        the order-statistic band is EXACT at any K —
        P(cover) ≥ ⌈(1−α)(K+1)⌉/(K+1) ≥ 1−α, distribution-free.
    studentize=True  → s(t) = in-sample pooled modulation SD_c E_c(t) (variant
        "S2", opt-in only): per-threshold-adaptive but the shared data-dependent
        denominator breaks exchangeability with the unobserved target, giving a
        finite-K self-inclusion coverage deficit at small K (quantified in
        SMALLK_CORRECTION_PREREG; this is why U0 is the default).
    """
    E = np.asarray(E, dtype=float)
    K, T = E.shape
    s = _modulation(E) if studentize else np.ones(T)
    R = np.max(np.abs(E) / s, axis=1)
    idx = int(np.ceil((1 - alpha) * (K + 1)))
    q = np.inf if idx > K else float(np.sort(R)[idx - 1])
    return q, s


def loo_deviations(F: np.ndarray) -> np.ndarray:
    """E_c = F_c − mean_{c'≠c} F_{c'}: deployment-mode calibration deviations.

    With an UNSURVEYED target the transport center must exclude the target by
    necessity. A grand-mean center then puts each calibration unit inside its
    own center (deviations shrunk by (K−1)/K) while the target sits outside —
    an asymmetry that biases the conformal quantile downward (anti-conservative,
    O(1/K)). The leave-one-out deviation removes the self-inclusion: each
    calibration score excludes its own unit exactly as the target's score
    excludes the target. The two pools still differ by one unit (K−1 vs K), so
    the calibration deviations are, if anything, slightly MORE dispersed than
    the target's — a residual O(1/K²) asymmetry in the conservative direction.
    The deployed construction is itself theorem-covered (supplement,
    Proposition: LOO validity): inflating the radius by K/(K−1) —
    `loo_exact_inflation(K)` — restores exact finite-sample validity at every
    K, distribution-free, and the uninflated band carries an explicit O(1/K)
    coverage remainder, measured at zero in e58. When the target IS surveyed
    (validation mode), a common grand mean restores exactness directly; fixed,
    own-unit (LOCF), and split-fold centers are the other exact constructions
    Theorem 3 states.
    """
    F = np.asarray(F, dtype=float)
    K = F.shape[0]
    if K < 2:
        raise ValueError("need at least 2 calibration units for a LOO center")
    tot = F.sum(axis=0, keepdims=True)
    return F - (tot - F) / (K - 1)


def loo_exact_inflation(K: int) -> float:
    """Radius factor restoring exact finite-sample validity for the deployed
    leave-one-out construction (supplement, Proposition: LOO validity):
    P(target score <= K/(K-1) * q_hat) >= 1 - alpha at every K,
    distribution-free. Applied BY DEFAULT to the returned anchor radius in
    `pcb.dapcb.dapcb` (loo_center=True), so the deployed band is the band the
    proposition certifies. At this paper's cross-national K the cost is
    <= 3.5% of width; e58 measures the uninflated deficit at zero."""
    if K < 2:
        raise ValueError("need K >= 2")
    return K / (K - 1.0)


def isotonic_tighten(lo: np.ndarray, hi: np.ndarray):
    """Lemma PCB-2: tighten a band around a monotone CDF, coverage-preserving.

    lo ← running max (a CDF is nondecreasing, so the lower bound can only rise);
    hi ← running min from the right; both clipped to [0,1].
    """
    lo = np.clip(np.maximum.accumulate(lo), 0.0, 1.0)
    hi = np.clip(np.minimum.accumulate(hi[::-1])[::-1], 0.0, 1.0)
    return lo, np.maximum(hi, lo)  # guard numerical crossing


def population_conformal_band(cal_errors: np.ndarray, center: np.ndarray,
                              alpha: float = 0.1, tighten: bool = True,
                              studentize: bool = False):
    """Full PCB band around `center` = F̂_target(·).

    cal_errors : (K, T) source transport-error curves. center : (T,) target
    plug-in headcount curve. Returns (lo, hi) absolute band in [0,1]^T.
    The default (studentize=False) is the finite-sample-exact unstudentized
    band (U0), valid at any K; `studentize=True` opts into the S2 variant,
    which carries a finite-K self-inclusion deficit (SMALLK_CORRECTION_PREREG).
    """
    q, s = conformal_band_quantile(cal_errors, alpha, studentize=studentize)
    center = np.asarray(center, dtype=float)
    if np.isinf(q):
        lo, hi = np.zeros_like(center), np.ones_like(center)
    else:
        lo, hi = center - q * s, center + q * s
    if tighten:
        lo, hi = isotonic_tighten(lo, hi)
    else:
        lo, hi = np.clip(lo, 0, 1), np.clip(hi, 0, 1)
    return lo, hi
