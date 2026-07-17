"""DA-PCB — Design-Aware Population Conformal Bands (prototype, E6).

Plug-in PCB calibrates on E_g = θ̂_g − θ̃_g, treating each source's weighted
sample CDF θ̃_g as the truth. When the sources are themselves modest surveys
(ESS-scale n with clustering and weight dispersion), E_g = T_g − S_g conflates
the transport error T_g = θ̂_g − θ_g with the survey error S_g = θ̃_g − θ_g.
Three consequences the E6 pilot measures:
  (i)  deployment (unsurveyed target, truth evaluation): the target score has
       no S term, so plug-in calibration is stochastically inflated —
       conservative coverage bought at inflated width;
  (ii) validation (surveyed target, evaluated against θ̃): a target whose
       survey is noisier than the calibration mix undercovers — the plug-in
       failure is CONDITIONAL, appearing under design heterogeneity;
  (iii) both distortions are estimable from the design: a PSU bootstrap gives
       v_g(t) = SD of S_g(t), enabling the corrections below.

Variants:
  * `da_studentized_band` — deconvolve the transport scale
    s_T² = s_plug² − mean_g v_g², studentise scores by the population-specific
    total scale √(s_T² + v_g²), score the target with its own v (0 in
    deployment). Aims at oracle width and conditional validity.
  * `da_worstcase_band` — score each source by its worst-case error over the
    design uncertainty set C_g = [L_g, U_g] (max distance from θ̂_g to the
    band ends). Conservative by construction: an upper envelope, not an
    efficiency device.
Validity is exact for plug-in/oracle (exchangeable scores); for the DA
variants it is approximate at the pilot stage (local-scale studentisation) —
the simulation quantifies the gap before any theory is claimed.
"""
from __future__ import annotations
import numpy as np

from .conformal_band import _modulation, isotonic_tighten


def psu_bootstrap(psu_cnt: np.ndarray, psu_tot: np.ndarray, B: int = 200,
                  rng=None, rescale: bool = False) -> np.ndarray:
    """PSU bootstrap of the weighted CDF. Returns (B, T).

    rescale=False: naive m-of-m with-replacement resampling. Known to
        UNDERSTATE the between-PSU variance by a factor (m-1)/m per stratum
        (severe in 2-PSU strata), and it is what produced the shipped result
        CSVs — the direction of the bias is disclosed in the paper.
    rescale=True: Rao–Wu–Yue rescaling bootstrap (Rao & Wu 1988; Rao, Wu &
        Yue 1992) — draw m−1 PSUs with replacement and scale totals by
        m/(m−1), which unbiases the with-replacement variance estimator.
        Use this for any rerun; single-PSU strata (m=1) still carry no
        internal variance information and must be collapsed upstream.
    """
    if rng is None:
        rng = np.random.default_rng(0)
    m = psu_tot.shape[0]
    if rescale:
        if m < 2:
            est = (psu_cnt.sum(axis=0) / psu_tot.sum(axis=0))[None, :]
            return np.repeat(est, B, axis=0)          # no variance info: flat
        idx = rng.integers(0, m, size=(B, m - 1))
        f = m / (m - 1.0)
        return (psu_cnt[idx].sum(axis=1) * f) / (psu_tot[idx].sum(axis=1) * f)[:, None]
    idx = rng.integers(0, m, size=(B, m))
    return psu_cnt[idx].sum(axis=1) / psu_tot[idx].sum(axis=1)[:, None]


def design_sd(psu_cnt, psu_tot, B: int = 200, rng=None,
              rescale: bool = False) -> np.ndarray:
    """v_g(t): design-based SD of the survey error S_g(t)."""
    return psu_bootstrap(psu_cnt, psu_tot, B, rng, rescale=rescale).std(axis=0)


def _finite_quantile(scores: np.ndarray, alpha: float) -> float:
    K = scores.shape[0]
    idx = int(np.ceil((1 - alpha) * (K + 1)))
    return np.inf if idx > K else float(np.sort(scores)[idx - 1])


def _finish(center, half, tighten):
    if np.any(np.isinf(half)):
        lo, hi = np.zeros_like(center), np.ones_like(center)
    else:
        lo, hi = center - half, center + half
    if tighten:
        return isotonic_tighten(lo, hi)
    return np.clip(lo, 0, 1), np.clip(hi, 0, 1)


def deconv_target_scale(cal_errors: np.ndarray, v_cal: np.ndarray,
                        z: float = 1.6448536, floor_frac: float = 0.05):
    """Finite-K-safe deconvolved target scale ŝ_T,safe(t) (docs/FINITE_K_
    CORRECTION_PROTOCOL.md).

    Guards the mean(v²) subtraction with its one-sided lower CI, so we subtract
    LESS when the design-noise estimate is uncertain:
        ŝ_T,safe² = max( s_plug² − [mean_c v̂_c² − z·SE]_+ , floor ),
        SE = SD_c(v̂²)/√K.
    z = Φ⁻¹(1−α₂) is the α-budget-split constant (default 1.645 = Φ⁻¹(0.95),
    α₂=α/2=0.05). Reduces to s_plug (clustered PCB) as v→0 and is never > s_plug —
    an efficiency dial between full deconvolution (z→0) and plug-in.
    """
    E, V = np.asarray(cal_errors, float), np.asarray(v_cal, float)
    K = E.shape[0]
    s_plug = _modulation(E, floor_frac)
    mv = (V**2).mean(axis=0)
    se = (V**2).std(axis=0) / np.sqrt(max(K, 1))
    sub = np.maximum(mv - z * se, 0.0)
    floor = (floor_frac * s_plug.max()) ** 2
    return np.sqrt(np.maximum(s_plug**2 - sub, floor))


