"""Assemble data/ess/Datafile-subset.dta from the per-round API downloads.

The loaders (`pcb.data.audit_ess`) read one Stata file, the ESS Data Wizard
subset described in docs/DATA_SOURCES.md. This script builds the equivalent
file from the integrated-file Parquets fetched by scripts/fetch_ess_api.py:
rounds 1-11 stacked in round order (round 10 = face-to-face file followed by
the self-completion file), restricted to the Wizard variable list plus `idno`
(SDDF merge key) and `mode` (the e40 mode audit). Variables absent in a round
(e.g. `trstprt` in round 1, `psu/stratum/prob` before round 9) are left
missing, exactly as the Wizard leaves them.

Check: per country x round counts must equal results/ess_audit.csv, and
e13 must reproduce results/ess_country_certification.csv bit-identically
(the bootstrap draws depend on within-country row order, which the
integrated files fix).

Usage:  python scripts/build_ess_subset.py
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyreadstat

INTEGRATED = ["ess1e06_7", "ess2e03_6", "ess3e03_7", "ess4e04_6", "ess5e03_6",
              "ess6e02_7", "ess7e02_3", "ess8e02_3", "ess9e03_3", "ess10e03_3",
              "ess10sce03_2", "ess11e04_2"]      # keep in sync with fetch_ess_api.py
OUT_DIR = "data/ess/api"

COLS = ["essround", "cntry", "idno", "trstprl", "trstplt", "trstprt", "stfdem",
        "ppltrst", "dweight", "pspwght", "pweight", "anweight",
        "psu", "stratum", "prob", "mode"]
OUT = "data/ess/Datafile-subset.dta"


def main():
    parts = []
    for doi in INTEGRATED:
        path = os.path.join(OUT_DIR, f"{doi}.parquet")
        have = [c for c in COLS if c in pq.read_schema(path).names]
        d = pq.read_table(path, columns=have).to_pandas()
        for c in COLS:
            if c not in d.columns:
                d[c] = np.nan
        parts.append(d[COLS])
        print(f"{doi:14s} rows {len(d):6d}  missing {[c for c in COLS if c not in have]}")
    df = pd.concat(parts, ignore_index=True)
    df["cntry"] = df["cntry"].astype(str)
    for c in COLS:
        if c not in ("cntry",):
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")
    # The API Parquets carry the ESS missing codes as values; the Stata
    # integrated files carry them as user-defined missings, which pyreadstat
    # reads as NaN (the loaders rely on that). Recode to match: 77 refusal,
    # 88 don't know, 99 no answer on the 0-10 items; 9 "not available" on mode.
    for c in ["trstprl", "trstplt", "trstprt", "stfdem", "ppltrst"]:
        df.loc[df[c].isin([77, 88, 99]), c] = np.nan
    df.loc[df["mode"].isin([9]), "mode"] = np.nan
    # Stata integer types, so the loaders read these back as integers (the
    # Wizard file stores them that way; keeps CSV formatting of round numbers
    # identical to the committed results).
    df["essround"] = df["essround"].astype("int32")
    df["idno"] = df["idno"].astype("int32")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pyreadstat.write_dta(df, OUT)
    print(f"wrote {OUT}: {len(df):,} rows, {len(COLS)} columns")

    audit = "results/ess_audit.csv"
    if os.path.exists(audit):
        a = pd.read_csv(audit).set_index(["cntry", "essround"])["n"]
        n = df.groupby(["cntry", "essround"]).size()
        n.index = n.index.set_levels(n.index.levels[1].astype(int), level=1)
        common = a.index.intersection(n.index)
        bad = (a.loc[common] != n.loc[common]).sum()
        print(f"country-rounds in audit: {len(a)}; matched: {len(common)}; "
              f"count mismatches: {int(bad)}")


if __name__ == "__main__":
    main()
