"""E30 — the certified core: where persistent deconsolidation actually lives.

Positive characterization of the countries that SURVIVE the persistent,
distribution-wide, weights-aware bar of the WVS Foa-Mounk reanalysis (E26).
Input is the tracked results/wvs_deconsolidation.csv (per-item certified
country lists); output is the co-certification structure:

  * items_certified per country (1..5) and which items;
  * the "certified core" = countries certified on >= 2 of the 5 battery items;
  * a descriptive regional/regime grouping of the core vs the single-item set.

Descriptive by design: the per-item certifications each carry their own
finite-sample guarantee (E26); the cross-item counts aggregate those binary
outcomes without any additional joint inference, and country-level item
availability differs (K = 59-77 per item), which the write-up discloses.

Run:  python -m pcb.experiments.e30_certified_core
Output: results/certified_core.csv (+ stdout summary)
"""
from __future__ import annotations
import os

import pandas as pd

SRC = "results/wvs_deconsolidation.csv"
OUT = "results/certified_core.csv"

ISO = {
    8: "Albania", 12: "Algeria", 31: "Azerbaijan", 70: "Bosnia and Herzegovina",
    100: "Bulgaria", 112: "Belarus", 124: "Canada", 196: "Cyprus",
    203: "Czechia", 218: "Ecuador", 231: "Ethiopia", 233: "Estonia",
    246: "Finland", 268: "Georgia", 288: "Ghana", 320: "Guatemala",
    344: "Hong Kong SAR", 348: "Hungary", 368: "Iraq", 398: "Kazakhstan",
    422: "Lebanon", 434: "Libya", 484: "Mexico", 578: "Norway",
    608: "Philippines", 616: "Poland", 646: "Rwanda", 703: "Slovakia",
    710: "South Africa", 752: "Sweden", 756: "Switzerland",
    780: "Trinidad and Tobago", 788: "Tunisia", 792: "Turkey",
    807: "North Macedonia", 818: "Egypt", 826: "United Kingdom",
    860: "Uzbekistan",
}

# descriptive grouping (labels, not covariates; used only for composition counts)
GROUP = {
    "post-communist": {8, 31, 70, 100, 112, 203, 233, 268, 348, 398, 616, 703,
                       807, 860},
    "MENA / Arab-Spring aftermath": {12, 368, 422, 434, 788, 818},
    "Latin America & Caribbean": {218, 320, 484, 780},
    "Sub-Saharan Africa": {231, 288, 646, 710},
    "Consolidated West": {124, 246, 578, 752, 756, 826},
    "Asia": {344, 608, 792},   # incl. Turkey with its Asia/Europe straddle
}


def build():
    df = pd.read_csv(SRC)
    items_by: dict[int, list[str]] = {}
    for _, r in df.iterrows():
        for code in map(int, str(r.persist_countries).split(";")):
            items_by.setdefault(code, []).append(r["item"])
    rows = []
    for code, items in items_by.items():
        grp = next((g for g, s in GROUP.items() if code in s), "other")
        rows.append(dict(iso=code, country=ISO.get(code, str(code)),
                         n_items=len(items), items=";".join(sorted(items)),
                         group=grp, core=len(items) >= 2))
    out = pd.DataFrame(rows).sort_values(["n_items", "country"],
                                         ascending=[False, True])
    return out


def main():
    out = build()
    os.makedirs("results", exist_ok=True)
    out.to_csv(OUT, index=False)
    core = out[out.core]
    print(f"certified anywhere: {len(out)} countries; "
          f"certified core (>=2 items): {len(core)}")
    print(core[["country", "n_items", "items", "group"]].to_string(index=False))
    print("\ncore composition:")
    print(core.group.value_counts().to_string())
    print("\nsingle-item composition:")
    print(out[~out.core].group.value_counts().to_string())
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
