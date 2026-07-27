"""E24 — does the deconvolution branch EVER activate on real ESS data?

The design-preserving stress test (e18) shows country-level ρ saturates near 0.23
because s_plug² = s_R² + v̄²: shrinking the sample inflates the observed spread and
the design noise in lockstep. This scan asks the sharper question the paper needs an
answer to: is there ANY real subpopulation cell where the design noise is large
enough — relative to the between-country transport spread — that ρ̂ crosses ρ₀ = 0.47
AND enough countries qualify for the finite-K safety gate to pass, so the deployed
selector actually rides deconvolution?

Mechanism we are hunting: design noise v is largest in small subpopulations (youth,
narrow age bands); the between-country transport spread s_R may be smaller there if
subgroup attitudes are more alike across countries. Lowering the min-cell floor
raises BOTH v (smaller cells) and K (more countries qualify) — the only regime that
could satisfy gate A and gate B at once.

This is EXPLORATORY (development), not a confirmatory validation: we report the full
ρ̂ distribution over every (subgroup × outcome × min-n) cell, exactly as produced, and
whether dapcb ever returns selected_branch == 'deconvolution'. No constant is tuned.

Run:  python -m pcb.experiments.e24_subgroup_rho_scan
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.data.audit_ess import audit, load, COLS
from pcb.dapcb import dapcb, RHO0
from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import rho_lcb

OUTCOMES = ("trstprl", "stfdem")
T = 10
CORE = np.array([1, 2, 3, 4])            # low-trust core thresholds t ∈ {1,2,3,4}
B_DESIGN = 500                           # stratified-PSU bootstrap draws per cell
MIN_NS = (80, 120, 200)                  # min valid responses per subgroup cell

# age-band subgroups, narrowest (noisiest) first
SUBGROUPS = {
    "youth_18_24":  lambda a: (a >= 18) & (a <= 24),
    "youth_18_29":  lambda a: (a >= 18) & (a <= 29),
    "young_25_34":  lambda a: (a >= 25) & (a <= 34),
    "mid_35_49":    lambda a: (a >= 35) & (a <= 49),
    "older_50_64":  lambda a: (a >= 50) & (a <= 64),
    "oldest_65p":   lambda a: (a >= 65),
    "full_18plus":  lambda a: (a >= 18),
}


RESCALE = False   # Rao-Wu-Yue rescaling: draw m-1 PSUs per stratum with replacement
                  # and scale stratum sums by m/(m-1); unbiases the between-PSU
                  # variance that plain m-of-m understates. Flip via e38 only.

def _wcdf_core(y, w):
    ind = y[:, None] <= CORE[None, :]
    return (w[:, None] * ind).sum(0) / w.sum()


def _design_sd_core(y, w, stratum, psu, rng, B=B_DESIGN):
    """Stratified-PSU (Rao–Wu) bootstrap SD of the core weighted CDF → (len(CORE),)."""
    ind = w[:, None] * (y[:, None] <= CORE[None, :])
    key = pd.MultiIndex.from_arrays([stratum, psu])
    g = pd.DataFrame(np.column_stack([ind, w]), index=key).groupby(level=[0, 1]).sum()
    cnt, tot = g.values[:, :len(CORE)], g.values[:, len(CORE)]
    strat = g.index.get_level_values(0).to_numpy()
    bc = np.zeros((B, len(CORE))); bt = np.zeros(B)
    for s in np.unique(strat):
        rows = np.flatnonzero(strat == s); m = len(rows)
        if m > 1 and RESCALE:
            f = m / (m - 1.0)
            idx = rows[rng.integers(0, m, size=(B, m - 1))]
            bc += cnt[idx].sum(1) * f; bt += tot[idx].sum(1) * f
            continue
        idx = rows[rng.integers(0, m, size=(B, m))] if m > 1 else \
            np.broadcast_to(rows, (B, 1))
        bc += cnt[idx].sum(1); bt += tot[idx].sum(1)
    return (bc / bt[:, None]).std(0)


def _cells(dfg, outcome, sg, min_n):
    """Per (country, round) with ≥min_n valid responses: (F_core, v_core)."""
    cells = {}
    for (c, r), g in dfg.groupby(["cntry", "essround"], observed=True):
        ok = g[outcome].notna().to_numpy()
        if ok.sum() < min_n:
            continue
        yv = g[outcome].to_numpy(float)[ok]
        wv = g["_w"].to_numpy(float)[ok]
        st = g["stratum"].to_numpy()[ok]; ps = g["psu"].to_numpy()[ok]
        if len(np.unique(st)) < 1 or len(np.unique(ps)) < 2:
            continue
        rng = np.random.default_rng(det_seed("e24", outcome, sg, min_n, str(c), int(r)))
        cells[(str(c), int(r))] = (_wcdf_core(yv, wv),
                                   _design_sd_core(yv, wv, st, ps, rng))
    return cells


def _transport_EV(cells):
    """Collapse to cross-country transport errors E and design SDs V (K, len(CORE)).

    DEPLOYMENT-mode centers: this scan feeds `dapcb` with `mu` as the center
    for a hypothetical unsurveyed target, so each calibration country's
    deviation must be taken against a LEAVE-ONE-OUT center (excluding its own
    rows), mirroring how the target sits outside the calibration pool. A
    grand-mean center here would shrink each calibration deviation by
    (K−1)/K relative to the target's — the self-inclusion asymmetry that
    biases the conformal quantile downward (see
    `pcb.inference.conformal_band.loo_deviations`). Per country keep the
    max-|dev| round per threshold — the LOCO transport construction of e16.
    (Shipped CSVs predating this fix used the grand-mean center; the ρ/gate
    diagnostics they report are insensitive to the O(1/K) center shift, but
    any coverage-bearing rerun should use this construction.)"""
    countries = sorted({k[0] for k in cells})
    Fmat = {c: np.array([cells[k][0] for k in cells if k[0] == c]) for c in countries}
    Vmat = {c: np.array([cells[k][1] for k in cells if k[0] == c]) for c in countries}
    allF = np.vstack([Fmat[c] for c in countries])
    tot, n_tot = allF.sum(0), allF.shape[0]
    mu = tot / n_tot
    E, V = [], []
    for c in countries:
        n_c = Fmat[c].shape[0]
        mu_loo = (tot - Fmat[c].sum(0)) / (n_tot - n_c)   # excludes c's own rows
        dev = Fmat[c] - mu_loo[None, :]
        j = np.argmax(np.abs(dev), axis=0)
        E.append(dev[j, np.arange(dev.shape[1])])
        V.append(Vmat[c][j, np.arange(dev.shape[1])])
    return np.array(E), np.array(V), mu, countries


def scan():
    df = load(COLS + ["agea"])
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0) & df["agea"].notna()]
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    # keep only country-rounds with a usable complex design (core sample)
    core_keys = set(klass[klass == "core"].index)
    age = df["agea"].to_numpy(float)

    rows = []
    for sg, mask in SUBGROUPS.items():
        dsg = df[mask(age)]
        for min_n in MIN_NS:
            for outcome in OUTCOMES:
                cells = _cells(dsg, outcome, sg, min_n)
                cells = {k: v for k, v in cells.items() if k in core_keys}
                K = len({k[0] for k in cells})
                if K < 4:
                    continue
                E, V, mu, countries = _transport_EV(cells)
                s = _modulation(E)
                rho_hat = float(np.sqrt((V**2).mean()) / s.mean())
                rl = float(rho_lcb(E, V))
                fit = dapcb(E, V, mu, alpha=0.10, tighten=False)
                rows.append(dict(
                    subgroup=sg, outcome=outcome, min_n=min_n, K=K,
                    rho_hat=rho_hat, rho_lcb=rl, D=fit.reliability,
                    delta_ucb=fit.delta_ucb, branch=fit.selected_branch,
                    gate_A=rl > RHO0, coverage_level=fit.coverage_level,
                    v_mean=float(np.sqrt((V**2).mean())), s_mean=float(s.mean())))
    return pd.DataFrame(rows)


def main():
    os.makedirs("results", exist_ok=True)
    d = scan()
    d.to_csv("results/ess_subgroup_rho_scan.csv", index=False)
    pd.set_option("display.width", 200, "display.max_rows", 200,
                  "display.float_format", lambda x: f"{x:.3f}")
    print("ESS subgroup transport-ρ scan (core design cells, low-trust core "
          "thresholds, α=0.10)\n")
    cols = ["subgroup", "outcome", "min_n", "K", "rho_hat", "rho_lcb", "D",
            "delta_ucb", "gate_A", "branch"]
    print(d.sort_values("rho_lcb", ascending=False)[cols].to_string(index=False))
    print(f"\nρ₀ = {RHO0}.  cells scanned: {len(d)}")
    print(f"max ρ̂       = {d.rho_hat.max():.3f}   "
          f"(subgroup {d.loc[d.rho_hat.idxmax(),'subgroup']}, "
          f"{d.loc[d.rho_hat.idxmax(),'outcome']}, K={d.loc[d.rho_hat.idxmax(),'K']})")
    print(f"max ρ̂_LCB   = {d.rho_lcb.max():.3f}   "
          f"(subgroup {d.loc[d.rho_lcb.idxmax(),'subgroup']}, "
          f"{d.loc[d.rho_lcb.idxmax(),'outcome']}, K={d.loc[d.rho_lcb.idxmax(),'K']})")
    n_gateA = int(d.gate_A.sum())
    n_deconv = int((d.branch == "deconvolution").sum())
    print(f"cells passing gate A (ρ̂_LCB > ρ₀): {n_gateA} / {len(d)}")
    print(f"cells the selector routes to DECONVOLUTION: {n_deconv} / {len(d)}")
    if n_deconv:
        print("\n*** DECONVOLUTION ACTIVATES ON REAL DATA ***")
        print(d[d.branch == "deconvolution"][cols].to_string(index=False))
    else:
        print("\nNo real cell activates deconvolution — the method stays inert / "
              "abstains on ESS, as the saturation argument predicts.")


if __name__ == "__main__":
    main()
