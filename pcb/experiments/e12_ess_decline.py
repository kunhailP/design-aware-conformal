"""E12 — Gate 5D part 1: design-aware within-country trust-decline certification
on real ESS core data (rounds 9–11). Preregistered in
docs/ESS_5D_PREREGISTRATION.md; do NOT change thresholds / country set / methods
after seeing results.

Estimand: consecutive-difference D_{c,r}(t) = F_{c,r+1}(t) − F_{c,r}(t) over the
low-trust core t ∈ {1,2,3,4}. Within one country the country effect cancels →
pure survey-design inference (no transport). Certify NET decline if D > 0 over
the whole core, simultaneously.

Methods (prereg §4): M0 plug-in point · M1 naive respondent bootstrap (ignores
PSU/strata) · M2 per-round design level-band non-overlap (stands in for any
level/transport band — powerless for a contrast) · M4 design-aware stratified-PSU
difference band. No oracle truth on ESS: we report certification and
reclassification, NOT coverage.

Run:  python -m pcb.experiments.e12_ess_decline
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed
import pandas as pd

from pcb.data.audit_ess import audit, load
from pcb.inference.decline_certify import certify_decline_differences

ALPHA = 0.10
B = 2000
T = 10                                   # thresholds t = 0..9
CORE_T = np.zeros(T, bool); CORE_T[1:5] = True     # low-trust core t ∈ {1,2,3,4}
OUTCOMES = ("trstprl", "stfdem")


def _round_stats(sub, outcome):
    """(y, w, stratum, psu) for valid responses of one country-round."""
    ok = sub[outcome].notna()
    return (sub[outcome][ok].to_numpy(float), sub["_w"][ok].to_numpy(float),
            sub["stratum"][ok].to_numpy(), sub["psu"][ok].to_numpy())


def _wcdf(y, w):
    ind = y[:, None] <= np.arange(T)[None, :]
    return (w[:, None] * ind).sum(0) / w.sum()


def _design_boot(y, w, stratum, psu, rng):
    """Stratified PSU bootstrap → (B, T) weighted-CDF draws (Rao–Wu)."""
    ind = w[:, None] * (y[:, None] <= np.arange(T)[None, :])
    key = pd.MultiIndex.from_arrays([stratum, psu])
    g = pd.DataFrame(np.column_stack([ind, w]), index=key).groupby(level=[0, 1]).sum()
    cnt, tot = g.values[:, :T], g.values[:, T]
    strat = g.index.get_level_values(0).to_numpy()
    bc = np.zeros((B, T)); bt = np.zeros(B)
    for s in np.unique(strat):
        rows = np.flatnonzero(strat == s); m = len(rows)
        idx = rows[rng.integers(0, m, size=(B, m))] if m > 1 else \
            np.broadcast_to(rows, (B, 1))
        bc += cnt[idx].sum(1); bt += tot[idx].sum(1)
    return bc / bt[:, None]


def _naive_boot(y, w, rng):
    """Respondent bootstrap ignoring the design → (B, T)."""
    n = len(y)
    idx = rng.integers(0, n, size=(B, n))
    wb = w[idx]; yb = y[idx]
    ind = (yb[:, :, None] <= np.arange(T)[None, None, :])
    return (wb[:, :, None] * ind).sum(1) / wb.sum(1)[:, None]


def _level_nonoverlap(cdf_r, cdf_r1, boot_r, boot_r1):
    """M2: simultaneous per-round design level bands, certify by non-overlap."""
    def band(cdf, boot):
        sd = np.maximum(boot.std(0), 1e-6)
        c = np.quantile(np.max(np.abs(cdf[None] - boot) / sd[None], axis=1),
                        1 - ALPHA)
        return cdf - c * sd, cdf + c * sd
    lo_r, hi_r = band(cdf_r, boot_r)
    lo_r1, hi_r1 = band(cdf_r1, boot_r1)
    return bool(np.all(lo_r1[CORE_T] >= hi_r[CORE_T]))


def analyse():
    df = load()
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    rows = []
    for outcome in OUTCOMES:
        for c, csub in df.groupby("cntry", observed=True):
            core_rounds = sorted(r for r in csub.essround.unique()
                                 if klass.get((c, r)) == "core")
            for r in core_rounds:
                if r + 1 not in core_rounds:
                    continue
                rng = np.random.default_rng(det_seed(outcome, c, r))
                a = csub[csub.essround == r]
                b = csub[csub.essround == r + 1]
                y0, w0, s0, p0 = _round_stats(a, outcome)
                y1, w1, s1, p1 = _round_stats(b, outcome)
                if min(len(y0), len(y1)) < 100:
                    continue
                f0, f1 = _wcdf(y0, w0), _wcdf(y1, w1)
                dhat = (f1 - f0)[None]                      # (1, T)

                db0, db1 = _design_boot(y0, w0, s0, p0, rng), \
                    _design_boot(y1, w1, s1, p1, rng)
                nb0, nb1 = _naive_boot(y0, w0, rng), _naive_boot(y1, w1, rng)
                d_design = (db1 - db0)[:, None, :]          # (B,1,T)
                d_naive = (nb1 - nb0)[:, None, :]

                m4 = certify_decline_differences(dhat, d_design, ALPHA, CORE_T)
                m1 = certify_decline_differences(dhat, d_naive, ALPHA, CORE_T)
                m2 = _level_nonoverlap(f0, f1, db0, db1)
                design_sd = float((db1 - db0).std(0)[CORE_T].mean())
                rows.append(dict(
                    outcome=outcome, cntry=c, r_from=int(r), r_to=int(r + 1),
                    n0=len(y0), n1=len(y1),
                    n_psu=min(a.psu.nunique(), b.psu.nunique()),
                    weight_cv=float(np.std(w0) / np.mean(w0)),
                    signal=float(dhat[0, CORE_T].mean()),
                    design_sd=design_sd,
                    M0_plugin=int(m4["plugin"]),
                    M1_naive=int(m1["design_aware"]),
                    M2_level=int(m2),
                    M4_design=int(m4["design_aware"]),
                    # recovery (mirror) under M4, for the certified-improvement col
                    M4_recovery=int(certify_decline_differences(
                        -dhat, -d_design, ALPHA, CORE_T)["design_aware"]))
                )
    return pd.DataFrame(rows)


def main():
    os.makedirs("results", exist_ok=True)
    pair = analyse()
    pair.to_csv("results/ess_design_aware_decline.csv", index=False)

    pd.set_option("display.width", 200)
    print(f"ESS core adjacent pairs analysed: {len(pair)//len(OUTCOMES)} per "
          f"outcome ({pair.cntry.nunique()} countries, rounds 9–11)\n")

    print("=== pair-level net-decline certification counts (α=0.10) ===")
    meth = ["M0_plugin", "M1_naive", "M2_level", "M4_design"]
    for outcome in OUTCOMES:
        p = pair[pair.outcome == outcome]
        line = " | ".join(f"{m.split('_')[0]} {int(p[m].sum()):2d}/{len(p)}"
                          for m in meth)
        print(f"{outcome:8s}: {line}")

    print("\n=== country-level (any core pair certified net decline) ===")
    for outcome in OUTCOMES:
        p = pair[pair.outcome == outcome]
        cty = p.groupby("cntry")[meth].max()
        N = int(cty.M0_plugin.sum()); M = int(cty.M4_design.sum())
        dropped = sorted(cty.index[(cty.M0_plugin == 1) & (cty.M4_design == 0)])
        print(f"{outcome}: plug-in flags N={N} countries, design-aware "
              f"certifies M={M}. Reclassified to inconclusive (N−M="
              f"{len(dropped)}): {dropped}")

    # reclassification vs design uncertainty
    print("\n=== reclassified pairs: are they the high-design-uncertainty ones? ===")
    for outcome in OUTCOMES:
        p = pair[(pair.outcome == outcome) & (pair.M0_plugin == 1)].copy()
        p["reclassified"] = (p.M4_design == 0).astype(int)
        if len(p) and p.reclassified.nunique() == 2:
            kept, drop = p[p.reclassified == 0], p[p.reclassified == 1]
            print(f"{outcome}: plug-in-certified pairs kept by DA (n={len(kept)}) "
                  f"vs reclassified (n={len(drop)}): "
                  f"design_sd {kept.design_sd.mean():.4f} vs {drop.design_sd.mean():.4f}, "
                  f"n {kept.n0.mean():.0f} vs {drop.n0.mean():.0f}, "
                  f"signal {kept.signal.mean():.4f} vs {drop.signal.mean():.4f}")

    # trstprl vs stfdem agreement at country level
    piv = pair.groupby(["cntry", "outcome"]).M4_design.max().unstack()
    both = piv.dropna()
    if {"trstprl", "stfdem"} <= set(both.columns):
        agree = int(((both.trstprl == 1) & (both.stfdem == 1)).sum())
        only_t = int(((both.trstprl == 1) & (both.stfdem == 0)).sum())
        only_s = int(((both.trstprl == 0) & (both.stfdem == 1)).sum())
        print(f"\ndesign-aware decline agreement: both {agree}, "
              f"trust-only {only_t}, satisfaction-only {only_s}")


if __name__ == "__main__":
    main()
