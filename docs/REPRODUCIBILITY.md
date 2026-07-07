# Reproducibility and Compute

Every number and public figure in the paper regenerates from two open data snapshots
with a single command:

```bash
pip install -r requirements.txt
make reproduce
```

`make reproduce` (driver: `scripts/reproduce.py`) runs four stages: fetch public data,
run all public-data experiments, regenerate the public figures, and a self-check that
compares the regenerated results against the values reported in the paper and exits
non-zero on any mismatch.

## Compute profile

CPU- and RAM-bound; no GPU. The whole public pipeline runs on a laptop in a few
minutes. The dominant cost is repeated leave-one-population-out cross-validation and the
simulation grid, not dense linear algebra. LightGBM runs on CPU throughout.

- Public reproduction (`make reproduce`): 4-8 vCPU, 8 GB RAM, a few minutes.
- Simulation grid alone (E2): parallelises across replicates via joblib if available.
- Optional private household layer (E1): 16 vCPU, 64 GB RAM.

## Determinism and seeding

- Every public experiment is deterministic. Randomness is seeded explicitly inside
  each script with a fixed `numpy.random.default_rng(seed)` (e.g. `e4_audit` uses
  `default_rng(0)`; `h2_phase` and `run_sim_grid` use fixed per-replicate seeds). Several
  experiments (`e3_baselines`, `e3_localized`, `e3_stress`, `e5_education`) use no
  randomness at all; they are exact functions of the input snapshot.
- No wall-clock date or time is used in any computational logic.
- Calibration and noise models are fit out of sample only (enforced in
  `models/predict_oof`), so calibration never uses data the model was trained on.
- The two public data snapshots are committed (`data/external/pip_curves.csv`,
  `data/external/education_curves.csv`) so results reproduce exactly even if the upstream
  World Bank APIs change. `make data` (or `python scripts/reproduce.py --refetch`)
  re-downloads them; expect minor drift if the APIs have been updated since.

## Expected self-check values

`make reproduce` (or `python scripts/reproduce.py --check`) verifies, within tolerance:

| check | expected |
|---|---|
| baselines: pointwise-band (M2) simultaneous coverage (consumption, 123 countries) | 54.1% |
| baselines: Gaussian-sup simultaneous coverage | 81.8% |
| baselines: PCB simultaneous coverage | 88.9% |
| localized: localized-band (M3′) / PCB width ratio (consumption) | 0.815 |
| audit: certified share of funding decisions | 46% |
| breadth: education pointwise-band simultaneous coverage | 51.4% |
| breadth: education PCB simultaneous coverage | 88.5% |

## Environment setup

- `pip install -r requirements.txt`. Versions are pinned to the exact set used to
  produce the paper (Python 3.11; numpy 2.4, pandas 3.0, scikit-learn 1.9, lightgbm 4.6,
  scipy 1.17, matplotlib 3.11).
- CPU only; no GPU or accelerator required.

## Entry points

All driven through the `Makefile` (run `make help` for the list):

`make reproduce`, `make data`, `make experiments`, `make figures`, `make theory`,
`make test`, `make paper`, `make e1` (optional private layer)

## Scope of public reproduction

- Fully public and self-checked: all simultaneous-coverage numbers (the within-population
  bootstrap interval, the random-effects variance-inflated interval, the pointwise band,
  Gaussian-sup, and PCB), the localized-band efficiency decomposition, the stress, region,
  and forward-transport results, the bias-boundary phase experiment (H2), the audit
  sufficiency and value-of-information results, the educational-attainment breadth result,
  the simulation grid, and the appendix theory checks. Figures `fig3`, `fig9`, `fig10`.
- Optional private layer (E1): the household-microdata reanalysis and figures `fig1`,
  `fig7`, `fig8` derive from DrivenData competition files that are not redistributable.
  Their committed PNGs and summary CSVs are provided; rebuild them with `make e1` once the
  files are placed in `data/`.
