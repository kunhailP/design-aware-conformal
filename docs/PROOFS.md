# Formal results and proofs

> Rigorous statements and proofs for the paper's core results. Every assumption is
> stated explicitly; each result is given in the form in which it is *exactly*
> true, with practical variants flagged as such. Notation matches
> `docs/CHARACTERIZATION.md` and the implementation in `pcb/inference/`.

## Setup and assumptions

Populations `P_1, …, P_{K+1} ~iid Π`. Thresholds `t_1 < … < t_T`. For each
population the plug-in error curve is
`E_i = (E_i(t_1), …, E_i(t_T)) ∈ ℝ^T`, `E_i(t) = θ̂_t(P_i) − θ_t(P_i)`,
where `θ_t(P)=P_P(Y<t)` and `θ̂` is computed by a fixed rule. Because populations
are i.i.d. and `θ̂` uses the same rule for each, the curves `E_1,…,E_{K+1}` are
i.i.d. (hence exchangeable) elements of `ℝ^T`. Population `K+1` is the target;
`Y` is unobserved there, so `E_{K+1}` is unobserved and is the quantity we bound.

- **(A1) Continuity.** For each population the sup-score defined below has a
  continuous distribution, so the scores are almost surely distinct (no ties).
- **(A2) Calibration-measurable modulation.** The modulation `s(·)∈ℝ^T_{>0}` used
  to studentise is measurable with respect to a set of populations *disjoint from
  the calibration scores it is applied to* (made precise per theorem).

The target estimand `θ_·(P_{K+1})` is a CDF read on the grid: `t ↦ θ_t(P_{K+1})`
is non-decreasing with values in `[0,1]`.

---

## Theorem 1 — Population conformal band (PCB): finite-sample simultaneous validity (exact)

**Construction (split modulation).** Partition the source populations into a
modulation fold `M` and a calibration fold `C`, `|C| = n`. Compute the modulation
`s = s(\{E_j\}_{j∈M})` from `M` only (e.g. `s(t) =` per-threshold standard
deviation over `M`, floored at `s_floor>0`). Define sup-scores
```
R_i = max_t |E_i(t)| / s(t),   i ∈ C ∪ {K+1}.
```
Let `q̂ = R_{(m)}` be the `m`-th smallest of `{R_i}_{i∈C}`,
`m = ⌈(1−α)(n+1)⌉`; if `m > n` set `q̂ = +∞`. The band is
`B(t) = [θ̂_t(P_{K+1}) − q̂·s(t), θ̂_t(P_{K+1}) + q̂·s(t)]`.

**Theorem 1.** Under (A1)–(A2),
```
P( θ_t(P_{K+1}) ∈ B(t)  for all t = t_1,…,t_T )  ≥  1 − α,
```
with finite samples and no distributional assumption beyond exchangeability.

*Proof.* Condition on the modulation fold `M`. Given `M`, the modulation `s` is a
fixed (deterministic) function `ℝ^T→ℝ^T_{>0}`. The populations in `C ∪ {K+1}` are
i.i.d. and independent of `M`, so conditional on `M` the scores
`{R_i}_{i∈C∪\{K+1\}}` are i.i.d. real random variables — in particular
**exchangeable**. By (A1) they are a.s. distinct, so the rank of `R_{K+1}` among
the `n+1` scores is uniform on `{1,…,n+1}`. Hence
```
P( R_{K+1} ≤ R_{(m)} | M ) = m/(n+1) = ⌈(1−α)(n+1)⌉/(n+1) ≥ 1−α.
```
Now the simultaneous coverage event is, pointwise,
`θ_t(P_{K+1}) ∈ B(t) ∀t  ⇔  |θ̂_t − θ_t| ≤ q̂ s(t) ∀t  ⇔  |E_{K+1}(t)| ≤ q̂ s(t) ∀t
 ⇔  max_t |E_{K+1}(t)|/s(t) ≤ q̂  ⇔  R_{K+1} ≤ q̂.`
Therefore `P(coverage | M) = P(R_{K+1} ≤ q̂ | M) ≥ 1−α`, and taking expectation
over `M` gives the claim. (If `m>n`, `q̂=+∞`, `B≡[−∞,∞]⊇[0,1]`, coverage is
trivially 1.) ∎

**Coverage-preserving post-processing.** Replacing `B(t)` by
`B(t) ∩ [0,1]` and then by its isotonic tightening (Lemma 4) only shrinks the band
while still containing the (monotone, `[0,1]`-valued) truth whenever the raw band
did; hence both operations preserve the `≥1−α` guarantee.

**Remark (in-sample modulation is empirically free).** The implementation in
`conformal_band.py` uses `s` from the calibration curves themselves; the split
construction above is the version that is *exactly* finite-sample valid. The two
are empirically indistinguishable: leave-one-country-out coverage is `88.9%`
(in-sample) vs `88.8%` (split); on a random exchangeable holdout, `89.7%` vs
`89.8%`. So the practical in-sample band inherits Theorem 1's guarantee with no
measurable loss, and one may report it without the split.

