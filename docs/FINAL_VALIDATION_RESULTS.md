# E33 — fresh sealed validation of the FINAL deployed pipeline

Motivation: the original holdout's sealed run (E22) scored a band the package
does not deploy, its failures motivated the U0/Theorem-5' redesign, and its
sealed config was lost — so the FINAL pipeline had never been evaluated on data
untouched by its own design process (referee point, accepted). E33 is that
evaluation: six DGP families disjoint from E22's ten, new K and rho grids,
fresh master seed frozen in the script before first execution, run once,
reported as produced. Script sha256 at each seal recorded in
`configs/final_validation_manifest.json`.

## Seal 1 (reported as produced, then diagnosed)

105/120 cells floor-compatible. All 15 failures in one family (ar2_rounds), at
ALL K including K=20 — impossible for a valid DGP, since the U0 anchor is exact
at any K for any exchangeable draw. Diagnosis: the GENERATOR normalized each
batch by its own sample SD, so the (1, L) target trajectory was scaled by the
SD of a single autocorrelated path while calibration used the pooled SD — an
exchangeability-violating asymmetry in the DGP, not a pipeline failure. Cells
preserved in `results/final_validation_seal1.csv`.

## Seal 2 (ar2_rounds normalization fixed to the analytic stationary SD; only
that branch changed — diff visible in the script's SEAL-2 AMENDMENT comment)

- **F1: 120/120 cells floor-compatible; worst cell 0.8783** (vs guarantee
  floors 1−α at K<94, 1−α−δ̂ at K≥94; 600 reps/cell, 2 MC-SE criterion)
- **F2: deconvolution activates in 0 draws below K=94** (algorithmic floor
  holds in practice as in theory); active only at K=250 (7 cells)
- Families: lognormal_country, ar2_rounds, scale_mixture, extreme_deff,
  corr_noise, long_traj; K ∈ {20,30,50,120,250}; rho_gen ∈ {0.15,0.35,0.55,0.75}

The seal-1 episode is itself evidence for the contract-test discipline: an
exact-at-any-K guarantee failing at K=20 immediately localizes the bug to the
generator. Output: `results/final_validation.csv`.
