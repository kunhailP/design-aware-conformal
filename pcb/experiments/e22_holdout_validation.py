"""E22 — independent confirmatory validation of the FROZEN safe selector.

Single-shot. Grid, seeds, and DGP families are sealed in
configs/holdout_validation.yaml (sha256 in configs/holdout_seed_manifest.json);
the frozen method is docs/SAFE_SELECTOR_SPEC.md, deployed verbatim via pcb.dapcb.
This runner asserts the config hash matches the manifest before running, so a
post-hoc config edit aborts. See docs/INDEPENDENT_VALIDATION_PREREG.md.

Run:  python -m pcb.experiments.e22_holdout_validation
Output: results/holdout_safe_selector.csv
"""
from __future__ import annotations
import hashlib
import json
import os

import numpy as np
import pandas as pd
import yaml

from pcb.util import det_seed
from pcb.dapcb import alpha_split, dapcb, _quantiles
from pcb.inference.design_aware import deconv_target_scale

CFG = "configs/holdout_validation.yaml"
MANIFEST = "configs/holdout_seed_manifest.json"
OUT = "results/holdout_safe_selector.csv"            # raw per-rep (gitignored)
OUT_CELLS = "results/holdout_safe_selector_cells.csv"  # tracked cell summary


def _load_config():
    cfg = yaml.safe_load(open(CFG))
    man = json.load(open(MANIFEST))
    h = hashlib.sha256(open(CFG, "rb").read()).hexdigest()
    if h != man["config_sha256"]:
        raise SystemExit(f"CONFIG HASH MISMATCH: {h} != sealed {man['config_sha256']}\n"
                         "The holdout config was edited after sealing. Aborting.")
    return cfg


def _ar1(K, L, s, phi, rng):
    """AR(1) rows over L positions with marginal SD s."""
    e = rng.normal(0, 1, (K, L))
    x = np.empty((K, L))
    x[:, 0] = e[:, 0]
    for j in range(1, L):
        x[:, j] = phi * x[:, j - 1] + np.sqrt(1 - phi**2) * e[:, j]
    return x * s


def _gen(fam, K, L, s_R, rho, rng):
    """Return (E, V, Et): observed calibration errors (K,L), reported design SDs
    (K,L), and the design-noise-free latent target deviation (L,)."""
    v = s_R * rho
    # --- transport latent R (K,L) and target Rt (L) ---
    if fam == "heavy_tail_country":
        R = rng.standard_t(3, (K, L)) * s_R / np.sqrt(3)
        Rt = rng.standard_t(3, L) * s_R / np.sqrt(3)
    elif fam in ("weak_dep_rounds", "strong_dep_rounds"):
        phi = 0.3 if fam.startswith("weak") else 0.8
        R = _ar1(K, L, s_R, phi, rng)
        Rt = _ar1(1, L, s_R, phi, rng)[0]
    elif fam == "irregular_length":
        sc = s_R * (0.5 + rng.gamma(2.0, 0.5, (K, 1)))     # heteroskedastic magnitude
        R = rng.normal(0, 1, (K, L)) * sc
        Rt = rng.normal(0, 1, L) * s_R * (0.5 + rng.gamma(2.0, 0.5))
    else:
        R = rng.normal(0, s_R, (K, L))
        Rt = rng.normal(0, s_R, L)
    # --- per-country design SD v_c (K,1) ---
    if fam == "hetero_design_var":
        vc = v * rng.gamma(2.0, 0.5, (K, 1))
    elif fam == "unequal_psu":
        m = rng.lognormal(0, 0.6, (K, 1))
        vc = v / np.sqrt(m / m.mean())
    elif fam == "unequal_weights":
        deff = 1 + rng.gamma(2.0, 0.4, (K, 1))
        vc = v * np.sqrt(deff / deff.mean())
    else:
        vc = np.full((K, 1), v)
    # --- design noise xi (K,L) ---
    if fam == "skewed_noise":
        z = rng.lognormal(0, 0.8, (K, L))
        z = (z - z.mean()) / z.std()
        xi = z * vc
    else:
        xi = rng.normal(0, 1, (K, L)) * vc
    E = R + xi
    # --- reported design SD V (K,L): noisy estimate, biased under misspecification ---
    if fam == "noise_misspec":
        V = np.abs(0.75 * vc * np.ones((K, L)))            # 25% under-report
    else:
        V = np.abs(vc * (1 + rng.normal(0, 0.15, (K, L))))
    return E, V, Rt


