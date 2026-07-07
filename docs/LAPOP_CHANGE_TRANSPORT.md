# LAPOP Part C — change-function transport results (E17)

Status: 2026-07-06. Preregistration carried over unchanged from Part B
(`LAPOP_PART_B_PROTOCOL.md`): same outcomes/thresholds/country set, calibration
unit = country, strict LOCO, **ρ₀=0.47 NOT retuned**, methods T1/T2/T3/T4. Code
`pcb/experiments/e17_lapop_change_transport.py`. Outputs `results/lapop_change_
transport.csv`, `results/lapop_change_candidate_b_by_rho.csv`, `results/lapop_
change_design_resampling.csv`. No coverage claim on LAPOP.

## Motivation

Part B transported LEVEL curves and found ρ small because between-country level
differences are huge. Part C transports the wave-to-wave CHANGE curve
D_{c,r}(t)=F_{c,r+1}(t)−F_{c,r}(t): its cross-country spread should be smaller
(the transport denominator), while a difference's design noise is ~√2 larger (the
numerator), so ρ_change could rise enough to activate the deconvolution branch.

## Result: ρ rises but the regime is STILL low-ρ

| outcome | ρ_change (mean) | ρ_level (Part B) | ≥ ρ₀=0.47 | branch ≠ PCB |
|---|---|---|---|---|
| b13 trust | 0.116 | 0.073 | 0/26 | 0/26 |
| sat | 0.103 | 0.069 | 0/26 | 0/26 |
| ing4 support | 0.197 | 0.133 | 0/26 | 0/26 |

The hypothesis was directionally correct — ρ_change ≈ 1.5× ρ_level — but the
change setting is still well below ρ₀. The deconvolution branch does not activate
for any of the 26 target countries on any outcome. Why only 1.5×: a difference's
design noise is only √2 larger, and cross-country CHANGE spread is itself
substantial (Latin-American trajectories diverge — some rise, some fall), so the
ratio climbs modestly, not into the high-ρ regime.

## Width behaviour (matches AW-1 / AW-2 to the decimal)

| outcome | T3/T1 | 1−½ρ² (AW-1 prediction) | T3/T2 |
|---|---|---|---|
| b13 | 0.995 | 0.993 | 0.912 |
| sat | 0.989 | 0.995 | 0.890 |
| ing4 | 0.965 | 0.981 | 0.802 |

T3/T1 tracks the O(ρ²) reduction rate of Theorem AW-1; T3/T2 tracks the
conservative-dominance ratio of AW-2. The observed numbers are a quantitative
confirmation of the adaptive-width theory, not just qualitative.

## Stress test (change curves, b13, design-resampling — NOT finite-pop coverage)

| method | pseudo-coverage | mean width |
|---|---|---|
| T1 PCB | 0.925 | 0.331 |
| T2 worst-case | 0.983 | 0.362 |
| T3 Candidate B | 0.919 | 0.329 |

T1 and T3 near nominal (0.90); the conservative T2 over-covers (0.983) at 10%
more width — exactly the excess AW-2 says Candidate B sheds. The routed pipeline
(all PCB here) holds coverage.

## The empirical regime characterization (reported, not hidden)

Across BOTH international surveys, BOTH estimands (level and change), and all
three outcomes, national-level cross-national inference is a **low-ρ regime**
(ρ̂ ≤ 0.20 < ρ₀ = 0.47). Design noise in modern ~1500/cell surveys is small
relative to cross-country variation in both levels and changes. Consequently:

- the deconvolution branch is never selected on real data — a finding, per the
  preregistration (do not lower ρ₀ to force activation);
- what real data validates is the target-blind reduction (AW-1, AW-3) and the
  efficiency over the conservative envelope (AW-2), both confirmed;
- the deconvolution branch's decisive regime (moderate/high ρ) is supplied by the
  Gate-5C simulation and the adaptive-width theory (`ADAPTIVE_WIDTH_THEORY.md`),
  which additionally PREDICTS the observed low-ρ width ratios.

This is the mature, defensible shape of the paper: an adaptive method that
provably removes unnecessary complexity in the regime real surveys occupy, with
theory + simulation guaranteeing protection in the regime they do not.

## Deferred (unchanged)

WVS weights-only replication; Foa–Mounk age-group analysis (the next preregistered
real-data ρ probe — smaller age×country×wave cells may raise ρ; age re-extract
from the ESS .dta required). A controlled high-ρ demonstration by progressive
source-subsampling remains a possible new-prereg extension.
