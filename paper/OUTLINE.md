# PA manuscript outline — word budget & main-vs-appendix split

Target: Political Analysis Research Article, ≤ 6,000 words (PA prefers short,
focused). Manuscript skeleton: `manuscript.md`. Companion poverty/education
paper: `papers/pcb-poverty/`. Title:

> **The Wrong Unit of Uncertainty: Adaptive Design-Aware Conformal Inference for
> Repeated Cross-National Surveys**

## Three things the reader must remember (write everything to serve these)

1. **Theory:** when the calibration target is itself observed only through a
   complex survey, the latent transport uncertainty is NOT identified without
   design information (Theorem 0).
2. **Method:** a safe adaptive procedure reduces to ordinary clustered PCB when
   design noise is small, deconvolves it only with enough information, and
   abstains conservatively otherwise.
3. **Politics:** wave-by-wave analysis suggests widespread trust decline, but
   controlling survey design AND the whole within-country trajectory certifies a
   persistent distribution-wide decline in only one country (Greece).

## Section budget (~6,000 words)

| § | title | words | key content | float |
|---|---|---|---|---|
| 1 | Introduction | 800 | noisy latent calibration; the missing uncertainty layer; contributions | — |
| 2 | Setup and impossibility | 800 | country trajectory, complex design, transport score; **Thm 0** | — |
| 3 | Safe adaptive method | 1,300 | PCB / deconvolution / conservative + the 3-gate selector; algorithm box | Alg 1 |
| 4 | Theory | 1,000 | Thm 1 oracle, Thm 2 estimated-law, Thm 3′ safe-adaptive validity, efficiency | — |
| 5 | Simulation & design-preserving stress test | 900 | selector transition + finite-K; safe-selector grid; LAPOP semi-synthetic | Fig 1, Fig 2 |
| 6 | ESS & LAPOP evidence | 900 | real-data regime characterization (all low-ρ); LAPOP real deff | Fig 3, Fig 4 |
| 7 | Political reanalysis | 500 | persistent decline 4→1 (Greece); youth robustness | Fig 5 |
| 8 | Discussion | 300 | when it reduces to PCB; limits without design data; scope | — |

## Main-text floats (≤ ~5) + Algorithm 1
1. Selector transition (sim, `selector_sweep.png`)
2. Safe-selector coverage grid (`safe_selector_grid.png`)
3. Guarantee hierarchy / plug-in vs design-aware (`guarantee_hierarchy.png`)
4. LAPOP level-vs-change ρ (`lapop_level_vs_change_rho.png`)
5. Country reclassification (`country_reclassification_map.png`)
Algorithm 1: the safe adaptive selector.

## MOVE to appendix / replication package (NOT main text)
poverty & education breadth (e1–e5, `papers/pcb-poverty/`), localized/weighted PCB,
predictor comparisons, VOI audit; full modulation grid (U0/S1/S2/S3) + Prop 3; WVS
weights-only replication; threshold/country-set sensitivity; DA candidate history
(A/B/C); finite-K correction detail (`safe_deconv_coverage.png`); all
gate/protocol docs (the preregistration trail).

## Reproducibility (PA Dataverse)
One-command reproduction; `dapcb()` API; theorem↔code contract tests
(test_theorem0, test_deconv_safe, test_safe_selector, …); data download scripts
(licensed microdata not redistributed).
