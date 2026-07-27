"""ESS schema audit — step 1 of the political-attitudes (DA-PCB) layer.

Input: the ESS Data Wizard subset at data/ess/Datafile-subset.dta (integrated
rounds, all countries; licensed microdata, never committed). Output:
  results/ess_audit.csv       one row per country x round with n, outcome
                              completeness, weight and design-variable coverage
  data/ess/core_audit.parquet the audit columns cached for the panel builder

Sample classification per country-round (drives the core/extended split):
  core     : outcomes + anweight + psu + stratum usable (full DA-PCB)
  extended : outcomes + a usable weight, but no/degenerate design variables
             (plug-in PCB + weight-only sensitivity)
  excluded : primary outcome (trstprl) under MIN_VALID completeness.

Run:  python -m pcb.data.audit_ess
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

DTA = "data/ess/Datafile-subset.dta"
CACHE = "data/ess/core_audit.parquet"
OUT = "results/ess_audit.csv"
COLS = ["essround", "cntry", "trstprl", "trstplt", "trstprt", "stfdem",
        "ppltrst", "dweight", "pspwght", "pweight", "anweight",
        "psu", "stratum", "prob"]
MIN_VALID = 0.80          # minimum share of valid primary-outcome responses


def load(columns=COLS) -> pd.DataFrame:
    if os.path.exists(CACHE):
        df = pd.read_parquet(CACHE)
        if set(columns) <= set(df.columns):
            return df[list(columns)]
    import pyreadstat
    df, _ = pyreadstat.read_dta(DTA, usecols=list(columns))
    df.to_parquet(CACHE)
    return df


def audit(df: pd.DataFrame) -> pd.DataFrame:
    def valid_share(s):          # ESS 0-10 items; pyreadstat maps refusals to NaN
        return s.notna().mean()

    g = df.groupby(["cntry", "essround"], observed=True)
    a = g.agg(
        n=("cntry", "size"),
        trstprl=("trstprl", valid_share),
        stfdem=("stfdem", valid_share),
        anweight=("anweight", valid_share),
        pspwght=("pspwght", valid_share),
        dweight=("dweight", valid_share),
        psu=("psu", valid_share),
        stratum=("stratum", valid_share),
        prob=("prob", valid_share),
        n_psu=("psu", "nunique"),
        n_strata=("stratum", "nunique"),
    ).reset_index()

    # a design layer is usable when nearly all rows carry it and it is
    # non-degenerate (more than a handful of PSUs to bootstrap over)
    design_ok = (a.psu > 0.95) & (a.stratum > 0.95) & (a.n_psu >= 20)
    weight_ok = (a.anweight > 0.95) | (a.pspwght > 0.95)
    outcome_ok = a.trstprl >= MIN_VALID
    a["sample"] = np.where(~outcome_ok, "excluded",
                           np.where(design_ok & weight_ok, "core",
                                    np.where(weight_ok, "extended",
                                             "excluded")))
    return a


def main():
    df = load()
    a = audit(df)
    os.makedirs("results", exist_ok=True)
    a.to_csv(OUT, index=False)

    print(f"country-rounds: {len(a)}   countries: {a.cntry.nunique()}   "
          f"rounds: {sorted(a.essround.unique())}")
    print(a["sample"].value_counts().to_string())
    print("\nby round:")
    print(a.pivot_table(index="essround", columns="sample", values="cntry",
                        aggfunc="count", fill_value=0).to_string())
    bad = a[a["sample"] == "excluded"]
    if len(bad):
        print("\nexcluded country-rounds:")
        print(bad[["cntry", "essround", "n", "trstprl", "anweight",
                   "psu"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
