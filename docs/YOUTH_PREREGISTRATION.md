# Youth age-group analysis — preregistration

Status: **sealed 2026-07-06 before extracting `agea` / seeing any age-stratified
result.** A robustness supplement to the political reanalysis
(`ESS_POLITICAL_PAYOFF.md`, `e13_ess_audit`), not a new method. Runner
`pcb/experiments/e23_ess_youth.py`; output `results/ess_youth_certification.csv`;
writeup `docs/YOUTH_RESULTS.md`.

## Question

Is the persistent, country-wide, design-aware distributional decline in political
trust (certified in only Greece for the full sample) **specific to an age group**?
This is an **age-group** comparison at each survey wave — NOT a cohort/panel design;
we do not track individuals over time, and we make no cohort-effect claims.

## Age groups (fixed now)

- **Primary:** youth, `agea` ∈ [18, 29].
- **Benchmark:** full adult sample (`agea` ≥ 18), i.e. the existing analysis.
- **Contrast:** older, `agea` ≥ 50.
- **Supplementary:** middle, `agea` ∈ [30, 49].

## Everything else reused unchanged from the main analysis

Outcomes: `trstprl` (primary), `stfdem` (replication). Thresholds t = 0..9 on the
0–10 scale. Countries/waves: the same ESS core rounds (9–11) that carry PSU/stratum
design information; `agea` missing rows dropped. Design bootstrap: the same
stratified-PSU Rao–Wu bootstrap (B=300), weights `anweight`→`pspwght`. Cutoff
ρ₀=0.47, the same guarantee hierarchy (pair / any-pair / net / persistent
country-wide simultaneous / Bonferroni-across-countries), the same fallback rules and
the same `certify_decline_differences`. No threshold, country set, wave range, ρ₀, or
fallback is changed for the age analysis.

## Minimum effective sample (fixed now)

A country-round enters an age group only if it has **≥ 200 valid responses** for the
outcome in that age band (youth cells are ~15–25% of the full sample). A country
enters the certification only if it has **≥ 2 core rounds** meeting that threshold
(same as the main analysis). Cells below the min-n are **abstained** (dropped, not
imputed) and their count is reported. This is fixed before seeing the counts.

## Primary metric and success framing

Per age group, the count of countries with a **persistent country-wide design-aware**
decline (the honest object), reported alongside the pair/any-pair/net rungs. There is
no oracle truth on real data, so we report counts and reclassifications, never "false
positive." The question is descriptive: does the youth count exceed, match, or fall
below the full-sample count (1, Greece)?

## Locked rules (post-results)

After `e23` runs, the age bins, min-n, thresholds, countries, waves, ρ₀, seed, and
fallback are immutable; results reported as produced. The design-noise regime (ρ̂) is
expected to be **larger** for youth than for the full sample (smaller n → more design
noise), which is itself informative about when the design-aware correction begins to
bite on real data.
