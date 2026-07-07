"""E18 — Gate 5D #3: design-preserving semi-synthetic regime experiment.

Preregistered in docs/SEMISYNTHETIC_PROTOCOL.md. NOT a real-data high-ρ
validation: LAPOP's real STRATA/PSU/weights are preserved while UPMs are
subsampled at fractions f, raising design noise (~1/√f) and hence ρ. Shows the
target-blind selector move PCB → deconvolution → conservative fallback across
ρ₀=0.47, and the adaptive pipeline hold coverage throughout. Change-transport
setting (highest-ρ real regime). Pseudo-truth = full-sample (f=1) estimate;
center μ = full-sample grand mean, fixed.

Run:  python -m pcb.experiments.e18_semisynthetic
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed
import pandas as pd

from pcb.data.audit_lapop import audit, load
from pcb.experiments.e15_lapop_certify import OUTCOMES, _core_mask, _series, _thr
from pcb.experiments.e16_lapop_transport import _radii, _select, _wcdf_core
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import _finite_quantile

ALPHA = 0.10
Z = 1.645
FRACTIONS = [1.0, 0.5, 0.25, 0.125, 0.0625]
R_REP = 30
B_DESIGN = 150


def _prep(df, a, outcome, cfg):
    """Per country: list of adjacent-core change pairs as raw (y,w,strata,upm)."""
    thr, core = _thr(cfg), _core_mask(cfg)
    pairs = {}
    for pais, g in df.groupby("pais", observed=True):
        years = sorted(y for y in g.year.unique()
                       if a.loc[(pais, y), "sample"] == "core")
        recs = []
        for y0, y1 in zip(years, years[1:]):
            rr = []
            ok = True
            for yr in (y0, y1):
                gy = g[g.year == yr]
                y, w = _series(gy, outcome), gy["wt"].where(gy["wt"] >= 0)
                m = (y.notna() & w.notna()).to_numpy()
                if m.sum() < 200:
                    ok = False; break
                rr.append((y.to_numpy()[m], w.to_numpy()[m],
                           gy["strata"].to_numpy()[m], gy["upm"].to_numpy()[m]))
            if ok:
                recs.append(tuple(rr))
        if recs:
            pairs[int(pais)] = recs
    return pairs, thr, core


def _sub(rows, f, rng):
    """Keep fraction f of UPMs within each stratum (design-preserving)."""
    y, w, st, up = rows
    if f >= 1.0:
        return rows
    keep = np.zeros(len(y), bool)
    for s in np.unique(st):
        idx = np.flatnonzero(st == s)
        u = np.unique(up[idx])
        k = max(1, int(round(len(u) * f)))
        sel = set(rng.choice(u, size=min(k, len(u)), replace=False).tolist())
        keep[idx] = np.array([x in sel for x in up[idx]])
    return y[keep], w[keep], st[keep], up[keep]


def _cdf_v(rows, thr, core, rng):
    """Weighted core CDF and design SD (stratified-PSU bootstrap) of a subsample."""
    y, w, st, up = rows
    ind = w[:, None] * (y[:, None] <= thr[None, :])
    key = pd.MultiIndex.from_arrays([st, up])
    grp = pd.DataFrame(np.column_stack([ind, w]), index=key).groupby(level=[0, 1]).sum()
    cnt, tot = grp.values[:, :len(thr)], grp.values[:, len(thr)]
    strat = grp.index.get_level_values(0).to_numpy()
    bc = np.zeros((B_DESIGN, len(thr))); bt = np.zeros(B_DESIGN)
    for s in np.unique(strat):
        r = np.flatnonzero(strat == s); m = len(r)
        j = r[rng.integers(0, m, size=(B_DESIGN, m))] if m > 1 else np.broadcast_to(r, (B_DESIGN, 1))
        bc += cnt[j].sum(1); bt += tot[j].sum(1)
    F = (cnt.sum(0) / tot.sum())[core]
    v = (bc / bt[:, None]).std(0)[core]
    return F, v


def _country_change(pairs, thr, core, f, rng):
    """Per country: change curves D and design SD over its pairs, at fraction f."""
    D, V = {}, {}
    for c, recs in pairs.items():
        dd, vv = [], []
        for r0, r1 in recs:
            F0, v0 = _cdf_v(_sub(r0, f, rng), thr, core, rng)
            F1, v1 = _cdf_v(_sub(r1, f, rng), thr, core, rng)
            dd.append(F1 - F0); vv.append(np.sqrt(v0**2 + v1**2))
        D[c] = np.array(dd); V[c] = np.array(vv)
    return D, V


def run():
    df, _ = load()
    a = audit(df).set_index(["pais", "year"])
    df = df[df.year != 2021]
    rows_out = []
    for outcome, cfg in OUTCOMES.items():
        pairs, thr, core = _prep(df, a, outcome, cfg)
        # full-sample pseudo-truth curves + fixed center
        rng0 = np.random.default_rng(11)
        Dfull, _ = _country_change(pairs, thr, core, 1.0, rng0)
        mu = np.vstack([Dfull[c] for c in Dfull]).mean(0)
        countries = list(pairs)
        ar = np.arange
        for f in FRACTIONS:
            for rep in range(R_REP):
                rng = np.random.default_rng(det_seed(outcome, f, rep))
                D, V = _country_change(pairs, thr, core, f, rng)
                for tgt in countries:
                    E, Vc = [], []
                    for c in countries:
                        if c == tgt:
                            continue
                        dev = D[c] - mu[None, :]
                        j = np.argmax(np.abs(dev), axis=0)
                        E.append(dev[j, ar(dev.shape[1])]); Vc.append(V[c][j, ar(dev.shape[1])])
                    E, Vc = np.array(E), np.array(Vc)
                    if len(E) < 5:
                        continue
                    r = _radii(E, Vc); s, sT = r["s"], r["sT"]
                    branch, w_ad = _select(r)
                    q2 = _finite_quantile(np.max((np.abs(E) + Z * Vc) / s[None], axis=1), ALPHA)
                    # pseudo-truth target score (full sample) vs fixed center
                    devT = Dfull[tgt] - mu[None, :]
                    t_pcb = np.max(np.abs(devT) / s[None], axis=1).max()
                    t_dec = np.max(np.abs(devT) / sT[None], axis=1).max()
                    # adaptive coverage uses the chosen branch's studentisation/quantile
                    if branch == "T3":
                        cov_ad = int(t_dec <= r["q3"])
                    elif branch == "T2":
                        cov_ad = int(t_pcb <= q2)
                    else:
                        cov_ad = int(t_pcb <= r["q1"])
                    rows_out.append(dict(
                        outcome=outcome, f=f, rep=rep, target=tgt, rho=r["rho"],
                        branch=branch, stable=r["stable"], w_adaptive=w_ad,
                        w_cons=r["w2"], cov_adaptive=cov_ad,
                        cov_T1=int(t_pcb <= r["q1"]), cov_T2=int(t_pcb <= q2),
                        cov_T3=int(t_dec <= r["q3"])))
    return pd.DataFrame(rows_out)


def main():
    os.makedirs("results", exist_ok=True)
    d = run()
    d.to_csv("results/lapop_semisynthetic.csv", index=False)

    print("Design-preserving semi-synthetic regime sweep (change transport, "
          "LAPOP real STRATA/PSU preserved)\n")
    g = d.groupby("f")
    summ = pd.DataFrame(dict(
        rho=g.rho.mean(),
        pct_PCB=g.branch.apply(lambda s: (s == "T1").mean() * 100),
        pct_deconv=g.branch.apply(lambda s: (s == "T3").mean() * 100),
        pct_cons=g.branch.apply(lambda s: (s == "T2").mean() * 100),
        cov_adaptive=g.cov_adaptive.mean(),
        cov_conservative=g.cov_T2.mean(),
        w_adaptive=g.w_adaptive.mean(),
        w_conservative=g.w_cons.mean(),
    )).reset_index().sort_values("f", ascending=False)
    pd.set_option("display.width", 200, "display.float_format", lambda x: f"{x:.3f}")
    print(summ.to_string(index=False))
    print(f"\nρ₀ = 0.47 (fixed). Rows: {len(d)}. "
          f"Deconv activates where ρ̂ ≥ ρ₀ and stable; conservative fallback where "
          f"unstable.")


if __name__ == "__main__":
    main()
