# LAPOP Part B — Candidate B transport validation protocol (fixed BEFORE results)

Status: 2026-07-06, committed before running `e16_lapop_transport.py`. Choices
(units, LOCO, methods, ρ rule, success thresholds) are fixed here per Gate-5D
discipline and NOT changed after seeing results. Part A (`LAPOP_EXTERNAL_
VALIDATION.md`) is frozen; this is a separate, cross-country transport problem.

## The one question Part B answers

When transporting a new country's political-attitude trajectory from other
countries, does Candidate B — which removes the source surveys' complex-design
error from the transport-score distribution — give a band that is **narrower than
the conservative worst-case yet still valid**, and that **reduces to ordinary
clustered PCB when the design effect is small**?

Two errors are separated for the first time here (Part A had only the second):

  F̃_cr(t) − F_cr(t)  =  [cross-country transport error]  +  [survey-design error].

## Calibration unit (fixed): ONE score per country

country-wave is NOT an independent calibration unit. Per country c:

  R̃_c = max_{r ∈ c's core years, t ∈ low core} |F̃_{c,r}(t) − μ^{(−c)}(t)| / σ(t),

with the cross-country transport center μ^{(−c)}(t) = mean of F̃ over all core
(country,year) cells EXCLUDING country c, and σ(t) the plug-in modulation
(`_modulation`). The max is over the country's rounds and the low-core
thresholds (the trajectory sup-score). Reduced to a (K, T_core) array for the
deconvolution machinery by taking, per threshold t, the round achieving the max
|deviation|: E_c(t) = signed deviation there, v_c(t) = design SD of F̃ at that
cell (stratified-PSU bootstrap on real STRATA/UPM/weight). Score = max_t |E_c|/σ.

## LOCO protocol (fixed)

For each target country c: its every wave and all its outcome information are
excluded from the transport center, the calibration scores, the ρ estimate, the
deconvolution/regularization, and the fallback decision. The target curve is used
only in the final width/stress evaluation. Method selection uses source
calibration data ONLY.

## Methods (fixed) — cross-country transport table (do NOT mix with Part A M3)

| tag | construction | code |
|---|---|---|
| T1 | clustered PCB on observed noisy scores (design-noise-ignoring baseline) | `da_studentized_band` with v_cal=0 |
| T2 | worst-case conservative design-aware band (envelope) | `da_worstcase_band` |
| **T3** | **Candidate B deconvolution band** (s_T²=s_plug²−mean v²) | `da_studentized_band` |
| T4 | target-blind adaptive fallback (rule below) | selector over T1/T2/T3 |
| Oracle | true-curve scores — SIMULATION ONLY (Gate 5C), never on LAPOP | — |

(Part A's M3 stratified-PSU band is a WITHIN-country survey-only method; it is
not a transport method and does not appear in this table.)

## ρ definition (fixed, SD ratio — unified project-wide)

ρ̂ = √(mean_c mean_t v_c(t)²) / s_pluḡ, an SD ratio of the design noise to the
observed transport-score scale (s_plug = modulation), computed from SOURCE
calibration only. This is the same SD-ratio convention as
`DESIGN_AWARE_THEOREM.md` and both prereg docs — never a variance share.

## Candidate B / fallback selection rule (fixed BEFORE results)

From source calibration only, per target:
- ρ̂ < ρ₀  → T1 (clustered PCB): the design effect is too small to bother.
- ρ̂ ≥ ρ₀ AND deconvolution stable (s_plug² − mean v² > floor, floor_frac=0.05)
  → T3 (Candidate B).
- ρ̂ ≥ ρ₀ AND unstable (would give negative/floored variance) → T2 (conservative).

ρ₀ = 0.47 taken from Gate-5C (SD-ratio units), fixed before seeing LAPOP. Not
retuned on LAPOP.

## Real-data evaluation (fixed): NO coverage claim on LAPOP

Report only: mean/max band half-width per method; **T3/T2 width ratio** (Candidate
B vs conservative); **T3/T1 width ratio** (vs clustered PCB); certification and
inconclusive-reclassification counts; all of these BY ρ tercile; fallback trigger
rate; low/high design-noise subgroup contrasts.

## Coverage support = three layers (fixed naming)

1. theorem (`DESIGN_AWARE_THEOREM.md`); 2. Gate-5C oracle simulation;
3. **design-resampling stress test** on LAPOP — explicitly NOT finite-population
coverage. Each country-year's full weighted estimate is fixed as pseudo-truth;
small subsamples are repeatedly drawn preserving the real STRATA–PSU structure;
each method's band (built from subsampled sources, LOCO) is checked for covering
the pseudo-truth target score. Reports pseudo-coverage + width, named as a stress
test, not coverage.

## Success criteria (fixed BEFORE results)

- **Low-ρ regime:** width(T3) ≤ 1.05 × width(T1) — reduces to clustered PCB.
- **Moderate/high-ρ regime:** width(T3) ≤ 0.90 × width(T2) — materially narrower
  than the conservative envelope. (The 1.05 / 0.90 thresholds are fixed here from
  the Gate-5C simulation magnitudes, not chosen to flatter LAPOP.)
- **Validity:** near-nominal pseudo-coverage in the design-resampling stress test
  and in Gate-5C simulation; the full pipeline (incl. fallback) does not
  undercover; unstable deconvolution always routes to T2.
- **Political meaning:** T3 keeps certifying clear changes, leaves design-noisy
  ambiguous changes inconclusive, and recovers some conclusions T2 over-abandons.

## Fixed carry-overs

Outcomes/thresholds identical to Part A (b13 trust, sat=5−pn4, ing4 support; low
cores t∈{1,2,3} / {1,2}). α=0.10. No new methods/outcomes/country filters added
after results. WVS stays weights-only; Foa–Mounk deferred (age re-extract).

## Deliverables

`results/lapop_transport_loco.csv`, `results/lapop_candidate_b_by_rho.csv`,
`results/lapop_design_resampling.csv`, `docs/LAPOP_CANDIDATE_B_RESULTS.md`,
`figures/lapop_width_by_rho.png`, `figures/lapop_candidate_b_vs_conservative.png`,
`figures/lapop_transport_certification.png`.
