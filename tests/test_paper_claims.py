"""Claim ledger: every headline number in the manuscript, checked against the
committed result tables.

Three rounds of referee reports on this paper found the same failure mode more
than once -- a number or a scope word in the text drifting away from what the
experiment actually produced (a caption claiming entries were unchanged when
only the country list was; an abstract clause contradicted by the paper's own
certified-core table). Prose review does not catch that reliably. This test
does: each entry below pins a claim in `paper/` to the artifact that licenses
it, and fails if either moves.

It is deliberately mechanical. If a claim cannot be expressed as a check
against a CSV, it does not belong in the ledger -- and a claim that is in the
paper but not in the ledger is a claim no one is checking, which is the state
this test exists to prevent.

Run: python -m pytest tests/test_paper_claims.py -q
"""
from __future__ import annotations

import os
import re

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
RESULTS = os.path.join(ROOT, "results")


def _tex() -> str:
    """Main text plus supplement, concatenated."""
    parts = []
    for p in ["main.tex", "supplement.tex"]:
        f = os.path.join(PAPER, p)
        if os.path.exists(f):
            parts.append(open(f, encoding="utf-8").read())
    sec = os.path.join(PAPER, "sections")
    if os.path.isdir(sec):
        for f in sorted(os.listdir(sec)):
            if f.endswith(".tex"):
                parts.append(open(os.path.join(sec, f), encoding="utf-8").read())
    return "\n".join(parts)


def _csv(name):
    p = os.path.join(RESULTS, name)
    if not os.path.exists(p):
        pytest.skip(f"{name} not present")
    return pd.read_csv(p)


TEXT = None


def setup_module(_):
    global TEXT
    TEXT = _tex()


def _norm(t):
    """Collapse whitespace so line breaks in the source do not defeat matching."""
    return re.sub(r"\s+", " ", t).lower()


def _present(*fragments):
    """Every fragment must appear in the manuscript, modulo line breaks."""
    flat = _norm(TEXT)
    missing = [f for f in fragments if _norm(f) not in flat]
    assert not missing, f"claim text missing from the manuscript: {missing}"


# ---------------------------------------------------------------- ESS, 9-11 --
def test_ess_short_window_counts():
    d = _csv("ess_country_certification.csv")
    t = d[d.outcome == "trstprl"]
    assert int(t.any_plugin.sum()) == 20
    assert int(t.any_da.sum()) == 12
    assert int(t.net_da.sum()) == 6
    assert int(t.persist_da.sum()) == 1
    assert sorted(t.cntry[t.persist_da]) == ["GR"]
    _present("flags $20$ of $30$ countries", "net first-to-last decline holds in $6$")


def test_ess_net_six_membership():
    d = _csv("ess_country_certification.csv")
    got = sorted(d[(d.outcome == "trstprl") & d.net_da].cntry)
    assert got == ["AT", "BE", "EE", "GB", "GR", "NL"], got
    for name in ["Austria", "Belgium", "Estonia", "the United Kingdom", "Greece",
                 "the Netherlands"]:
        assert name.lower() in _norm(TEXT)


# ------------------------------------------------------------- long window --
def test_long_window_counts():
    d = _csv("ess_long_window.csv")
    t = d[d.outcome == "trstprl"]
    assert len(t) == 34, len(t)
    assert int(t.any_da.sum()) == 28
    assert int(t.net_da.sum()) == 9
    assert int(t.persist_da.sum()) == 0
    assert int(t.persist_plugin.sum()) == 0, "plug-in must also certify zero"
    _present("\\emph{Zero} of thirty-four countries")


def test_long_window_pairs_and_weightsonly():
    d = _csv("ess_long_window.csv")
    t = d[d.outcome == "trstprl"]
    assert int(t.n_pairs.sum()) == 231
    assert int(t.n_pairs_weightsonly.sum()) == 174
    _present("$231$ adjacent pairs")


def test_israel_italy_have_no_certified_pair():
    """The under-detection showcase: span certified with no certified pair."""
    d = _csv("ess_long_window.csv")
    t = d[d.outcome == "trstprl"].set_index("cntry")
    for c in ("IL", "IT"):
        assert bool(t.loc[c, "net_da"]) and int(t.loc[c, "pair_da"]) == 0, c
    _present("no certified adjacent pair")


# ------------------------------------------------- endpoint robustness (e43) --
def test_joint_band_net_set():
    """Every rung is read off one band (Proposition: claim-family transfer)."""
    d = _csv("ess_joint_claims.csv")
    t = d[d.outcome == "trstprl"]
    got = sorted(t.cntry[t.net])
    assert got == ["CY", "ES", "GB", "GR", "HU", "IL", "IT", "UA"], got
    assert int(t.persistent.sum()) == 0
    _present("certifies in \\emph{eight} countries")


