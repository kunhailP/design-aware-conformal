"""Contract tests for the finite-K-safe deconvolution scale (deconv_target_scale).

Verifies the two properties preregistered in FINITE_K_CORRECTION_PROTOCOL.md:
(1) reduction — as design noise v→0 the safe scale → the plug-in modulation
    (band reduces to clustered PCB, protecting real low-ρ data);
(2) never wider than plug-in — ŝ_T,safe ≤ s_plug always (efficiency dial, never
    inflates beyond the honest plug-in).
"""
import numpy as np

from pcb.inference.conformal_band import _modulation
from pcb.inference.design_aware import deconv_target_scale


def test_reduces_to_plugin_at_zero_noise():
    rng = np.random.default_rng(0)
    E = rng.normal(0, 0.1, (40, 4))
    V = np.zeros((40, 4))                       # no design noise
    sT = deconv_target_scale(E, V)
    assert np.allclose(sT, _modulation(E), atol=1e-9)


def test_never_wider_than_plugin():
    rng = np.random.default_rng(1)
    for _ in range(20):
        E = rng.normal(0, 0.1, (30, 4))
        V = np.abs(rng.normal(0, 0.05, (30, 4)))
        sT = deconv_target_scale(E, V)
        assert np.all(sT <= _modulation(E) + 1e-12)


def test_wider_than_plain_deconvolution():
    """Safe scale ≥ plain deconvolved scale (guards the subtraction)."""
    rng = np.random.default_rng(2)
    E = rng.normal(0, 0.1, (30, 4)) + rng.normal(0, 0.08, (30, 4))
    V = np.abs(0.08 * (1 + rng.normal(0, 0.15, (30, 4))))
    s = _modulation(E)
    s_plain = np.sqrt(np.maximum(s**2 - (V**2).mean(0), (0.05 * s.max())**2))
    assert np.all(deconv_target_scale(E, V) >= s_plain - 1e-12)
