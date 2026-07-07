# Novelty Matrix — conformal inference for repeated cross-national survey curves

Status: Gate 5A literature audit, 2026-07-06. Compiled from four systematic
web surveys (functional/multivariate functional; panel/longitudinal/
non-exchangeable; clustered/design-based/noisy-calibration; irregular-length/
missingness/abstention). No new method code was written for this gate.

Our object, stated once so every row can be compared to it:

> A finite-sample band for a held-out **country**'s survey curve, where the
> exchangeable unit is the **country trajectory**, each country contributes a
> variable-length sequence of **rounds**, each round a **CDF over thresholds**
> estimated from a **complex survey** (weights, PSU, strata) so the calibration
> curves themselves carry **design variance**, the target may be a **new
> country / future wave / new region** (transport), and the band is
> **simultaneous over (rounds × thresholds)** with an **abstention** option.

Columns: **Est** estimand (Y=scalar, F=CDF/functional, τ=trajectory);
**Unit** exchangeable unit; **Dep** within-unit dependence handled;
**Fun** functional/trajectory response; **Irr** irregular/variable-length grid;
**Svy** complex survey design; **FS** finite-sample guarantee; **Shift**
distribution shift/transport; **Miss** missingness. ✓/–/~ = yes/no/partial.

## A. Functional conformal bands (the band machinery we build on)

| Paper | Est | Unit | Dep | Fun | Irr | Svy | FS | Shift | Miss | Relation |
|---|---|---|---|---|---|---|---|---|---|---|
| Lei–Rinaldo–Wasserman 2015 (AMAI; 1302.6452) | F | curve | – | ✓ | – | – | ✓ | – | – | Canonical sup-band over a single curve index. No repeated-measures index, no transport. |
| Diquigiovanni–Fontana–Vantini 2021 ("Importance of Being a Band"; 2102.06746) | F | curve | – | ✓ | – | – | ✓ exact | – | – | **The modulation-function source.** s(t) from the *training* split only; Remark 5 warns calibration-set s breaks exactness — never quantifies the penalty. |
| **Diquigiovanni–Fontana–Vantini 2022 (JMVA; 2106.01792)** | F | multivar. curve | ~ (joint sup) | ✓ | – | – | ✓ exact | – | – | **Closest structural analog.** Score sup_j sup_t \|y_j−μ̂_j\|/s_j — a max over a discrete index j AND t. But j = fixed heterogeneous components, NOT an exchangeable round trajectory; common grid required. |
| DFV 2021 (gas market; 2107.00527) | F | week-curve | ~ (de-trend) | ✓ | – | – | ~ | ~ | – | Sup-band pushed to time-indexed data by restoring exchangeability via preprocessing. Simultaneity over one curve's domain, not a horizon of rounds. |
| Ajroldi–DFV 2023 (CSDA; 2207.13656) | F | surface | FAR(1) | ✓ | – | – | ~ | – | – | Only genuinely two-index sup-band — but both indices functional (space×space); time consumed by autoregression, not covered. |
| Wang–Kurtek–Zhang 2025 (2502.15000) | F | curve | – | ✓ | ✓ | – | ✓ | – | ✓ | Irregular/partially observed curves via registration. Single curve, no repeated-measures index, no weights. |
| Diana–Romano–Irpino 2023 (Spatial Stat.) | F | spatial unit | spatial | ✓ | – | – | ✓ | ~ | – | Functional bands with geographic units (analog of "country"), spatial dependence; no time trajectory, no second index. |

## B. Panel / longitudinal / non-exchangeable / time-series conformal

