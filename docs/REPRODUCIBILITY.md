# Reproducibility and compute

Two tiers. Everything is deterministic under the committed seeds
(`pcb.util.det_seed`); Python 3.11, pins in `requirements.txt`.

## Tier 1 — no microdata (simulation / theory / benchmarks / public data)

```bash
pip install -r requirements.txt && pip install -e .
python -m pytest tests/ -q          # 57 contract tests (theorem <-> code)
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
