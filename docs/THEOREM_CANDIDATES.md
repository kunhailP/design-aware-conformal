# Theorem Candidates — three formalizations, ranked by novelty and necessity

Status: Gate 5A, 2026-07-06. Derived from `docs/NOVELTY_MATRIX.md`. No method
code written yet; this fixes the theory targets BEFORE implementation (Gate 5B
discipline). Notation: countries c = 1..K+1 exchangeable; country c observes
rounds r ∈ R_c (a round-set / missingness mask); threshold grid t = 1..T;
transport-error curve E_{c,r}(t) = θ̂_{c,r}(t) − θ_{c,r}(t); survey-estimated
curve θ̃_{c,r} with θ̃ = θ + S (survey error), design SD v_{c,r}(t).

Baseline result already in hand (Gate 3/4, `docs/ESS_CLUSTER_THEORY.md`): with
equal-length trajectories and modulation independent of the scored errors,
R_c = max_{r,t}|E_{c,r}(t)|/s_r(t) gives finite-sample simultaneous coverage
≥ 1−α over a held-out country. Call this **PCB-traj (exact)**. The three
candidates below each remove one of its idealizations.

---

## Candidate A — Design-aware clustered trajectory band

**Gap filled (matrix empty cell #1):** calibration curves are survey estimates
θ̃, not truth θ. Plug-in PCB scores E_plug = θ̂ − θ̃ = (θ̂−θ) − S conflate
transport error with survey error S. E6 simulation showed this is conditionally
anti-conservative for noisy-survey targets and distorts the validation
protocol; deployment (unsurveyed target) is conservative but wide.

**Estimand.** Band for the true (not survey-estimated) curve θ_{c*,r} of a
held-out country, valid simultaneously over (r ∈ R_{c*}, t).

**Theorem candidate (dominance form).** Let the per-country design-uncertainty
set be C_{c,r}(t) = [θ̃_{c,r}(t) ± z_β v_{c,r}(t)] with P(θ ∈ C) ≥ 1−β
(design bootstrap). Define the worst-case score
`R_c = max_{r,t} sup_{θ∈C_{c,r}} |θ̂_{c,r}(t) − θ(t)| / s_r(t)`.
Then the clustered band calibrated on {R_c} covers the true trajectory with
probability ≥ 1 − α − K·β (union over the K design-set failures), and ≥ 1−α as
β→0. A sharper form: if the noisy scores stochastically dominate the clean
scores (Feldman et al. 2022, Thm 2.1, lifted to sup-scores), plug-in PCB is
already conservative for the deployment estimand — the worst-case inflation is
only needed for the validation estimand and for the conditional (noisy-target)
failure.

**Assumptions.** Country trajectories exchangeable; design bootstrap consistent
for v (Rao–Wu for stratified PSU); s independent of scored errors (Candidate is
composable with the split modulation of Gate 4A). β spent explicitly from the α
budget — the honest price of not knowing θ.

**Counterexample / failure mode.** If v is estimated from too few PSUs
(singleton strata), the design set undercovers, β is wrong, and the K·β leak is
unbounded — must gate on effective PSU count (already flagged in the panel
builder). Worst-case score can also be trivially wide when v ≫ transport SD
(E6 cell E) — abstain rather than report.

**Implementation difficulty.** Low–moderate. `da_worstcase_band` and
`da_studentized_band` prototypes already exist (E6); the nested design
bootstrap is the CPU cost (B_design × B_country), vectorizable.

**Empirical necessity.** Conditional: on ESS with LOCF the noise ratio is
0.16–0.20 so the average effect is small, BUT the conditional failure (small-n
countries) is real and is exactly the ESS heterogeneity. Necessity is high for
WVS (smaller, more variable samples) and for the substantive small-country
claims.

**Novelty risk.** **LOW.** The matrix intersection is empty; the closest named
constructions (Uncertain Imputation, arXiv:2505.04733; Feldman dominance) target
adversarial/bounded corruption, not known heteroskedastic design variance. This
is the single most defensible new theorem. Position as "the known-heteroskedastic
-variance analogue of UI, with a design-bootstrap uncertainty set and a
dominance validity argument."

---

## Candidate B — Irregular-length trajectory band

**Gap filled (matrix empty cell #3):** countries have different |R_c|, so
raw sup-scores are not exchangeable (a longer trajectory has more draws to throw
a large max). Gate 4 avoided this by the balanced L=4 subset — it *discarded
data*. A PA method must use unbalanced ESS.

**Estimand.** Band for a held-out country's trajectory over its actual observed
round-set R_{c*}, valid conditional on the round-set pattern.

**Theorem candidate (two routes; the paper picks one, reports the other).**
- *Route B1 — Mondrian-by-length.* Partition countries by |R_c| (or by round-set
  pattern); within each length stratum ℓ, sup-scores are exchangeable, so the
  per-stratum clustered band has finite-sample coverage ≥ 1 − α − o(1)
  conditional on ℓ (Vovk 2012). Cost: needs enough countries per stratum — with
  ~35 ESS countries the fine partition starves.
- *Route B2 — mask-conditional weighted CP.* Treat R_c as a missingness mask M_c;
  reweight calibration countries by mask similarity to the target and apply
  weighted conformal (Fan et al. 2025 template). Coverage P(cover | M_{c*}) ≥
  1−α under MCAR of the round-set (countries miss waves independently of their
  trust level), adaptive under MAR. This is the honest ESS assumption and does
  not starve.
- *Route B3 (fallback) — length-normalized score* R_c = max_{r,t}|E|/(s_r(t)·
  a_{|R_c|}) with a length-calibration factor a_ℓ estimated on calibration
  countries. NO exact theorem exists (matrix: normalization is a heuristic);
  report only as an efficiency variant with simulation-characterized coverage.

**Assumptions.** B1: enough countries per length class. B2: round-set MCAR/MAR
w.r.t. the outcome — plausible for ESS (participation driven by funding, not
trust levels) but must be argued and probed. B3: none exact.

**Counterexample.** If wave participation IS informative (a country drops out
*because* trust collapsed — e.g., democratic backsliding ending ESS
participation), MAR fails and B2's guarantee degrades by the Barber et al. 2023
TV coverage-gap. Must test with the known ESS exits (RS, TR, and post-2012
dropouts already flagged in E9).

**Implementation difficulty.** Moderate. Mondrian is trivial; mask-conditional
weighting needs a mask-similarity kernel and the finite-sample weighted
quantile (weighted_conformal.py already has the machinery).

**Empirical necessity.** High — this is what lets the paper use all 289
country-rounds / 35 countries instead of the balanced 30, and it is the honest
answer to "why did you throw away data."

**Novelty risk.** **Moderate.** The impossibility ceiling (Barber et al. 2021)
and the mask-conditional template (Fan et al. 2025) exist, so B1/B2 are
*applications* of known guarantees to a new unit. The genuinely open piece is
B3 (a length-adjusted sup-score with a finite-sample theorem) — high-novelty but
high-risk; likely stays a simulation-characterized conjecture, not a theorem.
Net: solid contribution as "first conditional-validity treatment of irregular
survey panels," not a landmark theorem.

---

## Candidate C — Weighted trajectory band with abstention

**Gap filled (matrix empty cells #4):** transport to a structurally novel target
(hold out an entire region) breaks country exchangeability; and when no
calibration country resembles the target, a confident band is a lie.

**Estimand.** Band for a target region's country trajectories under covariate
shift, OR an explicit abstention certificate "target outside source support."

**Theorem candidate.** Weighted clustered conformal (Tibshirani et al. 2019 +
Barber et al. 2023 lifted to country level): reweight source countries by
covariate similarity w(c); finite-sample coverage ≥ 1−α under known weights,
degrading by the TV coverage-gap under estimated weights. Abstention rule: if
the clipped effective sample size (Wang–Goel 2026) falls below n_min, or the
target's covariate density ratio exceeds a clip threshold, return the trivial
band [0,1] with an explicit "out-of-support" flag rather than a weighted band.
Coverage-preserving because [0,1] trivially covers.

**Assumptions.** Covariate shift (not concept shift) between regions; a
similarity/weight model; a declared clip threshold with a stated ESS-based
n_min.

**Counterexample.** Concept shift — the *relationship* between covariates and
trust differs by region (Eastern-European trust dynamics structurally unlike
Nordic) — is not covariate shift, and no reweighting fixes it; the band
undercovers and abstention may not trigger. Must be stated as the boundary of
the method.

**Implementation difficulty.** Low. `weighted_conformal.py` exists; adds a
clip-based abstention gate.

**Empirical necessity.** Medium. Needed only for the leave-one-region-out
holdout; PCB-traj already holds for same-region and temporal transport (mirrors
the original paper's finding).

**Novelty risk.** **Moderate-high.** Weighted CP across populations and
abstention-by-clipping both exist; the combination (reject-option guarantee
*under shift*) is the open piece, but it is incremental over Wang–Goel 2026 +
García-Galindo 2025. Best positioned as a *robustness/honesty* section, not the
methodological center.

---

## Cross-cutting theory (needed regardless of which candidate leads)

- **Prop 1 (recursion of the wrong unit).** Round-level curve validity ≠
  trajectory validity: even if each round's band has coverage 1−α, the joint
  trajectory coverage is ≤ 1−α with a Šidák-type sandwich
  (1−α)^{|R_c|} ≤ Cov^traj ≤ 1−α. Already have the empirics (E8: 42.9%/54.3% vs
  0.89^7). This is the direct one-level-up analog of the original paper's
  pointwise-vs-simultaneous theorem — LOW novelty as pure theory but essential
  framing.
- **Prop 3 (self-inclusion breaks rank symmetry) — HIGH NOVELTY, see below.**

## The sleeper contribution: Prop 3 (in-sample modulation undercoverage)

The functional-conformal literature (DFV 2021 Remark 5; DFV 2022 verbatim
"s_{I₁} depends only on the training set as its dependence on the calibration
set would imply not to obtain closed-form valid prediction bands") **recognizes
the self-inclusion hazard only as a reason to avoid it, and never quantifies the
coverage penalty.** Gate 4A (E10) already quantifies it: slotwise in-sample
modulation undercovers to .733 (ESS) / .77 (sim, K=20, L=8), with a
self-inclusion score-ratio that shrinks as 1/(K·slices) and worsens with the
slicing granularity. A formal statement —

> *Prop 3 candidate.* When the modulation s is estimated on the same calibration
> scores it studentizes and sliced into g groups, each calibration score is
> deflated relative to the target's by a factor bounded below by a function of
> (K, g); consequently the conformal rank of the target is stochastically too
> high and coverage falls below 1−α by an amount increasing in g and decreasing
> in K. Split or pooled (g=1) modulation removes the leading term.

— is a clean, citable result with no prior quantification. **Novelty risk: LOW.**
It generalizes beyond surveys (applies to all studentized functional conformal),
so it is the contribution most likely to be cited outside political science.
Literature check done: no functional-conformal paper quantifies it. Remaining
check: the general split-conformal literature (Barber et al. normalized scores)
for any adjacent bound before claiming full priority.

---

## Recommendation (feeds PA_NOVELTY_RISK.md)

Lead the paper's **method** with **Candidate A (design-aware)** as the primary
theorem and **Prop 3** as the sharp secondary theorem — both LOW novelty-risk
and both filling confirmed-empty cells. Use **Candidate B (irregular panel)** as
the setting that makes the method usable on real ESS (necessity high, novelty
moderate). Demote **Candidate C** to a robustness section. Do **not** lead with
"trajectory PCB" as the novelty — it is a borrowable extension of DFV-JMVA (see
PA_NOVELTY_RISK.md).
