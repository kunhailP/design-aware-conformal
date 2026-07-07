"""E13 — Gate 5D inferential audit: separate the units of the ESS headline and
control the within-country multiplicity.

The e12 headline counted countries with ANY plug-in-certified pair, but each of
the 57 pairs used its own 90% band — looking across a country's pairs (and across
the 30 countries) inflates the error rate. This audit fixes the guarantee unit:

  pair-level      : marginal per-pair band (e12; multiplicity NOT controlled)
  country net     : one design band on the first→last core-round difference
  country persist : ONE country-wide simultaneous band over ALL of a country's
                    adjacent-wave differences × low-trust thresholds
                    R_c = max_{pairs, t} |D̂ − D| / s  → the strong, within-
                    country-multiplicity-controlled claim.

Country-wide certification is just `certify_decline_differences` applied to the
country's whole stack of pair-differences at once (the sup already spans
pairs × thresholds), so no new inference machinery is introduced. We also give a
Bonferroni-across-countries column for a fully-simultaneous set statement.

Real data has no oracle truth: reclassified countries are labelled "certified by
plug-in, inconclusive under design-aware inference" — NEVER "false positive"
(that term is reserved for the simulation, Gate 5C).

Run:  python -m pcb.experiments.e13_ess_audit
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed
import pandas as pd

from pcb.data.audit_ess import audit, load
from pcb.experiments.e12_ess_decline import (ALPHA, B, CORE_T, T, _design_boot,
                                             _round_stats, _wcdf)
from pcb.inference.decline_certify import certify_decline_differences

OUTCOMES = ("trstprl", "stfdem")


def _pair_diff(a, b, outcome, rng):
    """Design-bootstrap the F_{r+1}−F_r difference for one adjacent pair."""
    y0, w0, s0, p0 = _round_stats(a, outcome)
    y1, w1, s1, p1 = _round_stats(b, outcome)
    if min(len(y0), len(y1)) < 100:
        return None
    dhat = _wcdf(y1, w1) - _wcdf(y0, w0)                        # (T,)
    db0 = _design_boot(y0, w0, s0, p0, rng)
    db1 = _design_boot(y1, w1, s1, p1, rng)
    return dhat, (db1 - db0)                                     # (T,), (B,T)


def audit_country(csub, core_rounds, outcome, rng):
    """Returns per-country certification at three units + the pair records."""
    pairs = [(r, r + 1) for r in core_rounds if r + 1 in core_rounds]
    recs, hats, boots = [], [], []
    for r0, r1 in pairs:
        out = _pair_diff(csub[csub.essround == r0], csub[csub.essround == r1],
                         outcome, rng)
        if out is None:
            continue
        dhat, dboot = out
        hats.append(dhat); boots.append(dboot)
        c1 = certify_decline_differences(dhat[None], dboot[:, None], ALPHA, CORE_T)
        recs.append(dict(r_from=r0, r_to=r1, pair_plugin=c1["plugin"],
                         pair_da=c1["design_aware"]))
    if not hats:
        return None
    H = np.array(hats)                                           # (P, T)
    Bd = np.moveaxis(np.array(boots), 1, 0)                      # (B, P, T)

    # country-wide simultaneous persistent-decline band over all pairs × core
    persist = certify_decline_differences(H, Bd, ALPHA, CORE_T)
    # Bonferroni-across-countries version (for a simultaneous SET statement)
    persist_bonf = certify_decline_differences(H, Bd, ALPHA / 30.0, CORE_T)

    # net: first→last core round accumulated difference
    rounds = sorted(core_rounds)
    net_out = _pair_diff(csub[csub.essround == rounds[0]],
                         csub[csub.essround == rounds[-1]], outcome, rng)
    if net_out is not None:
        nd, nb = net_out
        net = certify_decline_differences(nd[None], nb[:, None], ALPHA, CORE_T)
    else:
        net = dict(plugin=False, design_aware=False)

    any_pair_plugin = any(r["pair_plugin"] for r in recs)
    any_pair_da = any(r["pair_da"] for r in recs)
    return dict(
        n_pairs=len(recs),
        pair_plugin=sum(r["pair_plugin"] for r in recs),
        pair_da=sum(r["pair_da"] for r in recs),
        any_plugin=any_pair_plugin, any_da=any_pair_da,
        net_plugin=net["plugin"], net_da=net["design_aware"],
        persist_plugin=persist["plugin"], persist_da=persist["design_aware"],
        persist_da_bonf=persist_bonf["design_aware"])


def main():
    df = load()
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    rows = []
    for outcome in OUTCOMES:
        for c, csub in df.groupby("cntry", observed=True):
            core_rounds = [r for r in sorted(csub.essround.unique())
                           if klass.get((c, r)) == "core"]
            if len([r for r in core_rounds if r + 1 in core_rounds]) == 0:
                continue
            rng = np.random.default_rng(det_seed(outcome, c))
            res = audit_country(csub, core_rounds, outcome, rng)
            if res:
                rows.append(dict(outcome=outcome, cntry=c, **res))
    cty = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    cty.to_csv("results/ess_country_certification.csv", index=False)

    print("ESS inferential audit — units of the decline headline "
          "(core rounds 9-11, α=0.10)\n")
    hdr = (f"{'outcome':8s} {'countries':>9s} {'pairs':>6s} | "
           f"{'certified pairs':>16s} | {'any-pair decline':>17s} | "
           f"{'net (span)':>12s} | {'persistent (ctry-wide)':>22s} | "
           f"{'persist+Bonf':>12s}")
    print(hdr); print("-" * len(hdr))
    for outcome in OUTCOMES:
        p = cty[cty.outcome == outcome]
        npair = int(p.n_pairs.sum())
        line = (f"{outcome:8s} {len(p):9d} {npair:6d} | "
                f"plug {int(p.pair_plugin.sum()):2d} / DA {int(p.pair_da.sum()):2d}"
                f"  of {npair:3d} | "
                f"plug {int(p.any_plugin.sum()):2d} / DA {int(p.any_da.sum()):2d}"
                f"       | "
                f"plug {int(p.net_plugin.sum()):2d} / DA {int(p.net_da.sum()):2d} | "
                f"plug {int(p.persist_plugin.sum()):2d} / DA "
                f"{int(p.persist_da.sum()):2d}            | "
                f"DA {int(p.persist_da_bonf.sum()):2d}")
        print(line)

    print("\nunique-country decline counts by guarantee unit (plug-in / DA):")
    for outcome in OUTCOMES:
        p = cty[cty.outcome == outcome]
        rep_plug = int((p.pair_plugin >= 2).sum())
        rep_da = int((p.pair_da >= 2).sum())
        print(f"  {outcome}: any-pair {int(p.any_plugin.sum())}/{int(p.any_da.sum())}"
              f"  repeated(≥2 pairs) {rep_plug}/{rep_da}"
              f"  net-span {int(p.net_plugin.sum())}/{int(p.net_da.sum())}"
              f"  persistent {int(p.persist_plugin.sum())}/{int(p.persist_da.sum())}")

    print("\nCountry lists (design-aware):")
    for outcome in OUTCOMES:
        p = cty[cty.outcome == outcome]
        print(f"\n{outcome}:")
        print(f"  persistent decline (country-wide simultaneous): "
              f"{sorted(p.cntry[p.persist_da])}")
        print(f"  net decline (first→last span):                  "
              f"{sorted(p.cntry[p.net_da])}")
        print(f"  any-pair decline (marginal, not mult-controlled): "
              f"{sorted(p.cntry[p.any_da])}")
        print(f"  plug-in-certified but inconclusive under DA:      "
              f"{sorted(p.cntry[p.any_plugin & ~p.any_da])}")


if __name__ == "__main__":
    main()