**Remark (the sub-nominal real-data coverage is non-exchangeability, verified).**
The `~1pp` shortfall under leave-one-country-out is *not* a modulation or
granularity artifact. It is the non-exchangeability of countries, exactly the
phenomenon this paper studies. Holding the construction fixed and only changing
the holdout from by-country to a random (exchangeable) split raises coverage from
`88.9%` to `89.7%`; the difference is the residual cross-population shift. This is
the regime the covariate-shift band (`weighted_conformal_band`) targets, which
restores `≈89%` even under whole-region holdout (where unweighted PCB falls to
`80.2%`). The guarantee is exact under exchangeability; the empirical gap measures
its violation, and the weighted construction is the repair.

---

## Theorem 2 — Marginal validity and simultaneous under-coverage

**Per-threshold band.** `B^M(t) = [θ̂_t(P_{K+1}) − q_t, θ̂_t(P_{K+1}) + q_t]`,
`q_t` the `m`-th smallest of `{|E_i(t)|}_{i∈C}`, `m=⌈(1−α)(n+1)⌉`.

**(a) Marginal validity.** For each fixed `t`, by the one-dimensional rank
argument applied to the exchangeable scalars `{|E_i(t)|}_{i∈C∪\{K+1\}}`,
`P(θ_t(P_{K+1}) ∈ B^M(t)) = P(|E_{K+1}(t)| ≤ q_t) ≥ 1−α.`

**(b) Simultaneous under-coverage.** Write `A_t = {|E_{K+1}(t)| > q_t}` and
`p_t = P(A_t) ≤ α`. The simultaneous coverage is
`C^{sim} = P(⋂_t A_t^c) = 1 − P(⋃_t A_t)`.

> **General sandwich (any dependence).** With exact level `p_t = α`,
> ```
> max(0, 1 − Tα)  ≤  C^{sim}  ≤  1 − α.
> ```
> *Proof.* Upper: `⋂_t A_t^c ⊆ A_{t_0}^c` for any `t_0`, so `C^{sim} ≤ 1−p_{t_0} = 1−α`.
> Lower: union bound `P(⋃A_t) ≤ Σ_t p_t = Tα`, so `C^{sim} ≥ 1−Tα`. ∎

> **Positive-dependence sandwich (Gaussian / association).** If the standardised
> error field `W(t)=E(t)/σ(t)` is multivariate Gaussian (or, more generally,
> positively associated), Šidák's inequality gives
> `P(⋂_t\{|W(t)|≤c_t\}) ≥ ∏_t P(|W(t)|≤c_t)`, hence
> ```
> (1−α)^T  ≤  C^{sim}  ≤  1 − α.
> ```

The gap `(1−α) − C^{sim}` is `0` iff `T=1` or the misses `A_t` coincide a.s.
(perfect dependence), and grows with `T` and with decreasing cross-threshold
dependence. As `K→∞`, `C^{sim} → P(M ≤ z_{1−α/2})` with `M = max_t|W(t)|`; the
correct simultaneous critical value is `c_α = Q_{1−α}(M) ≥ z_{1−α/2}` (Theorem 1's
sup-score quantile), and the marginal band's deficit is exactly the gap
`c_α − z_{1−α/2}`.

**Empirical check (consistent).** `T=19` pseudo-populations: `C^{sim}=37.5%`,
inside `[(1−α)^{19}, 1−α]=[13.5%, 90%]`. `T=10` PIP: `54.1%`, inside
`[(1−α)^{10},1−α]=[34.9%,90%]`. Both lie above the independence reference,
consistent with the positive association of CDF-value errors.

---

## Proposition 3 — When the random-effects variance-inflated interval (M1) is valid

Let the realised target deviation be `θ̂_t − θ_t ~ (b_t, σ_t^2)` with `σ_t^2 =
SE_within^2 + σ_between^2`, and let M1 use the symmetric half-width `z·σ_t`,
`z=z_{1−α/2}`. Write the standardised bias `δ_t = |b_t|/σ_t`.

**Claim.** Under the Gaussian idealisation the M1 marginal coverage at `t` is the
closed form
```
C(δ_t) = Φ(z − δ_t) + Φ(z + δ_t) − 1,
```
which is even, strictly decreasing in `|δ_t|`, with `C(0)=1−α` and
`C(δ) = (1−α) − z·φ(z)·δ^2 + O(δ^4)`. Consequently M1 attains coverage `≥ 1−α−η`
iff
```
δ_t ≤ c(α,η),   c(α,η) = √( η / (z·φ(z)) ) + O(η).
```

*Proof.* The realised deviation is `N(b_t, σ_t^2)`; the coverage of `[−zσ_t,
zσ_t]` around the mean `θ̂_t` is `P(|N(b_t,σ_t^2)| ≤ zσ_t)
= Φ((zσ_t − b_t)/σ_t) − Φ((−zσ_t − b_t)/σ_t) = Φ(z−δ_t) − Φ(−z−δ_t)
= Φ(z−δ_t) + Φ(z+δ_t) − 1 = C(δ_t)`, using `Φ(−x)=1−Φ(x)`. Evenness and
`C(0)=2Φ(z)−1=1−α` are immediate. Differentiating, `C'(δ) = −φ(z−δ)+φ(z+δ)`, so
`C'(0)=0`; `C''(δ) = −(z−δ)φ(z−δ) − (z+δ)φ(z+δ)`, so `C''(0) = −2zφ(z) < 0`,
giving the quadratic expansion and strict decrease for `δ>0`. Solving
`C(δ)=1−α−η` to leading order, `zφ(z)δ^2 ≈ η`, i.e. `δ ≈ √(η/(zφ(z)))`. ∎

