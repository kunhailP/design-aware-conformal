# Candidate B — the design-aware clustered conformal theorem

Status: 2026-07-06 (Gate 5D theory track). This consolidates the Gate-5A/5B
sketches (`DESIGN_AWARE_FORMAL_SETUP.md`, `DESIGN_AWARE_PROOF_SKETCHES.md`) into
the five results the paper must prove, each with **assumptions → statement →
proof → failure case → code correspondence**. The governing discipline (stated
once, applied everywhere): **"exact" and "asymptotically valid" are never mixed.**
Result A layer-1 and Result C are finite-sample exact; A layer-2, B, D carry an
explicit remainder; E is an O(g/K) deficit.

## Setup and notation

- **K exchangeable source countries** c = 1..K, plus a target K+1. Each country
  has a latent population curve F_c(·) (a CDF over the trust scale) and a
  transport center F̄ (leave-one-out mean or a fitted center).
- **Latent transport score** (one scalar per country, the exchangeable unit —
  Gate-2 finding that the country, not the country-round, is the unit):

  R_c = sup_{t,slot} |F_c(t) − F̄(t)| / σ(t),   studentized by a modulation σ(t).

  Conformalizing {R_c} gives a simultaneous band for the latent curve of a new
  country (Dunn–Wasserman–Ramdas exchangeable-group conformal; Diquigiovanni–
  Fontana–Vantini sup-over-index modulation).
- **The design complication.** F_c is never observed; a complex survey returns an
  estimate F̃_c = F_c + S_c, with survey/design error S_c. At the score level this
  induces

  R̃_c = R_c + ξ_c,   E[ξ_c | R_c] = 0,   Var(ξ_c | ·) = v_c²,

  where v_c² is estimated by a **stratified PSU / replicate-weight design
  bootstrap** (`design_sd`, `psu_bootstrap`). ρ_c := v_c / s_R is the design-to-
  transport noise ratio (SD form; the ONLY ρ used — cf. prereg §6).
- **Two possible deployment targets**, kept distinct throughout:
  (T1) the survey-estimated score R̃_{K+1} of a newly surveyed country;
  (T2) the LATENT score R_{K+1} — the object the political claim is about (the
  true population curve, not its survey estimate).

---

## Result A — Oracle validity (B1)

**A.1 (exact, distribution-free).** *Assumptions:* {(F_c, survey design)}_{c=1}^{K+1}
exchangeable; scores R̃_c computed by a fixed measurable rule from each country's
own sample. *Statement:* the split/full-conformal band using radius
q̃ = R̃_{(⌈(1−α)(K+1)⌉)} (order statistic of the observed scores) satisfies

  P( R̃_{K+1} ≤ q̃ ) ≥ 1 − α,

finite-sample, for target **T1**. *Proof:* exchangeability of {R̃_c}_{c=1}^{K+1}
⇒ the rank of R̃_{K+1} is uniform on {1,…,K+1}; standard conformal argument. No
assumption on the design-noise law is used. *Failure case:* none for T1 beyond
exchangeability (violated by, e.g., a country-specific mode effect correlated
with trust — a design assumption to state, not a theorem gap). *Code:*
`clustered_band.clustered_quantile` (exact order statistic m=⌈(1−α)(K+1)⌉),
`test_cluster_quantile_order`.

**A.2 (conservative for the latent target).** *Assumptions:* A.1, plus ξ_c
conditionally **symmetric** and independent of R_c. *Statement:* the same band is
conservative for target **T2**:

  P( R_{K+1} ≤ q̃ ) ≥ 1 − α − ε_sym,   ε_sym = 0 under exact symmetry.

*Proof:* R̃ = R + ξ with symmetric ξ is a mean-preserving spread of R; for the
one-sided upper functional (R ≥ 0, band {R ≤ q̃}) the convolution moves mass
outward symmetrically, so the (1−α) quantile of R̃ dominates that of R; hence a
radius calibrated on R̃ over-covers R. The Feldman–Zrnic–Candès noisy-label
argument supplies ε_sym as a total-variation bound when symmetry is only
approximate. *Failure case:* skewed design noise (e.g. small-cell boundary bias
near F=0/1) makes ε_sym > 0 and must be reported, not assumed away. *Code:*
`design_aware.da_worstcase_band` (the conservative plug-in radius).

---

## Result B — Estimated-law efficiency (B2 deconvolution)

*Assumptions:* A.1; ξ_c approximately Gaussian with variance v_c² estimated from
B design-bootstrap replicates v̂_c²; transport-score variance s_R² identified.
*Statement:* the **deconvolved** studentized band, using

  ŝ_T² = max( s̃² − mean_c(v̂_c²),  floor ),   s̃² = sample var of {R̃_c},

covers the latent target T2 with

  P( R_{K+1} ≤ q̂_T ) ≥ 1 − α − ε_{K,B},   ε_{K,B} → 0 as K, B → ∞,

