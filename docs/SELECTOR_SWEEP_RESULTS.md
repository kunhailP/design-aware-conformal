# Selector-transition sweep — results (E19, simulation, known truth)

Status: 2026-07-06. Code `pcb/experiments/e19_selector_sweep.py`, figure
`pcb/figures/fig_selector_sweep.py`, output `results/selector_sweep_sim.csv`.
Simulation with KNOWN truth (K=30 source countries, T_core=4, 1500 reps/level):
latent deviation curves E_c ~ N(0,s_R²), observed Ẽ_c = E_c + N(0,v²), v̂ estimated
with 15% error, target = a held-out LATENT curve (deployment, v_target=0). ρ dialed
via v/s_R. This is the ONE setting where the deconvolution regime is reachable and
coverage is real (not pseudo).

## Two things this sweep shows

### 1. The selector transitions correctly (the intended result)

| ρ̂ | PCB | deconv | conservative |
|---|---|---|---|
| 0.10–0.39 | 100% | 0% | 0% |
| 0.50 | 16% | 84% | 0% |
| 0.60 | 0% | 100% | 0% |
| 0.70 | 0% | 96% | 4% |
| 0.77 | 0% | 85% | 15% |
| 0.85 | 0% | 58% | 42% |
| 0.91 | 0% | 30% | 70% |

The target-blind selector moves PCB → deconvolution as ρ̂ crosses ρ₀=0.47, then
PCB=0 and the conservative fallback progressively takes over as the deconvolution
becomes unstable (ρ̂→1). The routing mechanism works exactly as designed.

### 2. The plain deconvolution UNDERCOVERS at finite K (honest limitation)

Coverage of the latent target:

| ρ̂ | PCB | deconvolution | adaptive (routed) |
|---|---|---|---|
| 0.10 | 0.87 | 0.86 | 0.87 |
| 0.39 | 0.92 | 0.86 | 0.92 |
| 0.50 | 0.94 | 0.86 | 0.86 |
| 0.60 | 0.97 | 0.84 | 0.84 |
| 0.70 | 0.98 | 0.74 | 0.77 |
| 0.77 | 0.99 | 0.61 | 0.75 |
| 0.85 | 1.00 | 0.46 | 0.84 |
| 0.91 | 1.00 | 0.30 | 0.92 |

PCB over-covers (Theorem 0/A.2: calibrating on the inflated observed scores is
conservative for the latent target — coverage → 1 as ρ grows). The **deconvolution
undercovers**, worsening with ρ, because s_T = √(s_plug² − mean v̂²) is a small
difference of large noisy quantities at finite K: it is under-estimated, inflating
the target's studentized score. The routed **adaptive** pipeline inherits the
undercoverage in the mid-ρ band (0.75–0.86 at ρ̂ 0.5–0.77) and only recovers at
very high ρ once the conservative fallback dominates.

This is a concrete measurement of Theorem 2's ε_{K,B}: at K=30 it is large in the
transition regime. It is NOT hidden — it is the honest finite-K behaviour of the
deconvolution estimator.

## Why this does not sink the paper (but must be stated)

- **Real data never reaches this regime.** ESS, LAPOP level, LAPOP change, and the
  design-preserving semi-synthetic sweep all stay at ρ̂ ≤ 0.23 (< the 0.47 where
  the deconvolution even begins to be chosen). On every real dataset the pipeline
  routes to PCB, which is exactly valid (Theorem 1a) / conservative (A.2). The
  undercoverage is a property of a branch that real cross-national inference never
  invokes.
- **The paper's protagonist is the impossibility + adaptive-reduction result**, not
  the deconvolution's finite-K performance. Theorem 0 says design information is
  necessary; the adaptive procedure uses it safely by reducing to PCB when the
  design effect is small (which, empirically, it always is at survey scale).

## Open methodological item (stated, not swept under)

The deconvolution branch needs a **finite-K coverage correction** to be valid when
actually invoked — either (i) a conservative confidence bound on s_T instead of the
plug-in difference, or (ii) a coverage-protective stability gate that routes to the
conservative fallback earlier (once s_T²/s_plug² drops below a preregistered
reliability margin), or (iii) a studentized-deconvolution quantile inflation
accounting for v̂ estimation error. This is a genuine next methodological step, to
be preregistered and re-validated — NOT tuned post hoc here. Until then the honest
claim is: deconvolution efficient and asymptotically valid; finite-K undercoverage
in the high-ρ regime; conservative fallback and (universally, in practice) the
low-ρ PCB reduction protect coverage on real data.
