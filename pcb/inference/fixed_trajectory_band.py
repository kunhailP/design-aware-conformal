"""Fixed-length trajectory PCB — estimand B: the last L rounds of a country,
all thresholds, simultaneously.  Main specification: L = 4.

Claim protected:
    Pr[ θ_{c*,r}(t) ∈ B_r(t)  ∀ r ∈ recent L rounds, ∀ t ] ≥ 1 − α .

Every country (calibration and target) contributes a trajectory of EXACTLY L
rounds — its most recent L, aligned by recency slot j = 0 (oldest of the L)
… L−1 (newest). Equal lengths remove the trajectory-length heterogeneity of
the all-round score (a longer trajectory has more chances to produce one
extreme error, so variable-length sup-scores are not comparable across
countries); the all-round variant is retained upstream only as a sensitivity.

Construction, with a per-slot modulation s_j(t) computed from the calibration
trajectories only:
    R_c = max_{j<L} max_t |E_{c,j}(t)| / s_j(t),
    q̂  = R_(m),  m = ⌈(1−α)(K+1)⌉   (exact order statistic, K countries),
    B_j(t) = θ̂_{c*,j}(t) ± q̂ · s_j(t),  isotonic-tightened per round.

Finite-sample validity (docs/ESS_CLUSTER_THEORY.md): if country trajectories
are exchangeable and s is independent of the scored errors (split modulation;
the in-sample variant is audited empirically), the rank of the target's score
among the K+1 is uniform, so the trajectory is covered with prob ≥ 1 − α.
With L = 1 the construction reduces to the clustered curve band, i.e. to PCB.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from .conformal_band import _modulation, isotonic_tighten


def stack_trajectories(E: np.ndarray, countries: np.ndarray,
                       rounds: np.ndarray, L: int = 4):
    """(K, L, T) array of each country's most recent L error curves.

    Countries with fewer than L rounds are dropped (returned in `dropped`).
    Slot order is oldest→newest within the selected L.
    """
    df = pd.DataFrame({"c": countries, "r": rounds, "i": np.arange(len(countries))})
    keep, labels, dropped = [], [], []
    for c, sub in df.sort_values("r").groupby("c", observed=True, sort=True):
        if len(sub) >= L:
            keep.append(sub.i.to_numpy()[-L:])
            labels.append(c)
        else:
            dropped.append(c)
    traj = E[np.array(keep)] if keep else np.empty((0, L, E.shape[1]))
    return traj, np.array(labels), dropped


def slot_modulation(traj: np.ndarray, floor_frac: float = 0.05) -> np.ndarray:
    """s_j(t): per-recency-slot modulation from calibration trajectories."""
    return np.stack([_modulation(traj[:, j, :], floor_frac)
                     for j in range(traj.shape[1])])


def trajectory_scores(traj: np.ndarray, s: np.ndarray) -> np.ndarray:
    """R_c = sup over slots and thresholds of |E|/s. traj (K,L,T), s (L,T)."""
    return np.max(np.abs(traj) / s[None, :, :], axis=(1, 2))


def trajectory_quantile(scores: np.ndarray, alpha: float = 0.1):
    """Exact finite-sample order statistic m = ⌈(1−α)(K+1)⌉ — never an
    interpolation quantile. Returns (q, m, attainable_level)."""
    K = scores.shape[0]
    m = int(np.ceil((1 - alpha) * (K + 1)))
    if m > K:
        return np.inf, m, 1.0
    return float(np.sort(scores)[m - 1]), m, m / (K + 1)


def trajectory_modulation(traj_cal: np.ndarray, kind: str = "none",
                          floor_frac: float = 0.05) -> np.ndarray:
    """s (L, T). `none` (default) is the unstudentized U0 construction, exact
    at any K; `pooled` estimates one s(t) from all K·L curves and repeats it
    across slots; `per_slot` estimates s_j(t) per recency slot.

    The default is U0 (`none`): every in-sample modulation puts calibration
    data in the denominator that studentises its own score, an asymmetry with
    the unobserved target that costs coverage at small K. With K ≈ 30
    countries a per-slot scale is estimated from only K curves — the E9 audit
    measured real undercoverage (trstprl L=4: 22/30 per-slot vs 27/30 pooled)
    — and even the pooled variant carries an O(1/(K·L)) self-inclusion bias.
    The exact theorem for a studentized band requires a split modulation;
    `pooled`/`per_slot` remain available as opt-in sensitivity variants.
    """
    K, L, T = traj_cal.shape
    if kind == "none":                       # U0: unstudentized, exact
        return np.ones((L, T))
    if kind == "pooled":
        return np.tile(_modulation(traj_cal.reshape(K * L, T), floor_frac),
                       (L, 1))
    if kind == "per_slot":
        return slot_modulation(traj_cal, floor_frac)
    raise ValueError(f"unknown modulation kind {kind}")


def fixed_trajectory_band(traj_cal: np.ndarray, centers: np.ndarray,
                          alpha: float = 0.1, tighten: bool = True,
                          modulation: str = "none"):
    """Band for a held-out country's L-round trajectory.

    traj_cal : (K, L, T) calibration trajectories (target country excluded,
               also from the modulation). centers : (L, T) predicted curves.
    Returns (lo, hi) each (L, T), plus a dict of audit fields.
    """
    s = trajectory_modulation(traj_cal, modulation)
    scores = trajectory_scores(traj_cal, s)
    q, m, attain = trajectory_quantile(scores, alpha)
    centers = np.asarray(centers, float)
    if np.isinf(q):
        lo, hi = np.zeros_like(centers), np.ones_like(centers)
    else:
        lo, hi = centers - q * s, centers + q * s
    for j in range(centers.shape[0]):
        if tighten:
            lo[j], hi[j] = isotonic_tighten(lo[j], hi[j])
        else:
            lo[j], hi[j] = np.clip(lo[j], 0, 1), np.clip(hi[j], 0, 1)
    audit = dict(K=traj_cal.shape[0], order_index=m, attainable=attain,
                 critical=q, s=s)
    return lo, hi, audit
