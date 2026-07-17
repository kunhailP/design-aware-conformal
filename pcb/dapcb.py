"""Design-Aware Population Conformal Bands — the public API.

One entry point, `dapcb(...)`, wraps the *nominal-safe* adaptive selector
(SAFE_SELECTOR_SPEC.md): it takes the transport-error curves of source
populations, each with a design-noise estimate from a complex-survey bootstrap,
and returns a simultaneous band for a new population's latent curve — activating
deconvolution ONLY when four target-blind gates pass, and otherwise reducing to
clustered PCB (low design noise) or a conservative fallback (design noise real but
information insufficient).

Gates (all frozen on the development grid before any confirmatory validation):
  A need        ρ̂_LCB > ρ₀ = 0.47                 design noise materially large
  B finite-K    δ̂_UCB(D) = 0.0061 + 0.0943·D ≤ δ_max = 0.02
                                                  coverage-remainder bound in budget
  C efficiency  Ĝain − Δ_g > g_min = 0.10          beats conservative by a margin
  D stability   min_t (s_plug² − mean_c v²) > (0.05·max s_plug)²
Deconvolution ⟺ A∧B∧C∧D; else ρ̂_LCB≤ρ₀ → PCB, else → conservative.

Guarantee (Theorem 5′, marginal over the whole procedure): the band covers the
target curve with probability ≥ `coverage_level`, finite-sample. The validity
argument uses NO conditional-on-selection step: PCB and conservative are
unstudentized and nested, so choosing between them is validity-free (Lemma NB);
the non-nested deconvolution branch is charged a frozen α-budget (BUDGET_DEC)
via a union bound, and only in the regime where its gate can open at all
(K ≥ 94, a deterministic consequence of the reliability floor). At
cross-national-survey K the guarantee is therefore exact 1−α with no remainder;
when the deconvolution budget is live, `coverage_level = 1 − α − δ̂_UCB(D)`
reports its estimated-law remainder through the observable diagnostic.

Quickstart
----------
>>> import numpy as np
>>> from pcb import dapcb
>>> fit = dapcb(E, V, center, alpha=0.10)   # E,V:(K,T)  center:(T,)
>>> lo, hi = fit.band
>>> print(fit)
"""
from __future__ import annotations
from dataclasses import dataclass

import numpy as np

from .inference.conformal_band import _modulation, isotonic_tighten
from .inference.design_aware import (_finite_quantile, deconv_reliability,
                                     deconv_target_scale, rho_lcb)

# --- frozen safe-selector constants (SAFE_SELECTOR_SPEC.md, development grid) ---
RHO0 = 0.47                 # gate A: SD-ratio cutoff (Gate 5C)
DELTA_MAX = 0.02            # gate B: coverage-remainder budget
DUCB_A, DUCB_B = 0.0061, 0.0943   # gate B: δ̂_UCB(D) = a + b·D
G_MIN = 0.10               # gate C: minimum width gain over conservative
GAIN_MARGIN = 0.05         # gate C: frozen conservative LCB margin (≥1.645·dev SE 0.028)
Z = 1.6448536              # α/2 budget split in the conservative envelope
BUDGET_DEC = 0.10          # fraction of α reserved for the (non-nested)
                           # deconvolution branch when gate B is feasible (K≥94);
                           # below that K the anchor branches keep the full α


def delta_ucb(D: float) -> float:
    """Frozen upper bound on the finite-K deconvolution coverage remainder."""
    return DUCB_A + DUCB_B * float(D)


