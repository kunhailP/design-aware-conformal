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
    assert len(t) == 34, len(t)   # e36 universe (>=2 usable rounds)
    assert int(t.any_da.sum()) == 28
    assert int(t.net_da.sum()) == 9
    assert int(t.persist_da.sum()) == 0
    assert int(t.persist_plugin.sum()) == 0, "plug-in must also certify zero"
    _present("Zero of the thirty-three countries")


def test_joint_contrast_totals():
    d = _csv("ess_joint_claims.csv")
    t = d[d.outcome == "trstprl"]
    assert int(t.n_spans.sum()) == 1173
    assert int(t.n_declining.sum()) == 193 and int(t.n_rising.sum()) == 212
    _present("$1{,}173$ ordered contrasts", "$193$ declining against $212$")
    assert "231 adjacent pairs" not in _norm(TEXT), "stale pre-joint pair count"


def test_no_false_under_detection_claim():
    """IL and IT DO have certified adjacent pairs under the joint band."""
    d = _csv("ess_joint_claims.csv")
    t = d[d.outcome == "trstprl"].set_index("cntry")
    assert bool(t.loc["IL", "any_pair"]) and bool(t.loc["IT", "any_pair"])
    for bad in ["no certified adjacent pair", "invisible to any single wave pair",
                "invisible to any pairwise reading"]:
        assert bad not in _norm(TEXT), f"claim falsified by the joint band: {bad}"


def test_no_unsupported_interior_optimum():
    """E52 refutes it with composition and unit size controlled."""
    d = _csv("controlled_unit_size.csv")
    g = d.groupby("target").halfwidth.median()
    fixed = g.loc[[t for t in (40, 60, 90, 125, 175, 250, 350) if t in g.index]]
    assert fixed.is_monotonic_decreasing, "coarsening should reduce the width"
    for bad in ["has an interior optimum", "an interior optimal unit",
                "sits far to the coarse side", "design parameter with an optimum"]:
        assert bad not in _norm(TEXT), f"unsupported claim survives: {bad}"
    _present("falls \\emph{monotonically} as units coarsen", "is infeasible")


# ------------------------------------------------- endpoint robustness (e43) --
def test_joint_band_net_set():
    """Every rung is read off one band (Proposition: claim-family transfer)."""
    d = _csv("ess_joint_claims.csv")
    t = d[d.outcome == "trstprl"]
    got = sorted(t.cntry[t.net])
    assert got == ["CY", "ES", "GB", "GR", "HU", "IL", "IT", "UA"], got
    assert int(t.persistent.sum()) == 0
    _present("certifies in eight countries")


def test_ukraine_magnitude_is_a_lower_bound():
    d = _csv("ess_joint_claims.csv")
    ua = d[(d.outcome == "trstprl") & (d.cntry == "UA")].iloc[0]
    assert 25.0 <= float(ua.net_lower) * 100 <= 26.0   # a lower bound rounds DOWN
    _present("at least $25$ points")


def test_erosion_share_is_not_ranked_across_countries():
    """The shared critical value grows with record length, so the share is a
    within-country quantity only; the manuscript must not rank on it."""
    d = _csv("ess_joint_claims.csv")
    t = d[d.outcome == "trstprl"]
    assert round(float(t.c.corr(t.n_rounds)), 2) >= 0.9
    es = t[t.cntry == "ES"].iloc[0]
    si = t[t.cntry == "SI"].iloc[0]
    assert (int(es.n_declining), int(es.n_spans)) == (32, 55)
    assert (int(si.n_declining), int(si.n_spans)) == (21, 55)
    _present("we do not rank on it", "increases strongly with record length")
    for bad in ["cyprus $0.62$", "eight democracies with no certified erosion"]:
        assert bad not in _norm(TEXT), f"cross-country ranking survives: {bad}"


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
def test_frontier_claims_are_withdrawn():
    """The ESS-region frontier was built on an inconsistent demeaning rule and
    is withdrawn; nothing in the manuscript may still assert it."""
    main = _norm(open(os.path.join(PAPER, "sections", "06_evidence.tex"),
                      encoding="utf-8").read())
    for bad in ["barrier belongs to the unit", "both barriers of proposition",
                "unit_frontier", "$13.9\\%$ narrower", "approaches} its cutoff"]:
        assert bad not in main, f"withdrawn frontier claim survives in S6: {bad}"
    _present("a withdrawn result")


def _retired_test_unit_frontier_gates():
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
    # the need gate only APPROACHES its cutoff: the manuscript must not claim
    # both barriers are crossed.
    assert round(float(w.rho_lcb.max()), 3) == 0.476
    _present("only \\emph{approaches} its cutoff", "not decisively crossed")
    for bad in ["both barriers of proposition", "are reachable}, two orders"]:
        assert bad not in _norm(TEXT), f"overstated frontier claim: {bad}"


