# WVS/EVS role redefinition — weights-only global replication (NOT design validation)

Status: 2026-07-06. Formalizes the decision (advisor, Gate 5D) to demote WVS from
primary external design validation to a global-generalization replication, after
the schema audit (`WVS_SCHEMA_AUDIT.md`) found NO PSU/stratum/replicate weights in
either WVS file. AmericasBarometer (`LAPOP_PREREGISTRATION.md`) becomes the
primary external **design** validation.

## Why WVS cannot carry design-aware validation

- WVS/EVS Trends and the EVS/WVS Joint provide survey weights (`S017`) and a
  region code (`X048`, NUTS) only. `X048` is an administrative region, NOT the
  sampling PSU: using it as a pseudo-PSU would neither reflect the true within-
  region sampling stages nor cluster sizes, and could over- or under-state the
  design variance. It cannot exercise Candidate B's known-survey-noise mechanism.
- Therefore any region-based design number on WVS is a **heuristic sensitivity
  analysis** for the appendix only, and must never be called design-valid
  inference, a PSU-aware band, or an empirical confirmation of Candidate B's
  design-variance recovery.

## The three-dataset identification split (each data source, one job)

| data | identification role | what it establishes |
|---|---|---|
| simulation (Gate 5C) | known truth | coverage / efficiency / naive≠proper divergence |
| ESS | primary political application | design-aware inference changes the substantive certification (Greece) |
| **AmericasBarometer** | **primary external design validation** | real UPM/STRATA: naive-vs-proper divergence, regime-adaptive B |
| WVS/EVS | global generalization | non-European, long-span trajectory replication (weights-only) |

## What WVS WILL do (permitted, weights-only)

- Unify the common trust item (`E069_07`, reverse-coded `trust = 4 − E069_07`) and
  satisfaction item (`E110`) direction/scale (4-category, 3 thresholds).
- Record wave gaps (~5–10y, irregular); weighted-CDF trajectories.
- Compare plug-in vs a **weights-aware** band (respondent/weight bootstrap only).
- Country-wide net / persistent decline (same E13 hierarchy), and compare the
  DIRECTION of conclusions to ESS (does over-certification shrink under a survey-
  aware band in a second, structurally different survey family, 106 countries).

## What WVS will NOT claim

- true complex-design validation; PSU-aware bands; high-DEFF empirical
  confirmation; or that Candidate B recovered proper design variance on WVS.
- The naive-vs-proper divergence (external criterion 2) is delegated to LAPOP
  (real design layer) and the simulation — never asserted from WVS.

## Framing sentence for the paper

"WVS provides a weights-only global external replication that the substantive
direction generalizes beyond Europe; the design-aware machinery is validated on
AmericasBarometer, whose public UPM/STRATA permit reconstruction of the true
complex-sample variance, and in simulation against known truth."
