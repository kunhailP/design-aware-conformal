"""E28 — the wrong-unit coverage collapse (Paper 2 benchmark).

Preregistered in docs/WRONG_UNIT_COVERAGE_PREREG.md. Ground-truth simulation showing
that a band calibrated for round-level or pointwise coverage covers the whole country
TRAJECTORY far below nominal (the recursion ~0.9^L), while the country-trajectory band
holds nominal at any L. All bands are unstudentized, so the only thing that varies is the
UNIT of the nonconformity score.

Post-preregistration robustness addition (2026-09): the obvious rejoinder is "of course marginal bands do
not cover jointly -- correct them". So the same run also carries the
Bonferroni-corrected wrong-unit bands (per-round band at alpha/L, per-threshold
band at alpha/(L*T)). Two facts result. (i) At survey scale they do not exist: a
conformal band at level alpha/L needs ceil((1-alpha/L)(K+1)) <= K calibration
countries, i.e. K >= L/alpha - 1, so at K=30 the corrected per-round band has an
infinite radius for every L >= 4 and the corrected per-threshold band for every L
(Theorem 3's infinite-radius convention). (ii) Where they do exist (a K=100
companion run) they over-cover and are wider than the trajectory band, which
holds nominal at every K. The question is therefore not "corrected or not" but
"which unit carries the simultaneous statement most efficiently".

The three original methods are drawn with exactly the shipped seeds and draw
order, so their rows reproduce the committed CSV bit-identically. Writes
results/wrong_unit_coverage.csv (K=30, all five methods) and
results/wrong_unit_coverage_bonferroni.csv (K=30 and K=100, with width ratios).

Run:  python -m pcb.experiments.e28_wrong_unit_coverage
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pcb.util import det_seed

ALPHA = 0.10
K = 30
K_COMPANION = 100
T = 6
L_GRID = [2, 4, 6, 8]
REPS = 4000
RHO_T = 0.6      # AR(1) across thresholds
RHO_L = 0.3      # compound symmetry across rounds

METHODS = ["marginal", "per_round", "trajectory", "per_round_bonf", "marginal_bonf"]


def _chol(L):
    """Cholesky of Kron(round CS, threshold AR(1)) covariance, shape (L*T, L*T)."""
    tt = np.abs(np.subtract.outer(np.arange(T), np.arange(T)))
    Rt = RHO_T ** tt                                   # AR(1) over thresholds
    Rl = np.full((L, L), RHO_L) + (1 - RHO_L) * np.eye(L)   # compound symmetry
    cov = np.kron(Rl, Rt)
    return np.linalg.cholesky(cov + 1e-10 * np.eye(L * T)), L


def _conf_q(scores, alpha=ALPHA, k=K):
    """Unstudentized conformal order statistic: ceil((1-a)(k+1))-th of k scores;
    infinite when that rank exceeds k (Theorem 3's convention)."""
    idx = int(np.ceil((1 - alpha) * (k + 1)))
    return np.inf if idx > k else float(np.sort(scores)[idx - 1])


def bonferroni_feasible_K(L, alpha=ALPHA, per_threshold=False):
    """Smallest K at which the Bonferroni-corrected wrong-unit band is finite."""
    m = L * T if per_threshold else L
    return int(np.ceil(m / alpha)) - 1


def _run_L(L, k=K, seed_tag="e28_wrongunit"):
    chol, _ = _chol(L)
    cov = {m: [] for m in METHODS}
    width = {m: [] for m in METHODS}          # radius relative to the trajectory band
    for r in range(REPS):
        rng = np.random.default_rng(det_seed(seed_tag, L, r))
        # (k+1) exchangeable country error tensors, shape (k+1, L, T)
        Z = rng.standard_normal((k + 1, L * T)) @ chol.T
        E = Z.reshape(k + 1, L, T)
        cal, tgt = E[:k], E[k]

        # 1) Trajectory band: one score per country = max over (l,t)
        q_tr = _conf_q(np.max(np.abs(cal), axis=(1, 2)), k=k)
        cov["trajectory"].append(bool(np.max(np.abs(tgt)) <= q_tr))
        width["trajectory"].append(1.0)

        # 2) Per-round band: sup-over-thresholds per round; trajectory = all rounds
        #    (uncorrected at alpha, and Bonferroni-corrected at alpha/L)
        for name, a in (("per_round", ALPHA), ("per_round_bonf", ALPHA / L)):
            ok, qs = True, []
            for l in range(L):
                q_l = _conf_q(np.max(np.abs(cal[:, l, :]), axis=1), a, k)
                qs.append(q_l)
                if np.max(np.abs(tgt[l])) > q_l:
                    ok = False
            cov[name].append(ok)
            width[name].append(float(np.max(qs)) / q_tr)

        # 3) Marginal band: per (l,t) two-sided conformal; trajectory = all points
        #    (uncorrected, and Bonferroni-corrected at alpha/(L*T))
        for name, a in (("marginal", ALPHA), ("marginal_bonf", ALPHA / (L * T))):
            ok, qs = True, []
            for l in range(L):
                for t in range(T):
                    q_m = _conf_q(np.abs(cal[:, l, t]), a, k)   # symmetric two-sided
                    qs.append(q_m)
                    if np.abs(tgt[l, t]) > q_m:
                        ok = False
            cov[name].append(ok)
            width[name].append(float(np.max(qs)) / q_tr)
    return cov, width


def _rows(L, k, cov, width):
    rows = []
    for m in METHODS:
        c = np.asarray(cov[m], float)
        w = np.asarray(width[m], float)
        finite = np.isfinite(w)
        rows.append(dict(L=L, method=m, K=k, traj_cov_pct=100 * c.mean(),
                         cov_se=100 * c.std() / np.sqrt(REPS), reps=REPS,
                         width_ratio_median=(float(np.median(w[finite]))
                                             if finite.all() else np.inf),
                         feasible=bool(finite.all())))
    return rows


def main(out="results/wrong_unit_coverage.csv",
         out_bonf="results/wrong_unit_coverage_bonferroni.csv"):
    print(f"E28 wrong-unit coverage: K={K}, T={T}, {REPS} reps, nominal {1-ALPHA:.0%} "
          f"TRAJECTORY coverage\n")
    print(f"  {'L':>3} | {'marginal':>9} | {'per-round':>10} | {'trajectory':>11} | "
          f"{'0.9^L ref':>9} | {'round+Bonf':>11} | {'thr+Bonf':>9}")
    rows, rows_b = [], []
    for L in L_GRID:
        cov, width = _run_L(L)
        m = {k: 100 * np.mean(v) for k, v in cov.items()}
        fb = lambda name: (f"{m[name]:>6.1f}% (w×{np.median(width[name]):.2f})"
                           if np.isfinite(width[name]).all() else "   infinite")
        print(f"  {L:>3} | {m['marginal']:>8.1f}% | {m['per_round']:>9.1f}% | "
              f"{m['trajectory']:>10.1f}% | {100*0.9**L:>8.1f}% | "
              f"{fb('per_round_bonf'):>11} | {fb('marginal_bonf'):>9}")
        r = _rows(L, K, cov, width)
        rows.extend(r)
        rows_b.extend(r)
    print(f"\n  Bonferroni feasibility floor K >= L/alpha - 1: "
          + ", ".join(f"L={L}: {bonferroni_feasible_K(L)}" for L in L_GRID)
          + f"  (per-threshold: {bonferroni_feasible_K(8, per_threshold=True)} at L=8)")

    print(f"\n  companion run at K={K_COMPANION} (corrected per-round band finite):")
    print(f"  {'L':>3} | {'per-round':>10} | {'trajectory':>11} | {'round+Bonf':>18} | "
          f"{'thr+Bonf':>18}")
    for L in L_GRID:
        cov, width = _run_L(L, k=K_COMPANION, seed_tag="e28_wrongunit_K100")
        m = {k: 100 * np.mean(v) for k, v in cov.items()}
        fb = lambda name: (f"{m[name]:>6.1f}% (w×{np.median(width[name]):.2f})"
                           if np.isfinite(width[name]).all() else "   infinite")
        print(f"  {L:>3} | {m['per_round']:>9.1f}% | {m['trajectory']:>10.1f}% | "
              f"{fb('per_round_bonf'):>18} | {fb('marginal_bonf'):>18}")
        rows_b.extend(_rows(L, K_COMPANION, cov, width))

    pd.DataFrame(rows).drop(columns=["K"]).to_csv(out, index=False)
    pd.DataFrame(rows_b).to_csv(out_bonf, index=False)
    print(f"\n  wrote {out} and {out_bonf}")
    print("  read: only the trajectory band holds nominal across L; per-round and "
          "marginal collapse as the trajectory lengthens (the wrong-unit recursion); "
          "correcting them by Bonferroni is infeasible at survey K and wider where "
          "feasible.")


if __name__ == "__main__":
    main()
