# Design-Aware Clustered Conformal — formal setup (Gate 5B, candidate-agnostic)

Status: Gate 5B, 2026-07-06. This document fixes the data-generating
hierarchy, what is random, the target estimand, and the exact coverage
statement — BEFORE choosing a method (candidates A/B/C live in
`DESIGN_AWARE_METHOD_CANDIDATES.md`). No implementation in this gate.
Companion freeze: tag `gate5a-freeze`.

## 1. Two-stage data-generating hierarchy

**Outer stage — countries.** A meta-population Π over country trajectories.
Country c has a latent finite-population trajectory of CDFs
  θ_c = { θ_{c,r}(t) : r ∈ R_c, t ∈ T },   θ_{c,r}(t) = P_{c,r}(Y ≤ t),
where R_c ⊆ {1,…,R} is the country's observed round-set and T the threshold
grid. Countries (θ_1,…,θ_{K+1}) are exchangeable draws from Π. θ_{c,r} is the
TRUE finite-population trust CDF of country c at round r — the object a
political scientist means by "trust in country c at wave r".

**Inner stage — complex surveys.** θ_{c,r} is never observed. ESS draws a
stratified multistage sample S_{c,r} under known design (strata h, PSUs,
inclusion probabilities π, design weights w, replicate weights). The analyst
observes only the design-weighted estimate
  θ̃_{c,r}(t) = Σ_i w_{i} 1{Y_i ≤ t} / Σ_i w_{i},
and, via a design bootstrap / replicate weights, an estimate of its
sampling law — in particular the design SD v_{c,r}(t) and, if wanted, the full
bootstrap distribution of θ̃_{c,r}.

**Predictor.** A rule f̂, trained WITHOUT the target country's data
(leave-one-country-out out-of-fold), produces θ̂_{c,r}(t) for every
country-round. Under LOCF f̂ is the country's own previous round and fits
nothing; under fitted predictors (GBM/functional AR) the OOF discipline binds.

## 2. Three error terms — the decomposition everything rests on

For a source country-round the analyst can form only the OBSERVABLE error
  Ẽ_{c,r}(t) = θ̂_{c,r}(t) − θ̃_{c,r}(t).
The error we would USE if truth were known is the LATENT error
  E_{c,r}(t) = θ̂_{c,r}(t) − θ_{c,r}(t)  (transport error).
They differ by the survey error S_{c,r}(t) = θ̃_{c,r}(t) − θ_{c,r}(t):
  Ẽ_{c,r} = E_{c,r} − S_{c,r}.

So the observable calibration curve is the latent transport-error curve
**contaminated by an additive, design-generated, approximately mean-zero,
KNOWN-variance survey error S** (Var ≈ v²). This is the single structural fact
that separates our problem from plain clustered PCB, and it is what any
non-trivial method must exploit rather than bound away. Plug-in clustered PCB
uses Ẽ as if it were E — i.e. calibrates on contaminated scores.

## 3. The estimand is latent, and comes in two views

The target is the LATENT trajectory θ_{K+1}, not the observed θ̃_{K+1}. Two
distinct, both legitimate, coverage targets — kept separate because E6 showed
they behave oppositely:

- **Deployment view (primary).** Target country is UNSURVEYED (or its survey is
  withheld): protect the latent θ_{K+1,r}(t). No survey error enters the
  target. This is the nowcasting/transport use case.
- **Validation view.** Target country IS surveyed; we can only check coverage
  against θ̃_{K+1}, which carries its own survey error S_{K+1}. Any ESS holdout
  evaluation is unavoidably in this view, so the method must state coverage
  w.r.t. θ̃ AND relate it back to the latent-θ claim.

## 4. Exact coverage statement (the target theorem's conclusion)

Deployment, simultaneous over the target's whole observed trajectory:
  Pr[ θ_{K+1,r}(t) ∈ B_{K+1,r}(t)  ∀ r ∈ R_{K+1}, ∀ t ∈ T ] ≥ 1 − α,
where the probability is over BOTH sources of randomness:
  (i) the outer draw of the K+1 countries from Π (transport uncertainty), and
  (ii) the inner survey designs of the K SOURCE countries (which contaminate
       the calibration scores).
The target has no inner term in the deployment view. Fitting randomness is
conditioned out via the OOF construction (stated as an assumption, not proved).

For the validation view the conclusion instead bounds
  Pr[ θ̃_{K+1,r}(t) ∈ B_{K+1,r}(t) ∀ r,t ], with S_{K+1} now an inner term on
the target side too — the method adds v_{K+1} back on this side (E6: this is
what restored nominal in both views).

## 5. What is random vs fixed (referee-proofing)

| quantity | status |
|---|---|
| θ_c (latent trajectories) | random (drawn from Π), FIXED once drawn; the estimand conditions on θ_{K+1} being a fresh draw |
| R_c (round-sets) | random; the irregular-panel candidate must state its mechanism (MCAR/MAR of wave participation w.r.t. trust) — see THEOREM_CANDIDATES §B |
| S_{c,r} (survey errors) | random given θ_c; law known up to design-bootstrap estimation of v |
| θ̃, θ̂, v | observed / computed |
| α, β | fixed; β (design-set level) must be spent from α WITHOUT a K-fold union — the central design constraint (§6) |

## 6. The design constraint that separates a real contribution from inflation

A method is only a contribution if it does NOT reduce to: "build a β-level
survey confidence set per source country, intersect K of them, pay 1−α−Kβ."
That union bound forces β→0 as K grows and inflates the band without bound.
The contamination view of §2 is the escape hatch: survey error enters as noise
on the calibration SCORE DISTRIBUTION (one distributional object), not as K
separate confidence events to intersect. A valid method must therefore act at
the level of the score distribution — deconvolution, stochastic-dominance, or a
design-valid per-country super-uniform statistic — not at the level of K
per-country sets. `DESIGN_AWARE_METHOD_CANDIDATES.md` evaluates each candidate
against this bar; any candidate that collapses to §6's union bound is dropped
per the Gate 5B go/no-go criteria.

## 7. Reduction check (a validity necessary condition)

When the survey design variance vanishes (v ≡ 0, S ≡ 0, infinite samples), Ẽ =
E and every candidate MUST reduce exactly to the frozen clustered PCB of
`ESS_CLUSTER_THEORY.md`. Any construction failing this reduction is
mis-specified. This is the first row of the go/no-go table.