def test_small_area_activation():
    """The one place the deployed selector activates on real survey data."""
    d = _csv("small_area_transport.csv")
    a = d[d.pool == "all countries"]
    fired = a[a.branch == "deconvolution"]
    assert len(fired) == 4, len(fired)
    assert set(fired.min_n) == {40, 60} and set(fired.essround) == {9, 10}
    assert int(fired.K.min()) == 228 and int(fired.K.max()) == 287
    # the band-vs-envelope claim uses the POINT width gain, which is the
    # certified LCB plus the frozen GAIN_MARGIN (0.05); width_ratio is the
    # deconvolved-target-scale ratio mean(sT)/mean(s), a different quantity
    # (the two were conflated in a pre-submission draft)
    point_gain = fired.gain_lcb + 0.05
    assert round(float(point_gain.min()), 3) == 0.205
    assert round(float(point_gain.max()), 3) == 0.266
    assert 0.155 <= float(fired.gain_lcb.min()) and float(fired.gain_lcb.max()) <= 0.22
    assert round(float(1 - fired.width_ratio.max()), 2) == 0.15
    assert round(float(1 - fired.width_ratio.min()), 2) == 0.17
    assert round(float(fired.coverage.min()), 3) == 0.881
    assert int(a.gate_A.sum()) == 8 and len(a) == 23
    _present("$21$--$27\\%$ narrower", "eight of twenty-three")
    _present("$15$--$17\\%$ below its plug-in",
             "width-gain lower bounds of $0.16$--$0.22$")
    # the common-level sensitivity must be reported, not buried
    c = d[d.pool == "common NUTS level"]
    assert (c.branch == "deconvolution").sum() == 0
    assert int(c.gate_A.sum()) == 9 and len(c) == 21
    assert int(c.K.max()) == 140
    _present("nine of twenty-one unit-rounds", "$K\\le140$")


def test_small_area_unit_is_exchangeable():
    """The clustering objection to E54, and the scope condition it leaves behind.

    The informative statistic is NOT the aggregate leave-one-country-out level
    (the held-out sets union to the whole pool, so that is partly self-
    fulfilling) but the LORO-minus-LOCO gap: deleting a region's country-mates
    from the calibration set is what within-country dependence would show up in.
    """
    S = _csv("small_area_exchangeability.csv")
    assert len(S) == 24 and set(S.scheme) == {"LOCO", "LORO"}
    lo = S[S.scheme == "LOCO"]
    assert len(lo) == 12
    assert round(float(lo.cov_pcb_anchor.min()), 3) == 0.893
    assert round(float(lo.cov_pcb_anchor.max()), 3) == 0.903
    p = S.pivot_table(index=["min_n", "essround"], columns="scheme",
                      values="cov_pcb_anchor")
    gap = (p["LORO"] - p["LOCO"]).abs().max()
    assert gap <= 0.0153, gap
    assert round(float(S.between_country_var_share.min()), 2) == 0.32
    assert round(float(S.between_country_var_share.max()), 2) == 0.49
    # the activating cells must not buy width with coverage
    act = S[S.branch == "deconvolution"]
    assert len(act) == 8 and float(act.cov_selected.min()) >= 0.93
    # E55 refits at K-1 (LORO) or K-|country| (LOCO), so the guaranteed level
    # sits a hair below E54's 0.881; the text rounds it to 0.88 for that reason
    assert 0.880 <= float(act.nominal.min()) and float(act.nominal.max()) <= 0.883

    C = _csv("small_area_loco_by_country.csv")
    assert round(float(C.cov_pcb_anchor.quantile(0.10)), 2) == 0.75
    assert float(C.cov_pcb_anchor.median()) == 1.0
    worst = C.groupby("cntry").cov_pcb_anchor.mean().nsmallest(3)
    assert set(worst.index) == {"BG", "GR", "HU"}, list(worst.index)
    assert round(float(worst.min()), 2) == 0.53
    assert round(float(worst.max()), 2) == 0.63

    _present("$32$--$49\\%$", "$0.89$--$0.90$", "at most $0.015$",
             "tenth percentile is $0.75$", "$0.53$--$0.63$")
    # the marginal/conditional distinction must be stated, not implied
    assert "marginal over regions" in _norm(TEXT)


def test_persistent_null_is_qualified_where_it_is_stated():
    """The abstract's most quotable sentence is its least supported one.

    "none certifies a persistent slide" is a statement about certification, not
    about Europe -- and it is read as the second unless the rung's severity
    travels with it. E42 puts 80% power at the persistent rung near a 0.08
    per-pair decline with realized size 0.001, so non-certification there is
    weak evidence of absence. Wherever the null is stated, the qualifier must be
    within reach of it.
    """
    d = _csv("real_severity.csv")
    p = d[d.design == "power"].set_index("delta")
    assert float(p.loc[0.00, "persist_rate"]) <= 0.01          # size, nominal 0.10
    assert float(p.loc[0.03, "persist_rate"]) < 0.10           # secular scale: no power
    assert float(p.loc[0.08, "persist_rate"]) >= 0.80          # crisis scale: powered
    assert float(p.loc[0.03, "net_rate"]) >= 0.70              # the net rung is the powered one

    flat = _norm(TEXT)
    assert "none certifies a persistent slide" in flat
    i = flat.index("none certifies a persistent slide")
    assert "crisis-scale" in flat[i:i + 160], (
        "the abstract states the persistent null without the severity qualifier")
    # and the body must say plainly what a non-certification is worth
    _present("weak evidence of absence")


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


