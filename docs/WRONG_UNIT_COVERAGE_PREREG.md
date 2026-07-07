# Preregistration — Experiment B: the wrong-unit coverage collapse (Paper 2)

Written BEFORE running e28. Choices fixed; results reported exactly as produced.

## Purpose
Paper 2's thesis is that inference attached to the wrong unit over-detects. The paper
demonstrates this for *claims* (certification counts) but not yet for *coverage*. A
referee will ask: "why not just do per-round inference?" We answer with a clean,
ground-truth simulation showing that a band calibrated for round-level (or pointwise)
coverage covers the whole country *trajectory* far below nominal, while the
country-trajectory band holds — the direct analog of the marginal-collapse in the
companion poverty paper.

## Design (fixed)
- $K=30$ exchangeable calibration countries + 1 held-out target; $T=6$ thresholds;
  trajectory length $L \in \{2,4,6,8\}$. 4000 replicates per $L$; deterministic seeds
  (`det_seed`, salt `"e28_wrongunit"`).
- Each country's error tensor $E_c \in \mathbb{R}^{L\times T}$ is mean-zero Gaussian with
  Kronecker covariance: AR(1) across thresholds ($\rho_t=0.6$) $\otimes$ compound
  symmetry across rounds (off-diagonal $\rho_\ell=0.3$). Countries are exchangeable.
- All bands are UNSTUDENTIZED ($s\equiv1$) so the only thing that varies is the **unit of
  the nonconformity score**, isolating the multiplicity/unit effect.

## Methods (fixed)
1. **Marginal** — per $(\ell,t)$ two-sided conformal interval; trajectory covered iff all
   $L\times T$ points covered.
2. **Per-round** — per round $\ell$, sup-over-thresholds conformal band; trajectory covered
   iff all $L$ rounds covered.
3. **Trajectory (ours)** — one score per country, $\max_{\ell,t}|E_c[\ell,t]|$; conformal
   order-statistic band over the whole trajectory.

All at nominal $90\%$.

## Pre-registered prediction
Trajectory band $\approx 0.90$ for every $L$ (finite-sample exact). Per-round coverage
decreases with $L$ (roughly $0.9^L$, milder under cross-round correlation). Marginal is
lowest. If the trajectory band does NOT hold nominal, or per-round does NOT decline with
$L$, report as produced and revise the claim.

## Frozen constants
$\alpha=0.10$; $K=30$; $T=6$; $\rho_t=0.6$; $\rho_\ell=0.3$; reps 4000; $L$-grid above.
