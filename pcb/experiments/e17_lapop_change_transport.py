"""E17 — Gate 5D Part C: change-function transport on LAPOP.

Part B transported LEVEL curves and found a low-ρ regime (between-country level
differences dwarf survey noise). Part C transports the wave-to-wave CHANGE curve

    D_{c,r}(t) = F_{c,r+1}(t) − F_{c,r}(t)   (adjacent core waves, same country),

whose cross-country spread may be much smaller than the level spread while the
design noise of a difference is ~√2 larger — so ρ_change = σ_design,Δ /
σ_cross-country,Δ can be materially higher, potentially activating the Candidate-B
deconvolution branch on real data. Preregistration carried over unchanged from
Part B (LAPOP_PART_B_PROTOCOL.md): same outcomes/thresholds/country set, calibration
unit = country, strict LOCO, ρ₀ = 0.47 NOT retuned, methods T1/T2/T3/T4.

If the change setting is ALSO low-ρ, that is reported as an empirical regime
characterization, not hidden.

Run:  python -m pcb.experiments.e17_lapop_change_transport
"""
from __future__ import annotations
import os

import numpy as np

from pcb.util import det_seed
import pandas as pd

from pcb.data.audit_lapop import audit, load
from pcb.experiments.e15_lapop_certify import OUTCOMES, _core_mask, _series, _thr
from pcb.experiments.e16_lapop_transport import (B_DESIGN, B_STRESS, RHO0,
                                                 _E_V, _design_draws, _radii,
                                                 _select, _wcdf_core)
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import _finite_quantile

ALPHA = 0.10
Z = 1.645


def _change_cells(df, a, outcome, cfg):
    """Per adjacent core pair: change curve D̃, its design SD, and stress draws."""
    thr, core = _thr(cfg), _core_mask(cfg)
    out = {}
    for pais, g in df.groupby("pais", observed=True):
        years = sorted(y for y in g.year.unique()
                       if a.loc[(pais, y), "sample"] == "core")
        for y0, y1 in zip(years, years[1:]):
            parts = {}
            ok = True
            draws_full = {}
            for tag, yr in (("0", y0), ("1", y1)):
                gy = g[g.year == yr]
                y, w = _series(gy, outcome), gy["wt"].where(gy["wt"] >= 0)
                m = y.notna() & w.notna()
                if m.sum() < 200:
                    ok = False; break
                yv, wv = y[m].to_numpy(), w[m].to_numpy()
                st = gy["strata"].to_numpy()[m.to_numpy()]
                up = gy["upm"].to_numpy()[m.to_numpy()]
                rng = np.random.default_rng(det_seed(outcome, pais, yr))
                parts[tag] = dict(F=_wcdf_core(yv, wv, thr, core),
                                  d=_design_draws(yv, wv, st, up, thr, core, B_DESIGN, rng),
                                  s=_design_draws(yv, wv, st, up, thr, core, B_STRESS, rng))
            if not ok:
                continue
            D = parts["1"]["F"] - parts["0"]["F"]                 # change curve
            vD = (parts["1"]["d"] - parts["0"]["d"]).std(0)       # design SD of Δ
            stress = parts["1"]["s"] - parts["0"]["s"]            # (B_STRESS, Tc)
            out[(int(pais), y0)] = dict(country=g["country"].iloc[0],
                                        F=D, v=vD, stress=stress)
    return out


def _country_arrays(cells):
    countries = sorted({k[0] for k in cells})
    Fmat = {c: np.array([cells[k]["F"] for k in cells if k[0] == c]) for c in countries}
    Vmat = {c: np.array([cells[k]["v"] for k in cells if k[0] == c]) for c in countries}
    mu = np.vstack([Fmat[c] for c in countries]).mean(0)
    name = {c: next(cells[k]["country"] for k in cells if k[0] == c) for c in countries}
    return countries, Fmat, Vmat, mu, name


