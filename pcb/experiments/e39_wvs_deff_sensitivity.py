"""E39 — the promised WVS design-effect sensitivity rerun (paper §7).

The WVS/EVS trend file ships no PSU/stratum identifiers, so the certification
bootstrap is weights-only and understates design variance under clustered
designs; the paper states the direction (counts inflate; the rung gap is a lower
bound) and flags this rerun. Here we rerun the full five-item certification with
the bootstrap CDF draws' variance inflated by deff in {1.5, 2.0} — draws are
recentered and rescaled about the point estimate, F + sqrt(deff) * (F_b - F) —
and report how the per-item counts, the marginal/persistent ratio range, and the
>=2-item certified core move.

Output: results/wvs_deff_sensitivity.csv (+ per-country flags per deff)
Run:    python -m pcb.experiments.e39_wvs_deff_sensitivity   (~2-4 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

import pcb.experiments.e26_wvs_deconsolidation as e26
from pcb.data.audit_wvs import load, ITEMS

DEFFS = (1.5, 2.0)


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    df = df[df["_w"].notna() & (df["_w"] > 0)]

    base = pd.read_csv("results/wvs_deconsolidation.csv").set_index("item")
    orig_cells = e26._cells
    rows, flags = [], []
    for deff in DEFFS:
        s = np.sqrt(deff)

        def cells_inflated(d, item, _orig=orig_cells, _s=s):
            out = _orig(d, item)
            return {k: (F, F[None, :] + _s * (Bd - F[None, :]))
                    for k, (F, Bd) in out.items()}

        e26._cells = cells_inflated
        try:
            for item in ITEMS:
                hier, K = e26._hierarchy(df, item)
                ap = sum(r["anypair"] for r in hier.values())
                ap_pi = sum(r["anypair_pi"] for r in hier.values())
                ps = sum(r["persist"] for r in hier.values())
                ps_pi = sum(r["persist_pi"] for r in hier.values())
                nt = sum(r["net"] for r in hier.values())
                rows.append(dict(deff=deff, item=item, K=K,
                                 anypair=ap, anypair_plugin=ap_pi, net=nt,
                                 persist=ps, persist_plugin=ps_pi,
                                 ratio=ap_pi / max(ps, 1),
                                 base_persist=int(base.loc[item, "persist"]),
                                 base_ratio=base.loc[item, "anypair_plugin"]
                                 / max(int(base.loc[item, "persist"]), 1)))
                for c, r in hier.items():
                    flags.append(dict(deff=deff, item=item, iso=c,
                                      persist=r["persist"]))
                print(f"deff={deff}: {item:12s} persist {ps} "
                      f"(base {int(base.loc[item,'persist'])}), "
                      f"marginal/persist {ap_pi}/{ps}")
        finally:
            e26._cells = orig_cells

    res = pd.DataFrame(rows)
    res.to_csv("results/wvs_deff_sensitivity.csv", index=False)
    fl = pd.DataFrame(flags)
    fl.to_csv("results/wvs_deff_country_flags.csv", index=False)

    print("\n=== summary ===")
    for deff in DEFFS:
        r = res[res.deff == deff]
        print(f"deff x{deff}: persist range {r.persist.min()}–{r.persist.max()} "
              f"(base {r.base_persist.min()}–{r.base_persist.max()}); "
              f"ratio range {r.ratio.min():.1f}–{r.ratio.max():.1f}x "
              f"(base {r.base_ratio.min():.1f}–{r.base_ratio.max():.1f}x)")
        per = (fl[fl.deff == deff].groupby("iso")["persist"].sum())
        core = sorted(per[per >= 2].index)
        print(f"  >=2-item core under deff x{deff}: {len(core)} countries: {core}")


if __name__ == "__main__":
    main()
