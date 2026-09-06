# Proof audit — what each result assumes, what each step uses, what pins it

Purpose: a checklist the author can work through by hand before submission
(and again before an R&R), one result at a time. For every theorem-like
statement in `paper/supplement.tex` it lists (1) the assumptions the proof
actually consumes, (2) the steps that carry the argument, each reduced to
the inequality or identity to verify, (3) what is imported from a standard
tool or from another result in the paper, (4) the contract test that
exercises it, and (5) status. "Hand-check" items are the ones worth doing
with pen and paper; each takes minutes, not hours.

Notation is the supplement's: $G$ latent deviation, $S$ design error,
$\tilde G=G+S$ observed, $W$ the shape process of (A1), $Y_c$ the raw
observed curve (normalized $\mu\equiv0$), $\bar Y$, $\bar Y_{-c}$ the
transport-center means.

## Assumptions (supplement, §S1, Theorem 4′ block)

| tag | content | consumed by |
|---|---|---|
| exchangeability | countries' observed trajectory laws symmetric | Thm 2(a), Thm 3, Prop S1, Thm 5′ first clause |
| (A1) scale family | $\tilde G_c=\sqrt{s_R^2+v_c^2}\,W_c$, $G_{K+1}=s_R W_{K+1}$, $W$ i.i.d., $EW=0$, $EW^2=1$, $0<s_{\min}\le s_R\le s_{\max}$ | Thm 2(c), Thm 4′, Prop S2, Prop S3, Lemma dominate |
| (A2) anti-concentration | density $\le L$ near the relevant quantile for $M=\max_t\|W\|$ and for $R^{\rm lat}=\max_t s_R\|W\|$; observed score puts mass $\ge\eta$ on each side within $\delta$ | Thm 4′(ii) middle term, Prop S2, Prop S3, Lemma orderstat |
| (A3) moments/bounded/bootstrap | finite fourth moment, curves bounded, unbiased size-$B$ bootstrap | Thm 4′(ii) scale-error term, Hoeffding steps in Props S2–S3 |
| independence across countries | for Thm 2(b)'s anti-concentration step only | Thm 2(b) rate remarks |

## Results

### Theorem 1 (non-identification; no uniform improvement)
- Assumes: curve-level additive model, class $\mathfrak S$ containing $\delta_0$ and closed under one symmetric convolution.
- (i) Hand-check: $\mathcal L_G*\mathcal S=\mathcal L_G'*\mathcal S'$ with $\mathcal L_G'=\mathcal L_G*\mathcal N$, $\mathcal S=\mathcal S_0*\mathcal N$ — one line of associativity/commutativity of convolution.
- (ii) Hand-check: on $S\equiv0$ the plug-in radius is the conformal order statistic; any measurable radius $\hat\rho\le\hat q_{\rm plug}$ valid at $1-\alpha$ can shave at most the discreteness slack $s_K$; randomized smoothing attains it. Uses only the conformal rank identity.
- Status: proved; standard ingredients, the contribution is the framing. Test: `test_theorem0.py`.

### Theorem 2 (oracle validity)
- (a) conformal rank identity on $\{\tilde R_c\}$. Test: `test_unstudentized_exchangeability.py`.
- (b) Hand-check: $\{R>\hat q\}\subseteq\{\xi<-u\}\cup\{\tilde R>\hat q-u\}$ with $\xi=\tilde R-R$ — no centring of $\xi$ used; $|\xi|\le\|S\|_\infty$ is the sup-norm triangle inequality.
- (c) under (A1): scale identity $s_T^2=s_{\rm plug}^2(1-\rho^2)$ coordinate-wise; exactness from Thm 4′(i).
- Rate remarks ($\sigma_\xi^{2/3}$, $\sigma_\xi\sqrt{\log}$): heuristic optimisation of $u$; not used by any other result. Bimodal remark: `test_latent_target_bridge.py`.
- Status: (a),(b),(c) proved; rates are remarks.

