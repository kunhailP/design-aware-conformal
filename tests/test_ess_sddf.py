"""Contract tests for the SDDF ingest/merge layer (pcb.data.ess_sddf).

Synthetic fixtures only — no licensed data. The contract: SDDF rows fill
psu/stratum exactly where the integrated subset is missing them, shipped
design variables are bit-unchanged, and the unchanged audit rule then
upgrades exactly the covered country-rounds to "core".
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest

from pcb.data.audit_ess import COLS, audit
from pcb.data.ess_sddf import load_sddf, merge_design


def _integrated(n=400, seed=0):
    """Two country-rounds: (AT, 1) design-missing, (AT, 9) design-shipped."""
    rng = np.random.default_rng(seed)
    rows = []
    for rnd, has_design in ((1, False), (9, True)):
        for i in range(n):
            rows.append(dict(
                essround=rnd, cntry="AT", idno=float(i),
                trstprl=float(rng.integers(0, 11)),
                trstplt=5.0, trstprt=5.0, stfdem=float(rng.integers(0, 11)),
                ppltrst=5.0, dweight=1.0, pspwght=1.0, pweight=1.0,
                anweight=1.0,
                psu=float(i % 25) if has_design else np.nan,
                stratum=float(i % 5) if has_design else np.nan,
                prob=0.001 if has_design else np.nan))
    return pd.DataFrame(rows)[COLS + ["idno"]]


@pytest.fixture()
def sddf_dir(tmp_path):
    n = 400
    # integrated-style file (cntry + essround columns present)
    pd.DataFrame(dict(
        cntry=["AT"] * n, essround=[1] * n, idno=np.arange(n, dtype=float),
        psu=(np.arange(n) % 25).astype(float),
        stratify=(np.arange(n) % 5).astype(float),
        prob=np.full(n, 0.001))).to_csv(tmp_path / "ESS1SDDF.csv", index=False)
    # per-country style file: cntry/round only in the filename, no stratify
    pd.DataFrame(dict(
        idno=np.arange(n, dtype=float),
        psu=(np.arange(n) % 25).astype(float))).to_csv(
            tmp_path / "ESS2_BE_SDDF.csv", index=False)
    return tmp_path


def test_ingest_harmonizes_both_vintages(sddf_dir):
    s = load_sddf(str(sddf_dir), cache=None, verbose=False)
    assert set(s.columns) == {"cntry", "essround", "idno", "psu", "stratum",
                              "prob"}
    assert sorted(s.cntry.unique()) == ["AT", "BE"]
    assert sorted(s.essround.astype(int).unique()) == [1, 2]
    # missing stratify -> constant stratum, not a dropped file
    assert (s[s.cntry == "BE"].stratum == 1.0).all()


def test_merge_fills_only_missing_and_upgrades_audit(sddf_dir):
    df = _integrated()
    s = load_sddf(str(sddf_dir), cache=None, verbose=False)
    merged = merge_design(df, s, verbose=False)
    # round 1 filled from SDDF
    r1 = merged[merged.essround == 1]
    assert r1.psu.notna().all() and r1.stratum.notna().all()
    # round 9 (shipped design) bit-unchanged
    r9o = df[df.essround == 9].reset_index(drop=True)
    r9m = merged[merged.essround == 9].reset_index(drop=True)
    pd.testing.assert_series_equal(r9o.psu, r9m.psu)
    pd.testing.assert_series_equal(r9o.stratum, r9m.stratum)
    # audit now classifies both country-rounds core
    a = audit(merged).set_index(["cntry", "essround"])["sample"]
    assert a.loc[("AT", 1)] == "core" and a.loc[("AT", 9)] == "core"
    # without the merge, round 1 is extended (the shipped state)
    a0 = audit(df).set_index(["cntry", "essround"])["sample"]
    assert a0.loc[("AT", 1)] == "extended"


def test_uncovered_rows_stay_missing(sddf_dir):
    df = _integrated()
    df.loc[df.index[:0], :]  # no-op guard
    # a country the SDDF does not cover keeps NaN design vars
    other = df[df.essround == 1].copy()
    other["cntry"] = "FR"
    both = pd.concat([df, other], ignore_index=True)
    s = load_sddf(str(sddf_dir), cache=None, verbose=False)
    merged = merge_design(both, s, verbose=False)
    fr = merged[(merged.cntry == "FR") & (merged.essround == 1)]
    assert fr.psu.isna().all()


# ---------------------------------------------------------------- e61 ledger --
def test_sddf_long_window_settlement():
    """Pins the committed e61 outputs: the SDDF upgrade changes no net or
    persistent count, with identical net membership (paper, Supplementary
    Material 'the direct settlement')."""
    import os
    new = "results/ess_joint_claims_sddf.csv"
    old = "results/ess_joint_claims.csv"
    assert os.path.exists(new) and os.path.exists(old)
    n, o = pd.read_csv(new), pd.read_csv(old)
    for outcome in ("trstprl", "stfdem"):
        nn = n[n.outcome == outcome]
        oo = o[o.outcome == outcome]
        assert sorted(nn.cntry[nn.net]) == sorted(oo.cntry[oo.net])
        assert int(nn.persistent.sum()) == 0 == int(oo.persistent.sum())
        assert int(nn.episodic.sum()) == int(oo.episodic.sum()) == 23
    assert sorted(n[(n.outcome == "trstprl") & n.net].cntry) == [
        "CY", "ES", "GB", "GR", "HU", "IL", "IT", "UA"]

    lw = pd.read_csv("results/ess_long_window_sddf.csv")
    for outcome, k_net, k_bonf in (("trstprl", 9, 8), ("stfdem", 8, 7)):
        p = lw[lw.outcome == outcome]
        assert int(p.net_da.sum()) == k_net
        assert int(p.net_da_bonf.sum()) == k_bonf
        assert int(p.persist_da.sum()) == 0