and the band **width shrinks toward the oracle** by ×√(1 − ρ²) relative to the
plug-in (A.2) width. *Proof sketch:* Var(R̃) = Var(R) + E[v²] under conditional
mean-zero noise (law of total variance); subtracting a consistent v̂² estimate
identifies s_R². ε_{K,B} decomposes as (i) Monte-Carlo O(1/√B) in v̂², (ii)
finite-K quantile/Var estimation O(1/√K), (iii) the Gaussian-shape approximation
(higher order in the standardized cumulants). Each → 0; none is claimed exact.
*Failure case:* mean(v̂²) ≥ s̃² (design noise ≳ transport signal, ρ ≳ 1) drives
ŝ_T² to the floor → hand off to Result D. *Code:* `design_aware.da_studentized_band`
(implements ŝ_T² = s_plug² − mean(V²) with the floor), `test_design_aware`.

**This is the regime-adaptive payoff (criterion set for WVS):** width ≈ oracle
when ρ small, and the correction is *earned* only where design noise is real.

---

## Result C — Zero-noise reduction

*Assumptions:* v_c → 0 for all c (negligible design noise). *Statement:* Candidate
B reduces **exactly** to the standard clustered/exchangeable-country PCB:
R̃_c → R_c, mean(v̂²) → 0, ŝ_T² → s̃², q̂_T → the plain conformal quantile of
{R_c}. *Proof:* direct substitution; every design-aware term vanishes.
*Consequence:* **no needless widening** when the survey is effectively a census /
uniform-weight design (criterion 1) — the method never pays for uncertainty it
doesn't have. This is why it is safe as a default. *Code:* setting
`v_cal = v_target = 0` in `da_studentized_band` returns the `clustered_band`
result; guaranteed by `test_single_round_reduces_to_pcb`.

---

## Result D — Conservative fallback (stability)

*Assumptions:* an estimated ρ̂ = √(mean(v̂²)/s̃²) computed from calibration only.
*Statement:* the estimator

  band = deconvolved (B)          if ρ̂ ≤ ρ*,
         plug-in / worst-case (A.2) if ρ̂ > ρ*  or  s̃² − mean(v̂²) < floor,

is valid for T2 in **both** branches (B's asymptotic guarantee below ρ*; A.2's
conservative guarantee above), and the switch depends only on calibration-side
(v̂, s̃) quantities — **never on the target** — so no selection bias enters.
*Proof:* the two branches are each independently valid (Results B, A.2); the
selector is measurable w.r.t. the calibration σ-field, so conditioning on the
chosen branch preserves its marginal guarantee. *Failure case:* ρ* mis-set — but
because both branches are valid, a wrong ρ* costs efficiency, not coverage. ρ* and
the floor are fixed in the preregistration (ρ* ≈ 0.47 from Gate-5C), before any
target. *Code:* the `max(·, floor)` guard in `da_studentized_band` + the
`da_worstcase_band` branch; the selection rule is pre-registered, not tuned.

---

## Result E — Finite-K self-inclusion deficit (Proposition 3)

*Assumptions:* the fixed-length-L trajectory estimand with in-sample modulation
where each country contributes to the modulation of g slots. *Statement:* the
finite-K coverage deficit is

  (1 − α) − coverage ≈ 0.382 · (g / K),   (empirical R² = 0.923, Gate-5C),

so **pooled** modulation (g = 1) is safe and **slotwise** (g = L) undercovers by
≈ 0.382·L/K. *Proof:* the studentized score's self-inclusion correlates the
numerator and denominator; a first-order expansion of the order-statistic bias in
the number of shared slots gives the linear g/K rate; the constant is estimated,
not derived, and flagged as such. *Failure case:* very small K with large L
(g/K not small) — the deficit is non-negligible and the split/unstudentized
variants (U0, S1, exact) must be used instead. *Code:*
`fixed_trajectory_band.trajectory_modulation(kind='pooled')` vs `'per_slot'`;
`test_split_modulation_exact`, `test_unstudentized_exchangeability`,
`e10_modulation_validity`.

---

## What is exact vs asymptotic (the one table a referee will check)

| result | guarantee | target | finite-sample? |
|---|---|---|---|
| A.1 | ≥ 1−α | T1 (survey estimate) | **exact**, distribution-free |
| A.2 | ≥ 1−α−ε_sym | T2 (latent) | exact iff noise symmetric |
| B | ≥ 1−α−ε_{K,B} | T2 (latent) | **asymptotic**, ε→0 in K,B |
| C | ≡ clustered PCB | — | **exact** reduction |
| D | valid both branches | T2 | inherits A.2 / B |
| E | deficit ≈ 0.382 g/K | fixed-L trajectory | finite-K correction |

The paper's ESS/ WVS empirics live under A.1 (exact, on the surveyed scores) and
B/D (efficiency for the latent target); coverage itself is demonstrated only in
simulation (Gate 5C), never claimed on real data. The remaining formal work is
tightening ε_{K,B} constants (currently order-of-magnitude) and the ε_sym TV
bound under boundary-skewed design noise — both are honestly open, neither blocks
the empirical claims.
