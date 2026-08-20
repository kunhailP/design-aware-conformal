"""E56 — cross-country prevalence: "at least how many countries declined?"

The joint band of e50 certifies claims within a country at one alpha, and the
paper is explicit that the across-country COUNT carries no familywise control.
This experiment completes the ladder: per-country certification p-values by
alpha-inversion of the same joint sup-t construction, then Goeman-Solari closed
testing (Simes local tests; countries' bootstraps are independent), yielding

    "with 90% simultaneous confidence, at least d of the K countries truly
     satisfy net distributional decline,"

simultaneously over every subset, so the d smallest-p countries can be NAMED at
no further cost.

Two modes:
  synthetic (always runs): K=33 countries shaped like the long-window ESS,
    8 planted net decliners, reporting d against the truth and against the
    fixed-alpha certified count.
  ESS (runs when the licensed microdata is present): per-country p_net on
    trstprl/stfdem, rounds 1-11, exactly the e50 inputs; writes
    results/ess_prevalence.csv. The certified-count row of the paper then
    upgrades to a prevalence statement.

Run:  python -m pcb.experiments.e56_prevalence
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed
from pcb.inference.prevalence import (claim_family_pvalues,
                                      prevalence_lower_bound)

ALPHA = 0.10
T = 6
CORE = np.array([False, True, True, True, True, False])


def _synthetic():
    rng = np.random.default_rng(det_seed("e56", "synthetic"))
    K, K1, L, n, nboot = 33, 8, 6, 1500, 800
    chol = np.linalg.cholesky(0.6 ** np.abs(np.subtract.outer(np.arange(T),
                                                              np.arange(T)))
                              + 1e-9 * np.eye(T))
    def draw(m):
        z = rng.standard_t(6, size=(m, T)) / np.sqrt(6 / 4)
        return z @ chol.T

    base = np.tile(np.linspace(0.15, 0.75, T), (L, 1))
    pvals, certified = {}, 0
    for c in range(K):
        truth = base + (0.05 if c < K1 else 0.0) * np.arange(L)[:, None]
        truth = np.clip(truth, 0, 1)
        obs = truth + draw(L) / np.sqrt(n)
        boots = obs[None] + draw(nboot * L).reshape(nboot, L, T) / np.sqrt(n)
        p = claim_family_pvalues(obs, boots, CORE)["p_net"]
        pvals[f"C{c:02d}"] = p
        certified += p <= ALPHA
    out = prevalence_lower_bound(pvals, ALPHA)
    print("=== E56 synthetic (K=33, 8 planted net decliners) ===")
    print(f"  certified at fixed alpha={ALPHA}: {certified}")
    print(f"  90% simultaneous lower bound on TRUE decliners: d = {out['d']}")
    print(f"  named: {out['countries_named']}")
    print(f"  (truth: 8; d <= 8 should hold in ~90% of reruns, and the fixed-"
          f"alpha count carries no such guarantee)")
    return out


def _ess():
    try:
        from pcb.data.audit_ess import audit, load
        from pcb.experiments.e12_ess_decline import (_design_boot, _naive_boot,
                                                     _round_stats, _wcdf, CORE_T)
    except Exception as e:                                  # pragma: no cover
        print(f"\n[ESS] loaders unavailable ({e}); skipping the real-data run.")
        return
    try:
        df = load()
    except Exception as e:
        print(f"\n[ESS] microdata not present ({e}); skipping the real-data run.")
        return

    kl = audit(df).set_index(["cntry", "essround"])["sample"]
    df = df.assign(_w=df["anweight"].fillna(df["pspwght"]))
    df = df[df._w.notna() & (df._w > 0)]
    rows = []
    for outcome in ("trstprl", "stfdem"):
        pvals = {}
        for c, csub in df.groupby("cntry", observed=True):
            usable = [r for r in sorted(csub.essround.unique())
                      if kl.get((c, r)) in ("core", "extended")]
            if len(usable) < 3:
                continue
            rng = np.random.default_rng(det_seed("e56", outcome, c))
            F, B = [], []
            for r in usable:
                y, w, s, p = _round_stats(csub[csub.essround == r], outcome)
                if len(y) < 100:
                    continue
                F.append(_wcdf(y, w))
                B.append(_design_boot(y, w, s, p, rng)
                         if kl.get((c, r)) == "core" else _naive_boot(y, w, rng))
            if len(F) < 3:
                continue
            pv = claim_family_pvalues(np.array(F), np.stack(B, 1), CORE_T)
            pvals[str(c)] = pv["p_net"]
            rows.append(dict(outcome=outcome, cntry=str(c),
                             p_net=round(pv["p_net"], 5),
                             p_any_adjacent=round(pv["p_any_adjacent"], 5)))
        out = prevalence_lower_bound(pvals, ALPHA)
        print(f"\n[ESS {outcome}] K={len(pvals)}; with 90% simultaneous "
              f"confidence at least {out['d']} countries truly satisfy net "
              f"decline: {out['countries_named']}")
    os.makedirs("results", exist_ok=True)
    pd.DataFrame(rows).to_csv("results/ess_prevalence.csv", index=False)
    print("wrote results/ess_prevalence.csv")


def main():
    _synthetic()
    _ess()


if __name__ == "__main__":
    main()
