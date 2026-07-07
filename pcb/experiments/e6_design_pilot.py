"""E6 — pilot gate 1: oracle vs plug-in vs design-aware PCB under a real
survey design (two-stage informative cluster sampling, ESS-scale n).

Questions (pre-stated, falsifiable):
  Q1  How much width does treating θ̃_g as truth cost against the oracle, and
      is plug-in PCB conservative (not anti-conservative) for the TRUE curve
      of an unsurveyed target?  [homogeneous designs, deployment view]
  Q2  Does design HETEROGENEITY produce genuine undercoverage in the
      validation view (target evaluated against its own survey estimate, as
      any ESS holdout must be) — concentrated on noisy-survey targets?
  Q3  Do the DA corrections restore oracle-like width (studentized) and
      conditional validity, and how conservative is the worst-case variant?

Views per replicate: deployment = band evaluated against the target's true
curve θ (no survey used); validation = against the target's survey estimate
θ̃ (what an ESS-based holdout can measure). da_studentized issues a different
band per view (v_target = 0 vs the target's own design SD); other methods
issue one band for both.

Run:  python -m pcb.experiments.e6_design_pilot          -> results/e6_design_pilot.csv
"""
from __future__ import annotations
import multiprocessing as mp
import os

import numpy as np
import pandas as pd

from pcb.inference.conformal_band import population_conformal_band
from pcb.inference.design_aware import (da_studentized_band, da_worstcase_band,
                                        psu_bootstrap)
from pcb.simulation.survey_dgp import (SurveyDesign, SurveySimConfig,
                                       generate_survey_hierarchy)

ALPHA = 0.10          # nominal simultaneous level (90%)
BETA = 0.10           # level of the per-source design uncertainty band
B_BOOT = 200
REPS = 500
K = 50

_BASE = SurveyDesign(m_psu=30, b_per_psu=50, icc=0.05, gamma=0.5, eta=0.3)
_NOISY = SurveyDesign(m_psu=20, b_per_psu=30, icc=0.15, gamma=1.0, eta=0.5)
_HET = (SurveyDesign(m_psu=12, b_per_psu=50, icc=0.15, gamma=1.0, eta=0.5),
        _BASE,
        SurveyDesign(m_psu=50, b_per_psu=50, icc=0.02, gamma=0.25, eta=0.2))

CELLS = {
    "A_baseline":         SurveySimConfig(K=K, s_transport=0.30, designs=(_BASE,)),
    "B_noisy_survey":     SurveySimConfig(K=K, s_transport=0.30, designs=(_NOISY,)),
    "C_heterogeneous":    SurveySimConfig(K=K, s_transport=0.30, designs=_HET),
    "D_small_shift":      SurveySimConfig(K=K, s_transport=0.10, designs=(_BASE,)),
    "E_small_shift_noisy": SurveySimConfig(K=K, s_transport=0.10, designs=(_NOISY,)),
}


def _covers(lo, hi, curve) -> float:
    return float(np.all((lo <= curve) & (curve <= hi)))


def one_rep(args):
    cell, seed = args
    cfg = CELLS[cell]
    rng = np.random.default_rng(seed)
    h = generate_survey_hierarchy(cfg, rng)
    th_true, th_hat = h["theta_true"], h["theta_hat"]
    tilde = np.array([s["theta_tilde"] for s in h["surveys"]])

    boots = [psu_bootstrap(s["psu_cnt"], s["psu_tot"], B_BOOT, rng)
             for s in h["surveys"]]
    v = np.array([b.std(axis=0) for b in boots])                  # (K+1, T)
    lo_d = np.array([np.quantile(b, BETA / 2, axis=0) for b in boots])
    hi_d = np.array([np.quantile(b, 1 - BETA / 2, axis=0) for b in boots])

    E_plug = th_hat[:-1] - tilde[:-1]
    E_true = th_hat[:-1] - th_true[:-1]
    center, tgt_true, tgt_tilde = th_hat[-1], th_true[-1], tilde[-1]

    bands = {
        "oracle": population_conformal_band(E_true, center, ALPHA),
        "plugin": population_conformal_band(E_plug, center, ALPHA),
        "da_wc": da_worstcase_band(E_plug, th_hat[:-1], lo_d[:-1], hi_d[:-1],
                                   center, ALPHA),
    }
    stud_dep = da_studentized_band(E_plug, v[:-1], center, None, ALPHA)
    stud_val = da_studentized_band(E_plug, v[:-1], center, v[-1], ALPHA)

    out = {"cell": cell, "seed": seed,
           "target_n": h["surveys"][-1]["n"],
           "survey_sd": float(v[:-1].mean()),
           "transport_sd": float(E_true.std(0).mean())}
    for name, (lo, hi) in bands.items():
        out[f"{name}_cov_true"] = _covers(lo, hi, tgt_true)
        out[f"{name}_cov_tilde"] = _covers(lo, hi, tgt_tilde)
        out[f"{name}_width"] = float((hi - lo).mean())
    out["da_stud_cov_true"] = _covers(*stud_dep, tgt_true)
    out["da_stud_width"] = float((stud_dep[1] - stud_dep[0]).mean())
    out["da_stud_cov_tilde"] = _covers(*stud_val, tgt_tilde)
    out["da_stud_width_val"] = float((stud_val[1] - stud_val[0]).mean())
    return out


def main():
    jobs = [(cell, 10_000 * i + j) for i, cell in enumerate(CELLS)
            for j in range(REPS)]
    with mp.Pool(min(64, os.cpu_count() or 8)) as pool:
        rows = pool.map(one_rep, jobs, chunksize=8)
    df = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/e6_design_pilot.csv", index=False)

    methods = ["oracle", "plugin", "da_stud", "da_wc"]
    agg = df.groupby("cell").agg(
        noise_ratio=("survey_sd", "mean"),
        transport_sd=("transport_sd", "mean"),
        **{f"{m}_{q}": (f"{m}_{q}", "mean") for m in methods
           for q in ("cov_true", "cov_tilde", "width")})
    agg["noise_ratio"] = agg["noise_ratio"] / agg["transport_sd"]
    pd.set_option("display.width", 200)
    print("\n=== E6 pilot: simultaneous coverage & width (nominal 90%) ===")
    print(agg.drop(columns="transport_sd").round(3).to_string())

    het = df[df.cell == "C_heterogeneous"]
    cond = het.groupby("target_n").agg(
        reps=("seed", "size"),
        plugin_val=("plugin_cov_tilde", "mean"),
        da_stud_val=("da_stud_cov_tilde", "mean"),
        plugin_dep=("plugin_cov_true", "mean"),
        da_stud_dep=("da_stud_cov_true", "mean"))
    print("\n=== Q2: validation-view coverage by target survey size "
          "(C_heterogeneous) ===")
    print(cond.round(3).to_string())


if __name__ == "__main__":
    main()
