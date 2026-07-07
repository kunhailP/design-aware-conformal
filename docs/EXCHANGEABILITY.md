# Coverage under population transport: country, region, and time

> Code: `pcb/experiments/e3_stress.py`. Results: `results/stress_pip.csv`.
> Nominal **90% simultaneous**. Cells = joint coverage / mean width.

PCB's guarantee is exact under population exchangeability, so we test it rather
than assume it, under three blocking schemes of increasing severity. The band
holds across country-level and temporal transport, and the covariate-shift
variant closes the one hard regime (whole-region holdout).

## Results (consumption, N=955, 123 countries, 6 regions, T=10)

| blocking | pointwise split-conformal | PCB | localized band (M3′) | weighted conformal (wPCB) |
|---|---|---|---|---|
| country | 54.1% / 0.060 | 88.9% / 0.097 | 88.3% / 0.079 | 89.7% / 0.120 |
| region (whole region held out) | 41.2% / 0.060 | 80.2% / 0.097 | 78.2% / 0.076 | 89.3% / 0.196 |
| forward-year (past surveys only) | 52.2% / 0.061 | 87.1% / 0.096 | 88.7% / 0.079 | 91.6% / 0.203 |

## What this shows

- PCB is valid under country-level and genuine temporal transport. With each
  target calibrated only on other countries' past surveys (real forward
  nowcasting, no future leakage), PCB holds 87.1% and the localized band 88.7%,
  indistinguishable from the country-blocked level. Predicting a future,
  unsurveyed year does not break the band.

- The covariate-shift band closes the cross-region gap. Withholding an entire
  world region is the hardest transport: the target region is wholly unseen, so
  unweighted PCB falls to 80.2%. The weighted conformal band (wPCB) restores 89.3%
  by reweighting toward covariate-similar populations and paying for the harder
  transport in width (0.196). Where no analog exists, it abstains with a [0,1]
  band rather than returning a confident but wrong interval. Cross-region
  transport is therefore not a wall but a priced operation.

- The per-threshold band is never the right tool here. The pointwise
  split-conformal band covers the curve 41–54% across every scheme; the
  simultaneous construction is what makes curve-level inference valid, in every
  transport regime.

## Method-to-regime map

| transport regime | use | coverage |
|---|---|---|
| same region / forward in time | PCB (or the localized band for tighter width) | 87–89% |
| structured, bias predictable | localized band (−18% width) | 88% |
| cross-region / structurally novel target | weighted conformal band, wPCB (widens or abstains) | 89% |

## Scope

The region grid is coarse (6); the kernel bandwidth τ (here 0.75) is fixed for
illustration. A finer leave-one-subregion-out split and a calibration-only rule
for τ (e.g. leave-one-region-out CV on the source pool) are the next refinements;
neither is expected to change the ordering. Income welfare reproduces the same
ranking (`main('income', ...)`).
