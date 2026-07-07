"""E28 — the wrong-unit coverage collapse (Paper 2 benchmark).

Preregistered in docs/WRONG_UNIT_COVERAGE_PREREG.md. Ground-truth simulation showing
that a band calibrated for round-level or pointwise coverage covers the whole country
TRAJECTORY far below nominal (the recursion ~0.9^L), while the country-trajectory band
holds nominal at any L. All bands are unstudentized, so the only thing that varies is the
UNIT of the nonconformity score.

Reports coverage as produced. Writes results/wrong_unit_coverage.csv.

Run:  python -m pcb.experiments.e28_wrong_unit_coverage
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pcb.util import det_seed

ALPHA = 0.10
K = 30
T = 6
L_GRID = [2, 4, 6, 8]
REPS = 4000
RHO_T = 0.6      # AR(1) across thresholds
RHO_L = 0.3      # compound symmetry across rounds


def _chol(L):
    """Cholesky of Kron(round CS, threshold AR(1)) covariance, shape (L*T, L*T)."""
    tt = np.abs(np.subtract.outer(np.arange(T), np.arange(T)))
    Rt = RHO_T ** tt                                   # AR(1) over thresholds
    Rl = np.full((L, L), RHO_L) + (1 - RHO_L) * np.eye(L)   # compound symmetry
    cov = np.kron(Rl, Rt)
    return np.linalg.cholesky(cov + 1e-10 * np.eye(L * T)), L


def _conf_q(scores):
    """Unstudentized conformal order statistic: ceil((1-a)(K+1))-th of K scores."""
    idx = int(np.ceil((1 - ALPHA) * (K + 1)))
    return np.inf if idx > K else float(np.sort(scores)[idx - 1])


def _run_L(L):
    chol, _ = _chol(L)
    cov_traj = {"marginal": [], "per_round": [], "trajectory": []}
    for r in range(REPS):
        rng = np.random.default_rng(det_seed("e28_wrongunit", L, r))
        # (K+1) exchangeable country error tensors, shape (K+1, L, T)
        Z = rng.standard_normal((K + 1, L * T)) @ chol.T
        E = Z.reshape(K + 1, L, T)
        cal, tgt = E[:K], E[K]

        # 1) Trajectory band: one score per country = max over (l,t)
        q_tr = _conf_q(np.max(np.abs(cal), axis=(1, 2)))
        cov_traj["trajectory"].append(bool(np.max(np.abs(tgt)) <= q_tr))

        # 2) Per-round band: sup-over-thresholds per round; trajectory = all rounds
        ok_round = True
        for l in range(L):
            q_l = _conf_q(np.max(np.abs(cal[:, l, :]), axis=1))
            if np.max(np.abs(tgt[l])) > q_l:
                ok_round = False
                break
        cov_traj["per_round"].append(ok_round)

        # 3) Marginal band: per (l,t) two-sided conformal; trajectory = all points
        ok_marg = True
        for l in range(L):
            for t in range(T):
                col = cal[:, l, t]
                q_m = _conf_q(np.abs(col))         # symmetric two-sided
                if np.abs(tgt[l, t]) > q_m:
                    ok_marg = False
                    break
            if not ok_marg:
                break
        cov_traj["marginal"].append(ok_marg)
    return cov_traj


def main(out="results/wrong_unit_coverage.csv"):
    print(f"E28 wrong-unit coverage: K={K}, T={T}, {REPS} reps, nominal {1-ALPHA:.0%} "
          f"TRAJECTORY coverage\n")
    print(f"  {'L':>3} | {'marginal':>9} | {'per-round':>10} | {'trajectory':>11} | "
          f"{'0.9^L ref':>9}")
    rows = []
    for L in L_GRID:
        c = _run_L(L)
        m = {k: 100 * np.mean(v) for k, v in c.items()}
        se = {k: 100 * np.std(v) / np.sqrt(REPS) for k, v in c.items()}
        print(f"  {L:>3} | {m['marginal']:>8.1f}% | {m['per_round']:>9.1f}% | "
              f"{m['trajectory']:>10.1f}% | {100*0.9**L:>8.1f}%")
        for k in c:
            rows.append(dict(L=L, method=k, traj_cov_pct=m[k], cov_se=se[k], reps=REPS))
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\n  wrote {out}")
    print("  read: only the trajectory band holds nominal across L; per-round and "
          "marginal collapse as the trajectory lengthens (the wrong-unit recursion).")


if __name__ == "__main__":
    main()
