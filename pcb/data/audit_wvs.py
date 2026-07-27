"""WVS/EVS Trends loader for the deconsolidation reanalysis (E26).

Licensed microdata (never committed): data/wvs/data_pa/Trends_VS_1981_2022_Stata_v4_1.dta
(442,473 rows, WVS/EVS integrated trends, 1981–2022). We load only the Foa–Mounk
democratic-support battery + country/wave/weight/age, recode WVS negative missing codes
to NaN, and recode each item to a common **pro-democratic orientation** (higher = more
supportive of liberal democracy) so a single "persistent decline" = deconsolidation.

No PSU/stratum in WVS (WVS_SCHEMA_AUDIT): the survey-aware sampling variance is a
weighted respondent bootstrap (weights-only), not a stratified-PSU design bootstrap.

Run:  python -m pcb.data.audit_wvs
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

DTA = "data/wvs/data_pa/Trends_VS_1981_2022_Stata_v4_1.dta"
CACHE = "data/wvs/trends_deconsolidation.parquet"

# raw items (WVS variable → orientation). We recode each to "pro-democratic": higher =
# more supportive of liberal democracy, so deconsolidation is a persistent DECLINE.
#   E235 importance of democracy 1..10 (high already = important)        → keep
#   E114 "strong leader" 1..4 (1=very good … 4=very bad)                 → reverse (5−x): high = reject strongman
#   E116 "army rule"     1..4 (1=very good … 4=very bad)                 → reverse: high = reject army rule
#   E117 "democratic system" 1..4 (1=very good … 4=very bad)            → keep-reverse to high=support? 1=very good FOR democracy → keep as 5−x so high=support
#   E069_07 confidence in parliament 1..4 (1=a great deal … 4=none)     → reverse: high = more confidence
RAW = ["S003", "S002VS", "S020", "S017", "X003",
       "E235", "E114", "E116", "E117", "E069_07"]
# recoded pro-democratic items and their integer support (max category)
ITEMS = {
    "imp_dem":   ("E235", 10, "importance of democracy (1–10, high=essential)"),
    "rej_leader": ("E114", 4, "reject 'strong leader' (recoded, high=reject strongman)"),
    "rej_army":  ("E116", 4, "reject army rule (recoded, high=reject)"),
    "sup_demsys": ("E117", 4, "support democratic system (recoded, high=support)"),
    "confid_parl": ("E069_07", 4, "confidence in parliament (recoded, high=confidence)"),
}


def _load_raw() -> pd.DataFrame:
    if os.path.exists(CACHE):
        return pd.read_parquet(CACHE)
    import pyreadstat
    df, _ = pyreadstat.read_dta(DTA, usecols=RAW, encoding="latin1")
    for c in RAW:
        df.loc[df[c] < 0, c] = np.nan            # WVS negatives = missing/NA
    df.to_parquet(CACHE)
    return df


def load() -> pd.DataFrame:
    """Return a frame with country S003, wave S002VS, year S020, weight _w, age X003,
    and the five pro-democratic recoded items (higher = more democratic)."""
    df = _load_raw().copy()
    df["_w"] = df["S017"].where(df["S017"] > 0)
    # E235 already high=essential; reverse the four 1..4 "1=very good" items so high=pro-dem
    df["imp_dem"] = df["E235"]
    for name in ("rej_leader", "rej_army", "sup_demsys", "confid_parl"):
        raw = ITEMS[name][0]
        df[name] = 5 - df[raw]                    # 1..4 → 4..1 (high = pro-democratic)
    return df


def audit(df: pd.DataFrame, min_n: int = 400) -> pd.DataFrame:
    """Per (country, wave) valid-n for each item and the ≥min_n / ≥2-wave counts."""
    rows = []
    for name in ITEMS:
        g = df.groupby(["S003", "S002VS"])[name].apply(lambda s: s.notna().sum())
        cells = g[g >= min_n]
        by_c = cells.reset_index().groupby("S003").size()
        rows.append(dict(item=name, desc=ITEMS[name][2], cells=len(cells),
                         countries=cells.index.get_level_values(0).nunique(),
                         countries_2waves=int((by_c >= 2).sum())))
    return pd.DataFrame(rows)


def main():
    df = load()
    a = audit(df)
    os.makedirs("results", exist_ok=True)
    a.to_csv("results/wvs_deconsolidation_audit.csv", index=False)
    print(f"WVS/EVS trends: {len(df)} rows, {df.S003.nunique()} countries, "
          f"waves {sorted(df.S002VS.dropna().unique().astype(int))}\n")
    print(a.to_string(index=False))


if __name__ == "__main__":
    main()
