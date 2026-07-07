# Small-K base-band correction — preregistration (2026-07-07)

**Choices fixed BEFORE running the validation grid.** After the frozen holdout (E22)
exposed the honest shortfall — the *base* clustered conformal band undercovers at small
K under hard DGPs (worst cell 0.843, weak cross-round dependence at K=25) — we diagnosed
the mechanism on development DGPs and fix the correction here, before any validation
number is seen. Post-validation, nothing below changes; results are reported as produced.

## Diagnosis (development, mechanism only)

The deployed base band studentizes with an **in-sample pooled modulation**
`s(t)=SD_c E_c(t)` (variant "S2"): every calibration score `R_c=max_t|E_c(t)|/s(t)`
divides by an `s` that includes cluster `c` itself, while the *unobserved* target uses an
`s` fit without it. This breaks exchangeability between the calibration scores and the
target score — a finite-K self-inclusion deficit (Prop 3), worst at small K and long
trajectories L. Measured (4000 reps/cell): S2 coverage falls to 0.847–0.864 at K=25,
weak/strong dependence — reproducing the holdout 0.843.

## The correction (FIXED)

**Deploy the unstudentized clustered conformal band ("U0") as the base band.**
Nonconformity score per cluster is the sup absolute transport error, with no data-
dependent denominator:

> R_c = max_t |E_c(t)|  ;  q̂ = ⌈(1−α)(K+1)⌉-th order statistic of {R_c}  ;
> band = center ± q̂, then isotonic-tightened and clipped to [0,1].

**Guarantee (fixed claim).** Because R_1,…,R_K, R_target are exchangeable (each is a
function of its own cluster only, no shared data-dependent modulation), the standard
conformal / Vovk order-statistic bound gives, at ANY K, distribution-free:

> P(band covers the whole latent target curve) ≥ ⌈(1−α)(K+1)⌉/(K+1) ≥ 1−α.

No asymptotics, no DGP assumption. This is the correction: trade the in-sample
studentization (a small-K coverage deficit) for exactness at every K.

**Why U0, not the split-modulation "S1".** S1 is also exact but estimates `s` from half
the clusters and scores on the other half — wasting half of an already small K, giving
wider bands at K≈30. U0 uses all K clusters and is exact. (S1 remains available as an
efficiency option where K is large and per-threshold heteroskedasticity is severe; not
deployed here.)

## Validation grid (FRESH — new seeds, new K, run ONCE)

- K ∈ {15, 20, 25, 30, 40, 60} — dense at the small-K regime of interest, **disjoint
  seed salt** `"e25_smallk"` from the holdout.
- 10 DGP families (same generator as E22: gaussian, skewed_noise, heavy_tail_country,
  hetero_design_var, unequal_psu, unequal_weights, irregular_length, noise_misspec,
  weak_dep_rounds, strong_dep_rounds).
- ρ ∈ {0.10, 0.25} — the low-ρ regime where the base band is the deployed branch (higher
  ρ routes to deconvolution/conservative, validated separately in E22).
- α = 0.10; ≥ 2000 reps/cell. Report U0 and S2 side by side.

## Success criteria (FIXED before results)

- **C1 (exact validity):** every cell's U0 coverage ≥ the Vovk floor
  ⌈(1−α)(K+1)⌉/(K+1) minus 2 Monte-Carlo SE — i.e. no systematic deficit; U0 tracks its
  finite-sample guarantee.
- **C2 (closes the gap):** every cell's U0 coverage ≥ 0.88 for K ≥ 20 (vs S2's 0.843);
  and U0 ≥ S2 in every cell.
- **C3 (bounded width cost):** U0 mean half-width ≤ 1.10 × S2 across all cells; report the
  ratio exactly. (Development estimate 1.03–1.05; on real homoskedastic ESS, E10 found U0
  narrowest, so no real-data width penalty is expected.)

## Real-data application (FIXED)

Rerun the deployed `dapcb` base band on real ESS transport cells with U0 and confirm
(a) it still reduces correctly at the low real-data ρ, and (b) its width vs S2 on real
ESS. No political-headline threshold/country/outcome changes.

## Post-validation discipline

No change to the correction, the grid, the seeds, or the criteria after seeing results.
If C1–C3 hold, U0 is adopted as the deployed base band (documented as the post-holdout
correction); the frozen E22 holdout stays on the record as the evidence that motivated it.
If any criterion fails, report the failure and do not adopt.
