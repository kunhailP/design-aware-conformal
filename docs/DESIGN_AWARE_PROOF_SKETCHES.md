# Proof Sketches — Gate 5B

Status: Gate 5B, 2026-07-06. Sketches, not final proofs — they fix the argument
structure and, crucially, mark exactly where each result is EXACT, CONSERVATIVE,
or CONJECTURAL, so the go/no-go is honest. Notation from
`DESIGN_AWARE_FORMAL_SETUP.md` and `DESIGN_AWARE_METHOD_CANDIDATES.md`.

Baseline (already established, `ESS_CLUSTER_THEORY.md`): with equal-length
exchangeable country trajectories and a modulation s independent of the scored
errors, R_c = max_{r,t}|E_{c,r}|/s_r(t) yields
Pr(R_{K+1} ≤ R_{(m)}) ≥ 1−α, m = ⌈(1−α)(K+1)⌉ — finite-sample simultaneous over
(rounds×thresholds). All sketches below perturb THIS by the survey error S.

---

## A. Worst-case band is valid but pays the union bound (EXACT bound)

Let G_c = {θ_{c,r}(t) ∈ C_{c,r}(t) ∀r,t} be the event country c's design set
covers its truth; Pr(G_c^complement) ≤ β. On ∩_{c≤K} G_c the robust scores
dominate the true transport magnitudes, so the clustered conformal argument on
{R_c^rob} gives Pr(cover | ∩G_c) ≥ 1−α. Then
Pr(cover) ≥ Pr(cover ∩ ∩G_c) ≥ (1−α) − Pr(∪ G_c^c) ≥ 1 − α − Kβ,
by the union bound over the K source events. The Kβ term is real (each source
design set can independently fail) and cannot be removed within this
construction — this is precisely why A is a baseline, not the method. ∎(sketch)

---

## B1. Plug-in clustered PCB is conservative for the latent deployment target

**Claim.** Under (D) below, the plug-in band calibrated on contaminated scores
{R̃_c} covers the latent deployment trajectory with prob ≥ 1−α — no Kβ.

**Step 1 (coordinatewise inflation, EXACT).** Fix (r,t). Survey error
S_{c,r}(t) ⟂ E_{c,r}(t), E[S]=0. By Jensen on the convex map x↦|a−x|,
E_S |E_{c,r}(t) − S_{c,r}(t)| ≥ |E_{c,r}(t)|. So in conditional mean each
contaminated coordinate magnitude is ≥ its clean counterpart.

**Step 2 (lift to the sup — the load-bearing step).** We need the contaminated
score R̃_c = max_{r,t}|E−S|/s to stochastically dominate the clean
R_c = max|E|/s. Coordinatewise expectation-dominance (Step 1) does NOT
automatically give sup stochastic dominance (max is nonlinear). Two honest
routes:
  (D-Gauss) If S_{c,r}(t) is Gaussian (design-bootstrap CLT, reasonable at
    moderate PSU counts), then |E−S| ⪰_st |E| coordinatewise in the usual
    stochastic order, and since max of independent-across-coordinates
    stochastically-larger variables is stochastically larger, R̃_c ⪰_st R_c.
    → dominance EXACT under Gaussian design noise.
  (D-TV) Without Gaussianity, use the Feldman et al. (2022) TV route: if
    d_TV(law R̃, law R) ≤ ε, inflate the level to α' = α + 2(K/(K+1))ε; the
    plug-in band at α' covers at 1−α. → dominance replaced by an explicit,
    estimable ε-correction (v gives ε).

**Step 3 (conformal monotonicity).** If R̃_c ⪰_st R_c then the (1−α) empirical
quantile of {R̃_c} is ≥ that of {R_c}; the clean target R_{K+1} exceeds the
larger threshold with prob ≤ α. Hence coverage ≥ 1−α. ∎(sketch)

**Status.** EXACT under (D-Gauss); CONSERVATIVE-with-known-correction under
(D-TV). Either way, NO union bound. This is the validity backbone and the reason
E6 saw 94–100% on deployment.

---

## B2. Deconvolution recovers efficiency (EXACT reduction; CONSERVATIVE guard)

**Claim.** Studentizing by the deconvolved transport scale shrinks width toward
the oracle while preserving B1 validity, with an explicit guard.

**Scale identity (EXACT in expectation).** With S ⟂ E and Var(S_{c,r}(t))=v²,
Var(Ẽ) = Var(E) + v². So s_T²(t) := s_plug²(t) − mean_c v_c²(t) is an unbiased
estimate of the transport-only variance Var(E). The oracle band uses s_T; the
plug-in uses s_plug ≥ s_T, hence is wider by √(1 − v²/s_plug²).

**Target scoring.** Deployment target has no S, so it is scored with s_T alone;
each calibration country is scored with √(s_T² + v_c²) (its own noise), matching
the target's clean scale to the calibration's contaminated scale in the studenti-
sation. Under (D) the rank argument of B1 still gives ≥1−α, now at oracle width.

**Guard (where it stops being exact — HONEST boundary).** When ρ = v/s_transport
≳ 1, s_plug² − v² is small or negative; the floor clips it and the studentised
target score is divided by too small a scale ⇒ over-tight ⇒ undercoverage
(E6 D/E: .81–.83). Rule: if the estimated ρ (per grid point or pooled) exceeds
ρ*, revert that band to the B1 plug-in (valid, conservative). ρ* to be set on the
Gate-5C simulation as the largest ρ at which deconvolution coverage stays ≥ 1−α
within MC error.

**Status.** Scale identity EXACT in expectation; validity via B1; the guard is
the price of finite noise. Reduces to clustered PCB at v=0 (s_T=s_plug, guard
never triggers). ∎(sketch)

