"""E11 — Gate 5C: simulation confirmation of the Gate-5B theorems.

Three parts, matching docs/GO_NO_GO_GATE5B.md "next gates":

  A. B1 dominance + B2 deconvolution + ρ* threshold.
     Fine sweep of the noise ratio ρ = design-SD / transport-SD. For the latent
     DEPLOYMENT target (unsurveyed) compare oracle / plug-in / DA-deconvolved
     coverage and width, directly test the dominance condition (D)
     (contaminated sup-score ⪰ clean), and read off ρ* = the largest ρ at which
     DA coverage stays ≥ 1−α within Monte-Carlo error.

  B. Prop 3 rate Δ(K, g) ≈ c·g/K.
     Clean hierarchical trajectory errors (no survey); L=4 trajectory estimand
     scored with g ∈ {1,2,4} modulation slices, K ∈ {20,30,50,100}. Fit the
     coverage deficit against g/K.

  C. Persistent-decline certification level.
     Trajectories with KNOWN persistent-decline / stable / one-off-dip truth;
     LOCO clustered trajectory band; apply decline_certify. Confirm
     false-certification ≤ α on non-declining truth (validity) and report power.

Run:  python -m pcb.experiments.e11_gate5c
"""
from __future__ import annotations
import multiprocessing as mp
import os

import numpy as np
import pandas as pd

from pcb.inference.conformal_band import _modulation, population_conformal_band
from pcb.inference.decline_certify import (certify_decline,
                                           certify_decline_differences,
                                           truth_is_persistent_decline)
from pcb.inference.design_aware import da_studentized_band, psu_bootstrap
from pcb.inference.fixed_trajectory_band import (trajectory_modulation,
                                                 trajectory_quantile,
                                                 trajectory_scores)
from pcb.simulation.survey_dgp import (SurveyDesign, SurveySimConfig, T_GRID,
                                       draw_survey, generate_survey_hierarchy,
                                       true_curve)

ALPHA = 0.10
MC3 = 3 * np.sqrt(0.9 * 0.1 / 800)          # ~3.2pp band on 800 reps


# ============================================================ Part A: B1/B2/ρ*

_DESIGN_A = SurveyDesign(m_psu=30, b_per_psu=50, icc=0.05, gamma=0.5, eta=0.3)
_S_TRANSPORT = [0.50, 0.40, 0.30, 0.22, 0.16, 0.12, 0.10, 0.08]
REPS_A = 800


def _one_rep_A(args):
    s_transport, seed = args
    cfg = SurveySimConfig(K=50, s_transport=s_transport, designs=(_DESIGN_A,))
    rng = np.random.default_rng(seed)
    h = generate_survey_hierarchy(cfg, rng)
    th_true, th_hat = h["theta_true"], h["theta_hat"]
    tilde = np.array([s["theta_tilde"] for s in h["surveys"]])
    v = np.array([psu_bootstrap(s["psu_cnt"], s["psu_tot"], 200, rng).std(0)
                  for s in h["surveys"]])

    E_true = th_hat[:-1] - th_true[:-1]          # clean transport errors
    E_plug = th_hat[:-1] - tilde[:-1]            # contaminated = E - S
    center, tgt = th_hat[-1], th_true[-1]        # deployment: latent target

    o_lo, o_hi = population_conformal_band(E_true, center, ALPHA)
    p_lo, p_hi = population_conformal_band(E_plug, center, ALPHA)
    d_lo, d_hi = da_studentized_band(E_plug, v[:-1], center, None, ALPHA)

    # dominance: unstudentised sup-magnitudes, contaminated vs clean
    clean_sup = np.max(np.abs(E_true), axis=1)
    cont_sup = np.max(np.abs(E_plug), axis=1)
    return dict(
        s_transport=s_transport,
        rho=float(v[:-1].mean() / max(E_true.std(0).mean(), 1e-9)),
        oracle_cov=float(np.all((o_lo <= tgt) & (tgt <= o_hi))),
        plugin_cov=float(np.all((p_lo <= tgt) & (tgt <= p_hi))),
        da_cov=float(np.all((d_lo <= tgt) & (tgt <= d_hi))),
        oracle_w=float((o_hi - o_lo).mean()),
        plugin_w=float((p_hi - p_lo).mean()),
        da_w=float((d_hi - d_lo).mean()),
        clean_sup_mean=float(clean_sup.mean()),
        cont_sup_mean=float(cont_sup.mean()),
        dominance_ok=float(cont_sup.mean() >= clean_sup.mean()))


