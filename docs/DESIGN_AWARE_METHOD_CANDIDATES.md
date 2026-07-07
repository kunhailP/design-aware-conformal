# Design-Aware Clustered Conformal — method candidates (Gate 5B)

Status: Gate 5B, 2026-07-06. Builds on `DESIGN_AWARE_FORMAL_SETUP.md`
(two-stage hierarchy; the contamination identity Ẽ = E − S; the union-bound
bar in §6; the v→0 reduction check in §7). Three candidates, evaluated against
those criteria. Verdict lives in `GO_NO_GO_GATE5B.md`; proofs in
`DESIGN_AWARE_PROOF_SKETCHES.md`. No implementation this gate.

Common notation: source countries c = 1..K, target K+1; per-round modulation
s_r(t) built OOF from calibration curves only; latent (clean) sup-score
R_c = max_{r∈R_c, t} |E_{c,r}(t)| / s_r(t); observable (contaminated) score
R̃_c = max_{r,t} |Ẽ_{c,r}(t)| / s_r(t) with Ẽ = θ̂ − θ̃ = E − S; design SD
v_{c,r}(t) from a stratified PSU / replicate-weight bootstrap.

---

## Candidate A — worst-case survey-confidence-set score (BASELINE ONLY)

**Algorithm.** Per country-round form a design confidence set
C_{c,r}(t) = [θ̃ ± z_β v_{c,r}(t)] (P(θ_{c,r}∈C) ≥ 1−β). Score
R_c^rob = max_{r,t} sup_{F∈C_{c,r}} |θ̂_{c,r}(t) − F(t)| / s_r(t)
= max_{r,t} ( |Ẽ_{c,r}(t)| + z_β v_{c,r}(t) ) / s_r(t). Calibrate the clustered
quantile on {R_c^rob}; band = θ̂_{K+1} ± q·s.

**Guarantee.** Coverage ≥ 1 − α − Kβ (union over the K source design-set
failure events; proof sketch A). **This is exactly the §6 union bound**: β must
shrink like α/K, the z_β term blows up, the band inflates without bound as K
grows.

**Reduction (v→0).** ✓ C collapses to {θ̃}={θ}, R^rob=R̃=R, reduces to
clustered PCB.

**Role.** Conservative UPPER ENVELOPE and sanity baseline — reports the price of
refusing to model the noise. **Not** the paper's method: fails the union-bound
bar. Keep it to show the reader what the naive combination costs, then beat it.

---

## Candidate B — contamination-model conformal (deconvolution + dominance) — PRIMARY

The escape from the union bound (setup §6): survey error is additive noise on
the score DISTRIBUTION (R̃ vs R), not K confidence events. Two coupled pieces.

**B1 — validity via stochastic dominance (the safe half).**
Deployment target has no survey error, so its score is the CLEAN R_{K+1}. The
calibration scores are the CONTAMINATED R̃_c. Because S_c ⟂ E_c is (approx.)
mean-zero, each coordinate satisfies E_S|E − S| ≥ |E| (Jensen), so the
contaminated sup-score is stochastically ≥ the clean one under the dominance
condition (D) of proof sketch B1. Then the conformal quantile from {R̃_c} is
≥ the clean quantile, and the plug-in clustered band is **conservative** for the
latent deployment trajectory: coverage ≥ 1 − α, NO Kβ term. (E6 confirmed:
94–100% on deployment.) Validity is thus free; the problem is width.

**B2 — efficiency via deconvolution (the performance half).**
Recover the oracle (clean) scale. With total plug-in scale s_plug(t)² and known
survey variance v²(t), estimate the transport-only scale
s_T(t)² = max( s_plug(t)² − mean_c v_{c}(t)², floor ), studentize calibration
scores by √(s_T² + v_c²) (each country by its own noise), and score the
deployment target by s_T alone (no survey term). Band width shrinks by the
factor √(s_T² )/√(s_plug²) = √(1 − (v/s_plug)²) toward the oracle. This is the
E6 `da_studentized` construction.

