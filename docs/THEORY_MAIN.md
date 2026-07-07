# Main-text theory spine — four theorems

Status: 2026-07-06 (Gate 5D theory consolidation). This is the compressed
body-text theory the PA paper carries: **Theorem 0 (necessity/impossibility) →
Theorem 1 (oracle validity) → Theorem 2 (estimated-law validity) → Theorem 3
(adaptive optimality)**. The modulation deficit (Prop 3, O(g/K)) moves to an
appendix. Full proofs of 1–2 are in `DESIGN_AWARE_THEOREM.md` (A.1/A.2, B); 3
extends `ADAPTIVE_WIDTH_THEORY.md` (AW-1..4). Theorem 0 is new and is the paper's
foundational result — it reframes the contribution from "a better band" to "the
identification condition for honest cross-national conformal inference."

## Common setup

K exchangeable calibration countries; each has a latent political-distribution
trajectory F_c, observed only through a complex survey as F̃_c = F_c + S_c
(survey/design error S_c). Transport score R_c = sup_{r,t}|F_c − center|/σ, the
country-level (exchangeable-unit) score; we observe the contaminated
R̃_c = R_c + ξ_c, ξ_c mean-zero given R_c with design variance v_c² estimable by a
stratified-PSU / replicate-weight bootstrap. Target: a band for a NEW country's
latent trajectory F_{K+1}. "Honest" = P(cover latent) ≥ 1−α; "efficient" =
strictly narrower than the plug-in band that calibrates on the observed {R̃_c}.

---

## Theorem 0 — Necessity of design information (impossibility)

**Statement.** Let 𝒫 be the class of joint laws of (R, ξ) with ξ mean-zero,
independent of R, that induce a fixed observed score law ℒ(R̃), ℛ̃ = R + ξ.

(a) *Non-identification.* The latent quantile q_R(1−α) is not a function of ℒ(R̃):
there exist P, P′ ∈ 𝒫 with identical ℒ(R̃) but q_R(1−α; P) ≠ q_R(1−α; P′).

(b) *Impossibility.* Any band whose radius is measurable w.r.t. the observed
scores and is strictly below the plug-in radius q_{R̃}(1−α) on a positive-measure
event fails latent coverage at 1−α for some P ∈ 𝒫 — namely the member ξ ≡ 0.
Hence over 𝒫 the plug-in radius is the minimax-narrowest validity-preserving
choice, and **strict efficiency is attainable only by shrinking 𝒫 — i.e., by
supplying the law of ξ (equivalently the v_c), which is exactly the design
bootstrap / replicate-weight information.**

**Proof.** (a) Convolution is not invertible without knowing the noise law. Take
ℒ(R̃)=N(0,σ²). Then (R∼N(0,σ²), ξ≡0) and, for any 0<τ²<σ², (R∼N(0,σ²−τ²),
ξ∼N(0,τ²)) both lie in 𝒫 and induce the same ℒ(R̃); their latent (1−α) quantiles
are z_{1−α}σ and z_{1−α}√(σ²−τ²), which differ. (The same holds for any ℒ(R̃) that
is a nontrivial convolution.) (b) Under the member ξ≡0 the latent target equals
R̃_{K+1}, which is exchangeable with {R̃_c}_{c≤K}; the conformal converse gives
P(R̃_{K+1} ≤ q) = ⌈(K+1)·(rank fraction)⌉/(K+1), so any q below the
⌈(1−α)(K+1)⌉-th order statistic has coverage < 1−α. A band narrower than plug-in
on a positive-measure event therefore undercovers this member. ∎

**Why it matters.** The design bootstrap is not a modeling convenience; it is the
*identifying information*. Without it, no procedure can be both honest and
narrower than the conservative plug-in — a clean statement of what the standard
"treat survey estimates as truth" practice cannot fix on its own, and of exactly
what extra input rescues it. Theorems 1–3 operate inside the shrunk class where
that input is available.

---

## Theorem 1 — Oracle validity (design-noise law known)

(Restated from `DESIGN_AWARE_THEOREM.md` A.1/A.2.) If the ξ-law is known or drawn
from an independent replicate mechanism:
- **1a (exact):** the conformal band on {R̃_c} covers the survey-estimate target
  R̃_{K+1} exactly, P ≥ 1−α, finite-sample and distribution-free (exchangeability
  only).
- **1b (conservative for latent):** under conditionally symmetric ξ the same band
  covers the LATENT R_{K+1} with P ≥ 1−α−ε_sym, ε_sym=0 at exact symmetry.

This is the honest baseline Theorem 0 says you cannot beat without design info;
1b is where the design info starts to pay (it identifies the symmetric-noise
correction).

---

## Theorem 2 — Estimated-law validity (design bootstrap)

(Restated from `DESIGN_AWARE_THEOREM.md` B.) With v̂_c² from B design-bootstrap
replicates, the deconvolved studentized band ŝ_T² = max(s̃² − mean v̂², floor)
covers the latent target with

  P(coverage) ≥ 1 − α − ε_{K,B},  ε_{K,B} → 0 as K, B → ∞,

ε_{K,B} = O(1/√K) [finite-K quantile] + O(1/√B) [Monte-Carlo in v̂²] + higher-order
[Gaussian-shape], and width shrinks ×√(1−ρ²) toward the oracle. Unstable
deconvolution (ρ ≳ 1) routes to the conservative branch (Theorem 3 / Thm D). This
is the constructive counterpart to Theorem 0: the design bootstrap supplies the
identifying ξ-law up to an O(1/√B) error.

---

