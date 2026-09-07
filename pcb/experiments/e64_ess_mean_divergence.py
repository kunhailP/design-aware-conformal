"""E64 — where a mean contrast misses an E50-certified CDF decline.

This is a fixed, narrow comparison, not a shape taxonomy. It reruns E50 only
for the already committed country-outcome net set, verifies the joint CDF
certification, and compares it with a one-sided design-bootstrap test of the
first-to-last weighted-mean decline.

Protocol: docs/ESS_MEAN_DIVERGENCE_PROTOCOL.md
Outputs:
  results/ess_mean_divergence.csv
  results/ess_mean_divergence_profiles.csv
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from pcb.data.audit_ess import audit, load
from pcb.experiments.e12_ess_decline import (
    ALPHA,
    CORE_T,
    _design_boot,
    _naive_boot,
    _round_stats,
    _wcdf,
)
from pcb.experiments.e50_joint_claim_family import MIN_N
from pcb.inference.claim_family import certify_claim_family
from pcb.util import det_seed


SOURCE = "results/ess_joint_claims.csv"


def _mean_from_cdf(cdf: np.ndarray) -> np.ndarray:
    """Weighted mean on the 0--10 scale from CDF values at thresholds 0--9."""
    return 10.0 - np.asarray(cdf, float).sum(axis=-1)


def _mean_decline_bound(curves: np.ndarray, boots: np.ndarray):
    mean = _mean_from_cdf(curves)
    boot_mean = _mean_from_cdf(boots)
    estimate = float(mean[0] - mean[-1])
    boot_diff = boot_mean[:, 0] - boot_mean[:, -1]
    sd = max(float(boot_diff.std()), 1e-6)
    stat = (boot_diff - estimate) / sd
    critical = float(np.quantile(stat, 1 - ALPHA))
    lower = estimate - critical * sd
    return dict(
        mean_first=float(mean[0]),
        mean_last=float(mean[-1]),
        mean_decline=estimate,
        mean_sd=sd,
        mean_lower=float(lower),
        mean_certified=bool(lower > 0),
    )


def main():
    os.makedirs("results", exist_ok=True)
    committed = pd.read_csv(SOURCE)
    candidates = {
        (row.outcome, row.cntry)
        for row in committed.loc[committed.net].itertuples()
    }

    df = load()
    klass = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]

    rows, profiles = [], []
    for outcome, country in sorted(candidates):
        csub = df[df.cntry == country]
        usable = [
            round_
            for round_ in sorted(csub.essround.unique())
            if klass.get((country, round_)) in ("core", "extended")
        ]
        rng = np.random.default_rng(det_seed("e50", outcome, country))
        curves, boots, rounds = [], [], []
        for round_ in usable:
            y, w, stratum, psu = _round_stats(
                csub[csub.essround == round_], outcome
            )
            if len(y) < MIN_N:
                continue
            curve = _wcdf(y, w)
            if klass.get((country, round_)) == "core":
                boot = _design_boot(y, w, stratum, psu, rng)
            else:
                boot = _naive_boot(y, w, rng)
            curves.append(curve)
            boots.append(boot)
            rounds.append(int(round_))

        curves_arr = np.asarray(curves)
        boots_arr = np.stack(boots, axis=1)
        joint = certify_claim_family(
            curves_arr, boots_arr, ALPHA, CORE_T
        )
        if not joint["net"]:
            raise RuntimeError(
                f"E50 net certification did not reproduce for "
                f"{outcome}/{country}"
            )
        mean_result = _mean_decline_bound(curves_arr, boots_arr)
        rows.append(dict(
            outcome=outcome,
            cntry=country,
            n_rounds=len(rounds),
            r_first=rounds[0],
            r_last=rounds[-1],
            cdf_net=True,
            cdf_net_lower=joint["net_lower"],
            divergence=not mean_result["mean_certified"],
            **mean_result,
        ))

        net_diff = curves_arr[-1] - curves_arr[0]
        net_boot = boots_arr[:, -1] - boots_arr[:, 0]
        net_sd = np.maximum(net_boot.std(0), 1e-6)
        net_lower = net_diff - joint["c"] * net_sd
        for threshold in range(len(net_diff)):
            profiles.append(dict(
                outcome=outcome,
                cntry=country,
                threshold=threshold,
                core=bool(CORE_T[threshold]),
                cdf_first=curves_arr[0, threshold],
                cdf_last=curves_arr[-1, threshold],
                cdf_diff=net_diff[threshold],
                cdf_lower=net_lower[threshold],
            ))

    result = pd.DataFrame(rows).sort_values(
        ["divergence", "outcome", "mean_lower"],
        ascending=[False, True, True],
    )
    profile = pd.DataFrame(profiles).sort_values(
        ["outcome", "cntry", "threshold"]
    )
    result.to_csv("results/ess_mean_divergence.csv", index=False)
    profile.to_csv("results/ess_mean_divergence_profiles.csv", index=False)

    divergence = result[result.divergence]
    print(f"E50-certified country-outcomes: {len(result)}")
    print(f"mean-vs-CDF divergence cases: {len(divergence)}")
    if len(divergence):
        print(divergence[[
            "outcome", "cntry", "cdf_net_lower",
            "mean_decline", "mean_lower",
        ]].to_string(index=False))


if __name__ == "__main__":
    main()