---

## C. Two-stage p-value: exact under an oracle, asymptotic in finite PSUs

**Oracle claim.** If U_c is exactly super-uniform conditional on country c
(Pr(U_c ≤ u | c) ≤ u), then {U_c} are exchangeable super-uniform scores across
the exchangeable countries; the conformal rank of U_{K+1} is uniform and the
band inverting the (1−α) rank is exactly valid — no union bound, no dominance
assumption. Cleanest possible statement.

**Where it breaks (EXACT caveat).** U_c is built from the design bootstrap /
replicate-weight law, which approximates the true design law with error
O(n_PSU^{-1/2}) (Rao–Wu; worse with singleton strata). So
Pr(U_c ≤ u | c) = u + O(n_PSU^{-1/2}), and super-uniformity — hence the exactness
— degrades precisely for small-PSU countries, the design-aware target cases.
Net coverage 1 − α − O(mean n_PSU^{-1/2}). ∎(sketch)

**Status.** EXACT under the design-p-value oracle; otherwise inherits the
bootstrap's asymptotic slack. Appendix ideal, not the deliverable.

---

## Prop 1 (recursion of the wrong unit) — EXACT, framing result

Each round's curve band has marginal coverage 1−α, but the trajectory event is
the intersection over |R_c| rounds. By the same Fréchet/Šidák sandwich as the
original pointwise-vs-simultaneous theorem, lifted one level:
(1−α)^{|R_c|} ≤ Pr(cover whole trajectory) ≤ 1−α,
with equality to the lower bound under round-independence and to the upper under
perfect round-dependence. Empirics (E8): 0.89^7 ≈ .44 vs observed .429/.543. ∎

**Status.** EXACT. Low theoretical novelty (known sandwich, one level up) but the
essential framing — "curve validity ≠ trajectory validity."

---

## Prop 3 (in-sample modulation undercoverage) — the sleeper, HIGH novelty

**Scope (deliberately narrow).** Not "studentization is a problem" (known); the
claim is a QUANTIFIED coverage deficit for finite-K, multi-slot functional
calibration when the modulation is estimated in-sample and sliced.

**Setup.** g modulation slices (g=1 pooled, g=L slotwise); scale ŝ estimated from
the K calibration curves. Calibration score R_i^in uses ŝ that INCLUDES curve i;
the target score R_new uses ŝ that does NOT include the target.

**Claim.** E[R_i^in] < E[R_new]: including curve i inflates the slice scale that
divides curve i's own deviations, deflating its score relative to the target's.
The rank of R_new is therefore stochastically too high and coverage falls below
1−α by Δ(K,g) with, to leading order,
Δ_cov ≈ c · (g / K) · (curvature of the score-to-scale map),
i.e. the deficit GROWS with the slicing granularity g and SHRINKS as 1/K. Split
modulation (scale from a disjoint fold) or pooling to g=1 removes the leading
1/K self-inclusion term.

**Evidence already in hand (E10).** slotwise (g=L=4): ESS .733, sim ratio
.88–.91 at K=20 worsening with L; pooled (g=1): ≥.97 ratio, coverage within
1–2pp; split & unstudentised: at attainable level across the grid. The
K×g×L simulation surface is exactly the Δ(K,g) characterization.

**Status.** CONJECTURAL leading-order expansion, but with the empirical surface
already measured and a clean mechanism. Literature: DFV force s onto the training
split TO AVOID this and never quantify it → no prior characterization. Remaining
priority check: general split-conformal normalized-score bounds (Barber et al.)
for any adjacent rate before claiming full priority. Generalizes beyond surveys
→ the most externally-citable result.

---

## Two-layer honesty note for Candidate B (added Gate 5D, per advisor)

Simulation showing nominal coverage is NOT a proof of finite-sample exactness.
The paper states B in two explicit layers:

- **Oracle design-noise law.** If the survey-error law (hence v, and the
  dominance/ε in B1) is KNOWN or drawn from an INDEPENDENT replicate mechanism
  disjoint from the calibration scores, B1 gives exact/conservative validity and
  B2's scale identity is exact-in-expectation. This is the clean theorem.
- **Estimated design-noise law.** In practice v and the noise law are estimated
  from the same replicate weights / design bootstrap. Then validity holds only up
  to a remainder:  Pr(coverage) ≥ 1 − α − ε_{K,B}, with ε_{K,B} → 0 as the
  number of source countries K and bootstrap draws B grow (and degrading with
  singleton strata / low PSU counts). ESS uses THIS layer.

The deconvolution must also declare, before seeing the target: the negative-
variance floor on s_T² = max(s_plug² − mean v², floor); that the regularization
/ floor and the ρ* fallback threshold are chosen WITHOUT the target; and that v
is estimated on a mechanism independent of the calibration score being
studentized where the exact layer is claimed. The paper never writes
"simulation valid ⇒ finite-sample exact"; it writes "exact under the oracle
layer; asymptotically valid with remainder ε_{K,B} under the estimated layer,
confirmed by simulation."

## What must be proven vs simulated (hand-off to Gate 5C)

| result | proof status | Gate-5C simulation must confirm |
|---|---|---|
| A union bound | exact | (none; it is the baseline to beat) |
| B1 dominance | exact under Gauss; ε-correction else | dominance holds on realistic ESS noise; ε small |
| B2 deconvolution | exact-in-expectation + guard | ρ* threshold; width→oracle rate |
| C p-value | exact under oracle; O(PSU^{-1/2}) else | slack size at ESS PSU counts |
| Prop 1 | exact | (already, E8) |
| Prop 3 | conjectural expansion | Δ(K,g) rate matches c·g/K |
