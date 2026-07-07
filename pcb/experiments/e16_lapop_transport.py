"""E16 — Gate 5D Part B: Candidate B cross-country TRANSPORT validation on LAPOP.

Preregistered in docs/LAPOP_PART_B_PROTOCOL.md. The leave-one-country-out (LOCO)
transport experiment that actually exercises Candidate B deconvolution: source
surveys' complex-design error is removed from the transport-score distribution.
Calibration unit = country (one score). Methods T1 PCB / T2 worst-case / T3
Candidate B / T4 fallback (Oracle is simulation-only, absent here).

No coverage claim on LAPOP: report width ratios, by-ρ terciles, fallback rate,
and a design-resampling STRESS TEST (pseudo-truth = full weighted estimate,
resample preserving real STRATA-PSU) — named a stress test, not coverage.

Run:  python -m pcb.experiments.e16_lapop_transport
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed
import pandas as pd

from pcb.data.audit_lapop import audit, load
from pcb.experiments.e15_lapop_certify import OUTCOMES, _core_mask, _series, _thr
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import _finite_quantile

ALPHA = 0.10
Z = 1.645                      # design-interval half-width (90%) for T2 envelope
RHO0 = 0.47                    # Gate-5C fallback cutoff (SD ratio) — fixed
FLOOR_FRAC = 0.05
B_DESIGN = 400                 # PSU-bootstrap draws for design SD
B_STRESS = 300                 # design-resampling stress-test replications


def _wcdf_core(y, w, thr, core):
    return ((w[:, None] * (y[:, None] <= thr[None, :])).sum(0) / w.sum())[core]


def _design_draws(y, w, strata, upm, thr, core, n, rng):
    """n stratified-PSU-bootstrap draws of the core weighted CDF → (n, Tc)."""
    ind = w[:, None] * (y[:, None] <= thr[None, :])
    key = pd.MultiIndex.from_arrays([strata, upm])
    grp = pd.DataFrame(np.column_stack([ind, w]), index=key).groupby(level=[0, 1]).sum()
    cnt, tot = grp.values[:, :len(thr)], grp.values[:, len(thr)]
    strat = grp.index.get_level_values(0).to_numpy()
    bc = np.zeros((n, len(thr))); bt = np.zeros(n)
    for s in np.unique(strat):
        rows = np.flatnonzero(strat == s); m = len(rows)
        idx = rows[rng.integers(0, m, size=(n, m))] if m > 1 else \
            np.broadcast_to(rows, (n, 1))
        bc += cnt[idx].sum(1); bt += tot[idx].sum(1)
    return (bc / bt[:, None])[:, core]


def _cells(df, a, outcome, cfg):
    """Per core (country,year): full core-CDF, design SD, and stress draws."""
    thr, core = _thr(cfg), _core_mask(cfg)
    out = {}
    for (pais, year), g in df.groupby(["pais", "year"], observed=True):
        if a.loc[(pais, year), "sample"] != "core":
            continue
        y, w = _series(g, outcome), g["wt"].where(g["wt"] >= 0)
        m = y.notna() & w.notna()
        if m.sum() < 200:
            continue
        yv, wv = y[m].to_numpy(), w[m].to_numpy()
        st = g["strata"].to_numpy()[m.to_numpy()]; up = g["upm"].to_numpy()[m.to_numpy()]
        rng = np.random.default_rng(det_seed(outcome, pais, year))
        draws = _design_draws(yv, wv, st, up, thr, core, B_DESIGN, rng)
        out[(int(pais), int(year))] = dict(
            country=g["country"].iloc[0],
            F=_wcdf_core(yv, wv, thr, core), v=draws.std(0),
            stress=_design_draws(yv, wv, st, up, thr, core, B_STRESS, rng))
    return out


def _country_traj(cells):
    """Collapse to per-country (max-|dev|-over-rounds) arrays vs LOCO center."""
    countries = sorted({k[0] for k in cells})
    Fmat = {c: np.array([cells[k]["F"] for k in cells if k[0] == c]) for c in countries}
    Vmat = {c: np.array([cells[k]["v"] for k in cells if k[0] == c]) for c in countries}
    allF = np.vstack([Fmat[c] for c in countries])
    mu = allF.mean(0)
    name = {c: next(cells[k]["country"] for k in cells if k[0] == c) for c in countries}
    return countries, Fmat, Vmat, mu, name


def _E_V(countries, Fmat, Vmat, mu, target):
    """(K-1, Tc) transport errors E and design SDs V over source countries."""
    E, V = [], []
    for c in countries:
        if c == target:
            continue
        muc = mu  # grand mean center (target-blind; ~mu^{-c}, K large)
        dev = Fmat[c] - muc[None, :]                 # (rounds, Tc)
        j = np.argmax(np.abs(dev), axis=0)           # max-|dev| round per t
        E.append(dev[j, np.arange(dev.shape[1])])
        V.append(Vmat[c][j, np.arange(dev.shape[1])])
    return np.array(E), np.array(V)


def _radii(E, V):
    """Half-width vectors (mean over t) for T1, T2, T3 + ρ̂ + stability."""
    s = _modulation(E)
    floor = (FLOOR_FRAC * s.max()) ** 2
    sT = np.sqrt(np.maximum(s**2 - (V**2).mean(0), floor))
    stable = (s**2 - (V**2).mean(0) > floor).all()
    q1 = _finite_quantile(np.max(np.abs(E) / s[None], axis=1), ALPHA)
    q2 = _finite_quantile(np.max((np.abs(E) + Z * V) / s[None], axis=1), ALPHA)
    q3 = _finite_quantile(np.max(np.abs(E) / np.sqrt(sT[None]**2 + V**2), axis=1), ALPHA)
    rho = float(np.sqrt((V**2).mean()) / s.mean())
    return dict(w1=float(q1 * s.mean()), w2=float(q2 * s.mean()),
                w3=float(q3 * sT.mean()), rho=rho, stable=bool(stable),
                q1=q1, q3=q3, s=s, sT=sT)


def _select(r):
    if r["rho"] < RHO0:
        return "T1", r["w1"]
    return ("T3", r["w3"]) if r["stable"] else ("T2", r["w2"])


def transport():
    df, _ = load()
    a = audit(df).set_index(["pais", "year"])
    df = df[df.year != 2021]
    rows = []
    for outcome, cfg in OUTCOMES.items():
        cells = _cells(df, a, outcome, cfg)
        countries, Fmat, Vmat, mu, name = _country_traj(cells)
        for tgt in countries:
            E, V = _E_V(countries, Fmat, Vmat, mu, tgt)
            r = _radii(E, V)
            pick, wsel = _select(r)
            rows.append(dict(outcome=outcome, target=tgt, country=name[tgt],
                             rho=r["rho"], stable=r["stable"],
                             w_T1=r["w1"], w_T2=r["w2"], w_T3=r["w3"],
                             chosen=pick, w_T4=wsel,
                             ratio_T3_T1=r["w3"] / r["w1"],
                             ratio_T3_T2=r["w3"] / r["w2"]))
    return pd.DataFrame(rows)


def stress_test(outcome="b13"):
    """Design-resampling stress test (pseudo-coverage, NOT finite-pop coverage).

    Full weighted estimate per country = pseudo-truth. Each replication draws a
    strata-PSU subsample of every country; source scores build each method's
    quantile (LOCO); coverage = pseudo-truth target score ≤ that quantile, under
    each method's own studentisation (T2 adds the design envelope). Reports
    pseudo-coverage and mean width per method.
    """
    df, _ = load()
    a = audit(df).set_index(["pais", "year"])
    df = df[df.year != 2021]
    cells = _cells(df, a, outcome, OUTCOMES[outcome])
    countries, Fmat, Vmat, mu, name = _country_traj(cells)
    Sdraws = {c: np.stack([cells[k]["stress"] for k in cells if k[0] == c], 0)
              for c in countries}   # (rounds, B_STRESS, Tc)
    ar = np.arange
    cov = {m: 0 for m in ("T1", "T2", "T3")}
    wid = {m: [] for m in ("T1", "T2", "T3")}
    tot = 0
    for tgt in countries:
        devT = Fmat[tgt] - mu[None, :]                    # full-sample truth dev
        for b in range(B_STRESS):
            E, V = [], []
            for c in countries:
                if c == tgt:
                    continue
                dev = Sdraws[c][:, b, :] - mu[None, :]     # subsample dev
                j = np.argmax(np.abs(dev), axis=0)
                E.append(dev[j, ar(dev.shape[1])]); V.append(Vmat[c][j, ar(dev.shape[1])])
            r = _radii(np.array(E), np.array(V))
            s, sT = r["s"], r["sT"]
            q2 = _finite_quantile(np.max((np.abs(np.array(E)) + Z * np.array(V))
                                         / s[None], axis=1), ALPHA)
            truth1 = np.max(np.abs(devT) / s[None], axis=1).max()   # max over r,t
            truth3 = np.max(np.abs(devT) / sT[None], axis=1).max()
            cov["T1"] += int(truth1 <= r["q1"]); wid["T1"].append(r["q1"] * s.mean())
            cov["T2"] += int(truth1 <= q2); wid["T2"].append(q2 * s.mean())
            cov["T3"] += int(truth3 <= r["q3"]); wid["T3"].append(r["q3"] * sT.mean())
            tot += 1
    return pd.DataFrame([dict(method=m, pseudo_coverage=cov[m] / tot,
                              mean_width=float(np.mean(wid[m]))) for m in cov])


def main():
    os.makedirs("results", exist_ok=True)
    loco = transport()
    loco.to_csv("results/lapop_transport_loco.csv", index=False)

    print(f"LAPOP Part B — LOCO transport, {loco.target.nunique()} target "
          f"countries × {loco.outcome.nunique()} outcomes\n")
    print("=== width by method and Candidate-B ratios (mean half-width) ===")
    for o in OUTCOMES:
        p = loco[loco.outcome == o]
        print(f"{o:5s}: T1 {p.w_T1.mean():.4f} | T2 {p.w_T2.mean():.4f} | "
              f"T3 {p.w_T3.mean():.4f} | T3/T1 {p.ratio_T3_T1.mean():.3f} | "
              f"T3/T2 {p.ratio_T3_T2.mean():.3f} | ρ̄ {p.rho.mean():.3f}")

    print("\n=== by ρ tercile (T3/T1 reduce-to-PCB, T3/T2 beat-conservative) ===")
    rho_rows = []
    for o in OUTCOMES:
        p = loco[loco.outcome == o].copy()
        p["tercile"] = pd.qcut(p.rho, 3, labels=["low", "mid", "high"])
        for terc, q in p.groupby("tercile", observed=True):
            rho_rows.append(dict(outcome=o, tercile=str(terc), n=len(q),
                                 rho=q.rho.mean(), T3_T1=q.ratio_T3_T1.mean(),
                                 T3_T2=q.ratio_T3_T2.mean()))
            print(f"{o:5s} {str(terc):4s} (n={len(q):2d}): ρ̄ {q.rho.mean():.3f} | "
                  f"T3/T1 {q.ratio_T3_T1.mean():.3f} | T3/T2 {q.ratio_T3_T2.mean():.3f}")
    pd.DataFrame(rho_rows).to_csv("results/lapop_candidate_b_by_rho.csv", index=False)

    print("\n=== fallback routing (T4 selection) ===")
    print(loco.groupby(["outcome", "chosen"]).size().to_string())

    print("\n=== design-resampling stress test (pseudo-coverage, b13, α=0.10) ===")
    st = stress_test("b13")
    st.to_csv("results/lapop_design_resampling.csv", index=False)
    print(st.to_string(index=False))


if __name__ == "__main__":
    main()
