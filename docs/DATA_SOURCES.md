# Data Sources: Provenance, Licence, and Selection Criteria

The unit of analysis is the *population*. A population is a country-year (or
survey-year) sample drawn from a common distribution of poverty curves. The
number of exchangeable populations available for estimation is the primary
constraint on the analysis.

## E1: DrivenData competition data

The household-microdata experiment (E1) uses household-level data from a
DrivenData prediction competition.

- Files: `data/train_hh_features.csv` (household features),
  `data/train_hh_gt.csv` (ground-truth household consumption), and
  `data/train_rates_gt.csv` (per-threshold poverty headcounts). The expected
  schema is documented in `data/schema/`.
- The data comprise three source surveys, partitioned into 24 pseudo-populations
  by survey and stratum.
- **Not redistributed.** The DrivenData competition licence does not permit
  redistribution, so these files are not committed to the repository. Users must
  obtain the data directly from the competition and place the files under
  `data/`.

## E3: World Bank Poverty and Inequality Platform (PIP)

The cross-country transport experiment (E3) uses real cross-country, cross-year
poverty curves from the World Bank Poverty and Inequality Platform (PIP).

- Acquired via `pcb/data/fetch_pip.py` (run `python -m pcb.data.fetch_pip`),
  which queries the PIP API and caches the raw responses under `data/external/`.
- For each population the script fetches the poverty headcount at a grid of
  poverty lines (the poverty curve), together with covariates including the
  distributional mean, median, Gini, mean log deviation, deciles, reporting
  aggregates, and region.
- Coverage: approximately 2,475 country-year surveys spanning 171 countries.
  Populations with a complete curve across all requested poverty lines are
  retained.
- Each population is keyed as (country, year, welfare type), where welfare type
  distinguishes consumption-based from income-based surveys.
- Licence: World Bank, CC-BY 4.0 (public data).

## Candidate external sources for extending E3

The following public and application-access microdata sources are candidate
extensions for increasing the number and diversity of populations. They are
listed here factually as options.

| Source | Unit | Outcome | Access | Note |
|---|---|---|---|---|
| World Bank LSMS / Microdata Library | country-year | consumption aggregate | public-use files (per study) | Closest match to the PIP welfare measure; requires substantial harmonisation. |
| LIS (Luxembourg Income Study) | country-year | harmonised income | application / remote execution | Income-based poverty with harmonised variables. |
| IPUMS International | country-census-year | employment, education, and housing deprivation | free, registration required | Generalises from consumption poverty to broader social deprivation indicators. |
| DHS (Demographic and Health Surveys) | country-year | wealth index, asset, and health deprivation | application | Asset-based deprivation rather than consumption. |

## Selection criteria for E3 populations

A population is eligible for inclusion if it satisfies the following:

- It provides a usable welfare aggregate (consumption or income).
- It provides survey weights, and ideally stratum and primary sampling unit
  identifiers.
- Its poverty threshold definition is comparable to, or convertible onto, a
  common threshold grid.
- It can be held entirely out of model training, so that transport to the target
  population is evaluated out of sample.

## Population-unit definition

The default population unit is `survey_year` / `country_year`. The unit is chosen
so that populations can plausibly be treated as exchangeable draws from a common
distribution of poverty curves.