def transport():
    df, _ = load()
    a = audit(df).set_index(["pais", "year"])
    df = df[df.year != 2021]
    rows = []
    for outcome, cfg in OUTCOMES.items():
        cells = _change_cells(df, a, outcome, cfg)
        countries, Fmat, Vmat, mu, name = _country_arrays(cells)
        for tgt in countries:
            E, V = _E_V(countries, Fmat, Vmat, mu, tgt)
            if len(E) < 5:
                continue
            r = _radii(E, V)
            pick, wsel = _select(r)
            rows.append(dict(outcome=outcome, target=tgt, country=name[tgt],
                             rho=r["rho"], stable=r["stable"], chosen=pick,
                             w_T1=r["w1"], w_T2=r["w2"], w_T3=r["w3"], w_T4=wsel,
                             ratio_T3_T1=r["w3"] / r["w1"],
                             ratio_T3_T2=r["w3"] / r["w2"]))
    return pd.DataFrame(rows)


def stress_test(outcome="b13"):
    df, _ = load()
    a = audit(df).set_index(["pais", "year"])
    df = df[df.year != 2021]
    cells = _change_cells(df, a, outcome, OUTCOMES[outcome])
    countries, Fmat, Vmat, mu, name = _country_arrays(cells)
    Sdraws = {c: np.stack([cells[k]["stress"] for k in cells if k[0] == c], 0)
              for c in countries}
    ar = np.arange
    cov = {m: 0 for m in ("T1", "T2", "T3")}; wid = {m: [] for m in cov}; tot = 0
    for tgt in countries:
        if len([k for k in cells if k[0] == tgt]) == 0:
            continue
        devT = Fmat[tgt] - mu[None, :]
        for b in range(B_STRESS):
            E, V = [], []
            for c in countries:
                if c == tgt:
                    continue
                dev = Sdraws[c][:, b, :] - mu[None, :]
                j = np.argmax(np.abs(dev), axis=0)
                E.append(dev[j, ar(dev.shape[1])]); V.append(Vmat[c][j, ar(dev.shape[1])])
            E, V = np.array(E), np.array(V)
            if len(E) < 5:
                continue
            r = _radii(E, V); s, sT = r["s"], r["sT"]
            q2 = _finite_quantile(np.max((np.abs(E) + Z * V) / s[None], axis=1), ALPHA)
            t1 = np.max(np.abs(devT) / s[None], axis=1).max()
            t3 = np.max(np.abs(devT) / sT[None], axis=1).max()
            cov["T1"] += int(t1 <= r["q1"]); wid["T1"].append(r["q1"] * s.mean())
            cov["T2"] += int(t1 <= q2); wid["T2"].append(q2 * s.mean())
            cov["T3"] += int(t3 <= r["q3"]); wid["T3"].append(r["q3"] * sT.mean())
            tot += 1
    return pd.DataFrame([dict(method=m, pseudo_coverage=cov[m] / tot,
                              mean_width=float(np.mean(wid[m]))) for m in cov])


def main():
    os.makedirs("results", exist_ok=True)
    loco = transport()
    loco.to_csv("results/lapop_change_transport.csv", index=False)

    print(f"LAPOP Part C — CHANGE-function transport, "
          f"{loco.target.nunique()} targets × {loco.outcome.nunique()} outcomes\n")
    print("=== ρ_change and Candidate-B routing by outcome ===")
    rho_rows = []
    for o in OUTCOMES:
        p = loco[loco.outcome == o]
        activ = (p.chosen != "T1").sum()
        print(f"{o:5s}: ρ_change mean {p.rho.mean():.3f} "
              f"[{p.rho.min():.3f},{p.rho.max():.3f}] | "
              f"≥ρ₀({RHO0}): {(p.rho >= RHO0).sum()}/{len(p)} | "
              f"branch≠T1: {activ}/{len(p)} | "
              f"T3/T1 {p.ratio_T3_T1.mean():.3f} | T3/T2 {p.ratio_T3_T2.mean():.3f}")
        rho_rows.append(dict(outcome=o, rho_mean=p.rho.mean(), rho_max=p.rho.max(),
                             n_ge_rho0=int((p.rho >= RHO0).sum()), n=len(p),
                             n_active=int(activ), T3_T1=p.ratio_T3_T1.mean(),
                             T3_T2=p.ratio_T3_T2.mean()))
    pd.DataFrame(rho_rows).to_csv("results/lapop_change_candidate_b_by_rho.csv",
                                  index=False)

    print("\n=== branch routing ===")
    print(loco.groupby(["outcome", "chosen"]).size().to_string())

    print("\n=== change-curve design-resampling stress test (b13) ===")
    st = stress_test("b13")
    st.to_csv("results/lapop_change_design_resampling.csv", index=False)
    print(st.to_string(index=False))


if __name__ == "__main__":
    main()
