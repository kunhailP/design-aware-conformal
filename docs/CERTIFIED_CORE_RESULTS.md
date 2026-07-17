# E30 — The certified core: where persistent deconsolidation actually lives

Status: run 2026-07-17 on the tracked `results/wvs_deconsolidation.csv` (E26
output). Deterministic; reruns byte-identical (`python -m
pcb.experiments.e30_certified_core`). Output: `results/certified_core.csv`,
figure `paper/figures/certified_core.png` (`pcb.figures.fig_certified_core`).

## What it computes

Aggregates the per-item persistent certifications of the WVS Foa–Mounk
reanalysis into a co-certification structure: how many of the five battery
items each country certifies on, and which. Descriptive by design — each
per-item certification carries its own finite-sample guarantee from E26; no
additional joint inference is claimed for the counts.

## Headline

38 countries certify on ≥1 item; **13 form the certified core (≥2 items)**:

| country | items | which |
|---|---|---|
| Albania | 4 | rej_leader, rej_army, sup_demsys, confid_parl |
| Bosnia and Herzegovina | 3 | rej_leader, rej_army, confid_parl |
| Ecuador | 3 | imp_dem, sup_demsys, confid_parl |
| Tunisia | 3 | imp_dem, rej_leader, sup_demsys |
| Azerbaijan, Uzbekistan | 2 | sup_demsys + confid_parl |
| Ghana, Iraq, Rwanda | 2 | imp_dem + confid_parl |
| Lebanon | 2 | imp_dem + rej_leader |
| Finland, Switzerland, Trinidad & Tobago | 2 | rej_leader + rej_army |

## The three findings

1. **The core is not the consolidated West.** Composition: post-communist 4,
   MENA/Arab-Spring 3, Latin America & Caribbean 2, Sub-Saharan Africa 2,
   consolidated West 2 (Finland, Switzerland — and only on the strongman/army
   pair). The thesis was formulated about mature democracies; the surviving
   multi-item phenomenon lives largely elsewhere.
2. **The Western syndrome that survives is specific**: rising openness to
   authoritarian alternatives (FI/CH) or falling parliament confidence
   (NO/UK single-item) — never persistent distribution-wide decline in support
   for democracy as a system. Consistent with Wuttke et al. (2022).
3. **Celebrated backsliding cases are narrower than their reputation**:
   Turkey, Philippines, Mexico certify only on importance-of-democracy.

## Caveats (stated in the paper)

- Cross-item counts are descriptive aggregation of per-item certified sets.
- Item coverage varies by country (K = 59–77 per item): countries measured on
  fewer items have fewer chances to co-certify.
- Regional labels are descriptive groupings, not covariates; no regression is
  claimed.
