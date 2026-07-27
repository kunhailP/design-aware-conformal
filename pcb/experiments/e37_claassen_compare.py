"""E37 — same-items comparison with Claassen's latent support-for-democracy panel.

Claassen's country-year support estimates (2019 PA; 2020 AJPS, corrected series
per Tai-Hu-Solt 2024) pool the same item families our WVS/EVS reanalysis
certifies item-by-item (strongman, army rule, importance/suitability of
democracy). His object is a smooth latent level with model-based uncertainty;
ours is a finite-sample per-item certification of persistent distribution-wide
decline. This experiment asks where the two objects agree and disagree.

For every country in the >=2-item screened universe (E34): his corrected series
SupDem_trim -> change over 2006->last available (his panel ends ~2020), vs our
certified-core membership. Cross-tab + named disagreement lists.

Inputs:  results/wvs_country_flags.csv, results/certified_core.csv,
         Claassen AJPS-corrected panel (path via CLAASSEN_PATH env, default
         /root/pa_data/Support_democracy_ajps_correct.csv; public, Harvard
         Dataverse doi:10.7910/DVN/HWLW0J).
Output:  results/claassen_compare.csv
Run:     python -m pcb.experiments.e37_claassen_compare
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

PATH = os.environ.get("CLAASSEN_PATH",
                      "/root/pa_data/Support_democracy_ajps_correct.csv")
Y0 = 2006          # first year of the modern WVS deconsolidation window (wave 5)


def _iso_num_to_alpha3(nums):
    import pycountry
    out = {}
    for n in nums:
        c = pycountry.countries.get(numeric=f"{int(n):03d}")
        out[int(n)] = c.alpha_3 if c else None
    return out


def main():
    os.makedirs("results", exist_ok=True)
    flags = pd.read_csv("results/wvs_country_flags.csv")
    core = pd.read_csv("results/certified_core.csv").set_index("iso")
    cl = pd.read_csv(PATH)[["Country", "Year", "ISO_code", "SupDem_trim"]]

    per = (flags.groupby("iso")
           .agg(n_items=("item", "size"), n_persist=("persist", "sum"),
                n_anypair_plugin=("anypair_plugin", "sum"))
           .reset_index())
    per = per[per.n_items >= 2].copy()
    per["iso3"] = per["iso"].map(_iso_num_to_alpha3(per["iso"]))
    per["country"] = per["iso"].map(core["country"])
    per["in_core"] = per["n_persist"] >= 2

    s = cl.dropna(subset=["SupDem_trim"])
    g = s[s.Year >= Y0].groupby("ISO_code")
    trend = g.apply(lambda d: pd.Series(
        dict(y_first=d.Year.min(), y_last=d.Year.max(),
             d_supdem=d.sort_values("Year").SupDem_trim.iloc[-1]
                      - d.sort_values("Year").SupDem_trim.iloc[0])),
        include_groups=False)
    m = per.merge(trend, left_on="iso3", right_index=True, how="inner")
    m["claassen_declining"] = m["d_supdem"] < 0

    ct = pd.crosstab(m["in_core"].map({True: "certified core", False: "not core"}),
                     m["claassen_declining"].map({True: "SupDem falling",
                                                  False: "SupDem flat/rising"}))
    print(f"Universe: {len(m)} of {len(per)} screened countries with a Claassen "
          f"series over {Y0}->{int(m.y_last.max())}\n")
    print(ct.to_string(), "\n")
    agree_core = m[m.in_core & m.claassen_declining]
    dis_core = m[m.in_core & ~m.claassen_declining]
    dis_marg = m[~m.in_core & (m.n_anypair_plugin >= 2) & m.claassen_declining]
    print("core & Claassen-declining (agree):",
          sorted(agree_core.country.dropna()))
    print("core but Claassen flat/rising (his pooling vs our certification):",
          sorted(dis_core.country.dropna()))
    print(f"marginal>=2 (not core) & Claassen-declining: {len(dis_marg)} countries"
          f" — his model and the marginal reading move together; the persistent"
          f" object is the stricter filter")
    m.to_csv("results/claassen_compare.csv", index=False)
    print("\nwrote results/claassen_compare.csv")


if __name__ == "__main__":
    main()
