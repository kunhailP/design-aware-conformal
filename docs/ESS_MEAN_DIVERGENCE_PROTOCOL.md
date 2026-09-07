# ESS mean-versus-distribution comparison: fixed protocol

Frozen before access to the licensed ESS file in this environment:
2026-09-07. This is a narrowly scoped diagnostic for the existing E50 result,
not a new shape taxonomy or a new inferential claim family.

## Question

Among country-outcome trajectories whose first-to-last decline is already
certified by E50's joint core-CDF band, does a conventional first-to-last
weighted-mean contrast fail to certify a decline at the same alpha 0.10?

The comparison is deliberately one-way. It screens only the E50-certified net
set committed before this protocol. A non-significant mean contrast will be
described as "not certified by the mean-based analysis," never as evidence that
the mean is stable or unchanged.

## Fixed construction

- Outcomes, countries, rounds, minimum sample size, weights, design
  classification, bootstrap count, and deterministic seeds are exactly E50's.
- For an outcome on the 0--10 scale and its CDF at thresholds 0--9,
  `mean = 10 - sum_t F(t)`.
- Mean decline is `mean_first - mean_last`, positive for deterioration.
- Its one-sided 90% lower bound uses the same percentile-t bootstrap convention
  as the within-country decline code, applied to this single scalar contrast.
- Distributional decline remains E50's two-sided joint band over every ordered
  span and both directions on the fixed low-trust core `{1,2,3,4}`.

## Decision rule

A divergence case requires:

1. E50 joint net certification reproduces as true; and
2. the mean-decline lower bound is non-positive.

If fewer than two clear country cases appear, no new main-text figure or
headline will be added. No post hoc cutpoints, shape labels, equivalence margin,
or alternative mean test will be introduced after seeing the result.

## Recorded result

The frozen analysis was run after the protocol was written. All 15
country-outcome trajectories in E50's certified net set also certified a
weighted-mean decline; the divergence count was zero. The stopping rule
therefore closed the figure and manuscript-text gate.
