"""E34 — per-country rung flags for the WVS deconsolidation reanalysis.

Companion to E26: identical machinery (same seeds, same cells, same certification
calls via e26._hierarchy), but writes the per-country booleans that E26 aggregates —
one row per (item, country) with any-pair / net / persistent flags, survey-aware and
plug-in. Input to the V-Dem regime-type and predictive-validity cross-tabs (E35).

Run:  python -m pcb.experiments.e34_wvs_country_flags
"""
from __future__ import annotations
import os

import pandas as pd

from pcb.data.audit_wvs import load, ITEMS
from pcb.experiments.e26_wvs_deconsolidation import _hierarchy

OUT = "results/wvs_country_flags.csv"


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    df = df[df["_w"].notna() & (df["_w"] > 0)]
    rows = []
    for item in ITEMS:
        flags, K = _hierarchy(df, item)
        for c, r in flags.items():
            rows.append(dict(item=item, iso=c, K_item=K,
                             anypair=r["anypair"], anypair_plugin=r["anypair_pi"],
                             net=r["net"], net_plugin=r["net_pi"],
                             persist=r["persist"], persist_plugin=r["persist_pi"]))
        print(f"{item}: {K} countries")
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
