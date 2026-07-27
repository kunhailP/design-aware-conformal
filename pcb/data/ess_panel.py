"""ESS country-round panel — step 2 of the political-attitudes layer.

One row per country x round with, for each outcome (trstprl primary, stfdem
replication), the design-weighted CDF over the 0-10 scale read at thresholds
t = 0..9, plus the design-bootstrap SD of each CDF value where the integrated
file carries psu/stratum (rounds 9-11, the core sample).

Weights: anweight where present, else pspwght (within a single country-round
the population-size factor pweight is a constant and cancels in the CDF).
Design bootstrap: stratified with-replacement PSU bootstrap (Rao-Wu style,
single-PSU strata contribute no variance — conservative-low, flagged in n_psu).

Run:  python -m pcb.data.ess_panel        -> data/ess/panel.parquet
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed

from pcb.util import det_seed
import pandas as pd

from pcb.data.audit_ess import load, audit

OUT = "data/ess/panel.parquet"
T_GRID = 10                      # thresholds t = 0..9 on the 0-10 scale
B_BOOT = 300
OUTCOMES = ("trstprl", "stfdem")


RESCALE = False   # Rao-Wu-Yue rescaling: draw m-1 PSUs per stratum with replacement
                  # and scale stratum sums by m/(m-1); unbiases the between-PSU
                  # variance that plain m-of-m understates. Flip via e38 only.

def weighted_cdf(y: np.ndarray, w: np.ndarray) -> np.ndarray:
    ind = y[:, None] <= np.arange(T_GRID)[None, :]
    return (w[:, None] * ind).sum(0) / w.sum()


def design_boot_sd(y, w, stratum, psu, B=B_BOOT, rng=None) -> np.ndarray:
    """Stratified PSU-bootstrap SD of the weighted CDF; (T_GRID,)."""
    if rng is None:
        rng = np.random.default_rng(0)
    ind = w[:, None] * (y[:, None] <= np.arange(T_GRID)[None, :])
    key = pd.MultiIndex.from_arrays([stratum, psu])
    g = pd.DataFrame(np.column_stack([ind, w]), index=key).groupby(level=[0, 1]).sum()
    cnt, tot = g.values[:, :T_GRID], g.values[:, T_GRID]
    strat = g.index.get_level_values(0).to_numpy()
    boot_c = np.zeros((B, T_GRID))
    boot_t = np.zeros(B)
    for s in np.unique(strat):
        rows = np.flatnonzero(strat == s)
        m = len(rows)
        if m > 1 and RESCALE:
            f = m / (m - 1.0)
            idx = rows[rng.integers(0, m, size=(B, m - 1))]
            boot_c += cnt[idx].sum(axis=1) * f
            boot_t += tot[idx].sum(axis=1) * f
            continue
        idx = rows[rng.integers(0, m, size=(B, m))] if m > 1 else \
            np.broadcast_to(rows, (B, 1))
        boot_c += cnt[idx].sum(axis=1)
        boot_t += tot[idx].sum(axis=1)
    return (boot_c / boot_t[:, None]).std(axis=0)


def build_panel() -> pd.DataFrame:
    df = load()
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    w_all = df["anweight"].fillna(df["pspwght"])
    df = df.assign(_w=w_all)
    df = df[df._w.notna() & (df._w > 0)]

    rows = []
    for (c, r), sub in df.groupby(["cntry", "essround"], observed=True):
        row = {"cntry": c, "essround": int(r), "sample": klass.loc[(c, r)]}
        has_design = (row["sample"] == "core")
        for out in OUTCOMES:
            ok = sub[out].notna()
            y, w = sub[out][ok].to_numpy(float), sub._w[ok].to_numpy(float)
            row[f"n_{out}"] = int(ok.sum())
            cdf = weighted_cdf(y, w)
            for t in range(T_GRID):
                row[f"{out}_t{t}"] = cdf[t]
            if has_design:
                v = design_boot_sd(y, w, sub.stratum[ok].to_numpy(),
                                   sub.psu[ok].to_numpy(),
                                   rng=np.random.default_rng(det_seed(c, r)))
                for t in range(T_GRID):
                    row[f"{out}_v{t}"] = v[t]
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    panel = build_panel()
    panel.to_parquet(OUT)
    core = panel[panel["sample"] == "core"]
    v = core[[f"trstprl_v{t}" for t in range(T_GRID)]].to_numpy()
    print(f"panel: {len(panel)} country-rounds "
          f"({panel.cntry.nunique()} countries), core with design SD: {len(core)}")
    print(f"trstprl design SD (core): mean {v.mean():.4f}, "
          f"p90 {np.quantile(v, .9):.4f}, max {v.max():.4f}")
    print(f"median n per country-round: {int(panel.n_trstprl.median())}")


if __name__ == "__main__":
    main()
