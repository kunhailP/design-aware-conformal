"""E15 — Gate 5D external design validation on AmericasBarometer (LAPOP).

Preregistered in docs/LAPOP_PREREGISTRATION.md. Within-country decline
certification (D_{c,r}(t)=F_{c,r+1}(t)−F_{c,r}(t) over the low core), replicating
the ESS E13 guarantee hierarchy, with the method set that the LAPOP design layer
makes possible:

  M0 raw plug-in point
  M1 respondent bootstrap (UNWEIGHTED resample)
  M2 weighted respondent bootstrap (resample rows, apply wt)
  M3 stratified-PSU bootstrap (resample upm within strata, Rao–Wu)  = PROPER design

M2-vs-M3 is the naive-vs-proper divergence (external criterion 2) that ESS could
not exercise (there the clustering design effect was small). The design-effect
ratio deff½_cr = SD_M3(D)/SD_M2(D) measures clustering; high-noise = top tercile.

Note (preregistration clarification): the Candidate-B deconvolution / worst-case /
fallback methods (M4–M6) are TRANSPORT-setting estimators (cross-country
deployment, Thm B/D) — they deconvolve design noise from cross-country transport
variability. The WITHIN-country difference has no transport term, so the proper
design band there IS M3 (nothing to deconvolve). M4–M6 are validated in the
cross-country transport experiment (Part B, e16), not here.

Real data has no oracle truth: report certification, width, reclassification, and
the design-effect regime split — not coverage. "certified by plug-in but
inconclusive under proper design inference," never "false positive."

Run:  python -m pcb.experiments.e15_lapop_certify
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed
import pandas as pd

from pcb.data.audit_lapop import audit, load
from pcb.inference.decline_certify import certify_decline_differences

ALPHA = 0.10
B = 2000
# per-outcome scale: (raw col, transform, n_categories, low-core thresholds)
OUTCOMES = {
    "b13": dict(cats=7, core=(1, 2, 3), rev=False),        # trust legislature 1-7
    "sat": dict(cats=4, core=(1, 2), rev=True),            # 5-pn4 satisfaction
    "ing4": dict(cats=7, core=(1, 2, 3), rev=False),       # support democracy 1-7
}


def _series(g, outcome):
    if outcome == "sat":
        v = g["pn4"].where(g["pn4"] >= 0)
        return 5 - v                                        # reverse → high=sat
    return g[outcome].where(g[outcome] >= 0)


def _thr(cfg):
    return np.arange(1, cfg["cats"])                        # F(t) for t=1..cats-1


def _core_mask(cfg):
    thr = _thr(cfg)
    return np.isin(thr, cfg["core"])


def _wcdf(y, w, thr):
    return ((w[:, None] * (y[:, None] <= thr[None, :])).sum(0)) / w.sum()


def _resp_boot(y, w, thr, rng):
    """Multinomial respondent resample → (B, T) weighted CDF."""
    n = len(y)
    ind = w[:, None] * (y[:, None] <= thr[None, :])         # (n, T)
    C = rng.multinomial(n, np.full(n, 1.0 / n), size=B).astype(float)  # (B, n)
    num = C @ ind                                           # (B, T)
    den = C @ w
    return num / den[:, None]


def _design_boot(y, w, strata, upm, thr, rng):
    """Stratified PSU bootstrap → (B, T) (resample upm within strata)."""
    ind = w[:, None] * (y[:, None] <= thr[None, :])
    key = pd.MultiIndex.from_arrays([strata, upm])
    grp = pd.DataFrame(np.column_stack([ind, w]), index=key).groupby(level=[0, 1]).sum()
    cnt, tot = grp.values[:, :len(thr)], grp.values[:, len(thr)]
    strat = grp.index.get_level_values(0).to_numpy()
    bc = np.zeros((B, len(thr))); bt = np.zeros(B)
    for s in np.unique(strat):
        rows = np.flatnonzero(strat == s); m = len(rows)
        idx = rows[rng.integers(0, m, size=(B, m))] if m > 1 else \
            np.broadcast_to(rows, (B, 1))
        bc += cnt[idx].sum(1); bt += tot[idx].sum(1)
    return bc / bt[:, None]


def _pair(a, b, outcome, cfg, rng):
    thr = _thr(cfg)
    ya, wa = _series(a, outcome), a["wt"].where(a["wt"] >= 0)
    yb, wb = _series(b, outcome), b["wt"].where(b["wt"] >= 0)
    ma = ya.notna() & wa.notna(); mb = yb.notna() & wb.notna()
    ya, wa = ya[ma].to_numpy(), wa[ma].to_numpy()
    yb, wb = yb[mb].to_numpy(), wb[mb].to_numpy()
    if min(len(ya), len(yb)) < 200:
        return None
    dhat = (_wcdf(yb, wb, thr) - _wcdf(ya, wa, thr))[None]  # (1,T)
    one = np.ones_like
    # M1 unweighted, M2 weighted respondent, M3 stratified PSU
    d1 = (_resp_boot(yb, one(wb), thr, rng) - _resp_boot(ya, one(wa), thr, rng))
    d2 = (_resp_boot(yb, wb, thr, rng) - _resp_boot(ya, wa, thr, rng))
    d3 = (_design_boot(yb, wb, b["strata"].to_numpy()[mb.to_numpy()],
                       b["upm"].to_numpy()[mb.to_numpy()], thr, rng)
          - _design_boot(ya, wa, a["strata"].to_numpy()[ma.to_numpy()],
                         a["upm"].to_numpy()[ma.to_numpy()], thr, rng))
    return dhat, d1, d2, d3


def certify_all(dhat, d1, d2, d3, core):
    out = {}
    out["M0"] = int(certify_decline_differences(dhat, d3[:, None], ALPHA, core)["plugin"])
    for tag, d in (("M1", d1), ("M2", d2), ("M3", d3)):
        out[tag] = int(certify_decline_differences(dhat, d[:, None], ALPHA, core)["design_aware"])
    sd2 = d2.std(0)[core].mean(); sd3 = d3.std(0)[core].mean()
    out["deff_ratio"] = float(sd3 / sd2) if sd2 > 0 else np.nan
    out["signal"] = float(dhat[0, core].mean())
    return out


def build_pairs():
    df, _ = load()
    a = audit(df).set_index(["pais", "year"])
    df = df[df.year != 2021]
    rows = []
    for outcome, cfg in OUTCOMES.items():
        core = _core_mask(cfg)
        for pais, g in df.groupby("pais", observed=True):
            years = sorted(y for y in g.year.unique()
                           if a.loc[(pais, y), "sample"] == "core")
            cty = g["country"].iloc[0]
            for y0, y1 in zip(years, years[1:]):
                rng = np.random.default_rng(det_seed(outcome, pais, y0))
                res = _pair(g[g.year == y0], g[g.year == y1], outcome, cfg, rng)
                if res is None:
                    continue
                dhat, d1, d2, d3 = res
                rec = dict(outcome=outcome, pais=int(pais), country=cty,
                           y0=int(y0), y1=int(y1),
                           n0=int((g.year == y0).sum()),
                           n_upm=int(g[g.year == y0].upm.nunique()))
                rec.update(certify_all(dhat, d1, d2, d3, core))
                rows.append(rec)
    return pd.DataFrame(rows)


def main():
    os.makedirs("results", exist_ok=True)
    pair = build_pairs()
    pair.to_csv("results/lapop_decline_certification.csv", index=False)
    print(f"LAPOP: {len(pair)} country-year pairs across "
          f"{pair.outcome.nunique()} outcomes, {pair.country.nunique()} countries\n")

    meth = ["M0", "M1", "M2", "M3"]
    print("=== pair-level decline certification (α=0.10) ===")
    for o in OUTCOMES:
        p = pair[pair.outcome == o]
        line = " | ".join(f"{m} {int(p[m].sum()):2d}/{len(p)}" for m in meth)
        print(f"{o:5s}: {line}")

    print("\n=== naive (M2) vs proper (M3) by design-effect regime (criterion 2) ===")
    for o in OUTCOMES:
        p = pair[pair.outcome == o].dropna(subset=["deff_ratio"]).copy()
        if len(p) < 6:
            continue
        hi = p.deff_ratio >= p.deff_ratio.quantile(2 / 3)
        lo = p.deff_ratio <= p.deff_ratio.quantile(1 / 3)
        print(f"{o}: deff½ median {p.deff_ratio.median():.2f} "
              f"[{p.deff_ratio.min():.2f},{p.deff_ratio.max():.2f}]")
        for lab, m in (("high-noise (top ρ tercile)", hi), ("low-noise (bottom)", lo)):
            q = p[m]
            print(f"    {lab:28s}: M2 {int(q.M2.sum())}/{len(q)}, "
                  f"M3 {int(q.M3.sum())}/{len(q)}, "
                  f"M2−M3 over-cert = {int(q.M2.sum()) - int(q.M3.sum())}, "
                  f"deff½ {q.deff_ratio.mean():.2f}")

    print("\n=== country-wide guarantee hierarchy (plug-in M0 / proper M3) ===")
    for o in OUTCOMES:
        p = pair[pair.outcome == o]
        rows = []
        for pais, g in p.groupby("pais"):
            H = None
            # any / net use per-pair flags; persistent needs the joint band → recompute
            rows.append(dict(pais=pais,
                             any0=int(g.M0.max()), anyM3=int(g.M3.max())))
        cc = pd.DataFrame(rows)
        print(f"{o}: any-pair decline — plug-in {int(cc.any0.sum())} countries / "
              f"proper-design {int(cc.anyM3.sum())}")


if __name__ == "__main__":
    main()
