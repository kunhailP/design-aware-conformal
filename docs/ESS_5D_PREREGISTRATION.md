# Gate 5D — ESS analysis preregistration (choices fixed BEFORE results)

Status: 2026-07-06, written before running `e12_ess_decline.py`. Per the Gate-5D
instruction item 10: thresholds, country set, wave range, and methods are fixed
here and are NOT to be changed after seeing results. Any deviation is logged as a
deviation, not silently applied.

## 1. Data scope (fixed)

- **Design-aware certification runs on the CORE sample only** (ESS rounds 9, 10,
  11 — the only rounds carrying psu/stratum in this integrated extract; audit:
  `results/ess_audit.csv`). This bounds the design-aware analysis to the
  2018–2022 window. Stated as a scope limit, not worked around.
- **Unit of analysis:** adjacent core-round country pairs (r, r+1) with both
  rounds in {9,10,11} for the same country. Confirmed available: **30 countries,
  57 adjacent pairs.** Non-adjacent pairs are NOT mixed.
- Per-country usable-pair counts are reported. Countries with 0 core pairs are
  excluded from the design-aware analysis (reported as excluded).

## 2. Outcomes and CDF direction (fixed, verified)

- **Primary:** `trstprl` (trust in parliament), 0 = no trust … 10 = complete
  trust (verified range 0–10 in data). **Replication:** `stfdem` (satisfaction
  with democracy), same 0–10 coding.
- CDF `F_{c,r}(t) = P(Y ≤ t)` over thresholds t = 0..9. High score = high trust,
  so **more mass at LOW t = a decline**: an increase F_{c,r+1}(t) ≥ F_{c,r}(t)
  for low t is the DECLINE direction. Recovery is the mirror.
- **Low-trust core** (the threshold set the FOSD claim is made over): t ∈
  {1,2,3,4} — "share with trust ≤ 1..4," the distrustful region. The extreme
  thresholds (t=0 and t≥5) are excluded from the FOSD claim because CDF
  differences degenerate toward 0 there and are un-certifiable under any noise
  (Gate-5C finding). This core is fixed in advance and matches the Gate-5C
  simulation (indices 1:5).

## 3. Estimand (fixed)

Consecutive-difference curve D_{c,r}(t) = F_{c,r+1}(t) − F_{c,r}(t). Within one
country the country effect cancels, so this is a pure survey-design inference —
no transport uncertainty enters (that only enters for unsurveyed targets).

- **Net decline (primary):** D certified > 0 for all t in the low-trust core,
  simultaneously — the low-trust share rose across the pair.
- **Persistent decline (secondary):** net decline certified for EVERY adjacent
  pair of the country's core trajectory (strict; expected to be rare per 5C).

## 4. Methods compared (fixed)

| tag | construction | what it (fails to) capture |
|---|---|---|
| M0 plug-in | certify iff point D̂(t) > 0 ∀ core t | no uncertainty → over-certifies |
| M1 naive-boot | difference band from a respondent bootstrap **ignoring PSU/strata** | understates variance (no design effect) |
| M2 trajectory-PCB | clustered level band, certify by non-overlap | transport band; powerless for decline (5C) |
| **M4 design-aware** | difference band from **stratified PSU bootstrap** | correct design variance |

M1 vs M4 isolates the design-effect (clustering) contribution; M0 vs M4 isolates
all survey uncertainty; M2 shows level bands cannot certify a contrast. (M3
DA-trajectory level band is omitted — it shares M2's powerlessness for this
estimand.) α = 0.10, bootstrap B = 2000, stratified PSU resampling (Rao–Wu;
single-PSU strata contribute no variance — conservative-low, flagged per pair).

## 5. Quantities logged per country-pair (fixed)

net_decline / net_recovery / inconclusive per method; band width over the core;
design SD of the difference; the point decline magnitude; n each round;
n_psu / n_strata completeness; weight CV. (ρ note below.)

## 6. ρ definition (fixed, to end the ambiguity)

Two DISTINCT ratios, never conflated:
- ρ_transport := σ_survey / σ_transport, a **standard-deviation ratio** of the
  cross-country design noise to the cross-country transport error. This is the
  Gate-5A/5C deployment-band quantity; ESS value ≈ 0.16–0.20 is THIS SD ratio.
  It governs the DA-deconvolution band for unsurveyed targets, not the
  within-country certification.
- For the within-country decline certification there is no transport term; the
  relevant quantity is the **design SD of the difference D** vs the **decline
  signal magnitude**, both reported directly (not as a single ρ). No variance-
  fraction ρ_Var is used anywhere; if introduced later it will be named
  explicitly.

## 7. Aggregation and the political-payoff report (fixed)

- Country-level: any-certified-decline, persistent decline, decline-then-reversal,
  trstprl-vs-stfdem disagreement.
- Headline: **N (plug-in / M0) vs M (design-aware / M4)** certified-decline
  country counts, WITH the explicit list of the N−M countries reclassified from
  "declining" to "inconclusive" and why (design SD, sample size, weight CV of
  those pairs). Reclassification rate in the high-design-uncertainty subgroup
  (smallest n / largest weight CV / fewest PSU) reported separately.

## 8. Explicitly deferred (needs data/inputs not in hand — NOT worked around)

- **WVS external validation:** requires WVS microdata upload (design metadata
  where available). Deferred to Gate 5D-part-2. No WVS numbers fabricated.
- **Foa–Mounk cohort/deconsolidation reanalysis:** requires age (agea), which is
  NOT in the current ESS extract. Re-extract agea from the .dta is a prerequisite;
  deferred to a focused robustness section. stfdem (satisfaction with democracy)
  serves as the democratic-support proxy in the core analysis meanwhile.

## 9. Honesty constraints carried from Gate 5C (fixed)

- Real ESS has no oracle truth: we do NOT claim measured coverage on ESS.
  Validity is established by theorem + simulation (5B/5C); ESS reports width,
  certification, and reclassification only.
- Candidate B's guarantee is stated in two layers (see
  `DESIGN_AWARE_PROOF_SKETCHES.md` two-layer note): exact/conservative under an
  oracle design-noise law; asymptotic with an O(K,B) remainder under the
  bootstrap-estimated law. ESS uses the estimated law → the asymptotic layer.