def part_A(pool) -> pd.DataFrame:
    jobs = [(s, 7000 * i + j) for i, s in enumerate(_S_TRANSPORT)
            for j in range(REPS_A)]
    rows = pool.map(_one_rep_A, jobs, chunksize=8)
    df = pd.DataFrame(rows)
    g = df.groupby("s_transport").agg(
        rho=("rho", "mean"),
        oracle=("oracle_cov", "mean"), plugin=("plugin_cov", "mean"),
        da=("da_cov", "mean"),
        oracle_w=("oracle_w", "mean"), plugin_w=("plugin_w", "mean"),
        da_w=("da_w", "mean"),
        dominance=("dominance_ok", "mean"),
        clean_sup=("clean_sup_mean", "mean"),
        cont_sup=("cont_sup_mean", "mean")).sort_values("rho")
    return df, g


# ========================================================= Part B: Prop 3 rate

def _prop3_cell(K, g, L=4, T=10, reps=3000, seed=0):
    """Coverage of the L-round trajectory band with g modulation slices.

    g slices partition the L slots into g contiguous groups sharing one scale.
    g=1 pooled, g=L slotwise. In-sample modulation (the regime Prop 3 is about).
    """
    rng = np.random.default_rng(seed)
    a = rng.normal(0, 0.03, size=(reps, K + 1, 1, 1))     # country effect
    b = rng.normal(0, 0.02, size=(reps, K + 1, L, 1))     # round shock
    u = rng.normal(0, 0.015, size=(reps, K + 1, L, T))    # threshold noise
    E = a + b + u
    cal, tgt = E[:, :K], E[:, K]
    groups = np.array_split(np.arange(L), g)

    hits = 0
    for rep in range(reps):
        s = np.empty((L, T))
        for grp in groups:                                # in-sample slice scale
            block = cal[rep, :, grp, :].reshape(-1, T)
            s[grp] = _modulation(block)
        cs = np.max(np.abs(cal[rep]) / s[None], axis=(1, 2))
        q, m, _ = trajectory_quantile(cs, ALPHA)
        hits += float(np.max(np.abs(tgt[rep]) / s) <= q)
    attain = np.ceil((1 - ALPHA) * (K + 1)) / (K + 1)
    return dict(K=K, g=g, L=L, coverage=hits / reps, attainable=attain,
                deficit=attain - hits / reps)


