"""Contract tests for the claim-family transfer construction.

The theorem being pinned: a single simultaneous band over a country's contrast
family certifies every derivable ordering claim on ONE coverage event, so the
joint statement costs one alpha in total regardless of how many claims are read
off it -- no Bonferroni across sub-spans, no separate budget for the reverse
direction, and no endpoint-selection cost, because every endpoint choice is
certified at the same time.

Three checks:
  1. joint validity -- the probability that ANY certified claim is false is at
     most alpha, over a null-imposed simulation with a known truth;
  2. the transfer property itself -- certification is monotone under set
     inclusion, so a claim implied by a certified claim is certified;
  3. two-sidedness -- declines and rises cannot both be certified for the same
     span, and the shared critical value dominates the one-sided one.
"""
from __future__ import annotations

import numpy as np

from pcb.inference.claim_family import certify_claim_family

ALPHA = 0.10
L, T, B = 5, 6, 600
CORE = np.array([False, True, True, True, True, False])


def _draw(rng, truth, sd):
    """Curves + bootstrap under a known truth, with correlated design noise."""
    err = rng.normal(0, sd, size=(L, T))
    curves = truth + err
    # bootstrap replicates around the observed curves, same noise scale
    boots = curves[None] + rng.normal(0, sd, size=(B, L, T))
    return curves, boots


def test_joint_validity_under_the_sharp_null():
    """No true ordering exists, so ANY certified claim is a false certification.
    The joint error rate over the whole family must respect alpha."""
    rng = np.random.default_rng(7)
    reps, bad = 400, 0
    flat = np.tile(np.linspace(0.1, 0.9, T), (L, 1))     # identical every round
    for _ in range(reps):
        curves, boots = _draw(rng, flat, 0.02)
        r = certify_claim_family(curves, boots, ALPHA, CORE)
        if r["declines"] or r["rises"]:
            bad += 1
    rate = bad / reps
    assert rate <= ALPHA + 3 * np.sqrt(ALPHA * (1 - ALPHA) / reps), rate


def test_transfer_is_monotone_under_implication():
    """A claim implied by the band is certified: if every adjacent pair
    certifies a decline, the span from first to last must certify too (the
    implied ordering is inside the same band)."""
    rng = np.random.default_rng(11)
    truth = np.stack([np.linspace(0.05, 0.55, T) + 0.10 * i for i in range(L)])
    hits = 0
    for _ in range(200):
        curves, boots = _draw(rng, truth, 0.006)
        r = certify_claim_family(curves, boots, ALPHA, CORE)
        adjacent = [(i, i + 1) for i in range(L - 1)]
        if all(p in r["declines"] for p in adjacent):
            hits += 1
            assert r["net"], "persistent certified but net was not"
    assert hits > 0, "the fixture never certified persistence; test is vacuous"


def test_directions_are_exclusive_and_share_one_budget():
    rng = np.random.default_rng(3)
    truth = np.stack([np.linspace(0.1, 0.9, T) + 0.04 * i for i in range(L)])
    curves, boots = _draw(rng, truth, 0.01)
    two = certify_claim_family(curves, boots, ALPHA, CORE, two_sided=True)
    one = certify_claim_family(curves, boots, ALPHA, CORE, two_sided=False)
    assert not (two["declines"] & two["rises"]), "a span certified both ways"
    # the two-sided band pays for covering both directions
    assert two["c"] >= one["c"] - 1e-12
    assert two["declines"] <= one["declines"]


def test_every_rung_comes_from_the_same_critical_value():
    """The rungs are read off one band: there is a single c, and each rung is a
    set-inclusion statement about it."""
    rng = np.random.default_rng(5)
    truth = np.stack([np.linspace(0.1, 0.9, T) + 0.03 * i for i in range(L)])
    curves, boots = _draw(rng, truth, 0.012)
    r = certify_claim_family(curves, boots, ALPHA, CORE)
    assert np.isfinite(r["c"])
    assert r["n_spans"] == L * (L - 1) // 2
    assert (r["net"] is True) == ((0, L - 1) in r["declines"])
    assert r["any_pair"] == any((i, i + 1) in r["declines"] for i in range(L - 1))
    assert 0.0 <= r["frac_spans_declining"] <= 1.0