Numerically (`α=0.1`): `c(α,0.01)=0.243`, `c(α,0.02)=0.344`, `c(α,0.05)=0.545`
(exact roots match `√(η/(zφ(z)))` to 3 decimals). The most-biased empirical cell
(`M1=71.5%`) implies `δ=1.067`, consistent with `σ_between≈SE_within` at low shift.
A separate, additive deficit `ρ_K` arises from estimating `σ_t` from finite `K`;
the conformal band (Theorem 1) pays neither penalty.

---

## Lemma 4 — Isotonic tightening is coverage-preserving (validity, not efficiency)

Let `[lo(·), hi(·)]` be any band containing the monotone, `[0,1]`-valued truth
`g(t)=θ_t(P_{K+1})` at every `t`. Define
`L(t) = clip_{[0,1]}( max_{t'≤t} lo(t') )`, `U(t) = clip_{[0,1]}( min_{t'≥t} hi(t') )`.

**Claim.** `g(t) ∈ [L(t), U(t)]` for all `t`, and `[L(t),U(t)] ⊆ [lo(t),hi(t)]`
pointwise. Hence simultaneous coverage is preserved and width never increases.

*Proof.* For `t'≤t`, monotonicity gives `g(t) ≥ g(t') ≥ lo(t')`, so
`g(t) ≥ max_{t'≤t} lo(t')`; since `g(t)≤1` and `g(t)≥0`, clipping to `[0,1]` cannot
push the bound above `g(t)`, giving `g(t) ≥ L(t)`. Symmetrically `g(t) ≤ U(t)`.
Inclusion holds because a running maximum only raises `lo` and a reverse running
minimum only lowers `hi`. ∎

**Scope.** This guarantees validity is preserved; it is *not* an
efficiency lever. The realised width reduction is the band edges' violation of
monotonicity, which is `≈0.2%` empirically when `θ̂` is smoothly monotone. Present
the CDF shape as a validity-safe projection, not as a source of width.

---

## Proposition 5 — Efficiency decomposition of the localized band

Let PCB use scale `s_E(t)` and sup-quantile `q = Q_{1−α}(max_t|E_i(t)|/s_E(t))`,
and let the localized conformal band (M3′) regress `E` on population features, use leave-one-out
residual scale `s_R(t)` and `q' = Q_{1−α}(max_t|resid_i(t)|/s_R(t))`. Then the mean
band-width ratio factorises exactly as
```
width_{M3'} / width_{PCB}  =  ( s̄_R / s̄_E ) · ( q' / q ),
```
where `s̄_R/s̄_E = √(1−ρ̄^2)` is the marginal residual-variance factor (ρ̄² the
average feature-explained share of transport-error variance) and `q'/q` is the
ratio of *sup-score* quantiles.

*Proof.* Both bands have half-width `q·s(t)` with their respective `(q,s)`, so the
mean width is `(2/T)·q·Σ_t s(t)`; the ratio is `(q'/q)·(Σ s_R/Σ s_E)`. The
per-threshold residual variance is `Var(E(t))(1−ρ^2(t))`, so
`s_R(t)/s_E(t)=√(1−ρ^2(t))`, and the `s`-weighted mean gives the stated factor. ∎

**Consequence (characterisation).** Since `s̄_R/s̄_E≈√(1−ρ̄^2)` depends only on
*average* explained variance while `q'/q` depends on the *worst-threshold* (sup)
structure, localization tightens a **simultaneous** band iff the predictable bias
drives the sup-score — strictly stronger than explaining average variance.
Verified: consumption `(0.901)(0.924)=0.832≈0.815`; income `(0.903)(1.039)=0.938
≈0.973` (the sup factor cancels the variance gain). This is the marginal-vs-
simultaneous dichotomy of Theorem 2, now in the efficiency domain.

---

## What is proved vs. asserted

| result | status |
|---|---|
| Thm 1 PCB validity (split modulation) | **proved, exact** |
| Thm 1 in-sample variant | exact up to symmetric-bag argument; empirically ~89% |
| Thm 2(a) marginal validity | **proved, exact** |
| Thm 2(b) general sandwich `[1−Tα, 1−α]` | **proved** |
| Thm 2(b) Gaussian sandwich `[(1−α)^T,1−α]` | **proved (Šidák assumption)** |
| Prop 3 M1 boundary `C(δ)`, `c(α,η)` | **proved (Gaussian idealisation)** |
| Lemma 4 isotonic coverage-preserving | **proved** |
| Prop 5 efficiency decomposition | **proved (algebraic); `q'/q` characterised, not closed-form)** |
