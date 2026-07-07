"""E2 simulation — synthetic population hierarchy generator.

Lets us control what real data cannot: the NUMBER of exchangeable populations K
and the SEVERITY of shift. This is what turns the project from an application
into a methods paper (RESEARCH_DESIGN §6 E2).

Generative law (shared across populations = the hyper-distribution Π):
    population i has a latent intercept a_i ~ N(0, s_shift)   (unobserved)
                       a covariate mean shift m_i ~ N(0, s_shift)
    households:  X_ij ~ N(m_i, I_d)
                 log Y_ij = a_i + X_ij·β + s_mis·(X_{ij,0}^2)  + ε_ij,  ε~N(0,σ²)
The predictor sees X only (NOT the population id), so it can never recover the
TARGET's a_{K+1} → this is the transport error. With s_mis>0 the missed
quadratic term makes that error biased and non-Gaussian, which is exactly the
regime where the Gaussian inflation (M1) should fail but conformal (M2) hold
(pre-registered H2). With s_shift=0 there is no between-population variation and
naive coverage should be ~nominal (sanity).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

BETA = np.array([1.0, -0.5, 0.8, 0.3, -0.2])  # fixed shared coefficients (d=5)
D = len(BETA)
SIGMA_Y = 0.5  # household-level log-consumption noise


@dataclass
class SimConfig:
    K: int = 10
    shift: str = "medium"            # none|low|medium|high
    misspec: str = "mild"            # none|mild|severe
    n_per_pop: int = 2000
    n_thresholds: int = 19
    threshold_focus: str = "median"  # lower_tail|median|upper_tail
    structured: bool = False         # if True, intercept a_i is tied to covariate
                                     # mean m_i, so OBSERVABLE population distance
                                     # predicts transport-error similarity (the
                                     # regime where M3 weighting can help — H4)
    seed: int = 0
    shift_scale: dict = field(default_factory=lambda: {
        "none": 0.0, "low": 0.10, "medium": 0.25, "high": 0.50})
    misspec_scale: dict = field(default_factory=lambda: {
        "none": 0.0, "mild": 0.15, "severe": 0.40})


_FOCUS = {
    "lower_tail": (0.05, 0.30),
    "median": (0.30, 0.70),
    "upper_tail": (0.70, 0.95),
}


def generate_population_hierarchy(cfg: SimConfig, rng=None):
    """Draw K source populations + 1 target from Π.

    Returns dict with:
      thresholds : (T,)
      pops       : list of K+1 dicts {X, y, w, a}; index -1 is the target
      theta_true : (K+1, T) true weighted headcount per population (oracle)
      s_shift, s_mis : the numeric knobs (for reporting σ_between vs Proposition 1)
    """
    if rng is None:
        rng = np.random.default_rng(cfg.seed)
    s_shift = cfg.shift_scale[cfg.shift]
    s_mis = cfg.misspec_scale[cfg.misspec]
    T, n, K = cfg.n_thresholds, cfg.n_per_pop, cfg.K

    u = np.ones(D) / np.sqrt(D)  # fixed direction linking covariates to intercept
    pops = []
    for _ in range(K + 1):
        m_i = rng.normal(0.0, s_shift, size=D)
        if cfg.structured and s_shift > 0:
            # intercept correlated with covariate mean → observable distance
            # predicts the (otherwise unobserved) transport error
            a_i = float(m_i @ u) + rng.normal(0.0, 0.3 * s_shift)
        else:
            a_i = rng.normal(0.0, s_shift)  # intercept independent of covariates
        X = rng.normal(m_i, 1.0, size=(n, D))
        logy = (a_i + X @ BETA + s_mis * (X[:, 0] ** 2)
                + rng.normal(0.0, SIGMA_Y, size=n))
        y = np.exp(logy)
        w = rng.gamma(shape=4.0, scale=0.25, size=n)  # survey weights, mean ≈ 1
        pops.append(dict(X=X, y=y, w=w, a=a_i))

    # thresholds from pooled SOURCE consumption, placed by focus
    src_y = np.concatenate([p["y"] for p in pops[:K]])
    lo, hi = _FOCUS[cfg.threshold_focus]
    thr = np.quantile(src_y, np.linspace(lo, hi, T))

    theta_true = np.zeros((K + 1, T))
    for i, p in enumerate(pops):
        wn = p["w"] / p["w"].sum()
        theta_true[i] = (wn[:, None] * (p["y"][:, None] < thr[None, :])).sum(0)

    return dict(thresholds=thr, pops=pops, theta_true=theta_true,
                s_shift=s_shift, s_mis=s_mis, K=K)
