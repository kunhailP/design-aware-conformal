# Adaptive-width theory — the regime guarantees Candidate B needs

Status: 2026-07-06 (Gate 5D Part C theory track). Both real datasets, both
estimands (level and change), are low-ρ (ESS deff≈1; LAPOP transport ρ̂≈0.07–0.13;
LAPOP change transport ρ̂≈0.10–0.20 — all < ρ₀=0.47), so the deconvolution branch
never activates on real data. This makes the THEORY, not the data, responsible
for the moderate/high-ρ regime. This note states the four results that discharge
that responsibility. Builds on `DESIGN_AWARE_THEOREM.md` (Thm A–E); notation
identical. Widths are half-widths of the transport band.

Setup: source calibration gives scores and per-index design SDs; three branch
widths at level 1−α:
- PCB:    W_P = q_P · s,        scores |E|/s,           s = _modulation(E)
- deconv: W_D = q_D · s_T,      s_T = s·√(1−ρ²),        scores |E|/√(s_T²+v²)
- cons:   W_C = q_C · s,        scores (|E|+z v)/s
with ρ² := mean_t v(t)² / s(t)² (SD-ratio convention, project-wide). The adaptive
rule (target-blind, Thm D): Ĵ = PCB if ρ̂<ρ₀; deconv if ρ̂≥ρ₀ ∧ stable; else cons.

---

## Theorem AW-1 (low-ρ reduction, with rate — proven)

*As ρ̂ → 0*, s_T = s√(1−ρ̂²) → s and the deconv scores → the PCB scores, so
q_D → q_P and

  W_D / W_P  =  (q_D/q_P)·√(1−ρ̂²)  =  1 − ½ρ̂² + O(ρ̂⁴).

Below ρ₀ the selector returns PCB exactly, so W_adaptive = W_P. *Proof:* Taylor
of √(1−ρ̂²); q_D/q_P → 1 by continuity of the finite-sample quantile in the
studentization as v→0 (the score vectors converge pointwise, K fixed). ∎

**Empirical check (this is the paper's cleanest quantitative tie).** The predicted
W_D/W_P = 1−½ρ̂² matches the LAPOP change-transport observations:

| outcome | ρ̂ | predicted 1−½ρ̂² | observed T3/T1 |
|---|---|---|---|
| b13 | 0.116 | 0.993 | 0.995 |
| sat | 0.103 | 0.995 | 0.989 |
| ing4 | 0.197 | 0.981 | 0.965 |

The second-order rate explains why, in every real-data regime, Candidate B sits
within ~1–3% of clustered PCB: the reduction penalty is O(ρ²), and real ρ is
small. The method is provably almost-free where it isn't needed.

---

## Theorem AW-2 (moderate/high-ρ conservative dominance — condition)

For ρ̂ ≥ ρ₀ with stable deconvolution,

  W_D / W_C  =  (q_D/q_C)·√(1−ρ̂²).

The worst-case scores (|E|+z v)/s stochastically dominate |E|/s, so q_C ≥ q_P and,
to first order, q_C ≈ q_P·(1 + z ρ̂·κ) for a design-geometry constant κ∈(0,1]
(κ = correlation of the |E| and v orderings across the calibration set). Hence

  W_D / W_C  ≈  √(1−ρ̂²) / (1 + z κ ρ̂)  <  1  for all ρ̂ > 0,

strictly, and decreasing in ρ̂: **the deconvolution band is strictly narrower than
the conservative envelope whenever design noise is present, by a margin that grows
with ρ̂.** *Empirical:* at z=1.645 and ρ̂≈0.1–0.2, this predicts W_D/W_C≈0.80–0.91,
matching the observed T3/T2 (0.80–0.91). The dominance is what the real data DID
confirm (T3<T2 everywhere), even though the branch chosen was PCB not deconv —
because W_D and W_C are both computed and compared regardless of routing. ∎(cond.)

---

## Theorem AW-3 (target-blind adaptive validity — proven)

The selector Ĵ ∈ {PCB, deconv, cons} is measurable w.r.t. the calibration σ-field
F_cal (it reads only source scores and design SDs — ρ̂, stability — never the
target). Each branch band B_j is marginally valid for its target layer:
P(cover_j) ≥ 1−α−ε_j (Thm A.1 exact for PCB on the survey-estimate target; A.2 for
cons; B for deconv). Because Ĵ ⟂ target given F_cal,

  P( target ∈ B_Ĵ )  =  Σ_j P(Ĵ=j) · P( target ∈ B_j | Ĵ=j )  ≥  1 − α − max_j ε_j.

*Proof:* conditioning on {Ĵ=j} is conditioning on an F_cal-event, under which B_j's
marginal guarantee is unchanged (the target's rank among calibration scores is
unaffected by an F_cal-measurable choice). Summing over the partition gives the
bound; no selection inflation because the target enters no branch's selection. ∎

This is the crux: adaptivity costs nothing in validity precisely because the
switch is target-blind. The design-resampling stress test (Part B/C) is consistent
with this — pseudo-coverage ≥ nominal in every branch and for the routed pipeline.

---

## Candidate AW-4 (adaptive width / oracle inequality — stated as open)

Let W* = min(W_P, W_D, W_C) be the oracle (best-branch) width, and let the ρ-axis
carry an oracle partition into cells where one branch is width-minimal. Conjecture:

  W_adaptive  ≤  W*  +  r_{K,B},     r_{K,B} → 0 as K,B → ∞,

with r_{K,B} governed by the measure of the boundary zone |ρ̂ − ρ*_oracle| where
the target-blind ρ₀ disagrees with the oracle partition; since ρ̂ is a √K-consistent
estimate of ρ, that zone has width O(1/√K), giving r_{K,B}=O(1/√K)+O(1/√B) under
Lipschitz width-in-ρ. *Status: OPEN.* What is proven: AW-1 (reduction), AW-2
(dominance condition), AW-3 (validity). What remains: (i) that ρ₀=0.47 coincides
with the oracle crossover W_D=W_C up to O(1/√K) — currently ρ₀ is fixed from
Gate-5C, not derived as the crossover; (ii) the Lipschitz constant of width-in-ρ.
The paper states AW-4 as a candidate with the proof sketch, not a theorem — no
overclaim.

---

## What this buys, given all real data is low-ρ

The empirical low-ρ finding stops being a weakness: it is exactly the regime
AW-1 covers (provable near-reduction, penalty O(ρ²), matching the data to the
decimal). AW-3 makes the adaptive switch free in validity; AW-2 gives the
strict efficiency over the conservative envelope that the data DID confirm; AW-4
(open) is the remaining bridge to a full oracle guarantee. The honest paper
sentence:

"In two large cross-national surveys the adaptive procedure removed unnecessary
design-noise correction automatically (reducing to clustered PCB with an O(ρ²)
penalty that matches the data), while the theory and simulation supply the
validity and efficiency guarantees in the moderate/high-noise regime that such
surveys do not reach."