**The two pieces are a single guarded estimator.** Deconvolution is
approximately exact only while the noise ratio ρ = v/s_transport is small; at
ρ ≳ 1 the subtraction s_plug² − v² is unstable and over-corrects (E6 cells D/E:
81–83% undercoverage). So: **use B2 when ρ below a threshold; fall back to the
B1 dominance band (valid, conservative) when ρ is large.** The guard makes the
estimator valid everywhere and efficient where it can be — an honest,
non-trivial, non-union-bound statement.

**Guarantee (target theorem).** (i) B1 dominance ⇒ coverage ≥ 1−α for the latent
deployment trajectory under condition (D), for ALL ρ (via the fallback). (ii)
B2 ⇒ width_DA / width_plugin → √(1−ρ⁻²_eff) in the low-ρ regime, reducing to
the oracle as v→0. (iii) validation view: add v_{K+1} back on the target side
(restores nominal in both views, E6).

**Reduction (v→0).** ✓ s_T = s_plug, no fallback, = clustered PCB.

**Novelty vs prior.** The contamination framing is the noisy-labels setting
(Feldman 2022 dominance; Uncertain Imputation 2505.04733) but: (a) labels are
finite-population CDFs not scalars, (b) noise is KNOWN heteroskedastic design
variance not adversarial corruption, (c) the unit is the country not the
individual, (d) the target is a multi-index trajectory, (e) we DECONVOLVE for
efficiency rather than only inflating for safety. No prior theorem takes
known-heteroskedastic-variance calibration points into a sup-score cluster band.

**Open risk.** Condition (D) (contaminated sup-score stochastically dominates
clean) is proved coordinatewise in expectation (Jensen) but the SUP is
nonlinear; the full stochastic-dominance step is the one that may need an extra
assumption (e.g. Gaussian design noise) or drop to "conservative in
expectation". This is the single proof to nail — see sketch B1.

---

## Candidate C — two-stage design-valid p-value (CLEAN THEORY, APPENDIX)

**Algorithm.** Inner: from the survey design of country c, build a super-uniform
statistic U_c (a design-valid p-value that the latent trajectory error exceeds
its studentized sup) using the replicate-weight / bootstrap distribution. Outer:
combine {U_c} across countries by a conformal rank (the U_c are the
nonconformity scores). Band = the θ̂ ± threshold implied by the calibrated rank.

**Guarantee (aspirational).** If each U_c is EXACTLY super-uniform conditional on
its country, the outer conformal step gives exact finite-sample coverage with NO
union bound — the cleanest possible statement, and the most "professor-grade" if
it holds.

**The finite-PSU trap (why it is appendix, not headline).** A design-based p-value
is super-uniform only if the design bootstrap / replicate-weight law is exact.
Rao–Wu and its kin are ASYMPTOTIC in the number of PSUs; ESS core countries have
~20–30 PSUs and singleton strata, so U_c is only approximately super-uniform
EXACTLY where design-awareness matters most (small, noisy surveys). C's exactness
is therefore conditional on a large-PSU approximation that fails on the target
cases. **Do not bet the paper's central theorem on C.**

**Reduction (v→0).** ✓ degenerate design ⇒ U_c degenerate ⇒ clustered PCB.

**Role.** A clean-theory appendix: "under an exact design-p-value oracle, the
two-stage construction is exactly valid; in finite PSU samples it inherits the
bootstrap's O(PSU^{-1/2}) slack." Useful as the ideal that B approximates
robustly, not as the deliverable.

---

## Summary against the Gate-5B criteria

| criterion (setup §6/§7) | A worst-case | B contamination | C two-stage p-value |
|---|---|---|---|
| reduces to clustered PCB at v=0 | ✓ | ✓ | ✓ |
| covers LATENT trajectory (not θ̃) | ✓ (conservative) | ✓ (dominance) | ✓ (if U exact) |
| NOT a K-fold union bound | ✗ (is 1−α−Kβ) | ✓ | ✓ |
| non-trivial efficiency vs [0,1] | ~ (can blow up) | ✓ (deconvolution) | ✓ |
| separates country-exch. from within-country design | ✓ | ✓ | ✓ |
| handles irregular missing rounds (≥ conditionally) | ~ | ✓ (composes w/ mask-cond.) | ~ |
| finite-sample honesty on ESS small-PSU regime | ✓ | ✓ | ✗ (asymptotic) |

**Lead: B. Baseline/envelope: A. Appendix ideal: C.** Detailed proofs next.
