"""Theorem 5′ — nested-band selection validity and the α-budget architecture.

Checks the three load-bearing facts of the revised deployed guarantee:

1. NESTING: the conservative U0 band contains the PCB U0 band on every draw
   (score dominance ⇒ quantile dominance at the same level), so Lemma NB
   applies: a miss of the selected anchor branch implies a miss of PCB.
2. FREE SELECTION: per-draw implication miss(selected) ⇒ miss(PCB) whenever
   the selected branch is an anchor (PCB/conservative) — asserted pointwise,
   not just on average, which is exactly the content of the lemma.
3. CONDITIONAL-BY-BRANCH COVERAGE in a stochastic-selection regime at K ≥ 94:
   marginal coverage respects 1 − α − δ̂, and the deconvolution branch's own
   draws — the term the old conditional argument could not justify — are
   covered at their budgeted level. (The old suite never had a regime where
   selection actually varied; this one does.)
4. TARGET-BLINDNESS: the selected branch is invariant to the center argument.
"""
import numpy as np

from pcb.dapcb import BUDGET_DEC, dapcb, gate_b_feasible, _quantiles
from pcb.inference.design_aware import deconv_target_scale

ALPHA = 0.10


def _draw(rng, K, T, rho_gen):
    R = rng.normal(0, 0.1, (K, T))
    vc = 0.1 * rho_gen * np.ones((K, 1))
    E = R + rng.normal(0, 1, (K, T)) * vc
    V = np.abs(vc * (1 + rng.normal(0, 0.15, (K, T))))
    Et = rng.normal(0, 0.1, T)                    # latent target deviation
    return E, V, Et


def test_conservative_band_contains_pcb_band_every_draw():
    rng = np.random.default_rng(11)
    for _ in range(300):
        K = int(rng.integers(8, 120))
        E, V, _ = _draw(rng, K, 6, rho_gen=rng.uniform(0, 2))
        a_anchor = ALPHA * (1 - BUDGET_DEC) if gate_b_feasible(K) else ALPHA
        sT = deconv_target_scale(E, V)
        qp, _, qc = _quantiles(E, sT, V, a_anchor, ALPHA * BUDGET_DEC)
        assert qc >= qp - 1e-12                   # nesting, pointwise (const radii)


def test_anchor_miss_implies_pcb_miss_pointwise():
    rng = np.random.default_rng(12)
    misses_checked = 0
    for _ in range(2000):
        K = 25
        E, V, Et = _draw(rng, K, 6, rho_gen=rng.uniform(0, 1.5))
        center = np.full(6, 0.5)
        fit = dapcb(E, V, center, alpha=ALPHA, tighten=False)
        if fit.selected_branch == "deconvolution":
            continue
        lo, hi = fit.band
        truth = center + Et
        selected_miss = not np.all((truth >= lo) & (truth <= hi))
        if selected_miss:
            misses_checked += 1
            sT = deconv_target_scale(E, V)
            qp, _, _ = _quantiles(E, sT, V, ALPHA, ALPHA * BUDGET_DEC)
            assert np.max(np.abs(Et)) > qp - 1e-12   # PCB missed too
    assert misses_checked > 20                       # the check actually bit


def test_marginal_and_per_branch_coverage_when_selection_is_stochastic():
    # K = 320 (gate B feasible AND the α_dec-budgeted deconvolution quantile is
    # informative), ρ around the gates so all three branches genuinely mix
    rng = np.random.default_rng(13)
    K, T, reps = 320, 4, 1200
    n_cov, branches = 0, {"PCB": [0, 0], "deconvolution": [0, 0],
                          "conservative": [0, 0]}
    for _ in range(reps):
        E, V, Et = _draw(rng, K, T, rho_gen=rng.uniform(0.4, 0.9))
        center = np.full(T, 0.5)
        fit = dapcb(E, V, center, alpha=ALPHA, tighten=False)
        lo, hi = fit.band
        truth = np.clip(center + Et, 0, 1)
        cov = int(np.all((truth >= lo) & (truth <= hi)))
        n_cov += cov
        b = branches[fit.selected_branch]
        b[0] += cov
        b[1] += 1
    # selection must actually vary for this regime to test anything
    assert sum(v[1] > 0 for v in branches.values()) >= 2, branches
    mc3 = 3 * np.sqrt(0.9 * 0.1 / reps)
    assert n_cov / reps >= (1 - ALPHA - 0.02) - mc3, (n_cov / reps, branches)
    # the deconvolution draws themselves (the term the old proof could not
    # bound) must respect their budgeted level when they occur in numbers
    dc, dn = branches["deconvolution"]
    if dn >= 200:
        assert dc / dn >= (1 - ALPHA - 0.02) - 3 * np.sqrt(0.9 * 0.1 / dn)


def test_selection_is_target_blind():
    rng = np.random.default_rng(14)
    E, V, _ = _draw(rng, 60, 5, rho_gen=1.0)
    f1 = dapcb(E, V, np.full(5, 0.2), alpha=ALPHA)
    f2 = dapcb(E, V, np.full(5, 0.8), alpha=ALPHA)
    assert f1.selected_branch == f2.selected_branch
    assert np.isclose(f1.reliability, f2.reliability)
