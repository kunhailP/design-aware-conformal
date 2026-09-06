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


def run_ess(df, kl, out="results/ess_prevalence.csv", tag="ESS"):
    """Per-country p_net / p_any_adjacent on the prepared ESS frame `df`
    (weights already in `_w`) with country-round classification `kl`, then the
    closed-testing prevalence bound under Simes AND Bonferroni local tests.
    Same seeds as the shipped run, so a design-upgraded frame (e61, SDDF
    rounds 1-8) changes only the extended-round draws."""
    from pcb.experiments.e12_ess_decline import (_design_boot, _naive_boot,
                                                 _round_stats, _wcdf, CORE_T)
    rows, bounds = [], {}
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
        for local in ("simes", "bonferroni"):
            b = prevalence_lower_bound(pvals, ALPHA, local)
            bounds[(outcome, local)] = b
            print(f"\n[{tag} {outcome}, {local}] K={len(pvals)}; with 90% "
                  f"simultaneous confidence at least {b['d']} countries truly "
                  f"satisfy net decline: {b['countries_named']}")
    os.makedirs("results", exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"wrote {out}")
    return bounds


def _ess():
    try:
        from pcb.data.audit_ess import audit, load
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
    return run_ess(df, kl)


def shipped_bounds(path="results/ess_prevalence.csv", alpha=ALPHA):
    """Re-read the committed p-values and report the bound under both local
    tests -- the microdata-free half of the sensitivity (supplement S4)."""
    d = pd.read_csv(path)
    out = {}
    for outcome, g in d.groupby("outcome"):
        for local in ("simes", "bonferroni"):
            out[(outcome, local)] = prevalence_lower_bound(
                dict(zip(g.cntry, g.p_net)), alpha, local)
    return out


def main():
    _synthetic()
    if os.path.exists("results/ess_prevalence.csv"):
        print("\n=== shipped ESS p-values: Simes vs Bonferroni local tests ===")
        for (outcome, local), b in shipped_bounds().items():
            print(f"  {outcome:8s} {local:10s} d = {b['d']}  named: "
                  f"{b['countries_named']}")
    _ess()


if __name__ == "__main__":
    main()
