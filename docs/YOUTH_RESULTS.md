# Youth age-group robustness — results (E23)

Status: **run once, 2026-07-06**, per the sealed `YOUTH_PREREGISTRATION.md`. Same
certification, thresholds, core rounds, design bootstrap, ρ₀, and fallback as the
main analysis; only the age band changes. Reported as produced.
`results/ess_youth_certification.csv`.

## Persistent country-wide design-aware decline, by age group

| age group | countries with data | any-pair (DA) | net (DA) | **persistent (DA)** | +Bonferroni |
|---|---|---|---|---|---|
| youth 18–29 | 17 | 4 / 4 | 0 / 0 | **0 / 0** | 0 / 0 |
| full 18+ (benchmark) | 30 | 12 / 13 | 6 / 8 | **1 (GR) / 1 (GR)** | 1 / 0 |
| older 50+ | 30 | 10 / 14 | 8 / 9 | **1 (GR) / 1 (GR)** | 1 / 0 |
| mid 30–49 | 30 | 8 / 9 | 3 / 4 | **1 (GR) / 0** | 0 / 0 |

(cells are `trstprl / stfdem`; 98 country-cells abstained below the 200-response
min-n or with <2 qualifying core rounds.)

## Honest reading

1. **The benchmark reproduces the headline exactly.** The full-sample age group
   certifies a persistent country-wide decline in exactly one country, Greece, for
   both outcomes — identical to the main analysis (`ESS_POLITICAL_PAYOFF.md`),
   confirming E23 is consistent with E13.

2. **The "only Greece" finding is not an artifact of pooling ages.** It holds
   \emph{within} the older (50+) group for both outcomes and within the middle
   (30–49) group for trust in parliament. The persistent decline is concentrated in
   the older and middle adult population, not created by averaging across ages.

3. **Youth (18–29) certify zero persistent declines — but this is largely a power
   result, not evidence of youth stability.** Only 17 of 30 countries clear the
   preregistered min-n gate for youth (youth are ~15–25% of each sample), and the
   remaining youth cells carry more design noise, so the design-aware bands are wider
   and certify less. Youth do show some any-pair signal (4 countries) but nothing
   survives the persistent, country-wide, simultaneous bar. We therefore do **not**
   read this as "youth attitudes are stable" or as "youth disaffection"; we read it
   as: at the sample sizes ESS provides for a single age band, the persistent
   distribution-wide claim is not certifiable for youth in any country, including
   Greece. This is exactly the small-K / low-power scope condition of
   `HOLDOUT_VALIDATION_RESULTS.md`, seen on real data.

4. **Direction of the design-aware correction.** That youth (smaller n, noisier
   design estimates) certify strictly fewer declines than the full sample is
   consistent with the preregistered expectation that ρ̂ is larger for youth: the
   correction bites harder exactly where the design noise is larger, which is the
   honest behavior.

## Bottom line for the paper

The robustness supplement supports the main claim and adds an honest caveat: the
persistent, distribution-wide trust decline is a Greece phenomenon that is present in
the older and middle adult population and **cannot be certified for youth at ESS
sample sizes** — an underpowered null, not a substantive age contrast. It is not a
story of youth-led democratic disaffection.