def test_center_exactness_seam():
    """S1.3 rem:center + §4 scope note: the LOO-center seam, measured (e58).
    The paper claims (a) no cell below the exact-construction floor beyond
    2×MC-SE across 28 cells, (b) the grand-mean deficit reaches -0.064, and
    (c) split-fold is infinite-radius throughout K≤15 at alpha=0.10."""
    d = _csv("center_exactness.csv")
    assert len(d) == 28, len(d)
    gap = d.cov_loo - d.vovk_floor
    assert (gap >= -2 * d.mc_se).all(), gap.min()
    assert round(float((d.cov_grand - d.vovk_floor).min()), 3) == -0.064
    small = d[d.K <= 15]
    assert np.isinf(small.w_split).all(), "split-fold must be infinite at K<=15"
    assert (d[d.K >= 20].w_split_over_loo > 1).all()
    _present("below the exact-construction floor", "makes the conformal radius infinite")


def test_feasibility_frontier():
    """S1 Lemma (universal floor) + the frontier remark + Sec. 6 paragraph:
    three regimes, all occupied by real-data cells, and the frozen selector
    fired only in the feasible one. The 94 is the frozen intercept of the
    universal law sqrt(2/(K-1))."""
    d = _csv("feasibility_frontier.csv")
    assert (d.loc[d.activated, "regime"] == "feasible").all()
    w = d[d.dataset == "WVS full-coverage items"]
    assert (w.regime == "unnecessary").all() and float(w.rho_lcb.max()) <= 0.10
    ess = d[d.dataset == "ESS national-unit scan"]
    assert int(ess.K.max()) <= 33 and float(ess.rho_lcb.max()) <= 0.15
    sa = d[d.dataset.str.startswith("ESS small-area")]
    assert {"unnecessary", "unlearnable", "feasible"} <= set(sa.regime)
    tau = (0.02 - 0.0061) / 0.0943
    assert int(np.ceil(1 + 2 / tau ** 2)) == 94
    _present("its intercept, $\\sqrt{2/(K-1)}$ the law",
             "Unbiased-estimation reliability floor")


def test_cross_country_prevalence():
    """S4 prevalence paragraph + Sec. 7: d = 6 on both outcomes at 90%, the
    p<=alpha sets reproduce the joint-band net sets exactly, and the named
    six are subsets of the certified sets."""
    from pcb.inference.prevalence import (prevalence_lower_bound,
                                          true_discoveries,
                                          true_discoveries_subset)
    d = _csv("ess_prevalence.csv")
    j = _csv("ess_joint_claims.csv")
    for oc in ("trstprl", "stfdem"):
        g = d[d.outcome == oc]
        assert len(g) == 33, (oc, len(g))
        assert true_discoveries(g.p_net.values, 0.10) == 6, oc
        certified = set(j[(j.outcome == oc) & j.net].cntry)
        assert set(g.cntry[g.p_net <= 0.10]) == certified, oc
        named = set(g.nsmallest(6, "p_net").cntry)
        assert named <= certified, (oc, named - certified)
        # naming is licensed only by the CLOSURE-CORRECT subset bound: the
        # six smallest-p countries must re-certify at d(S)=6 within the full
        # 33-country closed testing (not as their own family)
        assert true_discoveries_subset(
            sorted(g.p_net)[:6], g.p_net.tolist(), 0.10) == 6, oc
        out = prevalence_lower_bound(dict(zip(g.cntry, g.p_net)), 0.10)
        assert out["d"] == 6 and out["named_covers_d"], oc
        assert set(out["countries_named"]) == named, oc
    _present("at least six", "closed testing across the thirty-three")


def test_wrong_unit_collapse_figure_one():
    """Fig. 1 / Sec. 5: the paper's opening exhibit. At L=8 threshold-level
    coverage is 3.5%, round-level 49.8%, and only the country-trajectory
    score holds nominal 90% at every length."""
    d = _csv("wrong_unit_coverage.csv").set_index(["L", "method"])
    assert round(float(d.loc[(8, "marginal"), "traj_cov_pct"]), 1) == 3.5
    assert round(float(d.loc[(8, "per_round"), "traj_cov_pct"]), 1) == 49.8
    assert round(float(d.loc[(2, "per_round"), "traj_cov_pct"]), 1) == 81.7
    traj = d.xs("trajectory", level="method")
    assert (traj.traj_cov_pct >= 90 - 2 * traj.cov_se * 1).all() or \
        (traj.traj_cov_pct >= 88.9).all()
    _present("$49.8\\%$", "$3.5\\%$")
