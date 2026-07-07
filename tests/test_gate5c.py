"""Contract tests for the Gate-5C constructions (decline certification)."""
import numpy as np

from pcb.inference.decline_certify import (certify_decline,
                                           certify_decline_differences,
                                           truth_is_persistent_decline)


def test_level_band_fosd_is_exact_for_boxes():
    L, T = 3, 5
    # non-overlapping upward-moving CDFs → persistent decline certified
    lo = np.array([np.full(T, 0.1 * r + 0.2) for r in range(L)])
    hi = lo + 0.05
    c = certify_decline(lo, hi)
    assert c["persistent_decline"] and c["net_decline"]
    # overlap at one round → not certified
    hi2 = hi.copy(); hi2[0] += 0.2
    assert not certify_decline(lo, hi2)["persistent_decline"]


def test_truth_label_respects_core_mask():
    L, T = 2, 6
    theta = np.zeros((L, T))
    theta[1] = np.array([0, 0.3, 0.3, 0.3, -0.1, 0])  # up on core, down at t=4
    core = np.zeros(T, bool); core[1:4] = True
    assert truth_is_persistent_decline(theta, core)          # core-only: decline
    assert not truth_is_persistent_decline(theta)            # full range: not


def test_design_aware_certification_is_calibrated_under_no_change():
    """Under a true zero difference (no decline), design-aware false-cert ≤ α;
    plug-in over-certifies ~half the time (point estimate sign is a coin flip)."""
    rng = np.random.default_rng(0)
    B, L1, T, alpha = 400, 1, 2, 0.10
    da_hits = plug_hits = 0
    reps = 800
    for _ in range(reps):
        truth = np.zeros((L1, T))                            # no decline
        boot = truth + rng.normal(0, 0.02, size=(B, L1, T))  # design noise
        hat = truth + rng.normal(0, 0.02, size=(L1, T))
        c = certify_decline_differences(hat, boot, alpha)
        da_hits += c["design_aware"]
        plug_hits += c["plugin"]
    assert da_hits / reps <= alpha + 0.03                    # design-aware calibrated
    assert plug_hits / reps > 0.15                           # plug-in over-certifies
    assert plug_hits > 3 * da_hits                           # DA strictly tighter


def test_design_aware_certifies_a_clear_decline():
    rng = np.random.default_rng(1)
    B, L1, T = 400, 1, 4
    hat = np.full((L1, T), 0.15)                             # clear positive shift
    boot = hat + rng.normal(0, 0.02, size=(B, L1, T))
    assert certify_decline_differences(hat, boot, 0.10)["design_aware"]
