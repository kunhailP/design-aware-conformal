"""E63 — valid cross-item claims for the WVS certified core.

E26 certifies persistent decline separately on each of five democratic-attitude
items. E30's >=2-item core is descriptive: two separate alpha=.10 decisions do
not test that at least two item-level claims are true. This experiment inverts
E26's exact adjacent-pair band to obtain country-item p-values, combines them
with an arbitrary-dependence-valid Bonferroni partial-conjunction test, and then
optionally closes the country family.

Protocol: docs/WVS_PARTIAL_CONJUNCTION_PREREG.md
Outputs:
  results/wvs_item_pvalues.csv
  results/wvs_partial_conjunction.csv
  results/wvs_partial_conjunction_prevalence.csv
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

import pcb.experiments.e26_wvs_deconsolidation as e26
from pcb.data.audit_wvs import ITEMS, load
from pcb.experiments.e30_certified_core import ISO
from pcb.inference.decline_certify import decline_difference_pvalue
from pcb.inference.prevalence import (
    partial_conjunction_pvalue,
    prevalence_lower_bound,
)


ALPHA = 0.10


def _persistent_pvalue(cells, country: int, waves, item: str):
    """Return E26's persistent p-value and metadata for one country-item."""
    support = e26.SUPPORT[item]
    tmask = np.zeros(support, bool)
    tmask[[t - 1 for t in e26.CORE[item]]] = True
    observed = sorted(w for w in waves if (country, w) in cells)
    if len(observed) < 2:
        return None

    diff_hat, diff_boot = [], []
    for first, last in zip(observed[:-1], observed[1:]):
        f_first, b_first = cells[(country, first)]
        f_last, b_last = cells[(country, last)]
        diff_hat.append(f_last - f_first)
        diff_boot.append(b_last - b_first)
    dh = np.asarray(diff_hat)
    db = np.stack(diff_boot, axis=1)
    pvalue = decline_difference_pvalue(dh, db, tmask)
    verdict = e26._certify_country(cells, country, observed, item)
    p_verdict = pvalue <= ALPHA
    if p_verdict != bool(verdict["persist"]) and \
            abs(pvalue - ALPHA) > 2 / e26.B:
        raise RuntimeError(
            f"p-value inversion disagrees with E26 for {item}/{country}: "
            f"p={pvalue:.6f}, verdict={verdict['persist']}"
        )
    return dict(
        p_persistent=pvalue,
        p_le_alpha10=p_verdict,
        certifies_alpha10=bool(verdict["persist"]),
        n_waves=len(observed),
        first_wave=int(observed[0]),
        last_wave=int(observed[-1]),
    )


def _country_results(item_pvalues: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for iso, group in item_pvalues.groupby("iso", observed=True):
        pvalues = group.p_persistent.to_numpy(float)
        ordered = group.sort_values(["p_persistent", "item"])
        m = len(group)
        if m < 2:
            continue
        p_bonf = partial_conjunction_pvalue(pvalues, 2, "bonferroni")
        p_simes = partial_conjunction_pvalue(pvalues, 2, "simes")
        rows.append(dict(
            iso=int(iso),
            country=ISO.get(int(iso), str(int(iso))),
            m_items=m,
            p_pc_bonferroni=p_bonf,
            p_pc_simes=p_simes,
            pc_bonferroni=p_bonf <= ALPHA,
            pc_simes=p_simes <= ALPHA,
            n_certified_alpha10=int(group.certifies_alpha10.sum()),
            certified_items=";".join(sorted(
                group.loc[group.certifies_alpha10, "item"]
            )),
            two_smallest_items=";".join(ordered.item.iloc[:2]),
        ))
    return pd.DataFrame(rows).sort_values(
        ["p_pc_bonferroni", "p_pc_simes", "country"]
    )


def _prevalence_results(country_results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pc_method, p_column in (
        ("bonferroni", "p_pc_bonferroni"),
        ("simes", "p_pc_simes"),
    ):
        mapping = dict(zip(
            country_results.iso.astype(int),
            country_results[p_column].astype(float),
        ))
        for local in ("bonferroni", "simes"):
            out = prevalence_lower_bound(mapping, ALPHA, local)
            rows.append(dict(
                pc_method=pc_method,
                country_local_test=local,
                n_countries=len(mapping),
                d=out["d"],
                countries_named=";".join(map(str, out["countries_named"])),
                n_named=len(out["countries_named"]),
                named_covers_d=out["named_covers_d"],
            ))
    return pd.DataFrame(rows)


def _item_results(df: pd.DataFrame, deff: float = 1.0) -> pd.DataFrame:
    """Compute all country-item p-values, optionally inflating design variance."""
    item_rows = []
    scale = np.sqrt(deff)
    for item in ITEMS:
        print(f"building E26 cells for {item} (deff={deff:g})...")
        cells = e26._cells(df, item)
        if deff != 1.0:
            cells = {
                key: (curve, curve[None] + scale * (boot - curve[None]))
                for key, (curve, boot) in cells.items()
            }
        countries = sorted({int(country) for country, _ in cells})
        waves = sorted({int(wave) for _, wave in cells})
        current_rows = []
        for country in countries:
            result = _persistent_pvalue(cells, country, waves, item)
            if result is None:
                continue
            current_rows.append(dict(
                iso=country,
                country=ISO.get(country, str(country)),
                item=item,
                **result,
            ))
        available = len(current_rows)
        for row in current_rows:
            row["K_item"] = available
        item_rows.extend(current_rows)
        print(f"  {available} countries with at least two qualifying waves")
    columns = [
        "iso", "country", "item", "K_item", "p_persistent",
        "p_le_alpha10", "certifies_alpha10", "n_waves",
        "first_wave", "last_wave",
    ]
    return pd.DataFrame(item_rows)[columns].sort_values(
        ["item", "p_persistent", "country"]
    )


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    df = df[df["_w"].notna() & (df["_w"] > 0)]

    item_results = _item_results(df)
    country_results = _country_results(item_results)
    prevalence = _prevalence_results(country_results)

    item_results.to_csv("results/wvs_item_pvalues.csv", index=False)
    country_results.to_csv(
        "results/wvs_partial_conjunction.csv", index=False
    )
    prevalence.to_csv(
        "results/wvs_partial_conjunction_prevalence.csv", index=False
    )

    legacy = country_results.n_certified_alpha10 >= 2
    primary = country_results.pc_bonferroni
    print("\nWVS >=2-item claims")
    print(f"  descriptive alpha=.10 core: {int(legacy.sum())}")
    print(f"  Bonferroni partial conjunction: {int(primary.sum())}")
    print(country_results.loc[
        primary,
        ["country", "m_items", "p_pc_bonferroni", "certified_items"],
    ].to_string(index=False))
    print("\nAcross-country closed testing")
    print(prevalence.to_string(index=False))


if __name__ == "__main__":
    main()
