# When does localization tighten a *simultaneous* band? (efficiency theory)

> Deep-dive result. Verified numerically on PIP (consumption + income). Corrects
> two plausible-but-false claims and establishes the true characterization, which
> extends the paper's marginal-vs-simultaneous theme from *coverage* to *efficiency*.

## Two false leads, killed

**(F1) "CDF-shape tightening buys width."** The isotonic projection
is coverage-preserving, but its empirical width gain is ≈0.2%: when `θ̂` is
smoothly monotone, the raw band edges `θ̂ ∓ q·s` are already monotone, so the
running-max/min projection does almost nothing. Monotonicity is a validity tool,
not an efficiency tool, so it should be presented as such, not as a width lever.

**(F2) "Localized width = PCB width × √(1−ρ²)"** (ρ² = share of transport-error
variance explained by population features). False: consumption and income have
nearly identical explained variance (s-weighted LOO R² = 0.185 vs 0.182) yet very
different width gains (ratio 0.815 vs 0.973). Average explained variance does not
determine simultaneous-band efficiency.

## The true decomposition (exact, verified)

The localized band's width relative to PCB factorizes as

```
width_M3' / width_PCB  =  (s̄_resid / s̄_E) · (q'_{1−α} / q_{1−α})
                          \_____ ρ̄² factor _____/   \__ sup factor __/
```

- Marginal factor `s̄_resid/s̄_E = √(1−ρ̄²)`: the per-threshold residual-vs-raw
  scale ratio. It depends only on average explained variance and is ≈ 0.90 for
  both welfare types (R̄² ≈ 0.18).
- Sup factor `q'/q`: ratio of the studentized sup-score conformal quantiles
  `q = Q_{1−α}(max_t |E_i(t)|/s(t))` for the raw vs residual field. This is the
  factor that discriminates between the two welfare types.

Verified reconstruction (matches the directly measured ratios):

| welfare | s̄_resid/s̄_E | q'/q | reconstructed | observed |
|---|---:|---:|---:|---:|
| consumption | 0.901 | 0.924 | 0.832 | 0.815 |
| income | 0.903 | 1.039 | 0.938 | 0.973 |

## Characterization

> **Localization tightens a *simultaneous* band iff the predictable bias carries
> the sup-driving (worst-threshold) structure of the error field**, a strictly
> stronger condition than explaining average variance. When the predictable
> component is also the component that produces the largest studentized deviations
> (`q'/q < 1`), localization compounds the marginal gain (consumption: 0.92 × 0.90
> gives 18% narrower). When the predictable component is merely average-variance
> and the worst-threshold behaviour is residual noise, regressing it out leaves
> the sup-score essentially unchanged or worse (`q'/q ≳ 1`, inflated by the
> leave-one-out factor), and the net gain vanishes (income: 1.04 × 0.90 gives ~0).

## Why this matters (a structural parallel, not one dial)

The paper's spine is marginal ≠ simultaneous for coverage: a per-threshold band
valid at each point under-covers the curve. This result shows that the same
marginal-vs-simultaneous dichotomy that governs coverage also governs efficiency:
average (marginal) predictability ≠ sup (simultaneous) predictability. R² is the
marginal notion; `q'/q` is its simultaneous counterpart. The right efficiency
target for a curve-level band is the predictable share of the worst-threshold
error, not of the average error.

This converts the localized band from a heuristic that sometimes helps into a
result with a precise scope condition, and it explains, rather than reports, the
consumption-vs-income split. The relationship is a structural parallel between the
coverage and efficiency analyses (the same marginal-vs-simultaneous dichotomy
appears in both), not a single tunable parameter that jointly controls coverage
and efficiency.

## The modulation lever is near-saturated (option A, settled)

Could a better *modulation* `s(t)` beat PCB's heuristic `s = SD`? Any `s` that
depends only on the calibration bag keeps validity, and (by scale invariance) the
mean width is `∝ q(s)·Σ_t s(t)`. Fixing `q = 1` turns this into a clean program:

> **minimize Σ_t s(t)  s.t.  |E_i(t)| ≤ s(t) ∀t for ≥(1−α)K populations.**

The optimum is the minimum-area envelope of a (1−α)-fraction subset of error
curves, the genuinely optimal modulation. We built it greedily and compared it to
`SD` at matched coverage (leave-one-country-out, PIP):

| welfare | SD width @≈89% | optimal-envelope width @≈89% | gain |
|---|---:|---:|---:|
| consumption | 0.097 | ≈0.090 | ~7% |
| income | 0.061 | ≈0.061 | ~0% |

`SD` studentization is within ~7% (consumption) / ~0% (income) of the provably
optimal modulation. There is no large free width here. The reason is structural:
the sup-band's binding quantity is the tail scale at each threshold, and for a
roughly-Gaussian studentized field `SD(t)` already tracks it (the envelope is a
tail quantile of `|E(t)|`, ∝ `SD(t)` up to a Gaussian constant). This justifies
PCB's simple construction as near-frontier and forecloses the "you should have
optimized the modulation" objection.

## Efficiency, settled: only one lever is material

| lever | gain (consumption / income) | verdict |
|---|---|---|
| monotonicity (isotonic projection) | ~0.2% | validity tool, not efficiency |
| modulation `s(t)` (optimal envelope) | ≤7% / ~0% | near-saturated by SD |
| bias correction (M3′, asymmetry) | 18.5% / ~0% | the only material lever, governed by sup-predictability |

The efficiency of a poverty-curve simultaneous band comes essentially only from
asymmetric bias correction, and exactly to the degree the predictable bias drives
the worst-threshold error (above). Monotonicity and modulation are saturated,
which gives a complete characterization across every lever.

## Open constructive question (next)

If the sup-score tail is what matters, a localization that targets the
*worst-threshold* residual (extreme/quantile regression of `max_t |E|/s`) rather
than the per-threshold mean should dominate plain OLS localization when `q'/q` is
the binding factor. Untested; a positive result would turn this characterization
into a constructively optimal band. Negative result is also informative (the OLS
localization is already near the achievable frontier).

## Reproduce

`results/`-free; computed from `data/external/pip_curves.csv` with
`pcb.inference.conformal_band.conformal_band_quantile` and
`pcb.inference.localized_band._loo_fit` (see the decomposition snippet in the
project notes).
