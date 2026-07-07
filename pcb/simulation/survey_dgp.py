"""E6 simulation — survey-design population hierarchy (Design-Aware PCB).

What `generate_populations.py` cannot stage: a SOURCE CURVE THAT IS ITSELF A
SURVEY ESTIMATE. There each population's weighted sample CDF is treated as the
truth, so survey sampling error does not exist and the oracle/plug-in/DA
comparison is undefined. Here each population has an exact superpopulation
curve θ_g (computable in closed form), and what the analyst observes is a
weighted estimate θ̃_g from a two-stage cluster sample with informative PSU
selection — the ESS-like regime (n ≈ 600–2500, deff from clustering + weight
dispersion).

Generative law (population g):
    a_g = z_g + ν_g,  z_g ~ N(0, s_z),  ν_g ~ N(0, s_transport)
    latent  Y*_gi = a_g + u_c(i) + ε_gi,  u_c ~ N(0, σ_u²),  ε ~ Logistic(0,1)
    ordinal Y_gi = #{k : τ_k ≤ Y*_gi}  ∈ {0, …, T}   (trust-style 0–10 scale)
The predictor sees z_g only (never ν_g), so ν_g is the transport error — same
philosophy as generate_populations.py. σ_u sets the latent ICC
σ_u²/(σ_u²+π²/3); PSU inclusion ∝ exp(γ·u_c) makes the design informative
(weights 1/π correct it); a mean-one lognormal weight jitter (η) mimics
nonresponse-adjustment weight dispersion.

Truth is exact: θ_g(t) = E_u[Λ(τ_{t+1} − a_g − u)] by Gauss–Hermite, so
coverage against the true curve carries no Monte-Carlo error.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

T_CATS = 11                      # 0–10 ordinal scale
T_GRID = T_CATS - 1              # informative thresholds t = 0..9 (P(Y≤10)=1)
TAU = 1.5 * np.log(np.arange(1, T_CATS) / (T_CATS - np.arange(1, T_CATS)))
N_PSU_FRAME = 200                # PSU frame size per population
_GH_X, _GH_W = np.polynomial.hermite.hermgauss(41)


@dataclass
class SurveyDesign:
    """Per-population survey design knobs."""
    m_psu: int = 30              # sampled PSUs
    b_per_psu: int = 50          # individuals per sampled PSU (n = m·b)
    icc: float = 0.05            # latent-scale intraclass correlation
    gamma: float = 0.5           # informativeness: PSU inclusion ∝ exp(γ·u_c)
    eta: float = 0.3             # lognormal weight-jitter SD (nonresponse-style)

    @property
    def sigma_u(self) -> float:
        return float(np.sqrt(self.icc / (1 - self.icc) * np.pi**2 / 3))


@dataclass
class SurveySimConfig:
    K: int = 50                  # source populations (plus 1 target)
    s_z: float = 0.5             # observed between-population scale
    s_transport: float = 0.3     # unobserved shift ν_g = the transport error
    designs: tuple = (SurveyDesign(),)   # each population draws one uniformly
    seed: int = 0


def true_curve(a: float, sigma_u: float) -> np.ndarray:
    """Exact θ(t) = E_u[Λ(τ_{t+1} − a − u)], u ~ N(0, σ_u²); shape (T_GRID,)."""
    u = np.sqrt(2.0) * sigma_u * _GH_X                       # (41,)
    z = TAU[None, :] - a - u[:, None]                        # (41, T)
    return (_GH_W @ (1.0 / (1.0 + np.exp(-z)))) / np.sqrt(np.pi)


def draw_survey(a: float, d: SurveyDesign, rng: np.random.Generator):
    """Two-stage informative cluster sample from population with intercept a.

    Returns dict with
      theta_tilde : (T,) weighted sample CDF (the analyst's plug-in truth)
      psu_cnt     : (m, T) per-PSU weighted threshold counts  } sufficient for
      psu_tot     : (m,)   per-PSU weight totals              } design bootstrap
      n           : sample size
    """
    su = d.sigma_u
    u_frame = rng.normal(0.0, su, size=N_PSU_FRAME)
    p = np.exp(d.gamma * u_frame)
    p /= p.sum()
    sel = rng.choice(N_PSU_FRAME, size=d.m_psu, replace=False, p=p)
    u_sel = u_frame[sel]
    w_psu = 1.0 / (d.m_psu * p[sel])                         # ≈ 1/π_c

    n = d.m_psu * d.b_per_psu
    eps = rng.logistic(0.0, 1.0, size=(d.m_psu, d.b_per_psu))
    ystar = a + u_sel[:, None] + eps
    cat = np.searchsorted(TAU, ystar)                        # 0..10
    w = w_psu[:, None] * rng.lognormal(-d.eta**2 / 2, d.eta, size=cat.shape)

    ind = cat[:, :, None] <= np.arange(T_GRID)[None, None, :]     # (m, b, T)
    psu_cnt = (w[:, :, None] * ind).sum(axis=1)                   # (m, T)
    psu_tot = w.sum(axis=1)                                       # (m,)
    return dict(theta_tilde=psu_cnt.sum(0) / psu_tot.sum(),
                psu_cnt=psu_cnt, psu_tot=psu_tot, n=n)


def generate_survey_hierarchy(cfg: SurveySimConfig, rng=None):
    """Draw K sources + 1 target; every population is surveyed (the target's
    survey is used only by the validation view, never by the methods).

    Returns dict with per-population lists (index -1 = target):
      theta_true (K+1, T), theta_hat (K+1, T)  [predictor: knows z, not ν],
      surveys (list of draw_survey dicts), designs (list of SurveyDesign).
    """
    if rng is None:
        rng = np.random.default_rng(cfg.seed)
    K = cfg.K
    z = rng.normal(0.0, cfg.s_z, size=K + 1)
    nu = rng.normal(0.0, cfg.s_transport, size=K + 1)
    designs = [cfg.designs[rng.integers(len(cfg.designs))] for _ in range(K + 1)]

    theta_true = np.zeros((K + 1, T_GRID))
    theta_hat = np.zeros((K + 1, T_GRID))
    surveys = []
    for g in range(K + 1):
        su = designs[g].sigma_u
        theta_true[g] = true_curve(z[g] + nu[g], su)
        theta_hat[g] = true_curve(z[g], su)      # transport error = effect of ν_g
        surveys.append(draw_survey(z[g] + nu[g], designs[g], rng))

    return dict(theta_true=theta_true, theta_hat=theta_hat,
                surveys=surveys, designs=designs, K=K)
