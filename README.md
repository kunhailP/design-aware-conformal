# The Wrong Unit of Uncertainty

Replication package for *"The Wrong Unit of Uncertainty: Adaptive Design-Aware
Conformal Inference for Repeated Cross-National Surveys."*

**Anonymized for double-blind review** — author and affiliation are withheld.

## What this is

Claims about repeated cross-national surveys attach uncertainty to the wrong unit
twice: a wave-pair mean contrast stands in for a persistent, distribution-wide
trajectory, and an estimated distribution stands in for the latent one it samples.
This package provides a multiplicity-honest simultaneous band over a country's whole
trajectory, an impossibility result and a survey-scale unreachability boundary for
the design-aware correction, a provably-valid deployed procedure, and two named
reanalyses (ESS trust; WVS Foa–Mounk deconsolidation).

## Layout

```
paper/            LaTeX source (main.tex, sections/, figures/, refs.bib)
pcb/              method library + experiments
  inference/      clustered/population conformal, design_aware, safe selector
  simulation/ theory/ data/    generators, theory checks, survey loaders
  experiments/    e6-e26 (design-aware arc; ESS/LAPOP/WVS) + e28-e30 (benchmarks, certified core)
  figures/        figure generators
tests/            contract tests (theorem <-> code), 54 total
results/          precomputed result tables (CSV)
docs/             preregistrations, results write-ups, proofs, data sources
```

## Reproduce

```bash
pip install -r requirements.txt
python -m pytest tests/ -q                        # 54 contract tests (should pass)
# Simulation / theory — no microdata needed, run out of the box:
python -m pcb.experiments.e28_wrong_unit_coverage   # wrong-unit coverage collapse
python -m pcb.experiments.e29_beyond_surveys        # unreachability beyond surveys
python -m pcb.experiments.e11_gate5c                # theorem checks
python -m pcb.experiments.e19_selector_sweep        # selector transition
python -m pcb.experiments.e21_safe_selector         # safe-adaptive selector grid
python -m pcb.experiments.e22_holdout_validation    # confirmatory holdout (corrected scorer)
python -m pcb.experiments.e30_certified_core        # WVS certified core (from tracked CSV)
python -m pcb.experiments.e31_positive_regime       # many-unit regime where deconvolution pays
```

All runs use fixed seeds (`pcb.util.det_seed`) and are deterministic.
Figures: `python -m pcb.figures.<name>`.

## Data availability

The simulation, theory, and benchmark experiments above reproduce with **no
external data**. The real-data reanalyses use **licensed microdata that we cannot
redistribute**:

- **ESS** (European Social Survey) — trust reanalysis (E12, E13, E23, E24)
- **WVS/EVS** (World Values Survey) — Foa–Mounk deconsolidation (E26)
- **LAPOP** (AmericasBarometer) — external design validation (E15–E18)

Download each from its provider and place under `data/ess/`, `data/wvs/`,
`data/lapop/` respectively; see `docs/DATA_SOURCES.md` for exact files and schema.
