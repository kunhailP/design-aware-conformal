# Results — Experiment B: the wrong-unit coverage collapse (Paper 2)

Preregistered in `WRONG_UNIT_COVERAGE_PREREG.md`; run via
`pcb/experiments/e28_wrong_unit_coverage.py`. Reported exactly as produced.
Output: `results/wrong_unit_coverage.csv`.

## Whole-trajectory coverage (K=30, T=6, 4000 reps, nominal 90%)

| L (rounds) | marginal (per point) | per-round | trajectory (ours) | 0.9^L ref |
|---|---|---|---|---|
| 2 | 38.2% | 81.7% | **90.0%** | 81.0% |
| 4 | 16.1% | 68.2% | **90.2%** | 65.6% |
| 6 | 7.1% | 58.2% | **90.3%** | 53.1% |
| 8 | 3.5% | 49.8% | **90.9%** | 43.0% |

## Reading

- The **trajectory band holds nominal at every L** (90.0–90.9%): the whole country
  curve-path is a single exchangeable unit, so its sup-score obeys the finite-sample
  order-statistic guarantee regardless of trajectory length.
- The **per-round band collapses** as the trajectory lengthens (81.7% → 49.8%), tracking
  the recursion, milder than the independent-round reference 0.9^L because the simulated
  rounds are positively correlated (ρ_ℓ=0.3) — as they are in real panels.
- The **marginal (per-point) band collapses fastest** (38.2% → 3.5%).

## Significance

This is the coverage face of the paper's thesis and the direct analog of the
marginal-collapse in the companion poverty paper (54% vs 89% simultaneous). It answers
the referee question "why not just do per-round (or marginal) inference?" empirically:
those bands are honest about their own unit but cover the object of interest — the whole
trajectory — far below nominal. It also gives the mechanism behind the certification
collapse (any-pair 20 → persistent 1): asking for the correct object, not asking it more
strictly, is what removes the over-detection.
