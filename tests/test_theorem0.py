"""Theorem 1 (non-identification/impossibility) — numerical contract test.

The theorem is stated at the CURVE level (Ẽ = E + S with S ⊥ E, supplement
§S1.1); this test instantiates its T=1 coordinate construction, which the
proof notes already suffices (the general-T statement follows by product
laws). Signed Gaussian draws are the proof's own example — no sup-score
additive structure is used anywhere:
(a) non-identification — two admissible pairs with the SAME observed law
    ℒ(E+S) but DIFFERENT latent (1−α) quantiles;
(b) impossibility — under S≡0 the latent target is exchangeable with the
    calibration scores, so any radius below the conformal order statistic
    undercovers (the conformal converse).
"""
import numpy as np

ALPHA = 0.10


def test_nonidentification_same_observed_different_latent():
    """(a) Same ℒ(R̃)=N(0,σ²); latent quantiles z σ vs z √(σ²−τ²) differ."""
    rng = np.random.default_rng(0)
    sigma2, tau2, n = 1.0, 0.36, 400_000
    # law P: all spread is transport, no survey noise
    Rp = rng.normal(0, np.sqrt(sigma2), n); Sp = np.zeros(n)
    # law P': some spread is survey noise
    Rq = rng.normal(0, np.sqrt(sigma2 - tau2), n); Sq = rng.normal(0, np.sqrt(tau2), n)
    obs_p, obs_q = Rp + Sp, Rq + Sq
    # observed score laws coincide (same variance ⇒ same N(0,σ²))
    assert abs(np.var(obs_p) - np.var(obs_q)) < 0.02
    assert abs(np.quantile(obs_p, 1 - ALPHA) - np.quantile(obs_q, 1 - ALPHA)) < 0.02
    # latent quantiles differ by exactly the deconvolution gap
    qp, qq = np.quantile(np.abs(Rp), 1 - ALPHA), np.quantile(np.abs(Rq), 1 - ALPHA)
    assert qp - qq > 0.15                      # latent band genuinely narrower under P'


def test_subplugin_undercovers_under_zero_noise():
    """(b) ξ≡0 ⇒ any radius below the conformal order stat undercovers."""
    rng = np.random.default_rng(1)
    K, reps, hits_plugin, hits_sub = 60, 4000, 0, 0
    for _ in range(reps):
        scores = np.abs(rng.normal(0, 1, K))           # observed = latent (ξ=0)
        target = abs(rng.normal(0, 1))
        m = int(np.ceil((1 - ALPHA) * (K + 1)))
        q_plugin = np.sort(scores)[m - 1]
        q_sub = np.sort(scores)[m - 6]                 # strictly below plug-in
        hits_plugin += target <= q_plugin
        hits_sub += target <= q_sub
    assert hits_plugin / reps >= 1 - ALPHA - 0.02      # plug-in valid
    assert hits_sub / reps < 1 - ALPHA - 0.01          # sub-plug-in undercovers
