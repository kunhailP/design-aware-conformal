# Finite-K deconvolution coverage correction — protocol (fixed BEFORE results)

Status: 2026-07-06, committed before running `e20_safe_deconv.py`. E19 showed the
plain deconvolution undercovers at finite K in the high-ρ transition regime
because s_T² = s_plug² − mean(v̂²) subtracts an unreliable estimate. This fixes the
correction mechanism and its ONE constant from theory (an α-budget split), NOT by
fitting the observed coverage curve.

## Diagnosis (from E19, already seen)

PCB (no subtraction) is valid/conservative at all ρ. The undercoverage is caused
specifically by the **subtraction of mean(v̂²)** being too aggressive at finite K,
not by s_plug² (whose calibration variability the conformal quantile already
absorbs). Therefore the correction guards the SUBTRACTION only.

## The correction (fixed): conservative subtraction via a lower CI on mean(v²)

Replace the point subtraction mean(v̂²) with its one-sided LOWER confidence bound,
so we subtract LESS and the target scale is never smaller than warranted:

  ŝ_T,safe²(t) = max( s_plug(t)² − [ mean_c v̂_c(t)² − z_{α₂}·SE_c(t) ]₊ , floor ),

  SE_c(t) = SD_c( v̂_c(t)² ) / √K,   z_{α₂} = Φ⁻¹(1 − α₂),   α₂ = α/2.

- **α-budget split (the only design choice, fixed from theory):** allocate α₂ = α/2
  of the miscoverage budget to the scale-estimation CI and α₁ = α/2 to the
  conformal quantile (union bound). Even split — a principled default, NOT tuned to
  the coverage result. For α=0.10, z_{α₂} = Φ⁻¹(0.95) = 1.645.
- The safe scale is used consistently in both the calibration studentization
  √(ŝ_T,safe² + v²) and the deployment radius q·ŝ_T,safe.

## Key properties (why this is the right guard — predicted before running)

- **Reduces to PCB at low ρ (protects the real-data results).** As mean(v̂²) → 0
  (and its SE → 0), the subtracted term → 0, so ŝ_T,safe → s_plug and the band → the
  plug-in / clustered-PCB band. Real data (all ρ̂ ≤ 0.23, always routed to PCB
  anyway) is therefore unaffected; even the T3 width at low ρ stays ≈ PCB.
- **Never wider than PCB:** ŝ_T,safe ≤ s_plug always (we only subtract a
  non-negative amount), so the correction is an efficiency dial between full
  deconvolution and PCB — it never inflates beyond the honest plug-in.
- **Conservative at high ρ:** subtracting the lower CI instead of the point
  estimate leaves a larger target scale exactly where the point estimate was
  unreliable, lifting coverage.

## Success criteria (fixed BEFORE results)

1. Sim sweep (E20, same DGP as E19, KNOWN truth): safe-deconvolution and the
   routed adaptive-safe pipeline maintain coverage materially closer to nominal
   than the plain version across the transition regime (ρ̂ ∈ [0.47, 0.9]); ideally
   ≥ ~0.88 where plain fell to 0.75.
2. Low-ρ unchanged: at ρ̂ < ρ₀ the safe T3 width is within ~2% of PCB (reduction
   property preserved).
3. Report the coverage/width honestly whatever it is; if z_{α₂}=1.645 only
   partially fixes it, that is reported — NO retuning of α₂ after seeing results.
4. Real-data (LAPOP) certification/width results are unchanged (correction only
   affects the never-selected T3 branch; verified by re-running the low-ρ width).

## Deliverables

`pcb/inference/design_aware.py::deconv_target_scale` (+ unit test),
`pcb/experiments/e20_safe_deconv.py`, `results/safe_deconv_sweep.csv`,
`docs/FINITE_K_CORRECTION_RESULTS.md`, `figures/safe_deconv_coverage.png`.
