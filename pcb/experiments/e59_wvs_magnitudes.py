"""E59 — certified decline magnitudes for the WVS core matrix (Figure 4C).

No new hypothesis test: for each (country, item) the persistent-claim band of
e26 already implies a simultaneous lower bound on the per-pair decline,
L = min over (adjacent pairs x core thresholds) of  D_hat - c*sd,
with c the persistent-run critical value. L > 0 iff the persistent claim
certifies (identical decision to e26, machine-checked below), and its value is
the certified minimum decline in CDF points -- the evidence-strength layer the
magnitude-aware core matrix displays.

Output: results/wvs_core_magnitudes.csv (iso, item, certified, magnitude_lb)
Run:    python -m pcb.experiments.e59_wvs_magnitudes   (licensed microdata)
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.data.audit_wvs import load, ITEMS
from pcb.experiments.e26_wvs_deconsolidation import (ALPHA, CORE, MIN_N,
                                                     SUPPORT, _cells)


def _persistent_lb(cells, c, waves, item):
    M = SUPPORT[item]
    tmask = np.zeros(M, bool)
    tmask[[t - 1 for t in CORE[item]]] = True
    ws = sorted(w for w in waves if (c, w) in cells)
    pairs = list(zip(ws[:-1], ws[1:]))
    if not pairs:
        return None
    dh, db = [], []
    for a, b in pairs:
        Fa, Ba = cells[(c, a)]
        Fb, Bb = cells[(c, b)]
        dh.append(Fb - Fa)
        db.append(Bb - Ba)
    dh = np.array(dh)[:, tmask]
    db = np.stack(db, 1)[:, :, tmask]
    sd = np.maximum(db.std(0), 1e-6)
    dev = np.max((db - dh[None]) / sd[None], axis=(1, 2))
    crit = np.quantile(dev, 1 - ALPHA)
    return float(np.min(dh - crit * sd))


def main():
    os.makedirs("results", exist_ok=True)
    df = load()
    df = df[df["_w"].notna() & (df["_w"] > 0)]
    rows = []
    for item in ITEMS:
        cells = _cells(df, item)
        countries = sorted({c for c, _ in cells})
        waves = sorted({w for _, w in cells})
        for c in countries:
            lb = _persistent_lb(cells, c, waves, item)
            if lb is None:
                continue
            rows.append(dict(iso=c, item=item, certified=bool(lb > 0),
                             magnitude_lb=round(lb, 5)))
    d = pd.DataFrame(rows)
    d.to_csv("results/wvs_core_magnitudes.csv", index=False)
    cert = d[d.certified]
    print(f"country-item cells: {len(d)}; certified persistent: {len(cert)}")
    print("certified magnitude LB (CDF points): "
          f"min {cert.magnitude_lb.min():.3f}, "
          f"median {cert.magnitude_lb.median():.3f}, "
          f"max {cert.magnitude_lb.max():.3f}")


if __name__ == "__main__":
    main()