@dataclass
class DapcbResult:
    """Result of a `dapcb` fit. `band` is (lo, hi), each shape (T,)."""
    band: tuple
    selected_branch: str            # 'PCB' | 'deconvolution' | 'conservative'
    rho_hat: float
    rho_lcb: float
    reliability: float              # diagnostic D (lower = safer)
    delta_ucb: float                # gate-B finite-K remainder bound
    gain_lcb: float                 # gate-C width-gain lower bound (nan if not evaluated)
    coverage_level: float           # guaranteed lower bound on coverage
    fallback_reason: str            # '' if deconvolution was used
    overlap_warning: bool           # band hit the [0,1] boundary (uninformative there)

    def __repr__(self):
        lo, hi = self.band
        w = float(np.mean(hi - lo))
        r = (f"DapcbResult(branch={self.selected_branch!r}, "
             f"coverage≥{self.coverage_level:.3f}, mean_width={w:.3f}, "
             f"ρ̂={self.rho_hat:.3f} (LCB {self.rho_lcb:.3f}), D={self.reliability:.3f}, "
             f"δ̂_UCB={self.delta_ucb:.3f}")
        if not np.isnan(self.gain_lcb):
            r += f", gain_LCB={self.gain_lcb:.3f}"
        if self.fallback_reason:
            r += f", fallback: {self.fallback_reason}"
        if self.overlap_warning:
            r += ", ⚠ band touches [0,1] bound"
        return r + ")"


def _quantiles(E, sT, V, alpha_anchor, alpha_dec):
    """Conformal max-score quantiles for PCB, safe-deconvolution, conservative.

    PCB and conservative use UNSTUDENTIZED scores (U0 construction): each score
    depends only on its own cluster's data, so the K+1 scores are exchangeable
    and the order-statistic band is exact at any K. Because the conservative
    score max_t(|E_c|+z·v_c) dominates the PCB score max_t|E_c| pointwise, the
    two bands are NESTED (B_PCB ⊆ B_con) at the same level — which makes any
    data-dependent choice between them validity-free (Lemma NB in the paper:
    selecting the wider of two nested bands, by any rule, cannot reduce the
    coverage of the narrower band's guarantee). The deconvolution branch keeps
    its studentized construction and is calibrated at its own budget alpha_dec.
    """
    q_pcb = _finite_quantile(np.max(np.abs(E), 1), alpha_anchor)
    q_dec = _finite_quantile(np.max(np.abs(E) / np.sqrt(sT[None]**2 + V**2), 1),
                             alpha_dec)
    q_con = _finite_quantile(np.max(np.abs(E) + Z * V, 1), alpha_anchor)
    return q_pcb, q_dec, q_con


def gate_b_feasible(K: int) -> bool:
    """Whether gate B can open at all at this K — a deterministic fact.

    The reliability diagnostic obeys D ≥ √(2/(K−1)) BY CONSTRUCTION of the
    frozen SE formula (ŝ_T ≤ s_plug and the 2s⁴/(K−1) term), so
    δ̂_UCB(D) ≥ δ̂_UCB(√(2/(K−1))). If that already exceeds δ_max, no data can
    open gate B (Proposition 1's algorithmic floor: K ≥ 94 at the frozen
    constants). In that regime the deconvolution branch is unreachable and the
    deployed guarantee needs no α-budget for it.
    """
    floor = float(np.sqrt(2.0 / max(K - 1, 1)))
    return delta_ucb(floor) <= DELTA_MAX


def _gain_lcb(r_dec, r_con):
    """Lower bound on the deconvolution width gain 1 − W_dec/W_con: the point gain
    minus a frozen conservative margin (GAIN_MARGIN ≥ 1.645× the development
    jackknife SE). O(1); no per-cluster resampling."""
    w_dec, w_con = float(np.mean(r_dec)), float(np.mean(r_con))
    gain = 1.0 - w_dec / w_con if w_con > 0 else 0.0
    return gain - GAIN_MARGIN


