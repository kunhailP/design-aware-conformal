"""LAPOP AmericasBarometer grand-merge schema audit (Gate 5D external validation).

Audit ONLY — classifies each (country, year) into core / extended / excluded by
design-metadata completeness, records outcome availability, scale, and weight
variability. No certification analysis here (that waits on the LAPOP
preregistration). Mirrors `audit_ess.py`.

Design layer (per LAPOP documentation): WT (single country-year weight),
WEIGHT1500 (multi-country-year), STRATA (study strata), UPM (primary sampling
unit). Outcomes: b13 trust in legislature (1–7, high=trust, ESS-aligned), pn4
satisfaction with democracy, ing4 support for democracy.

Run:  python -m pcb.data.audit_lapop
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd
import pyreadstat

RAW = ("data/lapop/raw/"
       "Grand_Merge_2004-2023_LAPOP_AmericasBarometer_v1.0_FREE.dta")
COLS = ["pais", "wave", "year", "wt", "weight1500", "upm", "strata",
        "estratopri", "b13", "pn4", "ing4"]
OUTCOMES = ("b13", "pn4", "ing4")
MIN_NPSU = 20            # design_ok needs enough PSUs for a stable bootstrap


def load(cols=COLS):
    df, meta = pyreadstat.read_dta(RAW, usecols=cols, encoding="LATIN1")
    # country labels
    vl = meta.variable_value_labels.get("pais", {})
    df["country"] = df["pais"].map(vl).fillna(df["pais"].astype("Int64").astype(str))
    return df, meta


def _valid(s):
    """LAPOP missing = negative codes; keep the substantive scale only."""
    return s.where(s >= 0)


def audit(df):
    rows = []
    for (pais, year), g in df.groupby(["pais", "year"], observed=True):
        rec = dict(pais=int(pais),
                   country=g["country"].iloc[0], year=int(year), n=len(g))
        for o in OUTCOMES:
            v = _valid(g[o])
            rec[f"{o}_valid"] = float(v.notna().mean())
            rec[f"{o}_min"] = float(v.min()) if v.notna().any() else np.nan
            rec[f"{o}_max"] = float(v.max()) if v.notna().any() else np.nan
        wt = _valid(g["wt"])
        rec["has_wt"] = bool(wt.notna().any())
        rec["has_w1500"] = bool(_valid(g["weight1500"]).notna().any())
        rec["wt_cv"] = float(np.std(wt.dropna()) / np.mean(wt.dropna())) \
            if wt.notna().any() and wt.mean() != 0 else np.nan
        upm = g["upm"].where(g["upm"] >= 0)
        strata = g["strata"].where(g["strata"] >= 0)
        rec["n_upm"] = int(upm.nunique())
        rec["n_strata"] = int(strata.nunique())
        # singleton strata: strata carrying only one PSU (no design variance)
        if upm.notna().any() and strata.notna().any():
            per = g.dropna(subset=["upm", "strata"]).groupby("strata")["upm"].nunique()
            rec["singleton_strata"] = int((per <= 1).sum())
        else:
            rec["singleton_strata"] = np.nan
        rec["design_ok"] = bool(rec["n_upm"] >= MIN_NPSU and rec["n_strata"] >= 1
                                and rec["has_wt"])
        rows.append(rec)
    a = pd.DataFrame(rows)

    # sample classification: core needs a usable outcome + weight + design layer
    has_out = (a.b13_valid >= 0.5) | (a.pn4_valid >= 0.5)
    a["sample"] = np.where(has_out & a.design_ok, "core",
                           np.where(has_out & a.has_wt, "extended", "excluded"))
    return a


def main():
    os.makedirs("results", exist_ok=True)
    df, meta = load()
    a = audit(df)
    a.to_csv("results/lapop_country_round_audit.csv", index=False)

    # design-completeness summary by round/year
    comp = a.groupby("year").agg(
        cells=("pais", "size"),
        core=("sample", lambda s: (s == "core").sum()),
        extended=("sample", lambda s: (s == "extended").sum()),
        with_upm=("n_upm", lambda s: (s >= MIN_NPSU).sum()),
        med_npsu=("n_upm", "median"), med_nstrata=("n_strata", "median"),
        med_wtcv=("wt_cv", "median")).reset_index()
    comp.to_csv("results/lapop_design_completeness.csv", index=False)

    print(f"LAPOP grand merge: {len(df)} rows, {a.pais.nunique()} countries, "
          f"{a.year.nunique()} survey years, {len(a)} country-year cells\n")
    print("sample classification:")
    print(a["sample"].value_counts().to_string())

    print("\ndesign completeness by survey year:")
    print(comp.to_string(index=False))

    # repeated-country structure on the CORE sample (design-valid)
    core = a[a["sample"] == "core"]
    rounds_per = core.groupby("pais").year.nunique()
    print(f"\nCORE sample: {len(core)} country-years, {core.pais.nunique()} "
          f"countries; {(rounds_per >= 2).sum()} countries with >=2 core years "
          f"(adjacency possible)")

    # outcome scale/direction check
    print("\noutcome scales (min..max over valid, core cells):")
    for o in OUTCOMES:
        v = core[core[f"{o}_valid"] >= 0.5]
        if len(v):
            print(f"  {o}: {v[f'{o}_min'].min():.0f}..{v[f'{o}_max'].max():.0f} "
                  f"| available in {len(v)}/{len(core)} core cells")


if __name__ == "__main__":
    main()