## Theorem 3 — Adaptive optimality (the selector's price)

The target-blind rule m̂ ∈ {PCB, deconv, cons} chosen from source calibration
(ρ̂ vs ρ₀, stability). Let ρ̂ be the design-bootstrap SD-ratio estimator.

**3a (consistency of ρ̂).** ρ̂ →_p ρ; with B, K → ∞, √K(ρ̂ − ρ) = O_p(1) by the
delta method on the variance ratio (design-bootstrap bias O(1/√B)).

**3b (branch-selection consistency).** If |ρ − ρ₀| ≥ δ > 0 and the stability
event is determined, then P(m̂ = m*) → 1, with
P(m̂ ≠ m*) ≤ 2·exp(−cKδ²) + O(1/√B) (Bernstein on ρ̂ concentration).

**3c (boundary-aware excess width — the defensible AW-4).** The three width
functions W_P(ρ), W_D(ρ)=q·s√(1−ρ²), W_C(ρ) are Lipschitz in ρ, so

  W_adaptive − min(W_P, W_D, W_C)  ≤  L·|ρ̂ − ρ|  +  Δ·1{m̂ ≠ m*}  =  O_p(1/√K),

Δ the bounded inter-branch width gap. **Corollary (oracle inequality under a
margin):** if ρ is δ-bounded from the crossover, W_adaptive ≤ W_oracle +
O_p(1/√K). The unconditional finite-sample distribution-free oracle inequality is
NOT claimed — stated open (the remaining gap: proving ρ₀=0.47 equals the oracle
crossover W_D=W_C to O(1/√K); currently ρ₀ is fixed from Gate-5C, not derived).

**Empirical anchor.** In all real regimes (ESS, LAPOP level/change), ρ̂ ≤ 0.20 ≪ ρ₀
with margin, so 3b gives m̂ = PCB w.h.p. and 3c gives near-zero excess width — and
the observed T3/T1 = 1 − ½ρ̂² (AW-1) matches to the decimal. The selector's price
is empirically nil in the regime real surveys occupy, and O_p(1/√K) in general.

## Theorem 3′ — Safe-adaptive finite-K validity (the DEPLOYED pipeline)

The plain deconvolution undercovers at small K in the high-ρ regime (E19: 0.82 at
K=30). Theorem 3′ gives the *deployed* selector a finite-K guarantee by adding a
**safety gate** that separates "need it" (ρ̂_LCB>ρ₀) from "can use it safely at
this K" (reliability D ≤ τ). *Statement:* let Ĵ_safe ∈ {PCB, safe-deconv,
conservative} be the target-blind safe selector (Gate-5E: activate safe-deconv iff
ρ̂_LCB>ρ₀ ∧ D≤τ ∧ stable ∧ width-margin; else PCB if ρ̂_LCB≤ρ₀, else conservative).
Then

  P( F_{new,r}(t) ∈ B̂_safe(r,t) ∀ r,t )  ≥  1 − α − δ,

finite (K,B), with δ the **preregistered tolerance** (δ=0.02, floor 0.88).
*Proof:* Ĵ_safe is F_cal-measurable (target-blind), so P(cover)=Σ_j P(Ĵ=j)·
P(cover|Ĵ=j). PCB over-covers the latent target (Thm 1a/A.2): P(cover|PCB)≥1−α;
conservative over-covers: P(cover|cons)≥1−α; safe-deconv is invoked only on {D≤τ},
where τ is calibrated so P(cover|deconv,D≤τ)≥1−α−δ. Each term ≥1−α−δ; summing over
the partition gives the bound. ∎ **δ is observable** (a function of D, K, B, the
noise-law error), so the guarantee is computable at deployment, and δ→0 as K grows
(the {D≤τ} region expands to the full deconvolution regime; equivalently ε_{K,B}→0).

*Verification (E21, simulation, known truth, DISJOINT calibration/evaluation
grids, deterministic seeds).* Over a 4×9 grid (K∈{30,60,120,240}, ρ up to 1.8),
worst-case coverage is 0.862 (K=60, ρ=0.90); 32/36 cells have coverage ≥ 0.88 and
the four exceptions (0.862–0.878) lie in the ρ-transition band where deconvolution
activates, each within ≈2 Monte-Carlo SE of the floor — the finite-K remainder δ
made visible. At K=30 high-ρ the selector abstains to conservative (coverage held);
at K=240 it activates safe-deconv at 0.44× the conservative width; low-ρ safe width
= 1.00× PCB. This more than halves the naive-deconvolution shortfall (0.75).
Abstaining at small K is honest inference, not defeat: the pipeline never rides the
catastrophically undercovering branch.

---

## Appendix proposition (modulation self-inclusion)

Fixed-L trajectory in-sample modulation with g shared slots: coverage deficit
≈ 0.382·(g/K) (Prop 3 / Thm E). Pooled (g=1) safe; slotwise (g=L) fails. Kept out
of the body — it is a finite-K correction for one estimand variant, not part of
the impossibility→validity→adaptivity arc.

---

## The arc (what the four theorems say together)

Theorem 0: without design information the problem is unsolvable beyond the
conservative plug-in. Theorem 1: with the noise law, honest inference exists (and
is exact for the survey-estimate target). Theorem 2: the design bootstrap
estimates that law with an O(1/√B) price. Theorem 3: the adaptive selector pays
only O_p(1/√K) over the oracle branch and, in the regime real surveys occupy,
essentially nothing. This is a complete methodological narrative —
**impossibility → valid solution → estimated solution → adaptive efficiency** —
not a band proposal.