def rho_lcb(cal_errors: np.ndarray, v_cal: np.ndarray, z: float = 1.6448536,
            floor_frac: float = 0.05) -> float:
    """One-sided lower confidence bound on ρ = design-SD / total-SD.

    ρ = √(mean v²) / s_plug where s_plug² = s_R² + mean v² is the *total* (plug-in)
    spread — so ρ ∈ [0,1), NOT the design/transport ratio v/s_R (which is unbounded
    and is the generative dial in the simulation). The width law W_dec/W_pcb =
    √(1−ρ²) and the ρ₀=0.47 gate are both on this design/total ρ. Conservative about
    whether design noise matters: subtract z·SE from mean(v²) and inflate s_plug².
    Used by the safe selector's "need" gate (ρ̂_LCB > ρ₀).
    """
    E, V = np.asarray(cal_errors, float), np.asarray(v_cal, float)
    K = E.shape[0]
    s_plug = _modulation(E, floor_frac)
    mv = (V**2).mean(0); se = (V**2).std(0) / np.sqrt(max(K, 1))
    num = np.maximum(mv - z * se, 0.0).mean()
    den = (s_plug**2 * (1 + z * np.sqrt(2 / max(K - 1, 1)))).mean()
    return float(np.sqrt(num / den)) if den > 0 else 0.0


def deconv_reliability(cal_errors: np.ndarray, v_cal: np.ndarray,
                       floor_frac: float = 0.05) -> float:
    """Finite-K reliability diagnostic D = max_t SE(ŝ_T,safe²)/ŝ_T,safe².

    Large D ⇒ the deconvolved scale is poorly determined ⇒ the deconvolution is
    unsafe at this K. The safe selector's "safety" gate is D ≤ τ (τ calibrated on
    a simulation grid to guarantee coverage ≥ 1−α−δ).
    """
    E, V = np.asarray(cal_errors, float), np.asarray(v_cal, float)
    K = E.shape[0]
    s_plug = _modulation(E, floor_frac)
    sT2 = deconv_target_scale(E, V, floor_frac=floor_frac) ** 2
    se_sT2 = np.sqrt(2 * s_plug**4 / max(K - 1, 1) + ((V**2).std(0) / np.sqrt(K))**2)
    return float(np.max(se_sT2 / np.maximum(sT2, 1e-12)))


def da_studentized_band(cal_errors: np.ndarray, v_cal: np.ndarray,
                        center: np.ndarray, v_target: np.ndarray | None = None,
                        alpha: float = 0.1, tighten: bool = True,
                        floor_frac: float = 0.05):
    """Deconvolved, design-studentised DA-PCB.

    cal_errors : (K, T) plug-in errors θ̂_g − θ̃_g.
    v_cal      : (K, T) design SDs v_g(t) of the source survey errors.
    v_target   : (T,) design SD of the target's survey error — None/zeros for
                 deployment (unsurveyed target, band for the true curve);
                 the target's own v when evaluating against θ̃_target.
    """
    E, V = np.asarray(cal_errors, float), np.asarray(v_cal, float)
    s_plug = _modulation(E, floor_frac)
    floor = (floor_frac * s_plug.max()) ** 2
    s_T = np.sqrt(np.maximum(s_plug**2 - (V**2).mean(axis=0), floor))
    scores = np.max(np.abs(E) / np.sqrt(s_T[None, :]**2 + V**2), axis=1)
    q = _finite_quantile(scores, alpha)
    vt = np.zeros_like(s_T) if v_target is None else np.asarray(v_target, float)
    return _finish(np.asarray(center, float),
                   q * np.sqrt(s_T**2 + vt**2), tighten)


def da_worstcase_band(cal_errors: np.ndarray, theta_hat_cal: np.ndarray,
                      design_lo: np.ndarray, design_hi: np.ndarray,
                      center: np.ndarray, alpha: float = 0.1,
                      tighten: bool = True):
    """Worst-case DA-PCB: score = sup_t max(|θ̂−L|, |θ̂−U|)/s(t).

    theta_hat_cal : (K, T) source plug-in curves θ̂_g.
    design_lo/hi  : (K, T) design uncertainty bands [L_g, U_g] around θ̃_g.
    """
    E = np.asarray(cal_errors, float)
    s = _modulation(E)
    wc = np.maximum(np.abs(theta_hat_cal - design_lo),
                    np.abs(theta_hat_cal - design_hi))
    q = _finite_quantile(np.max(wc / s[None, :], axis=1), alpha)
    return _finish(np.asarray(center, float), q * s, tighten)
