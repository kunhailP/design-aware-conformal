"""E62 — the small-area activation under the Rao-Wu-Yue rescaling bootstrap.

E38 flips every stratified-bootstrap site at the national unit and finds all
counts and gates unchanged, but it does not touch E54/E55 — the paper's only
positive activation. Before the rescaling bootstrap can be promoted to the
deployed default, the activation itself has to survive it: this experiment
reruns the E54 sweep with the whole-country bootstrap drawing m-1 PSUs per
stratum and scaling that stratum's sums by m/(m-1) (single-PSU strata are
kept as-is, as everywhere else), and prints the activation table against the
shipped one.

Seeds match E54 per cell; the m-1 draw consumes the stream differently, so
cells differ by Monte Carlo noise plus the rescaling itself — the comparison
is of gate decisions and activation counts, not of bit-level draws.

Output: results/small_area_transport_rescaled.csv
Run:    python -m pcb.experiments.e62_small_area_rescaled   (~1-2 h)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.experiments.e54_small_area_transport import (B, CORE, MIN_SIZES,
                                                      ROUNDS, _load, _row)


def _country_draws_rwy(sub, min_n, rng):
    """E54's whole-country bootstrap with Rao-Wu-Yue rescaling."""
    y = sub["trstprl"].to_numpy(float); w = sub["_w"].to_numpy(float)
    reg = sub["region"].to_numpy()
    psu = sub["psu"].to_numpy(); strat = sub["stratum"].to_numpy()

    ind = w[:, None] * (y[:, None] <= CORE[None, :])
    key = pd.MultiIndex.from_arrays([strat, psu, reg])
    g = pd.DataFrame(np.column_stack([ind, w]), index=key).groupby(
        level=[0, 1, 2], observed=True).sum()
    cnt, tot = g.values[:, :len(CORE)], g.values[:, len(CORE)]
    s_lab = g.index.get_level_values(0).to_numpy()
    r_lab = g.index.get_level_values(2).to_numpy()

    regions = [r for r in np.unique(r_lab) if tot[r_lab == r].sum() > 0]
    keep = []
    for r in regions:
        m = r_lab == r
        if int((sub.region == r).sum()) >= min_n and m.sum() >= 2:
            keep.append(r)
    if len(keep) < 2:
        return None

    idx_by_stratum = {s: np.flatnonzero(s_lab == s) for s in np.unique(s_lab)}

    def resample():
        pick, fac = [], []
        for s, rows in idx_by_stratum.items():
            m = len(rows)
            if m > 1:
                pick.append(rows[rng.integers(0, m, size=m - 1)])
                fac.append(np.full(m - 1, m / (m - 1.0)))
            else:
                pick.append(rows)
                fac.append(np.ones(1))
        return np.concatenate(pick), np.concatenate(fac)

    def curves(rows, f=None):
        if f is None:
            f = np.ones(len(rows))
        num = cnt[rows] * f[:, None]; den = tot[rows] * f; lab = r_lab[rows]
        nat = num.sum(0) / max(den.sum(), 1e-12)
        out = {}
        for r in keep:
            m = lab == r
            if den[m].sum() <= 0:
                return None
            out[r] = num[m].sum(0) / den[m].sum() - nat
        return out

    point = curves(np.arange(len(tot)))
    if point is None:
        return None
    reps = {r: np.empty((B, len(CORE))) for r in keep}
    for b in range(B):
        rows, f = resample()
        c = curves(rows, f)
        if c is None:
            for r in keep:
                reps[r][b] = point[r]
        else:
            for r in keep:
                reps[r][b] = c[r]
    return {r: (point[r], reps[r].std(0), int((sub.region == r).sum()))
            for r in keep}


def main():
    os.makedirs("results", exist_ok=True)
    d = _load()
    lvl = (d.groupby("cntry", observed=True).region
           .apply(lambda x: int(np.median([len(v) for v in x.unique()]))))
    common = set(lvl[lvl == lvl.value_counts().idxmax()].index)

    rows = []
    for min_n in MIN_SIZES:
        for rnd in ROUNDS:
            cells, ctry = {}, {}
            for c, sub in d[d.essround == rnd].groupby("cntry", observed=True):
                rng = np.random.default_rng(det_seed("e54", str(c), int(rnd), min_n))
                got = _country_draws_rwy(sub, min_n, rng)
                if got:
                    for r, v in got.items():
                        cells[(str(c), r)] = v
                        ctry[(str(c), r)] = str(c)
            if len(cells) < 10:
                continue
            keys = list(cells)
            Dm = np.array([cells[k][0] for k in keys])
            Vm = np.array([cells[k][1] for k in keys])
            nm = np.array([cells[k][2] for k in keys])
            rows.append(_row(Dm, Vm, nm, min_n, rnd, "all countries"))
            sel = [i for i, k in enumerate(keys) if ctry[k] in common]
            if len(sel) >= 10:
                rows.append(_row(Dm[sel], Vm[sel], nm[sel], min_n, rnd,
                                 "common NUTS level"))
        r = [x for x in rows if x["min_n"] == min_n and x["pool"] == "all countries"]
        for x in r:
            print(f"min_n={min_n:>3} r{x['essround']}: K={x['K']:>3} "
                  f"rho_LCB={x['rho_lcb']:.3f} D={x['D']:.3f} "
                  f"A={int(x['gate_A'])} B={int(x['gate_B'])} -> {x['branch']}"
                  + (f"  gain={x['gain_lcb']}" if x['gain_lcb'] is not None else ""))
    t = pd.DataFrame(rows)
    t.to_csv("results/small_area_transport_rescaled.csv", index=False)

    a = t[t.pool == "all countries"]
    fired = a[a.branch == "deconvolution"]
    print("\n=== RWY-rescaled small-area sweep ===")
    print(f"  unit-rounds: {len(a)}  gate_A: {int(a.gate_A.sum())}  "
          f"gate_B: {int(a.gate_B.sum())}  FIRES: {len(fired)}")
    if len(fired):
        print(fired[["min_n", "essround", "K", "rho_lcb", "D", "gain_lcb",
                     "width_ratio", "coverage"]].to_string(index=False))

    shipped = "results/small_area_transport.csv"
    if os.path.exists(shipped):
        o = pd.read_csv(shipped)
        oa = o[o.pool == "all countries"]
        print("\n=== vs shipped (m-of-m) ===")
        print(f"  gate_A opens : shipped {int(oa.gate_A.sum())} -> rescaled "
              f"{int(a.gate_A.sum())}")
        print(f"  fires        : shipped "
              f"{int((oa.branch == 'deconvolution').sum())} -> rescaled "
              f"{len(fired)}")
        print(f"  max rho_LCB  : shipped {oa.rho_lcb.max():.3f} -> rescaled "
              f"{a.rho_lcb.max():.3f}")


if __name__ == "__main__":
    main()
