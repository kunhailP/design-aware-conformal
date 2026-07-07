# LAPOP external design validation — results (E15)

Status: 2026-07-06. Preregistered in `LAPOP_PREREGISTRATION.md` (choices fixed
before results; none changed after). Code `pcb/experiments/e15_lapop_certify.py`,
figures `pcb/figures/fig_lapop.py`, data `results/lapop_decline_certification.csv`.
Scope: 153 core country-years, 26 countries, 2004–2023 (2021 COVID round
excluded per audit), 373 adjacent-year pairs across b13 (trust in legislature,
primary), sat=5−pn4 (satisfaction, replication), ing4 (support). No oracle truth →
certification / width / regime, not coverage.

## Two findings, stated honestly (one strong, one a real limit)

### 1. The design effect ESS lacked is REAL on LAPOP (the machinery is validated)

The design-effect ratio deff½ = SD(proper stratified-PSU band) / SD(naive
respondent band) on the within-country difference:

| outcome | median deff½ | high-ρ tercile | max |
|---|---|---|---|
| b13 trust | 1.20 | 1.51 | 1.79 |
| sat | 1.17 | 1.43 | 1.81 |
| ing4 | 1.13 | 1.45 | 1.92 |

The proper stratified-PSU band is ~18% wider than the naive band at the median
and up to ~1.9× in the most-clustered country-years (`figures/lapop_design_
effect.png`). This is exactly the regime ESS could not exercise (there deff½ ≈ 1,
M1 ≈ M4). So LAPOP confirms that the proper design bootstrap captures clustering
variance the naive/weighted respondent bootstrap misses — the design-aware
machinery does real work where the design is genuinely complex.

### 2. The ESS over-certification mechanism reproduces in a different survey family

Pair-level certification (of ~125):

| outcome | M0 plug-in | M1 unweighted | M2 weighted | M3 proper PSU |
|---|---|---|---|---|
| b13 | 64 | 42 | 43 | 41 |
| sat | 70 | 46 | 46 | 45 |
| ing4 | 56 | 26 | 25 | 24 |

Accounting for survey uncertainty at all (M0 → any survey-aware band) roughly
halves certifications, in Latin America's complex multistage design just as in
Europe — a genuine external reproduction (`figures/lapop_external_reproduction.png`).
The "not fit to ESS" referee line is answered.

## The honest limit: the naive-vs-proper CERTIFICATION gap is modest

Although deff½ is materially > 1 (finding 1), the M2 (naive) → M3 (proper)
certification-COUNT difference is small even in the high-ρ tercile:

| outcome | high-noise M2 → M3 | low-noise M2 → M3 |
|---|---|---|
| b13 | 10 → 9 | 21 → 20 |
| sat | 16 → 15 | 17 → 17 |
| ing4 | 10 → 8 | 7 → 8 |

A 40–50% band-width inflation flips only 0–2 borderline pairs. **Certification is
a coarse binary**: most pairs are decisively certified or decisively not, so the
design effect moves WIDTH (efficiency) much more than it moves the certification
count. We report this rather than overclaim a large naive-vs-proper certification
divergence.

## What this means for the paper (the two-dataset story is stronger, not weaker)

The two real datasets exercise the two regimes cleanly, and the honest reading is
more defensible than a single dramatic number:

- **The dominant, universal lever is sampling-uncertainty-awareness itself**
  (M0 → survey-aware): it roughly halves certifications on BOTH ESS and LAPOP.
  This is the substantive payoff and it generalizes.
- **The clustering design-effect refinement (naive → proper PSU) is a WIDTH /
  efficiency phenomenon**, small on ESS (deff≈1) and real but certification-
  robust on LAPOP (deff½ up to 1.9, yet ≤2 pairs reclassified). The method is
  regime-adaptive: it pays for clustering variance only where it exists, and its
  practical effect on a binary certification is modest.

This matches Candidate B's design intent (Thm C: reduce to clustered PCB when the
design effect vanishes; earn the correction only where it is real) and is honest
about magnitudes.

## Deferred to Part B (e16, Candidate B transport)

M4 worst-case / M5 Candidate B deconvolution / M6 fallback are TRANSPORT-setting
estimators (cross-country deployment): the within-country difference has no
transport term, so the proper band there is simply M3. The deconvolution and its
ρ = design/transport SD ratio are validated in the leave-one-country-out
clustered-conformal transport experiment (Part B), where survey-estimated
calibration curves carry design noise to be deconvolved from cross-country
transport variability. This is a preregistration clarification (method-to-problem
assignment), not a change to thresholds/countries/outcomes.