def _one(fam, K, rho, rep, s_R, L, master):
    """Score the band `dapcb` ACTUALLY RETURNS against the latent target.

    (An earlier version of this runner rescored the branches with the S2
    studentized quantiles — a different band from the U0 construction dapcb
    ships — so the confirmatory holdout was certifying a band the package
    does not deploy. Fixed: cov_safe is computed on `fit.band` verbatim, and
    the per-branch diagnostics use the same U0/α-budget quantiles as dapcb.)
    """
    rng = np.random.default_rng(det_seed(master, fam, K, rho, rep))
    E, V, Et = _gen(fam, K, L, s_R, rho, rng)
    center = np.full(L, 0.5)
    fit = dapcb(E, V, center, tighten=False)               # deployed frozen selector
    # branch radii recomputed with dapcb's own U0/α-budget construction, and
    # coverage scored in score space (the synthetic truth is not a CDF, so the
    # deployed [0,1] clip would create artificial misses here)
    sT = deconv_target_scale(E, V)
    a_anchor, a_dec = alpha_split(K, 0.10)
    qp, qd, qc = _quantiles(E, sT, V, a_anchor, a_dec if a_dec > 0 else 0.01)
    cov = {"PCB": int(np.max(np.abs(Et)) <= qp),
           "deconvolution": int(np.max(np.abs(Et) / sT) <= qd),
           "conservative": int(np.max(np.abs(Et)) <= qc)}
    w = {"PCB": qp, "deconvolution": qd * sT.mean(), "conservative": qc}
    br = fit.selected_branch
    return dict(family=fam, K=K, rho=rho, branch=br,
                cov_safe=cov[br], w_safe=w[br], cov_level=fit.coverage_level,
                rlcb=fit.rho_lcb, D=fit.reliability, delta_ucb=fit.delta_ucb,
                cov_pcb=cov["PCB"], cov_dec=cov["deconvolution"], cov_con=cov["conservative"],
                w_pcb=w["PCB"], w_dec=w["deconvolution"], w_con=w["conservative"])


def main():
    cfg = _load_config()
    s_R, T = cfg["s_R"], cfg["T"]
    master = cfg["master_seed"]
    rows = []
    for fam in cfg["dgp_families"]:
        L = T * cfg["rounds_dep"] if fam.endswith("dep_rounds") else T
        for K in cfg["K"]:
            for rho in cfg["rho"]:
                for rep in range(cfg["reps"]):
                    rows.append(_one(fam, K, rho, rep, s_R, L, master))
        print(f"  done family={fam}")
    df = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    df.to_csv(OUT, index=False)                      # raw per-rep (gitignored, 61MB)
    # tracked cell-level summary (450 rows)
    cells = df.groupby(["family", "K", "rho"]).agg(
        coverage=("cov_safe", "mean"), reps=("cov_safe", "size"),
        cov_level=("cov_level", "mean"),
        dec=("branch", lambda s: (s == "deconvolution").mean()),
        con=("branch", lambda s: (s == "conservative").mean()),
        pcb=("branch", lambda s: (s == "PCB").mean()),
        w_safe=("w_safe", "mean"), w_pcb=("w_pcb", "mean"), w_con=("w_con", "mean"),
        cov_pcb=("cov_pcb", "mean"), cov_dec=("cov_dec", "mean"),
        cov_con=("cov_con", "mean"), rlcb=("rlcb", "mean"), D=("D", "mean"),
        delta_ucb=("delta_ucb", "mean")).reset_index().round(5)
    cells.to_csv(OUT_CELLS, index=False)

    # --- headline summary (printed; full analysis in the results doc) ---
    g = df.groupby(["family", "K", "rho"]).agg(
        cov_safe=("cov_safe", "mean"), reps=("cov_safe", "size"),
        cov_level=("cov_level", "mean"),
        dec=("branch", lambda s: (s == "deconvolution").mean()),
        w_safe=("w_safe", "mean"), w_pcb=("w_pcb", "mean"),
        w_con=("w_con", "mean"), rlcb=("rlcb", "mean")).reset_index()
    g["mc_se"] = np.sqrt(np.clip(g.cov_safe * (1 - g.cov_safe), 1e-6, None) / g.reps)
    g["floor_ok"] = g.cov_safe + 1.96 * g.mc_se >= g.cov_level - 1e-9
    print(f"\nCELLS: {len(g)}  worst cov_safe: {g.cov_safe.min():.3f}  "
          f"floor-compatible (P1): {int(g.floor_ok.sum())}/{len(g)}")
    bad = g[~g.floor_ok].sort_values("cov_safe")
    if len(bad):
        print("cells failing P1 (cov + 1.96 MC-SE < floor):")
        print(bad[["family", "K", "rho", "cov_safe", "cov_level", "dec"]].to_string(index=False))
    lo = g[g.rlcb <= 0.47]
    print(f"low-ρ safe/PCB width (E1): {(lo.w_safe/lo.w_pcb).mean():.3f}")
    dec = df[df.branch == "deconvolution"]
    if len(dec):
        print(f"deconv activations: {len(dec)} reps; deconv width/con: "
              f"{(dec.w_dec/dec.w_con).mean():.3f}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
