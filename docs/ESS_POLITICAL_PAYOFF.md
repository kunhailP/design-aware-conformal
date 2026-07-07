# Gate 5D part 1 — ESS political payoff: design-aware trust-decline certification

Status: 2026-07-06. Preregistered in `docs/ESS_5D_PREREGISTRATION.md` (choices
fixed before results; none changed after). Code: `pcb/experiments/e12_ess_decline.py`,
figures `pcb/figures/fig_ess_decline.py`. Data:
`results/ess_design_aware_decline.csv`. Scope: ESS core rounds 9–11 (2018–2022),
30 countries, 57 adjacent country-round pairs, trstprl primary + stfdem
replication. No oracle truth on ESS → we report certification and
reclassification, not coverage (validity is from theorem + Gate-5C simulation).

## Headline result — reported by GUARANTEE UNIT (inferential audit, E13)

The unit of the claim must be stated: a certified *pair*, a *country* with any
certified pair, or a country with a multiplicity-controlled *whole-trajectory*
guarantee are different objects. Certifying a net distributional decline in
political trust (the low-trust share, trust ≤ 1..4, rose over the low-trust range
simultaneously), design-aware vs plug-in, unique-country counts:

| guarantee unit (trstprl) | plug-in | design-aware | note |
|---|---|---|---|
| any-pair decline (marginal, NOT multiplicity-controlled) | 20 | 12 | loosest; the naive headline |
| repeated (≥2 certified pairs) | 3 | 1 | |
| **net decline** (first→last span, one band/country) | **10** | **6** | AT, BE, EE, GB, GR, NL |
| **persistent** (country-wide simultaneous over all pairs×thresholds) | 4 | **1** | **Greece only** |

(stfdem: any-pair 23/14, net 13/8, persistent 3/1 — Greece.)

**The properly-scoped result:** a country-wide simultaneous 90% band — one band
covering ALL of a country's adjacent-wave differences and the whole low-trust
range at once (R_c = max_{pairs,t}|D̂−D|/s), which controls the within-country
multiplicity across its pairs — certifies a *persistent distribution-wide trust
decline* for exactly **one country, Greece**, over 2018–2022, on both trust and
satisfaction. Plug-in claims 4/3. The multiplicity-uncontrolled "any-pair" count
(20→12) is the loosest reading and is reported as such, not as the headline. The
graded funnel is `figures/guarantee_hierarchy.png`.

Substantively this is a strong, defensible claim: the widespread "trust is
collapsing across democracies" reading rests on point estimates and per-wave,
per-country looks; once survey-design uncertainty AND the multiple-comparison
structure are both controlled, a certified persistent distribution-wide decline
survives only for Greece — consistent with its prolonged post-crisis political
turbulence. Elsewhere the declines are real-looking but not certifiable at the
whole-trajectory level without more data.

Terminology (real data has no oracle truth): the countries plug-in certifies but
design-aware does not are "certified by plug-in, inconclusive under design-aware
inference" — NOT "false positives." That term is reserved for the simulation
(Gate 5C), where plug-in's false-certification rate .222 ≫ α is measured against
known truth.

### Loosest-level reclassification (any-pair, for the mechanism check)

At the any-pair level, design-aware reclassifies to inconclusive: trstprl 8
countries (BE, CH, HR, HU, LV, ME, PT, SK), stfdem 9 (BE, CH, DE, IE, IT, NO, RS,
SE, SK). These are the weak-signal / high-noise pairs (next section) — the
mechanism check for why design-awareness demotes them.

## The reclassified countries are the weak-evidence ones (not arbitrary)

Among plug-in-certified pairs, those design-awareness reclassifies to
inconclusive are exactly the low-signal / high-noise pairs
(`figures/country_reclassification_map.png`):

- **trstprl:** kept pairs vs reclassified — decline signal 0.075 vs 0.032 (half
  the size), design SD 0.0155 vs 0.0199 (noisier), n 2179 vs 1495 (smaller).
- **stfdem:** decline signal 0.097 vs 0.027 (the dominant separator); the band
  correctly demotes weak-signal pairs even when raw n is not smaller — it is the
  signal-to-design-noise ratio, not n alone, that the studentized band uses.

Design-awareness is therefore doing real, interpretable work — it removes the
declines that rest on small or noisy surveys, and keeps the strong ones.

## Method decomposition (pair-level counts, 57 pairs)

| | M0 plug-in | M1 naive boot | M2 level band | M4 design-aware |
|---|---|---|---|---|
| trstprl | 23 | 12 | 5 | 13 |
| stfdem | 25 | 14 | 9 | 14 |

- **M0 → M1/M4 is the decisive step:** simply accounting for sampling uncertainty
  (any survey band) roughly halves certifications. This is where over-certification
  lives.
- **M1 (naive, ignores PSU/strata) ≈ M4 (proper design bootstrap):** on ESS the
  clustering design-effect refinement is modest (12 vs 13; 14 vs 14) — the
  intra-cluster correlation in these trust items is small relative to the
  sampling variance. Honest implication: on ESS the headline is "account for
  survey uncertainty at all," and the *design-effect* refinement should show
  larger separation where design effects are bigger (smaller, more clustered
  surveys — WVS, deferred). We report this rather than overclaim the clustering
  correction on ESS.
- **M2 (level-band non-overlap) is powerless:** 5 and 9, far below M4 — on real
  data, as in simulation, you cannot certify a within-country contrast from
  non-overlapping level bands (the bands are wider than the round-to-round
  change). Certify the *difference*, where the country effect cancels, not the
  levels. This validates the paired-difference construction as the right object.

## Two-outcome agreement

Design-aware certified net decline in **both** trust and satisfaction: 9
countries; trust-only: 3; satisfaction-only: 5. A country certified on both is a
stronger, corroborated claim; the disagreements (e.g. satisfaction-only) are
substantively interesting — declining satisfaction with democracy without a
certified parliament-trust decline, and vice versa.

## Honest scope and limits (carried from the preregistration)

- **Window:** design metadata (psu/stratum) exists only in rounds 9–11, so the
  design-aware certification covers 2018–2022. Stated as a data limit, not
  worked around; earlier rounds have weights only (extended sample) and cannot
  carry the design bootstrap.
- **No coverage claim on ESS:** validity is established by the Candidate-B
  theorem (two layers, `DESIGN_AWARE_PROOF_SKETCHES.md`) and Gate-5C simulation;
  on ESS we report certification counts, widths, and reclassification only.
- **Deferred, needs inputs not in hand:** WVS external validation (needs WVS
  microdata upload; the design-effect refinement should separate more there);
  the Foa–Mounk cohort/deconsolidation reanalysis (needs age `agea`, absent from
  the current extract — a re-extract from the .dta is the prerequisite). stfdem
  serves as the democratic-support proxy meanwhile.

## What this buys for the paper

The political section now has a real, defensible result that USES the method:
propagating survey-design uncertainty into a simultaneous within-country
difference band overturns 40% (8/20) of the apparent trust declines and 39%
(9/23) of the satisfaction declines that a standard analysis would report as
settled, while retaining the strong ones — and the overturned cases are
demonstrably the weak-evidence ones. This is the payoff that moves the paper from
"clever method" toward a paper political scientists cite (PA_NOVELTY_RISK §5).
