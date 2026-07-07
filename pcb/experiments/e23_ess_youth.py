"""E23 — youth age-group robustness (preregistered in docs/YOUTH_PREREGISTRATION.md).

Reruns the e13 country-wide design-aware decline certification within fixed age
bands, reusing the SAME certification (audit_country), thresholds, core rounds,
design bootstrap, ρ₀, and fallback. Age-GROUP comparison, not cohort. Min effective
n = 200 valid responses per country-round (sub-threshold cells abstained); a country
needs ≥2 qualifying core rounds. Nothing about the method is changed for age.

Run:  python -m pcb.experiments.e23_ess_youth
Output: results/ess_youth_certification.csv
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import COLS, audit, load
from pcb.experiments.e13_ess_audit import OUTCOMES, audit_country

MIN_N = 200                              # preregistered min valid responses per cell
AGE_GROUPS = {                           # fixed in the preregistration
    "youth_18_29": lambda a: (a >= 18) & (a <= 29),
    "full_18plus": lambda a: (a >= 18),
    "older_50plus": lambda a: (a >= 50),
    "mid_30_49": lambda a: (a >= 30) & (a <= 49),
}


def _qualifying_core_rounds(csub, klass, c, outcome):
    """Core rounds for country c with >= MIN_N valid outcome responses in this band."""
    out = []
    for r in sorted(csub.essround.unique()):
        if klass.get((c, r)) != "core":
            continue
        n = csub.loc[csub.essround == r, outcome].notna().sum()
        if n >= MIN_N:
            out.append(int(r))
    return out


def main():
    df = load(COLS + ["agea"])           # re-reads the .dta once to add agea
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0) & df["agea"].notna()]

    rows, abstain = [], []
    for grp, mask in AGE_GROUPS.items():
        sub_all = df[mask(df["agea"].to_numpy())]
        for outcome in OUTCOMES:
            for c, csub in sub_all.groupby("cntry", observed=True):
                cr = _qualifying_core_rounds(csub, klass, c, outcome)
                pairs = [r for r in cr if r + 1 in cr]
                if len(pairs) == 0:
                    abstain.append((grp, outcome, c))
                    continue
                rng = np.random.default_rng(det_seed("youth", grp, outcome, c))
                res = audit_country(csub[csub.essround.isin(cr)], cr, outcome, rng)
                if res:
                    rows.append(dict(age_group=grp, outcome=outcome, cntry=c, **res))
    cty = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    cty.to_csv("results/ess_youth_certification.csv", index=False)

    print(f"countries certified (persistent country-wide design-aware decline):")
    print(f"{'age group':>14s} | {'outcome':>8s} | {'#countries':>10s} | "
          f"{'any-pair DA':>11s} | {'net DA':>7s} | {'persistent DA':>13s} | "
          f"{'persist+Bonf':>12s} | countries(persist)")
    for grp in AGE_GROUPS:
        for outcome in OUTCOMES:
            p = cty[(cty.age_group == grp) & (cty.outcome == outcome)]
            if not len(p):
                print(f"{grp:>14s} | {outcome:>8s} | {'0 (no cells)':>10s}")
                continue
            names = sorted(p.cntry[p.persist_da.astype(bool)])
            print(f"{grp:>14s} | {outcome:>8s} | {len(p):>10d} | "
                  f"{int(p.any_da.sum()):>11d} | {int(p.net_da.sum()):>7d} | "
                  f"{int(p.persist_da.sum()):>13d} | "
                  f"{int(p.persist_da_bonf.sum()):>12d} | {names}")
    print(f"\nabstained country-cells (below min-n or <2 qualifying rounds): {len(abstain)}")
    print("wrote results/ess_youth_certification.csv")


if __name__ == "__main__":
    main()
