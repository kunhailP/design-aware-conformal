"""Cross-country prevalence: a simultaneous lower bound on TRUE discoveries.

The claim-family band certifies claims within one country at one alpha, and the
manuscript is explicit about the cost: alpha is spent per band, so the count
"eight countries certify net erosion" carries no familywise control across
countries. This module supplies the missing rung of the ladder --- threshold ->
wave -> trajectory -> country -> cross-country prevalence --- so that the
across-country statement becomes

    "with 1-alpha simultaneous confidence, at least d of the K countries
     truly satisfy the claim,"

which no subset selection can invalidate (Goeman & Solari 2011).

Two pieces:

1. `claim_family_pvalues` inverts the certification over its level. For a
   country's joint sup-t band, a span (a, b) certifies a decline at level
   alpha iff c_alpha < c*_{a,b} := min_t D_hat(t)/sd(t) over the core, where
   c_alpha is the (1-alpha) quantile of the bootstrap sup statistic. The
   smallest certifying alpha is therefore the bootstrap tail probability
   p = P*(stat >= c*), computed with the finite-B (1+#)/(B+1) correction.
   Under a false claim, {certify at alpha} is contained in {the band misses
   the contrast surface}, whose probability the design bootstrap controls at
   alpha, so p is a (design-asymptotic) valid p-value. Countries' bootstraps
   are independent, which is what the Simes local tests below need.

2. `true_discoveries` runs Goeman-Solari closed testing with Simes local
   tests, using the standard shortcut: the hardest subset of size k to reject
   is the one holding the k LARGEST p-values (enlarging any p-value can only
   keep Simes non-rejecting), so

       d = m - max{ k : the k largest p-values q_(1)<=...<=q_(k) satisfy
                        q_(i) > i * alpha / k for every i },

   a simultaneous 1-alpha lower confidence bound on the number of true
   claims among all m --- simultaneously over every subset, hence immune to
   the selection involved in then naming the certified countries.

Deployed entry points: `claim_family_pvalues`, `true_discoveries`,
`prevalence_lower_bound`.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np


def claim_family_pvalues(curves: np.ndarray, boots: np.ndarray,
                         t_mask: np.ndarray | None = None,
                         two_sided: bool = True) -> dict:
    """Per-span certification p-values for one country, by alpha-inversion.

    Mirrors `certify_claim_family` exactly (same spans, same sup statistic,
    same studentization); a contract test pins the two to each other. Returns
    {'p_decline': {span: p}, 'p_rise': {span: p} | None, 'p_net': p,
     'p_any_adjacent': p} where p_net is the (0, L-1) decline p-value and
    p_any_adjacent is the smallest adjacent-pair decline p-value (valid for
    the any-pair claim because the family sup is shared: the any-pair claim
    certifies at alpha iff some adjacent span does).
    """
    curves = np.asarray(curves, float)
    B_, L, T = boots.shape[0], curves.shape[0], curves.shape[1]
    core = np.ones(T, bool) if t_mask is None else np.asarray(t_mask, bool)
    spans = list(combinations(range(L), 2))

    dh = np.stack([curves[b, core] - curves[a, core] for a, b in spans])
    db = np.stack([boots[:, b, core] - boots[:, a, core] for a, b in spans], 1)
    sd = np.maximum(db.std(0), 1e-6)

    dev = (db - dh[None]) / sd[None]
    stat = np.max(np.abs(dev), axis=(1, 2)) if two_sided else \
        np.max(dev, axis=(1, 2))

    def _tail(c_star: float) -> float:
        # smallest alpha at which quantile(stat, 1-alpha) < c_star, with the
        # conformal-style finite-B correction; 1.0 when c_star <= 0 (a span
        # that no level certifies).
        if c_star <= 0:
            return 1.0
        return float((1 + np.sum(stat >= c_star)) / (B_ + 1))

    p_dec = {s: _tail(float(np.min(dh[i] / sd[i]))) for i, s in enumerate(spans)}
    p_rise = ({s: _tail(float(np.min(-dh[i] / sd[i]))) for i, s in enumerate(spans)}
              if two_sided else None)
    adjacent = [(i, i + 1) for i in range(L - 1)]
    return dict(p_decline=p_dec, p_rise=p_rise,
                p_net=p_dec[(0, L - 1)],
                p_any_adjacent=min(p_dec[s] for s in adjacent))


def _h(pvals, alpha: float) -> int:
    """Size of the largest subset of the FULL family that its own Simes test
    fails to reject: h(alpha) in Goeman et al.'s closed-testing shortcut.
    Checking the k largest p-values suffices, because enlarging any p-value
    keeps Simes non-rejecting."""
    p = np.sort(np.asarray(pvals, float))[::-1]          # descending
    h = 0
    for k in range(1, p.size + 1):
        q = np.sort(p[:k])                               # k largest, ascending
        if np.all(q > alpha * np.arange(1, k + 1) / k):  # Simes fails to reject
            h = k
    return h


def true_discoveries(pvals, alpha: float = 0.10) -> int:
    """Goeman-Solari 1-alpha lower confidence bound on the number of true
    claims among ALL of `pvals`, via closed testing with Simes local tests
    (d = m - h). Requires the p-values valid and independent across units (or
    PRDS), which the per-country design bootstraps satisfy."""
    return int(len(np.asarray(pvals, float)) - _h(pvals, alpha))


def true_discoveries_subset(sub_pvals, full_pvals, alpha: float = 0.10) -> int:
    """The same 1-alpha simultaneous bound, read on a SUBSET post hoc.

    Closed testing makes the bound simultaneous over every subset, but the
    subset bound must respect the closure over the FULL family: an
    intersection hypothesis inside S is rejected only if every superset up to
    the full family is locally rejected. With Simes local tests this reduces
    to the shortcut (Goeman--Solari 2011; Goeman et al. 2019 / the `hommel`
    formula): with h = h(alpha) computed once on the full family,

        d(S) = max_{1<=u<=|S|} [ 1 - u + #{ p in S : p <= u*alpha/h } ],

    and d(S) = |S| when h = 0. Running `true_discoveries` on the subset alone
    would treat S as its own family, ignore the closure, and can be
    anti-conservative (e.g. full p = (.04, .06, .5) at alpha = .1 gives
    d(all) = 1; the naive subset bound on (.04, .06) would claim 2, the
    closure-correct bound is 1)."""
    sub = np.sort(np.asarray(sub_pvals, float))
    h = _h(full_pvals, alpha)
    if h == 0:
        return int(sub.size)
    best = 0
    for u in range(1, sub.size + 1):
        best = max(best, 1 - u + int(np.sum(sub <= u * alpha / h)))
    return int(max(best, 0))


def prevalence_lower_bound(pvalue_per_country: dict, alpha: float = 0.10) -> dict:
    """Convenience wrapper: {country: p} -> the prevalence statement.

    Two distinct objects, both simultaneously valid at level alpha because
    closed testing licenses reading the bound on EVERY subset post hoc
    (Goeman & Solari 2011, Thm/Cor on simultaneity over subsets):

      d                 lower bound on true discoveries among ALL units;
      countries_named   the largest k such that the k smallest-p units S_k
                        satisfy d(S_k) = k -- i.e. a set whose members are
                        ALL true discoveries at the same simultaneous level.

    The global d alone does not license naming the d smallest-p units (the
    bound says "at least d among all", not "these d"); the named set is
    therefore RE-CERTIFIED on its closure-correct subset bound
    (`true_discoveries_subset`) before being returned. `named_covers_d`
    reports whether len(countries_named) == d.
    """
    items = sorted(pvalue_per_country.items(), key=lambda kv: kv[1])
    pvals = [p for _, p in items]
    d = true_discoveries(pvals, alpha)
    k_named = 0
    for k in range(1, len(items) + 1):
        if true_discoveries_subset(pvals[:k], pvals, alpha) == k:
            k_named = k
    return dict(d=d, alpha=alpha,
                countries_named=[c for c, _ in items[:k_named]],
                named_covers_d=(k_named >= d))