| Paper | Est | Unit | Dep | Fun | Irr | Svy | FS | Shift | Miss | Relation |
|---|---|---|---|---|---|---|---|---|---|---|
| **Dunn–Wasserman–Ramdas 2022 (JASA; 1809.07441)** | Y | **group** | ✓ hierarchical | – | ✓ unequal n_i | – | ✓ (subsampling) | – | – | **The exchangeability skeleton** (country=group) AND the only paper certifying unequal within-group counts. But predicts one new scalar draw, not a joint trajectory band. |
| Tu–Giesecke 2026 (2605.17705) | Y | unit (online) | ✓ temporal+heterog. | – | – | – | ✓ stepwise + long-run | ✓ | – | The "2026 non-exch. panel" method: ONLINE, per-round scalar. Not a held-out-trajectory band, no LOCO, no functional response. Orthogonal. |
| Batra et al. 2023 LPCI (2310.02863) | Y | series/point | ✓ quantile-FE | ~ | – | – | – asymptotic | ~ | – | Named "longitudinal conformal"; two-way coverage but asymptotic, per-period, aligned panel. The baseline to beat. |
| Sun–Yu 2024 CopulaCPTS (ICLR; 2212.03281) | τ | trajectory | ✓ copula over steps | ✓ horizon | – | – | ✓ joint | – | – | **Finite-sample JOINT over a whole multi-step trajectory** — the nearest simultaneity competitor. Protects future steps of exchangeable trajectories, not a held-out subject's observed path; copula, not sup-score. Benchmark against it. |
| Stankevičiūtė et al. 2021 (NeurIPS) | τ | whole series | ✓ within-series | ✓ | – | – | ✓ | – | – | Establishes "unit = whole sequence." Requires EQUAL length — the assumption our variable-length countries break. |
| Xu–Xie 2021 EnbPI (ICML) | Y | – (mixing) | ✓ temporal | – | – | – | ~ | ~ | – | Single-series forecasting baseline. |
| Chernozhukov–Wüthrich–Zhu 2021 (JASA; counterfactual) | Y/τ | time periods | ✓ block-perm | – | – | – | ✓ exact | ~ | – | Permutation-over-time for one series. Opposite unit choice. |
| Chernozhukov–Wüthrich–Zhu 2021 (PNAS; distributional CP) | Y | obs/time | ✓ mixing | – | – | – | ~ | – | – | CDF-based scores for a scalar target; no simultaneity, no country unit. |
| Gibbs–Candès 2021/2024 (ACI/DtACI) | Y | – (adversarial) | ✓ arbitrary | – | – | – | long-run only | ✓ | – | Single adversarial stream; ESS ~9 rounds too short. Contrast only. |
| Principato et al. 2024 (2411.13479) | Y | obs | hierarchy (sum) | – | – | – | ✓ marginal | – | – | Hierarchical linear constraints; component-wise only, not joint. Peripheral. |

## C. Clustered / design-based / group-conditional / noisy-calibration

| Paper | Est | Unit | Dep | Fun | Irr | Svy | FS | Shift | Miss | Relation |
|---|---|---|---|---|---|---|---|---|---|---|
| **Wieczorek 2023 (Survey Methodology; 2303.01422)** | Y | individual unit | ✓ strata/PSU/πps | – | – | **✓** | ✓ exact | **– (same pop.)** | – | **Only design-based CP.** Single finite population, scalar, individual-level, test unit from the SAME population — no transport, no CDF, no clusters-as-units, no design bootstrap. Our contribution sits exactly in its blind spots. |
| Bersson–Hoff 2024 (JSSAM; 2204.08122) | Y | small area | ~ borrow strength | – | – | ~ | ✓ area-level | ~ | – | Small-area + CP, model-based, scalar, single population. The "guarantee regardless of model" philosophy we want. |
| Bersson–Hoff 2024 (JRSS-A) | Y | area | ~ | – | – | – | ✓ | ~ | – | Companion; same program. |
| Vovk 2012 Mondrian (1209.2673) | Y | per-category | within-category exch. | – | – | ~ (taxonomy) | ✓ per-category | – | – | License for group/length-conditional validity — IF each category has enough units (the ESS bottleneck). |
| Jung et al. 2023 BatchMVP (2209.15145) | Y | obs | overlapping groups | – | – | – | ✓ multivalid | – | – | Overlapping-group-conditional coverage; assumes clean exchangeable examples. Guarantee-strength benchmark. |
| Gibbs–Cherian–Candès 2025 (JRSSB; 2305.12616) | Y | obs | – | – | – | – | ✓ over shift class | **✓** | – | **The transport primitive:** exact coverage over a finite-dim class of covariate shifts. Individual-level, no design variance in calibration points. |
| Bhattacharyya–Barber 2024 (2401.17452) | Y | per-group | group-shift | – | – | ~ | ✓ group-cond. | ✓ | – | Bridges Mondrian + weighted CP: each length-pattern/cluster a group with its own weight. Directly usable to fuse length-partition with transport. |
| Feldman–Einbinder–Bates–Angelopoulos–Gendler–Romano 2022 (2209.14295) | Y | obs | – | – | – | – | ✓ (Thm 2.1) | – | ✓ noisy label | **Closest to "calibration curves are noisy survey estimates."** Stochastic-dominance ⇒ CP conservative; TV-bound ⇒ α′=α+2(n/(n+1))ε. Global noise bound, not per-point known variance. |
| Sesia–Wang–Tong 2025 (JRSSB; 2309.05092) | Y | obs | – | – | – | – | ✓ exact correction | – | ✓ contaminated | Exact two-sided coverage correction under a known contamination model. Classification-only; contamination model, not known-variance additive noise. |
| Bar Shalom et al. 2025 (2505.04733) | Y | obs | – | – | – | – | ✓ | – | ✓ corrupted | **Named worst-case-over-uncertainty-set score (Uncertain Imputation).** Transplantable: replace corruption set with a design-CI per country. Targets bounded/adversarial corruption, not known heteroskedastic design variance. |
| Lee–Jung–Hong 2026 (2606.10563) | Y | individual | temporal shift | – | – | **✓ design weights** | ✓ | ✓ | – | Only recent paper marrying survey design weights with weighted CP — but transport ACROSS TIME within one population, scalar. |

