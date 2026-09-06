"""The public stratified-PSU bootstrap must be the construction the
experiments implement inline (paper: 'the stratified-PSU bootstrap').

Pins: (1) with one stratum it is `psu_bootstrap` exactly; (2) with several
strata it equals `e12_ess_decline._design_boot` draw for draw on the same
seed (same index order per stratum, strata in sorted order), for both the
m-of-m and the Rao-Wu-Yue rescaled variants; (3) single-PSU strata are held
fixed and contribute no variance.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pcb.inference.design_aware import psu_bootstrap, stratified_psu_bootstrap


def _psu_arrays(y, w, stratum, psu, T):
    ind = w[:, None] * (y[:, None] <= np.arange(T)[None, :])
    key = pd.MultiIndex.from_arrays([stratum, psu])
    g = pd.DataFrame(np.column_stack([ind, w]), index=key).groupby(level=[0, 1]).sum()
    return g.values[:, :T], g.values[:, T], g.index.get_level_values(0).to_numpy()


def test_single_stratum_reduces_to_psu_bootstrap():
    rng = np.random.default_rng(0)
    cnt = rng.uniform(0, 5, (12, 6)).cumsum(1); tot = cnt[:, -1] + rng.uniform(0, 2, 12)
    for rescale in (False, True):
        a = stratified_psu_bootstrap(cnt, tot, np.zeros(12), B=50,
                                     rng=np.random.default_rng(1), rescale=rescale)
        b = psu_bootstrap(cnt, tot, B=50, rng=np.random.default_rng(1), rescale=rescale)
        assert np.allclose(a, b)


def test_matches_the_experiments_inline_construction():
    try:
        from pcb.experiments import e12_ess_decline as e12
    except Exception as e:                                   # pragma: no cover
        pytest.skip(f"e12 not importable here: {e}")
    rng = np.random.default_rng(3)
    n, T = 600, 10
    y = rng.integers(0, T, n).astype(float)
    w = rng.uniform(0.5, 1.5, n)
    stratum = rng.integers(0, 5, n)
    psu = stratum * 100 + rng.integers(0, 8, n)
    cnt, tot, strat = _psu_arrays(y, w, stratum, psu, T)
    for rescale in (False, True):
        e12.RESCALE = rescale
        ref = e12._design_boot(y, w, stratum, psu, np.random.default_rng(7))
        got = stratified_psu_bootstrap(cnt, tot, strat, B=e12.B,
                                       rng=np.random.default_rng(7), rescale=rescale)
        assert got.shape == ref.shape
        assert np.allclose(got, ref), rescale
    e12.RESCALE = False


def test_singleton_strata_are_fixed():
    rng = np.random.default_rng(2)
    cnt = rng.uniform(0, 5, (3, 4)).cumsum(1); tot = cnt[:, -1] + 1
    strat = np.array([0, 1, 2])                              # every stratum has one PSU
    out = stratified_psu_bootstrap(cnt, tot, strat, B=20, rng=rng)
    assert np.allclose(out, out[0][None])                    # no variance at all
