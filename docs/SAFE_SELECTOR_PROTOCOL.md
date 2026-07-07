# Gate 5E — safe-adaptive selector protocol (fixed BEFORE results)

Status: 2026-07-06, committed before running `e21_safe_selector.py`. The finite-K
correction (E20) lifted the deconvolution but left ~0.82 coverage at K=30 high-ρ.
That residual is NOT declared solved. Gate 5E gives the DEPLOYED pipeline a
finite-K safety guarantee by separating three questions the old selector conflated:

> **can we use deconvolution · do we need it · can we SAFELY use it at this K?**

The old selector checked the first two. The safe selector adds the third and
abstains (falls back conservatively) when the answer is no — abstaining at small
K is honest inference, not defeat.

## Safe selector (fixed)

Per target, from source calibration ONLY, activate the deconvolution branch iff
ALL hold:

- **A. need:** ρ̂_LCB > ρ₀, where ρ̂_LCB is a one-sided lower confidence bound on
  ρ (design noise confidently matters). ρ̂_LCB = √( [mean_c v̂²−z·SE]_+ / s_plug²_UCB ),
  s_plug²_UCB = s_plug²(1+z√(2/(K−1))), z=1.645.
- **B. safety:** the deconvolution reliability diagnostic
  D = max_t SE(ŝ_T,safe²(t)) / ŝ_T,safe²(t) ≤ τ, where SE(ŝ_T²) =
  √( 2 s_plug⁴/(K−1) + (SD_c v̂²)²/K ). τ is calibrated ONCE on a simulation
  calibration grid (known truth) as the largest threshold for which D ≤ τ implies
  safe-deconvolution coverage ≥ the floor 1−α−δ, δ=0.02 (floor 0.88). Fixed
  thereafter; evaluated on a DISJOINT grid (different seeds).
- **C. stability:** s_plug² − mean(v̂²) > floor (deconvolution well-defined).
- **D. worth it:** width(safe-deconv) ≤ (1−m)·width(conservative), m=0.05 minimum
  improvement.

Otherwise: ρ̂_LCB ≤ ρ₀ → clustered PCB; else → conservative fallback. Both
non-deconvolution branches over-cover the latent target (Thm 0/A.2), so the
pipeline can only undercover through the deconvolution branch — which B gates to
coverage ≥ 0.88.

## Calibration discipline (fixed)

τ and δ are calibrated on the simulation CALIBRATION grid with KNOWN truth, then
FROZEN and evaluated on a disjoint EVALUATION grid. This is method design on
synthetic data (like choosing a regularizer), NOT peeking at real-data outcomes.
ρ₀=0.47, α=0.10 unchanged. No post-hoc changes to τ/δ after the evaluation grid.

## Safe-adaptive validity theorem (to state)

  P( F_{new,r}(t) ∈ B̂_safe(r,t) ∀ r,t ) ≥ 1 − α − δ,

finite (K,B), where δ is the preregistered tolerance AND the observable gate
guarantees the deconvolution is used only where its estimated remainder ≤ δ. δ is
computable from data (D, K, B, the noise-law error). Stated for the FULL selector,
not per branch.

## Success criteria (fixed BEFORE results, evaluation grid)

1. Coverage ≥ 0.88 (compatible with nominal 0.90 given MC error) in EVERY main
   cell including K=30 high-ρ — via fallback where needed.
2. Low-ρ width ≤ 1.05 × PCB (reduction preserved).
3. Moderate/high-ρ with SUFFICIENT K: safe-deconv activates and is materially
   narrower than conservative.
4. Unsafe deconvolution (small K, high ρ) ALWAYS routes to conservative/PCB.
5. No τ/δ/ρ₀ change after results.

## Deliverables

`pcb/inference/design_aware.py` (ρ̂_LCB, diagnostic D, safe selector),
`pcb/experiments/e21_safe_selector.py`, `results/safe_selector_grid.csv`,
`docs/SAFE_SELECTOR_RESULTS.md`, `docs/THEORY_MAIN.md` update (Thm 3 → safe-
adaptive validity), `figures/safe_selector_grid.png`.