## D. Transport, irregular length, missingness, abstention (the extension axes)

| Paper | Est | Unit | Dep | Fun | Irr | Svy | FS | Shift | Miss | Relation |
|---|---|---|---|---|---|---|---|---|---|---|
| Tibshirani–Barber–Candès–Ramdas 2019 (NeurIPS; 1904.06019) | Y | (x,y) | – | – | – | – | ✓ (known w) | ✓ | – | Weighted-CP foundation. Exact only with KNOWN weights — our estimated-weight/outside-support case is exactly what it does not cover. |
| Barber–Candès–Ramdas–Tibshirani 2023 (Ann. Stat.; 2202.13415) | Y | example | ✓ any | – | – | – | ✓ TV coverage-gap | ✓ | – | **The bound** that quantifies coverage loss from non-exchangeability — our length-heterogeneity penalty and abstention threshold diagnostic. |
| Barber–Candès–Ramdas–Tibshirani 2021 (Inf.&Inf.; 1903.04684) | Y | example | – | – | – | – | ✓ impossibility | – | – | **Hard ceiling:** exact pattern-conditional coverage is impossible distribution-free. Forces Mondrian-by-length or approximate statements. |
| Lei–Candès 2021 (JRSSB; 2006.06138) | Y | example | – | – | – | – | ~ | ✓ estimated w | ~ | Estimated-weight weighted CP with DR argument; assumes overlap/positivity we deliberately violate. |
| Yang–Kuchibhotla–Tchetgen 2024 (JRSSB; 2203.01761) | Y | example | – | – | – | – | ~ DR | ✓ estimated w | – | Doubly-robust estimated-weight transport. No support-failure handling. |
| Zaffran et al. 2023 (ICML; 2306.02732) | Y | masked ex. | – | – | ~ (mask) | – | ✓ marginal, any mask | ✓ (mask) | ✓ all mechanisms | **Reframe: country round-set = missingness mask.** Coverage varies BY mask even when marginal holds — our length problem restated. |
| Fan–Park–Vo–Brunel 2025 (2512.14221) | Y | per-mask | – | – | ✓ per-mask | – | ✓ mask-cond. (MCAR) | ✓ | ✓ | **Most on-target for irregular panels:** finite-sample P(Y∈C\|M=m)≥1−α under MCAR via mask-conditioned weighted CP. Scalar; we extend to sup-score + design + transport. |
| Wang–Goel 2026 (2605.02072) | Y | example | – | – | – | – | ✓ (moment-free) | ✓ unbounded | – | **State of the art for support failure:** weight clipping caps exploding weights → soft abstention. Basis for our hard "I don't know" threshold. |
| García-Galindo–Löfström 2025 (2506.21802) | Y | example | – | – | – | – | ✓ error-on-accepted | – (exch.) | – | Formal conformal reject option — but under exchangeability, NOT shift. Combining reject-guarantee with covariate shift is open. |

## Empty cells — what no row occupies (the contribution surface)

1. **Design variance in cross-population calibration units.** No paper makes
   the population the exchangeable calibration unit AND lets each unit be a
   survey-estimated CDF carrying PSU/strata/weight design variance propagated
   into the nonconformity score. Wieczorek is single-population/scalar; DWR is
   clean-i.i.d.-within-group; the noisy-calibration papers are individual-level
   with global (not per-unit-known) noise. **Intersection empty.**
2. **Quantified self-inclusion (in-sample modulation) undercoverage.** DFV
   force s onto the training split *to avoid* it and never analyze the penalty;
   nobody quantifies coverage loss vs (K, slicing granularity). **Empty.**
3. **Length-adjusted sup-score with a finite-sample guarantee.** Variable-length
   sup-scores are non-exchangeable; the only routes are Mondrian-by-length,
   group-weighted, or mask-conditional weighted CP. A clean length-adjusted
   score theorem does not exist. **Open.**
4. **Reject-option guarantee under covariate shift.** Weight clipping and the
   exchangeable reject option exist separately; their combination does not.
   **Open.**
5. **Band simultaneous over (repeated-measures × functional) indices with the
   subject as the exchangeable unit.** DFV-JMVA maxes over (component × t) but
   components are fixed, not an exchangeable trajectory; CopulaCPTS is joint
   over future steps, not a held-out subject's path. **Open, but the machinery
   is borrowable — this is the WEAKEST of the five (see PA_NOVELTY_RISK.md).**
