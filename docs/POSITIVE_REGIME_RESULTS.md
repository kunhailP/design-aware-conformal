# E31 — the positive regime: where the design-aware correction pays

Status: run 2026-07-17, deterministic (det_seed, master 20260718). Output:
`results/positive_regime.csv`. Run: `python -m pcb.experiments.e31_positive_regime`.

## Design

MRP-style small-area DGP (e29 'mrp', rescaled to sig=0.1): latent area curves =
shared area effect + threshold pattern; known heteroskedastic posterior SDs
(gamma across areas), observed E = R + xi. The FROZEN deployed pipeline (`dapcb`,
Theorem 5' α-budget architecture, α=0.10) is scored against the latent area curve.
Grid: K ∈ {60, 94, 150, 220, 300} × posterior-noise ratio ∈ {0.3, 0.5, 0.7, 0.9},
800 reps/cell.

## Findings

1. **Feasibility ≠ profitability.** Gate B is feasible from K=94, but with the
   deconvolution branch honestly budgeted at α_dec = max(0.1α, 3/(K+1)) its
   conformal quantile is informative — and the width-gain gate clears — only from
   K≈220. The practical activation frontier is K≈200–300.
2. **Where it fires, it pays.** At noise ratio 0.7: activation 31% of draws at
   K=220, 98% at K=300; deployed width 0.69–0.74× the conservative envelope at
   coverage 0.98–1.00 (floor 0.88). Worst active-cell coverage 0.975.
3. **The stability gate abstains correctly** at noise ≥ 0.9 (design noise ≈
   between-area signal): the deconvolved scale hits its floor and the pipeline
   returns the conservative envelope, which saturates toward the vacuous band —
   the honest answer in that corner.

## Note on the α_dec floor

The original flat budget α_dec = 0.1α made the deconvolution quantile index
⌈(1−α_dec)(K+1)⌉ exceed K for 94 ≤ K ≤ 99 (infinite radius) and sit at the
sample maximum until K≈200 — the branch was dead exactly where its gate first
opens. The 3/(K+1) floor (a function of K only, hence frozen; validity unchanged
by the union bound) repairs this; it was found by this experiment and is
disclosed in the paper's Theorem 5' statement.
