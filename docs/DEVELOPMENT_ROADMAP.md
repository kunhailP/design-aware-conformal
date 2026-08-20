# Development roadmap (2026-08-20): from "many good pieces" to four contributions

Direction agreed with the external editorial review: the goal is **more
fundamental, not more quantitative** — promote already-discovered phenomena to
general results, shrink the selector to a consequence of the theory, and close
the remaining theorem↔implementation seams. Companion to `PA_REVISION_PLAN.md`
(mechanical + framing items); this file owns the three technical workstreams.

## Target contribution architecture

> **C1.** The claim-unit problem: simultaneous inference over the entire
> trajectory (wrong-unit collapse: 3.5% / 49.8% / 90% at L=8).
> **C2.** Impossibility: with estimated calibration units and no design-noise
> law, no uniformly valid procedure improves on plug-in beyond discreteness slack.
> **C3.** Feasibility frontier: (K, ρ) regimes where correction is unnecessary /
> unlearnable / efficiency-improving.
> **C4.** Prevalence: simultaneous certification extended from claims within
> countries to "at least m of 33 countries" across them.

ESS/WVS become the application showing the four results change political
conclusions. The selector, gates, and frozen constants become *instances* of C3.

**Explicitly not doing** (agreed): another survey, a more complex selector,
larger simulation grids, or theorems added for count. Each risks the
architecture the revision exists to fix.

## Audit findings that reshape the work (2026-08-20 code/proof inspection)

1. **C2 is already proved, just buried.** The supplement's Theorem 1(ii) proof
   contains the exact inference-lower-bound the review asked for: on the
   ξ≡0 member, any non-randomized radius below the plug-in order statistic
   undercovers; randomized smoothing exhausts exactly the discreteness slack;
   "strict efficiency beyond the slack is attainable only by shrinking the class
   of admissible laws — i.e. by supplying the law of ξ" (supplement.tex:84-111).
   **Action: restate as the paper's headline impossibility theorem in the main
   text** (minimax phrasing, no new math), with Thm 1(i)'s non-identification as
   a corollary. Writing task, not research task.
2. **The exactness seam has a provable one-sided direction.**
   `pcb/inference/conformal_band.py:51-73` (`loo_deviations`): the LOO
   calibration pool (K−1 units) is *more* dispersed than the target's (K units),
   so the residual O(1/K²) asymmetry is claimed **conservative** — currently a
   docstring argument, echoed as "bounded only heuristically" at
   `04_theory.tex:108`. So Workstream A has three exits, in order of preference:
   (a) prove the one-sided dominance lemma (validity "≥ 1−α" is all Thm 3
   claims; exact level is not needed), (b) rerun headline results with the
   split-fold center Thm 3 already licenses, (c) downgrade the language.
3. **Certification is binary at frozen α=0.10.** `certify_claim_family`
   (`pcb/inference/claim_family.py`) returns certified spans at one α; no
   per-country p-values exist anywhere in the pipeline. C4 therefore needs an
   α-inversion layer, and real-data prevalence numbers need the licensed
   microdata (the committed CSVs store α=0.10 bounds only, not bootstrap draws).
   Implementation + contract tests can ship now; ESS numbers wait for the data.
4. **C3's raw material all exists.** Prop 1's floor D ≥ √(2/(K−1))
   (`06_evidence.tex:20-30`) is the χ²/CRLB identity for a variance from K
   exchangeable units — i.e. **selector-free**; the width gain ½ρ²+O(ρ⁴) is
   already proved (§4 Efficiency); the small-area regime flip is e48/e54/e55.
   What is missing is the assembly and one new lemma.

## Workstream A — close exactness (필수) — RESOLVED 2026-08-20 (e58)

- A1 DONE. `e58_center_exactness` (4 families × K∈{6..60}, 28 cells × 20k reps):
  LOO coverage never falls below the exact-construction floor by more than
  2×MC-SE (min gap −0.0039, SE 0.0021, 0/28 cells); the grand-mean construction
  Thm 3 excludes shows its real O(1/K) deficit (worst −0.064); and the strictly
  exact split-fold center returns an INFINITE radius throughout K≤15 (halving
  the calibration below ⌈1/α⌉) and costs 2–47% width where finite. Verdict:
  split-fold is not an alternative at survey K — LOO is a necessity, not a
  convenience, and its O(1/K²) asymmetry points conservative.
- A3 DONE. Language swept: abstract "finite-sample valid at any K"; intro
  "exact under its symmetric centers, conservative to O(1/K²) in deployment";
  §4 scope note carries the variance identity 1/(K(K−1)) + e58 + split-fold
  infeasibility; §8 "valid at any K"; supplement rem:center cites e58 with the
  honest "heuristic, not a bound" framing kept. Ledger pin:
  `test_center_exactness_seam`.