### Theorem 3 (exact finite-$K$ anchor, symmetric centres)
- Hand-check: the four symmetric-centre cases keep $(\tilde R_1,\dots,\tilde R_{K+1})$ exchangeable; coverage $\iff$ rank event; tie-breaking never anti-conservative; $\hat q=\infty$ convention when $m>K$.
- Status: proved. Tests: `test_fixed_length_exchangeability.py`, `test_unstudentized_exchangeability.py`.

### Proposition S1 (LOO deployment, survey-estimate target)
- Hand-check (two identities, five lines): $e_i=\tfrac{K+1}{K}(X_i-\bar X_+)$; $\|e_{K+1}\|=R^*$ exactly; $\|e_c\|\le a_c+R^*/K$ via $\tfrac{K+1}{K}\le\tfrac{K}{K-1}$ and the triangle inequality; then the rank argument gives $\hat q\ge R^*\tfrac{K-1}{K}$.
- Status: proved, distribution-free. Tests: `test_loo_validity.py::test_proof_identities_hold_exactly`, `::test_inflated_loo_band_meets_the_floor`.

### Lemma (order-statistic concentration) — new
- Hand-check: $Z_{(m)}>q+\delta\iff\hat F_K(q+\delta)<m/K$; $m/K\le1-\alpha+2/K$; $F(q+\delta)\ge1-\alpha+\eta$; one-sided DKW–Massart $\Pr(\sup(F-\hat F_K)>\varepsilon)\le e^{-2K\varepsilon^2}$. Mirror for the lower side with $F(q^-)\le1-\alpha$.
- Status: proved from a standard inequality. Consumed by Thm 4′(ii) and Prop S3 (replaces the earlier "binomial concentration" sentence).

### Theorem 4′ (estimated-law validity)
- (i) oracle scales: studentized scores are i.i.d. copies of $M$ (hand-check: $\max_t|\tilde G_c|/\sqrt{s_R^2+v_c^2}=\max_t|W_c|$ needs (A1) *coordinate-wise*, which is why the scale family must share the shape process).
- (ii) three terms: scale error $2Lq^*\delta_{K,B}$ (A2 density bound × relative scale perturbation), $\eta_{K,B}$ (Bernstein tails of the variance estimates, A3), $r_K$ (Lemma orderstat).
- Hand-check: the relative perturbation $\Delta_0(t)=\hat s_T(t)/s_R(t)-1$ needs $s_R\ge s_{\min}>0$ — now in (A1).
- (iii) one-sidedness of the guard: per-threshold statement only; the $1-T\alpha_2$ union bound is disclosed as weak at $T\approx10$–26. The main text says "on the guard event".
- Open: the constants $C_1,C_2$ are "obtainable", not displayed.
- Status: proved with explicit assumptions; constants undisplayed. Test: `test_estimated_law_validity.py`.

