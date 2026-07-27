"""E36 — long-window ESS trajectory extension: rounds 1–11 (fieldwork 2002–2024).

The headline analysis (E13) is confined to rounds 9–11, the window whose
integrated files ship PSU/stratum identifiers — leaving the persistent rung a
single wave pair for Greece and at most two pairs elsewhere. This experiment
extends every country's trajectory to its full ESS participation record:

  rounds classified "core"     (design variables usable, i.e. 9–11):
      stratified-PSU design bootstrap (as E12/E13);
  rounds classified "extended" (1–8: outcomes + weights, no/degenerate design
      variables in the integrated file):
      weights-only respondent bootstrap — the WVS treatment. Understated design
      variance can only *inflate* certified counts (err-inclusive), the same
      one-directional caveat as the WVS reanalysis; the separate SDDF files for
      rounds 1–8 would upgrade these rounds to the full design bootstrap.

Units mirror E13 exactly: any-pair / net (first→last participation) / persistent
(one simultaneous band over ALL adjacent-round pairs × low-trust core), plug-in
vs design-aware, plus Bonferroni across the countries analyzed.

Output: results/ess_long_window.csv  (one row per outcome × country)
Run:    python -m pcb.experiments.e36_ess_long_window
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import audit, load
from pcb.experiments.e12_ess_decline import (ALPHA, CORE_T, _design_boot,
                                             _naive_boot, _round_stats, _wcdf)
from pcb.inference.decline_certify import certify_decline_differences

OUTCOMES = ("trstprl", "stfdem")
MIN_N = 100

# Design-effect inflation applied to the WEIGHTS-ONLY (rounds 1-8) cells only:
# draws are rescaled about the point estimate, F + sqrt(deff)*(F_b - F), so the
# sup-t critical value scales exactly by sqrt(deff). 1.0 = the shipped
# analysis; e44 drives this to 1.5 and 2.0 as a sensitivity for the counts that
# the understated weights-only variance could inflate.
DEFF_EXTENDED = 1.0


def _boot_for(sub, outcome, klass_cr, rng):
    """CDF + bootstrap draws for one country-round; design boot iff 'core'."""
    y, w, s, p = _round_stats(sub, outcome)
    if len(y) < MIN_N:
        return None
    F = _wcdf(y, w)
    if klass_cr == "core":
        return F, _design_boot(y, w, s, p, rng)
    B = _naive_boot(y, w, rng)
    if DEFF_EXTENDED != 1.0:
        B = F[None, :] + np.sqrt(DEFF_EXTENDED) * (B - F[None, :])
    return F, B


def audit_country_long(csub, usable, klass, c, outcome, rng):
    """Certification at three units over the country's full trajectory."""
    rounds = sorted(usable)
    cells = {}
    for r in rounds:
        out = _boot_for(csub[csub.essround == r], outcome, klass.get((c, r)), rng)
        if out is not None:
            cells[r] = out
    rounds = sorted(cells)
    pairs = [(a, b) for a, b in zip(rounds[:-1], rounds[1:]) if b == a + 1]
    if not pairs:
        return None
    recs, hats, boots = [], [], []
    for r0, r1 in pairs:
        F0, B0 = cells[r0]; F1, B1 = cells[r1]
        dhat, dboot = F1 - F0, B1 - B0
        hats.append(dhat); boots.append(dboot)
        c1 = certify_decline_differences(dhat[None], dboot[:, None], ALPHA, CORE_T)
        recs.append(dict(r_from=r0, r_to=r1, pair_plugin=c1["plugin"],
                         pair_da=c1["design_aware"]))
    H = np.array(hats)
    Bd = np.moveaxis(np.array(boots), 1, 0)
    persist = certify_decline_differences(H, Bd, ALPHA, CORE_T)

    F0, B0 = cells[rounds[0]]; F1, B1 = cells[rounds[-1]]
    net = certify_decline_differences((F1 - F0)[None], (B1 - B0)[:, None],
                                      ALPHA, CORE_T)
    return dict(
        n_rounds=len(rounds), r_first=rounds[0], r_last=rounds[-1],
        n_pairs=len(recs),
        n_pairs_weightsonly=sum(1 for r0, r1 in pairs
                                if klass.get((c, r0)) != "core"
                                or klass.get((c, r1)) != "core"),
        pair_plugin=sum(r["pair_plugin"] for r in recs),
        pair_da=sum(r["pair_da"] for r in recs),
        any_plugin=any(r["pair_plugin"] for r in recs),
        any_da=any(r["pair_da"] for r in recs),
        net_plugin=net["plugin"], net_da=net["design_aware"],
        persist_plugin=persist["plugin"], persist_da=persist["design_aware"],
        _H=H, _Bd=Bd)


def main():
    df = load()
    kl = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    rows, stash = [], {}
    for outcome in OUTCOMES:
        for c, csub in df.groupby("cntry", observed=True):
            usable = [r for r in sorted(csub.essround.unique())
                      if kl.get((c, r)) in ("core", "extended")]
            if len(usable) < 2:
                continue
            rng = np.random.default_rng(det_seed("e36", outcome, c))
            res = audit_country_long(csub, usable, kl, c, outcome, rng)
            if res:
                stash[(outcome, c)] = (res.pop("_H"), res.pop("_Bd"))
                rows.append(dict(outcome=outcome, cntry=c, **res))
    cty = pd.DataFrame(rows)

    # Bonferroni across the countries actually analyzed, per outcome
    bonf = []
    for outcome in OUTCOMES:
        Kc = (cty.outcome == outcome).sum()
        for _, r in cty[cty.outcome == outcome].iterrows():
            H, Bd = stash[(outcome, r.cntry)]
            pb = certify_decline_differences(H, Bd, ALPHA / max(Kc, 1), CORE_T)
            bonf.append(pb["design_aware"])
    cty["persist_da_bonf"] = bonf

    os.makedirs("results", exist_ok=True)
    cty.to_csv("results/ess_long_window.csv", index=False)

    print("ESS long-window audit — rounds 1–11 (2002–2024), α=0.10")
    print("(rounds 1–8 weights-only bootstrap; understated variance errs inclusive)\n")
    for outcome in OUTCOMES:
        p = cty[cty.outcome == outcome]
        print(f"{outcome}: {len(p)} countries, {int(p.n_pairs.sum())} pairs "
              f"({int(p.n_pairs_weightsonly.sum())} with a weights-only side)")
        print(f"  any-pair  plug {int(p.any_plugin.sum()):2d} / DA {int(p.any_da.sum()):2d}")
        print(f"  net span  plug {int(p.net_plugin.sum()):2d} / DA {int(p.net_da.sum()):2d}"
              f"   -> {sorted(p.cntry[p.net_da])}")
        print(f"  persistent plug {int(p.persist_plugin.sum()):2d} / DA "
              f"{int(p.persist_da.sum()):2d}   -> {sorted(p.cntry[p.persist_da])}")
        print(f"  persistent+Bonf DA {int(p.persist_da_bonf.sum()):2d}"
              f"   -> {sorted(p.cntry[p.persist_da_bonf])}")
        med = p.n_pairs.median()
        print(f"  pairs per country: median {med:.0f}, max {int(p.n_pairs.max())}\n")


if __name__ == "__main__":
    main()
