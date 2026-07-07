"""Contract tests for the safe-adaptive selector helpers (Gate 5E)."""
import numpy as np

from pcb.inference.design_aware import deconv_reliability, rho_lcb


def test_rho_lcb_below_point_and_zero_at_no_noise():
    rng = np.random.default_rng(0)
    E = rng.normal(0, 0.1, (40, 4))
    assert rho_lcb(E, np.zeros((40, 4))) == 0.0          # no noise → LCB 0
    V = np.abs(rng.normal(0, 0.05, (40, 4)))
    point = np.sqrt((V**2).mean()) / np.abs(E).std()      # rough point ρ
    assert 0.0 <= rho_lcb(E, V) <= point + 0.1            # LCB ≤ point-ish


def test_reliability_grows_as_K_shrinks():
    """D (unreliability) should be larger at small K for the same noise level."""
    rng = np.random.default_rng(1)
    def D_at(K):
        vals = []
        for _ in range(40):
            E = rng.normal(0, 0.1, (K, 4)) + rng.normal(0, 0.07, (K, 4))
            V = np.abs(0.07 * (1 + rng.normal(0, 0.15, (K, 4))))
            vals.append(deconv_reliability(E, V))
        return np.mean(vals)
    assert D_at(30) > D_at(240)                           # smaller K → less reliable
