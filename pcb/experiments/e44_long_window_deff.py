"""E44 — design-effect sensitivity of the LONG-WINDOW counts (paper §7).

The long window (E36) uses the stratified-PSU design bootstrap for rounds 9-11
and a weights-only respondent bootstrap for rounds 1-8, where the integrated
file ships no PSU/stratum identifiers. Understated design variance can only
*inflate* certified counts -- which protects the "zero persistent" result but
is a liability for the "net erosion in nine" result, whose showcase countries
(Israel, Italy) sit on weights-only spans.

This is the E39 medicine applied to E36: rerun the whole long-window hierarchy
with the weights-only cells' bootstrap variance inflated by deff in
{1.5, 2.0} -- ESS design effects on attitudinal items are commonly 1.5-2.5 --
and report which net certifications survive. Rounds 9-11 keep their real design
bootstrap throughout (they need no inflation).

Output: results/ess_long_window_deff.csv (per country x deff)
        results/ess_long_window_deff_summary.csv (counts by rung x deff)
Run:    python -m pcb.experiments.e44_long_window_deff   (~1 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import audit, load
import pcb.experiments.e36_ess_long_window as e36

DEFFS = (1.0, 1.5, 2.0)


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    kl = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    rows, summary = [], []
    for deff in DEFFS:
        e36.DEFF_EXTENDED = deff
        for outcome in e36.OUTCOMES:
            cnt = dict(any_da=0, net_da=0, persist_da=0, n=0)
            for c, csub in df.groupby("cntry", observed=True):
                usable = [r for r in sorted(csub.essround.unique())
                          if kl.get((c, r)) in ("core", "extended")]
                if len(usable) < 2:
                    continue
                rng = np.random.default_rng(det_seed("e36", outcome, c))
                res = e36.audit_country_long(csub, usable, kl, c, outcome, rng)
                if not res:
                    continue
                res.pop("_H", None); res.pop("_Bd", None)
                rows.append(dict(deff=deff, outcome=outcome, cntry=c,
                                 n_pairs=res["n_pairs"],
                                 n_pairs_weightsonly=res["n_pairs_weightsonly"],
                                 any_da=res["any_da"], net_da=res["net_da"],
                                 persist_da=res["persist_da"]))
                cnt["n"] += 1
                for k in ("any_da", "net_da", "persist_da"):
                    cnt[k] += bool(res[k])
            summary.append(dict(deff=deff, outcome=outcome, **cnt))
            print(f"deff={deff}: {outcome:8s} K={cnt['n']:2d}  any {cnt['any_da']:2d}"
                  f"  net {cnt['net_da']:2d}  persist {cnt['persist_da']:2d}")
    e36.DEFF_EXTENDED = 1.0

    per = pd.DataFrame(rows); per.to_csv("results/ess_long_window_deff.csv", index=False)
    summ = pd.DataFrame(summary)
    summ.to_csv("results/ess_long_window_deff_summary.csv", index=False)

    print("\n=== survival of the net certifications ===")
    for outcome in e36.OUTCOMES:
        base = set(per[(per.deff == 1.0) & (per.outcome == outcome) & per.net_da].cntry)
        print(f"{outcome}: base (deff 1.0) net = {sorted(base)}")
        for deff in DEFFS[1:]:
            keep = set(per[(per.deff == deff) & (per.outcome == outcome)
                           & per.net_da].cntry)
            print(f"  deff {deff}: {len(keep)} survive -> {sorted(keep)}"
                  f"   dropped: {sorted(base - keep)}")
        robust = base.intersection(*[
            set(per[(per.deff == d) & (per.outcome == outcome) & per.net_da].cntry)
            for d in DEFFS[1:]])
        print(f"  deff-robust (survives 2.0): {sorted(robust)}")


if __name__ == "__main__":
    main()
