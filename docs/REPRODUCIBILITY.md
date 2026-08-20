# Reproducibility and compute

> **Entry point: [`REPLICATION.md`](../REPLICATION.md)** (run order, runtimes,
> verified bit-identical reproductions) and
> [`REPLICATION_MAP.md`](REPLICATION_MAP.md) (claim → artifact → ledger test).
> This file keeps the per-experiment detail.

Two tiers. Everything is deterministic under the committed seeds
(`pcb.util.det_seed`); Python 3.11, pins in `requirements.txt`.

## Tier 1 — no microdata (simulation / theory / benchmarks / public data)

```bash
pip install -r requirements.txt && pip install -e .
python -m pytest tests/ -q          # contracts + claim ledger (see REPLICATION.md for the current count)
# out of the box (each writes results/*.csv; ~seconds to ~minutes unless noted):
python -m pcb.experiments.e28_wrong_unit_coverage   # Table 1
python -m pcb.experiments.e32_severity              # severity/power
python -m pcb.experiments.e29_beyond_surveys        # unreachability beyond surveys
python -m pcb.experiments.e11_gate5c                # theorem checks
python -m pcb.experiments.e19_selector_sweep        # selector transition
python -m pcb.experiments.e21_safe_selector         # dev grid
python -m pcb.experiments.e22_holdout_validation    # 450-cell grid (~hours)
python -m pcb.experiments.e30_certified_core        # core aggregation (frozen CSV input)
python -m pcb.experiments.e31_positive_regime       # many-unit payoff
python -m pcb.experiments.e33_final_validation      # sealed final grid (~hours)
python -m pcb.experiments.e35_vdem_crosstab         # V-Dem cross-tabs (public)
python -m pcb.experiments.e37_claassen_compare      # Claassen comparison (public)
```

Verified 2026-07-27 in a fresh environment: 8 of these reproduce their committed
CSVs bit-identically (e11's outputs were refreshed from current code the same day).

## Tier 2 — licensed microdata (the two named reanalyses + LAPOP validation)

Obtain and place the three files per `docs/DATA_SOURCES.md` (checksums there),
then:

```bash
# schema audits + caches (order matters; each ~1–5 min)
python -m pcb.data.audit_ess
python -m pcb.data.ess_panel
python -m pcb.data.audit_wvs
python -m pcb.data.audit_lapop
# headline reanalyses
python -m pcb.experiments.e13_ess_audit             # ESS certification counts (§7)
python -m pcb.experiments.e36_ess_long_window       # long window 2002–2024 (§7)
python -m pcb.experiments.e26_wvs_deconsolidation   # WVS/EVS Foa–Mounk (§7; ~1–2 h)
python -m pcb.experiments.e34_wvs_country_flags     # per-country rung flags
python -m pcb.experiments.e50_joint_claim_family    # the joint band (paper Table 2)
python -m pcb.experiments.e54_small_area_transport  # small-area activation (§6; ~1–2 h)
python -m pcb.experiments.e55_small_area_exchangeability  # its LOCO/LORO audit (~30 min)
# robustness analyses (all require the microdata)
python -m pcb.experiments.e38_rescaled_bootstrap    # Rao-Wu-Yue rescaling
python -m pcb.experiments.e39_wvs_deff_sensitivity  # WVS deff x1.5/x2
python -m pcb.experiments.e40_mode_audit            # mode table + singleton strata
python -m pcb.experiments.e41_loro_exchangeability  # leave-one-region-out
python -m pcb.experiments.e42_real_severity         # null-imposed power curve
python -m pcb.experiments.e43_endpoint_sensitivity  # net-rung endpoint robustness
python -m pcb.experiments.e44_long_window_deff      # long-window deff sensitivity
python -m pcb.experiments.e45_magnitudes_and_rises  # certified sizes + recoveries
python -m pcb.experiments.e46_claassen_window_matched  # window/item-matched
# supporting real-data experiments
python -m pcb.experiments.e12_ess_decline
python -m pcb.experiments.e23_ess_youth
python -m pcb.experiments.e24_subgroup_rho_scan
python -m pcb.experiments.e15_lapop_certify
python -m pcb.experiments.e16_lapop_transport
python -m pcb.experiments.e17_lapop_change_transport
python -m pcb.experiments.e18_semisynthetic
```

Verified 2026-07-27 against the committed results from the raw licensed files:
`e13` (ESS certification) and `e26` (WVS all five items, all rungs) reproduce
**bit-identically**; LAPOP outputs were refreshed from current code (post-repair
version skew; 11 of 1,119 pair-level booleans moved, no paper claim affected).

## Figures

`python -m pcb.figures.<name>` writes to `figures/` (created on demand);
`fig_certified_core` writes `paper/figures/` directly. Paper figures regenerate
from the committed `results/*.csv` — microdata is not needed for figures.

## Compute

Everything runs on a single multicore machine; no GPU. The heavy items are the
validation grids (`e22`, `e33`; hours) and `e26` (~1–2 hours). Memory: the ESS
and LAPOP `.dta` reads peak at ~8–16 GB; the parquet caches make reruns cheap.

## Determinism

All RNG flows through `pcb.util.det_seed(...)` (named, per-cell seeds); reruns of
any experiment reproduce its committed CSV exactly on the same dependency pins.
The one disclosed exception is documented in the paper (§5): the original sealed
holdout config was lost and its corrected-scorer rerun uses a fresh seed.

## Claim ledger

`tests/test_paper_claims.py` pins every headline number in `paper/` to the
result table that licenses it, and fails if either moves. It runs in CI with the
contract tests. Three rounds of referee reports on this manuscript found the
same failure mode more than once — a number or a scope word in the text
drifting from what the experiment produced — so the ledger exists to make that
class of error impossible to ship. A claim in the paper but not in the ledger is
a claim no one is checking.

## Two things this package deliberately does not ship

`results/holdout_safe_selector.csv` is the 63 MB per-replicate output of the
development holdout; the per-cell summaries it reduces to
(`holdout_safe_selector_cells*.csv`) are shipped and are what the paper and the
ledger read. Re-running `e22_holdout_validation` regenerates the full file.

The R port's vignette is built with `rmarkdown`, which is a *suggested*
dependency. `R CMD check rpkg/dapcb --no-build-vignettes` (with
`_R_CHECK_FORCE_SUGGESTS_=false` if `knitr`/`rmarkdown` are absent) exercises the
golden cross-language tests without it, and that is the check that matters for
replication: it verifies the R and Python implementations agree to 1e-10.

## Superseded and withdrawn experiments

Some scripts remain in the package but no longer back a claim in the manuscript.
`e43` (endpoint sensitivity), `e45` (per-family magnitudes and rises) and `e44`
(per-family design-effect sweep) are **superseded** by the joint band, `e50`.
`e48`, `e49` and `e51` are **withdrawn**: the ESS-region frontier and the
apparent optimal unit were artifacts, diagnosed in the supplement. They are kept
so the diagnosis is reproducible; nothing in the paper cites them as live.
