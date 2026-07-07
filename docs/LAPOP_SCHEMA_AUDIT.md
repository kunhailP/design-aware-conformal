# LAPOP AmericasBarometer schema audit (BEFORE analysis)

Status: 2026-07-06. Audit only — no certification run until the LAPOP
preregistration (`LAPOP_PREREGISTRATION.md`) is fixed from these facts. Code:
`pcb/data/audit_lapop.py`. Outputs: `results/lapop_country_round_audit.csv`,
`results/lapop_design_completeness.csv`. Data (licensed, no redistribution —
gitignored under `data/lapop/raw/`): `Grand_Merge_2004-2023_LAPOP_
AmericasBarometer_v1.0_FREE.dta` (301,156 rows × 1,408 cols).

## Why LAPOP is the primary external design validation (vs WVS)

Unlike the WVS files (weights-only, no PSU/strata — see `WVS_ROLE_REDEFINITION.md`),
LAPOP ships the full survey-design layer in the public data and uses it
throughout 2004–2023. This is what lets the paper actually construct the proper
stratified-PSU design variance and test naive-vs-proper divergence (external-
validation criterion 2) on real data.

| role | variable | note |
|---|---|---|
| country | `pais` | 28 countries |
| survey year / round | `year`, `wave` | 14 years 2004–2023 |
| single country-year weight | `wt` | |
| multi country-year weight | `weight1500` | |
| **strata** | `strata` | study strata (also `estratopri` region, `estratosec` muni size) |
| **PSU** | `upm` | primary sampling unit |
| trust in legislature | `b13` | **1–7, high = trust (ESS-aligned)** — PRIMARY |
| satisfaction w/ democracy | `pn4` | 1–4, high = dissatisfied (reversed) — REPLICATION |
| support for democracy | `ing4` | 1–7, high = support — secondary |

## Structure and design completeness

- 168 country-year cells: **153 core** (usable outcome + weight + UPM + STRATA,
  n_upm ≥ 20), 15 excluded, 0 extended.
- **Design metadata present in every survey year 2004–2023**, median ~60–100 PSUs
  and 4–7 strata per country-year — a genuine multistage clustered design (real
  design effect, the regime ESS lacked).
- **26 countries have ≥ 2 core years** → adjacency for decline certification.
  Long panels: e.g. Brazil {2007,2008,2010,2012,2014}, Bolivia {2004,2006,2008},
  Belize {2008,2010,2012,2014,2023}.

## Outcome scales / direction (verified)

- `b13` trust in legislature: **1..7, high = trust**, in all 153 core cells. Same
  direction as ESS `trstprl` → low-trust core = low thresholds, decline = F rises
  at low t. No reverse-coding.
- `pn4` satisfaction: **1..4, high = dissatisfied** (1=very satisfied … 4=very
  dissatisfied) → reverse-code `sat = 5 − pn4` for uniform "decline = low-sat
  share rises." Available 137/153.
- `ing4` support for democracy: 1..7, high = support; 151/153.

## The 2021 round — excluded from design-aware certification (documented)

2021 is the COVID-era web/phone methodology: `upm` ≈ respondent (n_upm ≈ 3000,
n_strata = 1 — degenerate clustering) AND `b13` largely not asked (b13 valid
≈ 0–0.24 across countries). It correctly falls out of `core`. Excluded from the
design-aware trust analysis for BOTH reasons (no b13, no real design structure) —
a data fact surfaced by the audit, not a post-hoc filter. ing4/pn4 exist in 2021
but under the degenerate design, so also not used design-aware.

## Notes / caveats for the prereg

- A few `pais` codes lacked value labels in this merge (display as numeric codes);
  country names carry LATIN1 mojibake in raw labels (cosmetic only).
- `wt` within-cell CV is ≈ 0 for many early years (near self-weighting / pre-
  normalized); the design effect here comes from **clustering (UPM within
  STRATA)**, not weight variance — exactly what the stratified-PSU bootstrap
  captures and the respondent bootstrap misses. This is the mechanism the ESS
  data could not exercise.

## Proposed outcomes (to be FIXED in the preregistration, not here)

- Primary: `b13` trust in legislature (ESS `trstprl` analog).
- Replication: `sat = 5 − pn4` satisfaction with democracy (ESS `stfdem` analog).
- Secondary/support: `ing4` support for democracy.