def dapcb(cal_errors, v_cal, center, alpha: float = 0.10,
          tighten: bool = True) -> DapcbResult:
    """Nominal-safe adaptive design-aware population conformal band.

    Parameters
    ----------
    cal_errors : (K, T) array
        Transport-error curves E_c(t) = F̂_c(t) − F̃_c(t) of K source populations
        (the exchangeable unit is the population/country) over a T-threshold grid.
    v_cal : (K, T) array
        Design-noise SDs v_c(t) from a stratified-PSU / replicate-weight bootstrap
        (`pcb.inference.design_aware.design_sd`); zeros for a census source.
    center : (T,) array
        Predicted curve for the new, unsurveyed target population.
    alpha : float
        Miscoverage level.

    Returns
    -------
    DapcbResult with the band and the selection diagnostics. The safe-selector
    constants are frozen (SAFE_SELECTOR_SPEC.md) and not user-tunable.
    """
    E = np.asarray(cal_errors, float)
    V = np.asarray(v_cal, float)
    center = np.asarray(center, float)
    if E.ndim != 2 or V.shape != E.shape:
        raise ValueError("cal_errors and v_cal must be (K, T) with equal shape")
    K = E.shape[0]
    s = _modulation(E)                # diagnostics + deconvolution scale only
    sT = deconv_target_scale(E, V)

    # Validity architecture (Theorem 5′, no conditional-coverage step):
    #  * PCB and conservative are UNSTUDENTIZED (U0) and NESTED
    #    (B_PCB ⊆ B_con at the same level), so any target-blind choice between
    #    them inherits the PCB anchor's exact guarantee for free (Lemma NB) —
    #    P(miss) = P(miss ∧ J=PCB) + P(miss ∧ J=con) ≤ P(miss_PCB) ≤ α_anchor.
    #  * The deconvolution branch is NOT nested (it is narrower), so it gets
    #    its own miss budget via a union bound — but only in the regime where
    #    gate B can open at all (K ≥ 94, `gate_b_feasible`, a deterministic
    #    fact). At cross-national-survey K the branch is unreachable and the
    #    anchor keeps the FULL α: the deployed guarantee is exact with no
    #    remainder and no selection conditions.
    feasible = gate_b_feasible(K)
    a_anchor = alpha * (1.0 - BUDGET_DEC) if feasible else alpha
    a_dec = alpha * BUDGET_DEC
    q_pcb, q_dec, q_con = _quantiles(E, sT, V, a_anchor, a_dec)
    r_pcb = np.full(E.shape[1], q_pcb)
    r_con = np.full(E.shape[1], q_con)
    r_dec = q_dec * sT
    rl = rho_lcb(E, V)
    D = deconv_reliability(E, V)
    d_ucb = delta_ucb(D)
    stable = bool((s**2 - (V**2).mean(0) > (0.05 * s.max())**2).all())

    # branch choice (target-blind; affects width, not validity): A ∧ B ∧ C ∧ D
    # → deconvolution, else PCB when design noise is negligible, else the
    # conservative envelope.
    reason, gain_lcb = "", float("nan")
    if rl <= RHO0:                                        # gate A fails: no need
        branch, radius = "PCB", r_pcb
        reason = "design noise negligible (ρ̂_LCB ≤ ρ₀) → clustered PCB"
    else:
        gate_b = feasible and (d_ucb <= DELTA_MAX)
        gate_d = stable
        if gate_b and gate_d:
            gain_lcb = _gain_lcb(r_dec, r_con)
            gate_c = gain_lcb > G_MIN
        else:
            gate_c = False
        if gate_b and gate_d and gate_c:
            branch, radius = "deconvolution", r_dec
        else:
            branch, radius = "conservative", r_con
            reason = ("finite-K remainder too large (δ̂_UCB > δ_max)" if not gate_b
                      else "deconvolution unstable" if not gate_d
                      else "width gain insufficient (Ĝain_LCB ≤ g_min)"
                      ) + " → conservative fallback"
    # Marginal guarantee of the WHOLE procedure (not per realized branch):
    # exact 1−α when the deconvolution branch is unreachable; 1−α−δ̂ once the
    # α-budget exposes the estimated-law branch (its Theorem-4 remainder,
    # reported via the observable δ̂_UCB diagnostic).
    cov = 1 - alpha - (d_ucb if feasible else 0.0)

    lo, hi = center - radius, center + radius
    if tighten:
        lo, hi = isotonic_tighten(np.clip(lo, 0, 1), np.clip(hi, 0, 1))
    else:
        lo, hi = np.clip(lo, 0, 1), np.clip(hi, 0, 1)
    warn = bool(np.any(lo <= 0) and np.any(hi >= 1))
    return DapcbResult((lo, hi), branch, float(np.sqrt((V**2).mean()) / s.mean()),
                       float(rl), float(D), float(d_ucb), float(gain_lcb),
                       float(cov), reason, warn)
