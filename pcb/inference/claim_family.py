"""One band, one guarantee, every derivable claim.

The certification machinery of `decline_certify` states its validity correctly --
"validity is inherited from band coverage" -- but the deployed path builds a
*separate* simultaneous band for each contrast family (adjacent pairs for the
persistent rung, the first-to-last contrast for the net rung), so the inheritance
holds within a family and not across them. Every multiplicity objection this
paper has had to answer is a consequence of that split: an any-pair conjunction
with no control across a country's pairs, a sub-span sweep read as forty-five
marginal tests, a rise/fall pair with no shared budget, a screening correction
bolted on at one rung only.

The fix is not a correction. It is to build the band over the object all the
claims are functions of.

Let theta = {theta_r(t)} be a country's trajectory surface and let
D_{a,b}(t) = theta_b(t) - theta_a(t) for every ordered pair of observed rounds
a < b. A single studentized sup-t band over the whole family {D_{a,b}(t)},
calibrated at one critical value c, covers all of them jointly with probability
1 - alpha. On that one event, EVERY claim that is a deterministic function of the
covered surface is true simultaneously:

    CLAIM-FAMILY TRANSFER.  Let B be a 1-alpha simultaneous band for theta and
    let {A_j} be any family of claim sets. Define the certified subfamily
    J = {j : B is contained in A_j}. Then

        Pr( theta in A_j for every j in J )  >=  1 - alpha,

    with no dependence on the size of the family, no Bonferroni, and no
    selection cost -- because {theta in B} implies theta in A_j for every j in J
    by set inclusion, and the coverage event is a single event.

    Two scope limits follow and are easy to lose. The alpha is spent PER BAND,
    so a study covering many countries spends one alpha per country and the
    counts across countries carry no familywise control unless one is added.
    And `frac_spans_declining` is a LOWER BOUND on the true share, not an
    estimate; because the shared critical value grows with the length of a
    country's record while the denominator grows quadratically, the share is
    comparable within a country and not across.

So: the pairwise claims, the persistent claim, the net span, every sub-span, both
directions, and the endpoint-robustness statement are all read off one band at
one level. The sub-span fraction stops being a robustness sweep and becomes a
certified quantity. Endpoint choice stops being a researcher degree of freedom,
because every endpoint choice is certified at the same time. The price is a wider
critical value -- the sup now runs over all pairs, not one family -- and that
price is the honest cost of the joint statement.

Deployed entry point: `certify_claim_family`.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np


def certify_claim_family(curves: np.ndarray, boots: np.ndarray,
                         alpha: float = 0.10,
                         t_mask: np.ndarray | None = None,
                         two_sided: bool = True) -> dict:
    """Certify every derivable ordering claim from ONE simultaneous band.

    Parameters
    ----------
    curves : (L, T) observed CDFs for the country's L ordered rounds.
    boots  : (B, L, T) bootstrap replicates of the same curves.
    alpha  : level of the joint statement.
    t_mask : (T,) bool restricting claims to the informative threshold core.
    two_sided : if True the band covers declines AND rises jointly (the
        critical value is the sup over both directions), so certified
        recoveries carry the same guarantee as certified declines and need no
        separate budget. If False only declines are certified, at a slightly
        smaller critical value.

    Returns
    -------
    dict with
      `c`            the shared critical value,
      `lower[(a,b)]` the certified decline lower bound for that span
                     (min over core thresholds of D_hat - c*sd); > 0 certifies,
      `upper[(a,b)]` the analogous certified rise bound,
      `declines`     the set of spans certified as declines,
      `rises`        the set of spans certified as rises,
      and the derived rungs: `net`, `persistent`, `any_pair`, `n_spans`,
      `frac_spans_declining` -- all inherited from the same coverage event.
    """
    curves = np.asarray(curves, float)
    boots = np.asarray(boots, float)
    L, T = curves.shape
    if t_mask is None:
        t_mask = np.ones(T, bool)
    core = np.asarray(t_mask, bool)

    spans = list(combinations(range(L), 2))
    if not spans:
        return dict(c=np.nan, lower={}, upper={}, declines=set(), rises=set(),
                    net=False, persistent=False, any_pair=False, episodic=False,
                    n_spans=0, n_declining=0, n_rising=0,
                    frac_spans_declining=np.nan, net_lower=np.nan)

    # the family of contrasts, and its bootstrap replicates
    dh = np.stack([curves[b, core] - curves[a, core] for a, b in spans])      # (S, |core|)
    db = np.stack([boots[:, b, core] - boots[:, a, core] for a, b in spans], 1)  # (B, S, |core|)
    sd = np.maximum(db.std(0), 1e-6)

    # ONE critical value over the whole family (and both directions if asked)
    dev = (db - dh[None]) / sd[None]
    stat = np.max(np.abs(dev), axis=(1, 2)) if two_sided else \
        np.max(dev, axis=(1, 2))
    c = float(np.quantile(stat, 1 - alpha))

    lo = dh - c * sd                       # certified decline bound per span
    lower = {s: float(lo[i].min()) for i, s in enumerate(spans)}
    declines = {s for s in spans if lower[s] > 0}
    if two_sided:
        hi = -dh - c * sd                  # certified rise bound per span
        upper = {s: float(hi[i].min()) for i, s in enumerate(spans)}
        rises = {s for s in spans if upper[s] > 0}
        episodic = bool(declines and rises)
    else:
        # c controls only sup (db - dh)/sd, so the reverse direction carries no
        # guarantee here: return nothing rather than an uncalibrated object.
        upper = rises = episodic = None

    adjacent = [(i, i + 1) for i in range(L - 1)]
    return dict(
        c=c, lower=lower, upper=upper, declines=declines, rises=rises,
        net=(0, L - 1) in declines,
        persistent=bool(adjacent) and all(p in declines for p in adjacent),
        any_pair=any(p in declines for p in adjacent),
        episodic=episodic,
        n_spans=len(spans),
        n_declining=len(declines),
        n_rising=(len(rises) if rises is not None else None),
        frac_spans_declining=len(declines) / len(spans),
        net_lower=lower[(0, L - 1)])
