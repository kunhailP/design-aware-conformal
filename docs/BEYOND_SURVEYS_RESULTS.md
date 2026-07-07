# Results — Experiment C: the unreachability barriers hold beyond surveys (Paper 2)

Run via `pcb/experiments/e29_beyond_surveys.py`. Substantiates Remark `rem:general`.
Reported as produced. Output: `results/beyond_surveys.csv`.

## Barrier B — the reliability floor is distribution-free (median D; nominal τ_D=0.147)

| DGP | K=20 | K=30 | K=50 | K=94 | K=150 | K=300 | min D/floor | K\* (median D ≤ τ_D) |
|---|---|---|---|---|---|---|---|---|
| gaussian | 0.426 | 0.332 | 0.248 | 0.176 | 0.138 | 0.097 | 1.146 | 134 |
| t3 (heavy tail) | 0.505 | 0.375 | 0.273 | 0.191 | 0.146 | 0.101 | 1.155 | 149 |
| skew | 0.456 | 0.351 | 0.256 | 0.182 | 0.141 | 0.098 | 1.124 | 138 |
| **mrp (small-area)** | 0.380 | 0.308 | 0.236 | 0.172 | 0.136 | 0.096 | 1.061 | 129 |

- The floor $D \ge \sqrt{2/(K-1)}$ holds in **every** DGP (min $D/\text{floor} \ge 1.06$),
  including the non-survey MRP small-area setting — it is distribution-free.
- $K \ge 94$ is the floor-implied **necessary** minimum; the reliability gate actually
  opens only at $K \approx 130$–$150$ on concrete DGPs, so the barrier is if anything
  **stronger** than the headline $K \ge 94$.

## Barrier A — ρ saturation in the MRP setting (median ρ_LCB)

| signal / noise | ρ_LCB |
|---|---|
| 0.5 | 0.536 |
| 1.0 | 0.321 |
| 2.0 | 0.171 |
| 4.0 | 0.087 |

As the between-unit signal grows relative to the estimation noise, $\hat\rho$ saturates
below $\rho_0=0.47$ — the same mechanism as in surveys. But when posterior noise is
comparable to the between-area signal (ratio 0.5, $\hat\rho=0.54>\rho_0$), the need gate
**does** fire. So a many-area MRP setting with high posterior uncertainty can reach the
need gate that cross-national surveys never do — provided it also clears $K \approx 130$.

## Significance
The two barriers are not survey artifacts: the reliability floor and ρ saturation hold in
a non-survey, model-based small-area setting, so the impossibility/unreachability result
transfers to any conformal procedure calibrated on estimated objects. The experiment also
pinpoints where the method is **not** dead — many small areas ($K \gtrsim 130$) with
appreciable posterior noise — which is exactly the positive-result frontier the paper
identifies as future work.
