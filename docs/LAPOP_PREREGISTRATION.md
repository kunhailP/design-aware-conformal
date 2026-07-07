# LAPOP external-validation preregistration (choices fixed BEFORE results)

Status: 2026-07-06, written from `LAPOP_SCHEMA_AUDIT.md` before running the method
comparison. Per Gate-5D discipline: rounds, countries, outcomes, thresholds, and
methods are fixed here and NOT changed after seeing results. Any deviation is
logged as a deviation.

## 1. Purpose (fixed)

Primary external **method** validation of Candidate B on a real complex survey
whose design layer (UPM/STRATA) is present — the regime ESS lacked. The claim to
reproduce is NOT the same country list as ESS, but the same **mechanism**: proper
survey-design uncertainty (a) is unnecessary width where the design effect is
small, and (b) diverges from the naive band and demotes over-certification where
the design effect is large.

## 2. Data scope (fixed)

- **Sample:** the 153 `core` country-years (usable outcome + `wt` + `upm` +
  `strata`, n_upm ≥ 20), 28 countries, 2004–2023.
- **Excluded:** the 2021 COVID web/phone round (degenerate `upm`=respondent,
  n_strata=1, and `b13` largely unasked — audit §2021). No other exclusions.
- **Unit:** adjacent core-year country pairs (consecutive core survey years for
  the same country). "Adjacent" = consecutive available rounds, NOT fixed spacing
  (gaps recorded, typically 2 years). 26 countries have ≥ 2 core years.

## 3. Outcomes and direction (fixed)

- **Primary:** `b13` trust in legislature, 1–7, high = trust. CDF F(t)=P(Y≤t),
  t=1..6. Low-trust core = t ∈ {1,2,3} (share with trust ≤ 3, below the 1–7
  midpoint). Decline = F rises at low t. No reverse-coding (ESS-aligned).
- **Replication:** `sat = 5 − pn4` satisfaction with democracy, 1–4, high = sat.
  Low-sat core = t ∈ {1,2}. Decline = F_sat rises at low t.
- **Secondary:** `ing4` support for democracy, 1–7, low-support core t ∈ {1,2,3}.

## 4. Estimand and certification units (fixed, same as ESS E13)

Consecutive-difference D_{c,r}(t) = F_{c,r+1}(t) − F_{c,r}(t) over the low core.
Within-country ⇒ country effect cancels ⇒ pure design inference. Report the full
guarantee hierarchy: pair-level (marginal), any-pair, repeated (≥2), net (first→
last span), and **country-wide simultaneous persistent** (one band over all a
country's pairs × core thresholds, R_c = max_{pairs,t}|D̂−D|/s — the primary
multiplicity-controlled claim). α = 0.10, bootstrap B = 2000.

## 5. Methods compared (fixed) — the naive-vs-proper test LAPOP enables

| tag | construction | isolates |
|---|---|---|
| M0 | raw plug-in point | no uncertainty |
| M1 | respondent bootstrap (unweighted resample) | SRS sampling variance |
| M2 | weighted respondent bootstrap (resample rows, apply `wt`) | + weighting |
| **M3** | **stratified PSU bootstrap** (resample `upm` within `strata`, Rao–Wu) | **+ clustering design effect (the proper band)** |
| M4 | conservative survey-noise plug-in (worst-case, Thm A.2) | validity ceiling |
| **M5** | **Candidate B** (deconvolved studentized, Thm B) | regime-adaptive efficiency |
| M6 | conservative fallback (B below ρ*, worst-case above, Thm D) | stability |

M2-vs-M3 is the naive-vs-proper divergence (external criterion 2), now testable
because LAPOP has UPM/STRATA. M5-vs-M3 tests whether Candidate B recovers the
proper design width. M5-vs-M4 tests efficiency over the conservative ceiling.

## 6. Empirical design-noise ratio (fixed definition — the ONE ρ)

Per country-year and per pair: ρ_cr = σ_design,cr / σ_total,cr, an SD ratio, with
σ_design from the stratified-PSU bootstrap (M3) and σ_total the plug-in transport-
scale SD (consistent with `DESIGN_AWARE_THEOREM.md` and the ESS prereg — ρ is
always an SD ratio, never a variance fraction). Reported per pair; used to split
subgroups.

## 7. High- vs low-design-noise subgroups (fixed BEFORE results)

- **High-noise** = pairs in the top tercile of ρ_cr (equivalently few PSUs / high
  weight CV / small n — reported together).
- **Low-noise** = bottom tercile.
The subgroup cut is defined on ρ terciles fixed here; not re-cut after seeing
certification outcomes.

## 8. Success criteria (fixed; criterion 2 is the core one)

1. **Low-noise:** M5 (Candidate B) width ≈ M3/oracle (no needless widening).
2. **High-noise (CORE):** M2 (naive) and M3 (proper) diverge, and M5 reflects the
   proper design uncertainty, demoting over-certification. This is what ESS could
   not show (there design effects were small, M1≈M4).
3. M5 valid while narrower than the M4 conservative inflation.
4. Plug-in certifications reclassified to inconclusive concentrate in the complex-
   design (high-ρ) country-years.

No coverage claim on LAPOP (no oracle truth); coverage lives in Thm + Gate-5C sim.
Report width, certification counts, reclassification, ρ, and subgroup contrasts.

## 9. Candidate B settings (fixed)

ρ* = 0.47 (Gate-5C), negative-variance floor on ŝ_T², v̂² from the stratified-PSU
bootstrap; all chosen without the target. Fallback per Thm D.

## 10. What is NOT done here

No new bands/predictors/modulation beyond M0–M6. WVS stays a separate weights-only
replication (`WVS_ROLE_REDEFINITION.md`). Foa–Mounk cohort deferred (needs ESS age
re-extract). Region (`estratopri`) is a real LAPOP stratum here (unlike WVS
`X048`), so its use is design-valid, not a pseudo-cluster heuristic.
