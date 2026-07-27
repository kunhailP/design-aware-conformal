"""E47 — breakdown design effects for the long-window net certifications.

E44 shows the nine net certifications are unchanged at a design effect of 2.0 on
the weights-only rounds. That is a weaker statement than it sounds: all nine
spans END at round 11, a core cell that is not inflated, so a deff of 2.0 on the
first endpoint widens the span band by only ~1.1-1.3x. The informative quantity
is the BREAKDOWN point: the deff at which each certification would fail.

We bisect on the deff applied to the weights-only cells, per country, holding
the bootstrap draws fixed (paired comparison), and also report the deff measured
on that country's own core rounds -- the ratio of the stratified-PSU bootstrap
SD to the naive respondent bootstrap SD on the same cell -- so the reader can
see the breakdown point against a realistic scale rather than a hypothetical.

Output: results/ess_breakdown_deff.csv
Run:    python -m pcb.experiments.e47_breakdown_deff   (~1 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import audit, load
from pcb.experiments.e12_ess_decline import (ALPHA, CORE_T, _design_boot,
                                             _naive_boot, _round_stats, _wcdf)
from pcb.experiments.e45_magnitudes_and_rises import _band_lower

OUTCOMES = ("trstprl", "stfdem")
MIN_N = 100
DEFF_MAX = 100.0


def _cells(csub, rounds, klass, c, outcome, rng):
    """Per round: (F, design-or-naive draws, is_weights_only)."""
    out = {}
    for r in rounds:
        y, w, s, p = _round_stats(csub[csub.essround == r], outcome)
        if len(y) < MIN_N:
            continue
        F = _wcdf(y, w)
        if klass.get((c, r)) == "core":
            out[r] = (F, _design_boot(y, w, s, p, rng), False)
        else:
            out[r] = (F, _naive_boot(y, w, rng), True)
    return out


def _net_lb(cells, rounds, deff):
    """Certified net lower bound with `deff` applied to weights-only cells."""
    def draws(r):
        F, B, wo = cells[r]
        return F[None, :] + np.sqrt(deff) * (B - F[None, :]) if wo else B
    F0, F1 = cells[rounds[0]][0], cells[rounds[-1]][0]
    return _band_lower((F1 - F0)[None], (draws(rounds[-1]) - draws(rounds[0]))[:, None])


def _measured_deff(csub, r, outcome, rng):
    """Design-bootstrap SD / naive-bootstrap SD, squared, on one core cell."""
    y, w, s, p = _round_stats(csub[csub.essround == r], outcome)
    if len(y) < MIN_N:
        return np.nan
    d = _design_boot(y, w, s, p, rng)[:, CORE_T].std(0)
    n = _naive_boot(y, w, rng)[:, CORE_T].std(0)
    return float(np.mean((d / np.maximum(n, 1e-12)) ** 2))


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    kl = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    rows = []
    for outcome in OUTCOMES:
        for c, csub in df.groupby("cntry", observed=True):
            usable = [r for r in sorted(csub.essround.unique())
                      if kl.get((c, r)) in ("core", "extended")]
            if len(usable) < 2:
                continue
            rng = np.random.default_rng(det_seed("e36", outcome, c))
            cells = _cells(csub, usable, kl, c, outcome, rng)
            rr = sorted(cells)
            if len(rr) < 2 or not any(b == a + 1 for a, b in zip(rr[:-1], rr[1:])):
                continue
            if _net_lb(cells, rr, 1.0) <= 0:
                continue                                   # not certified at all
            lo, hi = 1.0, DEFF_MAX
            if _net_lb(cells, rr, hi) > 0:
                brk = np.inf
            else:
                for _ in range(30):                        # bisection
                    mid = 0.5 * (lo + hi)
                    if _net_lb(cells, rr, mid) > 0:
                        lo = mid
                    else:
                        hi = mid
                brk = 0.5 * (lo + hi)
            core_r = [r for r in rr if not cells[r][2]]
            md = (_measured_deff(csub, core_r[-1], outcome,
                                 np.random.default_rng(det_seed("e47", outcome, c)))
                  if core_r else np.nan)
            rows.append(dict(outcome=outcome, cntry=c, span=f"{rr[0]}-{rr[-1]}",
                             net_lb=round(_net_lb(cells, rr, 1.0), 4),
                             breakdown_deff=(np.inf if np.isinf(brk) else round(brk, 2)),
                             measured_core_deff=(round(md, 2) if md == md else np.nan)))
            print(f"{outcome:8s} {c}: lb={rows[-1]['net_lb']:.4f}  "
                  f"breakdown deff={rows[-1]['breakdown_deff']}  "
                  f"measured core deff={rows[-1]['measured_core_deff']}")
    res = pd.DataFrame(rows)
    res.to_csv("results/ess_breakdown_deff.csv", index=False)
    print("\n=== breakdown deff, net certifications ===")
    for outcome in OUTCOMES:
        p = res[res.outcome == outcome].sort_values("breakdown_deff")
        print(f"\n{outcome}:")
        print(p[["cntry", "span", "net_lb", "breakdown_deff",
                 "measured_core_deff"]].to_string(index=False))
    md = res.measured_core_deff.dropna()
    print(f"\nmeasured core-round deff across certified countries: "
          f"{md.min():.2f}-{md.max():.2f}, median {md.median():.2f} "
          f"({int((md < 1).sum())} of {len(md)} below 1)")


if __name__ == "__main__":
    main()
