# ESS Calibration-Unit Audit (E8) — country-round vs country trajectory

Status: blocking audit completed 2026-07-06. Code: `pcb/inference/clustered_band.py`,
`pcb/experiments/e8_cluster_audit.py`. Numbers: `results/ess_cluster_audit.csv`.

## 1. What K=250 in gate 2 actually was

Confirmed: the gate-2 (E7) conformal quantile was computed over **country-round
sup-scores** (~243 per target after excluding the target country), from 35
countries. Country-blocked prediction and country-blocked score/modulation
exclusion were in place (the held-out country's rounds never enter the
calibration errors nor the modulation `s(t)`), but the calibration **unit**
was the country-round. Rounds of one country are serially dependent, so those
scores are not exchangeable draws: `effective K ≈ 35 countries, not 250`.

## 2. The two constructions

Identical predictions (LOCF — **temporal transport**: nowcasting the next
round of a country whose earlier rounds exist; *not* unseen-country
transport), identical error curves, identical target-country exclusion.

- `round_cal` (gate-2 construction): quantile over country-round scores.
- `cluster_cal`: one score per country trajectory,
  `R_c = max_{r,t} |E_{c,r}(t)|/s(t)`; quantile over the K = #countries − 1
  country scores; the band `θ̂_{c,r} ± q·s(t)` is issued for every round of
  the held-out country and judged as covered only if **all rounds × all
  thresholds** lie inside (`R_{c*} ≤ q`).

## 3. Results (nominal 90%; `balanced` = countries with ≥4 LOCF rounds, last 4)

| outcome | layer | method | eff. K | attainable | country-level cov (exact) | round-level cov | mean width |
|---|---|---|---|---|---|---|---|
| trstprl | all | round_cal | 243* | .902 | **.429** (15/35) [.28,.59] | .892 | .291 |
| trstprl | all | cluster_cal | 34 | .914 | **.886** (31/35) [.74,.95] | .976 | .584 |
| trstprl | balanced | round_cal | 116* | .906 | .733 (22/30) | .883 | .293 |
| trstprl | balanced | cluster_cal | 29 | .900 | **.900** (27/30) [.74,.97] | .967 | .426 |
| stfdem | all | round_cal | 243* | .902 | .543 (19/35) | .896 | .324 |
| stfdem | all | cluster_cal | 34 | .914 | .886 (31/35) | .984 | .494 |
| stfdem | balanced | round_cal | 116* | .906 | .800 (24/30) | .900 | .322 |
| stfdem | balanced | cluster_cal | 29 | .900 | **.900** (27/30) | .950 | .443 |

\* nominal count of country-round scores; NOT independent units.

## 4. Diagnosis

1. **The gate-2 numbers survive at their own level.** Round-level coverage of
   `round_cal` is 88–90% — the marginal (per-country-round) claim did not
   collapse under the within-country dependence on this data.
2. **But the trajectory-level claim collapses.** The probability that a
   held-out country's ENTIRE trajectory (all its rounds, all thresholds) lies
   in the round-calibrated bands is 42.9% (trstprl) / 54.3% (stfdem) against
   nominal 90%. With ~7 rounds per country and ≈89% per round, ≈0.89^7 ≈ 0.44
   — the original paper's pointwise-versus-supremum failure, reproduced one
   level up. Any claim that spans rounds ("trust declined in country X",
   country rankings pooled over rounds) inherits this failure.
3. **Cluster calibration restores it.** 31/35 and 27/30 covered countries —
   nominal within the K≈30–34 granularity (attainable levels .914/.900;
   quantile steps 1/(K+1) ≈ 2.9–3.3%, so decimal-point comparisons are
   meaningless; exact counts and Wilson CIs are the honest report).
4. **The price is width**: ×2.0 for full trajectories (up to 10 rounds), ×1.45
   for 4-round trajectories. Trajectory length is part of the guarantee, so
   the `balanced` design both removes the round-count heterogeneity caveat
   (trajectory exchangeability is cleaner when lengths match) and prices the
   guarantee per fixed horizon.

## 5. Implications for the paper

- The methodological unit story now has three rungs: threshold → curve
  (original PCB), round-curve → country trajectory (clustered PCB). "The
  wrong unit of uncertainty" recurses, and the ESS layer contributes a new
  construction, not just a new dataset.
- Round-level claims remain available, but their honest calibration should
  use one score per country (e.g., most-recent-round scores, K = #countries)
  rather than pooled country-round scores; implementing that variant is the
  next step alongside the predictor suite.
- All reported Ks must state the exchangeable unit; granularity
  (`1/(K+1)`) and exact covered counts accompany every coverage figure.

## 6. Naming

LOCF-based results are labelled **temporal transport** throughout; the term
"unseen-country transport" is reserved for macro-covariate predictors that
never see the target country's past responses (E9, upcoming).
