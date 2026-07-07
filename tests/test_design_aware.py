"""Contract tests for the E6 survey DGP and the DA-PCB variants."""
import numpy as np

from pcb.inference.conformal_band import population_conformal_band
from pcb.inference.design_aware import (da_studentized_band, da_worstcase_band,
                                        design_sd, psu_bootstrap)
from pcb.simulation.survey_dgp import (SurveyDesign, SurveySimConfig, T_GRID,
                                       draw_survey, generate_survey_hierarchy,
                                       true_curve)


def test_true_curve_no_clustering_is_logistic_cdf():
    th = true_curve(0.0, 0.0)
    from pcb.simulation.survey_dgp import TAU
    assert np.allclose(th, 1 / (1 + np.exp(-TAU)), atol=1e-10)
    assert np.all(np.diff(th) > 0) and th.shape == (T_GRID,)


def test_survey_estimate_is_approximately_unbiased():
    """Informative PSU selection must be corrected by the 1/π weights."""
    d = SurveyDesign(m_psu=30, b_per_psu=50, icc=0.10, gamma=1.0, eta=0.3)
    rng = np.random.default_rng(1)
    est = np.mean([draw_survey(0.3, d, rng)["theta_tilde"]
                   for _ in range(400)], axis=0)
    assert np.abs(est - true_curve(0.3, d.sigma_u)).max() < 0.01


def test_bootstrap_sd_tracks_replication_sd():
    d = SurveyDesign(m_psu=25, b_per_psu=40, icc=0.10, gamma=0.5, eta=0.3)
    rng = np.random.default_rng(2)
    reps = [draw_survey(0.0, d, rng) for _ in range(300)]
    true_sd = np.array([r["theta_tilde"] for r in reps]).std(axis=0)
    boot_sd = np.mean([design_sd(r["psu_cnt"], r["psu_tot"], 200,
                                 np.random.default_rng(i))
                       for i, r in enumerate(reps[:50])], axis=0)
    assert np.abs(boot_sd - true_sd).max() < 0.4 * true_sd.max()


def test_da_studentized_reduces_to_pcb_when_designs_are_noiseless():
    rng = np.random.default_rng(3)
    E = rng.normal(0, 0.05, size=(40, T_GRID))
    center = np.linspace(0.1, 0.9, T_GRID)
    lo0, hi0 = population_conformal_band(E, center, 0.1)
    lo1, hi1 = da_studentized_band(E, np.zeros_like(E), center, None, 0.1)
    assert np.allclose(lo0, lo1) and np.allclose(hi0, hi1)


def test_da_worstcase_is_never_narrower_than_plugin():
    rng = np.random.default_rng(4)
    h = generate_survey_hierarchy(SurveySimConfig(K=30, seed=4), rng)
    tilde = np.array([s["theta_tilde"] for s in h["surveys"]])
    E = h["theta_hat"][:-1] - tilde[:-1]
    boots = [psu_bootstrap(s["psu_cnt"], s["psu_tot"], 100, rng)
             for s in h["surveys"][:-1]]
    lo_d = np.array([np.quantile(b, 0.05, axis=0) for b in boots])
    hi_d = np.array([np.quantile(b, 0.95, axis=0) for b in boots])
    c = h["theta_hat"][-1]
    lo_p, hi_p = population_conformal_band(E, c, 0.1, tighten=False)
    lo_w, hi_w = da_worstcase_band(E, h["theta_hat"][:-1], lo_d, hi_d, c, 0.1,
                                   tighten=False)
    assert np.all(hi_w - lo_w >= hi_p - lo_p - 1e-12)