- A2 remains OPEN as an upgrade, not a gate: a formal one-sided dominance lemma
  for sup-scores would convert the measured heuristic into a theorem (the
  supplement's rem:bimodal explains why naive convolution monotonicity fails).
  Candidate route: coupling the K−1 and K pools plus a dispersive-ordering
  argument on the max; park unless a referee asks.

## Workstream B — feasibility frontier theorem (최우선) — SHIPPED 2026-08-20

Status: supplement gains the **universal reliability floor lemma**
(Lehmann–Scheffé at the Gaussian member: any unbiased variance estimator from
K exchangeable populations has relative SE ≥ √(2/(K−1)), so ANY procedure
demanding reliability τ needs K ≥ 1+2/τ² — 94 is the frozen intercept, the
law is universal) plus a three-regime frontier remark and Figure S
(feasibility_frontier.pdf). §6 carries a compact paragraph. e57 assembles the
(K, ρ) placement from committed CSVs — all three regimes are occupied by real
cells (WVS: unnecessary; ESS national scan: left of the floor; small-area
common-NUTS: 4 unlearnable cells; e54 all-countries: 8 feasible, the 4 fired
cells all feasible) and the ledger pins it (`test_feasibility_frontier`).
Remaining upside (post-submission): upgrade the remark to a net-benefit
frontier theorem with explicit constants (½ρ² vs c·√(2/(K−1))). Original
design notes below.

Candidate results (assembly + one new lemma):

- **Lemma B1 (universal reliability floor).** Any estimator of the design-noise
  scale from K exchangeable populations has relative standard error
  ≥ √(2/(K−1)) at the Gaussian member (CRLB for a variance). Hence *any*
  procedure demanding relative reliability τ before correcting requires
  K ≥ 1 + 2/τ². De-parameterizes 94: the frozen τ_D=0.147 instantiates a
  universal floor, answering "isn't 94 just your threshold?" — 94 is the
  intercept, √(2/(K−1)) is the law.
- **Theorem B2 (net-benefit frontier).** Correction buys width ½ρ²+O(ρ⁴)
  (proved); a safe (LCB-based) correction pays an uncertainty premium of order
  √(2/(K−1)). Correction is width-improving only when
  ½ρ² ≳ c·√(2/(K−1)), giving the frontier ρ*(K) ≍ (8/(K−1))^{1/4} and three
  regimes: I unnecessary (ρ small), II unlearnable (ρ large, K < frontier),
  III feasible (both large).
- **e57 phase diagram.** One figure: (K, ρ) plane, frontier curve, three
  regimes shaded, and the three real datasets placed on it — ESS (K≤33,
  ρ appreciable: Regime II), WVS (K=59–77, ρ small: Regime I), ESS small-area
  (K large, ρ large: Regime III, where the frozen selector fired). Values are
  in committed results (e13/e26/e48/e54); no microdata needed. This replaces
  much of the selector exposition in §5–§6 — Figure 2 grows into the paper's
  second-most-important exhibit.
- Contract test: frontier formula vs simulated width-improvement sign on the
  existing grid.

## Workstream C — prevalence inference (최우선) — MACHINERY SHIPPED 2026-08-20

Status: `pcb/inference/prevalence.py` (alpha-inversion p-values mirroring
`certify_claim_family` + Goeman–Solari/Simes true-discovery lower bound) with
4 contract tests (`tests/test_prevalence.py`: inversion↔certification
consistency, Simes shortcut on known vectors, planted-truth validity ≤ α,
power) and `e56_prevalence` (synthetic K=33/8-planted demo recovers d=8;
ESS mode auto-runs when microdata is placed and writes
`results/ess_prevalence.csv`). Remaining: run the ESS mode on the licensed
data, then add the prevalence sentence to §7 and the abstract (do NOT add the
claim to the paper before the real d exists). Original design notes below.

- **e56: simultaneous lower confidence bound on true discoveries.** Per country,
  invert certification over α: p_c = smallest α at which the net-decline span
  certifies (available directly from the bootstrap sup-t null draws in
  `certify_claim_family` — one new function returning p-values instead of
  binary sets). Then Goeman–Solari (2011) closed testing (Simes local tests;
  both already cited at `07_political.tex:41`) yields, at 90% simultaneous
  confidence, "at least m of 33 countries experienced net distributional
  erosion" — and dually an upper bound on how many can be persistently
  declining. Completes the ladder: threshold → wave → trajectory → country →
  cross-country prevalence.
- Ship now: `pcb/inference/prevalence.py` + contract test on synthetic truth
  (planted m declines, check the bound covers). Real ESS numbers: rerun e12/e36
  with p-value output once microdata is placed (folds into the HANDOFF B5
  rescaled-bootstrap rerun so the data pass happens once).
- Text cost ~150 words in §7 + one sentence in the abstract; budget freed by
  the selector material moving to the supplement (Workstream B).

## C1 stretch (추천, not gating)

Analytic wrong-unit statement behind Figure 1: bounds on joint trajectory
coverage of marginal-unit bands as a function of L under stated dependence
(independent thresholds lower bound (1−α)^L-type collapse; comonotone upper
bound). Likely a short proposition; only worth main-text space if it stays
under a page — otherwise a supplement remark keeping Figure 1 as the exhibit.

## Sequencing

1. **A1 + C-implementation** (simulation decision run; e56 machinery +
   contract tests) — no author input, no microdata.
2. **B lemma/theorem drafting + e57** — theory writing against existing results.
3. **A2 or split-fold rerun** per A1's verdict.
4. **Restructure pass** (PA_REVISION_PLAN Phase 1) once A/B/C fix what the
   abstract may claim: 4-contribution intro, C2 promoted, selector demoted.
5. Microdata pass (HANDOFF B items + e56/e38 real numbers) when files arrive —
   now also including a Rao–Wu–Yue rescaled rerun of e54/e55 (the positive
   small-area result uses the default m-of-m PSU bootstrap; A3 assumes an
   unbiased design bootstrap, so the RWY check belongs with it).

Self-assessment target: idea 8.5 → manuscript that carries C1–C4 with closed
seams is the "PA method paper, full stop" state the review describes.
