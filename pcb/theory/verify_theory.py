"""Numerical verification of docs/PROOFS.md.

Checks the three results on synthetic standardized transport-error curves drawn
from a mean-zero Gaussian process with exponentially-decaying threshold
correlation (a model for the dependence of CDF values at nearby thresholds):

  Prop 1   per-threshold band is marginally valid but jointly under-covers, with
           Cov_sim(B^M) in [max(0,1-T*alpha), 1-alpha].
  Thm 2    Cov_sim(B^M) -> P(M <= z_{1-a/2}) and lies in [(1-a)^T, 1-a];
           PCB targets the sup-quantile c_alpha and recovers 1-alpha.
  Thm 3    q_sup <= z_{1-a/(2T)} (PCB radius <= Bonferroni radius), with PCB and
           Bonferroni both simultaneously valid -> PCB dominates on width.

Run:  python -m pcb.theory.verify_theory
"""
from __future__ import annotations
import numpy as np
from scipy.stats import norm


def _draw(n, T, rho, rng):
    """n standardized error curves W in R^T, Corr = rho^|i-j|."""
    idx = np.arange(T)
    C = rho ** np.abs(idx[:, None] - idx[None, :])
    L = np.linalg.cholesky(C + 1e-10 * np.eye(T))
    return rng.standard_normal((n, T)) @ L.T


def run_cell(T=19, K=400, alpha=0.1, rho=0.8, n_test=40000, seed=0):
    rng = np.random.default_rng(seed)
    cal = _draw(K, T, rho, rng)
    test = _draw(n_test, T, rho, rng)
    m = int(np.ceil((1 - alpha) * (K + 1)))

    # per-threshold conformal radii (sigma = 1 here)
    qt = np.sort(np.abs(cal), axis=0)[m - 1]                 # (T,)
    # sup-score conformal radius
    qsup = np.sort(np.max(np.abs(cal), axis=1))[m - 1]
    # Bonferroni per-threshold radii at level 1 - alpha/T
    mb = int(np.ceil((1 - alpha / T) * (K + 1)))
    finite_bonf = mb <= K
    qbonf = np.sort(np.abs(cal), axis=0)[min(mb, K) - 1] if finite_bonf else np.full(T, np.inf)

    cov_marg_pt = (np.abs(test) <= qt[None, :]).mean()
    cov_marg_sim = (np.abs(test) <= qt[None, :]).all(axis=1).mean()
    cov_sup_sim = (np.max(np.abs(test), axis=1) <= qsup).mean()
    cov_bonf_sim = (np.abs(test) <= qbonf[None, :]).all(axis=1).mean()

    z = norm.ppf(1 - alpha / 2)
    zbonf = norm.ppf(1 - alpha / (2 * T))
    p_M_le_z = (np.max(np.abs(test), axis=1) <= z).mean()     # P(M <= z_{1-a/2})

    return dict(T=T, K=K, alpha=alpha, rho=rho,
                cov_marg_pt=cov_marg_pt, cov_marg_sim=cov_marg_sim,
                cov_sup_sim=cov_sup_sim, cov_bonf_sim=cov_bonf_sim,
                floor=(1 - alpha) ** T, p_M_le_z=p_M_le_z,
                qsup=qsup, zbonf=zbonf, z=z,
                w_sup=2 * qsup, w_bonf=2 * float(np.mean(qbonf)),
                w_marg=2 * float(np.mean(qt)), finite_bonf=finite_bonf)


def main():
    alpha = 0.1
    ok = True
    print("=== Prop 1 + Thm 2: marginal valid, jointly under-covers, sandwich ===")
    print(f"{'rho':>5} {'T':>3} | {'marg_pt':>7} {'marg_sim':>8} {'floor':>6} "
          f"{'P(M<=z)':>7} {'PCB_sim':>7}")
    for rho in (0.5, 0.8, 0.95):
        r = run_cell(T=19, K=1500, alpha=alpha, rho=rho, seed=1)
        print(f"{rho:>5} {r['T']:>3} | {r['cov_marg_pt']*100:6.1f}% "
              f"{r['cov_marg_sim']*100:7.1f}% {r['floor']*100:5.1f}% "
              f"{r['p_M_le_z']*100:6.1f}% {r['cov_sup_sim']*100:6.1f}%")
        # Prop 1 marginal validity
        ok &= r['cov_marg_pt'] >= 1 - alpha - 0.01
        # Thm 2 sandwich: floor <= marg_sim <= 1 - alpha
        ok &= r['floor'] - 0.01 <= r['cov_marg_sim'] <= 1 - alpha + 0.01
        # Thm 2(a): marg_sim ~ P(M <= z_{1-a/2}) (asymptotic in K; finite-K tolerance)
        ok &= abs(r['cov_marg_sim'] - r['p_M_le_z']) < 0.03
        # Thm 2(c): PCB recovers nominal
        ok &= r['cov_sup_sim'] >= 1 - alpha - 0.01

    print("\n=== Thm 3: PCB radius <= Bonferroni radius; both simultaneously valid ===")
    print(f"{'rho':>5} | {'q_sup':>6} {'z_bonf':>6} {'w_sup':>6} {'w_bonf':>6} "
          f"{'ratio':>6} | {'PCB_sim':>7} {'Bonf_sim':>8}")
    for rho in (0.5, 0.8, 0.95):
        r = run_cell(T=19, K=1500, alpha=alpha, rho=rho, seed=2)
        ratio = r['w_sup'] / r['w_bonf']
        print(f"{rho:>5} | {r['qsup']:6.3f} {r['zbonf']:6.3f} "
              f"{r['w_sup']:6.3f} {r['w_bonf']:6.3f} {ratio:6.3f} | "
              f"{r['cov_sup_sim']*100:6.1f}% {r['cov_bonf_sim']*100:7.1f}%")
        # Thm 3: q_sup <= z_{1-a/(2T)} (Gaussian limit) and PCB no wider than Bonferroni
        ok &= r['qsup'] <= r['zbonf'] + 0.05
        ok &= r['w_sup'] <= r['w_bonf'] + 1e-9
        # realized conformal coverage fluctuates around the >= 1-alpha guarantee at finite K
        ok &= r['cov_sup_sim'] >= 1 - alpha - 0.015
        ok &= r['cov_bonf_sim'] >= 1 - alpha - 0.015

    print("\n=== Sandwich vs observed empirical joint coverages (THEORY Thm 2b) ===")
    for T, obs, lbl in [(19, 0.375, "E1 pseudo-pop"), (10, 0.541, "E3 PIP consumption")]:
        floor = (1 - alpha) ** T
        inside = floor <= obs <= 1 - alpha
        print(f"  {lbl:>20} (T={T}): floor (1-a)^T={floor:.3f} <= obs={obs:.3f} "
              f"<= 1-a=0.900  -> {'inside ✓' if inside else 'OUTSIDE ✗'}")
        ok &= inside

    print("\n" + ("ALL THEORY CHECKS PASS ✓" if ok else "SOME CHECKS FAILED ✗"))
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