### Proposition S2 (LOO-centred deconvolution)
- Studentizer perturbation: exact identity $\hat s^{\rm loo}_{\rm plug}=\tfrac{K}{K-1}\hat s^{\rm raw}_{\rm plug}$ (hand-check: LOO deviations are $\tfrac{K}{K-1}$ times grand-mean deviations).
- Numerator perturbation: $|\tilde S_c-S_c|\le\zeta/\omega_0$, Hoeffding + union bound over $(K+1)T$ cells (needs A3 boundedness and $EW=0$; needs $\omega_0>0$, which (A1)'s $s_{\min}$ supplies).
- Status: proved. Test: `test_loo_validity.py::test_loo_centered_deconvolution_coverage`.

### Proposition S3 (LOO-centred anchors, latent target) — new
- Step 0: Lemma dominate on raw scores (below).
- Step 1 hand-check: $|a_c-\tilde R_c|\le\max_t|\bar Y_{-c}(t)|$ (sup-norm triangle inequality); a uniform score perturbation $\le\zeta$ moves any order statistic by $\le\zeta$.
- Step 2 hand-check: $\max_t|G_{K+1}-\bar Y|\le R^{\rm lat}+\max_t|\bar Y|$.
- Step 3: miss $\Rightarrow R^{\rm lat}>\hat q-2\zeta$ (uses $\tfrac{K}{K-1}\ge1$).
- Step 4: $\zeta\le C_3\sqrt{\log((K+1)T)/K}$ w.p. $1-O(K^{-1/2})$ (Hoeffding; same as S2).
- Step 5–6: window below $\hat q$; $R^{\rm lat}\perp\hat q$ under (A1); density bound on $\{|\hat q-q^\dagger|\le\delta\}$, Lemma orderstat off it.
- **Author decisions**: (A2) now names $R^{\rm lat}$ and the mass condition explicitly — accept, or restate (A2) for "every weighted sup $\max_t s(t)|W(t)|$ with bounded $s$".
- Status: proved under the stated (A2). Test: `test_loo_validity.py::test_loo_centered_anchor_latent_coverage` (bounded and Gaussian $W$; raw vs LOO on the same draws).

### Lemma (anchor domination under A1)
- Hand-check: $\sqrt{s_R^2+v_c^2}\ge s_R$ pointwise $\Rightarrow\tilde R_c\ge R^{\rm lat}_c$ for the coupled copy; order statistics preserve the coupling; conformal rank identity on the $K+1$ i.i.d. latent scores.
- Scope: raw-centred scores; the LOO deployment is Prop S3.
- Status: proved. Test: `test_anchor_domination.py`.

### Theorem 5′ (safe-adaptive validity)
- $K<94$: nested anchors ($B_{\rm clu}\subseteq B_{\rm con}$ because the conservative score dominates pointwise) + Thm 3 (or Prop S1 with the LOO centre) $\Rightarrow$ selection-free validity for T1. Hand-check the nesting lemma: miss of the selected band $\Rightarrow$ miss of $B_{\rm clu}$.
- $K\ge94$: union bound $\alpha_{\rm anchor}+\alpha_{\rm dec}+\varepsilon_{K,B}$ with the anchor term from Lemma dominate (raw) or Prop S3 (LOO, $+\gamma^{\rm anch}_K$, absorbed) and the deconvolution term from Thm 4′(ii) (+$\gamma_K$ of Prop S2, absorbed). No term conditions on $\hat J$.
- Status: proved given the cited pieces. Tests: `test_safe_selector.py`, `test_anchor_domination.py`, `test_deployed_path_coverage.py`.

### Proposition 2 (finite-$K$ feasibility) and the reliability-floor lemma
- (b) hand-check: $\hat s_T\le s_{\rm plug}$ $\Rightarrow$ $D\ge\sqrt{2s^4_{\rm plug}/(K-1)}/s^2_{\rm plug}=\sqrt{2/(K-1)}$; $K\ge1+2/\tau_D^2$; $\tau_D=(0.02-0.0061)/0.0943$ gives 94.
- Floor lemma: Lehmann–Scheffé at the Gaussian member for unbiased variance estimators; scope = unbiased class (the text now says so).
- Status: (b) deterministic identity; lemma proved in its class. Tests: `test_prop1_floor.py`, `test_feasibility_frontier`.

### AW-1 (low-$\rho$ reduction)
- What is proved: $W_D/W_P\to1$ as $\rho\to0$ (continuity); the oracle scale factor is exactly $\sqrt{1-\rho^2}=1-\tfrac12\rho^2+O(\rho^4)$.
- What is *not* proved: that the band ratio inherits the second-order expansion (a first-order $O(\rho)$ term in $q_D/q_P$ is not excluded). The main text no longer claims it.
- AW-2/AW-3 are conditional on stated first-order expansions; AW-4 is open (labelled).

## Hand-check list (order of payoff)

1. Prop S3 steps 1–3 (three inequalities).
2. Lemma orderstat (DKW both sides, the $2/K$ slack).
3. Thm 4′(i): why coordinate-wise (A1) is exactly what makes the studentized scores i.i.d.
4. Prop S1's two identities.
5. Lemma dominate's coupling.
6. Thm 5′ nesting: the two-line inclusion.
7. Prop 2(b): the $\sqrt{2/(K-1)}$ identity and the 94.
8. Thm 1(ii): the least-favourable member argument.
9. Thm 2(b): the one-line event inclusion.

Anything that fails a hand-check goes back into `paper/supplement.tex` and gets a
contract test before the statement is touched again.
