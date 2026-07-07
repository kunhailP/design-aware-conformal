# WVS deconsolidation reanalysis — preregistration (2026-07-07)

Choices fixed BEFORE running E26. The named target is the **Foa–Mounk "democratic
deconsolidation"** thesis (Journal of Democracy 2016/2017): across established
democracies, and *especially among the young*, support for liberal democracy is
eroding and openness to authoritarian alternatives rising — evidence built from
marginal wave-by-wave shifts in single items. We apply the paper's wrong-unit
correction: how many countries show a **persistent, distribution-wide, design-aware,
simultaneous** decline in democratic support, versus how many a marginal reading flags.
This formalizes the Alexander–Welzel / Voeten critique with a principled instrument.

WVS has **no PSU/stratum** (WVS_SCHEMA_AUDIT), so the survey-aware band is a **weighted
respondent bootstrap** (weights-only sampling variance), not a stratified-PSU design
bootstrap. Reported honestly as such; the mechanism (sampling-uncertainty-aware
simultaneous band demotes plug-in over-certification) is what WVS tests, in a survey
family structurally different from ESS (108 countries incl. non-European, coarse
4-category items, irregular ~5–10y wave gaps).

## Items (recoded to pro-democratic; deconsolidation = persistent DECLINE)

| id | WVS var | scale | core thresholds (decline = F rises there) |
|---|---|---|---|
| `imp_dem` (PRIMARY) | E235 importance of democracy | 1–10, high=essential | t ∈ {6,7,8} |
| `rej_leader` | E114 "strong leader", reversed | 1–4, high=reject strongman | t ∈ {1,2} |
| `rej_army` | E116 "army rule", reversed | 1–4, high=reject | t ∈ {1,2} |
| `sup_demsys` | E117 "democratic system", reversed | 1–4, high=support | t ∈ {1,2} |
| `confid_parl` | E069_07 confidence parliament, reversed | 1–4, high=confidence | t ∈ {1,2} |

`imp_dem` is the Foa–Mounk headline item and the PRIMARY outcome; the other four are
the regime-support battery, reported together. Deconsolidation for every item = a
persistent rise in the CDF over its low-support core = the whole distribution shifting
away from democratic support.

## Unit, estimand, methods (identical to the ESS design, E13)

- Exchangeable unit = **country trajectory**; K per item = countries with ≥ 2 qualifying
  waves (imp_dem 59, regime battery 76–77).
- Estimand = within-country consecutive-wave difference D(t)=F_{w+1}(t)−F_w(t) over the
  low-support core; the country effect cancels → weights-only survey inference.
- min valid n per (country,wave) cell = **400**; adjacency = consecutive qualifying waves.
- Methods: **M0 plug-in** (point, ignores sampling) vs **M-survey-aware** = weighted
  respondent bootstrap simultaneous lower band (B=2000, α=0.10).
- Guarantee hierarchy (as E13): marginal any-pair → repeated → net first→last →
  **persistent country-wide simultaneous** (over all pairs × core thresholds) →
  Bonferroni-across-countries.

## What is reported (no ground truth ⇒ certification, not coverage)

For each item: the count of countries certified declining at each rung, plug-in vs
survey-aware. Headline = **marginal N → persistent M** per item, and which countries
survive to the persistent bar. The claim is the *collapse up the hierarchy*, exactly as
on ESS — deconsolidation, made a distribution-wide simultaneous statement, is certified
in far fewer countries than a marginal reading suggests.

## Youth contrast (Foa–Mounk's central claim) — preregistered, ONE run

Foa–Mounk emphasize youth. Rerun the persistent certification within age band
**youth 18–29 (X003)** and **older 50+**, changing nothing else, min_n=300 per age×cell.
Report youth vs older persistent counts. Interpret an all-age or youth null honestly as
power-limited where the qualifying-country count is small (as in the ESS youth analysis).

## Gate probe (completes the unreachability argument on the largest survey)

On the same WVS transport construction (LOCO cross-country, per item), compute ρ̂, ρ̂_LCB,
and the reliability D at the WVS K, and record whether either selector gate opens. Fixed
expectation to be confirmed or refuted as produced: **gate A fails** (weights-only design
noise ⇒ small ρ) and **gate B fails** (even WVS's largest item, K=77, is below the
K≥94 the reliability floor √(2/(K−1)) ≤ τ_D=0.147 requires). If so, WVS — the largest
repeated cross-national survey — clears *neither* barrier, complementing ESS (where K is
the binding limit): the two barriers are never jointly cleared at cross-national scale.

## Post-run discipline

No change to items, directions, thresholds, min-n, or the hierarchy after seeing results.
Reported exactly as produced. WVS remains a weights-only replication (no PSU claim); the
region variable X048 is not used as a PSU.