def test_ukraine_magnitude_is_a_lower_bound():
    d = _csv("ess_joint_claims.csv")
    ua = d[(d.outcome == "trstprl") & (d.cntry == "UA")].iloc[0]
    assert 25.5 <= float(ua.net_lower) * 100 <= 26.5
    _present("at least} $26$ points")


def test_joint_band_erosion_index():
    d = _csv("ess_joint_claims.csv")
    t = d[d.outcome == "trstprl"].set_index("cntry")
    for iso, quoted in [("CY", "0.62"), ("ES", "0.58"), ("GR", "0.53"),
                        ("UA", "0.47"), ("SI", "0.38"), ("IL", "0.36")]:
        assert f"{float(t.loc[iso, 'frac_declining']):.2f}" == quoted, iso
        assert f"${quoted}$" in _norm(TEXT), (iso, quoted)
    zero = sorted(t[t.n_declining == 0].index)
    assert zero == ["BG", "CH", "CZ", "LT", "LV", "ME", "NO", "RS"], zero
    for name in ["Bulgaria", "Switzerland", "Czechia", "Lithuania", "Latvia",
                 "Montenegro", "Norway", "Serbia"]:
        assert name.lower() in _norm(TEXT)


def test_joint_band_episodic_needs_no_correction():
    d = _csv("ess_joint_claims.csv")
    for oc in ("trstprl", "stfdem"):
        assert int(d[d.outcome == oc].episodic.sum()) == 23, oc
    _present("twenty-three of thirty-three")
    assert "eighteen of thirty-four" not in _norm(TEXT), (
        "the Bonferroni patch is superseded by the joint band")


# --------------------------------------------------------------- WVS rungs --
def test_wvs_rung_gap_decomposition():
    """The headline ratio must be reported as the mixed quantity it is, with the
    rung-only decomposition beside it."""
    d = _csv("wvs_deconsolidation.csv")
    mixed = (d.anypair_plugin / d.persist)
    plug = (d.anypair_plugin / d.persist_plugin)
    da = (d.anypair / d.persist)
    assert (round(mixed.min(), 1), round(mixed.max(), 1)) == (2.6, 6.5)
    assert (round(plug.min(), 1), round(plug.max(), 1)) == (1.7, 4.8)
    assert (round(da.min(), 1), round(da.max(), 1)) == (1.9, 4.8)
    _present("$1.7$--$4.8\\times$", "$1.9$--$4.8\\times$")


def test_certified_core_size_and_west():
    d = _csv("certified_core.csv")
    assert int(d.core.sum()) == 13
    assert int((d.n_items >= 1).sum()) == 38
    west = d[d.group == "Consolidated West"]
    # Finland and Switzerland ARE core members: the manuscript must not claim
    # that no consolidated Western democracy certifies at all.
    assert sorted(west[west.core].country) == ["Finland", "Switzerland"]
    assert "nothing certifies" not in _norm(TEXT), (
        "the abstract once claimed no consolidated democracy certifies; "
        "Finland and Switzerland do (two items each)")
    _present("no consolidated Western democracy certifies on support for a "
             "democratic system")


# ----------------------------------------------------------- unreachability --
def test_reliability_floor_arithmetic():
    from pcb.dapcb import gate_b_feasible
    assert not gate_b_feasible(93) and gate_b_feasible(94)
    _present("$K\\ge94$")


def test_wvs_gate_probe():
    d = _csv("wvs_gate_probe.csv")
    assert d.K.min() >= 95 and d.K.max() <= 105
    assert round(float(d.rho_lcb.max()), 2) <= 0.10


# -------------------------------------------------------- severity (E32/E42) --
def test_real_severity_is_monte_carlo_not_mde():
    """The power design must carry sampling noise in the point estimate: a
    structural 0.000 at delta=0 is an arithmetic identity, not a size."""
    d = _csv("real_severity.csv")
    p = d[d.design == "power"]
    size = float(p[p.delta == 0].persist_rate.iloc[0])
    assert 0 < size <= 0.02, (
        f"realized size {size}: exactly 0.000 means the estimate was fixed at "
        "the truth, which is a minimum-detectable-effect curve, not power")


def test_severity_ordering():
    d = _csv("real_severity.csv")
    p = d[d.design == "power"].sort_values("delta")
    net80 = p[p.net_rate >= 0.8].delta.min()
    per80 = p[p.persist_rate >= 0.8].delta.min()
    assert net80 < per80, "the net rung must be the more powered instrument"


