"""E35 — V-Dem cross-tabs for the WVS certified core (public data; descriptive).

Two questions, both suggested by referee triage (R3-M8) and HANDOFF items C12/C14:

1. Regime type. Cross-tab the deconsolidation certification sets against the
   V-Dem Regimes-of-the-World classification (v2x_regime, 2019): how much of the
   "deconsolidation" geography is electoral/closed autocracy, where falling stated
   support reads as autocratic legitimation rather than democratic deconsolidation?

2. Predictive validity. Among countries screened on >=2 items, does membership in
   the persistent certified core anticipate subsequent V-Dem electoral-democracy
   decline better than the marginal (plug-in any-pair) flag? Outcome: change in
   v2x_polyarchy over 2022->latest (strictly after the WVS wave-7 window) and
   2017->latest. N is small; we report medians, proportions declining, and exact
   tests (Fisher / Mann-Whitney), as description rather than regression.

Inputs:  results/wvs_country_flags.csv (E34), results/certified_core.csv (E30),
         V-Dem country-year (path via VDEM_PATH env, default /root/pa_data/vdem.RData).
Outputs: results/vdem_regime_crosstab.csv, results/vdem_predictive.csv
Run:     python -m pcb.experiments.e35_vdem_crosstab
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

VDEM = os.environ.get("VDEM_PATH", "/root/pa_data/vdem.RData")
REGIME = {0: "closed autocracy", 1: "electoral autocracy",
          2: "electoral democracy", 3: "liberal democracy"}


def _vdem():
    import pyreadr
    df = pyreadr.read_r(VDEM)["vdem"]
    return df[["country_name", "country_text_id", "year",
               "v2x_regime", "v2x_polyarchy"]]


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
    core = pd.read_csv("results/certified_core.csv")
    vd = _vdem()

    per = (flags.groupby("iso")
           .agg(n_items=("item", "size"),
                n_persist=("persist", "sum"),
                n_persist_plugin=("persist_plugin", "sum"),
                n_anypair_plugin=("anypair_plugin", "sum"),
                n_net=("net", "sum"))
           .reset_index())
    a3 = _iso_num_to_alpha3(per["iso"])
    per["iso3"] = per["iso"].map(a3)
    name = core.set_index("iso")["country"]
    per["country"] = per["iso"].map(name)

    # --- 1. regime type of the certification sets (2019, last pre-wave-7-end year) --
    reg = vd[vd["year"] == 2019].set_index("country_text_id")["v2x_regime"]
    per["regime_2019"] = per["iso3"].map(reg).map(lambda x: REGIME.get(int(x)) if pd.notna(x) else None)
    per["in_core"] = per["n_persist"] >= 2
    ct = (per[per["n_persist"] >= 1]
          .assign(set_=np.where(per.loc[per["n_persist"] >= 1].index.isin(
              per[per["in_core"]].index), "core (>=2 items)", "single-item"))
          .groupby(["set_", "regime_2019"], observed=True).size().unstack(fill_value=0))
    ct.to_csv("results/vdem_regime_crosstab.csv")
    print("Regime type (2019) of persistent-certified countries:")
    print(ct.to_string(), "\n")
    core13 = per[per["in_core"]].sort_values("n_persist", ascending=False)
    print(core13[["country", "regime_2019", "n_persist"]].to_string(index=False), "\n")

    # --- 2. predictive validity on the >=2-item screened universe -----------------
    uni = per[per["n_items"] >= 2].dropna(subset=["iso3"]).copy()
    poly = vd.pivot_table(index="country_text_id", columns="year",
                          values="v2x_polyarchy", aggfunc="first")
    latest = int(max(y for y in poly.columns if poly[y].notna().sum() > 100))
    for y0 in (2022, 2017):
        uni[f"d{y0}"] = uni["iso3"].map(poly[latest] - poly[y0])
    rows = []
    groups = {
        "certified core (>=2 persist)": uni["in_core"],
        "marginal >=2 (anypair plug-in), not core": (uni["n_anypair_plugin"] >= 2) & ~uni["in_core"],
        "not flagged (anypair plug-in <2)": uni["n_anypair_plugin"] < 2,
    }
    from scipy import stats
    for label, m in groups.items():
        g = uni[m]
        for y0 in (2022, 2017):
            d = g[f"d{y0}"].dropna()
            rows.append(dict(group=label, window=f"{y0}->{latest}", n=len(d),
                             median_dpoly=round(float(d.median()), 4),
                             prop_declining=round(float((d < 0).mean()), 3)))
    res = pd.DataFrame(rows)
    # exact tests: core vs marginal-not-core, primary window 2022->latest
    a = uni[groups["certified core (>=2 persist)"]]["d2022"].dropna()
    b = uni[groups["marginal >=2 (anypair plug-in), not core"]]["d2022"].dropna()
    mw = stats.mannwhitneyu(a, b, alternative="less")
    tab = np.array([[(a < 0).sum(), (a >= 0).sum()], [(b < 0).sum(), (b >= 0).sum()]])
    fi = stats.fisher_exact(tab, alternative="greater")
    res.attrs = {}
    res.to_csv("results/vdem_predictive.csv", index=False)
    print(res.to_string(index=False))
    print(f"\ncore vs marginal-not-core, d(2022->{latest}):"
          f" Mann-Whitney one-sided p={mw.pvalue:.3f};"
          f" Fisher (declining) one-sided p={fi.pvalue:.3f}"
          f" | medians {a.median():.4f} vs {b.median():.4f}")
    with open("results/vdem_predictive_tests.txt", "w") as f:
        f.write(f"universe: screened on >=2 items, n={len(uni)}\n"
                f"latest V-Dem year: {latest}\n"
                f"core n={len(a)}, marginal-not-core n={len(b)}\n"
                f"MannWhitney(one-sided, core more negative) p={mw.pvalue:.4f}\n"
                f"Fisher(one-sided, core more often declining) p={fi.pvalue:.4f}\n"
                f"median d2022: core {a.median():.4f}, marginal {b.median():.4f}\n")


if __name__ == "__main__":
    main()
