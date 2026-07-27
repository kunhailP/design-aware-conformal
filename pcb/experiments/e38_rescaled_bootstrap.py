"""E38 — the promised Rao–Wu–Yue rescaled-bootstrap rerun (paper §6/§7/§8).

The shipped real-data CSVs use plain m-of-m PSU resampling, which understates
between-PSU variance by (m-1)/m per stratum; the paper discloses the direction
(rho-hat values are floors; certified counts err inclusive) and flags this rerun.
Here we flip the RESCALE flag in every stratified-bootstrap site (e12/e13
certification engine, e24 subgroup scan, e17 LAPOP change transport, ess_panel
design SDs) and rerun, writing *_rescaled.csv alongside the shipped files and
printing the deltas the text promises:

  (1) ESS certification counts by rung (rescaled vs shipped)   -> counts move DOWN or hold
  (2) ESS subgroup rho-hat scan max + gate activations         -> rho moves UP; gates still closed?
  (3) LAPOP change-transport rho-hat                           -> rho moves UP; still below rho0?
  (4) ESS panel design SDs (core rounds)                       -> SDs move UP

Run:  python -m pcb.experiments.e38_rescaled_bootstrap   (~1-2 h, real microdata)
"""
from __future__ import annotations
import os
import shutil

import numpy as np
import pandas as pd

import pcb.experiments.e12_ess_decline as e12
import pcb.experiments.e13_ess_audit as e13
import pcb.experiments.e24_subgroup_rho_scan as e24
import pcb.experiments.e17_lapop_change_transport as e17
import pcb.experiments.e16_lapop_transport as e16
import pcb.data.ess_panel as ess_panel
from pcb.util import det_seed
from pcb.data.audit_ess import audit, load

SWAP = {
    "results/ess_subgroup_rho_scan.csv": "results/ess_subgroup_rho_scan_rescaled.csv",
    "results/lapop_change_transport.csv": "results/lapop_change_transport_rescaled.csv",
    "results/lapop_change_candidate_b_by_rho.csv":
        "results/lapop_change_candidate_b_by_rho_rescaled.csv",
    "results/lapop_change_design_resampling.csv":
        "results/lapop_change_design_resampling_rescaled.csv",
}


def _run_swapped(mainfn, paths):
    """Run a main() that writes shipped paths; capture outputs under _rescaled
    names and restore the shipped files afterwards."""
    saved = {}
    for p in paths:
        if os.path.exists(p):
            saved[p] = p + ".shipped_bak"
            shutil.move(p, saved[p])
    try:
        mainfn()
        for p in paths:
            if os.path.exists(p):
                shutil.move(p, SWAP[p])
    finally:
        for p, b in saved.items():
            if os.path.exists(b):
                shutil.move(b, p)


def ess_certification_rescaled():
    df = load()
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]
    rows = []
    for outcome in e13.OUTCOMES:
        for c, csub in df.groupby("cntry", observed=True):
            core_rounds = [r for r in sorted(csub.essround.unique())
                           if klass.get((c, r)) == "core"]
            if len([r for r in core_rounds if r + 1 in core_rounds]) == 0:
                continue
            rng = np.random.default_rng(det_seed(outcome, c))
            res = e13.audit_country(csub, core_rounds, outcome, rng)
            if res:
                rows.append(dict(outcome=outcome, cntry=c, **res))
    out = pd.DataFrame(rows)
    out.to_csv("results/ess_country_certification_rescaled.csv", index=False)
    return out


def main():
    os.makedirs("results", exist_ok=True)

    # -- (1) ESS certification with RWY rescaling ------------------------------
    e12.RESCALE = True
    new = ess_certification_rescaled()
    old = pd.read_csv("results/ess_country_certification.csv")
    print("=== (1) ESS certification, RWY-rescaled vs shipped (plug/DA) ===")
    for oc in e13.OUTCOMES:
        n, o = new[new.outcome == oc], old[old.outcome == oc]
        for rung in ("any_da", "net_da", "persist_da", "persist_da_bonf"):
            print(f"  {oc:8s} {rung:16s} shipped {int(o[rung].sum()):2d} -> "
                  f"rescaled {int(n[rung].sum()):2d}")
        moved = sorted(set(o.cntry[o.net_da]) ^ set(n.cntry[n.net_da]))
        if moved:
            print(f"  {oc}: net membership changes: {moved}")
    e12.RESCALE = False

    # -- (2) ESS subgroup rho scan ---------------------------------------------
    e24.RESCALE = True
    _run_swapped(e24.main, ["results/ess_subgroup_rho_scan.csv"])
    e24.RESCALE = False
    o = pd.read_csv("results/ess_subgroup_rho_scan.csv")
    n = pd.read_csv("results/ess_subgroup_rho_scan_rescaled.csv")
    print("\n=== (2) ESS subgroup rho scan ===")
    print(f"  max rho_hat: shipped {o.rho_hat.max():.3f} -> rescaled "
          f"{n.rho_hat.max():.3f} (rho0=0.47)")
    for col in ("gate_A", "branch"):
        if col in n:
            opens = (n[col] != "PCB").sum() if col == "branch" else n[col].sum()
            print(f"  rescaled {col}: {opens} non-PCB/open of {len(n)}")

    # -- (3) LAPOP change transport --------------------------------------------
    e16.RESCALE = True
    _run_swapped(e17.main, ["results/lapop_change_transport.csv",
                            "results/lapop_change_candidate_b_by_rho.csv",
                            "results/lapop_change_design_resampling.csv"])
    e16.RESCALE = False
    o = pd.read_csv("results/lapop_change_transport.csv")
    n = pd.read_csv("results/lapop_change_transport_rescaled.csv")
    print("\n=== (3) LAPOP change transport ===")
    if "rho" in n:
        print(f"  max rho: shipped {o.rho.max():.3f} -> rescaled {n.rho.max():.3f}")

    # -- (4) ESS panel design SDs ----------------------------------------------
    ess_panel.RESCALE = True
    pn = ess_panel.build_panel()
    ess_panel.RESCALE = False
    pn.to_csv("results/ess_panel_design_sd_rescaled.csv", index=False)
    core = pn[pn.get("v_trstprl").notna()] if "v_trstprl" in pn else pn
    print("\n=== (4) ESS panel design SDs (rescaled) written ===")
    print(f"  rows: {len(pn)}")


if __name__ == "__main__":
    main()
