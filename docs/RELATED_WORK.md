# Related work & novelty scan (design-aware conformal)

Deep-research scan, 2026-07-06. **Novelty verdict: the impossibility /
deconvolution-on-survey-estimates framing is genuinely new.** Most anchors below are
well-established; items marked **[VERIFY]** were surfaced by web fetch whose summary
partly echoed the query wording (possible hallucination) — DO NOT cite until the PDF
is confirmed.

## Novelty rating of our three contributions
- **(1) Impossibility / non-identification theorem — NOVEL (highest value).** No prior
  work proves that when conformal calibration objects are complex-survey *estimates*,
  the latent transport-error law is non-identified (a deconvolution obstruction), so
  no observed-score band is both valid and strictly narrower than the conservative
  plug-in. Frame as importing Fan (1991)-style deconvolution non-identifiability into
  the coverage ledger of clustered conformal.
- **(2) Nominal-safe adaptive selector — NOVEL-to-INCREMENTAL.** New as a package but
  components echo known ideas. **Pitch as a deployment safeguard/guarantee, NOT a
  performance win**, or a referee asks "why not just Dunn–Wasserman–Ramdas?"
- **(3) Empirical (low-ρ ⇒ reduces to clustered CP; 1-of-30 persistent decline) —
  INCREMENTAL as method but VALUABLE and honest.** Frame "1 of 30 vs ~20 marginal"
  as a **multiplicity** statement (FDR / partial pooling).

Strategic note: (1)&(3) cut against (2) — you prove a correction is needed in
principle, then show it is empirically inert. That candor is a *strength* for PA.

## Pre-emption risks (cite and distinguish)
- **Wieczorek (2023), Design-Based Conformal Prediction, Survey Methodology
  (arXiv:2303.01422) [VERIFY issue].** Closest survey-design CP — design enters via
  test/calibration *weighting*, not as noise corrupting transported objects. The
  "isn't this solved?" reflex citation; our answer: they treat sampled units as
  objects, we treat each country's *estimated distribution* as a noisy object.
- **Sesia, Wang, Tong (2025), Adaptive Conformal Classification with Noisy Labels,
  JRSS-B [VERIFY].** Deconvolve a *known* noise model; our value-add is proving when
  it is impossible and gating it.
- **Einbinder et al. (2024), Label-noise robustness of CP, JMLR 25
  (arXiv:2209.14295).** Plug-in-on-noisy is conservative — analogous but label noise.
- **Lee, Jung, Hong (2026), arXiv:2606.10563 [VERIFY — POSSIBLY HALLUCINATED; fetch
  PDF before citing].** Reported motivational overlap (historical survey estimates as
  noisy calibration objects). #1 pre-emption check.
- **Rafe, Das (2026), arXiv:2605.05562 [VERIFY — POSSIBLY HALLUCINATED].** Subgroup
  reliability under survey weights; different problem.

## Methods anchors (well-established)
- Weighted/nonexchangeable CP & shift: Tibshirani et al. 2019; Barber et al. 2023;
  Gibbs & Candès 2021, 2024. *Distinguish our "adaptive" (design-noise-certified
  selection) from theirs (temporal/online).*
- Cluster/hierarchical CP (population as unit): Dunn, Wasserman & Ramdas 2023 (JASA);
  Lee & Barber 2023 (arXiv:2306.06342) [VERIFY title]. **Our backbone.**
- Noisy/estimated calibration & deconvolution: Einbinder 2024; Sesia 2025; **Fan 1991
  (Ann. Statist. 19:1257) — the deconvolution non-identifiability we import.**
- Functional/simultaneous bands: Diquigiovanni, Fontana & Vantini 2021
  (arXiv:2106.01792).
- Survey design variance: Binder 1983; Lumley 2010; Kaminska & Lynn 2017 (JOS).
- Multiplicity across countries: Benjamini & Hochberg 1995; Gelman, Hill & Yajima 2012.

## Political-science framing (VERIFIED URLs — see docs/POLITICAL_PAYOFF.md)
The field has ALREADY converged that "trust declining everywhere" is an over-reading
— our headline formalizes that skepticism, it doesn't fight consensus:
- Foa & Mounk 2016/2017 (deconsolidation thesis) VS the skeptics: Norris 2017
  ("trendless fluctuation"), Voeten 2017 (specification-fragile), Alexander & Welzel
  2017, **Wuttke, Gavras & Schoen 2022 (BJPS, 18 democracies, preregistered)**,
  **Valgarðsson et al. 2025 (BJPS, 1958–2019, no universal secular decline)**.
- Greece crisis-era collapse robustly documented: Armingeon & Guthmann 2014 (EJPR),
  Torcal 2014 (ABS) — so "only Greece" is a credibility feature, not an anomaly.
- Distributional vs mean change: DiMaggio, Evans & Bryson 1996 (AJS).

## Action items before submission
1. Fetch Lee–Jung–Hong (2026, arXiv:2606.10563) in full — confirm any
   impossibility/deconvolution claim; if arXiv ID invalid, drop it.
2. Confirm titles/venues for all [VERIFY] items.
3. Separate our "adaptive"/"design-based" from Gibbs–Candès / Wieczorek explicitly.
4. Verify 2017 JoD exchange piece titles; van der Meer 2024 / Devine 2024 author lists.
