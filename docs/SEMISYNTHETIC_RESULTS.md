# Design-preserving semi-synthetic regime experiment — results (E18)

Status: 2026-07-06. Preregistered in `SEMISYNTHETIC_PROTOCOL.md` (fixed before
results; ρ₀=0.47 not retuned, fractions fixed). Code
`pcb/experiments/e18_semisynthetic.py`, output `results/lapop_semisynthetic.csv`.
This is a **design-preserving semi-synthetic regime stress test**, NOT a real-data
high-ρ validation.

## Result: ρ SATURATES below ρ₀ — the deconvolution regime is unreachable even
## by aggressive design-preserving subsampling

LAPOP change-transport, UPMs subsampled within strata at fraction f (mean over 30
draws × 3 outcomes × 26 targets):

| f | ρ̂ | branch | adaptive cov | conservative cov | adaptive width | conservative width |
|---|---|---|---|---|---|---|
| 1.000 | 0.138 | 100% PCB | 0.923 | 0.965 | 0.301 | 0.336 |
| 0.500 | 0.183 | 100% PCB | 0.926 | 0.978 | 0.305 | 0.355 |
| 0.250 | 0.228 | 100% PCB | 0.933 | 0.985 | 0.314 | 0.376 |
| 0.125 | 0.232 | 100% PCB | 0.945 | 0.989 | 0.322 | 0.393 |
| 0.062 | 0.198 | 100% PCB | 0.959 | 0.985 | 0.339 | 0.391 |

ρ̂ rises from 0.14 to ~0.23 then **saturates and turns over** — it never approaches
ρ₀=0.47. The deconvolution branch does not activate at any fraction.

## Why ρ saturates (this is the substantive point, not an artifact)

The observed transport-score variance decomposes as

  s_plug²  =  s_R²  +  v̄²      (true between-country spread + design-noise variance).

Subsampling inflates the design noise v̄, but it inflates the observed between-
country spread s_plug in lockstep, so the SELECTOR's ρ̂ = v̄/s_plug =
1/√(1+(s_R/v̄)²) climbs only slowly and saturates; at the smallest fraction the
CDF estimates become so noisy that s_plug grows faster than v̄ and ρ̂ turns over.
ρ₀=0.47 corresponds to v̄²/s_plug² ≈ 0.22 — design noise being ~22% of the total
observed variance — a genuinely high-noise regime that AmericasBarometer's
clustering never reaches, even subsampled to 1/16 of its PSUs.

**Interpretation.** This is a stronger version of the Part B/C finding: not only is
real cross-national inference low-ρ, but the design-noise fraction cannot be
pushed into the deconvolution regime by shrinking these surveys — because the
observable transport scale absorbs the added noise. On survey-scale data the
deconvolution branch is effectively unreachable; it is a guarantee for regimes
(tiny samples, or design noise comparable to the true signal) outside modern
cross-national surveys.

## What DID hold across the whole sweep (validates AW-1/AW-3 on real design)

- **Adaptive coverage ≥ nominal at every fraction** (0.923–0.959 ≥ 0.90), on the
  real STRATA/PSU structure, as design noise triples.
- **Adaptive (=PCB here) is uniformly narrower than the conservative envelope**
  (width 0.30–0.34 vs 0.34–0.39), and the conservative band over-covers
  increasingly (0.965→0.989) — the excess AW-2 says Candidate B sheds.
- The target-blind selector never triggered an unnecessary correction — exactly
  AW-3's no-harm property, now stress-tested across a 3× design-noise range.

## The branch transition is shown in SIMULATION (E19), where noise is dial-able

Because neither real nor design-preserving-subsampled LAPOP reaches ρ₀, the
selector transition PCB → deconvolution → conservative-fallback cannot be
exhibited on this survey. It is shown in the simulation (`e19_selector_sweep.py`),
where the DGP's survey-noise is a free parameter and coverage is measured against
KNOWN truth. That sweep exhibits the transition AND honestly reveals a limitation:
at moderate/high ρ with finite K the plain deconvolution branch UNDERCOVERS (a
large ε_{K,B}, Theorem 2), because s_T=√(s_plug²−v̄²) is a noisy small difference —
see `SELECTOR_SWEEP_RESULTS.md`. This matters for theory but not for practice:
real cross-national inference never reaches that regime (this doc + Parts B/C), so
the deconvolution branch is never actually used on real data. Naming stays strict:
LAPOP = semi-synthetic regime stress test (this doc); simulation = transition +
the honest finite-K characterization.
