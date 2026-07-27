"""E46 — window- and item-matched comparison with the Claassen latent panel.

E37 compared our certified core against Claassen's corrected support-for-
democracy series and found them nearly independent. But that comparison is
confounded two ways, as its own decomposition admitted: his corrected series
ends in 2017 while WVS wave 7 (fieldwork 2017-2022) drives several of our
certifications, and his latent construct excludes institutional-confidence
items that drive several of our core memberships. Divergence produced by
non-overlapping data is not information added by our method.

This experiment removes both confounds:

  WINDOW-MATCHED : recertify the five-item hierarchy on WVS/EVS waves whose
                   fieldwork ends by 2017, then compare.
  ITEM-MATCHED   : restrict the comparison to the four support-for-democracy
                   items (imp_dem, rej_leader, rej_army, sup_demsys), dropping
                   confid_parl, which is institutional trust -- an item family
                   Claassen deliberately excludes.

Residual divergence under the matched comparison isolates the pooling/smoothing
cost, which is the substantively interesting quantity.

Output: results/claassen_window_matched.csv
Run:    python -m pcb.experiments.e46_claassen_window_matched   (~1-2 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

import pcb.experiments.e26_wvs_deconsolidation as e26
from pcb.data.audit_wvs import load, ITEMS

YEAR_CUT = 2017
SUPDEM_ITEMS = ("imp_dem", "rej_leader", "rej_army", "sup_demsys")
CLAASSEN = os.environ.get("CLAASSEN_PATH",
                          "/root/pa_data/Support_democracy_ajps_correct.csv")


def _iso_num_to_alpha3(nums):
    import pycountry
    out = {}
    for n in nums:
        c = pycountry.countries.get(numeric=f"{int(n):03d}")
        out[int(n)] = c.alpha_3 if c else None
    return out


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    df = df[df["_w"].notna() & (df["_w"] > 0)]
    dfw = df[df["S020"] <= YEAR_CUT]
    print(f"window-matched sample: {len(dfw):,} of {len(df):,} respondents "
          f"(fieldwork <= {YEAR_CUT})\n")

    rows = []
    for item in ITEMS:
        flags, K = e26._hierarchy(dfw, item)
        for c, r in flags.items():
            rows.append(dict(item=item, iso=c, persist=r["persist"],
                             anypair_plugin=r["anypair_pi"]))
        print(f"{item:12s} K={K:3d}  persistent {sum(r['persist'] for r in flags.values())}")
    fl = pd.DataFrame(rows)

    per = (fl.groupby("iso")
           .agg(n_items=("item", "size"), n_persist=("persist", "sum"))
           .reset_index())
    per_sd = (fl[fl.item.isin(SUPDEM_ITEMS)].groupby("iso")
              .agg(n_items_sd=("item", "size"), n_persist_sd=("persist", "sum"))
              .reset_index())
    per = per.merge(per_sd, on="iso", how="left").fillna(0)
    per["iso3"] = per["iso"].map(_iso_num_to_alpha3(per["iso"]))
    per["in_core"] = per.n_persist >= 2
    per["in_core_supdem"] = per.n_persist_sd >= 2

    cl = pd.read_csv(CLAASSEN)[["Country", "Year", "ISO_code", "SupDem_trim"]]
    s = cl.dropna(subset=["SupDem_trim"])
    s = s[(s.Year >= 2006) & (s.Year <= YEAR_CUT)]
    tr = s.sort_values("Year").groupby("ISO_code")["SupDem_trim"].agg(
        lambda v: v.iloc[-1] - v.iloc[0])
    per["d_supdem"] = per["iso3"].map(tr)
    m = per[per.n_items >= 2].dropna(subset=["d_supdem"]).copy()
    m["claassen_declining"] = m.d_supdem < 0
    m.to_csv("results/claassen_window_matched.csv", index=False)

    from scipy import stats
    print(f"\nwindow-matched universe: {len(m)} countries with >=2 screened items "
          f"and a Claassen series over 2006-{YEAR_CUT}")
    for label, col in (("all five items", "in_core"),
                       ("support-for-democracy items only", "in_core_supdem")):
        ct = pd.crosstab(m[col], m["claassen_declining"])
        core_rate = m.loc[m[col], "claassen_declining"].mean()
        rest_rate = m.loc[~m[col], "claassen_declining"].mean()
        tab = [[int(((m[col]) & m.claassen_declining).sum()),
                int(((m[col]) & ~m.claassen_declining).sum())],
               [int(((~m[col]) & m.claassen_declining).sum()),
                int(((~m[col]) & ~m.claassen_declining).sum())]]
        p = stats.fisher_exact(np.array(tab), alternative="greater").pvalue
        print(f"\n-- {label} --")
        print(ct.to_string())
        print(f"   core declining in his series: {core_rate:.2f} "
              f"(n={int(m[col].sum())}) vs non-core {rest_rate:.2f} "
              f"(n={int((~m[col]).sum())}); Fisher one-sided p={p:.3f}")


if __name__ == "__main__":
    main()