# ------------------------------------------------------- deff sensitivities --
def test_long_window_deff_membership_stable():
    d = _csv("ess_long_window_deff.csv")
    t = d[d.outcome == "trstprl"]
    sets = {deff: set(g[g.net_da].cntry) for deff, g in t.groupby("deff")}
    base = sets[1.0]
    for deff, s in sets.items():
        assert s == base, (deff, sorted(base ^ s))
    assert len(base) == 9


def test_wvs_deff_core_stability():
    d = _csv("wvs_deff_country_flags.csv")
    for deff, g in d.groupby("deff"):
        per = g.groupby("iso")["persist"].sum()
        n_core = int((per >= 2).sum())
        assert n_core in (12, 13), (deff, n_core)


# ------------------------------------------------------ LORO exchangeability --
def test_loro_east_undercoverage():
    d = _csv("loro_exchangeability.csv")
    east = d[d.region == "East"].set_index("outcome")
    assert int(east.loc["trstprl", "covered"]) == 6
    assert int(east.loc["stfdem", "covered"]) == 5
    assert int(east.loc["trstprl", "n_test"]) == 9
    _present("$6/9$", "$5/9$")


# ------------------------------------------------------------- mode / design --
def test_singleton_strata_count():
    d = _csv("ess_singleton_strata.csv")
    assert int(d.strata_singleton.iloc[0]) == 1
    assert int(d.strata_total.iloc[0]) == 7028
    _present("$1$ of $7{,}028$")


def test_mode_table_self_completion_set():
    d = _csv("ess_mode_table.csv")
    sc = sorted(d[(d.essround == 10) &
                  (d["mode"] == "self-completion")].cntry.unique())
    assert sc == ["AT", "CY", "DE", "ES", "IL", "LV", "PL", "RS", "SE"], sc


def test_claassen_window_matched_core_turnover():
    m = _csv("claassen_window_matched.csv")
    core17 = set(m[m.in_core].iso3.dropna())
    full = {"ALB", "AZE", "BIH", "CHE", "ECU", "FIN", "GHA", "IRQ", "LBN",
            "RWA", "TTO", "TUN", "UZB"}
    assert len(full - core17) == 5 and {"TUN", "IRQ", "LBN"} <= (full - core17)
    _present("drops all three Arab-Spring cases")


# ------------------------------------------------- unit frontier (E49) -------
def test_unit_frontier_gates():
    d = _csv("unit_frontier.csv")
    w = d[d.estimand.str.startswith("within")]
    # K and rho move as claimed as the unit refines
    assert (int(w[w.min_n == 400].K.min()), int(w[w.min_n == 400].K.max())) == (21, 30)
    assert (int(w[w.min_n == 25].K.min()), int(w[w.min_n == 25].K.max())) == (300, 315)
    assert round(float(w[w.min_n == 400].rho_lcb.min()), 2) == 0.08
    assert round(float(w[w.min_n == 25].rho_lcb.max()), 2) == 0.47
    # reliability gate: all rounds by min_n = 80, not before
    assert w[w.min_n == 80].gate_B_reliability.all()
    assert not w[w.min_n == 150].gate_B_reliability.any()
    # need gate: opens in exactly one round, at 30 and 25
    opened = w[w.gate_A_need]
    assert set(opened.min_n) == {25, 30}, sorted(set(opened.min_n))
    assert len(opened) == 2, len(opened)
    # and the selector still abstains
    assert not (w.branch == "deconvolution").any(), (
        "if the selector now activates, the manuscript must say so")
    both = w[w.gate_A_need & w.gate_B_reliability]
    assert round(float(both.raw_width_gain.max()), 3) == 0.139
    _present("$13.9\\%$ narrower", "in one of the three rounds")


# ------------------------------------------------------------ no stale text --
def test_no_stale_pre_joint_counts():
    """The joint construction changed the span count; nothing may still say nine."""
    flat = _norm(TEXT)
    for bad in ["net erosion in nine", "certifies in nine",
                "only three of the nine", "three of them robust to dropping"]:
        assert bad not in flat, f"stale pre-joint-band claim: {bad}"


def test_no_unverified_robustness_superlatives():
    """Guard against the caption failure mode: a blanket 'all entries unchanged'
    claim about a table whose magnitude columns were never recomputed."""
    banned = ["All entries are unchanged at a design effect",
              "All entries unchanged at a design effect"]
    for b in banned:
        assert b not in _norm(TEXT), (
            f"'{b}' overstates E44, which recomputes counts only; magnitudes "
            "shrink under deff inflation")
