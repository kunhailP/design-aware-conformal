"""E58 — closing the LOO-center exactness seam: LOO vs split-fold vs oracle.

Theorem 3 states exactness for centers satisfying the symmetric-construction
condition (fixed / own-unit / split-fold / validation-mode grand mean). The
DEPLOYED unsurveyed-target construction instead uses the leave-one-out center
(`loo_deviations`): each calibration score excludes its own unit, the target's
center is the mean of all K. The docstring argument says the residual
asymmetry is O(1/K^2) in the CONSERVATIVE direction (the calibration pool has
K-1 units, so its deviations are, if anything, more dispersed than the
target's); the manuscript currently calls this "bounded only heuristically."

This experiment measures the seam directly, at the K where an O(1/K^2) term
could bite. For each family and K, over many replications:

  LOO         R_c = max_t |F_c - mean_{c'!=c} F_c'|, target vs mean of all K
              (deployment mode; validity claimed, exactness not)
  SPLIT       center = mean of fold A; scores and target on fold B
              (a Theorem-3 admissible case; exact at |B| by construction)
  ORACLE      center = true mu (fixed center; exact, the efficiency benchmark)
  GRAND       center = mean of all K INCLUDING the scored unit
              (the self-inclusion construction Theorem 3 excludes;
              anti-conservative O(1/K), shown for contrast)

Decision rule recorded in DEVELOPMENT_ROADMAP.md (Workstream A): if LOO never
dips below the Vovk floor - 2 MC-SE at any K while split-fold pays visible
width, the conservative-direction lemma is the right closure; if split-fold is
nearly free, rerunning the headline transports with it is cleaner.

The variance identity behind the lemma attempt, recorded here because the
experiment tests its finite-sample consequence: with iid unit curves,
Var(scaled LOO calibration deviation) = K/(K-1) sigma^2 per coordinate against
Var(target deviation) = (K+1)/K sigma^2, and K/(K-1) - (K+1)/K = 1/(K(K-1)):
the calibration scores are more dispersed by exactly O(1/K^2), in the
conservative direction.

Run:  python -m pcb.experiments.e58_center_exactness
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd

from pcb.util import det_seed

ALPHA = 0.10
T = 6
REPS = 20000
KS = [6, 8, 10, 15, 20, 30, 60]
FAMILIES = ("gaussian", "heavy_tail", "skewed", "ar_rounds")


def _draw(fam: str, n: int, rng) -> np.ndarray:
    """n unit deviation curves (n, T) from a zero-mean family."""
    if fam == "gaussian":
        return rng.normal(0, 1.0, (n, T))
    if fam == "heavy_tail":
        return rng.standard_t(3, (n, T)) / np.sqrt(3.0)
    if fam == "skewed":
        return (rng.gamma(2.0, 1.0, (n, T)) - 2.0) / np.sqrt(2.0)
    if fam == "ar_rounds":                      # dependence across the grid
        e = rng.normal(0, 1.0, (n, T))
        for t in range(1, T):
            e[:, t] = 0.7 * e[:, t - 1] + np.sqrt(1 - 0.49) * e[:, t]
        return e
    raise ValueError(fam)


def _finite_q(scores: np.ndarray, alpha: float) -> float:
    K = scores.shape[0]
    idx = int(np.ceil((1 - alpha) * (K + 1)))
    return np.inf if idx > K else float(np.sort(scores)[idx - 1])


def _cell(fam: str, K: int) -> dict:
    cov = dict(loo=0, split=0, oracle=0, grand=0)
    wid = dict(loo=0.0, split=0.0, oracle=0.0, grand=0.0)
    nA = K // 2                                  # split: fold A -> center
    for rep in range(REPS):
        rng = np.random.default_rng(det_seed("e58", fam, K, rep))
        X = _draw(fam, K + 1, rng)               # K calibration + 1 target
        cal, tgt = X[:K], X[K]

        # LOO (deployment): calibration excludes own unit; target vs mean of K
        tot = cal.sum(0)
        E_loo = cal - (tot[None] - cal) / (K - 1)
        q = _finite_q(np.max(np.abs(E_loo), 1), ALPHA)
        cov["loo"] += int(np.max(np.abs(tgt - tot / K)) <= q); wid["loo"] += q

        # SPLIT: center from fold A, scores from fold B, target same center
        muA = cal[:nA].mean(0)
        q = _finite_q(np.max(np.abs(cal[nA:] - muA[None]), 1), ALPHA)
        cov["split"] += int(np.max(np.abs(tgt - muA)) <= q); wid["split"] += q

        # ORACLE: fixed true center (zero)
        q = _finite_q(np.max(np.abs(cal), 1), ALPHA)
        cov["oracle"] += int(np.max(np.abs(tgt)) <= q); wid["oracle"] += q

        # GRAND (excluded by Theorem 3): self-inclusive center for calibration
        mu = tot / K
        q = _finite_q(np.max(np.abs(cal - mu[None]), 1), ALPHA)
        cov["grand"] += int(np.max(np.abs(tgt - mu)) <= q); wid["grand"] += q

    m = int(np.ceil((1 - ALPHA) * (K + 1)))
    mB = int(np.ceil((1 - ALPHA) * (K - nA + 1)))
    out = dict(family=fam, K=K, reps=REPS,
               vovk_floor=m / (K + 1),
               vovk_floor_split=(np.nan if mB > K - nA else mB / (K - nA + 1)),
               mc_se=float(np.sqrt(0.9 * 0.1 / REPS)))
    for k in cov:
        out[f"cov_{k}"] = cov[k] / REPS
        out[f"w_{k}"] = wid[k] / REPS
    return out


def main():
    os.makedirs("results", exist_ok=True)
    rows = [_cell(f, K) for f in FAMILIES for K in KS]
    d = pd.DataFrame(rows)
    d["w_split_over_loo"] = d.w_split / d.w_loo
    d.to_csv("results/center_exactness.csv", index=False)

    fl = d.cov_loo - d.vovk_floor
    print("=== E58: the LOO exactness seam, measured ===")
    print(d[["family", "K", "vovk_floor", "cov_loo", "cov_split", "cov_grand",
             "w_split_over_loo"]].to_string(index=False,
                                            float_format=lambda x: f"{x:.4f}"))
    print(f"\nLOO coverage minus Vovk floor: min {fl.min():+.4f} "
          f"(MC-SE {d.mc_se.iloc[0]:.4f}); "
          f"cells below floor - 2*SE: {(fl < -2 * d.mc_se).sum()} of {len(d)}")
    print(f"grand-mean (excluded case)  : min gap "
          f"{(d.cov_grand - d.vovk_floor).min():+.4f} "
          f"(the self-inclusion deficit Theorem 3 exists to avoid)")
    inf_split = np.isinf(d.w_split).sum()
    print(f"split-fold width / LOO width: median {d.w_split_over_loo.median():.3f}, "
          f"max {d.w_split_over_loo.max():.3f}; infinite-radius cells: {inf_split}")


if __name__ == "__main__":
    main()
