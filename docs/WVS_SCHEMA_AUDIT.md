# WVS/EVS external-validation schema audit (BEFORE analysis)

Status: 2026-07-06. Per the Gate-5D instruction, only a schema audit is performed
here — no certification analysis is run until the WVS preregistration is written
from these facts. Files (licensed, gitignored under `data/wvs/`):
`Trends_VS_1981_2022_Stata_v4_1.dta` (WVS/EVS integrated trends, 442,473 rows ×
732 cols) and `ZA7503_v3-0-0.dta` (EVS/WVS Joint 2017–2022, 224,434 × 635).

## Variables located

| role | variable | note |
|---|---|---|
| country | `S003` (ISO num), `S009` (alpha-2), `S024` (country-wave) | |
| wave / year | `S002VS` (EVS-WVS chronology), `S020` (year) | irregular ~5–10y gaps |
| confidence in parliament | `E069_07` | **4 categories, 1=a great deal … 4=none** |
| satisfaction w/ democracy | `E110` | 4 categories, 1=very satisfied … 4=not at all |
| weight | `S017` (design weight), `S018` (equilibrated-1000), `pwght` (pop size) | |
| region | `X048*` (NUTS-1/2, ISO 3166-2) | **not a PSU** |

## Structure (parliament item, WVS/EVS trends)

- 295 country-year cells carry `E069_07`; **106 unique countries; 78 with ≥ 2
  waves** (the adjacency requirement). Far more countries and a longer span than
  ESS (30 core countries, 2018–2022) — a genuinely different survey family.
- Median n per country-year ≈ **1187** (ESS core pairs ≈ 1500–2200).

## The decisive finding: NO design metadata (PSU / stratum / replicate weights)

Neither WVS file contains PSU, stratum, cluster, or replicate-weight variables —
searched by name and label in both. Only survey weights (`S017`) and a region
code (`X048`, NUTS, which is a geographic label, not the sampling PSU). Moreover
the median within-cell weight CV is ≈ 0 — many WVS country-years ship uniform or
near-uniform weights.

**Consequence for the method comparison.** The ESS clustering design-effect
demonstration (M1 naive respondent bootstrap vs **M4 stratified-PSU** difference
band) CANNOT be reproduced on WVS: with no PSU/strata, the proper design
bootstrap is not constructible, so the naive respondent/weight bootstrap **is**
the only survey-aware band available on WVS. The external-validation success
criterion "naive and Candidate B diverge in a high-design-noise regime"
(criterion 2) is therefore **not achievable on WVS** — that specific divergence
needs a survey with public PSU/strata (or stays in the Gate-5C simulation, where
the design DGP already produces deff > 1 and the divergence is measured against
known truth).

## What WVS CAN validate (honest, revised scope)

WVS is still a strong external test of the paper's CORE mechanism in a
structurally different survey: propagating sampling uncertainty into a
simultaneous within-country difference band demotes plug-in over-certification.
Different from ESS on every axis that matters for generalization:

- 106 countries incl. non-European / developing democracies (vs ESS 30 European);
- coarse 4-category trust scale → only **3 thresholds** (vs ESS 0–10);
- irregular ~5–10-year wave gaps (vs ESS 2-year rounds);
- weight-based rather than PSU-based sampling variance; smaller n.

Reproducing the mechanism here defends against the referee line "the method is
fit to ESS." Achievable criteria: 1 (no needless widening where sampling noise is
small), 3 (tighter than conservative plug-in inflation), 4 (reduces political
over-certification), 5 (no post-hoc threshold/method changes). Criterion 2
(naive≠proper) is explicitly delegated to the simulation.

## Direction and coding for the WVS preregistration (to fix next)

- `E069_07` is REVERSED vs ESS `trstprl`: high value = LOW confidence. Reverse-
  code to a trust scale `trust = 4 − E069_07` (0–3, high = high trust) so the ESS
  machinery and "low-trust share rises = decline" logic apply unchanged. Low-trust
  core on the 0–3 scale = t ∈ {0,1}. Same for `E110`.
- Negative values are WVS missing codes → dropped. Weight = `S017`.
- Adjacent = consecutive available waves for a country (gaps recorded; ~5–10y, so
  "adjacent" means consecutive surveys, not fixed spacing — a documented
  difference from ESS's 2-year rounds).

## Recommended path (for confirmation)

1. WVS as **cross-survey mechanism replication** (plug-in vs respondent/weight
   survey-aware difference band), full inferential audit as in E13 (pair / net /
   persistent / country-wide simultaneous), reverse-coded, 4-category.
2. Keep the **naive-vs-proper divergence** (criterion 2) in the simulation — no
   clean public real-data high-deff file is in hand; optionally add `X048` region
   as a caveated pseudo-cluster robustness only.
3. Candidate B theorem (A–E) completed in parallel (`DESIGN_AWARE_THEOREM.md`),
   independent of WVS.
