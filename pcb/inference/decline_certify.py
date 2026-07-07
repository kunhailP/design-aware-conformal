"""Certify distribution-wide trust decline from a trajectory band.

A design-aware clustered trajectory band gives, jointly with prob ≥ 1−α, a box
[lo_{r}(t), hi_{r}(t)] for every θ_{c,r}(t) over (rounds × thresholds). Because
the band is a PRODUCT of intervals, an ordering claim holds for every surface in
the band iff it holds for the box's worst corner — so the FOSD test below is
EXACT for the box, not merely conservative (docs/POLITICAL_PAYOFF_ESTIMAND.md).

First-order stochastic deterioration (trust moves DOWN) from round r to r+1 means
more mass at low t: F_{r+1}(t) ≥ F_r(t) for all t. Every F_{r+1} in its interval
and every F_r in its interval satisfy this iff lo_{r+1}(t) ≥ hi_r(t) ∀t. Hence:

  persistent : that non-overlap holds for EVERY consecutive pair,
  net        : it holds between the first and last observed round,
  partial    : the point estimates move down on some t-range but FOSD is not
               certified (reported as "moved, not certified").

Validity is inherited from band coverage: certifying decline when the truth is
not a decline requires the band to miss the truth, prob ≤ α.
"""
from __future__ import annotations
import numpy as np


def _fosd_down(lo_next: np.ndarray, hi_prev: np.ndarray) -> bool:
    """Certify F_next(t) ≥ F_prev(t) ∀t (trust deteriorates) for a box band."""
    return bool(np.all(lo_next >= hi_prev))


def certify_decline(lo: np.ndarray, hi: np.ndarray) -> dict:
    """lo, hi : (L, T) trajectory band, rounds ordered oldest→newest.

    Returns flags {persistent, net, recovery_persistent, indeterminate}.
    """
    L = lo.shape[0]
    pairs_down = [_fosd_down(lo[r + 1], hi[r]) for r in range(L - 1)]
    pairs_up = [_fosd_down(lo[r], hi[r + 1]) for r in range(L - 1)]  # recovery
    persistent = bool(np.all(pairs_down))
    net = _fosd_down(lo[-1], hi[0])
    recovery = bool(np.all(pairs_up))
    return dict(persistent_decline=persistent,
                net_decline=net,
                persistent_recovery=recovery,
                indeterminate=not (persistent or recovery or net))


def truth_is_persistent_decline(theta: np.ndarray,
                                t_mask: np.ndarray | None = None) -> bool:
    """Ground-truth label: latent FOSD-down at every consecutive pair over the
    (optionally core-restricted) threshold range — the exact claim certified."""
    if t_mask is None:
        t_mask = np.ones(theta.shape[1], dtype=bool)
    th = theta[:, t_mask]
    return bool(np.all([np.all(th[r + 1] >= th[r])
                        for r in range(th.shape[0] - 1)]))


def certify_decline_differences(diff_hat: np.ndarray, diff_boot: np.ndarray,
                                alpha: float = 0.10,
                                t_mask: np.ndarray | None = None) -> dict:
    """Design-aware certification on WITHIN-country consecutive differences.

    For a SURVEYED country the persistent-decline claim θ_{r+1}(t) ≥ θ_r(t)
    ∀(r,t) is a pure survey-design inference: the country effect cancels in the
    difference D_r(t) = θ̃_{r+1}(t) − θ̃_r(t), leaving only design uncertainty
    (no transport error). This is where propagating design variance is the whole
    game — and it is far tighter than a level band.

    diff_hat  : (L-1, T) observed consecutive differences of the weighted CDFs.
    diff_boot : (B, L-1, T) design-bootstrap replicates of those differences.
    t_mask    : (T,) bool restricting the FOSD claim to an informative threshold
                range. The CDF differences degenerate to ≈0 at the extreme
                thresholds (both CDFs pin to 0/1), where FOSD is un-certifiable
                under any noise; the claim is made over the distribution's core.
    Certify (design-aware) if a one-sided simultaneous lower band over the
    (pair × core-threshold) grid stays ≥ 0: L = D̂ − ĉ·sd ≥ 0, ĉ = (1−α)
    quantile of the studentised sup deviation across bootstrap replicates.
    Also returns the PLUG-IN verdict (point estimate ≥ 0 everywhere), which
    ignores design uncertainty and over-certifies.
    """
    if t_mask is None:
        t_mask = np.ones(diff_hat.shape[1], dtype=bool)
    dh = diff_hat[:, t_mask]
    db = diff_boot[:, :, t_mask]
    sd = np.maximum(db.std(0), 1e-6)                     # (L-1, |core|)
    # percentile-t simultaneous lower band: the distribution of (D̂ − D) is
    # approximated by the bootstrap distribution of (D* − D̂) = (db − dh); certify
    # if maxₖ (D̂ − D)/sd ≤ ĉ everywhere, ĉ = (1−α) quantile of that sup.
    dev = np.max((db - dh[None]) / sd[None], axis=(1, 2))  # (B,)
    c = np.quantile(dev, 1 - alpha)
    return dict(design_aware=bool(np.all(dh - c * sd >= 0)),
                plugin=bool(np.all(dh >= 0)))
