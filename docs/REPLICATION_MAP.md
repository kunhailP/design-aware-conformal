# Replication map — every headline claim, its artifact, and its pin

The machine-authoritative version of this table is
`tests/test_paper_claims.py`: each row below is enforced by the named ledger
test, which reads the CSV and greps the manuscript, and fails if either
moves. Experiments regenerate the CSVs deterministically (fixed seeds); the
three marked ★ have been verified to reproduce **bit-identically** from the
raw licensed files in two independent environments (see `REPLICATION.md`).

| paper claim (location) | experiment | artifact (`results/`) | ledger test |
|---|---|---|---|
| ESS 2018–2024: marginal 20/30 → any-pair 12 → net 6 → persistent 1 (abstract, §7) | `e13` ★ | `ess_country_certification.csv` | `test_ess_short_window_counts` |
| The net six: AT, BE, EE, GB, GR, NL (§7) | `e13` ★ | same | `test_ess_net_six_membership` |
| Long window per-rung: persistent 0/33 incl. plug-in; any-pair 28; net 9 (§7) | `e36` | `ess_long_window.csv` | `test_long_window_counts` |
| Joint band: 1,173 ordered contrasts; 193 declining / 212 rising (§7) | `e50` ★ | `ess_joint_claims.csv` | `test_joint_contrast_totals` |
| Joint net set of eight: CY, ES, GB, GR, HU, IL, IT, UA; persistent 0 (§7) | `e50` ★ | same | `test_joint_band_net_set` |
| 23/33 certify both a decline and a recovery, each outcome (abstract, §7) | `e50` ★ | same | `test_joint_band_episodic_needs_no_correction` |
| Ukraine's span decline ≥ 25 points (§7) | `e50` ★ | same | `test_ukraine_magnitude_is_a_lower_bound` |
| Erosion share is within-country only (c–length corr. 0.96) (§7) | `e50` ★ | same | `test_erosion_share_is_not_ranked_across_countries` |
| **Prevalence: at least 6 of 33 truly declined, both outcomes, 90% simultaneous** (abstract, §7, S4) | `e56` | `ess_prevalence.csv` | `test_cross_country_prevalence` |
| WVS rung-gap decomposition: 2.6–6.5× mixed; 1.7–4.8× / 1.9–4.8× rung-only (§7) | `e26` ★ | `wvs_deconsolidation.csv` | `test_wvs_rung_gap_decomposition` |
| 13-country certified core; West enters twice, flagged (§7) | `e30` | `certified_core.csv` | `test_certified_core_size_and_west` |
| Core stable at variance ×1.5 / ×2.0 (13 → 12) (§7) | `e39` | `wvs_deff_country_flags.csv` | `test_wvs_deff_core_stability` |
| Wrong-unit collapse: 3.5% / 49.8% vs 90% at L=8 (§5, Fig. 1) | `e28` | `wrong_unit_coverage.csv` | `test_wrong_unit_collapse_figure_one` |
| Severity: net rung powered at 0.02–0.03, persistent needs 0.06–0.08 (§5) | `e32`, `e42` | `severity.csv`, `real_severity.csv` | `test_severity_ordering` |
| Real-data injection thresholds ≈ 0.033 / 0.075; size 0.001–0.007 (§5) | `e42` | `real_severity.csv` | `test_real_severity_is_monte_carlo_not_mde` |
| Reliability floor: D ≥ √(2/(K−1)), K ≥ 94 at frozen τ_D (§6, Prop. 1) | identity | — | `test_reliability_floor_arithmetic`, `test_prop1_floor` |
| WVS gate probe: K=95–105 floor-feasible, ρ̂_LCB ≤ 0.10, gate A never opens (§6) | `e26` probe | `wvs_gate_probe.csv` | `test_wvs_gate_probe` |
| Three regimes occupied; selector fired only in 'feasible' (§6, S1, Fig. S) | `e57` | `feasibility_frontier.csv` | `test_feasibility_frontier` |
| Small-area activation: 4 cells, K=228–287, band 20.5–26.6% narrower (certified 0.16–0.22), level 0.881 (abstract, §6) | `e54` | `small_area_transport.csv` | `test_small_area_activation` |
| Region is the exchangeable unit: LOCO ≈ LORO within 0.015; East caveat (§6) | `e55`, `e41` | `small_area_exchangeability.csv`, LORO CSVs | `test_small_area_unit_is_exchangeable`, `test_loro_east_undercoverage` |
| LOO-center seam: 0/28 cells below the exact floor; split-fold infinite at K≤15 (§4, S1) | `e58` | `center_exactness.csv` | `test_center_exactness_seam` |
| Persistent-null qualifier travels with every statement of the null (abstract, §5, §7) | — | — | `test_persistent_null_is_qualified_where_it_is_stated` |
| Mode audit: Greek pair mode-constant; net counts unchanged excluding switchers (§7) | `e40` | `ess_mode_table.csv`, `ess_mode_constant_certification.csv` | `test_mode_table_self_completion_set` |
| Singleton strata 1 of 7,028; RWY floors tight (§6) | `e38` | `ess_singleton_strata.csv`, `*_rescaled.csv` | `test_singleton_strata_count` |
| Withdrawn results stay withdrawn (frontier, interior optimum) (S) | — | — | `test_frontier_claims_are_withdrawn`, `test_no_unsupported_interior_optimum` |

Guard tests with no single number: `test_no_false_under_detection_claim`,
`test_no_stale_pre_joint_counts`, `test_no_unverified_robustness_superlatives`,
`test_claassen_window_matched_core_turnover`,
`test_long_window_deff_membership_stable`.

Theorem ↔ code contracts (the other 70 tests) live in the remaining
`tests/test_*.py` files, one file per result: e.g. `test_theorem0` (Theorem 1,
curve level), `test_fixed_length_exchangeability` /
`test_unstudentized_exchangeability` (Theorem 3), `test_estimated_law_validity`
(Theorem 4′), `test_safe_selector` / `test_anchor_domination` (Theorem 5′),
`test_prop1_floor` (Proposition 1), `test_claim_family` (Proposition 2 and the
rung partial order), `test_prevalence` (the closed-testing bound, planted
truth), `test_dapcb_api` (the deployed entry point end to end).
