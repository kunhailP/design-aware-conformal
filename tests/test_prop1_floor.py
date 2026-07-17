"""Proposition 1(a): the reliability diagnostic's ALGORITHMIC floor.

D = max_t SE(ŝ_T²)/ŝ_T² ≥ √(2/(K−1)) holds identically — for every possible
dataset — because the frozen SE formula contains the 2·s_plug⁴/(K−1) term and
the finite-K-safe scale satisfies ŝ_T ≤ s_plug by construction. This is what
Theorem 5′ uses (gate B can never open below K = 1 + 2/τ_D², i.e. K ≥ 94 at
the frozen constants), so it gets a machine check across adversarial inputs.
"""
import numpy as np

from pcb.dapcb import DELTA_MAX, delta_ucb, gate_b_feasible
from pcb.inference.design_aware import deconv_reliability


def test_reliability_floor_is_algebraic_across_random_inputs():
    rng = np.random.default_rng(0)
    for trial in range(200):
        K = int(rng.integers(3, 400))
        T = int(rng.integers(2, 12))
        scale = 10.0 ** rng.uniform(-3, 2)
        E = rng.standard_t(df=2.5, size=(K, T)) * scale      # heavy-tailed, hostile
        V = np.abs(rng.standard_normal((K, T))) * scale * rng.uniform(0, 2)
        D = deconv_reliability(E, V)
        floor = np.sqrt(2.0 / (K - 1))
        assert D >= floor - 1e-12, (K, T, D, floor)


def test_gate_b_infeasible_below_94_and_feasible_at_survey_scale_never():
    # deterministic consequence: K < 94 ⇒ gate B cannot open, no matter the data
    for K in [4, 10, 25, 33, 40, 60, 80, 93]:
        assert not gate_b_feasible(K)
        assert delta_ucb(np.sqrt(2.0 / (K - 1))) > DELTA_MAX
    for K in [94, 120, 160, 320]:
        assert gate_b_feasible(K)


def test_floor_binds_for_zero_design_noise_too():
    # even with V ≡ 0 (ŝ_T = s_plug exactly) the 2/(K−1) term alone binds
    rng = np.random.default_rng(1)
    for K in [5, 30, 94, 320]:
        E = rng.normal(0, 1, (K, 6))
        D = deconv_reliability(E, np.zeros_like(E))
        assert D >= np.sqrt(2.0 / (K - 1)) - 1e-12
