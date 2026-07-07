# Independent validation preregistration (confirmatory, single-shot)

Status: **sealed 2026-07-06 before any holdout result.** Config
`configs/holdout_validation.yaml` (sha256 in `configs/holdout_seed_manifest.json`);
frozen method `docs/SAFE_SELECTOR_SPEC.md`; runner `pcb/experiments/
e22_holdout_validation.py`; output `results/holdout_safe_selector.csv`; writeup
`docs/HOLDOUT_VALIDATION_RESULTS.md`.

## Purpose

Confirm that the **frozen** nominal-safe selector — whose constants were set on the
development grid (`gate5d-finiteK-fix`) — attains nominal-safe coverage and adaptive
efficiency on a design it has never seen. This is a single-shot confirmatory study,
not a development loop.

## What is disjoint from development

- **K**: {25, 40, 80, 160, 320} vs development {30, 60, 120, 240}.
- **ρ**: {0.10, 0.25, 0.38, 0.43, 0.47, 0.51, 0.58, 0.72, 0.90}, dense at the ρ₀=0.47
  cutoff, vs development {0.10,…,1.80}.
- **DGP**: ten families (below); development used gaussian only.
- **Seeds**: master seed 20260706, per-cell `det_seed(master, family, K, ρ, rep)`,
  sealed in the manifest before running.

## DGP families (10)

gaussian · skewed_noise · heavy_tail_country · hetero_design_var · unequal_psu ·
unequal_weights · irregular_length · noise_misspec (reported design SD biased 25%
low) · weak_dep_rounds (AR1 φ=0.3) · strong_dep_rounds (AR1 φ=0.8). The latent
target covered is design-noise-free (the transport curve). noise_misspec
deliberately violates the correct-noise-law assumption to probe robustness.

## Primary metrics (per cell = family × K × ρ)

1. **Coverage vs the theoretical finite-K floor.** cover ≥ 1 − α − δ̂_UCB, where
   δ̂_UCB is the branch-appropriate remainder (0 for PCB/conservative; δ̂_UCB(D) for
   deconvolution), evaluated within Monte-Carlo 95% intervals.
2. **Nominal coverage & MC CI.** distance of coverage from 0.90 within MC error.
3. **Worst-cell coverage.**
4. **Efficiency:** low-ρ safe-width / PCB-width; deconvolution-eligible safe-width /
   conservative-width.
5. **Routing:** branch-activation and fallback rates by K and ρ.
6. **Selector regret:** excess width vs the ex-post best valid branch.

## Success criteria (fixed before results)

Primary (validity):
- **P1** Every cell's coverage is compatible with its finite-K floor 1−α−δ̂_UCB
  within a 95% MC interval (i.e. coverage + 1.96·MC-SE ≥ floor).
- **P2** Worst-cell coverage ≥ 0.86, and no *systematic* band of cells (a
  contiguous K×ρ region within a family) sits below 0.88 beyond MC noise.
- **P3** The four development transition cells' failure mode (coverage ~0.86 while
  deconvolution activates ~100%) does NOT recur: wherever coverage < 0.88, the
  selector must have routed predominantly to conservative/PCB, not deconvolution.

Efficiency:
- **E1** low-ρ (ρ̂_LCB ≤ ρ₀): safe-width ≤ 1.05 × PCB-width.
- **E2** deconvolution-eligible cells: safe-width ≤ 0.90 × conservative-width.
- **E3** deconvolution activation rises with K and is ~0 at small K / insufficient
  information (honest abstention, not a failure).

Robustness:
- **R1** noise_misspec and heavy-tail/skew/dependence families do not produce
  coverage below 0.86 via the deconvolution branch (the gates must catch them).

## Locked analysis rules (post-results)

After `e22` runs once, the following are immutable: gate constants (ρ₀, δ_max,
DUCB_A/B, g_min, Z_GAIN, stability floor), the DGP families and their parameters,
the K/ρ grids, the master seed, and the cell set. No cell is deleted; a failing
result is reported as-is. e22 asserts `sha256(config) == manifest.config_sha256`
before running, so a silent config edit aborts the run.

## Role of real data (ESS / LAPOP)

ESS and LAPOP results were already seen and are **not** confirmatory validation of
the frozen selector. They serve as (i) the political application, (ii) the low-ρ
regime characterization, (iii) confirmation that the selector reduces to clustered
PCB on real cross-national data. The frozen method's coverage/efficiency claims rest
on this independent simulation and the theorems, not on the real-data reanalysis.
