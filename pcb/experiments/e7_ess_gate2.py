"""E7 — pilot gate 2: does the marginal-vs-simultaneous failure, and the
design-aware correction, materialise on real ESS political-attitude curves?

Population = country x round (289 available). Predictor = last observed round
carried forward (LOCF), the strong simple baseline of the research design; the
target's own round is never used. This is TEMPORAL TRANSPORT (nowcasting the
next round of a country with survey history), not unseen-country transport.
Calibration is COUNTRY-BLOCKED leave-one-country-out: all rounds of the target
country are excluded, so within-country serial dependence cannot leak into the
calibration set. CAVEAT (audited in e8_cluster_audit): the quantile here is
computed over country-round scores, so the round-level coverage it reports is
marginal per country-round; trajectory-level claims need the clustered
calibration of pcb/inference/clustered_band.py.

Measured (validation view, against the target's survey estimate):
  M2   per-threshold split-conformal band  - marginal + simultaneous coverage
  PCB  population conformal band           - simultaneous coverage, width
  DA   design-studentised band (core sample, rounds with psu/stratum):
       validation band uses the target's own design SD.
Diagnostic: noise ratio = design SD of the source curves / SD of transport
errors - the number that decides how much the DA layer matters on ESS.

Run:  python -m pcb.experiments.e7_ess_gate2   -> results/ess_gate2.csv
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.data.ess_panel import OUT as PANEL_PATH, T_GRID
from pcb.inference.conformal_band import population_conformal_band
from pcb.inference.design_aware import da_studentized_band

ALPHA = 0.10


def curves(panel: pd.DataFrame, outcome: str, kind: str = "t") -> np.ndarray:
    return panel[[f"{outcome}_{kind}{t}" for t in range(T_GRID)]].to_numpy()


def locf_pairs(panel: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """One row per country-round that has an earlier round: adds theta_hat."""
    panel = panel.sort_values(["cntry", "essround"]).reset_index(drop=True)
    th = curves(panel, outcome)
    rows = []
    for c, sub in panel.groupby("cntry", observed=True):
        idx = sub.index.to_numpy()
        for j in range(1, len(idx)):
            rows.append(dict(row=idx[j], prev=idx[j - 1],
                             gap=int(panel.essround[idx[j]]
                                     - panel.essround[idx[j - 1]])))
    pairs = pd.DataFrame(rows)
    out = panel.loc[pairs.row].reset_index(drop=True)
    out["gap"] = pairs.gap.to_numpy()
    for t in range(T_GRID):
        out[f"hat_t{t}"] = th[pairs.prev.to_numpy(), t]
    return out


def m2_band(E_cal: np.ndarray, alpha: float = ALPHA) -> np.ndarray:
    """Per-threshold symmetric conformal radii q_t (T,)."""
    K = E_cal.shape[0]
    k = int(np.ceil((1 - alpha) * (K + 1)))
    A = np.sort(np.abs(E_cal), axis=0)
    return A[min(k, K) - 1]


def evaluate(pairs: pd.DataFrame, outcome: str, use_da: bool):
    th_hat = pairs[[f"hat_t{t}" for t in range(T_GRID)]].to_numpy()
    th_til = curves(pairs, outcome)
    E = th_hat - th_til
    V = curves(pairs, outcome, "v") if use_da else None

    recs = []
    for i in range(len(pairs)):
        cal = (pairs.cntry != pairs.cntry.iloc[i]).to_numpy()
        Ec, e_tgt = E[cal], E[i]
        q = m2_band(Ec)
        lo, hi = population_conformal_band(Ec, th_hat[i], ALPHA)
        rec = dict(cntry=pairs.cntry.iloc[i], essround=pairs.essround.iloc[i],
                   n=pairs[f"n_{outcome}"].iloc[i], gap=pairs.gap.iloc[i],
                   m2_marg=float(np.mean(np.abs(e_tgt) <= q)),
                   m2_sim=float(np.all(np.abs(e_tgt) <= q)),
                   m2_width=float(2 * q.mean()),
                   pcb_sim=float(np.all((lo <= th_til[i]) & (th_til[i] <= hi))),
                   pcb_width=float((hi - lo).mean()))
        if use_da:
            dlo, dhi = da_studentized_band(Ec, V[cal], th_hat[i], V[i], ALPHA)
            plo, phi = da_studentized_band(Ec, V[cal], th_hat[i], None, ALPHA)
            rec.update(
                da_sim=float(np.all((dlo <= th_til[i]) & (th_til[i] <= dhi))),
                da_width=float((dhi - dlo).mean()),
                da_width_deploy=float((phi - plo).mean()))
        recs.append(rec)
    return pd.DataFrame(recs), E


def main():
    panel = pd.read_parquet(PANEL_PATH)
    core = panel[panel["sample"] == "core"]
    frames = []
    for outcome in ("trstprl", "stfdem"):
        for name, sub, use_da in (("all", panel, False), ("core", core, True)):
            pairs = locf_pairs(sub, outcome)
            res, E = evaluate(pairs, outcome, use_da)
            res.insert(0, "outcome", outcome)
            res.insert(1, "layer", name)
            frames.append(res)
            line = (f"{outcome:8s} {name:5s} K={len(res):3d} "
                    f"({res.cntry.nunique()} countries) | "
                    f"M2 marg {res.m2_marg.mean():.3f} sim {res.m2_sim.mean():.3f} "
                    f"w {res.m2_width.mean():.3f} | "
                    f"PCB sim {res.pcb_sim.mean():.3f} w {res.pcb_width.mean():.3f}")
            if use_da:
                v = curves(pairs, outcome, "v")
                ratio = v.mean() / E.std(0).mean()
                line += (f" | DA sim {res.da_sim.mean():.3f} w {res.da_width.mean():.3f}"
                         f" (deploy w {res.da_width_deploy.mean():.3f})"
                         f" | noise ratio {ratio:.2f}")
            print(line)
    os.makedirs("results", exist_ok=True)
    pd.concat(frames).to_csv("results/ess_gate2.csv", index=False)


if __name__ == "__main__":
    main()
