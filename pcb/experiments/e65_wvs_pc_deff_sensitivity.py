"""E65 — design-effect sensitivity of the WVS partial-conjunction core.

The WVS Trend File has no PSU/stratum identifiers. Following E39, this reruns
the E63 p-values after multiplying the weights-only bootstrap variance by
1.5 and 2.0. It tests whether the stronger >=2-item statement survives the
same disclosed design-uncertainty stress test as the descriptive core.

Outputs:
  results/wvs_partial_conjunction_deff.csv
  results/wvs_partial_conjunction_deff_prevalence.csv
"""
from __future__ import annotations

import os

import pandas as pd

from pcb.data.audit_wvs import load
from pcb.experiments.e63_wvs_partial_conjunction import (
    _country_results,
    _item_results,
    _prevalence_results,
)


DEFFS = (1.5, 2.0)


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    df = df[df["_w"].notna() & (df["_w"] > 0)]

    countries, prevalence = [], []
    for deff in DEFFS:
        item_results = _item_results(df, deff)
        country_results = _country_results(item_results)
        country_results.insert(0, "deff", deff)
        countries.append(country_results)

        prev = _prevalence_results(country_results)
        prev.insert(0, "deff", deff)
        prevalence.append(prev)

        legacy = country_results.n_certified_alpha10 >= 2
        valid = country_results.pc_bonferroni
        print(
            f"deff={deff:g}: descriptive core {int(legacy.sum())}; "
            f"partial-conjunction core {int(valid.sum())}"
        )
        print(
            country_results.loc[
                valid, ["country", "p_pc_bonferroni"]
            ].to_string(index=False)
        )

    pd.concat(countries, ignore_index=True).to_csv(
        "results/wvs_partial_conjunction_deff.csv", index=False
    )
    pd.concat(prevalence, ignore_index=True).to_csv(
        "results/wvs_partial_conjunction_deff_prevalence.csv", index=False
    )


if __name__ == "__main__":
    main()
