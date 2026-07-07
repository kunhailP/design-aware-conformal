# Design-preserving semi-synthetic regime experiment — protocol (fixed BEFORE results)

Status: 2026-07-06, committed before running `e18_semisynthetic.py`. This is
explicitly a **design-preserving semi-synthetic regime stress test**, NOT a
real-data high-ρ validation. Its job: show, on LAPOP's real STRATA/PSU/weight
structure, that as design noise grows the target-blind selector moves through
PCB → deconvolution → conservative fallback around the preregistered ρ₀, and that
the adaptive pipeline holds coverage throughout.

## Construction (fixed)

- Base data: LAPOP core change-transport setting (E17), the highest-ρ real
  regime, adjacent-core-wave change curves D_{c,r}(t), 26 countries, 3 outcomes.
- **Design-preserving subsampling:** within each country-year and each stratum,
  keep a fraction f of the UPMs (≥1), retaining all respondents in the kept PSUs
  and their weights. This shrinks n while preserving the multistage clustered
  design, so the design SD grows ~1/√f and ρ rises with 1/√f. **Pseudo-truth = the
  full-sample (f=1) estimate**; the transport center μ is the full-sample grand
  mean, fixed across fractions.
- **Fractions (fixed sweep, preregistered):** f ∈ {1.0, 0.5, 0.25, 0.125, 0.0625}.
  The 0.0625 step extends the advisor's {1,.5,.25,.125} example by one, fixed here
  BEFORE results, to ensure the sweep spans ρ₀ into the fallback regime. Not
  changed after seeing results.
- Replications: R = 30 independent subsample draws per fraction (design bootstrap
  B = 150 for v̂). Seeded.

## Fixed carry-overs (unchanged from Part B/C preregistration)

Outcomes b13/sat/ing4, low-core thresholds, adjacent-core pairs, calibration unit
= country, strict LOCO, **ρ₀ = 0.47 NOT retuned**, methods T1/T2/T3, fallback rule
(ρ̂<ρ₀→T1; ρ̂≥ρ₀ ∧ stable→T3; else T2). No new methods/outcomes.

## Recorded per fraction (fixed)

ρ̂ (mean, spread); selected-branch fractions (PCB / deconv / cons); pseudo-coverage
of the full-sample pseudo-truth by the adaptive pipeline and by each fixed branch;
mean adaptive width and conservative width; fallback (T2) trigger rate.

## Success criteria (fixed BEFORE results)

- ρ̂ increases monotonically as f falls (design-noise dial works).
- The selector transitions PCB → deconv → cons as ρ̂ crosses ρ₀ / the stability
  edge — i.e., the deconvolution branch DOES activate semi-synthetically.
- Adaptive pseudo-coverage stays ≥ nominal (1−α=0.90) across ALL fractions,
  including where deconv activates and where fallback triggers.
- Adaptive width < conservative width wherever deconv is chosen.

## Naming discipline (fixed)

Report as "design-preserving semi-synthetic regime experiment." Never
"real-data high-ρ validation," never a coverage claim about the finite population.
Deliverables: `results/lapop_semisynthetic.csv`,
`figures/semisynthetic_regime_sweep.png` (ρ on x-axis vs coverage / relative
width / selected-branch share).