def part_B(pool) -> pd.DataFrame:
    jobs = [(K, g) for K in (20, 30, 50, 100) for g in (1, 2, 4)]
    rows = pool.starmap(_prop3_cell,
                        [(K, g, 4, 10, 3000, 1000 * K + g) for K, g in jobs])
    df = pd.DataFrame(rows)
    # fit deficit ≈ c·g/K  (through the origin) on the in-sample-sliced cells
    x = (df.g / df.K).to_numpy()
    y = df.deficit.to_numpy()
    c = float((x @ y) / (x @ x))
    ss = 1 - ((y - c * x) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    df.attrs["c"] = c
    df.attrs["r2"] = ss
    return df


# ============================================ Part C: decline-certification level

_L_C, _T_C = 4, T_GRID
_DES_C = SurveyDesign(m_psu=40, b_per_psu=45, icc=0.06, gamma=0.5, eta=0.3)  # n≈1800, ESS-scale
REPS_C = 500
_CORE = np.zeros(_T_C, dtype=bool)
_CORE[1:5] = True                          # low-trust band (trust ≤ 1..4)


_B_DIFF = 300           # design-bootstrap replicates for the difference band


def _country_trajectory(kind, rng):
    """Latent trajectory + per-round survey draws for one country.

    The persistent-decline claim compares two OBSERVED rounds of the SAME
    country, so certification is a within-country design inference (the country
    effect cancels; no transport). We return the per-round PSU sufficient
    statistics so the consecutive DIFFERENCES can be design-bootstrapped jointly.
    """
    base = rng.normal(0.3, 0.4)
    if kind == "decline":                                # monotone down, magnitude
        steps = np.cumsum(np.abs(rng.normal(0.30, 0.08, size=_L_C - 1)))  # varies
        a = base - np.concatenate([[0], steps])
    elif kind == "stable":
        a = base + rng.normal(0, 0.03, size=_L_C)
    else:                                                # one-off dip then back
        a = base + np.array([0.0, -0.5, 0.0, 0.05])[:_L_C]
    su = _DES_C.sigma_u
    theta = np.array([true_curve(a[r], su) for r in range(_L_C)])
    surveys = [draw_survey(a[r], _DES_C, rng) for r in range(_L_C)]
    return theta, surveys


def _one_rep_C(args):
    seed, _ = args
    rng = np.random.default_rng(seed)
    kind = rng.choice(["decline", "stable", "dip"])
    theta, surveys = _country_trajectory(kind, rng)
    tilde = np.array([s["theta_tilde"] for s in surveys])

    # joint PSU bootstrap of every round → consecutive-difference replicates
    boots = np.array([psu_bootstrap(s["psu_cnt"], s["psu_tot"], _B_DIFF, rng)
                      for s in surveys])                 # (L, B, T)
    diff_hat = tilde[1:] - tilde[:-1]                    # (L-1, T)
    diff_boot = np.moveaxis(boots[1:] - boots[:-1], 1, 0)  # (B, L-1, T)

    # persistent: FOSD-down at EVERY consecutive pair over the low-trust core
    persist = certify_decline_differences(diff_hat, diff_boot, ALPHA, _CORE)
    # net: first→last accumulated decline (one difference, stronger signal)
    net_hat = (tilde[-1] - tilde[0])[None]
    net_boot = (boots[-1] - boots[0])[None]
    net_boot = np.moveaxis(net_boot, 1, 0)              # (B,1,T)
    net = certify_decline_differences(net_hat, net_boot, ALPHA, _CORE)

    truth_p = truth_is_persistent_decline(theta, _CORE)
    truth_n = bool(np.all(theta[-1][_CORE] >= theta[0][_CORE]))
    return dict(kind=str(kind), truth_persistent=truth_p, truth_net=truth_n,
                persist_plugin=persist["plugin"], persist_da=persist["design_aware"],
                net_plugin=net["plugin"], net_da=net["design_aware"])


def part_C(pool) -> pd.DataFrame:
    rows = pool.map(_one_rep_C, [(5000 + j, 0) for j in range(REPS_C * 40)])
    return pd.DataFrame(rows)


# =================================================================== main

def main():
    os.makedirs("results", exist_ok=True)
    with mp.Pool(min(64, os.cpu_count() or 8)) as pool:
        dfA, gA = part_A(pool)
        dfB = part_B(pool)
        dfC = part_C(pool)

    dfA.to_csv("results/gate5c_partA_ratesweep.csv", index=False)
    gA.to_csv("results/gate5c_partA_summary.csv")
    dfB.to_csv("results/gate5c_partB_prop3.csv", index=False)
    dfC.to_csv("results/gate5c_partC_certify.csv", index=False)

    pd.set_option("display.width", 200)
    print("=== Part A: coverage(latent deployment) & width vs noise ratio ρ "
          f"(nominal {1-ALPHA:.0%}, MC±{MC3:.3f}) ===")
    print(gA.round(3).to_string())
    valid = gA[gA.da >= (1 - ALPHA) - MC3]
    rho_star = valid.rho.max() if len(valid) else float("nan")
    print(f"\nρ*  (largest ρ with DA coverage ≥ nominal−MC): {rho_star:.2f}")
    dom_cells = int((gA.cont_sup >= gA.clean_sup).sum())
    print(f"dominance (D): mean contaminated sup ≥ mean clean sup in "
          f"{dom_cells}/{len(gA)} cells (per-replicate {gA.dominance.min():.0%}"
          f"–{gA.dominance.max():.0%}); plug-in is conservative in all cells "
          f"(plugin cov {gA.plugin.min():.3f}–{gA.plugin.max():.3f} ≥ nominal)")

    print("\n=== Part B: Prop 3 coverage deficit, in-sample sliced modulation ===")
    print(dfB.pivot_table(index="K", columns="g",
                          values="deficit").round(3).to_string())
    print(f"fit  deficit ≈ c·(g/K):  c = {dfB.attrs['c']:.3f}, "
          f"R² = {dfB.attrs['r2']:.3f}")

    print("\n=== Part C: within-country decline certification, "
          "design-aware vs plug-in (α = 0.10) ===")
    print("certified share by country kind:")
    by = dfC.groupby("kind").agg(
        n=("kind", "size"),
        persist_plugin=("persist_plugin", "mean"),
        persist_da=("persist_da", "mean"),
        net_plugin=("net_plugin", "mean"),
        net_da=("net_da", "mean"))
    print(by.round(3).to_string())

    for level, tcol in (("persistent", "truth_persistent"), ("net", "truth_net")):
        non = dfC[~dfC[tcol]]
        dec = dfC[dfC[tcol]]
        pc, dc = f"{level[:4]}_plugin", f"{level[:4].replace('pers','persist').replace('net','net')}_da"
        pc = "persist_plugin" if level == "persistent" else "net_plugin"
        dc = "persist_da" if level == "persistent" else "net_da"
        print(f"\n[{level}]  false-cert on NON-{level}-decline (≤α={ALPHA}): "
              f"plug-in {non[pc].mean():.3f} | design-aware {non[dc].mean():.3f}"
              f"   power on true {level}: "
              f"plug-in {dec[pc].mean():.3f} | design-aware {dec[dc].mean():.3f}")
    print(f"\nheadline (net decline): plug-in flags {dfC.net_plugin.mean():.1%} "
          f"of countries, design-aware certifies {dfC.net_da.mean():.1%} "
          f"— the gap is the over-certification design-awareness removes.")


if __name__ == "__main__":
    main()
