# WVS partial-conjunction upgrade: frozen protocol

Frozen before access to the licensed WVS file in this environment:
2026-09-07. This analysis strengthens the cross-item interpretation of the
existing E26 result; it does not change E26's estimand, bootstrap, item cores,
or persistent-decline definition.

## Target

For each country, test the partial-conjunction claim that at least two available
WVS battery items truly exhibit persistent decline over every consecutive
observed wave pair and every preregistered core threshold.

The component p-values invert the exact one-sided adjacent-pair band used by
`pcb.experiments.e26_wvs_deconsolidation`. A country-item is available when E26
has at least two qualifying waves, using E26's fixed `MIN_N=400`, item support,
core thresholds, weights, 2,000 bootstrap draws, and deterministic seeds.

## Fixed tests

For a country with `m` available item p-values
`p_(1) <= ... <= p_(m)`, `m >= 2`:

- primary, arbitrary-dependence-valid partial conjunction:
  `p_pc_bonferroni = min(1, (m - 1) * p_(2))`;
- sensitivity under independence or PRDS across items: apply Simes to the
  largest `m - 1` ordered p-values.

The primary country-level claim certifies at alpha 0.10 when
`p_pc_bonferroni <= 0.10`. It establishes that at least two items truly decline;
it does not by itself identify which two.

Across countries, the primary prevalence and named-set analysis applies
Goeman--Solari closed testing with Bonferroni local tests to the country-level
`p_pc_bonferroni` values. This layer is valid under arbitrary cross-country
dependence. Simes local tests are reported only as a sensitivity requiring
independence or PRDS.

## Outputs fixed in advance

- `results/wvs_item_pvalues.csv`: one row per available country-item;
- `results/wvs_partial_conjunction.csv`: one row per country with at least two
  available items;
- `results/wvs_partial_conjunction_prevalence.csv`: global lower bounds and
  closure-correct named sets under Bonferroni and Simes local tests.
- `results/wvs_partial_conjunction_deff*.csv`: the same country and prevalence
  results after the existing E39 variance multipliers 1.5 and 2.0.

The existing descriptive `>=2`-item core remains in the results for comparison.
No assumption is made that its 13 members will survive partial conjunction.

## Interpretation and stopping rule

The WVS Trend File has weights but no PSU or stratum identifiers. The upgrade
controls cross-item and, in the prevalence analysis, cross-country multiplicity,
but it does not repair that design-information limitation. The manuscript will
retain the weights-only caveat.

If the primary partial-conjunction set is empty or loses the current geographic
interpretation, the result will be reported as a robustness boundary rather than
used to replace the descriptive core headline. No item core, alpha, minimum
sample size, bootstrap count, or conjunction rule will be changed after seeing
the result.
